from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set API keys from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in .env")

# Import AI functions
from src.speech_to_text import recognize_speech
from src.ai import chat_with_ai
from src.memory import save_conversation
from src.text_to_speech import speak

app = FastAPI()

@app.get("/voice-assistant")
def voice_assistant():
    user_input = recognize_speech()
    ai_response = chat_with_ai(user_input)
    save_conversation(user_input, ai_response)
    speak(ai_response)
    return {"User": user_input, "AI": ai_response}

@app.get("/livekit")
def livekit_status():
    return {
        "status": "LiveKit is running",
        "livekit_url": LIVEKIT_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
