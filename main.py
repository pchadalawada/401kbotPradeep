import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent

load_dotenv()

app = FastAPI(title="IRS-Compliant 401(k) Withdrawal Assistant API")

# Allow CORS for the Angular frontend (which typically runs on port 4200)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent globally
try:
    agent = get_agent()
    AGENT_LOADED = True
except Exception as e:
    print(f"Error loading agent: {e}")
    AGENT_LOADED = False

class ChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage]

class ChatResponse(BaseModel):
    response: str

def convert_to_langchain_messages(history: list[ChatMessage], new_message: str):
    """Convert history to Langchain message objects."""
    langchain_msgs = []
    for msg in history:
        if msg.role == "user":
            langchain_msgs.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_msgs.append(AIMessage(content=msg.content))
            
    # Append the new user message
    langchain_msgs.append(HumanMessage(content=new_message))
    return langchain_msgs

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not AGENT_LOADED:
        raise HTTPException(status_code=500, detail="Agent could not be loaded. Check API keys.")
        
    langchain_messages = convert_to_langchain_messages(request.history, request.message)
    
    # Run the agent
    config = {"configurable": {"thread_id": "fastapi_session"}}
    
    try:
        result = agent.invoke({"messages": langchain_messages}, config=config)
        final_message = result["messages"][-1].content
        return ChatResponse(response=final_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve the API health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "agent_loaded": AGENT_LOADED}

# Mount the static Angular files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist", "frontend", "browser")

if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    
    # Optional: Catch-all for Angular's client-side routing
    @app.exception_handler(404)
    async def fallback_to_index(request, exc):
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "message": "Welcome to the 401(k) Withdrawal Assistant API. The frontend is not built yet.",
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
