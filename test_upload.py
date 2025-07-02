#!/usr/bin/env python3
"""
Test script for file upload functionality.
This script helps test the upload endpoint locally and diagnose issues.
"""

import requests
import os
import sys
from pathlib import Path

def create_test_file(size_mb: float, filename: str = "test.txt") -> str:
    """Create a test file of specified size in MB."""
    size_bytes = int(size_mb * 1024 * 1024)
    content = "A" * size_bytes
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Created test file: {filename} ({size_mb}MB)")
    return filename

def test_upload(file_path: str, api_url: str = "http://localhost:8000/api/upload"):
    """Test file upload to the API."""
    print(f"\nTesting upload of: {file_path}")
    print(f"File size: {os.path.getsize(file_path) / (1024*1024):.2f}MB")
    print(f"API URL: {api_url}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(api_url, files=files, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Document ID: {data.get('document_id')}")
            print(f"Chunk count: {data.get('chunk_count')}")
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    """Main test function."""
    print("File Upload Test Script")
    print("=" * 50)
    
    # Test different file sizes
    test_sizes = [1, 2, 4, 4.5, 5, 10]  # MB
    
    for size in test_sizes:
        filename = f"test_{size}mb.txt"
        file_path = create_test_file(size, filename)
        
        # Test local API
        test_upload(file_path, "http://localhost:8000/api/upload")
        
        # Clean up test file
        os.remove(file_path)
        print("-" * 30)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific file
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            test_upload(file_path)
        else:
            print(f"File not found: {file_path}")
    else:
        main() 