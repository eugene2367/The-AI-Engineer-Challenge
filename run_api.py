#!/usr/bin/env python3
"""
Simple script to run the FastAPI application from the root directory.
This avoids module import issues when running from subdirectories.
"""

import os
import sys
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app from the api directory
from api.app import app

if __name__ == "__main__":
    print("🚀 Starting FastAPI server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/api/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True  # Enable auto-reload for development
    ) 