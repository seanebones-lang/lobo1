"""
Conversational Memory and Context Management
Handles conversation history and context for better responses
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class Message:
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create from dictionary"""
        return cls(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data['metadata']
        )

class ConversationManager:
    def __init__(self, max_history: int = 10, ttl_hours: int = 24):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of messages to keep in memory
            ttl_hours: Time to live for conversations in hours
        """
        self.max_history = max_history
        self.ttl = timedelta(hours=ttl_hours)
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.now()
    
    def create_conversation(self, session_id: str) -> str:
        """Create a new conversation session"""
        self.conversations[session_id] = {
            'created_at': datetime.now(),
            'messages': [],
            'context': {},
            'user_preferences': {},
            'conversation_type': 'general'
        }
        logger.info(f"Created new conversation session: {session_id}")
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add message to conversation history"""
        if session_id not in self.conversations:
            self.create_conversation(session_id)
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.conversations[session_id]['messages'].append(message)
        
        # Enforce max history
        if len(self.conversations[session_id]['messages']) > self.max_history:
            self.conversations[session_id]['messages'] = \
                self.conversations[session_id]['messages'][-self.max_history:]
        
        # Auto-cleanup if needed
        self._auto_cleanup()
    
    def get_conversation_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get formatted conversation context for LLM"""
        if session_id not in self.conversations:
            return ""
        
        messages = self.conversations[session_id]['messages'][-max_messages:]
        
        context_parts = []
        for msg in messages:
            if msg.role == 'user':
                context_parts.append(f"User: {msg.content}")
            else:
                context_parts.append(f"Assistant: {msg.content}")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self, session_id: str) -> str:
        """Generate a summary of the conversation"""
        if session_id not in self.conversations:
            return ""
        
        messages = self.conversations[session_id]['messages']
        if not messages:
            return ""
        
        # Extract key topics and themes
        topics = set()
        for msg in messages:
            # Simple keyword extraction (in production, use proper NLP)
            words = msg.content.lower().split()
            topics.update([word for word in words if len(word) > 4])
        
        return f"Conversation topics: {', '.join(list(topics)[:5])}"
    
    def update_context(self, session_id: str, key: str, value: Any) -> None:
        """Update conversation context"""
        if session_id in self.conversations:
            self.conversations[session_id]['context'][key] = value
            logger.debug(f"Updated context for {session_id}: {key} = {value}")
    
    def get_context(self, session_id: str, key: str, default: Any = None) -> Any:
        """Get value from conversation context"""
        if session_id in self.conversations:
            return self.conversations[session_id]['context'].get(key, default)
        return default
    
    def set_user_preference(self, session_id: str, preference: str, value: Any) -> None:
        """Set user preference for the conversation"""
        if session_id not in self.conversations:
            self.create_conversation(session_id)
        
        self.conversations[session_id]['user_preferences'][preference] = value
        logger.info(f"Set user preference for {session_id}: {preference} = {value}")
    
    def get_user_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences for the conversation"""
        if session_id in self.conversations:
            return self.conversations[session_id]['user_preferences']
        return {}
    
    def set_conversation_type(self, session_id: str, conv_type: str) -> None:
        """Set the type of conversation (e.g., 'technical', 'casual', 'formal')"""
        if session_id in self.conversations:
            self.conversations[session_id]['conversation_type'] = conv_type
            logger.info(f"Set conversation type for {session_id}: {conv_type}")
    
    def get_conversation_type(self, session_id: str) -> str:
        """Get the type of conversation"""
        if session_id in self.conversations:
            return self.conversations[session_id]['conversation_type']
        return 'general'
    
    def get_recent_messages(self, session_id: str, n: int = 3) -> List[Message]:
        """Get the most recent n messages"""
        if session_id not in self.conversations:
            return []
        
        return self.conversations[session_id]['messages'][-n:]
    
    def search_conversation_history(self, session_id: str, query: str) -> List[Message]:
        """Search through conversation history for relevant messages"""
        if session_id not in self.conversations:
            return []
        
        relevant_messages = []
        query_lower = query.lower()
        
        for msg in self.conversations[session_id]['messages']:
            if query_lower in msg.content.lower():
                relevant_messages.append(msg)
        
        return relevant_messages
    
    def cleanup_old_conversations(self) -> int:
        """Remove expired conversations"""
        now = datetime.now()
        expired_sessions = []
        
        for session_id, conversation in self.conversations.items():
            if now - conversation['created_at'] > self.ttl:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversations[session_id]
            logger.info(f"Cleaned up expired conversation: {session_id}")
        
        return len(expired_sessions)
    
    def _auto_cleanup(self) -> None:
        """Auto-cleanup if cleanup interval has passed"""
        if datetime.now() - self.last_cleanup > self.cleanup_interval:
            self.cleanup_old_conversations()
            self.last_cleanup = datetime.now()
    
    def get_conversation_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about the conversation"""
        if session_id not in self.conversations:
            return {}
        
        conversation = self.conversations[session_id]
        messages = conversation['messages']
        
        if not messages:
            return {}
        
        user_messages = [msg for msg in messages if msg.role == 'user']
        assistant_messages = [msg for msg in messages if msg.role == 'assistant']
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'conversation_duration': (datetime.now() - conversation['created_at']).total_seconds(),
            'avg_message_length': sum(len(msg.content) for msg in messages) / len(messages),
            'conversation_type': conversation['conversation_type']
        }
    
    def export_conversation(self, session_id: str) -> Dict[str, Any]:
        """Export conversation data"""
        if session_id not in self.conversations:
            return {}
        
        conversation = self.conversations[session_id]
        return {
            'session_id': session_id,
            'created_at': conversation['created_at'].isoformat(),
            'messages': [msg.to_dict() for msg in conversation['messages']],
            'context': conversation['context'],
            'user_preferences': conversation['user_preferences'],
            'conversation_type': conversation['conversation_type']
        }
    
    def import_conversation(self, data: Dict[str, Any]) -> str:
        """Import conversation data"""
        session_id = data['session_id']
        
        self.conversations[session_id] = {
            'created_at': datetime.fromisoformat(data['created_at']),
            'messages': [Message.from_dict(msg_data) for msg_data in data['messages']],
            'context': data['context'],
            'user_preferences': data['user_preferences'],
            'conversation_type': data['conversation_type']
        }
        
        logger.info(f"Imported conversation: {session_id}")
        return session_id
    
    def clear_conversation(self, session_id: str) -> None:
        """Clear a specific conversation"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation: {session_id}")
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs"""
        return list(self.conversations.keys())
