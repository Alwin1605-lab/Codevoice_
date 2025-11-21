"""
Test script for Judge0 integration
"""

import asyncio
from judge0_executor import execute_with_judge0, get_language_info

async def test_judge0():
    """Test Judge0 with different languages."""
    
    print("🚀 Testing Judge0 Integration...")
    print()
    
    # Get language info
    info = get_language_info()
    print(f"📋 Service: {info['service']}")
    print(f"📋 Supported Languages: {len(info['supported_languages'])}")
    print(f"📋 Free Tier: {info['free_tier']}")
    print(f"📋 Works with localhost: {info['works_with_localhost']}")
    print()
    
    # Test cases
    test_cases = [
        {
            "language": "python",
            "code": "print('Hello from Python!')\nprint('Math test:', 2 + 3)",
            "inputs": "",
            "name": "Python Hello World"
        },
        {
            "language": "javascript",
            "code": "console.log('Hello from JavaScript!');\nconsole.log('Math test:', 2 + 3);",
            "inputs": "",
            "name": "JavaScript Hello World"
        },
        {
            "language": "java",
            "code": """
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello from Java!");
        System.out.println("Math test: " + (2 + 3));
    }
}
            """,
            "inputs": "",
            "name": "Java Hello World"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"🧪 Test {i}: {test['name']}")
        print(f"Language: {test['language']}")
        
        try:
            stdout, stderr, compile_output = await execute_with_judge0(
                test['language'], 
                test['code'], 
                test['inputs']
            )
            
            print(f"✅ Success!")
            if stdout:
                print(f"📤 Output:\n{stdout}")
            if stderr:
                print(f"⚠️  Stderr:\n{stderr}")
            if compile_output:
                print(f"🔧 Compile Output:\n{compile_output}")
                
        except Exception as e:
            print(f"❌ Failed: {e}")
        
        print("-" * 50)
        print()

if __name__ == "__main__":
    asyncio.run(test_judge0())