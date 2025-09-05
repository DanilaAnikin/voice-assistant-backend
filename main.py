from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from openai import OpenAI
import re
from typing import Dict, Any
from pydantic import BaseModel

from src.speech_to_text import recognize_speech  # ✅ Ensure this function works
from src.memory import save_conversation
from src.text_to_speech import speak
from src.fcm_service import fcm_service

# Enhanced imports for Firebase
import logging
from datetime import datetime

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

if not openai_api_key:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in .env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="🔥 Voice Assistant with Firebase Push Notifications", version="2.0")

# ✅ Enable CORS to prevent API call issues from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def chat_with_ai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content
    except Exception as e:
        return f"Error fetching AI response: {str(e)}"

class ChatRequest(BaseModel):
    text: str = None
    spoken: bool = False
    device_id: str = None

class ChatResponse(BaseModel):
    User: str
    AI: str
    error: str = None
    pushed_to_devices: list = []

@app.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    try:
        user_input = request.text

        if not user_input:
            user_input = recognize_speech()  # ✅ Convert speech to text

        ai_response = chat_with_ai(user_input)
        save_conversation(user_input, ai_response)

        if request.spoken:
            speak(ai_response)  # ✅ Generate spoken output

        # 🔥 NEW: Send AI response as push notification to registered devices
        pushed_devices = []
        if fcm_service.app and registered_devices:
            if request.device_id and request.device_id in registered_devices:
                # Send to specific device
                device_data = registered_devices[request.device_id]
                fcm_token = device_data["fcm_token"]
                success = fcm_service.send_message_to_device(fcm_token, ai_response, "ai_response")
                if success:
                    pushed_devices.append(request.device_id)
                    logger.info(f"📤 AI response sent to device: {request.device_id}")
            else:
                # Send to all registered devices
                for device_id, device_data in registered_devices.items():
                    fcm_token = device_data["fcm_token"]
                    success = fcm_service.send_message_to_device(fcm_token, ai_response, "ai_response")
                    if success:
                        pushed_devices.append(device_id)
                
                if pushed_devices:
                    logger.info(f"📤 AI response sent to {len(pushed_devices)} devices: {pushed_devices}")

        return ChatResponse(
            User=user_input, 
            AI=ai_response,
            pushed_to_devices=pushed_devices
        )

    except Exception as e:
        logger.error(f"❌ Chat processing failed: {str(e)}")
        return ChatResponse(
            User=request.text or "",
            AI="",
            error=f"Backend failure: {str(e)}"
        )


# Notification processing models
class NotificationRequest(BaseModel):
    app: str
    sender: str
    text: str
    subtext: str
    package_name: str
    timestamp: int
    priority: int

class NotificationResponse(BaseModel):
    result: str
    output: str


# Configuration - Set to False for simple echo mode
AI_ENABLED = False  # Set to True to enable AI processing
FILTER_ENABLED = True  # Set to False to disable spam filtering

# Spam keywords (can be expanded)
SPAM_KEYWORDS = [
    "free", "prize", "winner", "congratulations", "claim now", "limited time",
    "urgent", "act now", "click here", "verify account", "suspended",
    "lottery", "casino", "bet", "loan", "debt", "credit", "offer expires"
]

# Apps to always allow (can be configured by user)
ALLOWED_APPS = {
    "WhatsApp", "Messages", "Gmail", "Telegram", "Signal", "Discord",
    "Calendar", "Clock", "Phone", "SMS", "Messenger"
}

# Apps to always block
BLOCKED_APPS = {
    "Facebook", "Instagram", "TikTok", "Snapchat"  # Social media spam
}

def is_spam(text: str) -> bool:
    """Basic spam detection using keywords"""
    if not text:
        return False
    
    text_lower = text.lower()
    spam_indicators = 0
    
    for keyword in SPAM_KEYWORDS:
        if keyword in text_lower:
            spam_indicators += 1
    
    # Consider it spam if it has 2+ spam keywords
    return spam_indicators >= 2

