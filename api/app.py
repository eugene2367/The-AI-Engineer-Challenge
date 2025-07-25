# Import required FastAPI components for building the API
import sys
import os
# Add parent directory to Python path to find aimakerspace module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
from typing import Optional, List
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.openai_utils.chatmodel import ChatOpenAI
from aimakerspace.text_utils import chunk_text
import asyncio
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Initialize our components (lazy initialization to avoid API key requirement at startup)
chat_model = None
vector_db = VectorDatabase()

def get_chat_model():
    """Get or create the chat model instance."""
    global chat_model
    if chat_model is None:
        chat_model = ChatOpenAI(model_name="gpt-4-turbo-preview")
    return chat_model

# Store uploaded documents in memory (in production, use a proper database)
documents = {}

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication
    project_id: Optional[str] = None # OpenAI project ID

class QueryRequest(BaseModel):
    query: str
    document_id: str
    api_key: str  # OpenAI API key for authentication

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the provided API key
        client = OpenAI(
            api_key=request.api_key,
            project=request.project_id,
        )
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model or "gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True  # Enable streaming response
            )
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), openai_api_key: str = Form(None)):
    try:
        logger.info(f"Received file upload request: {file.filename}")
        logger.debug(f"Content-Type: {file.content_type}")
        logger.debug(f"File size (if available): {getattr(file, 'size', 'unknown')}")
        
        # Check file size before processing (Vercel has 4.5MB limit)
        if hasattr(file, 'size') and file.size:
            logger.info(f"File size from request: {file.size} bytes ({file.size / (1024*1024):.2f} MB)")
            if file.size > 4.5 * 1024 * 1024:
                logger.warning(f"File exceeds Vercel's 4.5MB limit: {file.size} bytes")
                raise HTTPException(
                    status_code=413, 
                    detail="File too large for Vercel deployment. Maximum size is 4.5MB. Please use a smaller file or deploy to a different platform."
                )
        
        # Read file content in chunks to handle large files
        content = b""
        chunk_size = 1024 * 1024  # 1MB chunks
        total_size = 0
        chunk_count = 0
        
        logger.info("Starting file content reading...")
        
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            content += chunk
            total_size += len(chunk)
            chunk_count += 1
            logger.debug(f"Read chunk {chunk_count}: {len(chunk)} bytes. Total size: {total_size} bytes ({total_size / (1024*1024):.2f} MB)")

        logger.info(f"File reading completed. Total size: {total_size} bytes ({total_size / (1024*1024):.2f} MB)")

        # Check file size after reading
        if total_size > 10 * 1024 * 1024:
            logger.warning(f"File too large after reading: {total_size} bytes")
            raise HTTPException(
                status_code=413, 
                detail="File too large. Maximum size is 10MB"
            )

        # Check for Vercel's limit again after reading
        if total_size > 4.5 * 1024 * 1024:
            logger.warning(f"File exceeds Vercel's 4.5MB limit after reading: {total_size} bytes")
            raise HTTPException(
                status_code=413, 
                detail="File too large for Vercel deployment. Maximum size is 4.5MB. Please use a smaller file or deploy to a different platform."
            )

        # Try to decode the content or extract from PDF/CSV
        try:
            logger.info("Attempting to decode file content or extract from PDF/CSV...")
            text_content = None
            if file.content_type == "application/pdf" or (file.filename and file.filename.lower().endswith(".pdf")):
                from PyPDF2 import PdfReader
                import io
                pdf_stream = io.BytesIO(content)
                reader = PdfReader(pdf_stream)
                extracted_text = []
                for page in reader.pages:
                    extracted_text.append(page.extract_text() or "")
                text_content = "\n".join(extracted_text).strip()
                if not text_content:
                    logger.error("No extractable text found in PDF.")
                    raise HTTPException(
                        status_code=400,
                        detail="No extractable text found in PDF. Please upload a text-based PDF."
                    )
            elif file.content_type in ["text/csv", "application/csv"] or (file.filename and file.filename.lower().endswith(".csv")):
                import csv
                import io
                csv_stream = io.StringIO(content.decode("utf-8"))
                reader = csv.reader(csv_stream)
                rows = list(reader)
                # Flatten CSV rows into a string for chunking
                text_content = "\n".join([", ".join(row) for row in rows])
                if not text_content:
                    logger.error("No extractable text found in CSV.")
                    raise HTTPException(
                        status_code=400,
                        detail="No extractable text found in CSV. Please upload a valid CSV file."
                    )
            else:
                # Try decoding as utf-8, fallback to latin-1 for .txt files
                try:
                    text_content = content.decode("utf-8")
                except UnicodeDecodeError as e:
                    logger.warning(f"UTF-8 decode failed: {e}. Trying latin-1.")
                    try:
                        text_content = content.decode("latin-1")
                    except Exception as e2:
                        logger.error(f"Failed to decode .txt file as utf-8 or latin-1: {e2}")
                        raise HTTPException(
                            status_code=400,
                            detail=".txt file could not be decoded as UTF-8 or Latin-1. Please check file encoding."
                        )
            logger.info(f"Successfully obtained file content, length: {len(text_content)} characters")
        except Exception as e:
            logger.error(f"Failed to decode or extract file content: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="File must be a valid text document or a text-based PDF. PDF files with only images are not supported."
            )
        
        # Generate a simple document ID (in production, use UUID)
        document_id = str(hash(text_content))
        logger.info(f"Generated document ID: {document_id}")
        
        # Delete previous document/context before ingesting new one
        if documents:
            logger.info(f"Deleting previous document(s): {list(documents.keys())}")
            documents.clear()
            try:
                vector_db.clear()  # Assuming VectorDatabase has a clear() method
                logger.info("Cleared vector database context.")
            except Exception as e:
                logger.warning(f"Could not clear vector database: {e}")
        
        # Chunk the text into smaller segments
        logger.info("Creating text chunks...")
        chunks = chunk_text(text_content)
        logger.info(f"Created {len(chunks)} text chunks")
        
        # Create embeddings and store in vector database
        try:
            logger.info("Storing embeddings in vector database...")
            await vector_db.abuild_from_list(chunks, api_key=openai_api_key)
            logger.info("Successfully stored embeddings in vector database")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Failed to store embeddings: {str(e)}\n{tb}", exc_info=True)
            # Return detailed error info to the frontend (for debugging)
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to process document: {type(e).__name__}: {str(e)}\n{tb}"
            )
        
        # Store the original chunks for reference
        documents[document_id] = chunks
        
        logger.info(f"Upload completed successfully. Document ID: {document_id}")
        return {"document_id": document_id, "chunk_count": len(chunks)}
        
    except HTTPException as e:
        logger.error(f"HTTP error in upload: {e.status_code} - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/query")
