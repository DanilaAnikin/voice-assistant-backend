import firebase_admin
from firebase_admin import credentials, messaging
import os
import json
import time

class FCMService:
    def __init__(self):
        self.app = None
        self.init_firebase()
    
    def init_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Try to load service account key from file
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json")
            
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                self.app = firebase_admin.initialize_app(cred)
                print("Firebase initialized with service account file")
            else:
                print("Firebase service account file not found. FCM disabled.")
                print(f"Create {service_account_path} with your Firebase service account key")
                
        except Exception as e:
            print(f"Failed to initialize Firebase: {e}")
            print("FCM features will be disabled")
    
    def send_message_to_device(self, token: str, message: str, message_type: str = "server_message"):
        """Send message to specific device"""
        if not self.app:
            print("Firebase not initialized. Cannot send message.")
            return False
        
        try:
            message_obj = messaging.Message(
                data={
                    'message': message,
                    'type': message_type,
                    'timestamp': str(int(time.time()))
                },
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    data={
                        'message': message,
                        'type': message_type
                    }
                )
            )
            
            response = messaging.send(message_obj)
            print(f"Successfully sent message to {token}: {response}")
            return True
            
        except Exception as e:
            print(f"Failed to send FCM message: {e}")
            return False
    
    def send_custom_notification(self, token: str, title: str, body: str):
        """Send notification with title and body"""
        if not self.app:
            return False
        
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={
                    'message': body,
                    'type': 'notification'
                },
                token=token
            )
            
            response = messaging.send(message)
            print(f"Successfully sent notification: {response}")
            return True
            
        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

# Global FCM service instance
fcm_service = FCMService()