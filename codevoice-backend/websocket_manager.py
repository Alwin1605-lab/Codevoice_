import asyncio
import json
import uuid
from typing import Dict, Set, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging
from models.collaboration_models import CollaborationSession, ParticipantRole, CollaborationEvent, EventType

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections: session_id -> {websockets}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Dictionary to store user info: websocket -> user_info
        self.user_connections: Dict[WebSocket, Dict] = {}
        # Dictionary to store session metadata
        self.sessions: Dict[str, Dict] = {}
        # Dictionary mapping user_id -> set of websockets (for targeted messaging)
        self.user_id_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_info: Dict):
        """Accept a new WebSocket connection and add to session.
        user_info is expected to contain a stable 'id' identifying the authenticated user.
        """
        await websocket.accept()

        user_id = user_info.get('id')
        if not user_id:
            # Generate a fallback id if missing (should not happen in production)
            user_id = str(uuid.uuid4())
            user_info['id'] = user_id
            logger.warning("WebSocket connect without user_id; generated temporary id")

        # Initialize session if it doesn't exist
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': asyncio.get_event_loop().time(),
                'participants': []
            }

        # Add connection to session
        self.active_connections[session_id].add(websocket)
        self.user_connections[websocket] = {
            'session_id': session_id,
            'user_info': user_info
        }

        # Track user->websocket mapping
        if user_id not in self.user_id_connections:
            self.user_id_connections[user_id] = set()
        self.user_id_connections[user_id].add(websocket)

        # Add user to session participants if not already present
        existing = any(p.get('id') == user_id for p in self.sessions[session_id]['participants'])
        if not existing:
            self.sessions[session_id]['participants'].append(user_info)

        # Notify other participants about new user
        await self.broadcast_to_session(
            session_id,
            {
                'type': 'user_joined',
                'user': user_info,
                'participants_count': len(self.active_connections[session_id])
            },
            exclude=websocket
        )

        # Send current session info to new user
        await self.send_personal_message(
            {
                'type': 'session_info',
                'session_id': session_id,
                'participants': self.sessions[session_id]['participants'],
                'participants_count': len(self.active_connections[session_id])
            },
            websocket
        )

        logger.info(f"User {user_info.get('name', 'Unknown')} ({user_id}) joined session {session_id}")

        # Persist to DB (best effort)
        try:
            session = await CollaborationSession.get(session_id)
            if session:
                await session.add_participant(user_id, user_info.get('name') or f'user_{user_id}', role=ParticipantRole.EDITOR)
                await session.save()
                await CollaborationEvent.log_event(
                    session_id=session_id,
                    user_id=user_id,
                    event_type=EventType.USER_JOINED,
                    description=f"{user_info.get('name','User')} joined session",
                    data={"user": user_info}
                )
        except Exception as e:
            logger.warning(f"DB sync on connect failed for session {session_id}: {e}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection and clean up"""
        if websocket in self.user_connections:
            user_data = self.user_connections[websocket]
            session_id = user_data['session_id']
            user_info = user_data['user_info']
            user_id = user_info.get('id')
            
            # Remove from session
            if session_id in self.active_connections:
                self.active_connections[session_id].discard(websocket)
                
                # Remove user from participants
                self.sessions[session_id]['participants'] = [
                    p for p in self.sessions[session_id]['participants'] 
                    if p.get('id') != user_info.get('id')
                ]
                
                # If session is empty, clean it up
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                    del self.sessions[session_id]
                else:
                    # Notify remaining participants
                    asyncio.create_task(self.broadcast_to_session(session_id, {
                        'type': 'user_left',
                        'user': user_info,
                        'participants_count': len(self.active_connections[session_id])
                    }))
            
            # Remove user connection
            del self.user_connections[websocket]

            # Remove from user_id mapping
            if user_id and user_id in self.user_id_connections:
                self.user_id_connections[user_id].discard(websocket)
                if not self.user_id_connections[user_id]:
                    del self.user_id_connections[user_id]
            
            logger.info(f"User {user_info.get('name', 'Unknown')} left session {session_id}")

            # Persist disconnect to DB (best effort)
            try:
                if session_id:
                    # CollaborationSession.get is async; schedule task because we're in sync function
                    async def _persist():
                        try:
                            session = await CollaborationSession.get(session_id)
                            if session and user_id:
                                await session.remove_participant(user_id)
                                await CollaborationEvent.log_event(
                                    session_id=session_id,
                                    user_id=user_id,
                                    event_type=EventType.USER_LEFT,
                                    description=f"{user_info.get('name','User')} left session",
                                    data={"user": user_info}
                                )
                        except Exception as e2:
                            logger.warning(f"DB sync on disconnect failed for session {session_id}: {e2}")
                    asyncio.create_task(_persist())
            except Exception as e:
                logger.warning(f"Failed scheduling DB sync on disconnect: {e}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast message to all connections in a session"""
        if session_id not in self.active_connections:
            return
        
        # Create list of connections to avoid modification during iteration
        connections = list(self.active_connections[session_id])
        
        for connection in connections:
            if exclude and connection == exclude:
                continue
            
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting to session {session_id}: {e}")
                # Remove failed connection
                self.active_connections[session_id].discard(connection)
                if connection in self.user_connections:
                    del self.user_connections[connection]
    
    async def handle_message(self, websocket: WebSocket, message: dict):
        """Process incoming message and route appropriately"""
        message_type = message.get('type')
        
        if websocket not in self.user_connections:
            return
        
        session_id = self.user_connections[websocket]['session_id']
        user_info = self.user_connections[websocket]['user_info']
        
        # Add sender info to message
        message['sender'] = user_info
        message['timestamp'] = asyncio.get_event_loop().time()
        
        if message_type == 'code_change':
            # Broadcast code changes to session
            await self.broadcast_to_session(session_id, message, exclude=websocket)
        
        elif message_type == 'cursor_position':
            # Broadcast cursor position to session
            await self.broadcast_to_session(session_id, message, exclude=websocket)
        
        elif message_type == 'chat_message':
            # Broadcast chat message to session
            await self.broadcast_to_session(session_id, message)
        
        elif message_type == 'voice_command':
            # Broadcast voice command to session
            await self.broadcast_to_session(session_id, message, exclude=websocket)
        
        elif message_type == 'file_share':
            # Broadcast file sharing to session
            await self.broadcast_to_session(session_id, message, exclude=websocket)
        
        elif message_type == 'compile_request':
            # Handle compilation request (could be processed and results shared)
            await self.broadcast_to_session(session_id, message, exclude=websocket)
        
        else:
            # Default: broadcast unknown message types
            await self.broadcast_to_session(session_id, message, exclude=websocket)
    
    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a session"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        return None
    
    def list_active_sessions(self) -> List[Dict]:
        """Get list of all active sessions"""
        return [
            {
                'session_id': session_id,
                'participants_count': len(connections),
                'participants': self.sessions[session_id]['participants'],
                'created_at': self.sessions[session_id]['created_at']
            }
            for session_id, connections in self.active_connections.items()
            if connections  # Only include sessions with active connections
        ]
    
    async def send_collaboration_invite(self, from_user: Dict, to_user_id: str, session_id: str, project_name: str):
        """Send collaboration invite to a specific user (targeted). Falls back if user offline.

        Returns the invite payload dictionary. Persistence/email fallback should be handled by caller.
        """
        invite_payload = {
            'type': 'collaboration_invite',
            'invite_id': str(uuid.uuid4()),
            'session_id': session_id,
            'project_name': project_name,
            'from_user': from_user.get('name'),
            'from_user_id': from_user.get('id'),
            'from_user_avatar': from_user.get('avatar', ''),
            'to_user_id': to_user_id,
            'timestamp': asyncio.get_event_loop().time()
        }

        # Attempt targeted delivery
        delivered = False
        if to_user_id in self.user_id_connections:
            dead_sockets: List[WebSocket] = []
            for ws in list(self.user_id_connections[to_user_id]):
                try:
                    await ws.send_text(json.dumps(invite_payload))
                    delivered = True
                except Exception as e:
                    logger.warning(f"Failed to send invite to user {to_user_id}: {e}")
                    dead_sockets.append(ws)
            # Cleanup dead sockets
            for dead in dead_sockets:
                self.user_id_connections[to_user_id].discard(dead)
            if not self.user_id_connections.get(to_user_id):
                self.user_id_connections.pop(to_user_id, None)

        if not delivered:
            logger.info(f"User {to_user_id} offline or no active sockets; invite queued for fallback handling")
            invite_payload['offline'] = True
        else:
            invite_payload['offline'] = False

        return invite_payload

# Global connection manager instance
manager = ConnectionManager()