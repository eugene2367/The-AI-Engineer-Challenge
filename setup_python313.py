#!/usr/bin/env python3
"""
Specialized setup script for Python 3.13+ users.
This script installs packages one by one to avoid compatibility issues.
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
    print("🐍 Python 3.13+ Setup Script")
    print("=" * 40)
    print("This script installs packages one by one to avoid compatibility issues.")
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Not in a virtual environment!")
        print("💡 Consider creating one first:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print()
    
    # Check if Python 3 is available
    python_cmd = "python3" if platform.system() != "Windows" else "python"
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        if not run_command(f"{python_cmd} -m venv venv", "Creating virtual environment"):
            return False
    
    # Activate virtual environment and install dependencies
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
    else:
        pip_cmd = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip")
    
    # Install packages one by one with compatible versions
    packages = [
        ("fastapi>=0.104.0", "FastAPI web framework"),
        ("uvicorn>=0.24.0", "ASGI server"),
        ("openai>=1.3.0", "OpenAI API client"),
        ("pydantic>=2.4.0", "Data validation"),
        ("python-multipart>=0.0.6", "File upload support"),
        ("numpy>=1.24.0", "Numerical computing"),
        ("PyPDF2>=3.0.0", "PDF processing"),
        ("python-dotenv>=1.0.0", "Environment variables"),
    ]
    
    failed_packages = []
    
    for package, description in packages:
        if not run_command(f"{pip_cmd} install {package}", f"Installing {description}"):
            failed_packages.append(package)
    
    if failed_packages:
        print(f"\n❌ Failed to install {len(failed_packages)} packages:")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 Try these alternatives:")
        print("1. Install without version constraints:")
        for package in failed_packages:
            base_package = package.split('>=')[0].split('==')[0]
            print(f"   pip install {base_package}")
        print("\n2. Use conda instead:")
        print("   conda install fastapi uvicorn openai pydantic numpy")
        print("\n3. Downgrade to Python 3.11:")
        print("   brew install python@3.11")
        print("   python3.11 -m venv venv")
        return False
    
    # Install frontend dependencies
    if not run_command("npm install", "Installing frontend dependencies"):
        print("⚠️  Frontend dependencies failed. Try manually:")
        print("   cd frontend && npm install")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    print("   source venv/bin/activate")
    print("\n2. Test the API:")
    print("   python run_api.py")
    print("\n3. Start the frontend:")
    print("   cd frontend && npm run dev")

if __name__ == "__main__":
    main() 