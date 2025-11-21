"""
Models for background generation tasks (Gemini project generation).
"""
from beanie import Document
from pydantic import Field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class TaskStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class GenerationTask(Document):
    task_id: str
    status: TaskStatus = TaskStatus.queued
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    artifact_path: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "generation_tasks"
        indexes = ["task_id", "status", "created_at"]

    async def mark_running(self):
        self.status = TaskStatus.running
        self.updated_at = datetime.utcnow()
        await self.save()

    async def mark_completed(self, result: Dict[str, Any], artifact_path: Optional[str] = None):
        self.status = TaskStatus.completed
        self.result = result
        self.artifact_path = artifact_path
        self.updated_at = datetime.utcnow()
        await self.save()

    async def mark_failed(self, error: str):
        self.status = TaskStatus.failed
        self.error = error
        self.updated_at = datetime.utcnow()
        await self.save()
