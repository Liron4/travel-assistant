from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse
from app.services.llm_service import get_agent_response
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Travel Assistant API", version="1.0.0")

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Travel Assistant API is running with HOT RELOAD! 🔥", "status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return the agent's response
    """
    try:
        # Validate API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            raise HTTPException(
                status_code=500, 
                detail="OpenRouter API key is not configured. Please set OPENROUTER_API_KEY in your environment."
            )
        
        # Get response from the LangChain agent
        response_content = get_agent_response(request.user_input)
        return ChatResponse(content=response_content)
        
    except Exception as e:
        # Return a user-friendly error message
        error_msg = f"I apologize, but I'm experiencing some technical difficulties: {str(e)}"
        return ChatResponse(content=error_msg)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
