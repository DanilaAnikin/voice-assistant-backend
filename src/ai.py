from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
import os

  # Reads API key from environment variables

if not openai.api_key:
    raise ValueError("OpenAI API Key is missing. Set OPENAI_API_KEY in .env.local")

def chat_with_ai(prompt):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a voice assistant."},
        {"role": "user", "content": prompt}
    ])
    return response.choices[0].message.content
