# Import required FastAPI components for building the API
from fastapi import FastAPI, UploadFile, File, HTTPException
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

# Initialize our components
chat_model = ChatOpenAI(model_name="gpt-4-turbo-preview")
vector_db = VectorDatabase()

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
                model=request.model,
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
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")
        
        # Generate a simple document ID (in production, use UUID)
        document_id = str(hash(text_content))
        
        # Chunk the text into smaller segments
        chunks = chunk_text(text_content)
        
        # Create embeddings and store in vector database
        await vector_db.abuild_from_list(chunks)
        
        # Store the original chunks for reference
        documents[document_id] = chunks
        
        return {"document_id": document_id, "chunk_count": len(chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/query")
async def query_document(request: QueryRequest):
    try:
        if request.document_id not in documents:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Search for relevant chunks
        relevant_chunks = vector_db.search_by_text(
            request.query,
            k=3,  # Get top 3 most relevant chunks
            return_as_text=True
        )
        
        # Construct the prompt with context
        context = "\n".join(relevant_chunks)
        messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions about documents. Use the provided context to answer questions accurately and concisely. If you're not sure about something, say so."},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.query}"}
        ]
        
        # Stream the response
        async def generate_response():
            async for token in chat_model.astream(messages):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream"
        )
    except Exception as e:
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
