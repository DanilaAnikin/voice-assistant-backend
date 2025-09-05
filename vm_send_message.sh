#!/bin/bash
# VM Message Sender - Easy CLI tool for sending messages to phone
# This script sends messages from the VM backend to the Android phone

# VM Server configuration
VM_HOST="185.120.71.223"
VM_PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}📱 VM to Phone Message Sender${NC}"
    echo ""
    echo "This tool sends messages from the VM backend to your Android phone."
    echo "Messages will appear in the chat and be spoken aloud by the phone."
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "  $0 send \"message\"                    # Send message to default device"
    echo "  $0 send \"message\" --device ID        # Send to specific device"
    echo "  $0 send \"message\" --silent           # Send silently (no TTS)"
    echo "  $0 notify \"title\" \"body\"             # Send notification with title"
    echo "  $0 broadcast \"message\"                # Send to all connected phones"
    echo "  $0 broadcast \"message\" --silent       # Send to all devices silently"  
    echo "  $0 chat \"question\"                    # Ask AI and send response to phone"
    echo "  $0 devices                             # List connected devices"
    echo "  $0 status                              # Check server status"
    echo "  $0 setup                               # Show Firebase setup instructions"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 send \"Hello from the VM server!\""
    echo "  $0 send \"Silent message\" --silent"
    echo "  $0 notify \"Server Alert\" \"System backup completed successfully\""
    echo "  $0 broadcast \"Server maintenance starting in 10 minutes\""
    echo "  $0 broadcast \"Silent broadcast\" --silent"
    echo "  $0 chat \"What's the current time?\""
}

# Function to show Firebase setup instructions
show_setup() {
    echo -e "${BLUE}🔥 Firebase Setup Instructions${NC}"
    echo ""
    echo "To enable message sending to your phone, you need to set up Firebase:"
    echo ""
    echo -e "${YELLOW}1. Download Firebase Admin SDK key:${NC}"
    echo "   - Go to https://console.firebase.google.com/"
    echo "   - Open your project > Settings > Service accounts"
    echo "   - Click 'Generate new private key'"
    echo "   - Save as 'firebase_admin_config.json' in this directory"
    echo ""
    echo -e "${YELLOW}2. Current Firebase status:${NC}"
    # Check Firebase status
    cd "$(dirname "$0")"
    if [[ -f "firebase_admin_config.json" ]]; then
        echo -e "   ${GREEN}✅ firebase_admin_config.json found${NC}"
    else
        echo -e "   ${RED}❌ firebase_admin_config.json missing${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}3. Test the connection:${NC}"
    echo "   $0 status"
    echo ""
}

# Check if CLI script exists
CLI_SCRIPT="$(dirname "$0")/cli_client.py"
if [[ ! -f "$CLI_SCRIPT" ]]; then
    echo -e "${RED}❌ CLI script not found: $CLI_SCRIPT${NC}"
    exit 1
fi

# Check arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

# Execute command
case "$1" in
    "send")
        if [[ -z "$2" ]]; then
            echo -e "${RED}❌ Error: Message required for send command${NC}"
            echo -e "${YELLOW}Usage:${NC} $0 send \"your message\""
            exit 1
        fi
        if [[ "$*" =~ --silent ]]; then
            echo -e "${BLUE}📤 Sending silent message to phone...${NC}"
        else
            echo -e "${BLUE}📤 Sending message to phone...${NC}"
        fi
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" send "$2" "${@:3}"
        ;;
    "notify")
        if [[ -z "$2" || -z "$3" ]]; then
            echo -e "${RED}❌ Error: Title and body required for notify command${NC}"
            echo -e "${YELLOW}Usage:${NC} $0 notify \"title\" \"body\""
            exit 1
        fi
        echo -e "${BLUE}🔔 Sending notification to phone...${NC}"
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" notify "$2" "$3" "${@:4}"
        ;;
    "broadcast")
        if [[ -z "$2" ]]; then
            echo -e "${RED}❌ Error: Message required for broadcast command${NC}"
            echo -e "${YELLOW}Usage:${NC} $0 broadcast \"your message\""
            exit 1
        fi
        if [[ "$*" =~ --silent ]]; then
            echo -e "${BLUE}📢 Broadcasting silent message to all devices...${NC}"
        else
            echo -e "${BLUE}📢 Broadcasting message to all devices...${NC}"
        fi
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" broadcast "$2" "${@:3}"
        ;;
    "chat")
        if [[ -z "$2" ]]; then
            echo -e "${RED}❌ Error: Question required for chat command${NC}"
            echo -e "${YELLOW}Usage:${NC} $0 chat \"your question\""
            exit 1
        fi
        echo -e "${BLUE}🤖 Asking AI and sending response to phone...${NC}"
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" chat "$2" "${@:3}"
        ;;
    "devices")
        echo -e "${BLUE}📱 Checking connected devices...${NC}"
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" devices
        ;;
    "status")
        echo -e "${BLUE}🔍 Checking server status...${NC}"
        python3 "$CLI_SCRIPT" --host "$VM_HOST" --port "$VM_PORT" status
        ;;
    "setup")
        show_setup
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac
