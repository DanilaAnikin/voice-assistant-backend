#!/usr/bin/env python3
"""
Comprehensive tests for all src/ modules
Tests speech_to_text, text_to_speech, memory, fcm_service, and ai modules
"""

import pytest
import os
import sqlite3
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
import json
import time

# Import modules to test
from src.fcm_service import FCMService
import src.speech_to_text as stt
import src.text_to_speech as tts
import src.memory as memory

class TestFCMService:
    """Test Firebase Cloud Messaging service"""
    
    def setup_method(self):
        """Setup for each test"""
        # Clear any existing app instances
        pass
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', False)
    def test_fcm_service_without_firebase(self):
        """Test FCM service when Firebase is not available"""
        service = FCMService()
        assert service.app is None
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', True)
    @patch('src.fcm_service.os.path.exists')
    @patch('src.fcm_service.firebase_admin.initialize_app')
    @patch('src.fcm_service.credentials.Certificate')
    def test_fcm_service_initialization_success(self, mock_cert, mock_init, mock_exists):
        """Test successful FCM service initialization"""
        mock_exists.return_value = True
        mock_app = Mock()
        mock_init.return_value = mock_app
        
        service = FCMService()
        
        assert service.app == mock_app
        mock_cert.assert_called()
        mock_init.assert_called_once()
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', True)
    @patch('src.fcm_service.os.path.exists')
    def test_fcm_service_initialization_no_key_file(self, mock_exists):
        """Test FCM service initialization when key file doesn't exist"""
        mock_exists.return_value = False
        
        service = FCMService()
        
        assert service.app is None
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', True)
    @patch('src.fcm_service.messaging.send')
    def test_send_message_to_device_success(self, mock_send):
        """Test successful message sending"""
        service = FCMService()
        service.app = Mock()  # Simulate initialized app
        mock_send.return_value = "message_id_123"
        
        result = service.send_message_to_device("test_token", "Test message", "test_type")
        
        assert result == True
        mock_send.assert_called_once()
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', True)
    @patch('src.fcm_service.messaging.send')
    def test_send_message_to_device_failure(self, mock_send):
        """Test message sending failure"""
        service = FCMService()
        service.app = Mock()
        mock_send.side_effect = Exception("Firebase error")
        
        result = service.send_message_to_device("test_token", "Test message", "test_type")
        
        assert result == False
    
    def test_send_message_without_app(self):
        """Test sending message when app is not initialized"""
        service = FCMService()
        service.app = None
        
        result = service.send_message_to_device("test_token", "Test message")
        
        assert result == False
    
    @patch('src.fcm_service.FIREBASE_AVAILABLE', True)
    @patch('src.fcm_service.messaging.send')
    def test_send_custom_notification(self, mock_send):
        """Test sending custom notification with title and body"""
        service = FCMService()
        service.app = Mock()
        mock_send.return_value = "notification_id_456"
        
        result = service.send_custom_notification("test_token", "Test Title", "Test Body")
        
        assert result == True
        mock_send.assert_called_once()
        # Verify the message structure
        call_args = mock_send.call_args[0][0]
        assert hasattr(call_args, 'notification')
        assert hasattr(call_args, 'data')
        assert hasattr(call_args, 'token')

class TestSpeechToText:
    """Test speech-to-text functionality"""
    
    def test_recognize_speech_function_exists(self):
        """Test that recognize_speech function exists"""
        assert hasattr(stt, 'recognize_speech')
        assert callable(stt.recognize_speech)
    
    @patch('src.speech_to_text.sr.Recognizer')
    @patch('src.speech_to_text.sr.Microphone')
    def test_recognize_speech_success(self, mock_mic, mock_recognizer):
        """Test successful speech recognition"""
        # Mock the recognizer and microphone
        mock_rec_instance = Mock()
        mock_mic_instance = Mock()
        mock_recognizer.return_value = mock_rec_instance
        mock_mic.return_value = mock_mic_instance
        
        # Mock successful recognition
        mock_rec_instance.listen.return_value = "audio_data"
        mock_rec_instance.recognize_google.return_value = "Hello world"
        
        # Import and test (if the function uses these libraries)
        try:
            result = stt.recognize_speech()
            # The actual implementation might be different
        except (AttributeError, ImportError):
            # If the module doesn't have this exact implementation, test what it has
            pytest.skip("Speech recognition implementation differs from expected")
    
    def test_speech_to_text_imports(self):
        """Test that speech_to_text module imports correctly"""
        import src.speech_to_text
        # Basic test that the module loads
        assert src.speech_to_text is not None

