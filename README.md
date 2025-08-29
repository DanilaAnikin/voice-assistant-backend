# Voice Assistant Backend Server

A FastAPI-based backend server that powers the Android Voice Assistant app, providing AI chat capabilities, notification processing, and Firebase Cloud Messaging integration.

## 🎯 Features

### Core Functionality
- **🤖 AI Chat Integration** - OpenAI ChatGPT integration for intelligent conversations
- **📱 Notification Processing** - Smart filtering and processing of Android notifications
- **🔊 Text-to-Speech** - Google Text-to-Speech (gTTS) integration
- **🎙️ Speech Recognition** - Voice input processing capabilities
- **🔥 Firebase Cloud Messaging** - Push notifications to Android devices
- **💾 Conversation Memory** - SQLite database for conversation history

### Advanced Features
- **🛡️ Smart Spam Filtering** - Keyword-based and AI-powered spam detection
- **⚡ Fast API** - High-performance async API with automatic documentation
- **🔧 Configurable Processing** - Enable/disable AI processing and filtering
- **📊 Device Management** - Track and manage registered Android devices
- **🌐 CORS Enabled** - Cross-origin resource sharing for web clients

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Internet connection
- (Optional) Firebase project for FCM

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/DanilaAnikin/voice-assistant-backend.git
   cd Voice-Based-AI-Assistant-with-ChatGPT-on-Raspberry-Pi
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Add your OpenAI API key:
   ```bash
   OPENAI_API_KEY=sk-proj-your-api-key-here
   ```

5. **Run Server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Setup (Alternative)
```bash
docker build -t voice-assistant-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key voice-assistant-backend
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

## 🏗️ Architecture

### Core Components
```
main.py                    # FastAPI application and routing
├── src/
│   ├── ai.py             # OpenAI integration
│   ├── speech_to_text.py # Speech recognition
│   ├── text_to_speech.py # TTS generation
│   ├── memory.py         # Database operations
│   ├── fcm_service.py    # Firebase Cloud Messaging
│   └── livekit_handler.py # Real-time audio (optional)
├── models/               # Wake word detection models
├── requirements.txt      # Python dependencies
└── .env                 # Environment configuration
```

### Processing Flow
```
Android App → POST /notify → Spam Filter → AI Processing → Response → TTS
Android App → POST /chat → OpenAI API → Memory Storage → Response
Server → FCM → Push Notification → Android App → TTS
```

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

## 🔥 Firebase Integration

### Setup FCM (Optional)
1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create new project or use existing one

2. **Generate Service Account**
   - Project Settings → Service Accounts
   - Generate new private key (JSON)

3. **Configure Server**
   ```bash
   pip install firebase-admin
   export FIREBASE_SERVICE_ACCOUNT_KEY=/path/to/firebase-key.json
   ```

4. **Android App Setup**
   - Add `google-services.json` to Android project
   - Register FCM token with server

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