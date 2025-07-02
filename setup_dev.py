#!/usr/bin/env python3
"""
Development setup script for The AI Engineer Challenge.
This script helps set up the development environment quickly.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Setting up The AI Engineer Challenge development environment...")
    print("=" * 60)
    
    # Check if Python 3 is available
    python_cmd = "python3" if platform.system() != "Windows" else "python"
    
    # Create virtual environment
    if not os.path.exists("venv"):
        if not run_command(f"{python_cmd} -m venv venv", "Creating virtual environment"):
            return False
    else:
        print("✅ Virtual environment already exists")
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install API dependencies
    if not run_command(f"{pip_cmd} install -r api/requirements.txt", "Installing API dependencies"):
        return False
    
    # Install frontend dependencies
    if not run_command("npm install", "Installing frontend dependencies"):
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start the API server:")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("   python run_api.py")
    print("\n2. Start the frontend (in a new terminal):")
    print("   cd frontend")
    print("   npm run dev")
    print("\n3. Test the upload functionality:")
    print("   python test_upload.py")
    print("\n🌐 Your app will be available at:")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 