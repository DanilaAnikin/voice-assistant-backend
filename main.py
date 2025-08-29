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

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

if not openai_api_key:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in .env")

app = FastAPI()

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

@app.post("/chat")
async def chat_with_assistant(request: Request):
    try:
        data = await request.json()
        user_input = data.get("text")  # Text input

        if not user_input:
            user_input = recognize_speech()  # ✅ Convert speech to text

        ai_response = chat_with_ai(user_input)
        save_conversation(user_input, ai_response)

        if data.get("spoken", False):
            speak(ai_response)  # ✅ Generate spoken output

        return {"User": user_input, "AI": ai_response}

    except Exception as e:
        return {"error": f"Backend failure: {str(e)}"}


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


# Device token storage (in production, use a proper database)
device_tokens = {}

@app.post("/register_device")
async def register_device(request: Request):
    """Register FCM token for device"""
    try:
        data = await request.json()
        device_id = data.get("device_id", "default")
        fcm_token = data.get("fcm_token", "")
        
        if fcm_token:
            device_tokens[device_id] = fcm_token
            print(f"Registered device {device_id} with token: {fcm_token[:20]}...")
            return {"result": "success", "message": "Device registered"}
        else:
            return {"error": "No FCM token provided"}
    
    except Exception as e:
        return {"error": f"Error registering device: {str(e)}"}

@app.post("/send_message")
async def send_custom_message(request: Request):
    """Send custom message to be spoken on phone"""
    try:
        data = await request.json()
        message = data.get("message", "")
        device_id = data.get("device_id", "default")
        message_type = data.get("type", "server_message")
        
        if not message:
            return {"error": "No message provided"}
        
        # Get device token
        fcm_token = device_tokens.get(device_id)
        if not fcm_token:
            return {"error": f"No registered device found for {device_id}"}
        
        # Send via FCM
        success = fcm_service.send_message_to_device(fcm_token, message, message_type)
        
        if success:
            return {"result": "success", "message": f"Message sent to {device_id}"}
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
        
        fcm_token = device_tokens.get(device_id)
        if not fcm_token:
            return {"error": f"No registered device found for {device_id}"}
        
        success = fcm_service.send_custom_notification(fcm_token, title, body)
        
        if success:
            return {"result": "success", "message": "Notification sent"}
        else:
            return {"error": "Failed to send notification"}
    
    except Exception as e:
        return {"error": f"Error sending notification: {str(e)}"}

@app.get("/devices")
async def list_devices():
    """List registered devices"""
    return {
        "devices": list(device_tokens.keys()),
        "count": len(device_tokens)
    }
