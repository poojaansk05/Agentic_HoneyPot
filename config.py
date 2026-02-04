import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ================= API Security =================
    API_KEY = os.getenv("HONEYPOT_API_KEY", "your-secret-api-key-here")

    # ================= Google AI Studio (Gemini) =================
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # ================= Server Settings =================
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))

    # ================= Agent Settings =================
    # Fast + free-tier friendly
    CONVERSATION_MODEL = "gemini-2.0-flash"  
    
    # If you later want stronger reasoning:
    # CONVERSATION_MODEL = "gemini-1.5-pro"

    MAX_TOKENS = 1024

    # ================= Security =================
    ALLOWED_ORIGINS = ["*"]  # Lock this down in production

config = Config()