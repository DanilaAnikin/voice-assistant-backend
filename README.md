# 🎙️ Voice Assistant - AI-Powered Android App & Backend Server

A comprehensive voice assistant system with Android app and Python backend server, featuring AI chat, notification processing, Bluetooth integration, and Firebase Cloud Messaging.

## 📱 Complete System Overview

### Android App (Kotlin + Jetpack Compose)
- **🎙️ Voice Recognition** - Android SpeechRecognizer API for hands-free interaction
- **📲 Bluetooth Button Control** - Trigger STT with Shokz OpenRun headset buttons
- **🔊 Enhanced TTS** - Support for on-device AI TTS (Sherpa-ONNX) with fallback
- **⚡ Wake Word Detection** - Always-listening for custom phrases ("hey assistant", "jarvis")
- **🎨 Dynamic Themes** - 8 customizable color themes with Material3 design
- **📱 Smart Notifications** - Process and filter incoming notifications with AI
- **💬 Persistent Chat History** - Full conversation management with SQLite + Room
- **🔥 Firebase Integration** - Push notifications and real-time messaging

### Backend Server (Python + FastAPI)
- **🤖 AI Chat Integration** - OpenAI ChatGPT for intelligent conversations
- **📡 Notification Processing** - Smart filtering and AI-enhanced message processing
- **🔥 Firebase Cloud Messaging** - Push notifications to registered devices
- **🛡️ Smart Spam Filtering** - Configurable keyword-based and AI spam detection
- **📊 Device Management** - Multi-device support with registration and broadcasting
- **🌐 RESTful API** - FastAPI with automatic documentation and async processing

## 🎯 Key Features

### 🎙️ Voice Interaction
- **Bluetooth Integration** - Short-press for instant STT, long-press for assistant mode
- **Wake Word Detection** - Continuous listening with customizable trigger phrases
- **Multiple TTS Options** - Default Android TTS + on-device AI TTS (Sherpa-ONNX)
- **Voice Speed Control** - Adjustable TTS speed (0.5x-2.0x) with user preferences
- **Hands-free Operation** - Works with screen off/locked via foreground services

### 🔔 Smart Notifications
- **AI Processing** - Intelligent notification summarization and context enhancement
- **Spam Filtering** - Multi-level filtering with app whitelists and keyword detection
- **Custom Routing** - Send processed notifications back to phone for TTS playback
- **Priority Handling** - Urgent notifications get immediate attention
- **Server-originated Messages** - Send custom alerts and reminders from backend

### 🎨 User Experience
- **Dynamic Theming** - 8 color options applied across entire app interface
- **Auto-scroll Chat** - Always shows latest messages in conversations
- **Settings Management** - Comprehensive preferences with visual feedback
- **History Management** - Complete conversation history with statistics
- **Professional UI** - Material3 design with smooth animations and transitions

## 🚀 Quick Start Guide

### 📋 Prerequisites

