import os
from typing import Tuple, List

import httpx
from dotenv import load_dotenv

load_dotenv()


class RemoteExecError(Exception):
    pass


def _get_provider() -> str:
    return os.getenv("EXEC_PROVIDER", os.getenv("USE_REMOTE_EXECUTION", "")).strip().lower()


# Basic default mappings for Judge0 CE (may vary by deployment)
JUDGE0_LANGUAGE_IDS = {
    # language -> language_id
    "python": 71,       # Python (3.8.1) – common in Judge0 CE
    "python3": 71,
    "javascript": 63,  # Node.js (12.x)
    "nodejs": 63,
    "cpp": 54,         # C++ (G++ 9.2.0 or newer)
    "c++": 54,
    "c": 50,           # C (GCC 9.2.0)
    "java": 62,        # Java (OpenJDK 13)
}


def run_remote(language: str, code: str, stdin: str = "") -> Tuple[str, str, str]:
    """
    Execute code using a remote provider selected via environment variables.

    Provider selection (by priority):
    - EXEC_PROVIDER=piston|judge0|local
    - USE_REMOTE_EXECUTION=true (defaults to 'piston')

    Returns (stdout, stderr, compile_output) just like the local runner.
    """
    provider = _get_provider()
    if provider in ("", "false", "0", "no", "local"):
        raise RemoteExecError("Remote provider not enabled")

    if provider == "judge0":
        return _run_via_judge0(language, code, stdin)
    if provider == "jdoodle":
        return _run_via_jdoodle(language, code, stdin)
    if provider == "onecompiler":
        return _run_via_onecompiler(language, code, stdin)
    # default to piston
    return _run_via_piston(language, code, stdin)


def _run_via_judge0(language: str, code: str, stdin: str) -> Tuple[str, str, str]:
    base_url = os.getenv("JUDGE0_URL", "https://judge0-ce.p.rapidapi.com")
    # Most Judge0 deployments support the "wait=true" query to return sync
    submit_url = f"{base_url.rstrip('/')}/submissions?base64_encoded=false&wait=true"

    headers = {}
    # RapidAPI gateway headers (optional)
    rapidapi_key = os.getenv("RAPIDAPI_KEY") or os.getenv("JUDGE0_RAPIDAPI_KEY")
    rapidapi_host = os.getenv("RAPIDAPI_HOST")
    if rapidapi_key and "rapidapi" in base_url:
        headers.update({
            "X-RapidAPI-Key": rapidapi_key,
            "X-RapidAPI-Host": rapidapi_host or "judge0-ce.p.rapidapi.com",
        })

    language_id = JUDGE0_LANGUAGE_IDS.get(language.lower())
    if not language_id:
        return "", f"Language '{language}' is not mapped for Judge0.", None

    payload = {
        "language_id": language_id,
        "source_code": code,
        "stdin": stdin or "",
    }

    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(submit_url, json=payload, headers=headers)
            if resp.status_code >= 400:
                return "", f"Judge0 error: {resp.status_code} {resp.text}", None
            data = resp.json()
    except Exception as e:
        return "", f"Judge0 request failed: {e}", None

    stdout = (data.get("stdout") or "")
    stderr = (data.get("stderr") or "")
    compile_output = data.get("compile_output") or data.get("message") or ""
    return stdout, stderr, compile_output


def _piston_endpoints() -> Tuple[str, str]:
    """Return (execute_url, runtimes_url) based on env.
    Supports self-hosted base at PISTON_BASE_URL (e.g., http://localhost:2000)
    and legacy EMKC aggregator.
    """
    base = os.getenv("PISTON_BASE_URL")
    if base:
        base = base.rstrip("/")
        return f"{base}/api/v2/execute", f"{base}/api/v2/runtimes"
    # Legacy envs: direct execute/runtimes URLs or EMKC defaults
    exec_url = os.getenv("PISTON_URL") or "https://emkc.org/api/v2/piston/execute"
    runtimes_url = os.getenv("PISTON_RUNTIMES_URL") or "https://emkc.org/api/v2/piston/runtimes"
    return exec_url, runtimes_url


def _resolve_piston_version(language: str) -> str:
    # Prefer per-language override, then global, then '*' (self-hosted commonly accepts '*')
    return os.getenv(f"PISTON_VERSION_{language.upper()}", os.getenv("PISTON_VERSION", "*"))


def _run_via_piston(language: str, code: str, stdin: str) -> Tuple[str, str, str]:
    execute_url, _ = _piston_endpoints()
    payload = {
        "language": language.lower(),
        "version": _resolve_piston_version(language),
        "files": [{"content": code, "name": f"Main.{language.lower()}"}],
        "stdin": stdin or "",
        "compile_timeout": 10000,
        "run_timeout": 3000,
    }
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(execute_url, json=payload)
            if resp.status_code >= 400:
                return "", f"Piston error: {resp.status_code} {resp.text}", None
            data = resp.json()
    except Exception as e:
        return "", f"Piston request failed: {e}", None

    run = data.get("run") or {}
    compile_phase = data.get("compile") or {}
    stdout = (run.get("stdout") or "")
    stderr = (run.get("stderr") or "")
    compile_output = (compile_phase.get("stdout") or compile_phase.get("stderr") or "")
    return stdout, stderr, compile_output


