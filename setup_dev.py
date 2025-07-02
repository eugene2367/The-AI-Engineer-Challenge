#!/usr/bin/env python3
"""
Development setup script for The AI Engineer Challenge.
This script helps set up the development environment quickly.
"""

import os
import sys
import subprocess
import platform

def run_command(command, description, check=True):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed!")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Warning: Python 3.13+ detected. Some dependencies may have compatibility issues.")
        print("💡 Consider using Python 3.11 or 3.12 for better compatibility.")
        return False
    elif version.major == 3 and version.minor >= 11:
        print("✅ Python version is compatible!")
        return True
    else:
        print("❌ Python 3.11+ is required!")
        return False

def create_requirements_compatible():
    """Create a compatible requirements file for Python 3.13+."""
    compatible_requirements = """fastapi>=0.104.0
uvicorn>=0.24.0
openai>=1.3.0
pydantic>=2.4.0
python-multipart>=0.0.6
numpy>=1.24.0
PyPDF2>=3.0.0
python-dotenv>=1.0.0
"""
    
    with open("api/requirements_compatible.txt", "w") as f:
        f.write(compatible_requirements)
    
    print("📝 Created compatible requirements file: api/requirements_compatible.txt")

def main():
    print("🚀 Setting up The AI Engineer Challenge development environment...")
    print("=" * 60)
    
    # Check Python version
    is_compatible = check_python_version()
    
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
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip", check=False)
    
    # Install API dependencies
    if not is_compatible:
        print("🔄 Creating compatible requirements for Python 3.13+...")
        create_requirements_compatible()
        requirements_file = "api/requirements_compatible.txt"
    else:
        requirements_file = "api/requirements.txt"
    
    print(f"📦 Installing dependencies from {requirements_file}...")
    if not run_command(f"{pip_cmd} install -r {requirements_file}", "Installing API dependencies"):
        print("\n💡 Alternative installation methods:")
        print("1. Try installing packages one by one:")
        print("   pip install fastapi uvicorn openai pydantic python-multipart numpy PyPDF2 python-dotenv")
        print("\n2. Use conda instead of pip:")
        print("   conda install fastapi uvicorn openai pydantic python-multipart numpy")
        print("\n3. Downgrade to Python 3.11 or 3.12:")
        print("   brew install python@3.11")
        print("   python3.11 -m venv venv")
        return False
    
    # Install frontend dependencies
    if not run_command("npm install", "Installing frontend dependencies"):
        print("⚠️  Frontend dependencies failed to install. You can try manually:")
        print("   cd frontend && npm install")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("\n2. Start the API server:")
    print("   python run_api.py")
    print("\n3. Start the frontend (in a new terminal):")
    print("   cd frontend")
    print("   npm run dev")
    print("\n4. Test the upload functionality:")
    print("   python test_upload.py")
    print("\n🌐 Your app will be available at:")
    print("   Frontend: http://localhost:3000")
    print("   API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    
    if not is_compatible:
        print("\n⚠️  Note: You're using Python 3.13+. If you encounter issues:")
        print("   - Try the alternative installation methods above")
        print("   - Consider using Python 3.11 or 3.12")
        print("   - Check the troubleshooting guide for more help")

if __name__ == "__main__":
    main() 