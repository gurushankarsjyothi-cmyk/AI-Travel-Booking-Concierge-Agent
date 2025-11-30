"""
Memory Management - Handles conversation history and context
"""

from langchain.memory import ConversationBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from typing import List


class SimpleMemoryStore(BaseChatMessageHistory):
    """Simple in-memory chat history store for maintaining conversation context."""
    
    def __init__(self):
        self.messages: List[BaseMessage] = []
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the store."""
        self.messages.append(message)
    
    def clear(self) -> None:
        """Clear all messages from the store."""
        self.messages = []
    
    @property
    def messages_list(self) -> List[BaseMessage]:
        """Return the list of messages."""
        return self.messages


def create_memory_for_session(session_id: str) -> ConversationBufferMemory:
    """
    Create memory for a specific conversation session.
    
    Args:
        session_id: Unique identifier for the conversation session
        
    Returns:
        ConversationBufferMemory instance configured for the session
    """
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        chat_memory=SimpleMemoryStore()
    )
    return memory
