# Async Project Generation + WebSocket Progress

This document explains the asynchronous project generation flow added to the backend and how the frontend can subscribe to progress updates.

Overview
- Endpoint to enqueue generation: `POST /api/project-generation/generate/async` (accepts JSON `ProjectGenerationRequest`). Returns `{"task_id": "<id>", "status": "queued"}`.
- WebSocket for progress: `ws://<host>/api/project-generation/ws/tasks/{task_id}` streams JSON status updates for the task.
- Optional Redis pub/sub: If `REDIS_URL` (or `REDIS_URI`) is set in the environment, the backend will publish task updates to channel `project_tasks:{task_id}`. The WebSocket will subscribe to Redis for real-time updates; if Redis is not configured, the WS will fallback to DB polling.

How it works (high level)
1. Client posts a project generation request to `/api/project-generation/generate/async`.
2. Backend schedules the task and returns a `task_id`.
3. A background worker picks up the task and invokes the model (Gemini or Groq).
4. As the worker completes/fails the task, it writes `GenerationTask` status to the DB and publishes the update to Redis (if configured).
5. Clients connect to the WS endpoint `/api/project-generation/ws/tasks/{task_id}` to receive updates. The WS will prefer to subscribe to Redis; otherwise it polls the DB for changes.

Environment
- Optional: `REDIS_URL` or `REDIS_URI` — if present, the backend will use Redis for pub/sub. Example: `redis://localhost:6379/0`.

Frontend usage
- Enqueue a generation job using `POST /api/project-generation/generate/async` with the `ProjectGenerationRequest` JSON payload.
- Open a WebSocket to `ws://localhost:8000/api/project-generation/ws/tasks/{task_id}` and listen for JSON messages like:

```json
{
  "task_id": "...",
  "status": "queued|running|completed|failed",
  "result": { /* optional result payload */ },
  "error": null
}
```

- On `status: completed` the client can request the generated artifact or save the embedded `result` into the project DB.

Notes and next steps
- For production-grade real-time updates, use a dedicated message broker (Redis Streams, RabbitMQ, Kafka) or use DB change streams.
- Consider adding finer-grained progress messages (per-file generation) and backpressure handling for large payloads.
- The current implementation prioritizes robustness: it works with or without Redis and won't block if Redis is misconfigured.
