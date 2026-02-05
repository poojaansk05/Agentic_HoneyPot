from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Import your agent logic (Ensure these files exist in the same folder)
from agent_loop import HoneypotAgent 

# 1. This is the 'app' variable Uvicorn is looking for
app = FastAPI(title="Agentic Honeypot API")

# 2. Initialize your honeypot agent
agent = HoneypotAgent()

# 3. Define a data structure for incoming messages
class Message(BaseModel):
    content: str
    sender: str = "unknown"

---

### Endpoints

@app.get("/")
async def health_check():
    """Check if the honeypot is online."""
    return {
        "status": "online",
        "system": "Agentic Honeypot",
        "docs_url": "/docs"
    }

@app.post("/chat")
async def chat_with_scammer(message: Message):
    """
    The main endpoint for your honeypot. 
    Send a scammer's message here to get an AI-generated response.
    """
    try:
        # Calls the logic from your agent_loop.py
        response = agent.process_interaction(message.content)
        return {
            "scammer_message": message.content,
            "honeypot_reply": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# This block allows you to run it via 'python main.py' as well
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