def list_remote_languages() -> List[str]:
    provider = _get_provider()
    if provider in ("", "false", "0", "no", "local"):
        return []
    if provider == "judge0":
        base_url = os.getenv("JUDGE0_URL", "https://judge0-ce.p.rapidapi.com")
        url = f"{base_url.rstrip('/')}/languages"
        headers = {}
        rapidapi_key = os.getenv("RAPIDAPI_KEY") or os.getenv("JUDGE0_RAPIDAPI_KEY")
        rapidapi_host = os.getenv("RAPIDAPI_HOST")
        if rapidapi_key and "rapidapi" in base_url:
            headers.update({
                "X-RapidAPI-Key": rapidapi_key,
                "X-RapidAPI-Host": rapidapi_host or "judge0-ce.p.rapidapi.com",
            })
        try:
            with httpx.Client(timeout=15) as client:
                resp = client.get(url, headers=headers)
                if resp.status_code == 200:
                    langs = resp.json()
                    # Return lowercased names if present, else language_ids mapped
                    names = [str(item.get("name") or item.get("id", "")).lower() for item in langs]
                    names = [n for n in names if n]
                    return sorted(set(names))
        except Exception:
            pass
        return sorted(set(JUDGE0_LANGUAGE_IDS.keys()))
    if provider == "jdoodle":
        # JDoodle doesn't expose a simple languages endpoint; allow override via env
        env_csv = os.getenv("JDOODLE_LANGUAGES", "")
        if env_csv:
            names = [s.strip().lower() for s in env_csv.split(",") if s.strip()]
            return sorted(set(names))
        # fallback common set
        return sorted({"c", "cpp", "java", "python3", "python2", "php", "ruby", "go", "nodejs", "javascript"})
    if provider == "onecompiler":
        env_csv = os.getenv("ONECOMPILER_LANGUAGES", "")
        if env_csv:
            names = [s.strip().lower() for s in env_csv.split(",") if s.strip()]
            return sorted(set(names))
        # fallback common set
        return sorted({"python", "javascript", "java", "c", "cpp", "go", "rust", "ruby", "typescript", "kotlin", "php"})
    # piston
    _, piston_runtimes_url = _piston_endpoints()
    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(piston_runtimes_url)
            if resp.status_code == 200:
                items = resp.json()
                names = [str(it.get("language", "")).lower() for it in items]
                names = [n for n in names if n]
                return sorted(set(names))
    except Exception:
        pass
    # Fallback minimal set commonly supported by Piston
    return sorted({"python", "javascript", "java", "c", "cpp", "go", "rust", "ruby", "typescript"})


def _run_via_jdoodle(language: str, code: str, stdin: str) -> Tuple[str, str, str]:
    url = os.getenv("JDOODLE_URL", "https://api.jdoodle.com/v1/execute")
    client_id = os.getenv("JDOODLE_CLIENT_ID")
    client_secret = os.getenv("JDOODLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        return "", "JDoodle credentials missing (JDOODLE_CLIENT_ID/JDOODLE_CLIENT_SECRET)", None

    lang = os.getenv(f"JDOODLE_LANGUAGE_{language.upper()}", language)
    version_index = os.getenv(f"JDOODLE_VERSIONINDEX_{language.upper()}", os.getenv("JDOODLE_VERSIONINDEX", "0"))

    payload = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "script": code,
        "language": lang,
        "versionIndex": str(version_index),
        "stdin": stdin or "",
    }
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, json=payload)
            if resp.status_code >= 400:
                return "", f"JDoodle error: {resp.status_code} {resp.text}", None
            data = resp.json()
    except Exception as e:
        return "", f"JDoodle request failed: {e}", None

    stdout = data.get("output") or data.get("stdout") or ""
    stderr = data.get("error") or data.get("stderr") or ""
    compile_output = data.get("statusCode") and f"statusCode={data.get('statusCode')} cpuTime={data.get('cpuTime')} memory={data.get('memory')}" or ""
    return stdout, stderr, compile_output


def _run_via_onecompiler(language: str, code: str, stdin: str) -> Tuple[str, str, str]:
    url = os.getenv("ONECOMPILER_URL", "https://onecompiler-apis.p.rapidapi.com/api/v1/run")
    api_key = os.getenv("ONECOMPILER_RAPIDAPI_KEY") or os.getenv("RAPIDAPI_KEY")
    host = os.getenv("ONECOMPILER_RAPIDAPI_HOST", "onecompiler-apis.p.rapidapi.com")
    if not api_key:
        return "", "OneCompiler RapidAPI key missing (ONECOMPILER_RAPIDAPI_KEY or RAPIDAPI_KEY)", None

    version = os.getenv(f"ONECOMPILER_VERSION_{language.upper()}", os.getenv("ONECOMPILER_VERSION", "*"))
    file_name = os.getenv(f"ONECOMPILER_FILENAME_{language.upper()}", f"Main.{language.lower()}")
    payload = {
        "language": language.lower(),
        "version": version,
        "stdin": stdin or "",
        "files": [{"name": file_name, "content": code}],
    }
    headers = {"X-RapidAPI-Key": api_key, "X-RapidAPI-Host": host}
    try:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, json=payload, headers=headers)
            if resp.status_code >= 400:
                return "", f"OneCompiler error: {resp.status_code} {resp.text}", None
            data = resp.json()
    except Exception as e:
        return "", f"OneCompiler request failed: {e}", None

    # Try to normalize likely shapes
    run = data.get("run") or {}
    stdout = run.get("stdout") or data.get("stdout") or data.get("output") or ""
    stderr = run.get("stderr") or data.get("stderr") or data.get("error") or ""
    compile_phase = data.get("compile") or {}
    compile_output = compile_phase.get("stdout") or compile_phase.get("stderr") or data.get("message") or ""
    return stdout, stderr, compile_output
