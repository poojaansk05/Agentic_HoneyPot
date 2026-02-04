# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An autonomous AI system that engages suspected scammers in multi-turn conversations to extract actionable intelligence such as **bank accounts, UPI IDs, and phishing links** while maintaining a believable human persona.


## Problem Statement

Scam messages increasingly exploit human emotions and urgency.  
This project builds an **AI honeypot agent** that:

- Detects scam intent  
- Engages the scammer without revealing detection  
- Adapts behavior based on scammer sentiment  
- Extracts structured intelligence  
- Stops automatically when enough evidence is collected

---

## Core Capabilities

- Multi-turn autonomous conversation  
- Sentiment-aware strategy selection  
- Human-like persona (non-accusatory, natural tone)  
- Structured intelligence extraction  
- Secure API interface  
- Metrics for evaluation

---

## System Architecture

User → FastAPI Endpoint → Agent Loop  
Agent Loop → Sentiment → Strategy → LLM Reply  
After Each Turn → Intelligence Extractor → Stop Decision

---

## 🔌 API Contract

### Request (from Mock Scammer API)

POST /honeypot  
Headers: X-API-KEY

{
  "conversation_id": "abc123",
  "message": "Pay immediately or account will be blocked"
}

---

### Response – Continue

{
  "status": "CONTINUE",
  "reply": "Which bank should I use to pay?",
  "turn": 1
}

---

### Response – Completed

{
  "status": "COMPLETED",
  "intelligence": {
      "bank_accounts": ["123456789"],
      "ifsc_codes": ["SBIN0001234"],
      "upi_ids": ["raj@ybl"],
      "phishing_links": []
  },
  "turns": 2
}

---

## 🤖 Agent Logic

1. Receive scam message  
2. Analyze sentiment  
3. Map to strategy  
4. Generate human-like reply via LLM  
5. Extract intelligence  
6. Stop when high-value data captured

### Strategies

- aggressive → calm_compliance  
- impatient → delay_verify  
- friendly → friendly_extract

### Stop Conditions

- Bank account detected  
- UPI ID detected  
- Phishing link detected

---

## 🧪 Evaluation Metrics

- Engagement duration  
- Number of turns  
- Completeness of intelligence  
- Stability of responses  
- Detection accuracy

---

## 🛠 Tech Stack

- Python  
- FastAPI  
- Ollama (Llama3 – offline LLM)  
- Prompt Engineering  
- Regex / JSON parsing  
- Modular agent architecture

---

## 🚀 Setup

### 1. Install Dependencies

pip install -r requirements.txt

### 2. Run Ollama

ollama pull llama3

### 3. Start API

uvicorn main:app --reload

---

## 🧩 Team Contributions

- Secure API & infrastructure  
- Autonomous AI agent  
- Intelligence extraction & metrics

---

## 📌 Key Outcomes

- Believable human interaction  
- Autonomous decision making  
- Structured scam intelligence  
- Low latency & offline support

---