def ai_process_notification(notification_text: str, app_name: str, sender: str) -> str:
    """Process notification with AI to make it more voice-friendly"""
    try:
        prompt = f"""You are a voice assistant. Process this notification to be read aloud naturally.

App: {app_name}
Sender: {sender}
Message: {notification_text}

Instructions:
1. Make it concise and voice-friendly
2. Add context if needed (e.g., "Message from John on WhatsApp")
3. Remove unnecessary details
4. If it's urgent/important, mention that
5. Keep it under 2 sentences

Respond with just the processed text to speak:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI processing error: {e}")
        # Fallback: basic formatting
        if sender and sender != app_name:
            return f"Message from {sender} on {app_name}: {notification_text}"
        else:
            return f"{app_name} notification: {notification_text}"

@app.post("/notify")
async def process_notification(notification: NotificationRequest) -> NotificationResponse:
    """Process incoming notification and return response to speak"""
    try:
        # Step 1: Basic filtering
        if FILTER_ENABLED:
            # Check if app is blocked
            if notification.app in BLOCKED_APPS:
                return NotificationResponse(result="filtered_out", output="")
            
            # Check if app is not in allowed list (if list is not empty)
            if ALLOWED_APPS and notification.app not in ALLOWED_APPS:
                return NotificationResponse(result="filtered_out", output="")
        
        # Step 2: Spam filtering
        if is_spam(notification.text):
            return NotificationResponse(result="spam_filtered", output="")
        
        # Step 3: Process with AI if enabled
        processed_text = notification.text  # default
        
        if AI_ENABLED and notification.text.strip():
            processed_text = ai_process_notification(
                notification.text, 
                notification.app, 
                notification.sender
            )
        
        # Step 4: Fallback formatting if AI didn't process
        if not AI_ENABLED or not processed_text.strip():
            if notification.sender and notification.sender != notification.app:
                processed_text = f"Message from {notification.sender} on {notification.app}: {notification.text}"
            else:
                processed_text = f"{notification.app}: {notification.text}"
        
        return NotificationResponse(result="success", output=processed_text)
    
    except Exception as e:
        print(f"Error processing notification: {e}")
        # Return original text as fallback
        return NotificationResponse(result="success", output=f"{notification.app}: {notification.text}")


# Enhanced device registration models
class DeviceRegistrationRequest(BaseModel):
    device_id: str
    fcm_token: str
    device_type: str = "android"
    app_version: str = "1.0"

class DeviceRegistrationResponse(BaseModel):
    status: str
    message: str
    device_id: str

# Enhanced device storage (in production, use a proper database)
registered_devices = {}

@app.post("/register_device", response_model=DeviceRegistrationResponse)
async def register_device(request: DeviceRegistrationRequest):
    """Register Android device for push notifications"""
    try:
        # Store device registration with metadata
        device_data = {
            "device_id": request.device_id,
            "fcm_token": request.fcm_token,
            "device_type": request.device_type,
            "app_version": request.app_version,
            "registered_at": datetime.now().isoformat()
        }
        
        registered_devices[request.device_id] = device_data
        
        logger.info(f"📱 Device registered: {request.device_id} with token: {request.fcm_token[:20]}...")
        
        # Send welcome message to newly registered device
        if fcm_service.app:
            welcome_msg = "🔥 Welcome! Your Voice Assistant is now connected and ready for remote notifications!"
            success = fcm_service.send_message_to_device(
                request.fcm_token, 
                welcome_msg, 
                "welcome_message"
            )
            if success:
                logger.info(f"📤 Welcome message sent to {request.device_id}")
        
        return DeviceRegistrationResponse(
            status="success", 
            message="Device registered successfully! Welcome message sent.",
            device_id=request.device_id
        )
        
    except Exception as e:
        logger.error(f"❌ Device registration failed: {str(e)}")
        return DeviceRegistrationResponse(
            status="error",
            message=f"Registration failed: {str(e)}",
            device_id=request.device_id
        )

@app.post("/send_message")
async def send_custom_message(request: Request):
    """Send custom message to be spoken on phone"""
    try:
        data = await request.json()
        message = data.get("message", "")
        device_id = data.get("device_id", "default")
        message_type = data.get("type", "server_message")
        silent = data.get("silent", False)
        
        if not message:
            return {"error": "No message provided"}
        
        # Get device token
        if device_id not in registered_devices:
            return {"error": f"No registered device found for {device_id}"}
        
        device_data = registered_devices[device_id]
        fcm_token = device_data["fcm_token"]
        
        # Send via FCM with silent flag
        success = fcm_service.send_message_to_device(fcm_token, message, message_type, silent)
        
        if success:
            silent_text = " (silent)" if silent else ""
            return {"result": "success", "message": f"Message sent to {device_id}{silent_text}"}
        else:
            return {"error": "Failed to send FCM message"}
    
    except Exception as e:
        return {"error": f"Error sending message: {str(e)}"}

@app.post("/send_notification")
async def send_notification(request: Request):
    """Send notification with title and body"""
    try:
        data = await request.json()
        title = data.get("title", "Voice Assistant")
        body = data.get("body", "")
        device_id = data.get("device_id", "default")
        
        if not body:
            return {"error": "No message body provided"}
        
        if device_id not in registered_devices:
            return {"error": f"No registered device found for {device_id}"}
        
        device_data = registered_devices[device_id]
        fcm_token = device_data["fcm_token"]
        
        success = fcm_service.send_custom_notification(fcm_token, title, body)
        
        if success:
            return {"result": "success", "message": "Notification sent"}
        else:
            return {"error": "Failed to send notification"}
    
    except Exception as e:
        return {"error": f"Error sending notification: {str(e)}"}

@app.get("/devices")
async def list_devices():
    """List all registered devices with details"""
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
        "firebase_active": fcm_service.app is not None
    }

@app.get("/firebase_status")
async def firebase_status():
    """Check Firebase and system status"""
    return {
        "firebase_initialized": fcm_service.app is not None,
        "registered_devices_count": len(registered_devices),
        "can_send_notifications": fcm_service.app is not None and len(registered_devices) > 0,
        "ai_enabled": AI_ENABLED,
        "filter_enabled": FILTER_ENABLED
    }

@app.post("/broadcast_message")
async def broadcast_message(message: str, silent: bool = False):
    """Send message to all registered devices"""
    try:
        if not fcm_service.app:
            return {"status": "error", "message": "Firebase not initialized"}
        
        if not registered_devices:
            return {"status": "error", "message": "No registered devices"}
        
        successful_devices = []
        failed_devices = []
        
        for device_id, device_data in registered_devices.items():
            fcm_token = device_data["fcm_token"]
            success = fcm_service.send_message_to_device(fcm_token, message, "broadcast", silent)
            
            if success:
                successful_devices.append(device_id)
            else:
                failed_devices.append(device_id)
        
        logger.info(f"📢 Broadcast sent to {len(successful_devices)} devices")
        
        return {
            "status": "completed",
            "message": f"Broadcast sent to {len(successful_devices)} devices",
            "successful_devices": successful_devices,
            "failed_devices": failed_devices,
            "total_devices": len(registered_devices)
        }
        
    except Exception as e:
        logger.error(f"❌ Broadcast failed: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/send_message_to_device")
async def send_message_to_device_endpoint(device_id: str, message: str):
    """Send custom message to specific device"""
    try:
        if not fcm_service.app:
            return {"status": "error", "message": "Firebase not initialized"}
        
        if device_id not in registered_devices:
            return {"status": "error", "message": f"Device {device_id} not found"}
        
        device_data = registered_devices[device_id]
        fcm_token = device_data["fcm_token"]
        
        success = fcm_service.send_message_to_device(fcm_token, message, "custom_message")
        
        if success:
            logger.info(f"📤 Message sent to {device_id}: {message}")
            return {
                "status": "success",
                "message": "Message sent successfully",
                "device_id": device_id
            }
        else:
            return {
                "status": "failed", 
                "message": "Failed to send message",
                "device_id": device_id
            }
        
    except Exception as e:
        logger.error(f"❌ Send message failed: {str(e)}")
        return {"status": "error", "message": str(e)}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Server startup initialization"""
    logger.info("🚀 Starting Voice Assistant Server with Firebase Push Notifications")
    logger.info("📱 Ready to receive Android device registrations!")
    
    if fcm_service.app:
        logger.info("✅ Firebase Admin SDK is active - Push notifications enabled")
    else:
        logger.warning("❌ Firebase Admin SDK not initialized - Push notifications disabled")
        logger.info("📁 Make sure firebase_admin_config.json exists in the project directory")

# Add main execution
if __name__ == "__main__":
    import uvicorn
    logger.info("🔥 Voice Assistant Server with Firebase Push Notifications")
    logger.info("📱 Endpoints available:")
    logger.info("   POST /register_device - Register Android devices")
    logger.info("   POST /chat - Chat with AI (sends push notifications)")
    logger.info("   POST /notify - Process notifications")
    logger.info("   POST /send_message_to_device - Send custom messages")
    logger.info("   POST /broadcast_message - Send to all devices")
    logger.info("   GET /devices - List registered devices")
    logger.info("   GET /firebase_status - Check system status")
    uvicorn.run(app, host="0.0.0.0", port=8000)
