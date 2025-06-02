from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import openai

from src.speech_to_text import recognize_speech
from src.memory import save_conversation
from src.text_to_speech import speak

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("Missing OpenAI API Key! Set OPENAI_API_KEY in .env")

openai.api_key = openai_api_key

app = FastAPI()

# ✅ Allow CORS requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the actual frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

def chat_with_ai(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error fetching AI response: {str(e)}"

@app.post("/chat")
async def chat_with_assistant(request: Request):
    try:
        data = await request.json()
        user_input = data.get("text")

        if not user_input:
            user_input = recognize_speech()

        ai_response = chat_with_ai(user_input)
        save_conversation(user_input, ai_response)

        if data.get("spoken", False):
            speak(ai_response)

        return {"User": user_input, "AI": ai_response}

    except Exception as e:
        return {"error": f"Backend failure: {str(e)}"}
