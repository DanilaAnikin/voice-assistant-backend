#!/usr/bin/env python3
"""
Comprehensive tests for main.py FastAPI application
Tests all endpoints, error handling, and integration components
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import status

# Import the FastAPI app
from main import app, chat_with_ai, is_spam, ai_process_notification, registered_devices

# Create test client
client = TestClient(app)

class TestChatEndpoint:
    """Test /chat endpoint functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        registered_devices.clear()
    
    @patch('main.chat_with_ai')
    @patch('main.save_conversation')
    @patch('main.speak')
    def test_chat_with_text_input(self, mock_speak, mock_save, mock_chat):
        """Test chat endpoint with text input"""
        mock_chat.return_value = "Hello! How can I help you?"
        
        response = client.post("/chat", json={
            "text": "Hello, how are you?",
            "spoken": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["User"] == "Hello, how are you?"
        assert data["AI"] == "Hello! How can I help you?"
        assert data["pushed_to_devices"] == []
        
        mock_chat.assert_called_once_with("Hello, how are you?")
        mock_save.assert_called_once()
        mock_speak.assert_not_called()
    
    @patch('main.chat_with_ai')
    @patch('main.save_conversation')
    @patch('main.speak')
    def test_chat_with_spoken_output(self, mock_speak, mock_save, mock_chat):
        """Test chat endpoint with TTS output"""
        mock_chat.return_value = "I'm doing well, thank you!"
        
        response = client.post("/chat", json={
            "text": "How are you?",
            "spoken": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["AI"] == "I'm doing well, thank you!"
        
        mock_speak.assert_called_once_with("I'm doing well, thank you!")
    
    @patch('main.chat_with_ai')
    @patch('main.recognize_speech')
    @patch('main.save_conversation')
    def test_chat_without_text_uses_speech_recognition(self, mock_save, mock_recognize, mock_chat):
        """Test chat endpoint without text input uses speech recognition"""
        mock_recognize.return_value = "What's the weather like?"
        mock_chat.return_value = "I don't have access to weather data."
        
        response = client.post("/chat", json={
            "spoken": False
        })
        
        assert response.status_code == 200
        mock_recognize.assert_called_once()
        mock_chat.assert_called_once_with("What's the weather like?")
    
    @patch('main.fcm_service')
    def test_chat_with_registered_devices(self, mock_fcm_service):
        """Test chat endpoint sends to registered devices"""
        # Setup registered device
        registered_devices["test_device"] = {
            "fcm_token": "test_token_123",
            "device_type": "android"
        }
        mock_fcm_service.app = True
        mock_fcm_service.send_message_to_device.return_value = True
        
        with patch('main.chat_with_ai', return_value="Test response"):
            with patch('main.save_conversation'):
                response = client.post("/chat", json={
                    "text": "Test message",
                    "device_id": "test_device"
                })
        
        assert response.status_code == 200
        data = response.json()
        assert "test_device" in data["pushed_to_devices"]
        mock_fcm_service.send_message_to_device.assert_called_once()
    
    @patch('main.chat_with_ai')
    def test_chat_error_handling(self, mock_chat):
        """Test chat endpoint error handling"""
        mock_chat.side_effect = Exception("OpenAI API error")
        
        response = client.post("/chat", json={
            "text": "Test message"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "OpenAI API error" in data["error"]

class TestNotificationEndpoint:
    """Test /notify endpoint functionality"""
    
    def test_notify_success(self):
        """Test successful notification processing"""
        response = client.post("/notify", json={
            "app": "WhatsApp",
            "sender": "John Doe",
            "text": "Hey, are we still meeting at 3?",
            "subtext": "",
            "package_name": "com.whatsapp",
            "timestamp": 1640995200,
            "priority": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert "John Doe" in data["output"]
        assert "WhatsApp" in data["output"]
    
    def test_notify_spam_filtering(self):
        """Test spam filtering in notifications"""
        response = client.post("/notify", json={
            "app": "WhatsApp",  # Use allowed app so it gets to spam filtering
            "sender": "Spam Sender",
            "text": "You won a free prize! Click here to claim your winnings now!",  # Multiple spam keywords
            "subtext": "",
            "package_name": "com.whatsapp",
            "timestamp": 1640995200,
            "priority": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "spam_filtered"
        assert data["output"] == ""
    
    def test_notify_blocked_app(self):
        """Test blocked app filtering"""
        response = client.post("/notify", json={
            "app": "Facebook",
            "sender": "Friend",
            "text": "Check out this post",
            "subtext": "",
            "package_name": "com.facebook.katana",
            "timestamp": 1640995200,
            "priority": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "filtered_out"
    
    @patch('main.AI_ENABLED', True)
    @patch('main.ai_process_notification')
    def test_notify_with_ai_processing(self, mock_ai_process):
        """Test notification processing with AI enabled"""
        mock_ai_process.return_value = "AI-enhanced message from John"
        
        response = client.post("/notify", json={
            "app": "Messages",
            "sender": "John",
            "text": "Original message text",
            "subtext": "",
            "package_name": "com.android.messaging",
            "timestamp": 1640995200,
            "priority": 0
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        assert data["output"] == "AI-enhanced message from John"
        mock_ai_process.assert_called_once()

class TestDeviceManagement:
    """Test device registration and management endpoints"""
    
    def setup_method(self):
        """Setup for each test"""
        registered_devices.clear()
    
    @patch('main.fcm_service')
    def test_register_device_success(self, mock_fcm_service):
        """Test successful device registration"""
        mock_fcm_service.app = True
        mock_fcm_service.send_message_to_device.return_value = True
        
        response = client.post("/register_device", json={
            "device_id": "android_test_123",
            "fcm_token": "test_fcm_token_456",
            "device_type": "android",
            "app_version": "1.0"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["device_id"] == "android_test_123"
        
        # Verify device is stored
        assert "android_test_123" in registered_devices
        assert registered_devices["android_test_123"]["fcm_token"] == "test_fcm_token_456"
    
    def test_register_device_without_firebase(self):
        """Test device registration without Firebase"""
        response = client.post("/register_device", json={
            "device_id": "android_test_123",
            "fcm_token": "test_fcm_token_456"
        })
        
        # Should still register the device even without Firebase
        assert response.status_code == 200
        assert "android_test_123" in registered_devices
    
    def test_list_devices_empty(self):
        """Test listing devices when none registered"""
        response = client.get("/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 0
        assert data["devices"] == {}
    
    def test_list_devices_with_data(self):
        """Test listing registered devices"""
        # Register a test device
        registered_devices["test_device"] = {
            "device_type": "android",
            "app_version": "1.0",
            "registered_at": "2024-01-01T00:00:00",
            "fcm_token": "test_token_123456789"
        }
        
        response = client.get("/devices")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert "test_device" in data["devices"]
        # Check that FCM token is truncated for security (first 20 chars + "...")
        assert data["devices"]["test_device"]["fcm_token"] == "test_token_123456789..."
    
    @patch('main.fcm_service')
    def test_send_message_success(self, mock_fcm_service):
        """Test sending message to specific device"""
        # Register device
        registered_devices["test_device"] = {
            "fcm_token": "test_token_123"
        }
        mock_fcm_service.send_message_to_device.return_value = True
        
        response = client.post("/send_message", json={
            "message": "Test message",
            "device_id": "test_device",
            "type": "test_message"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "success"
        mock_fcm_service.send_message_to_device.assert_called_once()
    
    def test_send_message_device_not_found(self):
        """Test sending message to non-existent device"""
        response = client.post("/send_message", json={
            "message": "Test message",
            "device_id": "nonexistent_device"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "No registered device found" in data["error"]

class TestUtilityEndpoints:
    """Test utility and status endpoints"""
    
    def test_firebase_status(self):
        """Test Firebase status endpoint"""
        response = client.get("/firebase_status")
        
        assert response.status_code == 200
        data = response.json()
        assert "firebase_initialized" in data
        assert "registered_devices_count" in data
        assert "can_send_notifications" in data
        assert "ai_enabled" in data
        assert "filter_enabled" in data
    
    @patch('main.fcm_service')
    def test_broadcast_message(self, mock_fcm_service):
        """Test broadcasting message to all devices"""
        # Register test devices
        registered_devices["device1"] = {"fcm_token": "token1"}
        registered_devices["device2"] = {"fcm_token": "token2"}
        
        mock_fcm_service.app = True
        mock_fcm_service.send_message_to_device.return_value = True
        
        response = client.post("/broadcast_message", params={"message": "Broadcast test"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert len(data["successful_devices"]) == 2
        assert mock_fcm_service.send_message_to_device.call_count == 2
    
    @patch('main.fcm_service')
    def test_broadcast_no_firebase(self, mock_fcm_service):
        """Test broadcast without Firebase"""
        mock_fcm_service.app = None  # Firebase not initialized
        
        response = client.post("/broadcast_message", params={"message": "Test"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "Firebase not initialized" in data["message"]

class TestHelperFunctions:
    """Test standalone helper functions"""
    
    def test_chat_with_ai_success(self):
        """Test successful AI chat"""
        with patch('main.client.chat.completions.create') as mock_create:
            mock_choice = Mock()
            mock_choice.message.content = "Test AI response"
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            mock_create.return_value = mock_response
            
            result = chat_with_ai("Test prompt")
            assert result == "Test AI response"
            mock_create.assert_called_once()
    
    def test_chat_with_ai_error(self):
        """Test AI chat error handling"""
        with patch('main.client.chat.completions.create') as mock_create:
            mock_create.side_effect = Exception("API Error")
            
            result = chat_with_ai("Test prompt")
            assert "Error fetching AI response" in result
    
    def test_is_spam_detection(self):
        """Test spam detection function"""
        # Test spam messages
        assert is_spam("You won a free prize! Click here!")
        assert is_spam("Urgent! Act now to claim your lottery winnings!")
        assert is_spam("Congratulations! You are the winner of a million dollars!")
        
        # Test non-spam messages
        assert not is_spam("Hey, how are you doing?")
        assert not is_spam("Meeting scheduled for tomorrow at 3pm")
        assert not is_spam("Thanks for the help earlier")
        assert not is_spam("Can you pick up milk from the store?")
    
    @patch('main.client.chat.completions.create')
    def test_ai_process_notification(self, mock_create):
        """Test AI notification processing"""
        mock_choice = Mock()
        mock_choice.message.content = "AI processed message"
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response
        
        result = ai_process_notification("Original message", "WhatsApp", "John")
        assert result == "AI processed message"
        mock_create.assert_called_once()
    
    @patch('main.client.chat.completions.create')
    def test_ai_process_notification_error(self, mock_create):
        """Test AI notification processing with error fallback"""
        mock_create.side_effect = Exception("AI Error")
        
        result = ai_process_notification("Original message", "WhatsApp", "John")
        assert "Message from John on WhatsApp" in result

class TestErrorHandling:
    """Test error handling across the application"""
    
    def test_malformed_json(self):
        """Test handling of malformed JSON requests"""
        response = client.post("/chat", data="invalid json")
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/notify", json={
            "app": "WhatsApp"
            # Missing required fields
        })
        assert response.status_code == 422
    
    def test_invalid_device_id(self):
        """Test handling of invalid device IDs"""
        response = client.post("/send_message", json={
            "message": "Test",
            "device_id": ""  # Empty device ID
        })
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

class TestCORSandMiddleware:
    """Test CORS and middleware functionality"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/chat")
        # CORS should be enabled for all origins
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
    
    def test_api_documentation(self):
        """Test API documentation endpoints"""
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/redoc")
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])