#### For Backend Server
- **Python 3.8+** with pip
- **OpenAI API Key** (get from [OpenAI Platform](https://platform.openai.com/api-keys))
- **Internet connection** for API calls
- **(Optional)** Firebase project for push notifications

#### For Android App  
- **Android Studio Arctic Fox** or newer
- **Android device/emulator** with API 24+ (Android 7.0+)
- **Bluetooth headset** (optional, for hands-free features)

### 🖥️ Backend Server Setup

#### 1. Clone and Setup Repository
```bash
# Clone the repository
git clone https://github.com/DanilaAnikin/voice-assistant-backend.git
cd Voice-Based-AI-Assistant-with-ChatGPT-on-Raspberry-Pi

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
# Create environment file
cp .env.example .env  # or create manually if not exists
nano .env
```

**Required .env configuration:**
```bash
# Essential
OPENAI_API_KEY=sk-proj-your-openai-api-key-here

# Optional but recommended
FIREBASE_SERVICE_ACCOUNT_PATH=firebase_admin_config.json
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

#### 3. Start the Server
```bash
# Development mode (with auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

#### 4. Verify Server is Running
```bash
# Check server health
curl http://localhost:8000/docs  # Interactive API documentation
curl http://localhost:8000/firebase_status  # Firebase integration status

# Test basic chat endpoint
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"text":"Hello, how are you?","spoken":false}'
```

### 📱 Android App Setup

#### 1. Open Project in Android Studio
```bash
# Navigate to Android project directory
cd /path/to/voice-assistant-android-kotlin
# Open in Android Studio or use command line:
studio .
```

#### 2. Configure Server URL
Edit `app/build.gradle.kts`:
```kotlin
android {
    defaultConfig {
        // Update with your server's IP address
        buildConfigField("String", "DEFAULT_BASE_URL", "\"http://YOUR_SERVER_IP:8000/\"")
    }
}
```

#### 3. Enable Firebase (Optional)
If you want push notifications:
1. Place `google-services.json` in `app/` directory
2. Uncomment Firebase dependencies in `app/build.gradle.kts`
3. Uncomment Google Services plugin

#### 4. Build and Install
```bash
# Via Android Studio: Build → Make Project → Run
# Or via command line:
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 🧪 Quick Testing

#### 1. Test Backend Server
```bash
# Send test message
./send_cli.sh send "Hello from server!"

# Check system status  
./send_cli.sh status

# Test AI chat
python cli_client.py chat "Tell me a joke"
```

#### 2. Test Android App
1. **Launch app** on device/emulator
2. **Test chat** - Type message and verify AI response
3. **Test voice** - Press microphone button and speak
4. **Test Bluetooth** (if available) - Press headset button
5. **Test notifications** - Send message from server CLI

### 🐳 Docker Setup (Alternative)

#### Quick Docker Run
```bash
# Build image
docker build -t voice-assistant-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-openai-key \
  -v $(pwd)/firebase_admin_config.json:/app/firebase_admin_config.json \
  --name voice-assistant \
  voice-assistant-backend

# Check logs
docker logs voice-assistant

# Test running container
curl http://localhost:8000/docs
```

#### Docker Compose (Recommended)
Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  voice-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./firebase_admin_config.json:/app/firebase_admin_config.json
      - ./voice_assistant.db:/app/voice_assistant.db
    restart: unless-stopped
```

Run with:
```bash
# Set environment variable
export OPENAI_API_KEY=your-key-here

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## 📡 API Endpoints

### Chat Endpoint
**POST** `/chat`
```json
{
  "text": "Hello, how are you?",
  "spoken": false
}
```

**Response:**
```json
{
  "User": "Hello, how are you?",
  "AI": "I'm doing well, thank you! How can I help you today?"
}
```

## 💻 Command Line Interface

The server includes a powerful CLI for sending messages and notifications from the command line.

### Python CLI (`cli_client.py`)
```bash
# Send message to default device
python cli_client.py send "Hello from server!"

# Send to specific device  
python cli_client.py send "Hello!" --device android_123

# Send notification with title
python cli_client.py notify "Alert" "Something important happened"

# Broadcast to all devices
python cli_client.py broadcast "Server maintenance in 10 minutes"

# Chat with AI and send response to devices
python cli_client.py chat "What's the weather like?"

# List registered devices
python cli_client.py devices

# Check server status
python cli_client.py status

# Use different server host/port
python cli_client.py --host 192.168.1.100 --port 8080 status
```

### Bash Wrapper (`send_cli.sh`) - Simplified Syntax
```bash
# Quick message sending
./send_cli.sh send "Hello from command line!"
./send_cli.sh notify "Alert" "Server maintenance starting"  
./send_cli.sh broadcast "System will reboot in 5 minutes"
./send_cli.sh chat "What's the current time?"
./send_cli.sh devices
./send_cli.sh status
```

### Environment Variables for CLI
```bash
export VOICE_SERVER_HOST=192.168.1.100  # Default: localhost
export VOICE_SERVER_PORT=8080            # Default: 8000
./send_cli.sh status
```

### CLI Examples
```bash
# Send reminder to specific device
python cli_client.py send "Meeting in 10 minutes" --device phone_001

# Send system alert to all devices
./send_cli.sh broadcast "Server backup starting - services may be slow"

# Get AI response and push to devices
python cli_client.py chat "Tell me a joke" --device android_123

# Check if Firebase and devices are working
./send_cli.sh status
```

> 📖 **For detailed CLI documentation, see [CLI_GUIDE.md](CLI_GUIDE.md)**

### Notification Processing
**POST** `/notify`
```json
{
  "app": "WhatsApp",
  "sender": "John Doe", 
  "text": "Hey, are we still meeting at 3?",
  "subtext": "",
  "package_name": "com.whatsapp",
  "timestamp": 1640995200,
  "priority": 0
}
```

**Response:**
```json
{
  "result": "success",
  "output": "Message from John Doe on WhatsApp: Hey, are we still meeting at 3?"
}
```

### Device Management
**POST** `/register_device`
```json
{
  "device_id": "phone_001",
  "fcm_token": "firebase-cloud-messaging-token"
}
```

**POST** `/send_message`
```json
{
  "device_id": "phone_001",
  "message": "Your reminder: Meeting in 10 minutes",
  "type": "reminder"
}
```

**GET** `/devices` - List all registered devices

### Additional Endpoints
- **POST** `/send_notification` - Send custom notifications
- **GET** `/docs` - Interactive API documentation
- **GET** `/redoc` - ReDoc API documentation

## 🏗️ System Architecture

### 📱 Android App Structure
```
app/src/main/java/com/danila/voiceassistant/
├── 🎨 ui/
│   ├── screens/          # Chat, History, Settings screens
│   ├── components/       # Reusable UI components
│   └── theme/           # Dynamic theming system
├── 🎙️ audio/
│   ├── TtsManager.kt    # Standard Android TTS
│   ├── SmartTtsManager.kt # AI TTS with Sherpa-ONNX
│   └── SpeechRecognition.kt # Voice input handling
├── 🔧 service/
│   ├── MediaButtonService.kt # Bluetooth button handling
│   ├── WakeWordService.kt   # Always-listening detection
│   ├── BackgroundTtsService.kt # TTS playback service
│   └── FirebaseMessagingService.kt # FCM integration
├── 🌐 network/
│   ├── ChatService.kt   # API communication
│   ├── RetrofitClient.kt # HTTP client setup
│   └── models/         # Data classes
├── 📊 database/
│   ├── entities/       # Room database entities
│   ├── dao/           # Data access objects
│   └── AppDatabase.kt # Database configuration
├── ⚙️ settings/
│   ├── AppSettings.kt  # SharedPreferences wrapper
│   └── UserPreferences.kt # Settings data management
└── 📱 MainActivity.kt  # Main entry point
```

### 🖥️ Backend Server Structure
```
📁 Voice-Based-AI-Assistant-with-ChatGPT-on-Raspberry-Pi/
├── 🚀 main.py                    # FastAPI application and routing
├── 📂 src/
│   ├── 🤖 ai.py                 # OpenAI ChatGPT integration
│   ├── 🎙️ speech_to_text.py     # Speech recognition (gTTS)
│   ├── 🔊 text_to_speech.py     # TTS generation
│   ├── 💾 memory.py             # SQLite database operations
│   ├── 🔥 fcm_service.py        # Firebase Cloud Messaging
│   └── 📡 livekit_handler.py    # Real-time audio (optional)
├── 🔧 tools/
│   ├── cli_client.py           # Python CLI for server interaction
│   ├── send_cli.sh             # Bash wrapper for CLI commands
│   └── test_*.py               # Testing utilities
├── 📊 models/                   # Wake word detection models
├── 📋 requirements.txt          # Python dependencies
├── ⚙️ .env                     # Environment configuration
└── 🔥 firebase_admin_config.json # Firebase service account
```

### 🔄 Processing Flow

#### Voice Command Flow
```
🎧 Bluetooth Headset
    │ (short press)
    ▼
📱 MediaButtonReceiver → MediaButtonService
    │ (start Bluetooth SCO)
    ▼
🎙️ SpeechRecognizer (headset mic)
    │ (recognized text)
    ▼
🌐 POST /chat → 🤖 OpenAI API
    │ (AI response)
    ▼
🔊 BackgroundTtsService → 🎧 Headset Audio
```

#### Notification Processing Flow
```
📱 Android NotificationListenerService
    │ (captured notification)
    ▼
🌐 POST /notify → 🛡️ Spam Filter
    │ (if not spam)
    ▼
🤖 AI Processing (optional)
    │ (enhanced message)
    ▼
🔥 Firebase Cloud Messaging
    │ (push notification)
    ▼
📱 FirebaseMessagingService → 🔊 TTS Playback
```

#### Chat Conversation Flow
```
📱 ChatScreen (user input)
    │ (text message)
    ▼
🌐 POST /chat → 🤖 OpenAI ChatGPT
    │ (AI response)
    ▼
💾 SQLite Database (conversation history)
    │ 
    ▼
🔥 FCM Push (optional) → 📱 Android App
    │ (display response)
    ▼
🔊 TTS Manager → 📢 Audio Output
```

### 🔧 Technology Stack

#### 📱 Android App
- **Language**: Kotlin 100%
- **UI Framework**: Jetpack Compose + Material3
- **Architecture**: MVVM + Repository Pattern
- **Database**: Room (SQLite wrapper)
- **Networking**: Retrofit + Moshi
- **Dependency Injection**: Manual DI (lightweight)
- **Testing**: JUnit4, MockK, Compose Testing
- **Min SDK**: Android 7.0 (API 24)
- **Target SDK**: Android 14 (API 34)

#### 🖥️ Backend Server
- **Language**: Python 3.8+
- **Web Framework**: FastAPI (async)
- **AI Integration**: OpenAI GPT-3.5/4
- **Database**: SQLite with async support
- **Push Notifications**: Firebase Admin SDK
- **Speech Processing**: gTTS (Google Text-to-Speech)
- **Testing**: pytest, unittest
- **Deployment**: Docker, systemd, nginx

## 🔧 Configuration

### Processing Modes
Edit `main.py` to configure processing:

```python
# Configuration flags
AI_ENABLED = False      # Enable AI processing of notifications
FILTER_ENABLED = True   # Enable spam filtering

# Allowed/blocked apps
ALLOWED_APPS = {"WhatsApp", "Messages", "Gmail", "Telegram"}
BLOCKED_APPS = {"Facebook", "Instagram", "TikTok"}

# Spam keywords
SPAM_KEYWORDS = ["free", "prize", "winner", "urgent", "click here"]
```

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-proj-your-openai-key

# Optional Firebase
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/firebase-key.json
FIREBASE_PROJECT_ID=your-firebase-project

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🛡️ Notification Filtering

### Smart Filtering System
1. **App-based Filtering** - Allow/block specific apps
2. **Spam Detection** - Keyword-based spam identification
3. **AI Enhancement** - Intelligent notification processing
4. **Priority Handling** - Process urgent notifications first

### Customization
```python
def is_spam(text: str) -> bool:
    """Customize spam detection logic"""
    text_lower = text.lower()
    spam_indicators = sum(1 for keyword in SPAM_KEYWORDS if keyword in text_lower)
    return spam_indicators >= 2  # Adjust threshold as needed
```

## 🤖 AI Integration

### OpenAI Models
- **GPT-4** - Primary chat model for conversations
- **GPT-3.5-turbo** - Notification processing (faster, cost-effective)

### Prompt Engineering
The server uses carefully crafted prompts for notification processing:
```python
prompt = f"""You are a voice assistant. Process this notification to be read aloud naturally.

App: {app_name}
Sender: {sender}
Message: {notification_text}

Instructions:
1. Make it concise and voice-friendly
2. Add context if needed
3. Remove unnecessary details
4. If urgent/important, mention that
5. Keep it under 2 sentences"""
```

## 🔥 Firebase Setup & Integration

Firebase provides push notification capabilities for seamless communication between server and Android devices.

### 1. Create Firebase Project

1. **Visit Firebase Console**
   ```
   https://console.firebase.google.com/
   ```

2. **Create New Project**
   - Click "Add project"
   - Enter project name: `voice-assistant-app`
   - Enable Google Analytics (optional)
   - Choose analytics account or create new

3. **Add Android App**
   - Click "Add app" → Android
   - Package name: `com.danila.voiceassistant`
   - App nickname: `Voice Assistant`
   - SHA-1 certificate fingerprint (optional for development)

### 2. Download Configuration Files

#### For Android App: `google-services.json`
Download and place in `app/` directory. Example structure:

```json
{
  "project_info": {
    "project_number": "123456789012",
    "project_id": "voice-assistant-app-12345",
    "storage_bucket": "voice-assistant-app-12345.appspot.com"
  },
  "client": [
    {
      "client_info": {
        "mobilesdk_app_id": "1:123456789012:android:abcdef1234567890abcdef",
        "android_client_info": {
          "package_name": "com.danila.voiceassistant"
        }
      },
      "oauth_client": [
        {
          "client_id": "123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com",
          "client_type": 3
        }
      ],
      "api_key": [
        {
          "current_key": "key_here"
        }
      ],
      "services": {
        "appinvite_service": {
          "other_platform_oauth_client": [
            {
              "client_id": "123456789012-zyxwvutsrqponmlkjihgfedcba987654.apps.googleusercontent.com",
              "client_type": 3
            }
          ]
        }
      }
    }
  ],
  "configuration_version": "1"
}
```

> **⚠️ Security Note**: This file contains sensitive information. Never commit it to version control.
> Add `google-services.json` to your `.gitignore` file.

#### For Backend Server: Service Account Key
1. **Generate Service Account**
   - Project Settings → Service Accounts
   - Click "Generate new private key"
   - Download JSON file (e.g., `firebase_admin_config.json`)

2. **Example Service Account Structure**
```json
{
  "type": "service_account",
  "project_id": "YOUR_PROJECT_ID",
  "private_key_id": "YOUR_PRIVATE_KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "YOUR_CLIENT_EMAIL",
  "client_id": "YOUR_CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/YOUR_CLIENT_EMAIL",
  "universe_domain": "googleapis.com"
}
```

### 3. Configure Backend Server

#### Install Firebase Admin SDK
```bash
pip install firebase-admin
```

#### Set Environment Variables
```bash
# Method 1: Environment variable
export FIREBASE_SERVICE_ACCOUNT_PATH="/path/to/firebase_admin_config.json"

# Method 2: Direct file placement
# Place firebase_admin_config.json in project root directory
cp /path/to/downloaded-service-account.json firebase_admin_config.json
```

#### Verify Firebase Setup
```bash
# Check Firebase status
curl http://localhost:8000/firebase_status

# Expected response:
{
  "firebase_initialized": true,
  "registered_devices_count": 0,
  "can_send_notifications": true,
  "ai_enabled": false,
  "filter_enabled": true
}
```

### 4. Android App Configuration

#### Add Firebase Dependencies (app/build.gradle.kts)
```kotlin
// Firebase Cloud Messaging (uncomment when ready)
implementation(platform("com.google.firebase:firebase-bom:32.8.1"))
implementation("com.google.firebase:firebase-messaging-ktx")
implementation("com.google.firebase:firebase-analytics-ktx")
```

#### Enable Google Services Plugin
```kotlin
// Uncomment in app/build.gradle.kts
id("com.google.gms.google-services")
```

#### Register Device with Server
The Android app automatically registers its FCM token with the backend server:
```kotlin
// Device registration happens in MainActivity
val request = DeviceRegistrationRequest(
    device_id = "android_${Build.MODEL}_${System.currentTimeMillis()}",
    fcm_token = fcmToken,
    device_type = "android",
    app_version = "1.0"
)
```

### 5. Testing Firebase Integration

#### Test Message Sending
```bash
# Send test message to all devices
./send_cli.sh broadcast "Firebase test message"

# Send to specific device
python cli_client.py send "Hello from server!" --device android_123

# Check registered devices
./send_cli.sh devices
```

#### Verify on Android
1. Install and run the Android app
2. Check logcat for FCM token registration
3. Send test message from server
4. Verify notification appears and triggers TTS

### 6. Troubleshooting Firebase

#### Common Issues
```bash
# Check Firebase initialization
curl http://localhost:8000/firebase_status

# Verify service account file exists
ls -la firebase_admin_config.json

# Check server logs for Firebase errors
tail -f server.log | grep -i firebase

# Test FCM token format (should be ~152 characters)
echo $FCM_TOKEN | wc -c
```

#### Service Account Permissions
Ensure the service account has these roles in Firebase Console:
- **Firebase Admin** - Full access to Firebase features
- **Cloud Messaging Admin** - Send push notifications
- **Service Account Token Creator** - Generate access tokens

### 7. Production Considerations

#### Security Best Practices
```bash
# Secure service account file permissions
chmod 600 firebase_admin_config.json

# Use environment variables in production
export FIREBASE_SERVICE_ACCOUNT_PATH="/secure/path/firebase_admin_config.json"

# Never commit these files to version control
echo "firebase_admin_config.json" >> .gitignore
echo "google-services.json" >> .gitignore
```

#### Monitoring & Logging
```python
# Add to main.py for production monitoring
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log Firebase operations
logger.info(f"📤 FCM message sent to {device_id}: {message}")
```

## 💾 Database Schema

SQLite database (`voice_assistant.db`):
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_input TEXT,
    ai_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,
    fcm_token TEXT,
    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Troubleshooting

### Common Issues

#### OpenAI API Errors
```bash
# Check API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# Verify billing and quota
# Check OpenAI dashboard for usage limits
```

#### Server Not Accessible
```bash
# Check if server is running
netstat -tlnp | grep :8000

# Test local connection
curl http://localhost:8000/docs

# Check firewall settings for external access
sudo ufw allow 8000
```

#### Notification Processing Issues
1. Check `AI_ENABLED` and `FILTER_ENABLED` settings
2. Review allowed/blocked app lists
3. Test with simple notification first
4. Check OpenAI API quota and billing

#### Firebase Connection Problems
1. Verify service account JSON path
2. Check Firebase project permissions
3. Ensure Android app has correct `google-services.json`
4. Test FCM token registration

### Debugging
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Run with verbose output:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

## 🚀 Deployment

### Production Deployment
```bash
# Install production ASGI server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Systemd Service
Create `/etc/systemd/system/voice-assistant.service`:
```ini
[Unit]
Description=Voice Assistant Backend
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/project
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Reverse Proxy (Nginx)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Environment Setup
For production, use environment variables instead of `.env` file:
```bash
export OPENAI_API_KEY=your-key
export FIREBASE_SERVICE_ACCOUNT_KEY=/path/to/key.json
export HOST=0.0.0.0
export PORT=8000
```

## 📊 Performance & Monitoring

### Performance Tips
- Use async/await for I/O operations
- Implement request rate limiting
- Cache frequent AI responses
- Use connection pooling for database
- Monitor OpenAI API usage and costs

### Health Checks
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

## 🔒 Security

### Best Practices
- Use environment variables for secrets
- Implement API key authentication
- Add rate limiting to prevent abuse
- Use HTTPS in production
- Validate all input data
- Sanitize notification content

### API Security
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/protected-endpoint")
async def protected(token: str = Security(security)):
    if not validate_token(token):
        raise HTTPException(status_code=401)
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Open Pull Request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review server logs for errors
3. Test API endpoints with curl or Postman
4. Create an issue in the repository

## 🙏 Acknowledgments

- **OpenAI** - ChatGPT API for AI conversations
- **FastAPI** - Modern, fast web framework
- **Firebase** - Cloud messaging service
- **Google** - Text-to-speech and speech recognition
- **Python Community** - Amazing libraries and tools