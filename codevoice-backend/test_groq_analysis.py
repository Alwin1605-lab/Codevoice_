"""
Test script for Groq Code Analysis API
Tests the intelligent code explanation and error analysis features.
"""

import asyncio
import aiohttp
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8001"
GROQ_API_KEY = os.getenv("GROQ_COMPILER_API_KEY") or os.getenv("GROQ_API_KEY")

# Test code samples
PYTHON_CODE = """
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the functions
print(f"Factorial of 5: {factorial(5)}")
print(f"Fibonacci of 10: {fibonacci(10)}")
"""

PYTHON_ERROR_CODE = """
def divide_numbers(a, b):
    result = a / b  # This will cause ZeroDivisionError
    return result

print(divide_numbers(10, 0))
"""

JAVASCRIPT_CODE = """
function bubbleSort(arr) {
    let n = arr.length;
    for (let i = 0; i < n - 1; i++) {
        for (let j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                let temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
    return arr;
}

const numbers = [64, 34, 25, 12, 22, 11, 90];
console.log("Sorted array:", bubbleSort(numbers));
"""

async def test_code_explanation():
    """Test code explanation with different skill levels."""
    print("\\n🧠 Testing Code Explanation...")
    
    async with aiohttp.ClientSession() as session:
        for skill_level in ["beginner", "intermediate", "advanced", "expert"]:
            print(f"\\n📊 Testing {skill_level} level explanation:")
            
            payload = {
                "code": PYTHON_CODE,
                "language": "python",
                "user_level": skill_level,
                "explanation_type": "overview",
                "focus_areas": ["algorithm", "recursion"]
            }
            
            try:
                async with session.post(
                    f"{BASE_URL}/api/code-analysis/explain",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ {skill_level.capitalize()} explanation generated")
                        print(f"Preview: {result['explanation'][:150]}...")
                    else:
                        error_text = await response.text()
                        print(f"❌ Error ({response.status}): {error_text}")
            except Exception as e:
                print(f"❌ Request failed: {e}")

async def test_error_analysis():
    """Test error analysis functionality."""
    print("\\n🔍 Testing Error Analysis...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "code": PYTHON_ERROR_CODE,
            "language": "python",
            "error_message": "ZeroDivisionError: division by zero",
            "user_level": "intermediate",
            "include_fix": True
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/code-analysis/analyze-error",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Error analysis completed")
                    print(f"Analysis: {result['analysis'][:200]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ Error analysis failed ({response.status}): {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def test_code_improvements():
    """Test code improvement suggestions."""
    print("\\n💡 Testing Code Improvement Suggestions...")
    
    async with aiohttp.ClientSession() as session:
        payload = {
            "code": JAVASCRIPT_CODE,
            "language": "javascript",
            "user_level": "advanced",
            "explanation_type": "optimization"
        }
        
        try:
            async with session.post(
                f"{BASE_URL}/api/code-analysis/suggest-improvements",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Improvement suggestions generated")
                    print(f"Suggestions: {result['suggestions'][:200]}...")
                else:
                    error_text = await response.text()
                    print(f"❌ Improvement analysis failed ({response.status}): {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def test_skill_levels():
    """Test skill levels endpoint."""
    print("\\n📚 Testing Skill Levels Endpoint...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/code-analysis/skill-levels") as response:
                if response.status == 200:
                    result = await response.json()
                    print("✅ Skill levels retrieved")
                    print(f"Available levels: {result['skill_levels']}")
                    print(f"Explanation types: {result['explanation_types']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get skill levels ({response.status}): {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def test_health_check():
    """Test health check endpoint."""
    print("\\n🏥 Testing Health Check...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/code-analysis/health") as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Service healthy: {result}")
                else:
                    error_text = await response.text()
                    print(f"❌ Health check failed ({response.status}): {error_text}")
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def main():
    """Run all tests."""
    print("🚀 Starting Groq Code Analysis API Tests")
    print(f"🔑 API Key configured: {'Yes' if GROQ_API_KEY else 'No'}")
    print(f"🌐 Testing against: {BASE_URL}")
    
    if not GROQ_API_KEY:
        print("⚠️  Warning: GROQ_COMPILER_API_KEY or GROQ_API_KEY not found in environment")
        print("   Tests may fail if the API requires authentication")
    
    # Run all tests
    await test_health_check()
    await test_skill_levels()
    await test_code_explanation()
    await test_error_analysis()
    await test_code_improvements()
    
    print("\\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())