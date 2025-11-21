"""
Simple verification script for Groq Code Analysis API
Tests basic functionality without running the full server.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def test_groq_direct():
    """Test Groq API directly without FastAPI."""
    print("🔍 Testing Groq API Direct Connection...")
    
    # Get API key
    api_key = os.getenv("GROQ_COMPILER_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ No Groq API key found in environment variables")
        print("   Set GROQ_COMPILER_API_KEY or GROQ_API_KEY in your .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    try:
        # Initialize Groq client
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
        
        # Test code sample
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
        
        # Create a simple explanation prompt
        prompt = f"""
Explain this Python code for a beginner programmer. Use simple language and explain what it does:

```python
{test_code}
```

Provide a clear, concise explanation appropriate for someone new to programming.
"""
        
        print("🚀 Sending request to Groq...")
        
        # Make API call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        
        explanation = response.choices[0].message.content.strip()
        
        print("✅ Groq API call successful!")
        print("\\n📖 Generated Explanation:")
        print("-" * 50)
        print(explanation[:300] + "..." if len(explanation) > 300 else explanation)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False

def test_groq_module_import():
    """Test if our groq_code_analysis module can be imported."""
    print("\\n🔧 Testing Groq Code Analysis Module Import...")
    
    try:
        import groq_code_analysis
        print("✅ groq_code_analysis module imported successfully")
        
        # Test enum imports
        from groq_code_analysis import SkillLevel, ExplanationType
        print("✅ Skill levels and explanation types imported")
        print(f"   Skill Levels: {[level.value for level in SkillLevel]}")
        print(f"   Explanation Types: {[exp_type.value for exp_type in ExplanationType]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        return False

def test_environment_setup():
    """Test environment configuration."""
    print("\\n🌍 Testing Environment Setup...")
    
    # Check for .env file
    env_file_path = ".env"
    if os.path.exists(env_file_path):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found - API keys should be set in environment")
    
    # Check required packages
    try:
        import groq
        print(f"✅ groq package version: {groq.__version__ if hasattr(groq, '__version__') else 'unknown'}")
    except ImportError:
        print("❌ groq package not installed")
        return False
    
    try:
        import aiohttp
        print(f"✅ aiohttp package version: {aiohttp.__version__}")
    except ImportError:
        print("❌ aiohttp package not installed")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Groq Code Analysis Verification")
    print("=" * 50)
    
    # Run all tests
    results = []
    
    results.append(test_environment_setup())
    results.append(test_groq_module_import())
    results.append(test_groq_direct())
    
    print("\\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    if all(results):
        print("🎉 All tests passed! Groq Code Analysis is ready to use.")
        print("\\n🔗 Available API endpoints:")
        print("   POST /api/code-analysis/explain - Code explanations")
        print("   POST /api/code-analysis/analyze-error - Error analysis") 
        print("   POST /api/code-analysis/suggest-improvements - Code improvements")
        print("   GET  /api/code-analysis/skill-levels - Available skill levels")
        print("   GET  /api/code-analysis/health - Health check")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        failed_count = len(results) - sum(results)
        print(f"   {sum(results)}/{len(results)} tests passed, {failed_count} failed")