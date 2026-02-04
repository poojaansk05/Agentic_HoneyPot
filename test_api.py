import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/v1/honeypot"
API_KEY = "your-super-secret-api-key-change-this"  # Match your .env file

# Test messages
test_cases = [
    {
        "name": "Simple scam attempt",
        "request": {
            "message": "Congratulations! You have won 1 crore rupees. Please share your bank account number to claim the prize.",
            "conversation_history": [],
            "metadata": {}
        }
    },
    {
        "name": "UPI scam",
        "request": {
            "message": "Sir, I am calling from bank. Your account will be blocked. Please send OTP to verify. Also send UPI ID.",
            "conversation_history": [
                {"role": "user", "content": "Hello, this is bank calling"},
                {"role": "assistant", "content": "Oh, hello! What can I help you with?"}
            ],
            "metadata": {}
        }
    },
    {
        "name": "Multi-turn conversation",
        "request": {
            "message": "Good! Now send me your account number and I will transfer the money.",
            "conversation_history": [
                {"role": "user", "content": "You won prize of 50000 rupees"},
                {"role": "assistant", "content": "Really? That's wonderful! How do I claim it?"},
                {"role": "user", "content": "Just give me your details"},
                {"role": "assistant", "content": "What details do you need?"}
            ],
            "metadata": {}
        }
    }
]

def test_honeypot(test_case):
    """Test the honeypot endpoint"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {test_case['name']}")
    print(f"{'='*60}")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=test_case['request'],
            timeout=30
        )
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ SUCCESS")
            print(f"\nScam Detected: {result['scam_detected']}")
            print(f"Confidence: {result['confidence_score']}")
            print(f"Current Persona: {result['engagement_metrics']['current_persona']}")
            print(f"\nAgent Response:")
            print(f"  {result['agent_response']}")
            print(f"\nEngagement Metrics:")
            print(f"  Total Turns: {result['engagement_metrics']['total_turns']}")
            print(f"  Scammer Messages: {result['engagement_metrics']['scammer_messages']}")
            print(f"  Agent Messages: {result['engagement_metrics']['agent_messages']}")
            print(f"\nExtracted Intelligence:")
            print(f"  Bank Accounts: {result['extracted_intelligence']['bank_accounts']}")
            print(f"  UPI IDs: {result['extracted_intelligence']['upi_ids']}")
            print(f"  Phone Numbers: {result['extracted_intelligence']['phone_numbers']}")
            print(f"  Phishing Links: {result['extracted_intelligence']['phishing_links']}")
            
            if result.get('reasoning'):
                print(f"\nReasoning:")
                print(f"  {result['reasoning']}")
        else:
            print(f"\n❌ FAILED")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT - Request took too long")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR - Is the server running?")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

def test_health():
    """Test health endpoint"""
    print(f"\n{'='*60}")
    print("Testing Health Endpoint")
    print(f"{'='*60}")
    
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_auth():
    """Test authentication"""
    print(f"\n{'='*60}")
    print("Testing Authentication")
    print(f"{'='*60}")
    
    # Test with wrong API key
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "wrong-key"
    }
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"message": "test", "conversation_history": []},
            timeout=10
        )
        
        if response.status_code == 401:
            print("✅ Authentication working correctly - rejected invalid key")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("\n🚀 Starting Honeypot API Tests")
    
    # Test health
    test_health()
    
    # Test authentication
    test_auth()
    
    # Run test cases
    for test_case in test_cases:
        test_honeypot(test_case)
    
    print(f"\n{'='*60}")
    print("Tests Complete!")
    print(f"{'='*60}\n")