# 💻 Command Line Interface Guide

The Voice Assistant Server includes powerful CLI tools for sending messages, notifications, and managing devices from the command line.

## 🚀 Quick Start

### Installation
The CLI tools are included with the server. No additional installation required.

### Make Scripts Executable
```bash
chmod +x cli_client.py
chmod +x send_cli.sh
```

## 🐍 Python CLI (`cli_client.py`)

### Basic Usage
```bash
python cli_client.py [OPTIONS] COMMAND [ARGS]
```

### Available Commands

#### Send Message
```bash
# Send to default device
python cli_client.py send "Hello from server!"

# Send to specific device
python cli_client.py send "Meeting reminder" --device android_123
```

#### Send Notification
```bash
# Send notification with title and body
python cli_client.py notify "Alert" "Something important happened"

# Send to specific device
python cli_client.py notify "Reminder" "Meeting in 10 minutes" --device phone_001
```

#### Broadcast Message
```bash
# Send to all registered devices
python cli_client.py broadcast "Server maintenance in 10 minutes"
```

#### Chat with AI
```bash
# Get AI response and send to devices
python cli_client.py chat "What's the weather like?"

# Send AI response to specific device
python cli_client.py chat "Tell me a joke" --device android_123

# Enable spoken response (if TTS is configured)
python cli_client.py chat "What time is it?" --spoken
```

#### Device Management
```bash
# List all registered devices
python cli_client.py devices

# Check server and Firebase status
python cli_client.py status
```

### Server Configuration
```bash
# Use different host/port
python cli_client.py --host 192.168.1.100 --port 8080 status

# Default is localhost:8000
python cli_client.py status
```

### Response Examples

**Success Response:**
```json
✅ Success!
{
  "result": "success",
  "message": "Message sent successfully",
  "device_id": "android_123"
}
```

**Error Response:**
```
❌ Error: No registered device found for android_456
```

## 🐚 Bash Wrapper (`send_cli.sh`)

Simplified syntax for common operations.

### Basic Usage
```bash
./send_cli.sh COMMAND [ARGS]
```

### Available Commands

#### Send Messages
```bash
./send_cli.sh send "Hello from bash!"
./send_cli.sh notify "Alert" "Server maintenance starting"
./send_cli.sh broadcast "System will reboot in 5 minutes"
```

#### AI and Status
```bash
./send_cli.sh chat "What's the current time?"
./send_cli.sh devices
./send_cli.sh status
```

### Environment Variables
```bash
# Configure server connection
export VOICE_SERVER_HOST=192.168.1.100
export VOICE_SERVER_PORT=8080

# Now all commands use the configured server
./send_cli.sh status
```

### Help
```bash
./send_cli.sh help
# Shows usage examples and available commands
```

## 📋 Practical Examples

### System Administration
```bash
# Server maintenance notification
./send_cli.sh broadcast "Server backup starting - services may be slow for 5 minutes"

# Check system health
python cli_client.py status

# Send individual reminders
python cli_client.py send "Database backup completed successfully" --device admin_phone
```

### AI Interactions
```bash
# Get weather and send to all devices
python cli_client.py chat "What's today's weather forecast?"

# Ask for news and send to specific device
python cli_client.py chat "Give me today's top 3 news headlines" --device morning_device

# Fun interactions
./send_cli.sh chat "Tell me a programming joke"
```

### Device Testing
```bash
# Test Firebase connectivity
python cli_client.py notify "Test" "Firebase messaging is working!"

# Check registered devices
python cli_client.py devices

# Send test message to each device
for device in android_123 phone_001 tablet_456; do
  python cli_client.py send "Testing device $device" --device $device
done
```

### Remote Server Management
```bash
# Monitor remote server
VOICE_SERVER_HOST=my-server.com python cli_client.py status

# Send alerts from monitoring scripts
if [[ $(disk_usage) -gt 90 ]]; then
  ./send_cli.sh broadcast "WARNING: Disk usage above 90%"
fi

# Scheduled maintenance notifications
./send_cli.sh notify "Maintenance" "Scheduled reboot in 10 minutes"
sleep 600
./send_cli.sh broadcast "Server rebooting now..."
```

## 🔧 Integration Examples

### Bash Scripts
```bash
#!/bin/bash
# maintenance.sh - Server maintenance script

echo "Starting maintenance..."
./send_cli.sh notify "Maintenance" "Server maintenance started"

# Perform maintenance tasks
perform_backup()
update_system()
restart_services()

echo "Maintenance complete"
./send_cli.sh notify "Complete" "Server maintenance finished successfully"
```

### Cron Jobs
```bash
# Send daily reminders
0 9 * * * cd /path/to/voice-assistant && ./send_cli.sh broadcast "Good morning! Daily backup completed"

# Weekly status report
0 18 * * 5 cd /path/to/voice-assistant && python cli_client.py chat "Generate weekly server status report"
```

### Python Integration
```python
import subprocess
import json

def send_notification(title, message, device_id=None):
    cmd = ["python", "cli_client.py", "notify", title, message]
    if device_id:
        cmd.extend(["--device", device_id])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def get_server_status():
    result = subprocess.run(["python", "cli_client.py", "status"], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        # Parse JSON response
        return json.loads(result.stdout.split('\n', 1)[1])  # Skip "✅ Success!"
    return None

# Usage
send_notification("Alert", "Database connection lost")
status = get_server_status()
if status and not status.get("firebase_initialized"):
    send_notification("Error", "Firebase not initialized")
```

## 🐛 Troubleshooting

### Connection Errors
```bash
# Check if server is running
curl http://localhost:8000/health

# Test with different host/port
python cli_client.py --host 127.0.0.1 --port 8000 status

# Check network connectivity
ping your-server-ip
```

### Common Issues

**"Connection refused"**
- Server is not running
- Wrong host/port combination
- Firewall blocking connection

**"No registered devices"**
- Android app not installed/opened
- Device hasn't registered with server
- Check device list: `python cli_client.py devices`

**"Firebase not initialized"**
- Missing firebase service account file
- Check server status: `python cli_client.py status`

### Debug Mode
```bash
# Add verbose logging to see what's happening
python -u cli_client.py status 2>&1 | tee debug.log

# Check server logs
tail -f server.log
```

## 🚀 Advanced Usage

### Automated Monitoring
```bash
#!/bin/bash
# monitor.sh - Continuous server monitoring

while true; do
    if ! python cli_client.py status >/dev/null 2>&1; then
        echo "Server down - attempting restart"
        systemctl restart voice-assistant
        sleep 30
        
        if python cli_client.py status >/dev/null 2>&1; then
            ./send_cli.sh broadcast "Server recovered from outage"
        fi
    fi
    sleep 60
done
```

### Batch Operations
```bash
#!/bin/bash
# batch_notify.sh - Send notifications to multiple devices

devices=("android_123" "phone_001" "tablet_456")
message="$1"

for device in "${devices[@]}"; do
    echo "Sending to $device..."
    python cli_client.py send "$message" --device "$device"
    sleep 1  # Rate limiting
done
```

This CLI system provides a powerful interface for managing your Voice Assistant server remotely and integrating with other systems and scripts.