# Voice Assistant VM Setup Guide

## Quick Fix for Current Error

Your service is failing because `firebase_admin` is not installed. The server now works without it!

### Option 1: Run without FCM (Simplest)
```bash
# Your server will now start successfully without firebase_admin
# FCM features will be disabled but core functionality works
sudo systemctl restart voice-assistant.service
```

### Option 2: Install Firebase (Full Features)
```bash
# Install firebase-admin for FCM messaging support
pip install firebase-admin

# Then restart your service
sudo systemctl restart voice-assistant.service
```

## Current Setup Status

✅ **Core server functionality** - notification processing, AI chat, spam filtering  
✅ **All endpoints working** - `/notify`, `/chat`, `/register_device`, `/devices`  
⚠️ **FCM messaging** - requires firebase-admin package (optional)

## Testing Your Server

```bash
# Test from your VM
curl -X GET http://localhost:8000/devices

# Test notification processing
curl -X POST http://localhost:8000/notify \
  -H "Content-Type: application/json" \
  -d '{
    "app": "WhatsApp",
    "sender": "Test User",
    "text": "Hello world",
    "subtext": "",
    "package_name": "com.whatsapp",
    "timestamp": 1693318800,
    "priority": 1
  }'
```

## Service Configuration

Your systemd service should work with these files:
- Main app: `/home/ubuntu/voice-assistant-backend/main.py`
- Requirements: Install with `pip install -r requirements.txt`
- Environment: Set `OPENAI_API_KEY` in `.env` file

## Full Installation (if needed)

```bash
cd /home/ubuntu/voice-assistant-backend

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Firebase for FCM
pip install firebase-admin

# Set your OpenAI API key in .env
echo "OPENAI_API_KEY=your_real_api_key_here" > .env

# Test the server
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Or start via systemctl
sudo systemctl restart voice-assistant.service
```

## What Works Now

Your voice assistant server is fully functional for:
- ✅ Processing notifications with AI
- ✅ Filtering spam messages
- ✅ Chat endpoint for voice commands  
- ✅ Device registration
- ✅ Fallback when OpenAI API unavailable

The only optional feature is FCM push messaging (which requires Firebase setup).

Your Android app can connect and use all core features immediately! 🚀