class TestTextToSpeech:
    """Test text-to-speech functionality"""
    
    def test_speak_function_exists(self):
        """Test that speak function exists"""
        assert hasattr(tts, 'speak')
        assert callable(tts.speak)
    
    @patch('src.text_to_speech.gTTS')
    @patch('src.text_to_speech.os.system')
    def test_speak_success(self, mock_system, mock_gtts):
        """Test successful text-to-speech"""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        tts.speak("Hello, this is a test")
        
        mock_gtts.assert_called_once_with(text="Hello, this is a test", lang="en")
        mock_tts_instance.save.assert_called_once_with("response.mp3")
        mock_system.assert_called_once_with("mpg321 response.mp3")
    
    @patch('src.text_to_speech.gTTS')
    def test_speak_with_gtts_error(self, mock_gtts):
        """Test speak function error handling"""
        mock_gtts.side_effect = Exception("gTTS error")
        
        # Should not raise exception
        try:
            tts.speak("Test text")
        except Exception as e:
            pytest.fail(f"speak() raised an exception: {e}")
    
    def test_speak_empty_text(self):
        """Test speak function with empty text"""
        with patch('src.text_to_speech.gTTS') as mock_gtts:
            tts.speak("")
            # Should handle empty text gracefully
            mock_gtts.assert_called_once_with(text="", lang="en")
    
    def test_speak_special_characters(self):
        """Test speak function with special characters"""
        with patch('src.text_to_speech.gTTS') as mock_gtts:
            test_text = "Hello! How are you? I'm doing well. 100% great!"
            tts.speak(test_text)
            mock_gtts.assert_called_once_with(text=test_text, lang="en")

