"""
Firebase Push Notifications Integration
Complete implementation for sending push notifications to your Voice Assistant Android app
"""

import firebase_admin
from firebase_admin import credentials, messaging
import json
import logging
from typing import Optional, List, Dict
from datetime import datetime

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with service account credentials"""
    try:
        # Path to your service account key file
        cred = credentials.Certificate("firebase_admin_config.json")
        firebase_admin.initialize_app(cred)
        logging.info("Firebase Admin SDK initialized successfully")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False

class FirebasePushNotificationManager:
    """Manages Firebase push notifications for Voice Assistant"""
    
    def __init__(self):
        self.initialized = initialize_firebase()
        
    def send_message_to_device(self, fcm_token: str, message_text: str, title: str = "Voice Assistant") -> bool:
        """Send a push notification to a specific device"""
        if not self.initialized:
            logging.error("Firebase not initialized")
            return False
            
        try:
            # Create the message
            message = messaging.Message(
                data={
                    'message': message_text,
                    'type': 'server_response',
                    'timestamp': datetime.now().isoformat()
                },
                notification=messaging.Notification(
                    title=title,
                    body=message_text
                ),
                android=messaging.AndroidConfig(
                    priority='high',  # Ensures delivery even when app is in background
                    notification=messaging.AndroidNotification(
                        channel_id='voice_assistant_channel',
                        sound='default'
                    )
                ),
                token=fcm_token
            )
            
            # Send the message
            response = messaging.send(message)
            logging.info(f"Successfully sent message to {fcm_token[:20]}... Response: {response}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send message to {fcm_token[:20]}...: {e}")
            return False
    
    def send_message_to_multiple_devices(self, fcm_tokens: List[str], message_text: str, title: str = "Voice Assistant") -> Dict[str, bool]:
        """Send a push notification to multiple devices"""
        if not self.initialized:
            logging.error("Firebase not initialized")
            return {}
            
        results = {}
        
        try:
            # Create the message
            message = messaging.MulticastMessage(
                data={
                    'message': message_text,
                    'type': 'server_response',
                    'timestamp': datetime.now().isoformat()
                },
                notification=messaging.Notification(
                    title=title,
                    body=message_text
                ),
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        channel_id='voice_assistant_channel',
                        sound='default'
                    )
                ),
                tokens=fcm_tokens
            )
            
            # Send to multiple devices
            response = messaging.send_multicast(message)
            
            # Process results
            for i, result in enumerate(response.responses):
                token = fcm_tokens[i]
                if result.success:
                    results[token] = True
                    logging.info(f"Successfully sent message to {token[:20]}...")
                else:
                    results[token] = False
                    logging.error(f"Failed to send message to {token[:20]}...: {result.exception}")
                    
            logging.info(f"Multicast result: {response.success_count} successful, {response.failure_count} failed")
            return results
            
        except Exception as e:
            logging.error(f"Failed to send multicast message: {e}")
            return {token: False for token in fcm_tokens}
    
    def send_ai_response(self, fcm_token: str, ai_response: str) -> bool:
        """Send AI response as push notification (will be spoken by the app)"""
        return self.send_message_to_device(
            fcm_token=fcm_token,
            message_text=ai_response,
            title="AI Response"
        )
    
    def send_notification_alert(self, fcm_token: str, notification_text: str) -> bool:
        """Send notification alert as push notification"""
        return self.send_message_to_device(
            fcm_token=fcm_token,
            message_text=f"Notification: {notification_text}",
            title="New Notification"
        )

# Global instance
push_manager = FirebasePushNotificationManager()

# Integration functions for your existing FastAPI server
def send_push_to_device(device_id: str, message: str, registered_devices: dict) -> bool:
    """Send push notification to a specific registered device"""
    if device_id not in registered_devices:
        logging.warning(f"Device {device_id} not found in registered devices")
        return False
        
    device_data = registered_devices[device_id]
    fcm_token = device_data.get('fcm_token')
    
    if not fcm_token:
        logging.warning(f"No FCM token found for device {device_id}")
        return False
        
    return push_manager.send_ai_response(fcm_token, message)

def send_push_to_all_devices(message: str, registered_devices: dict) -> Dict[str, bool]:
    """Send push notification to all registered devices"""
    if not registered_devices:
        logging.warning("No registered devices found")
        return {}
        
    fcm_tokens = []
    device_mapping = {}
    
    for device_id, device_data in registered_devices.items():
        fcm_token = device_data.get('fcm_token')
        if fcm_token:
            fcm_tokens.append(fcm_token)
            device_mapping[fcm_token] = device_id
    
    if not fcm_tokens:
        logging.warning("No FCM tokens found for any devices")
        return {}
        
    results = push_manager.send_message_to_multiple_devices(fcm_tokens, message)
    
    # Convert token-based results to device-id based results
    device_results = {}
    for token, success in results.items():
        device_id = device_mapping.get(token, "unknown")
        device_results[device_id] = success
        
    return device_results

# Example usage and testing
if __name__ == "__main__":
    # Test the Firebase integration
    logging.basicConfig(level=logging.INFO)
    
    # Example: Send a test message
    test_token = "your_test_fcm_token_here"
    test_message = "Hello from your Voice Assistant server!"
    
    if push_manager.initialized:
        print("Firebase initialized successfully!")
        # Uncomment to test:
        # success = push_manager.send_message_to_device(test_token, test_message)
        # print(f"Test message sent: {success}")
    else:
        print("Firebase initialization failed. Check your firebase_admin_config.json file.")