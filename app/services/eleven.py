import os
from dotenv import load_dotenv
load_dotenv()
ELEVEN_KEY = os.getenv("ELEVEN_API_KEY")
eleven_client = None
# This is a minimal wrapper: replace with official ElevenLabs SDK calls.
if ELEVEN_KEY:
    eleven_client = {"api_key": ELEVEN_KEY}
