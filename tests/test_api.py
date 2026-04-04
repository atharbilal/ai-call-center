"""Tests for API endpoints."""
import pytest
import httpx
import json

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "active_calls" in data
    print("✅ test_health_endpoint passed")
    print(f"   Server status: {data['status']}, Active calls: {data['active_calls']}")

def test_test_agent_new_call():
    """Test starting a new test call."""
    response = httpx.post(
        f"{BASE_URL}/test-agent",
        json={"message": "", "call_sid": "API_TEST001"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["call_sid"] == "API_TEST001"
    assert "ai_response" in data
    assert data["stage"] == "language_detection"
    print("✅ test_test_agent_new_call passed")
    print(f"   AI Response: {data['ai_response'][:50]}...")

def test_test_agent_existing_call():
    """Test continuing an existing test call."""
    # First, start a call
    httpx.post(
        f"{BASE_URL}/test-agent",
        json={"message": "", "call_sid": "API_TEST002"}
    )
    
    # Then send a message
    response = httpx.post(
        f"{BASE_URL}/test-agent",
        json={"message": "9876543210", "call_sid": "API_TEST002"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["call_sid"] == "API_TEST002"
    assert data["customer_input"] == "9876543210"
    print("✅ test_test_agent_existing_call passed")
    print(f"   Stage: {data['stage']}, Identified: {data['customer_identified']}")

def test_calls_endpoint():
    """Test listing active calls."""
    # Start a test call first
    httpx.post(
        f"{BASE_URL}/test-agent",
        json={"message": "", "call_sid": "API_TEST003"}
    )
    
    # Get active calls
    response = httpx.get(f"{BASE_URL}/calls")
    assert response.status_code == 200
    data = response.json()
    assert "active_calls" in data
    assert len(data["active_calls"]) >= 1
    print("✅ test_calls_endpoint passed")
    print(f"   Active calls: {data['count']}")

if __name__ == "__main__":
    print("Running API tests...\n")
    test_health_endpoint()
    test_test_agent_new_call()
    test_test_agent_existing_call()
    test_calls_endpoint()
    print("\n All API tests passed!")
