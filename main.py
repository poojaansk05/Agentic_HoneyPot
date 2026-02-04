from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google import genai
import os
import time
import re
import json
from typing import Optional, List, Dict

from models import (
    HoneypotRequest, 
    HoneypotResponse, 
    ErrorResponse,
    EngagementMetrics,
    ExtractedIntelligence,
    Message
)
from config import config

# Initialize FastAPI
app = FastAPI(
    title="AI-Powered Agentic Honeypot API",
    description="Autonomous scam detection and engagement system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Anthropic client
# Initialize Gemini v1 client
gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)

# ==================== AUTHENTICATION ====================

async def verify_api_key(x_api_key: str = Header(..., description="API Key for authentication")):
    """Verify the API key from request headers"""
    if x_api_key != config.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )
    return x_api_key

# ==================== UTILITY FUNCTIONS ====================

def extract_intelligence(text: str) -> ExtractedIntelligence:
    """Extract intelligence from conversation text using regex patterns"""
    
    # Bank account patterns (8-18 digits)
    bank_accounts = list(set(re.findall(r'\b\d{8,18}\b', text)))
    
    # UPI ID patterns (username@bankname)
    upi_ids = list(set(re.findall(r'\b[\w\.-]+@[\w\.-]+\b', text)))
    # Filter out email-like patterns that don't end with common UPI handles
    upi_handles = ['paytm', 'phonepe', 'googlepay', 'ybl', 'oksbi', 'okhdfcbank', 'okicici', 'okaxis']
    upi_ids = [upi for upi in upi_ids if any(handle in upi.lower() for handle in upi_handles)]
    
    # Phone numbers (10 digits, Indian format)
    phone_numbers = list(set(re.findall(r'\b[6-9]\d{9}\b', text)))
    
    # Phishing links
    phishing_links = list(set(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)))
    
    return ExtractedIntelligence(
        bank_accounts=bank_accounts,
        upi_ids=upi_ids,
        phishing_links=phishing_links,
        phone_numbers=phone_numbers,
        other_intelligence={}
    )

def calculate_engagement_metrics(conversation_history: List[Message], current_persona: str) -> EngagementMetrics:
    """Calculate engagement metrics from conversation history"""
    
    scammer_messages = sum(1 for msg in conversation_history if msg.role == "user")
    agent_messages = sum(1 for msg in conversation_history if msg.role == "assistant")
    total_turns = len(conversation_history)
    
    # Estimate duration (rough estimate: 30 seconds per turn)
    engagement_duration = total_turns * 30.0
    
    return EngagementMetrics(
        total_turns=total_turns,
        scammer_messages=scammer_messages,
        agent_messages=agent_messages,
        engagement_duration_seconds=engagement_duration,
        current_persona=current_persona
    )

def determine_persona(conversation_history: List[Message], scammer_message: str) -> str:
    """
    Dynamically determine persona based on scammer behavior
    Unique Feature: Persona switching
    """
    
    # Default persona
    if len(conversation_history) < 2:
        return "polite_elderly"
    
    # Analyze scammer's tone
    scammer_text = scammer_message.lower()
    
    # Check for impatience indicators
    impatience_keywords = ['hurry', 'quick', 'fast', 'immediately', 'now', 'urgent', 'asap']
    if any(keyword in scammer_text for keyword in impatience_keywords):
        return "busy_professional"
    
    # Check for aggression
    aggression_keywords = ['stupid', 'fool', 'idiot', 'listen', 'must', 'have to']
    if any(keyword in scammer_text for keyword in aggression_keywords):
        return "confused_novice"
    
    # Check for technical language
    tech_keywords = ['account', 'transfer', 'otp', 'verify', 'login', 'password']
    if sum(1 for keyword in tech_keywords if keyword in scammer_text) >= 2:
        return "tech_curious_user"
    
    # Default to elderly if nothing triggered
    return "polite_elderly"

def get_persona_prompt(persona: str) -> str:
    """Get system prompt for specific persona"""
    
    personas = {
        "polite_elderly": """You are playing the role of a polite, elderly person (60-70 years old) who is not very tech-savvy but willing to help. 
Characteristics:
- Speak in a friendly, slightly formal manner
- Ask clarifying questions about technical terms
- Show slight confusion but genuine interest
- Mention you need to ask your grandson/granddaughter for help with complex things
- Be trusting but occasionally hesitant
- Use phrases like "Oh dear", "I'm not sure I understand", "Let me see"
""",
        
        "busy_professional": """You are playing the role of a busy professional who is multitasking.
Characteristics:
- Keep responses shorter and more direct
- Mention you're in a meeting or working
- Ask for quick summaries
- Show mild impatience but willingness to help
- Use phrases like "I'm in the middle of something", "Can we make this quick?", "What exactly do you need?"
""",
        
        "confused_novice": """You are playing the role of someone who is genuinely confused and struggles with technology.
Characteristics:
- Ask very basic questions
- Misunderstand technical terms
- Need step-by-step guidance
- Express frustration with technology
- Ask the scammer to explain things multiple times
- Use phrases like "I don't understand", "What does that mean?", "How do I do that?"
""",
        
        "tech_curious_user": """You are playing the role of someone who is somewhat tech-savvy and curious.
Characteristics:
- Ask probing questions about the process
- Want to understand WHY you need to do something
- Express mild skepticism
- Ask about security and safety
- Use phrases like "Why do you need that?", "Is this safe?", "I've heard about scams"
"""
    }
    
    return personas.get(persona, personas["polite_elderly"])

async def detect_and_engage_scam(request: HoneypotRequest) -> HoneypotResponse:
    """
    Core function: Detect scam and generate agent response
    """
    
    start_time = time.time()
    
    # Determine current persona based on conversation
    current_persona = determine_persona(request.conversation_history, request.message)
    
    # Build conversation for Claude
    conversation_messages = []
    
    # Add conversation history
    for msg in request.conversation_history:
        conversation_messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add current message
    conversation_messages.append({
        "role": "user",
        "content": request.message
    })
    
    # System prompt for the agent
    system_prompt = f"""You are an AI honeypot agent designed to engage with potential scammers.

{get_persona_prompt(current_persona)}

Your objectives:
1. DETECT if this is a scam attempt (look for requests for money, personal info, OTP, bank details, urgency, threats)
2. If it's a scam, ENGAGE naturally without revealing you know it's a scam
3. EXTRACT information: bank account numbers, UPI IDs, phone numbers, phishing links
4. Keep the conversation going to gather more intelligence
5. Act believable and human-like

Response format - you MUST respond with ONLY valid JSON:
{{
    "scam_detected": true/false,
    "confidence_score": 0.0-1.0,
    "agent_response": "your natural response to continue the conversation",
    "reasoning": "short reason (1 sentence)"
}}

Important:
- Stay in character for the persona: {current_persona}
- Never reveal you're an AI or honeypot
- Ask questions that might reveal more scammer details
- Be natural and conversational
- If scam detected, string them along for more information
"""

    try:
        # Call Claude API
        # Build Gemini prompt
        conversation_text = ""
        for msg in request.conversation_history:
            conversation_text += f"{msg.role.upper()}: {msg.content}\n"

        conversation_text += f"USER: {request.message}\n"

        full_prompt = f"""
        {system_prompt}

        Conversation so far:
        {conversation_text}

        Respond ONLY with valid JSON.
        """

        # Call Gemini
                # Call Gemini (v1)
        response = gemini_client.models.generate_content(
            model=config.CONVERSATION_MODEL,  # e.g. "gemini-1.5-flash"
            contents=full_prompt
        )

        response_text = response.text
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                agent_decision = json.loads(json_match.group())
            else:
                agent_decision = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            agent_decision = {
                "scam_detected": True,
                "confidence_score": 0.7,
                "agent_response": "I'm not sure I understand. Could you explain that again?",
                "reasoning": "Failed to parse agent response, using fallback"
            }
        
        # Extract intelligence from entire conversation
        full_conversation = " ".join([msg.content for msg in request.conversation_history] + [request.message])
        extracted_intel = extract_intelligence(full_conversation)
        
        # Calculate engagement metrics
        updated_history = request.conversation_history + [Message(role="user", content=request.message)]
        engagement = calculate_engagement_metrics(updated_history, current_persona)
        
        # Build response
        honeypot_response = HoneypotResponse(
            scam_detected=agent_decision.get("scam_detected", True),
            confidence_score=agent_decision.get("confidence_score", 0.7),
            agent_response=agent_decision.get("agent_response", "Could you tell me more about this?"),
            engagement_metrics=engagement,
            extracted_intelligence=extracted_intel,
            reasoning=agent_decision.get("reasoning", ""),
            status="success"
        )
        
        return honeypot_response
        
    except Exception as e:
        print(f"Error in detect_and_engage_scam: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent processing error: {str(e)}")

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "online",
        "service": "AI-Powered Agentic Honeypot",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "honeypot": "/api/v1/honeypot"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "honeypot-api"
    }

@app.post("/api/v1/honeypot", response_model=HoneypotResponse)
async def honeypot_endpoint(
    request: HoneypotRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Main honeypot endpoint
    Accepts scam messages and returns intelligent responses
    """
    
    try:
        # Process the request
        response = await detect_and_engage_scam(request)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            status="error",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False
    )