"""
Session Manager - Maintains conversation context and authentication state
"""

import uuid
from datetime import datetime


class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self):
        """Create a new session with unique ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "authenticated": False,
            "order_id": None,
            "conversation_history": [],
            "context": {}
        }
        print(f"[Session] Created new session: {session_id}")
        return session_id
    
    def get_session(self, session_id):
        """Retrieve session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id, **kwargs):
        """Update session with new data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)
            return True
        return False
    
    def add_message(self, session_id, role, content):
        """Add message to conversation history"""
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
    
    def authenticate_session(self, session_id, order_id):
        """Mark session as authenticated"""
        if session_id in self.sessions:
            self.sessions[session_id]["authenticated"] = True
            self.sessions[session_id]["order_id"] = order_id
            print(f"[Session] Authenticated session {session_id} for order {order_id}")
            return True
        return False
    
    def is_authenticated(self, session_id):
        """Check if session is authenticated"""
        session = self.get_session(session_id)
        return session["authenticated"] if session else False
    
    def get_conversation_history(self, session_id):
        """Get full conversation history"""
        session = self.get_session(session_id)
        return session["conversation_history"] if session else []
    
    def get_conversation_summary(self, session_id):
        """Generate a simple conversation summary"""
        history = self.get_conversation_history(session_id)
        if not history:
            return "No conversation recorded"
        
        summary_lines = []
        for msg in history:
            role = msg["role"].capitalize()
            summary_lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(summary_lines)
    
    def close_session(self, session_id):
        """Close and archive session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session["closed_at"] = datetime.now().isoformat()
            print(f"[Session] Closed session: {session_id}")
            return session
        return None


# Global session manager instance
session_manager = SessionManager()
