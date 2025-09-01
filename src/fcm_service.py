import os
import json
import time

# Optional Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Warning: firebase_admin not installed. FCM features will be disabled.")
    print("Install with: pip install firebase-admin")
    FIREBASE_AVAILABLE = False

class FCMService:
    def __init__(self):
        self.app = None
        self.init_firebase()
    
    def init_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not FIREBASE_AVAILABLE:
            print("Firebase Admin SDK not available. FCM disabled.")
            return
            
        try:
            # Try to load service account key from file
            service_account_paths = [
                "firebase_admin_config.json",  # New path
                os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "firebase-service-account.json"),  # Original path
                "firebase-service-account.json"  # Backup path
            ]
            
            for service_account_path in service_account_paths:
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    self.app = firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase initialized successfully with {service_account_path}")
                    print(f"🔥 FCM Push Notifications are now active!")
                    return
            
            print("❌ Firebase service account file not found. FCM disabled.")
            print("📁 Looking for: firebase_admin_config.json or firebase-service-account.json")
                
        except Exception as e:
            print(f"❌ Failed to initialize Firebase: {e}")
            print("🔥 FCM features will be disabled")
    
    def send_message_to_device(self, token: str, message: str, message_type: str = "server_message"):
        """Send message to specific device"""
        if not FIREBASE_AVAILABLE:
            print("Firebase Admin SDK not available. Cannot send message.")
            return False
            
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
        if not FIREBASE_AVAILABLE:
            print("Firebase Admin SDK not available. Cannot send notification.")
            return False
            
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