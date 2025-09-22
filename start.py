#!/usr/bin/env python3
"""
Startup script for AI Task Planning Agent
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'requests', 
        'sqlalchemy', 'python-dotenv', 'pydantic', 'jinja2'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install them with: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("⚠️  No .env file found. Creating from template...")
        
        # Copy from .env.example
        example_path = Path('.env.example')
        if example_path.exists():
            with open(example_path, 'r') as f:
                content = f.read()
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("❗ Please add your OpenAI API key to the .env file")
            return False
        else:
            print("❌ Neither .env nor .env.example file found")
            return False
    
    # Check for OpenAI API key
    with open(env_path, 'r') as f:
        content = f.read()
    
    if 'OPENAI_API_KEY=your_openai_api_key_here' in content:
        print("❗ Please update your OpenAI API key in the .env file")
        print("   The current key is just a placeholder")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🤖 AI Task Planning Agent - Startup Check")
    print("=" * 50)
    
    # Check current directory
    if not Path('main.py').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies installed")
    
    # Check environment file
    print("\n🔑 Checking environment configuration...")
    env_ready = check_env_file()
    
    if env_ready:
        print("✅ Environment configuration ready")
    else:
        print("\n🚀 After setting up your API keys, run:")
        print("   python start.py")
        sys.exit(1)
    
    # Start the application
    print("\n🚀 Starting AI Task Planning Agent...")
    print("🌐 Application will be available at: http://localhost:8000")
    print("📝 Press Ctrl+C to stop the server\n")
    
    # Import and run
    try:
        import uvicorn
        from main import app
        
        uvicorn.run(
            "main:app",
            host=os.getenv("HOST", "localhost"),
            port=int(os.getenv("PORT", 8000)),
            reload=True,
            reload_dirs=[".", "./agent", "./tools", "./database", "./web"]
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()