# 📱 VM to Phone Message Sending Guide

This guide shows you how to send messages from your VM backend to your Android phone. Messages will appear in the chat interface and be spoken aloud by the voice assistant.

## 🚀 Quick Start

The easiest way to send messages is using the `vm_send_message.sh` script:

```bash
# Send a simple message
./vm_send_message.sh send "Hello from the VM!"

# Send a notification with title
./vm_send_message.sh notify "Server Alert" "Backup completed successfully"

# Broadcast to all connected devices
./vm_send_message.sh broadcast "Server maintenance in 10 minutes"

# Chat with AI and send response to phone
./vm_send_message.sh chat "What's the weather like today?"

# Check server status and connected devices
./vm_send_message.sh status
./vm_send_message.sh devices
```

## 🔧 Setup Requirements

### 1. Firebase Configuration

For messages to reach your phone, Firebase must be properly configured:

```bash
# Check if Firebase is set up
./vm_send_message.sh setup
```

**To set up Firebase:**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Open your project → Settings → Service accounts
3. Click "Generate new private key" 
4. Save the JSON file as `firebase_admin_config.json` in the backend directory
5. Restart your server: `python3 main.py`

### 2. Phone Registration

Your Android phone must be registered with the server:

1. **Open the Voice Assistant app** on your phone
2. **Go to Settings** → Check that server URL is set to `http://185.120.71.223:8000`
3. **The app automatically registers** when it starts (check logcat for "Device registered successfully")

Verify registration:
```bash
./vm_send_message.sh devices
# Should show your device in the list
```

## 📤 Available Commands

### Basic Message Sending
```bash
# Send text message (will appear in chat and be spoken)
./vm_send_message.sh send "Your message here"

# Send to specific device (if multiple phones connected)
./vm_send_message.sh send "Hello!" --device android_123
```

### Notifications
```bash
# Send notification with custom title
./vm_send_message.sh notify "Alert Title" "Notification body text"
```

### Broadcasting
```bash
# Send same message to all connected phones
./vm_send_message.sh broadcast "System announcement"
```

### AI Integration
```bash
# Ask AI a question and send response to phone
./vm_send_message.sh chat "What's the current time?"
./vm_send_message.sh chat "Tell me a joke"
```

### System Management
```bash
# Check server status
./vm_send_message.sh status

# List all registered devices
./vm_send_message.sh devices

# Show setup instructions
./vm_send_message.sh setup
```

## 🐍 Python API Usage

You can also use the Python CLI directly:

```bash
# Basic usage
python3 cli_client.py --host 185.120.71.223 --port 8000 send "Message"

# With device targeting
python3 cli_client.py --host 185.120.71.223 --port 8000 send "Hello" --device android_123

# Send notification
python3 cli_client.py --host 185.120.71.223 --port 8000 notify "Title" "Body"

# Broadcast
python3 cli_client.py --host 185.120.71.223 --port 8000 broadcast "Message for all"

# Chat with AI
python3 cli_client.py --host 185.120.71.223 --port 8000 chat "Your question"
```

## 📱 How Messages Appear on Phone

When you send a message from the VM:

1. **📱 Notification** appears on phone screen
2. **💬 Message** is added to the chat interface  
3. **🔊 TTS** speaks the message aloud (if enabled)
4. **📊 Server tag** shows it came from server (distinct color)

Message types:
- **Server Messages**: Blue background in chat
- **AI Responses**: Assistant messages from server queries
- **Notifications**: System notifications with custom titles

## 🔍 Troubleshooting

### "No registered devices found"
- Make sure your phone app is running and connected to `http://185.120.71.223:8000`
- Check Settings → Server URL in the Android app
- Restart the app to re-register

### "Firebase not initialized"
- Download `firebase_admin_config.json` from Firebase Console
- Place it in the backend directory
- Restart the server: `python3 main.py`

### "Message sent but not received"
- Check phone's internet connection
- Verify notification permissions are enabled
- Check Firebase token is valid: `./vm_send_message.sh devices`

### Server not responding
```bash
# Test server connectivity
curl -X GET http://185.120.71.223:8000/firebase_status

# Check if server is running
./vm_send_message.sh status
```

## 🎯 Use Cases

**System Administration:**
```bash
./vm_send_message.sh notify "Backup Complete" "Daily backup finished at $(date)"
./vm_send_message.sh broadcast "Server restart in 5 minutes"
```

**Remote AI Queries:**
```bash
./vm_send_message.sh chat "Check disk space"
./vm_send_message.sh chat "What's my external IP?"
```

**Status Updates:**
```bash
./vm_send_message.sh send "Database optimization completed"
./vm_send_message.sh notify "Security Alert" "Failed login attempt detected"
```

## 🏗️ Architecture

```
VM Backend (185.120.71.223:8000)
    ↓ Firebase Cloud Messaging
Android Phone
    ↓ FirebaseMessagingService
Chat Interface + TTS
```

The system uses Firebase Cloud Messaging to deliver messages instantly to your phone, even when the app is in the background.