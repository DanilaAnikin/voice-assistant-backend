<img src="./.github/assets/app-icon.png" alt="Voice Assistant App Icon" width="100" height="100">

# Web Voice Assistant

## Clone the repository
```bash
git clone git@github.com:DanilaAnikin/voice-assistant-backend.git
cd voice-assistant-backend
```

## Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Create a ```.env``` file:
```bash
nano .env
```
3. Then add:
```bash
OPENAI_API_KEY=sk-proj-your-api-key
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
LIVEKIT_URL=wss://your-livekit-server-url
```
to your new ```.env``` file with correct KEYs and URLs

4. Run the backend server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. Setup frontend from ```github.com/DanilaAnikin/voice-assistant-frontend```, run it and open on your device
