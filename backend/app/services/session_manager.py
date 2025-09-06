"""
Session Manager for Travel Assistant

Manages conversation sessions using LangChain's ConversationSummaryBufferMemory
with intelligent conversation context management and memory optimization.
"""

from typing import Dict
from langchain.memory import ConversationSummaryBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
import os

class SessionManager:
    """
    Manages conversation sessions with intelligent memory management
    
    Features:
    - ConversationSummaryBufferMemory for each session
    - Automatic conversation summarization
    - Memory buffer optimization
    - Session isolation
    """
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSummaryBufferMemory] = {}
        
        # Initialize the LLM for memory summarization
        # Using a separate instance optimized for summarization
        self.summarizer_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1,  # Low temperature for consistent summaries
            max_tokens=1000,  # Shorter responses for summaries
        )
    
    def get_memory(self, session_id: str) -> ConversationSummaryBufferMemory:
        """
        Get or create ConversationSummaryBufferMemory for a session
        
        Args:
            session_id: Unique identifier for the conversation session
            
        Returns:
            ConversationSummaryBufferMemory instance for the session
        """
        if session_id not in self.sessions:
            # Create new memory with intelligent configuration
            memory = ConversationSummaryBufferMemory(
                llm=self.summarizer_llm,
                max_token_limit=2000,  # Buffer size before summarization
                return_messages=True,   # Return full message objects
                memory_key="chat_history",
                input_key="input",
                output_key="output"
            )
            
            self.sessions[session_id] = memory
            
        return self.sessions[session_id]
    
    def clear_session(self, session_id: str) -> bool:
        """
        Clear a conversation session
        
        Args:
            session_id: Session to clear
            
        Returns:
            True if session was cleared, False if session didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_all_sessions(self) -> list:
        """
        Get list of all active session IDs
        
        Returns:
            List of active session IDs
        """
        return list(self.sessions.keys())
    
    def get_session_stats(self, session_id: str) -> dict:
        """
        Get statistics for a session
        
        Args:
            session_id: Session to analyze
            
        Returns:
            Dictionary with session statistics
        """
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        memory = self.sessions[session_id]
        messages = memory.chat_memory.messages
        
        return {
            "session_id": session_id,
            "total_messages": len(messages),
            "has_summary": hasattr(memory.chat_memory, 'summary') and memory.chat_memory.summary is not None,
            "buffer_size": memory.max_token_limit,
            "memory_key": memory.memory_key
        }
