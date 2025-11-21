"""
Test script for Gemini Project Generation and Codex Compilation APIs
Validates both AI-powered project generation and advanced code compilation.
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CODEX_API_KEY = os.getenv("CODEX_API_KEY")

# Test data
SIMPLE_PYTHON_CODE = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def main():
    num = 10
    print(f"Fibonacci of {num}: {fibonacci(num)}")

if __name__ == "__main__":
    main()
"""

BUGGY_PYTHON_CODE = """
def divide_numbers(a, b):
    result = a / b  # This will cause ZeroDivisionError
    return result

def main():
    print(divide_numbers(10, 0))
    print(divide_numbers(10, 2))

main()
"""

OPTIMIZATION_TARGET_CODE = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

numbers = [64, 34, 25, 12, 22, 11, 90]
sorted_numbers = bubble_sort(numbers.copy())
print("Sorted array:", sorted_numbers)
"""

async def test_gemini_health():
    """Test Gemini project generation health check."""
    print("\\n🏥 Testing Gemini Health Check...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/project-generation/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Gemini service healthy: {result}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Gemini health check failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False

async def test_codex_health():
    """Test Codex compiler health check."""
    print("\\n🏥 Testing Codex Health Check...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/codex-compiler/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Codex service healthy: {result}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Codex health check failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False

async def test_gemini_project_generation():
    """Test Gemini project generation functionality."""
    print("\\n🏗️ Testing Gemini Project Generation...")
    
    async with aiohttp.ClientSession() as session:
        # Test project templates endpoint
        try:
            async with session.get(f"{BASE_URL}/api/project-generation/templates") as response:
                if response.status == 200:
                    templates = await response.json()
                    print(f"✅ Project templates retrieved: {len(templates.get('project_types', []))} types")
                else:
                    print(f"❌ Failed to get templates ({response.status})")
                    return False
        except Exception as e:
            print(f"❌ Templates request failed: {e}")
            return False
        
        # Test project generation
        project_request = {
            "project_name": "test_fastapi_app",
            "project_type": "api_server",
            "framework": "fastapi",
            "complexity": "intermediate",
            "description": "A simple REST API for user management",
            "features": ["user_authentication", "database_integration"],
            "technologies": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
            "include_tests": True,
            "include_docker": True,
            "authentication": True,
            "database_type": "postgresql"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/project-generation/generate",
                json=project_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Project generation successful")
                    
                    project_data = result.get("project", {})
                    structure = project_data.get("project_structure", {})
                    files = structure.get("files", {})
                    folders = structure.get("folders", [])
                    
                    print(f"   📁 Folders created: {len(folders)}")
                    print(f"   📄 Files created: {len(files)}")
                    
                    if "setup_instructions" in project_data:
                        print(f"   📋 Setup steps: {len(project_data['setup_instructions'])}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Project generation failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Generation request failed: {e}")
            return False

async def test_codex_compilation():
    """Test Codex compilation functionality."""
    print("\\n⚡ Testing Codex Code Compilation...")
    
    async with aiohttp.ClientSession() as session:
        # Test supported languages
        try:
            async with session.get(f"{BASE_URL}/api/codex-compiler/languages") as response:
                if response.status == 200:
                    langs = await response.json()
                    print(f"✅ Supported languages: {len(langs.get('supported_languages', []))}")
                else:
                    print(f"❌ Failed to get languages ({response.status})")
                    return False
        except Exception as e:
            print(f"❌ Languages request failed: {e}")
            return False
        
        # Test code compilation
        compilation_request = {
            "code": SIMPLE_PYTHON_CODE,
            "language": "python",
            "mode": "compile_and_run",
            "timeout": 30,
            "explain_output": True
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/codex-compiler/compile",
                json=compilation_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Codex compilation successful")
                    
                    exec_result = result.get("execution_result", {})
                    success = result.get("success", False)
                    
                    print(f"   🎯 Execution success: {success}")
                    if exec_result.get("runtime_output"):
                        print(f"   📤 Output: {exec_result['runtime_output'][:100]}...")
                    
                    if result.get("codex_analysis"):
                        print("   🧠 Codex analysis provided")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Compilation failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Compilation request failed: {e}")
            return False

async def test_codex_debugging():
    """Test Codex debugging functionality."""
    print("\\n🐛 Testing Codex Code Debugging...")
    
    async with aiohttp.ClientSession() as session:
        debug_request = {
            "code": BUGGY_PYTHON_CODE,
            "language": "python",
            "error_description": "ZeroDivisionError occurs when running this code",
            "debug_context": "Function divides numbers but doesn't handle zero division"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/codex-compiler/debug",
                json=debug_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Codex debugging successful")
                    
                    debug_result = result.get("debug_result", {})
                    issues = debug_result.get("issues_found", [])
                    suggestions = debug_result.get("debug_suggestions", [])
                    
                    print(f"   🔍 Issues found: {len(issues)}")
                    print(f"   💡 Debug suggestions: {len(suggestions)}")
                    
                    if debug_result.get("fixed_code"):
                        print("   🔧 Fixed code provided")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Debugging failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Debug request failed: {e}")
            return False

async def test_codex_optimization():
    """Test Codex code optimization functionality."""
    print("\\n🚀 Testing Codex Code Optimization...")
    
    async with aiohttp.ClientSession() as session:
        optimization_request = {
            "code": OPTIMIZATION_TARGET_CODE,
            "language": "python",
            "optimization_goals": ["performance", "readability"],
            "target_platform": "general",
            "maintain_functionality": True
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/codex-compiler/optimize",
                json=optimization_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Codex optimization successful")
                    
                    opt_result = result.get("optimization_result", {})
                    optimizations = opt_result.get("optimizations_applied", [])
                    
                    print(f"   ⚡ Optimizations applied: {len(optimizations)}")
                    
                    if opt_result.get("performance_improvement"):
                        print(f"   📊 Performance improvement: {opt_result['performance_improvement']}")
                    
                    if opt_result.get("optimized_code"):
                        print("   ✨ Optimized code provided")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Optimization failed ({response.status}): {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Optimization request failed: {e}")
            return False

async def test_integration_with_compile_api():
    """Test integration of Codex with the main compile API."""
    print("\\n🔗 Testing Integration with Main Compile API...")
    
    async with aiohttp.ClientSession() as session:
        # Test compile providers endpoint
        try:
            async with session.get(f"{BASE_URL}/compile/providers") as response:
                if response.status == 200:
                    providers = await response.json()
                    services = providers.get("supported_services", [])
                    
                    if "codex" in services:
                        print("✅ Codex integrated in compile API")
                        print(f"   🛠️ Available services: {', '.join(services)}")
                        return True
                    else:
                        print("❌ Codex not found in compile API services")
                        return False
                else:
                    print(f"❌ Failed to get compile providers ({response.status})")
                    return False
        except Exception as e:
            print(f"❌ Providers request failed: {e}")
            return False

async def main():
    """Run all tests."""
    print("🚀 Starting Gemini & Codex Integration Tests")
    print(f"🔑 Gemini API Key configured: {'Yes' if GEMINI_API_KEY else 'No'}")
    print(f"🔑 Codex API Key configured: {'Yes' if CODEX_API_KEY else 'No'}")
    print(f"🌐 Testing against: {BASE_URL}")
    
    if not GEMINI_API_KEY:
        print("⚠️  Warning: GEMINI_API_KEY not found in environment variables")
    
    if not CODEX_API_KEY:
        print("⚠️  Warning: CODEX_API_KEY not found in environment variables")
    
    # Run all tests
    test_results = []
    
    test_results.append(await test_gemini_health())
    test_results.append(await test_codex_health())
    test_results.append(await test_gemini_project_generation())
    test_results.append(await test_codex_compilation())
    test_results.append(await test_codex_debugging())
    test_results.append(await test_codex_optimization())
    test_results.append(await test_integration_with_compile_api())
    
    # Summary
    print("\\n" + "="*60)
    print("📊 Test Results Summary:")
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        print("🎉 All tests passed! Gemini & Codex integrations are working perfectly.")
        print("\\n🔗 Available APIs:")
        print("   📁 Gemini Project Generation:")
        print("      POST /api/project-generation/generate")
        print("      POST /api/project-generation/generate-files") 
        print("      GET  /api/project-generation/templates")
        print("   ⚡ Codex Compiler:")
        print("      POST /api/codex-compiler/compile")
        print("      POST /api/codex-compiler/optimize")
        print("      POST /api/codex-compiler/debug")
        print("      GET  /api/codex-compiler/languages")
        print("   🔗 Enhanced Compile API:")
        print("      POST /compile/ (now includes Codex as premium option)")
    else:
        print(f"❌ {total - passed} tests failed. Please check the errors above.")
        print(f"   {passed}/{total} tests passed")
    
    print("\\n🎯 Integration Status:")
    print("   • Gemini: Intelligent project scaffolding and generation")
    print("   • Codex: AI-powered code compilation, debugging, and optimization")
    print("   • Enhanced compilation hierarchy: Codex → Judge0 → Remote → Local → Groq")

if __name__ == "__main__":
    asyncio.run(main())