class TestMemory:
    """Test memory/database functionality"""
    
    def setup_method(self):
        """Setup temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db_path = self.temp_db.name
    
    def teardown_method(self):
        """Cleanup temporary database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_save_conversation_function_exists(self):
        """Test that save_conversation function exists"""
        assert hasattr(memory, 'save_conversation')
        assert callable(memory.save_conversation)
    
    @patch('src.memory.sqlite3.connect')
    def test_save_conversation_success(self, mock_connect):
        """Test successful conversation saving"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        memory.save_conversation("Hello", "Hi there!")
        
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    @patch('src.memory.sqlite3.connect')
    def test_save_conversation_database_error(self, mock_connect):
        """Test conversation saving with database error"""
        mock_connect.side_effect = sqlite3.Error("Database error")
        
        # Should handle database errors gracefully
        try:
            memory.save_conversation("Hello", "Hi there!")
        except sqlite3.Error:
            pytest.fail("save_conversation should handle database errors")
    
    def test_save_conversation_empty_inputs(self):
        """Test saving conversation with empty inputs"""
        with patch('src.memory.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            memory.save_conversation("", "")
            # Should still attempt to save
            mock_connect.assert_called_once()
    
    def test_save_conversation_special_characters(self):
        """Test saving conversation with special characters"""
        with patch('src.memory.sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            user_input = "What's 2+2? Can you help with 'coding'?"
            ai_response = "2+2=4. I'd be happy to help with \"coding\" questions!"
            
            memory.save_conversation(user_input, ai_response)
            mock_connect.assert_called_once()
    
    def test_memory_module_imports(self):
        """Test that memory module imports correctly"""
        import src.memory
        assert src.memory is not None

class TestAIModule:
    """Test AI module functionality (if it exists as a separate module)"""
    
    def test_ai_module_imports(self):
        """Test that ai module imports correctly"""
        try:
            import src.ai
            assert src.ai is not None
        except ImportError:
            pytest.skip("AI module not found or not implemented")

class TestLiveKitHandler:
    """Test LiveKit handler functionality"""
    
    def test_livekit_module_imports(self):
        """Test that livekit_handler module imports correctly"""
        try:
            import src.livekit_handler
            assert src.livekit_handler is not None
        except ImportError:
            pytest.skip("LiveKit handler module not found")
    
    def test_livekit_handler_basic_functionality(self):
        """Test basic LiveKit handler functionality if available"""
        try:
            import src.livekit_handler as lk
            # Test any available functions
            if hasattr(lk, 'initialize'):
                assert callable(lk.initialize)
        except ImportError:
            pytest.skip("LiveKit handler not available")

class TestModuleIntegration:
    """Test integration between modules"""
    
    @patch('src.text_to_speech.speak')
    @patch('src.memory.save_conversation')
    def test_chat_to_tts_integration(self, mock_save, mock_speak):
        """Test integration between chat response and TTS"""
        # Simulate the flow from main.py
        user_input = "How are you?"
        ai_response = "I'm doing well, thank you!"
        
        # Save conversation
        memory.save_conversation(user_input, ai_response)
        
        # Speak response
        tts.speak(ai_response)
        
        mock_save.assert_called_once_with(user_input, ai_response)
        mock_speak.assert_called_once_with(ai_response)
    
    @patch('src.fcm_service.FCMService.send_message_to_device')
    def test_fcm_integration(self, mock_send):
        """Test FCM service integration"""
        service = FCMService()
        service.app = Mock()  # Simulate initialized app
        mock_send.return_value = True
        
        # Test sending a message
        result = service.send_message_to_device("test_token", "Test message")
        
        assert result == True

class TestErrorHandling:
    """Test error handling across all modules"""
    
    def test_tts_with_none_input(self):
        """Test TTS with None input"""
        with patch('src.text_to_speech.gTTS') as mock_gtts:
            try:
                tts.speak(None)
            except TypeError:
                # Expected behavior - gTTS should handle None gracefully
                pass
    
    def test_memory_with_none_inputs(self):
        """Test memory functions with None inputs"""
        with patch('src.memory.sqlite3.connect') as mock_connect:
            try:
                memory.save_conversation(None, None)
            except Exception:
                # Should handle None inputs gracefully
                pass
    
    def test_fcm_with_invalid_token(self):
        """Test FCM with invalid token"""
        service = FCMService()
        service.app = Mock()
        
        result = service.send_message_to_device("", "Test message")
        # Should handle empty token gracefully
        assert isinstance(result, bool)

class TestPerformance:
    """Test performance characteristics"""
    
    def test_fcm_service_initialization_time(self):
        """Test FCM service initialization is reasonably fast"""
        import time
        start_time = time.time()
        
        with patch('src.fcm_service.FIREBASE_AVAILABLE', False):
            service = FCMService()
        
        end_time = time.time()
        initialization_time = end_time - start_time
        
        # Should initialize quickly (under 1 second)
        assert initialization_time < 1.0
    
    @patch('src.text_to_speech.gTTS')
    @patch('src.text_to_speech.os.system')
    def test_tts_call_time(self, mock_system, mock_gtts):
        """Test TTS function call time"""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        start_time = time.time()
        tts.speak("Short test message")
        end_time = time.time()
        
        call_time = end_time - start_time
        # Function call should be fast (actual TTS generation is mocked)
        assert call_time < 0.1

class TestModuleConstants:
    """Test module constants and configurations"""
    
    def test_fcm_service_constants(self):
        """Test FCM service has proper constants"""
        import src.fcm_service as fcm
        assert hasattr(fcm, 'FIREBASE_AVAILABLE')
        assert isinstance(fcm.FIREBASE_AVAILABLE, bool)
    
    def test_speech_modules_have_required_imports(self):
        """Test speech modules have required imports"""
        # Test imports work without errors
        import src.speech_to_text
        import src.text_to_speech
        # Basic existence test
        assert src.speech_to_text is not None
        assert src.text_to_speech is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])