# Firebase Integration for Voice Assistant Backend
# Add this to your existing FastAPI server

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging

# Add these models to your existing server
class DeviceRegistrationRequest(BaseModel):
    device_id: str
    fcm_token: str
    device_type: str = "android"
    app_version: str = "1.0"

class DeviceRegistrationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    device_id: Optional[str] = None

# In-memory storage for demo (you should use a real database)
registered_devices = {}

# Add this endpoint to your FastAPI app
@app.post("/register_device")
async def register_device(request: DeviceRegistrationRequest):
    """Register an Android device for push notifications"""
    try:
        # Store device registration
        device_data = {
            "device_id": request.device_id,
            "fcm_token": request.fcm_token,
            "device_type": request.device_type,
            "app_version": request.app_version,
            "registered_at": datetime.now().isoformat()
        }
        
        # Save to in-memory storage (use database in production)
        registered_devices[request.device_id] = device_data
        
        logging.info(f"Device registered: {request.device_id} with token: {request.fcm_token[:20]}...")
        
        return DeviceRegistrationResponse(
            status="success", 
            message="Device registered successfully",
            device_id=request.device_id
        )
        
    except Exception as e:
        logging.error(f"Device registration failed: {str(e)}")
        return DeviceRegistrationResponse(
            status="error",
            message=f"Registration failed: {str(e)}"
        )

# Helper function to get device token (for sending notifications)
def get_device_token(device_id: str) -> Optional[str]:
    """Get FCM token for a specific device"""
    device = registered_devices.get(device_id)
    return device["fcm_token"] if device else None

# Example: Send push notification (requires Firebase Server Key)
import requests

def send_push_notification(fcm_token: str, message: str, server_key: str = None):
    """Send push notification to Android device"""
    if not server_key:
        logging.warning("No Firebase server key provided - cannot send push notification")
        return None
    
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
        "Authorization": f"key={server_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "to": fcm_token,
        "data": {
            "message": message,
            "type": "server_response"
        },
        "notification": {
            "title": "Voice Assistant Response",
            "body": message
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        logging.info(f"Push notification sent: {response.status_code}")
        return response.json()
    except Exception as e:
        logging.error(f"Failed to send push notification: {str(e)}")
        return None

# Example usage in your existing chat endpoint:
"""
@app.post("/chat")
async def chat(request: ChatRequest):
    # Your existing chat logic here...
    ai_response = "Your AI response"
    
    # Optional: Send response as push notification to registered devices
    for device_id, device_data in registered_devices.items():
        fcm_token = device_data["fcm_token"]
        # send_push_notification(fcm_token, ai_response, YOUR_FIREBASE_SERVER_KEY)
    
    return {"AI": ai_response, "User": request.text}
"""

# Endpoint to list registered devices (for debugging)
@app.get("/registered_devices")
async def list_registered_devices():
    """List all registered devices (for debugging)"""
    return {
        "devices": list(registered_devices.keys()),
        "count": len(registered_devices)
    }

if __name__ == "__main__":
    print("Firebase integration module loaded")
    print(f"Registered devices storage: {registered_devices}")