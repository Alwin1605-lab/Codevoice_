"""
Backend startup and configuration check script.
This script validates the environment and starts the server.
"""

import sys
import os
import asyncio
from config import config
from enhanced_api import router as enhanced_router

def print_banner():
    """Print a startup banner."""
    print("=" * 60)
    print("🎤 VOICE CONTROLLED IDE - BACKEND SERVER")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn", 
        "websockets",
        "groq",
        "google",
        "github",
        "dotenv"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_").replace(".", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies installed!")
    return True

def main():
    """Main startup function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    
    # Show configuration status
    print(config.get_status_report())
    
    # Check for critical missing keys
    validation = config.validate_required_keys()
    if "GEMINI_API_KEY" in validation["missing_keys"]:
        print("\n⚠️  IMPORTANT: Add your Gemini API key to .env file:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print()
    
    if "GIT_TOKEN" in validation["missing_keys"]:
        print("⚠️  IMPORTANT: Add your GitHub token to .env file:")
        print("   GIT_TOKEN=your_github_token_here")
        print()
    
    print("🚀 Backend Ready! Available endpoints:")
    print("   📁 /api/generate-ai-project/ - AI Project Generation")
    print("   🐙 /api/github/create-repo/ - GitHub Repository Creation") 
    print("   🔗 /api/ws/{session_id} - WebSocket Collaboration")
    print("   👥 /api/collaboration/invite/ - Send Collaboration Invites")
    print()
    print("Start the server with: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print()

if __name__ == "__main__":
    main()