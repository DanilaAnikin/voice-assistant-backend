#!/usr/bin/env python3
"""
CLI client for Voice Assistant Server
Allows sending messages and notifications from command line
"""

import argparse
import requests
import json
import sys
from typing import Optional

# Default server configuration
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8000
DEFAULT_BASE_URL = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}"

class VoiceAssistantCLI:
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to server"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url)
            elif method.upper() == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def send_message(self, message: str, device_id: str = "default") -> dict:
        """Send custom message to specific device"""
        data = {
            "message": message,
            "device_id": device_id,
            "type": "cli_message"
        }
        return self._make_request("POST", "/send_message", data)
    
    def send_notification(self, title: str, body: str, device_id: str = "default") -> dict:
        """Send notification with title and body"""
        data = {
            "title": title,
            "body": body,
            "device_id": device_id
        }
        return self._make_request("POST", "/send_notification", data)
    
    def broadcast_message(self, message: str) -> dict:
        """Send message to all registered devices"""
        return self._make_request("POST", f"/broadcast_message?message={message}")
    
    def send_to_device(self, device_id: str, message: str) -> dict:
        """Send message to specific device using endpoint params"""
        return self._make_request("POST", f"/send_message_to_device?device_id={device_id}&message={message}")
    
    def list_devices(self) -> dict:
        """List all registered devices"""
        return self._make_request("GET", "/devices")
    
    def get_status(self) -> dict:
        """Get Firebase and system status"""
        return self._make_request("GET", "/firebase_status")
    
    def chat(self, text: str, device_id: str = None, spoken: bool = False) -> dict:
        """Send chat message to AI"""
        data = {
            "text": text,
            "spoken": spoken
        }
        if device_id:
            data["device_id"] = device_id
        return self._make_request("POST", "/chat", data)

def main():
    parser = argparse.ArgumentParser(
        description="CLI client for Voice Assistant Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send simple message to default device
  python cli_client.py send "Hello from server!"
  
  # Send message to specific device
  python cli_client.py send "Hello!" --device android_123
  
  # Send notification with title
  python cli_client.py notify "Alert" "Something important happened"
  
  # Broadcast to all devices
  python cli_client.py broadcast "Server maintenance in 10 minutes"
  
  # Chat with AI and send response to device
  python cli_client.py chat "What's the weather like?"
  
  # List registered devices
  python cli_client.py devices
  
  # Check server status
  python cli_client.py status
        """
    )
    
    parser.add_argument(
        "--host", 
        default=DEFAULT_HOST,
        help=f"Server host (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=DEFAULT_PORT,
        help=f"Server port (default: {DEFAULT_PORT})"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Send message command
    send_parser = subparsers.add_parser("send", help="Send message to device")
    send_parser.add_argument("message", help="Message to send")
    send_parser.add_argument("--device", default="default", help="Target device ID")
    
    # Send notification command  
    notify_parser = subparsers.add_parser("notify", help="Send notification")
    notify_parser.add_argument("title", help="Notification title")
    notify_parser.add_argument("body", help="Notification body")
    notify_parser.add_argument("--device", default="default", help="Target device ID")
    
    # Broadcast command
    broadcast_parser = subparsers.add_parser("broadcast", help="Send message to all devices")
    broadcast_parser.add_argument("message", help="Message to broadcast")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with AI")
    chat_parser.add_argument("text", help="Message for AI")
    chat_parser.add_argument("--device", help="Send AI response to specific device")
    chat_parser.add_argument("--spoken", action="store_true", help="Enable spoken response")
    
    # Device list command
    subparsers.add_parser("devices", help="List registered devices")
    
    # Status command  
    subparsers.add_parser("status", help="Show server status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI client
    base_url = f"http://{args.host}:{args.port}"
    cli = VoiceAssistantCLI(base_url)
    
    # Execute command
    try:
        if args.command == "send":
            result = cli.send_message(args.message, args.device)
        elif args.command == "notify":
            result = cli.send_notification(args.title, args.body, args.device)
        elif args.command == "broadcast":
            result = cli.broadcast_message(args.message)
        elif args.command == "chat":
            result = cli.chat(args.text, args.device, args.spoken)
        elif args.command == "devices":
            result = cli.list_devices()
        elif args.command == "status":
            result = cli.get_status()
        else:
            print(f"Unknown command: {args.command}")
            return
        
        # Print result
        if "error" in result:
            print(f"❌ Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        else:
            print("✅ Success!")
            print(json.dumps(result, indent=2))
            
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()