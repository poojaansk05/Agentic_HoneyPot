from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Request Models
class Message(BaseModel):
    role: str = Field(..., description="Role of the message sender (user/assistant)")
    content: str = Field(..., description="Content of the message")

class HoneypotRequest(BaseModel):
    message: str = Field(..., description="Current incoming message from scammer")
    conversation_history: List[Message] = Field(default=[], description="Previous conversation history")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")

# Response Models
class ExtractedIntelligence(BaseModel):
    bank_accounts: List[str] = Field(default=[], description="Extracted bank account numbers")
    upi_ids: List[str] = Field(default=[], description="Extracted UPI IDs")
    phishing_links: List[str] = Field(default=[], description="Extracted phishing URLs")
    phone_numbers: List[str] = Field(default=[], description="Extracted phone numbers")
    other_intelligence: Dict[str, Any] = Field(default={}, description="Other extracted data")

class EngagementMetrics(BaseModel):
    total_turns: int = Field(..., description="Total number of conversation turns")
    scammer_messages: int = Field(..., description="Number of messages from scammer")
    agent_messages: int = Field(..., description="Number of agent responses")
    engagement_duration_seconds: Optional[float] = Field(None, description="Estimated duration")
    current_persona: str = Field(default="polite_elderly", description="Current agent persona")

class HoneypotResponse(BaseModel):
    scam_detected: bool = Field(..., description="Whether scam intent was detected")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in scam detection (0-1)")
    agent_response: str = Field(..., description="Agent's response to continue conversation")
    engagement_metrics: EngagementMetrics = Field(..., description="Conversation engagement metrics")
    extracted_intelligence: ExtractedIntelligence = Field(..., description="Extracted scam intelligence")
    reasoning: Optional[str] = Field(None, description="Agent's reasoning process (optional)")
    status: str = Field(default="success", description="API call status")

class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default={})