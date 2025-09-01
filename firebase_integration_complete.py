"""
Complete Firebase Integration for Voice Assistant Backend
Add this code to your existing FastAPI server (main.py or app.py)
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import logging

# Import the Firebase push notification manager
from firebase_push_notifications import push_manager, send_push_to_device, send_push_to_all_devices

# Your existing FastAPI app
app = FastAPI(title="Voice Assistant with Firebase")

# Device registration storage (use database in production)
registered_devices: Dict[str, dict] = {}

# Data models (add these to your existing models)
class DeviceRegistrationRequest(BaseModel):
    device_id: str
    fcm_token: str
    device_type: str = "android"
    app_version: str = "1.0"

class DeviceRegistrationResponse(BaseModel):
    status: str
    message: Optional[str] = None
    device_id: Optional[str] = None

class ChatRequest(BaseModel):
    text: Optional[str] = None
    spoken: bool = False
    device_id: Optional[str] = None  # New: identify which device sent the request

class ChatResponse(BaseModel):
    User: Optional[str] = None
    AI: Optional[str] = None
    error: Optional[str] = None
    pushed_to_devices: Optional[List[str]] = None  # New: list of devices that received push

class NotificationRequest(BaseModel):
    title: str
    message: str
    app_name: Optional[str] = None
    device_id: Optional[str] = None

class NotificationResponse(BaseModel):
    result: str
    output: Optional[str] = None
    pushed_to_devices: Optional[List[str]] = None

# API Endpoints

@app.post("/register_device", response_model=DeviceRegistrationResponse)
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
        
        # Save to storage (use database in production)
        registered_devices[request.device_id] = device_data
        
        logging.info(f"Device registered: {request.device_id} with token: {request.fcm_token[:20]}...")
        
        # Send welcome message to the newly registered device
        if push_manager.initialized:
            welcome_msg = "Welcome! Your Voice Assistant is now connected and ready to receive notifications."
            push_manager.send_message_to_device(
                fcm_token=request.fcm_token,
                message_text=welcome_msg,
                title="Voice Assistant Connected"
            )
        
        return DeviceRegistrationResponse(
            status="success", 
            message="Device registered successfully. Welcome message sent!",
            device_id=request.device_id
        )
        
    except Exception as e:
        logging.error(f"Device registration failed: {str(e)}")
        return DeviceRegistrationResponse(
            status="error",
            message=f"Registration failed: {str(e)}"
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Enhanced chat endpoint with push notification support"""
    try:
        user_message = request.text or "Hello"
        
        # Your existing AI processing here
        # This is just an example - replace with your actual AI logic
        ai_response = f"You said: '{user_message}'. This is your AI assistant responding!"
        
        pushed_devices = []
        
        # Send AI response as push notification to devices
        if push_manager.initialized and registered_devices:
            if request.device_id:
                # Send to specific device
                success = send_push_to_device(request.device_id, ai_response, registered_devices)
                if success:
                    pushed_devices.append(request.device_id)
            else:
                # Send to all registered devices
                results = send_push_to_all_devices(ai_response, registered_devices)
                pushed_devices = [device_id for device_id, success in results.items() if success]
        
        return ChatResponse(
            User=user_message,
            AI=ai_response,
            pushed_to_devices=pushed_devices
        )
        
    except Exception as e:
        logging.error(f"Chat processing failed: {str(e)}")
        return ChatResponse(
            User=request.text,
            error=f"Chat failed: {str(e)}"
        )

@app.post("/notify", response_model=NotificationResponse)
async def process_notification(request: NotificationRequest):
    """Process notification and send to devices via push"""
    try:
        # Process the notification (your existing logic)
        notification_text = f"{request.title}: {request.message}"
        
        # Your existing AI processing for notifications
        ai_response = f"You have a new notification: {notification_text}"
        
        pushed_devices = []
        
        # Send as push notification
        if push_manager.initialized and registered_devices:
            if request.device_id:
                # Send to specific device
                success = send_push_to_device(request.device_id, ai_response, registered_devices)
                if success:
                    pushed_devices.append(request.device_id)
            else:
                # Send to all registered devices
                results = send_push_to_all_devices(ai_response, registered_devices)
                pushed_devices = [device_id for device_id, success in results.items() if success]
        
        return NotificationResponse(
            result="success",
            output=ai_response,
            pushed_to_devices=pushed_devices
        )
        
    except Exception as e:
        logging.error(f"Notification processing failed: {str(e)}")
        return NotificationResponse(
            result="error",
            output=f"Failed to process notification: {str(e)}"
        )

@app.post("/send_message_to_device")
async def send_message_to_device_endpoint(device_id: str, message: str):
    """Send a custom message to a specific device"""
    try:
        success = send_push_to_device(device_id, message, registered_devices)
        
        return {
            "status": "success" if success else "failed",
            "device_id": device_id,
            "message": "Message sent successfully" if success else "Failed to send message"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/broadcast_message")
async def broadcast_message(message: str):
    """Send a message to all registered devices"""
    try:
        results = send_push_to_all_devices(message, registered_devices)
        
        successful_devices = [device_id for device_id, success in results.items() if success]
        failed_devices = [device_id for device_id, success in results.items() if not success]
        
        return {
            "status": "completed",
            "successful_devices": successful_devices,
            "failed_devices": failed_devices,
            "total_devices": len(registered_devices),
            "successful_count": len(successful_devices)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/registered_devices")
async def list_registered_devices():
    """List all registered devices (for debugging)"""
    return {
        "devices": {
            device_id: {
                "device_type": data["device_type"],
                "app_version": data["app_version"],
                "registered_at": data["registered_at"],
                "fcm_token": data["fcm_token"][:20] + "..." if data["fcm_token"] else None
            }
            for device_id, data in registered_devices.items()
        },
        "count": len(registered_devices),
        "firebase_initialized": push_manager.initialized
    }

@app.get("/firebase_status")
async def firebase_status():
    """Check Firebase initialization status"""
    return {
        "firebase_initialized": push_manager.initialized,
        "registered_devices_count": len(registered_devices),
        "can_send_notifications": push_manager.initialized and len(registered_devices) > 0
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize Firebase when server starts"""
    logging.info("Starting Voice Assistant Server with Firebase support")
    if push_manager.initialized:
        logging.info("✅ Firebase Admin SDK initialized successfully")
    else:
        logging.warning("❌ Firebase Admin SDK failed to initialize")

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    print("🔥 Voice Assistant Server with Firebase Push Notifications")
    print("📱 Ready to receive device registrations and send notifications!")
    uvicorn.run(app, host="0.0.0.0", port=8000)