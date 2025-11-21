import subprocess
import tempfile
import os
import sys
import shutil
import re

ext_map = {
    "python": "py",
    "javascript": "js",
    "cpp": "cpp",
    "java": "java",
    "c": "c"
}

def check_executable(name):
    """Return path to executable or None."""
    return shutil.which(name)

def wrap_runnable_code(language, code):
    match = re.search(r"def\s+(\w+)\s*\(([^)]*)\)", code) if language.lower() == "python" else None
    java_match = re.search(r"(?:public\s+)?(?:static\s+)?\w+\s+(\w+)\s*\(([^)]*)\)", code) if language.lower() == "java" else None
    cpp_match = re.search(r"(?:vector<\w+>|int|void|string)\s+(\w+)\s*\(([^)]*)\)", code) if language.lower() == "cpp" else None
    js_match = re.search(r"function\s+(\w+)\s*\(([^)]*)\)", code) if language.lower() == "javascript" else None
    c_match = re.search(r"(?:int|void|float|double|char)\s+(\w+)\s*\(([^)]*)\)", code) if language.lower() == "c" else None

    func_name, params = None, []
    if match:
        func_name = match.group(1)
        params = [p.strip().split("=")[0] for p in match.group(2).split(",") if p.strip()]
    elif java_match:
        func_name = java_match.group(1)
        params = [p.strip().split()[-1] for p in java_match.group(2).split(",") if p.strip()]
    elif cpp_match:
        func_name = cpp_match.group(1)
        params = [p.strip().split()[-1] for p in cpp_match.group(2).split(",") if p.strip()]
    elif js_match:
        func_name = js_match.group(1)
        params = [p.strip() for p in js_match.group(2).split(",") if p.strip()]
    elif c_match:
        func_name = c_match.group(1)
        params = [p.strip().split()[-1] for p in c_match.group(2).split(",") if p.strip()]

    example_values = []
    for p in params:
        if "num" in p.lower() or "arr" in p.lower() or "list" in p.lower():
            example_values.append("[2, 7, 11, 15]" if language.lower() not in ["java", "cpp", "c"] else "{2, 7, 11, 15}")
        elif "target" in p.lower() or "k" in p.lower():
            example_values.append("9")
        elif "str" in p.lower() or p.lower() == "s":
            example_values.append('"example"')
        else:
            example_values.append("0")
    args_str = ", ".join(example_values)

    if language.lower() == "python":
        if "if __name__" not in code and func_name:
            code += f"\n\nif __name__ == \"__main__\":\n    print({func_name}({args_str}))\n"
        return code
    elif language.lower() == "java":
        code = re.sub(r'public class\s+\w+', 'public class Main', code)
        if "public static void main" not in code and func_name:
            code = f"""
public class Main {{
    {code}
    public static void main(String[] args) {{
        var result = {func_name}({args_str});
        System.out.println(result);
    }}
}}
"""
        return code
    elif language.lower() == "cpp":
        if "int main" not in code and func_name:
            code = f"""
#include <iostream>
#include <vector>
using namespace std;
{code}
int main() {{
    auto result = {func_name}({args_str});
    cout << result << endl;
    return 0;
}}
"""
            code = code.replace("{{", "{").replace("}}", "}")
        return code
    elif language.lower() == "c":
        if "int main" not in code and func_name:
            code = f"""
#include <stdio.h>
{code}
int main() {{
    int result = {func_name}({args_str});
    printf("%d\\n", result);
    return 0;
}}
"""
            code = code.replace("{{", "{").replace("}}", "}")
        return code
    elif language.lower() == "javascript":
        if "console.log" not in code and func_name:
            code += f"\n\nconsole.log({func_name}({args_str}));\n"
        return code
    return code

def run_locally(language, code, stdin=""):
    """
    Run source code using local compilers/interpreters.
    WARNING: This executes arbitrary code on the host. Use only for trusted input
    or during development inside an isolated VM/docker container.
    Returns (stdout, stderr, compile_output)
    """
    language = language.lower()
    if language not in ext_map:
        return "", f"Language {language} not supported.", None
    ext = ext_map[language]
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, f"Main.{ext}")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(code)
        stdout = ""
        stderr = ""
        compile_output = ""
        try:
            if language == "python":
                py_exec = sys.executable or check_executable("python")
                if not py_exec:
                    return "", "Python executable not found on PATH.", None
                proc = subprocess.run([py_exec, src_path],
                                      input=stdin,
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
                stdout, stderr = proc.stdout, proc.stderr
            elif language == "javascript":
                node = check_executable("node")
                if not node:
                    return "", "Node.js executable not found on PATH.", None
                proc = subprocess.run([node, src_path],
                                      input=stdin,
                                      capture_output=True,
                                      text=True,
                                      timeout=10)
                stdout, stderr = proc.stdout, proc.stderr
            elif language == "cpp":
                gpp = check_executable("g++")
                if not gpp:
                    return "", "g++ not found on PATH.", None
                exe_path = os.path.join(tmpdir, "program.exe" if os.name == "nt" else "program")
                compile_proc = subprocess.run([gpp, src_path, "-O2", "-std=c++17", "-o", exe_path],
                                              capture_output=True, text=True, timeout=20)
                compile_output = compile_proc.stderr or compile_proc.stdout
                if compile_proc.returncode != 0:
                    return "", "", compile_output
                run_cmd = [exe_path] if os.name != "nt" else [exe_path]
                proc = subprocess.run(run_cmd, input=stdin, capture_output=True, text=True, timeout=5)
                stdout, stderr = proc.stdout, proc.stderr
            elif language == "java":
                javac = check_executable("javac")
                java = check_executable("java")
                if not javac or not java:
                    return "", "javac/java not found on PATH.", None
                src_path = os.path.join(tmpdir, "Main.java")
            elif language == "c":
                gcc = check_executable("gcc")
                if not gcc:
                    return "", "gcc not found on PATH.", None
                exe_path = os.path.join(tmpdir, "program.exe" if os.name == "nt" else "program")
                compile_proc = subprocess.run([gcc, src_path, "-O2", "-std=c99", "-o", exe_path],
                                              capture_output=True, text=True, timeout=20)
                compile_output = compile_proc.stderr or compile_proc.stdout
                if compile_proc.returncode != 0:
                    return "", "", compile_output
                run_cmd = [exe_path] if os.name != "nt" else [exe_path]
                proc = subprocess.run(run_cmd, input=stdin, capture_output=True, text=True, timeout=5)
                stdout, stderr = proc.stdout, proc.stderr
                with open(src_path, "w", encoding="utf-8") as f:
                    f.write(code)
                compile_proc = subprocess.run(
                    ["javac", "--release", "8", "Main.java"],
                    capture_output=True, text=True, timeout=20, cwd=tmpdir
                )
                compile_output = compile_proc.stderr or compile_proc.stdout
                if compile_proc.returncode != 0:
                    return "", "", compile_output
                proc = subprocess.run(
                    [java, "-cp", tmpdir, "Main"],
                    input=stdin, capture_output=True, text=True, timeout=5
                )
                stdout, stderr = proc.stdout, proc.stderr
        except subprocess.TimeoutExpired:
            return "", "Execution timed out.", compile_output
        except Exception as e:
            return "", f"Execution error: {e}", compile_output
        return stdout, stderr, compile_output
