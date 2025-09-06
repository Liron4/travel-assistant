"""
Travel Assistant Backend - Pure LangChain Implementation

This backend is built exclusively using LangChain framework with:
- ConversationSummaryBufferMemory for intelligent conversation management
- Google Gemini 2.5 Flash with function calling and grounding
- Chain-of-thought prompting for multi-step reasoning
- Natural conversation flow with tool integration
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

from app.services.travel_agent import TravelAgent
from app.services.session_manager import SessionManager

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Travel Assistant API",
    description="LangChain-powered travel assistant with intelligent conversation management",
    version="2.0.0"
)

# Initialize services
session_manager = SessionManager()
travel_agent = TravelAgent()

class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    conversation_summary: Optional[str] = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main chat endpoint using pure LangChain implementation
    
    Features:
    - ConversationSummaryBufferMemory for context management
    - Tool calling with weather and search capabilities
    - Chain-of-thought reasoning for complex queries
    - Natural conversation flow
    """
    try:
        # Get or create conversation memory for this session
        memory = session_manager.get_memory(request.session_id)
        
        # Process the message through the travel agent
        response = await travel_agent.process_message(
            message=request.message,
            memory=memory,
            session_id=request.session_id
        )
        
        # Get conversation summary if available
        summary = memory.chat_memory.get_summary() if hasattr(memory.chat_memory, 'get_summary') else None
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            conversation_summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "framework": "LangChain", "model": "gemini-2.5-flash"}

@app.get("/sessions/{session_id}/summary")
async def get_session_summary(session_id: str):
    """Get conversation summary for a session"""
    try:
        memory = session_manager.get_memory(session_id)
        summary = memory.chat_memory.get_summary() if hasattr(memory.chat_memory, 'get_summary') else None
        
        return {
            "session_id": session_id,
            "summary": summary,
            "message_count": len(memory.chat_memory.messages)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history for a session"""
    try:
        session_manager.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)