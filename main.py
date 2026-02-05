from fastapi import FastAPI
from agent_loop import HoneypotAgent  # Removed 'agent.' prefix

# This is the line Uvicorn is looking for
app = FastAPI()

# Initialize your logic
honeypot = HoneypotAgent()

@app.get("/")
async def status():
    return {"message": "Honeypot API is running"}

@app.post("/interact")
async def interact(user_input: str):
    # This calls the logic in your agent_loop.py
    response = honeypot.process_interaction(user_input)
    return {"response": response}
