import os
from typing import List
import re


class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks


class PDFLoader:
    def __init__(self, path: str):
        self.documents = []
        self.path = path
        print(f"PDFLoader initialized with path: {self.path}")

    def load(self):
        print(f"Loading PDF from path: {self.path}")
        print(f"Path exists: {os.path.exists(self.path)}")
        print(f"Is file: {os.path.isfile(self.path)}")
        print(f"Is directory: {os.path.isdir(self.path)}")
        print(f"File permissions: {oct(os.stat(self.path).st_mode)[-3:]}")
        
        try:
            # Try to open the file first to verify access
            with open(self.path, 'rb') as test_file:
                pass
            
            # If we can open it, proceed with loading
            self.load_file()
            
        except IOError as e:
            raise ValueError(f"Cannot access file at '{self.path}': {str(e)}")
        except Exception as e:
            raise ValueError(f"Error processing file at '{self.path}': {str(e)}")

    def load_file(self):
        with open(self.path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            self.documents.append(text)

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        
                        # Extract text from each page
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                        
                        self.documents.append(text)

    def load_documents(self):
        self.load()
        return self.documents


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split a text into overlapping chunks of approximately equal size.
    
    Args:
        text (str): The input text to be chunked
        chunk_size (int): Target size for each chunk in characters
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # If text is shorter than chunk_size, return it as a single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find the end of the chunk
        end = start + chunk_size
        
        if end >= len(text):
            # If we're at the end, just take the rest
            chunks.append(text[start:])
            break
            
        # Try to find a sentence boundary within the last 200 characters of the chunk
        last_period = text.rfind('.', end - 200, end)
        last_question = text.rfind('?', end - 200, end)
        last_exclamation = text.rfind('!', end - 200, end)
        
        # Find the latest sentence boundary
        sentence_end = max(last_period, last_question, last_exclamation)
        
        if sentence_end > start:
            # If we found a sentence boundary, use it
            end = sentence_end + 1
            chunks.append(text[start:end].strip())
            start = end - overlap
        else:
            # If no space found, just cut at a space
            last_space = text.rfind(' ', end - 200, end)
            if last_space > start:
                end = last_space
                chunks.append(text[start:end].strip())
                start = end - overlap
            else:
                # If no space found, just cut at chunk_size
                chunks.append(text[start:end].strip())
                start = end - overlap
    
    return chunks


if __name__ == "__main__":
    loader = TextFileLoader("data/KingLear.txt")
    loader.load()
    splitter = CharacterTextSplitter()
    chunks = splitter.split_texts(loader.documents)
    print(len(chunks))
    print(chunks[0])
    print("--------")
    print(chunks[1])
    print("--------")
    print(chunks[-2])
    print("--------")
    print(chunks[-1])
