from fastapi import APIRouter, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Dict, List, Set
import json
import uuid
from datetime import datetime

router = APIRouter()

# Store active collaboration sessions
active_sessions: Dict[str, Dict] = {}
connected_clients: Dict[str, Set[WebSocket]] = {}

class CollaborationManager:
    def __init__(self):
        self.sessions = {}
        self.clients = {}
    
    async def create_session(self, creator_id: str, session_name: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "id": session_id,
            "name": session_name,
            "creator": creator_id,
            "participants": [creator_id],
            "code": "",
            "language": "python",
            "created_at": datetime.now().isoformat(),
            "cursor_positions": {},
            "voice_queue": []
        }
        self.clients[session_id] = set()
        return session_id
    
    async def join_session(self, session_id: str, user_id: str) -> bool:
        if session_id in self.sessions:
            if user_id not in self.sessions[session_id]["participants"]:
                self.sessions[session_id]["participants"].append(user_id)
            return True
        return False
    
    async def leave_session(self, session_id: str, user_id: str):
        if session_id in self.sessions:
            if user_id in self.sessions[session_id]["participants"]:
                self.sessions[session_id]["participants"].remove(user_id)
            if not self.sessions[session_id]["participants"]:
                # Delete empty session
                del self.sessions[session_id]
                if session_id in self.clients:
                    del self.clients[session_id]
    
    async def update_code(self, session_id: str, code: str, user_id: str):
        if session_id in self.sessions:
            self.sessions[session_id]["code"] = code
            await self.broadcast_to_session(session_id, {
                "type": "code_update",
                "code": code,
                "user": user_id,
                "timestamp": datetime.now().isoformat()
            })
    
    async def update_cursor(self, session_id: str, user_id: str, line: int, column: int):
        if session_id in self.sessions:
            self.sessions[session_id]["cursor_positions"][user_id] = {
                "line": line,
                "column": column,
                "timestamp": datetime.now().isoformat()
            }
            await self.broadcast_to_session(session_id, {
                "type": "cursor_update",
                "user": user_id,
                "line": line,
                "column": column
            })
    
    async def add_voice_message(self, session_id: str, user_id: str, transcript: str, audio_url: str = None):
        if session_id in self.sessions:
            voice_message = {
                "user": user_id,
                "transcript": transcript,
                "audio_url": audio_url,
                "timestamp": datetime.now().isoformat()
            }
            self.sessions[session_id]["voice_queue"].append(voice_message)
            await self.broadcast_to_session(session_id, {
                "type": "voice_message",
                **voice_message
            })
    
    async def add_client(self, session_id: str, websocket: WebSocket):
        if session_id not in self.clients:
            self.clients[session_id] = set()
        self.clients[session_id].add(websocket)
    
    async def remove_client(self, session_id: str, websocket: WebSocket):
        if session_id in self.clients:
            self.clients[session_id].discard(websocket)
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        if session_id in self.clients:
            disconnected = []
            for client in self.clients[session_id]:
                try:
                    await client.send_text(json.dumps(message))
                except:
                    disconnected.append(client)
            
            # Remove disconnected clients
            for client in disconnected:
                self.clients[session_id].discard(client)

collaboration_manager = CollaborationManager()

@router.post("/create-session/")
async def create_collaboration_session(
    creator_id: str = Form(...),
    session_name: str = Form(...)
):
    """
    Create a new real-time collaboration session
    """
    try:
        session_id = await collaboration_manager.create_session(creator_id, session_name)
        return {
            "session_id": session_id,
            "session_name": session_name,
            "creator": creator_id,
            "join_url": f"/collaborate/{session_id}"
        }
    except Exception as e:
        return {"error": f"Failed to create session: {str(e)}"}

@router.post("/join-session/")
async def join_collaboration_session(
    session_id: str = Form(...),
    user_id: str = Form(...)
):
    """
    Join an existing collaboration session
    """
    try:
        success = await collaboration_manager.join_session(session_id, user_id)
        if success:
            session = collaboration_manager.sessions.get(session_id)
            return {
                "success": True,
                "session": session
            }
        else:
            return {"error": "Session not found"}
    except Exception as e:
        return {"error": f"Failed to join session: {str(e)}"}

@router.get("/sessions/")
async def list_active_sessions():
    """
    List all active collaboration sessions
    """
    sessions = []
    for session_id, session_data in collaboration_manager.sessions.items():
        sessions.append({
            "id": session_id,
            "name": session_data["name"],
            "creator": session_data["creator"],
            "participants_count": len(session_data["participants"]),
            "language": session_data["language"],
            "created_at": session_data["created_at"]
        })
    return {"sessions": sessions}

@router.websocket("/collaborate/{session_id}")
async def websocket_collaboration(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time collaboration
    """
    await websocket.accept()
    await collaboration_manager.add_client(session_id, websocket)
    
    try:
        # Send current session state to new client
        if session_id in collaboration_manager.sessions:
            session = collaboration_manager.sessions[session_id]
            await websocket.send_text(json.dumps({
                "type": "session_state",
                "code": session["code"],
                "language": session["language"],
                "participants": session["participants"],
                "cursor_positions": session["cursor_positions"]
            }))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            user_id = message.get("user_id")
            
            if message_type == "code_update":
                await collaboration_manager.update_code(
                    session_id, 
                    message.get("code", ""), 
                    user_id
                )
            
            elif message_type == "cursor_update":
                await collaboration_manager.update_cursor(
                    session_id,
                    user_id,
                    message.get("line", 0),
                    message.get("column", 0)
                )
            
            elif message_type == "voice_message":
                await collaboration_manager.add_voice_message(
                    session_id,
                    user_id,
                    message.get("transcript", ""),
                    message.get("audio_url")
                )
            
            elif message_type == "language_change":
                if session_id in collaboration_manager.sessions:
                    collaboration_manager.sessions[session_id]["language"] = message.get("language", "python")
                    await collaboration_manager.broadcast_to_session(session_id, {
                        "type": "language_changed",
                        "language": message.get("language"),
                        "user": user_id
                    })
    
    except WebSocketDisconnect:
        await collaboration_manager.remove_client(session_id, websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await collaboration_manager.remove_client(session_id, websocket)