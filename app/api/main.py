"""
FastAPI Backend - REST API for Travel Booking Agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict
import uuid
import os
from dotenv import load_dotenv

from app.agents.travel_agent import agent_executor
from app.utils.memory import create_memory_for_session
from langchain_core.messages import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Travel Booking Concierge Agent",
    description="Intelligent travel assistant for flight and hotel bookings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
sessions: Dict[str, Dict] = {}


# Request/Response Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message to the agent", min_length=1)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Agent's response")
    session_id: str = Field(..., description="Session ID for this conversation")


class SessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str = Field(..., description="Newly created session ID")
    message: str = Field(..., description="Welcome message")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    version: str


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """
    Health check endpoint to verify service status.
    """
    return HealthResponse(
        status="online",
        service="Travel Booking Concierge Agent",
        version="1.0.0"
    )


@app.post("/api/session", response_model=SessionResponse)
async def create_session():
    """
    Create a new conversation session.
    Returns a unique session ID for maintaining conversation context.
    """
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "memory": create_memory_for_session(session_id),
        "created_at": str(uuid.uuid1().time)
    }
    
    return SessionResponse(
        session_id=session_id,
        message="New session created successfully. How can I assist with your travel plans today?"
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message through the travel agent.
    Maintains conversation context using session IDs.
    
    Args:
        request: ChatRequest containing user message and optional session_id
        
    Returns:
        ChatResponse with agent's reply and session_id
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in sessions:
            sessions[session_id] = {
                "memory": create_memory_for_session(session_id),
                "created_at": str(uuid.uuid1().time)
            }
        
        # Get session memory
        memory = sessions[session_id]["memory"]
        
        # Run agent with conversation history
        result = agent_executor.invoke({
            "input": request.message,
            "chat_history": memory.chat_memory.messages
        })
        
        # Update memory with new messages
        memory.chat_memory.add_message(HumanMessage(content=request.message))
        memory.chat_memory.add_message(AIMessage(content=result["output"]))
        
        return ChatResponse(
            response=result["output"],
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a conversation session and clear its memory.
    
    Args:
        session_id: ID of the session to delete
    """
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/api/sessions")
async def list_sessions():
    """
    List all active sessions (for debugging/monitoring).
    """
    return {
        "active_sessions": len(sessions),
        "sessions": list(sessions.keys())
    }


# Run server
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
