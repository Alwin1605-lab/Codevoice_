import pytest
from ai_code_generator import AICodeGenerator


def test_parse_clean_json():
    generator = AICodeGenerator()
    text = '{"files": [{"path": "README.md", "content": "Hello"}]}'
    files = generator._parse_ai_response(text)
    assert isinstance(files, list)
    assert files[0]["path"] == "README.md"


def test_parse_with_fenced_json():
    generator = AICodeGenerator()
    text = 'Here is the output:\n```json\n{"files": [{"path": "index.js", "content": "console.log(1)"}]}\n```'
    files = generator._parse_ai_response(text)
    assert isinstance(files, list)
    assert files[0]["path"] == "index.js"


def test_parse_no_json_returns_fallback():
    generator = AICodeGenerator()
    text = 'This is non-json output from the model without useful structure.'
    files = generator._parse_ai_response(text)
    assert isinstance(files, list)
    # fallback contains package.json entry
    assert any(f["path"] == "package.json" for f in files)
