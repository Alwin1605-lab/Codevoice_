import pytest
import json
from ai_code_generator import AICodeGenerator

class DummyResponse:
    def __init__(self, text):
        self.text = text

class DummyGroqChoice:
    def __init__(self, content):
        self.message = type('M', (), {'content': content})

class DummyGroqResponse:
    def __init__(self, content):
        self.choices = [DummyGroqChoice(content)]

def test_gemini_provider_success(monkeypatch):
    gen = AICodeGenerator()
    # Mock gemini model
    sample = {"files": [{"path": "README.md", "content": "Hello"}]}
    dummy = DummyResponse(json.dumps(sample))
    class MockModel:
        def generate_content(self, prompt):
            return dummy
    gen.gemini_model = MockModel()
    gen.groq_client = None

    result = gen.generate_project_structure({
        'name': 'test',
        'description': 'desc',
        'framework': 'react',
        'features': [],
        'type': 'web'
    })

    assert result['success'] is True
    assert result.get('generated_by') == 'gemini'
    assert isinstance(result['files'], list)

def test_groq_fallback(monkeypatch):
    gen = AICodeGenerator()
    gen.gemini_model = None
    # Mock groq client
    sample = {"files": [{"path": "index.js", "content": "console.log(1)"}]}
    groq_resp = DummyGroqResponse(json.dumps(sample))
    class MockGroqClient:
        class chat:
            class completions:
                @staticmethod
                def create(*args, **kwargs):
                    return groq_resp
    gen.groq_client = MockGroqClient()

    result = gen.generate_project_structure({
        'name': 'test2',
        'description': 'desc',
        'framework': 'react',
        'features': [],
        'type': 'web'
    })

    assert result['success'] is True
    assert result.get('generated_by') == 'groq'
    assert isinstance(result['files'], list)
