#!/usr/bin/env python3
"""
Test script for the Voice Assistant Server
Tests notification processing and FCM messaging
"""

import requests
import json
import sys
import time

SERVER_URL = "http://localhost:8000"

def test_notification_processing():
    """Test the /notify endpoint"""
    print("🧪 Testing notification processing...")
    
    test_notification = {
        "app": "WhatsApp",
        "sender": "John Doe", 
        "text": "Hey, are you free for lunch today?",
        "subtext": "",
        "package_name": "com.whatsapp",
        "timestamp": int(time.time()),
        "priority": 1
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/notify", json=test_notification)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_spam_detection():
    """Test spam filtering"""
    print("🧪 Testing spam detection...")
    
    spam_notification = {
        "app": "SMS",
        "sender": "Unknown",
        "text": "Congratulations! You won a FREE prize! Click here to claim now!",
        "subtext": "",
        "package_name": "com.android.messaging",
        "timestamp": int(time.time()),
        "priority": 1
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/notify", json=spam_notification)
        result = response.json()
        print(f"Response: {result}")
        
        # Should be filtered as spam
        if result.get("result") == "spam_filtered":
            print("✅ Spam correctly filtered")
            return True
        else:
            print("❌ Spam not detected")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_device_registration():
    """Test device registration"""
    print("🧪 Testing device registration...")
    
    device_data = {
        "device_id": "test_device",
        "fcm_token": "fake_token_for_testing_123456789"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/register_device", json=device_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_endpoint():
    """Test chat endpoint"""
    print("🧪 Testing chat endpoint...")
    
    chat_data = {
        "text": "Hello, how are you?",
        "spoken": False
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/chat", json=chat_data)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        # Check if we got AI response
        if result.get("AI"):
            print("✅ AI response received")
            return True
        else:
            print("❌ No AI response")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_server_health():
    """Test if server is running"""
    print("🧪 Testing server health...")
    
    try:
        response = requests.get(f"{SERVER_URL}/devices")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure the server is running: uvicorn main:app --reload")
        return False

def main():
    print("🚀 Voice Assistant Server Test Suite")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        global SERVER_URL
        SERVER_URL = sys.argv[1]
        
    print(f"Testing server at: {SERVER_URL}")
    print()
    
    tests = [
        ("Server Health", test_server_health),
        ("Notification Processing", test_notification_processing), 
        ("Spam Detection", test_spam_detection),
        ("Device Registration", test_device_registration),
        ("Chat Endpoint", test_chat_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        if test_func():
            print(f"✅ {test_name} PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} FAILED")
        time.sleep(1)
    
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Server is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server configuration.")

if __name__ == "__main__":
    main()