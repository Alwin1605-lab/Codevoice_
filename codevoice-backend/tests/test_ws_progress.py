import pytest
import asyncio
from fastapi.testclient import TestClient
from main import app
import types

client = TestClient(app)

class MockTask:
    def __init__(self, task_id, status, result=None, artifact_path=None, error=None):
        self.task_id = task_id
        self.status = status
        self.result = result
        self.artifact_path = artifact_path
        self.error = error

@pytest.mark.parametrize('sequence', [
    ['queued', 'running', 'completed'],
    ['queued', 'failed']
])
def test_ws_streaming(monkeypatch, sequence):
    # Create an iterator that returns different MockTask states on each call
    seq = sequence.copy()
    task_id = 'test-task-123'

    async def fake_find_one(cond):
        # Return None initially to simulate not found, then statuses
        if not seq:
            return MockTask(task_id, seq[-1] if seq else 'completed', result={'response': {'project': {}}})
        status = seq.pop(0)
        if status == 'queued':
            return MockTask(task_id, 'queued')
        if status == 'running':
            return MockTask(task_id, 'running')
        if status == 'completed':
            return MockTask(task_id, 'completed', result={'response': {'project': {'name': 'x'}}})
        if status == 'failed':
            return MockTask(task_id, 'failed', error='error')
        return MockTask(task_id, 'queued')

    # Patch the GenerationTask.find_one used in the ws handler
    import gemini_project_generator as gpg
    monkeypatch.setattr(gpg.GenerationTask, 'find_one', fake_find_one)

    with client.websocket_connect(f"/api/project-generation/ws/tasks/{task_id}") as websocket:
        messages = []
        try:
            while True:
                msg = websocket.receive_json()
                messages.append(msg)
                if msg.get('status') in ('completed', 'failed') or msg.get('error'):
                    break
        except Exception:
            pass

    assert any(m.get('task_id') == task_id for m in messages)
