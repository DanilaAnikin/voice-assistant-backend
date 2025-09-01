# 🛠️ Development Setup Guide

Quick setup guide for developers new to this Voice Assistant project.

## 📋 What You Need to Create/Update

### 🔑 Essential Files to Create

#### 1. **`.env` file** (Backend Server)
```bash
# Copy template and update with your keys
cp .env.example .env
```
**Required content:**
```bash
OPENAI_API_KEY=sk-proj-YOUR-OPENAI-KEY-HERE
FIREBASE_SERVICE_ACCOUNT_PATH=firebase_admin_config.json
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 2. **`firebase_admin_config.json`** (Backend Server)
- Download from [Firebase Console](https://console.firebase.google.com/)
- Project Settings → Service Accounts → Generate new private key
- Place in project root directory

#### 3. **`google-services.json`** (Android App)
- Download from Firebase Console → Project Settings → Your apps
- Place in `app/` directory of Android project
- **⚠️ Never commit this file to git!**

### ⚙️ Files to Update

#### 1. **`app/build.gradle.kts`** (Android)
Update server URL with your development machine's IP:
```kotlin
buildConfigField("String", "DEFAULT_BASE_URL", "\"http://192.168.1.XXX:8000/\"")
```

#### 2. **`.gitignore`** (Add if missing)
```bash
# Sensitive files - never commit
.env
firebase_admin_config.json
google-services.json

# Database
voice_assistant.db
*.db

# Python
venv/
__pycache__/
*.pyc
```

## 🚀 Quick Development Setup

### Backend Server (Python)
```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Create .env file (see above)
# 3. Add firebase_admin_config.json (see above)

# 4. Start development server
uvicorn main:app --reload --host 0.0.0.0

# 5. Test it works
curl http://localhost:8000/docs
```

### Android App (Kotlin)
```bash
# 1. Open in Android Studio
# 2. Add google-services.json to app/ directory
# 3. Update DEFAULT_BASE_URL in app/build.gradle.kts
# 4. Uncomment Firebase dependencies if needed

# 5. Build and run
./gradlew assembleDebug
# Or use Android Studio Run button
```

## 🧪 Testing Your Setup

### Test Backend
```bash
# Test AI chat
python cli_client.py chat "Hello, are you working?"

# Check Firebase status
curl http://localhost:8000/firebase_status

# Send test notification (if Android app is running)
./send_cli.sh send "Test message from server"
```

### Test Android App
1. **Launch app** - Should connect to your server
2. **Type message** - Should get AI response
3. **Press mic button** - Should do speech-to-text
4. **Check logs** - Should see FCM token registration

## 🔧 Development Workflow

### Making Changes
```bash
# Backend changes - server auto-reloads with --reload flag
# Android changes - rebuild and reinstall:
./gradlew assembleDebug && adb install app/build/outputs/apk/debug/app-debug.apk
```

### Debugging
```bash
# Backend logs
tail -f logs/server.log  # if configured, or check terminal

# Android logs  
adb logcat -s VoiceAssistant  # filter by app tag
```

## 🚨 Common Issues & Solutions

### ❌ "OpenAI API key not found"
**Solution:** Check `.env` file has correct `OPENAI_API_KEY=sk-proj-...`

### ❌ "Firebase not initialized"
**Solution:** 
1. Verify `firebase_admin_config.json` exists in project root
2. Check file permissions: `chmod 600 firebase_admin_config.json`

### ❌ "Connection refused" (Android → Server)
**Solution:**
1. Update `DEFAULT_BASE_URL` in `app/build.gradle.kts` with your computer's IP
2. Check firewall allows port 8000: `sudo ufw allow 8000`
3. Start server with `--host 0.0.0.0` not just `localhost`

### ❌ "google-services.json not found"
**Solution:**
1. Download from Firebase Console
2. Place in `app/` directory (not `app/src/`)
3. Uncomment Firebase dependencies in `build.gradle.kts`

### ❌ Android app crashes on startup
**Solution:**
1. Check Android logs: `adb logcat`
2. Verify `google-services.json` is in correct location
3. Make sure server URL is reachable from device/emulator

## 📁 Project Structure Overview

```
📁 Backend (Python FastAPI)
├── main.py              # Server entry point
├── .env                 # ← CREATE: API keys
├── firebase_admin_config.json  # ← CREATE: Firebase service account
├── src/fcm_service.py   # Firebase messaging
└── cli_client.py        # Testing CLI

📁 Android App (Kotlin)
├── app/build.gradle.kts # ← UPDATE: Server URL
├── app/google-services.json  # ← CREATE: Firebase config
├── app/src/main/java/com/danila/voiceassistant/
│   ├── MainActivity.kt   # App entry point
│   ├── service/         # Background services
│   ├── network/         # API communication
│   └── audio/           # Voice processing
```

## 🎯 What Each Component Does

- **Backend Server**: Handles AI chat, notification processing, Firebase messaging
- **Android App**: Voice UI, Bluetooth integration, notification capture
- **Firebase**: Push notifications between server and Android
- **OpenAI**: Powers the AI chat responses

## 📞 Getting Help

1. **Check server logs** for backend issues
2. **Check `adb logcat`** for Android issues  
3. **Test API endpoints** with curl or browser at `http://localhost:8000/docs`
4. **Verify network connectivity** between Android device and development machine

---

**🎉 Once setup is complete, you should be able to:**
- Send messages from Android app and get AI responses
- Use voice commands via microphone or Bluetooth headset
- Receive server-sent messages as push notifications
- See real-time communication between all components

Happy coding! 🚀