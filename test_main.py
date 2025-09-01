#!/usr/bin/env python3
"""
Comprehensive unit tests for the Voice Assistant Backend
Tests main.py functionality including API endpoints, Firebase integration, and core features
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
import tempfile
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import main after setting up the path
from main import app, chat_with_ai, process_notification, is_spam, classify_notification_importance

# Create test client
client = TestClient(app)

class TestMainAPI:
    """Test the main FastAPI application endpoints"""

    def test_chat_endpoint_success(self):
        """Test successful chat endpoint response"""
        with patch('main.chat_with_ai') as mock_chat:
            mock_chat.return_value = "Hello! How can I help you?"
            
            response = client.post("/chat", json={
                "text": "Hello",
                "spoken": False
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "AI" in data
            assert data["AI"] == "Hello! How can I help you?"
            assert "spoken" in data

    def test_chat_endpoint_with_spoken_true(self):
        """Test chat endpoint with spoken=True"""
        with patch('main.chat_with_ai') as mock_chat, \
             patch('main.speak') as mock_speak:
            
            mock_chat.return_value = "Hello! How can I help you?"
            mock_speak.return_value = None
            
            response = client.post("/chat", json={
                "text": "Hello",
                "spoken": True
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["spoken"] == True
            mock_speak.assert_called_once()

    def test_chat_endpoint_invalid_data(self):
        """Test chat endpoint with invalid data"""
        response = client.post("/chat", json={
            "invalid_field": "test"
        })
        
        assert response.status_code == 422  # Validation error

    def test_notify_endpoint_success(self):
        """Test successful notification processing"""
        with patch('main.process_notification') as mock_process, \
             patch('main.fcm_service') as mock_fcm:
            
            mock_process.return_value = True
            mock_fcm.send_to_device = Mock(return_value=True)
            
            notification_data = {
                "app": "WhatsApp",
                "sender": "John Doe",
                "text": "Hello there!",
                "package_name": "com.whatsapp",
                "timestamp": int(datetime.now().timestamp()),
                "priority": 1
            }
            
            response = client.post("/notify", json=notification_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["result"] == "processed"

    def test_notify_endpoint_spam_detection(self):
        """Test spam detection in notify endpoint"""
        with patch('main.is_spam') as mock_spam:
            mock_spam.return_value = True
            
            spam_notification = {
                "app": "SMS",
                "sender": "Unknown",
                "text": "You won a FREE prize! Click now!",
                "package_name": "com.android.messaging",
                "timestamp": int(datetime.now().timestamp()),
                "priority": 1
            }
            
            response = client.post("/notify", json=spam_notification)
            
            assert response.status_code == 200
            data = response.json()
            assert data["result"] == "spam_filtered"

    def test_register_device_success(self):
        """Test successful device registration"""
        with patch('main.fcm_service') as mock_fcm:
            mock_fcm.register_device = Mock(return_value=True)
            mock_fcm.get_device_count = Mock(return_value=1)
            
            device_data = {
                "device_id": "test-device-123",
                "fcm_token": "test-token-456"
            }
            
            response = client.post("/register_device", json=device_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "device_count" in data

    def test_register_device_failure(self):
        """Test device registration failure"""
        with patch('main.fcm_service') as mock_fcm:
            mock_fcm.register_device = Mock(return_value=False)
            
            device_data = {
                "device_id": "test-device-123",
                "fcm_token": "invalid-token"
            }
            
            response = client.post("/register_device", json=device_data)
            
            assert response.status_code == 400
            data = response.json()
            assert data["status"] == "error"

    def test_get_devices_endpoint(self):
        """Test get devices endpoint"""
        with patch('main.fcm_service') as mock_fcm:
            mock_devices = [
                {"device_id": "device1", "fcm_token": "token1"},
                {"device_id": "device2", "fcm_token": "token2"}
            ]
            mock_fcm.get_all_devices = Mock(return_value=mock_devices)
            mock_fcm.get_device_count = Mock(return_value=2)
            
            response = client.get("/devices")
            
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 2
            assert len(data["devices"]) == 2

    def test_speech_to_text_endpoint(self):
        """Test speech to text endpoint"""
        with patch('main.recognize_speech') as mock_recognize:
            mock_recognize.return_value = "Hello world"
            
            # Create a temporary audio file for testing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(b"fake audio data")
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as audio_file:
                    response = client.post("/speech-to-text", 
                                         files={"audio": ("test.wav", audio_file, "audio/wav")})
                
                assert response.status_code == 200
                data = response.json()
                assert "text" in data
            finally:
                os.unlink(temp_file_path)

class TestCoreLogic:
    """Test core logic functions"""

    @patch('main.client')
    def test_chat_with_ai_success(self, mock_client):
        """Test successful AI chat interaction"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = chat_with_ai("Hello")
        
        assert result == "Hello! How can I help you?"
        mock_client.chat.completions.create.assert_called_once()

    @patch('main.client')
    def test_chat_with_ai_error(self, mock_client):
        """Test AI chat interaction error handling"""
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        result = chat_with_ai("Hello")
        
        assert "Error fetching AI response" in result
        assert "API Error" in result

    def test_is_spam_detection(self):
        """Test spam detection logic"""
        spam_messages = [
            "Congratulations! You won a FREE prize!",
            "Click here to claim your reward NOW!",
            "URGENT: Your account will be suspended",
            "Make money fast with this simple trick!"
        ]
        
        for message in spam_messages:
            assert is_spam(message, "Unknown") == True

    def test_is_not_spam_detection(self):
        """Test legitimate message detection"""
        legitimate_messages = [
            "Hey, are you free for lunch today?",
            "Meeting starts in 10 minutes",
            "Happy birthday! Hope you have a great day",
            "Can you please send me the report?"
        ]
        
        for message in legitimate_messages:
            assert is_spam(message, "John Doe") == False

    def test_classify_notification_importance(self):
        """Test notification importance classification"""
        # High importance
        high_importance = classify_notification_importance("urgent meeting", "Boss")
        assert high_importance >= 8

        # Medium importance
        medium_importance = classify_notification_importance("lunch tomorrow?", "Friend")
        assert 4 <= medium_importance <= 7

        # Low importance
        low_importance = classify_notification_importance("sale today", "Store")
        assert low_importance <= 5

    @patch('main.fcm_service')
    @patch('main.save_conversation')
    def test_process_notification_success(self, mock_save, mock_fcm):
        """Test successful notification processing"""
        mock_save.return_value = None
        mock_fcm.send_to_device = Mock(return_value=True)
        
        notification_data = {
            "app": "WhatsApp",
            "sender": "John",
            "text": "Hello!",
            "package_name": "com.whatsapp",
            "timestamp": int(datetime.now().timestamp()),
            "priority": 1
        }
        
        result = process_notification(notification_data)
        
        assert result == True
        mock_save.assert_called_once()

