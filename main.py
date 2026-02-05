from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. THE FIX: Define 'app' at the top level so Uvicorn can find it
app = FastAPI(title="Agentic Honeypot")

# 2. THE IMPORT FIX: Using a try/except block 
# This prevents the server from crashing if your other files have errors
try:
    from agent_loop import HoneypotAgent
    agent = HoneypotAgent()
    print("✅ Successfully loaded HoneypotAgent from agent_loop.py")
except ImportError:
    print("⚠️ Warning: agent_loop.py not found or has errors. Using MockAgent.")
    class MockAgent:
        def process_interaction(self, msg): return f"Mock response to: {msg}"
    agent = MockAgent()

# --- Data Models ---
class ChatInput(BaseModel):
    message: str

# --- Endpoints ---

@app.get("/")
async def root():
    """This generates your base URL response"""
    return {"message": "Honeypot API is live!", "docs": "/docs"}

@app.post("/chat")
async def chat(input_data: ChatInput):
    """This generates your interaction endpoint URL"""
    try:
        reply = agent.process_interaction(input_data.message)
        return {"honeypot_reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This part is optional but helpful for running via 'python main.py'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
