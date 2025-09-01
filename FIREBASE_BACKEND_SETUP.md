# 🔥 Firebase Backend Setup - Complete Guide

Your Firebase integration is ready! Here's how to set it up on your backend server.

## 📁 Files Created

1. **`firebase_admin_config.json`** - Your Firebase service account credentials
2. **`firebase_push_notifications.py`** - Firebase Admin SDK manager
3. **`firebase_integration_complete.py`** - Complete FastAPI integration
4. **`FIREBASE_BACKEND_SETUP.md`** - This setup guide

## 🚀 Installation Steps

### Step 1: Install Firebase Admin SDK

```bash
pip install firebase-admin
```

### Step 2: Secure Your Credentials

Make sure your `firebase_admin_config.json` file has proper permissions:

```bash
chmod 600 firebase_admin_config.json
```

Add it to your `.gitignore`:
```bash
echo "firebase_admin_config.json" >> .gitignore
```

### Step 3: Integration Options

**Option A: Update Your Existing Server**
- Copy the endpoints from `firebase_integration_complete.py` into your existing `main.py`
- Import the Firebase functions at the top
- Add the device registration storage

**Option B: Use the Complete New Server**
- Replace your existing server with `firebase_integration_complete.py`
- Rename it to `main.py` or your preferred filename
- Add your existing AI logic to the chat endpoint

## 🎯 New API Endpoints

Your server will now have these new endpoints:

### **Device Management**
- `POST /register_device` - Register Android devices for push notifications
- `GET /registered_devices` - List all registered devices
- `GET /firebase_status` - Check Firebase initialization status

### **Push Notifications**
- `POST /send_message_to_device` - Send message to specific device
- `POST /broadcast_message` - Send message to all devices

### **Enhanced Existing Endpoints**
- `POST /chat` - Now sends AI responses as push notifications
- `POST /notify` - Now sends notification alerts as push notifications

## 🧪 Testing Your Setup

### 1. Start Your Server
```bash
python firebase_integration_complete.py
```

You should see:
```
🔥 Voice Assistant Server with Firebase Push Notifications
📱 Ready to receive device registrations and send notifications!
✅ Firebase Admin SDK initialized successfully
```

### 2. Check Firebase Status
```bash
curl http://your-server:8000/firebase_status
```

Expected response:
```json
{
  "firebase_initialized": true,
  "registered_devices_count": 0,
  "can_send_notifications": false
}
```

### 3. Install Android APK
Install the updated APK on your Android device. The app will automatically:
1. Generate FCM token
2. Register with your server
3. Send welcome push notification

### 4. Test Push Notifications

#### Using curl
```bash
# Send message to specific device
curl -X POST "http://your-server:8000/send_message_to_device?device_id=DEVICE_ID&message=Hello from server!"

# Broadcast to all devices
curl -X POST "http://your-server:8000/broadcast_message?message=Hello everyone!"
```

#### Using Command Line Interface (Recommended)

The server includes convenient CLI tools for testing:

**Python CLI:**
```bash
# Check server and Firebase status
python cli_client.py status

# List registered devices
python cli_client.py devices

# Send message to default device
python cli_client.py send "Hello from command line!"

# Send notification with title
python cli_client.py notify "Test Alert" "Firebase messaging is working!"

# Broadcast to all devices
python cli_client.py broadcast "Server testing in progress"

# Chat with AI and send response to devices
python cli_client.py chat "Tell me a joke"
```

**Bash Wrapper (Simpler):**
```bash
# Quick status check
./send_cli.sh status

# Send message
./send_cli.sh send "Hello from bash!"

# Send notification
./send_cli.sh notify "Alert" "Testing Firebase notifications"

# Broadcast message
./send_cli.sh broadcast "Testing broadcast functionality"
```

**Using Different Server:**
```bash
# Test remote server
python cli_client.py --host 192.168.1.100 --port 8000 status

# Or with environment variables
export VOICE_SERVER_HOST=192.168.1.100
export VOICE_SERVER_PORT=8000
./send_cli.sh status
```

## 🔧 Integration with Your Existing AI

Update your existing chat logic in the `/chat` endpoint:

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # Your existing AI logic here
    user_message = request.text
    
    # Replace this with your actual AI processing
    ai_response = your_existing_ai_function(user_message)
    
    # Push notification logic (already included)
    pushed_devices = []
    if push_manager.initialized and registered_devices:
        results = send_push_to_all_devices(ai_response, registered_devices)
        pushed_devices = [device_id for device_id, success in results.items() if success]
    
    return ChatResponse(
        User=user_message,
        AI=ai_response,
        pushed_to_devices=pushed_devices
    )
```

## 📱 Android App Workflow

1. **App Startup**: Device registers with FCM token
2. **User Sends Message**: Via chat interface or voice
3. **Server Processing**: Your AI processes the message
4. **Push Notification**: Server sends response as push notification
5. **TTS Playback**: Android app speaks the response through headphones/speaker

## 🔒 Security Notes

- ✅ Service account key is secure (better than legacy server key)
- ✅ Private key is properly formatted
- ✅ Credentials should never be committed to version control
- ✅ Use environment variables in production

## 🐛 Troubleshooting

### "Firebase not initialized"
- Check that `firebase_admin_config.json` exists
- Verify JSON format is correct
- Check file permissions

### "No registered devices"
- Make sure Android app is installed and opened
- Check `/registered_devices` endpoint
- Verify device has internet connection

### "Push notification failed"
- Check FCM token is valid
- Verify Firebase project settings
- Check server logs for detailed errors

## 🎉 Ready to Go!

Your Firebase integration is complete! The system now supports:

✅ **Automatic device registration**  
✅ **Push notifications with TTS**  
✅ **Remote AI responses**  
✅ **Multi-device support**  
✅ **Background processing**  

Install the Android APK and start your server - you'll have a complete voice assistant with remote push notification capabilities! 🚀