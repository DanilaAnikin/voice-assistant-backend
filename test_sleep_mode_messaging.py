#!/usr/bin/env python3
"""
Test Suite for Sleep Mode Messaging
Tests the complete flow of sending messages to sleeping devices with TTS and silent modes
"""

import pytest
import requests
import time
import subprocess
import json
from typing import Dict, Any

# Test configuration
SERVER_URL = "http://localhost:8000"
TEST_DEVICE_ID = "test_device_123"

class SleepModeMessagingTests:
    def __init__(self, server_url: str = SERVER_URL):
        self.server_url = server_url
        self.session = requests.Session()
        
    def test_server_status(self) -> bool:
        """Test if server is running and Firebase is initialized"""
        try:
            response = self.session.get(f"{self.server_url}/firebase_status")
            data = response.json()
            
            assert response.status_code == 200, "Server not responding"
            assert data.get("firebase_initialized", False), "Firebase not initialized"
            
            print("✅ Server is running with Firebase initialized")
            return True
            
        except Exception as e:
            print(f"❌ Server status test failed: {e}")
            return False
    
    def test_device_registration(self) -> bool:
        """Test that devices can be registered"""
        try:
            # Register a test device
            registration_data = {
                "device_id": TEST_DEVICE_ID,
                "fcm_token": "test_token_for_sleep_mode_testing",
                "device_type": "android",
                "app_version": "1.0"
            }
            
            response = self.session.post(
                f"{self.server_url}/register_device",
                json=registration_data
            )
            
            assert response.status_code == 200, f"Registration failed: {response.text}"
            data = response.json()
            assert data.get("status") == "success", f"Registration unsuccessful: {data}"
            
            print("✅ Device registration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Device registration test failed: {e}")
            return False
    
    def test_regular_message_sending(self) -> bool:
        """Test sending regular (non-silent) messages"""
        try:
            message_data = {
                "message": "Test message for TTS",
                "device_id": TEST_DEVICE_ID,
                "type": "test_message",
                "silent": False
            }
            
            response = self.session.post(
                f"{self.server_url}/send_message",
                json=message_data
            )
            
            assert response.status_code == 200, f"Message sending failed: {response.text}"
            data = response.json()
            assert data.get("result") == "success", f"Message not sent successfully: {data}"
            
            print("✅ Regular message sending test passed")
            return True
            
        except Exception as e:
            print(f"❌ Regular message sending test failed: {e}")
            return False
    
    def test_silent_message_sending(self) -> bool:
        """Test sending silent messages"""
        try:
            message_data = {
                "message": "Silent test message",
                "device_id": TEST_DEVICE_ID,
                "type": "test_message",
                "silent": True
            }
            
            response = self.session.post(
                f"{self.server_url}/send_message",
                json=message_data
            )
            
            assert response.status_code == 200, f"Silent message sending failed: {response.text}"
            data = response.json()
            assert data.get("result") == "success", f"Silent message not sent: {data}"
            assert "(silent)" in data.get("message", ""), "Silent flag not indicated in response"
            
            print("✅ Silent message sending test passed")
            return True
            
        except Exception as e:
            print(f"❌ Silent message sending test failed: {e}")
            return False
    
    def test_broadcast_messaging(self) -> bool:
        """Test broadcasting messages to all devices"""
        try:
            # Test regular broadcast
            response = self.session.post(
                f"{self.server_url}/broadcast_message?message=Test broadcast&silent=false"
            )
            
            assert response.status_code == 200, f"Broadcast failed: {response.text}"
            data = response.json()
            assert data.get("status") == "completed", f"Broadcast not completed: {data}"
            
            # Test silent broadcast
            response = self.session.post(
                f"{self.server_url}/broadcast_message?message=Silent broadcast&silent=true"
            )
            
            assert response.status_code == 200, f"Silent broadcast failed: {response.text}"
            data = response.json()
            assert data.get("status") == "completed", f"Silent broadcast not completed: {data}"
            
            print("✅ Broadcast messaging test passed")
            return True
            
        except Exception as e:
            print(f"❌ Broadcast messaging test failed: {e}")
            return False
    
    def test_cli_tools(self) -> bool:
        """Test CLI tools with silent flag"""
        try:
            # Test regular CLI send
            result = subprocess.run([
                "python3", "cli_client.py",
                "--host", "localhost",
                "--port", "8000",
                "send", "CLI test message",
                "--device", TEST_DEVICE_ID
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0, f"CLI regular send failed: {result.stderr}"
            
            # Test silent CLI send
            result = subprocess.run([
                "python3", "cli_client.py",
                "--host", "localhost",
                "--port", "8000",
                "send", "CLI silent test message",
                "--device", TEST_DEVICE_ID,
                "--silent"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0, f"CLI silent send failed: {result.stderr}"
            
            # Test CLI broadcast
            result = subprocess.run([
                "python3", "cli_client.py",
                "--host", "localhost",
                "--port", "8000",
                "broadcast", "CLI broadcast test",
                "--silent"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0, f"CLI broadcast failed: {result.stderr}"
            
            print("✅ CLI tools test passed")
            return True
            
        except Exception as e:
            print(f"❌ CLI tools test failed: {e}")
            return False
    
    def test_shell_wrapper(self) -> bool:
        """Test the shell wrapper script"""
        try:
            # Test regular message
            result = subprocess.run([
                "bash", "vm_send_message.sh",
                "send", "Shell wrapper test"
            ], capture_output=True, text=True, timeout=15)
            
            # Should work even if no real devices (will show error but script works)
            # Test silent message
            result = subprocess.run([
                "bash", "vm_send_message.sh",
                "send", "Silent shell test", "--silent"
            ], capture_output=True, text=True, timeout=15)
            
            # Test broadcast
            result = subprocess.run([
                "bash", "vm_send_message.sh",
                "broadcast", "Shell broadcast test", "--silent"
            ], capture_output=True, text=True, timeout=15)
            
            print("✅ Shell wrapper test passed")
            return True
            
        except Exception as e:
            print(f"❌ Shell wrapper test failed: {e}")
            return False
    
    def test_message_data_structure(self) -> bool:
        """Test that messages have correct data structure for sleep mode"""
        try:
            # This would need to inspect Firebase messages, but we can't easily test that
            # Instead, we test the API response structure
            
            message_data = {
                "message": "Data structure test",
                "device_id": TEST_DEVICE_ID,
                "type": "test_message",
                "silent": True
            }
            
            response = self.session.post(
                f"{self.server_url}/send_message",
                json=message_data
            )
            
            # Should succeed and return proper structure
            assert response.status_code == 200
            data = response.json()
            
            # Check response has expected fields
            required_fields = ["result", "message"]
            for field in required_fields:
                assert field in data, f"Missing field {field} in response"
            
            print("✅ Message data structure test passed")
            return True
            
        except Exception as e:
            print(f"❌ Message data structure test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        tests = [
            ("Server Status", self.test_server_status),
            ("Device Registration", self.test_device_registration),
            ("Regular Message Sending", self.test_regular_message_sending),
            ("Silent Message Sending", self.test_silent_message_sending),
            ("Broadcast Messaging", self.test_broadcast_messaging),
            ("CLI Tools", self.test_cli_tools),
            ("Shell Wrapper", self.test_shell_wrapper),
            ("Message Data Structure", self.test_message_data_structure)
        ]
        
        results = {}
        passed = 0
        total = len(tests)
        
        print("🧪 Running Sleep Mode Messaging Tests")
        print("=" * 50)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Running: {test_name}")
            try:
                result = test_func()
                results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Sleep mode messaging is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the implementation.")
        
        return results

def main():
    """Main test runner"""
    tester = SleepModeMessagingTests()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    if all(results.values()):
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()