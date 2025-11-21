"""
Simple verification script for Gemini and Codex API integrations
Tests the APIs directly without requiring a running server.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_setup():
    """Test Gemini API setup and basic functionality."""
    print("🔍 Testing Gemini API Setup...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package available")
        
        # Test basic Gemini connection
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        test_prompt = "Generate a simple 'Hello World' Python script structure as JSON with file content."
        response = model.generate_content(test_prompt)
        
        if response.text:
            print("✅ Gemini API call successful!")
            print(f"   Sample response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("   Run: pip install google-generativeai>=0.8.0")
        return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_codex_setup():
    """Test Codex (OpenAI) API setup and basic functionality."""
    print("\\n🔍 Testing Codex API Setup...")
    
    api_key = os.getenv("CODEX_API_KEY")
    if not api_key:
        print("❌ CODEX_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        import openai
        print("✅ openai package available")
        
        # Test basic OpenAI connection
        client = openai.OpenAI(api_key=api_key)
        
        test_prompt = "Fix this Python code and explain the issue: def divide(a, b): return a / b\\nprint(divide(10, 0))"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": test_prompt}],
            temperature=0.2,
            max_tokens=200
        )
        
        if response.choices[0].message.content:
            print("✅ Codex (OpenAI) API call successful!")
            print(f"   Sample response: {response.choices[0].message.content[:100]}...")
            return True
        else:
            print("❌ Codex API returned empty response")
            return False
            
    except ImportError:
        print("❌ openai package not installed")
        print("   Run: pip install openai>=1.0.0")
        return False
    except Exception as e:
        print(f"❌ Codex API test failed: {e}")
        return False

def test_module_imports():
    """Test if our new modules can be imported."""
    print("\\n🔧 Testing Module Imports...")
    
    modules_to_test = [
        ("gemini_project_generator", "Gemini Project Generator"),
        ("codex_compiler", "Codex Compiler")
    ]
    
    results = []
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name} module imported successfully")
            results.append(True)
        except ImportError as e:
            print(f"❌ {display_name} module import failed: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ {display_name} module error: {e}")
            results.append(False)
    
    return all(results)

def test_integration_in_main():
    """Test if main.py includes our new integrations."""
    print("\\n🔗 Testing Main App Integration...")
    
    try:
        # Try importing main to see if it includes our modules
        import main
        print("✅ main.py imported successfully")
        
        # Check if the app has our routers
        app = main.app
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        
        gemini_routes = [r for r in routes if '/api/project-generation' in r]
        codex_routes = [r for r in routes if '/api/codex-compiler' in r]
        
        if gemini_routes:
            print(f"✅ Gemini routes found: {len(gemini_routes)} endpoints")
        else:
            print("⚠️  Gemini routes not found in app")
        
        if codex_routes:
            print(f"✅ Codex routes found: {len(codex_routes)} endpoints")
        else:
            print("⚠️  Codex routes not found in app")
        
        return len(gemini_routes) > 0 and len(codex_routes) > 0
        
    except Exception as e:
        print(f"❌ Main app integration test failed: {e}")
        return False

def show_api_summary():
    """Show summary of implemented APIs."""
    print("\\n" + "="*60)
    print("📊 Implementation Summary")
    print("="*60)
    
    print("\\n🎯 Gemini Project Generation API:")
    print("   📁 POST /api/project-generation/generate")
    print("      - Generate complete project structures")
    print("      - Supports: Web, Mobile, Desktop, API, ML projects")
    print("      - Frameworks: React, Vue, FastAPI, Flask, Flutter, etc.")
    print("   📦 POST /api/project-generation/generate-files")
    print("      - Generate and download project as ZIP")
    print("   📋 GET /api/project-generation/templates")
    print("      - Get available project templates")
    print("   🏥 GET /api/project-generation/health")
    print("      - Health check endpoint")
    
    print("\\n⚡ Codex Compiler API:")
    print("   🔨 POST /api/codex-compiler/compile")
    print("      - AI-enhanced code compilation and execution")
    print("      - Supports: Python, JavaScript, Java, C++, C#, Go, Rust")
    print("   🚀 POST /api/codex-compiler/optimize")
    print("      - Code optimization suggestions")
    print("   🐛 POST /api/codex-compiler/debug")
    print("      - Intelligent debugging assistance")
    print("   📋 GET /api/codex-compiler/languages")
    print("      - Get supported programming languages")
    print("   🏥 GET /api/codex-compiler/health")
    print("      - Health check endpoint")
    
    print("\\n🔗 Enhanced Compilation Hierarchy:")
    print("   1. Codex (Premium AI-powered compilation)")
    print("   2. Judge0 (Free community service)")
    print("   3. Remote execution services")
    print("   4. Local compilation")
    print("   5. Groq simulation (fallback)")
    
    print("\\n🔧 Configuration:")
    print("   • GEMINI_API_KEY: Google Gemini for project generation")
    print("   • CODEX_API_KEY: OpenAI for code analysis and compilation")
    print("   • EXEC_PROVIDER: Set to 'codex' to prioritize Codex compilation")

if __name__ == "__main__":
    print("🚀 Gemini & Codex Integration Verification")
    print("="*50)
    
    # Run verification tests
    results = []
    
    results.append(test_gemini_setup())
    results.append(test_codex_setup())
    results.append(test_module_imports())
    results.append(test_integration_in_main())
    
    # Show results
    print("\\n" + "="*50)
    print("📊 Verification Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 All verifications passed! Ready to use Gemini & Codex APIs.")
    else:
        print(f"⚠️  {total - passed} verifications failed. Check the details above.")
        print(f"   {passed}/{total} tests passed")
    
    # Show API summary regardless of test results
    show_api_summary()
    
    print("\\n🚀 Next Steps:")
    print("   1. Start the backend server: python -m uvicorn main:app --host 0.0.0.0 --port 8001")
    print("   2. Test the APIs using the generated test script: python test_gemini_codex.py")
    print("   3. Use the enhanced compilation in your Voice Controlled IDE frontend")