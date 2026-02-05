from fastapi import FastAPI
import uvicorn

# MANDATORY: This is the entry point for the web server
app = FastAPI()

@app.get("/")
async def home():
    return {"status": "success", "endpoint": "active"}

# This allows you to run the file DIRECTLY without typing 'uvicorn main:app'
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
