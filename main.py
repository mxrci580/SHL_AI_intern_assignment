import os
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

from retriever.retriever import SHLRetriever
from agent.extractor import extract_conversation_state
from agent.fsm import determine_next_state
from agent.generator import generate_response
from agent.schemas import AgentResponse
from agent.demo_fallback import get_demo_response

app = FastAPI(
    title="SHL Product Recommendation Agent API",
    description="Deterministic runtime RAG pipeline for SHL assessment recommendations.",
    version="1.0.0"
)

# GET /health for readiness check
@app.get("/health")
async def health_endpoint():
    return {"status": "ok"}

# Request schema matching official non-negotiable specifications
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

# Global pipeline objects initialized on startup
project_root = Path(__file__).parent
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("WARNING: GEMINI_API_KEY is not set in environment.")

client = None
retriever = None

@app.on_event("startup")
def startup_event():
    global client, retriever, api_key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = "MOCK_KEY"
    client = genai.Client(api_key=api_key)
    retriever = SHLRetriever(project_root, client)

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: ChatRequest):
    """The unified runtime chat endpoint coordinating Extractor -> FSM -> Retriever -> Generator."""
    if not request.messages:
        raise HTTPException(status_code=400, detail="messages list cannot be empty")
        
    # Get the latest user message
    user_messages = [m for m in request.messages if m.role == "user"]
    if not user_messages:
        raise HTTPException(status_code=400, detail="Request must contain at least one user message")
    user_message = user_messages[-1].content.strip()
    
    if not user_message:
        raise HTTPException(status_code=400, detail="User message cannot be empty")
        
    # Extract preceding conversation history contents
    history = [m.content for m in request.messages[:-1]]
    
    # Check if explicit demo mode is set
    if os.getenv("DEMO_MODE") == "true":
        print(f"DEMO MODE ACTIVATED: Serving simulated fallback for query '{user_message}'")
        return get_demo_response(user_message, history)
        
    try:
        # 1. Extractor Layer (Gemini) - Linguistic understanding only
        state = extract_conversation_state(
            user_message=user_message,
            conversation_history=history,
            client=client
        )
        
        # 2. Decision Layer (FSM) - Deterministic workflow state routing
        next_state = determine_next_state(state)
        
        # 3. Retriever Layer (FAISS + Metadata Filtering)
        retrieved_products = []
        if next_state in ("RETRIEVE", "REFINE", "COMPARE", "JUSTIFY", "FINALIZE"):
            # Sift candidates based on extracted state details
            retrieved_products = retriever.retrieve(state, top_n=5)
            
        # 4. Generator Layer (Gemini) - Linguistic natural language responses
        agent_res = generate_response(
            fsm_state=next_state,
            state=state,
            retrieved_products=retrieved_products,
            client=client
        )
        
        return agent_res
        
    except Exception as e:
        err_str = str(e)
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "quota" in err_str.lower():
            print(f"QUOTA EXHAUSTED WARNING: Live Gemini API call hit 429 rate limits. Falling back to Demo Mode for query '{user_message}'")
            return get_demo_response(user_message, history)
            
        print(f"Exception encountered in pipeline controller: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {err_str}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
