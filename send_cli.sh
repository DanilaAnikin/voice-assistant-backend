#!/bin/bash
# Quick CLI wrapper for common server operations
# Usage: ./send_cli.sh "Your message here"

# Default configuration
HOST="${VOICE_SERVER_HOST:-localhost}"
PORT="${VOICE_SERVER_PORT:-8000}"

# Check if python CLI exists
CLI_SCRIPT="$(dirname "$0")/cli_client.py"
if [[ ! -f "$CLI_SCRIPT" ]]; then
    echo "❌ CLI script not found: $CLI_SCRIPT"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Voice Assistant CLI Wrapper"
    echo ""
    echo "Usage:"
    echo "  $0 send \"message\"                    # Send message to default device"
    echo "  $0 notify \"title\" \"body\"             # Send notification"
    echo "  $0 broadcast \"message\"                # Send to all devices"  
    echo "  $0 chat \"question\"                    # Chat with AI"
    echo "  $0 devices                             # List devices"
    echo "  $0 status                              # Server status"
    echo ""
    echo "Environment variables:"
    echo "  VOICE_SERVER_HOST (default: localhost)"
    echo "  VOICE_SERVER_PORT (default: 8000)"
    echo ""
    echo "Examples:"
    echo "  $0 send \"Hello from command line!\""
    echo "  $0 notify \"Alert\" \"Server maintenance starting\""
    echo "  $0 broadcast \"System will reboot in 5 minutes\""
    echo "  $0 chat \"What's the current time?\""
}

# Check arguments
if [[ $# -eq 0 ]]; then
    show_usage
    exit 1
fi

# Execute command
case "$1" in
    "send")
        if [[ -z "$2" ]]; then
            echo "❌ Error: Message required for send command"
            echo "Usage: $0 send \"your message\""
            exit 1
        fi
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" send "$2" "${@:3}"
        ;;
    "notify")
        if [[ -z "$2" || -z "$3" ]]; then
            echo "❌ Error: Title and body required for notify command"
            echo "Usage: $0 notify \"title\" \"body\""
            exit 1
        fi
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" notify "$2" "$3" "${@:4}"
        ;;
    "broadcast")
        if [[ -z "$2" ]]; then
            echo "❌ Error: Message required for broadcast command"
            echo "Usage: $0 broadcast \"your message\""
            exit 1
        fi
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" broadcast "$2"
        ;;
    "chat")
        if [[ -z "$2" ]]; then
            echo "❌ Error: Question required for chat command"
            echo "Usage: $0 chat \"your question\""
            exit 1
        fi
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" chat "$2" "${@:3}"
        ;;
    "devices")
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" devices
        ;;
    "status")
        python "$CLI_SCRIPT" --host "$HOST" --port "$PORT" status
        ;;
    "help"|"--help"|"-h")
        show_usage
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac