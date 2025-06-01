from livekit import RoomServiceClient
import os

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
API_KEY = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")

room_client = RoomServiceClient(LIVEKIT_URL, API_KEY, API_SECRET)

def create_room(room_name):
    room = room_client.create_room(name=room_name)
    return room