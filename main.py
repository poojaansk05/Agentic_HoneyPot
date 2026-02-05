from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# 1. MANDATORY: The 'app' attribute Uvicorn is looking for
app = FastAPI()

# 2. Simplified Agent Logic (Integrated to avoid ModuleNotFoundError)
class HoneypotAgent:
    def process_interaction(self, message: str):
        # This is where your LLM logic usually goes
        return f"Honeypot received: {message}. Analyzing for scam patterns..."

agent = HoneypotAgent()

class ChatRequest(BaseModel):
    message: str

# 3. YOUR ENDPOINTS
@app.get("/")
async def root():
    return {"status": "Honeypot Live", "endpoint": "/chat"}

@app.post("/chat")
async def chat(request: ChatRequest):
    response = agent.process_interaction(request.message)
    return {"reply": response}

# 4. Direct execution to bypass Windows Path errors
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