async def query_document(request: QueryRequest):
    try:
        logger.info(f"Received query request for document {request.document_id}")
        
        if request.document_id not in documents:
            logger.warning(f"Document not found: {request.document_id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Search for relevant chunks
        try:
            relevant_chunks = vector_db.search_by_text(
                request.query,
                k=3,  # Get top 3 most relevant chunks
                return_as_text=True,
                api_key=request.api_key  # Pass the API key for embedding search
            )
            logger.info(f"Found {len(relevant_chunks)} relevant chunks")
            logger.debug(f"Chunks: {relevant_chunks}")
        except Exception as e:
            logger.error(f"Error searching vector database: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to search document")
        
        # Construct the prompt with context
        # Ensure relevant_chunks is a list of strings
        context_chunks = []
        if relevant_chunks:
            if isinstance(relevant_chunks[0], tuple):
                # If it's a list of tuples, extract the text (first element)
                context_chunks = [str(chunk[0]) for chunk in relevant_chunks]
            else:
                # If it's already a list of strings
                context_chunks = [str(chunk) for chunk in relevant_chunks]
        
        context = "\n".join(context_chunks)
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about documents. Use the provided context to answer questions accurately and concisely. If you're not sure about something, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.query}"}
        ]
        
        # Stream the response
        async def generate_response():
            try:
                # Initialize OpenAI client with the provided API key
                client = OpenAI(api_key=request.api_key)
                
                # Create a streaming chat completion request
                stream = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    stream=True
                )
                
                # Yield each chunk of the response as it becomes available
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield f"data: {json.dumps({'token': chunk.choices[0].delta.content})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Error generating response: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error handling query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