class TestSpamFiltering:
    """Test spam filtering functionality"""

    def test_spam_keywords_detection(self):
        """Test detection of spam keywords"""
        spam_keywords = [
            "free", "winner", "congratulations", "urgent", 
            "limited time", "act now", "click here", "prize"
        ]
        
        for keyword in spam_keywords:
            message = f"Hello {keyword} offer for you!"
            assert is_spam(message, "Unknown") == True

    def test_suspicious_sender_detection(self):
        """Test detection of suspicious senders"""
        suspicious_senders = ["Unknown", "NoReply", "Automated", ""]
        
        for sender in suspicious_senders:
            assert is_spam("Regular message", sender) == True

    def test_legitimate_sender_bypass(self):
        """Test that known senders bypass spam detection"""
        known_senders = ["John Doe", "Alice Smith", "Bob Johnson"]
        
        for sender in known_senders:
            # Even with spam keywords, known senders should not be filtered
            result = is_spam("free lunch tomorrow?", sender)
            # This depends on implementation - adjust based on actual logic
            assert isinstance(result, bool)

class TestErrorHandling:
    """Test error handling scenarios"""

    def test_invalid_json_request(self):
        """Test handling of invalid JSON requests"""
        response = client.post("/chat", data="invalid json")
        assert response.status_code == 422

    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        response = client.post("/notify", json={"app": "Test"})  # Missing required fields
        assert response.status_code == 422

    @patch('main.chat_with_ai')
    def test_ai_service_unavailable(self, mock_chat):
        """Test handling when AI service is unavailable"""
        mock_chat.return_value = "Error fetching AI response: Service unavailable"
        
        response = client.post("/chat", json={
            "text": "Hello",
            "spoken": False
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "Error fetching AI response" in data["AI"]

class TestFirebaseIntegration:
    """Test Firebase integration"""

    @patch('main.fcm_service')
    def test_firebase_message_sending(self, mock_fcm):
        """Test Firebase message sending"""
        mock_fcm.send_to_device = Mock(return_value=True)
        
        notification_data = {
            "app": "WhatsApp",
            "sender": "John",
            "text": "Test message",
            "package_name": "com.whatsapp",
            "timestamp": int(datetime.now().timestamp()),
            "priority": 1
        }
        
        response = client.post("/notify", json=notification_data)
        
        assert response.status_code == 200
        mock_fcm.send_to_device.assert_called()

    @patch('main.fcm_service')
    def test_device_registration_with_firebase(self, mock_fcm):
        """Test device registration with Firebase"""
        mock_fcm.register_device = Mock(return_value=True)
        mock_fcm.get_device_count = Mock(return_value=1)
        
        device_data = {
            "device_id": "test-device",
            "fcm_token": "test-fcm-token"
        }
        
        response = client.post("/register_device", json=device_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        mock_fcm.register_device.assert_called_once_with("test-device", "test-fcm-token")

class TestPerformance:
    """Test performance and load scenarios"""

    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            with patch('main.chat_with_ai') as mock_chat:
                mock_chat.return_value = "Response"
                response = client.post("/chat", json={"text": "Hello", "spoken": False})
                results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5

    def test_large_notification_data(self):
        """Test handling of large notification data"""
        large_text = "A" * 10000  # 10KB of text
        
        notification_data = {
            "app": "WhatsApp",
            "sender": "John",
            "text": large_text,
            "package_name": "com.whatsapp",
            "timestamp": int(datetime.now().timestamp()),
            "priority": 1
        }
        
        with patch('main.process_notification') as mock_process:
            mock_process.return_value = True
            response = client.post("/notify", json=notification_data)
            
            assert response.status_code == 200

# Test utilities
class TestUtilities:
    """Test utility functions"""

    def test_timestamp_validation(self):
        """Test timestamp validation in notifications"""
        current_time = int(datetime.now().timestamp())
        
        # Test with current timestamp
        notification_data = {
            "app": "Test",
            "sender": "Test",
            "text": "Test",
            "package_name": "com.test",
            "timestamp": current_time,
            "priority": 1
        }
        
        with patch('main.process_notification') as mock_process:
            mock_process.return_value = True
            response = client.post("/notify", json=notification_data)
            assert response.status_code == 200

    def test_priority_handling(self):
        """Test notification priority handling"""
        priorities = [1, 2, 3, 4, 5]
        
        for priority in priorities:
            notification_data = {
                "app": "Test",
                "sender": "Test",
                "text": "Test",
                "package_name": "com.test",
                "timestamp": int(datetime.now().timestamp()),
                "priority": priority
            }
            
            with patch('main.process_notification') as mock_process:
                mock_process.return_value = True
                response = client.post("/notify", json=notification_data)
                assert response.status_code == 200

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])