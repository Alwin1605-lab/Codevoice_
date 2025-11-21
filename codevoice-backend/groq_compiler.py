import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    # Use dedicated compiler API key if available, fallback to main key
    api_key = os.getenv("GROQ_COMPILER_API_KEY") or os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_COMPILER_API_KEY or GROQ_API_KEY not set in environment")
    return Groq(api_key=api_key)

def compile_with_groq(language: str, code: str, stdin: str = "") -> tuple[str, str, str]:
    """
    Use Groq to simulate code compilation and execution.
    Returns (stdout, stderr, compile_output) format to match other compilers.
    """
    try:
        client = get_groq_client()
        
        # Build a comprehensive prompt for code execution simulation
        prompt = f"""You are a {language} code execution simulator. Analyze the following code and predict its exact output.

IMPORTANT RULES:
1. Execute the code step by step mentally
2. Return ONLY the program output that would appear on stdout
3. If there are syntax errors, return them as compilation errors
4. If there are runtime errors, return them as runtime errors
5. If the code runs successfully with no output, return nothing
6. Do not add explanations, just simulate the exact output

Language: {language}
Code:
```{language}
{code}
```
"""

        if stdin.strip():
            prompt += f"\nInput (stdin):\n{stdin}\n"
        
        prompt += "\nSimulated Output:"

        # Use a suitable model for code analysis
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for more deterministic output
            max_tokens=2048
        )
        
        output = response.choices[0].message.content.strip()
        
        # Parse the response to determine if it's an error or output
        if any(keyword in output.lower() for keyword in ['error', 'exception', 'traceback', 'syntax', 'invalid']):
            # Likely an error
            if any(keyword in output.lower() for keyword in ['syntax', 'invalid syntax', 'compilation']):
                return "", "", output  # Compilation error
            else:
                return "", output, ""  # Runtime error
        else:
            # Normal output
            return output, "", ""
            
    except Exception as e:
        return "", f"Groq compilation failed: {str(e)}", ""

def compile_with_groq_analysis(language: str, code: str, stdin: str = "") -> tuple[str, str, str]:
    """
    Enhanced version that asks Groq to analyze and then execute code.
    """
    try:
        client = get_groq_client()
        
        # First, ask Groq to analyze the code for issues
        analysis_prompt = f"""Analyze this {language} code for syntax errors, logical issues, and predict its behavior:

Code:
```{language}
{code}
```

Respond in JSON format:
{{
    "has_syntax_errors": boolean,
    "syntax_errors": "description of syntax errors if any",
    "will_run": boolean,
    "expected_output": "predicted output",
    "runtime_errors": "potential runtime errors if any"
}}
"""

        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.1,
            max_tokens=1024
        )
        
        # Try to parse JSON response
        import json
        try:
            analysis = json.loads(response.choices[0].message.content.strip())
            
            if analysis.get("has_syntax_errors", False):
                return "", "", analysis.get("syntax_errors", "Syntax error detected")
            
            if not analysis.get("will_run", True):
                return "", analysis.get("runtime_errors", "Runtime error"), ""
            
            # If code looks good, return the predicted output
            output = analysis.get("expected_output", "")
            if stdin.strip():
                # Re-run with stdin consideration
                return compile_with_groq(language, code, stdin)
            
            return output, "", ""
            
        except json.JSONDecodeError:
            # Fallback to simple simulation
            return compile_with_groq(language, code, stdin)
            
    except Exception as e:
        return "", f"Groq analysis failed: {str(e)}", ""