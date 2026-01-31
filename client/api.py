
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
from langchain_core.messages import HumanMessage, AIMessage

import sys
import os

# Add the project root to sys.path so we can import 'client.loader'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client.loader import get_agent_app

agent_app = None
mcp_client_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_app, mcp_client_instance
    print("Initializing Agent...")
    agent_app, mcp_client_instance = await get_agent_app()
    yield
    print("Shutting down...")
    # cleanup if needed

app = FastAPI(lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    if not agent_app:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Invoke agent
    result = await agent_app.ainvoke(
        {"messages": [HumanMessage(content=request.message)]},
        config=config,
    )
    
    # Extract last message
    messages = result.get("messages", [])
    last_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
    
    response_text = last_ai.content if last_ai else "No response generated."
    
    return {"response": response_text}

if __name__ == "__main__":
    uvicorn.run("client.api:app", host="0.0.0.0", port=8002, reload=True)
