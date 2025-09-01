from gtts import gTTS
import os

def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("response.mp3")
        os.system("mpg321 response.mp3")
    except Exception as e:
        print(f"Text-to-speech error: {e}")
