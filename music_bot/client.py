from pyrogram import Client
from pytgcalls import PyTgCalls
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, List
from config import API_ID, API_HASH, BOT_TOKEN, FFMPEG_PROCESSES, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, logger, SUDO_USERS

# Initialize bot
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Initialize PyTgCalls with correct parameters
pytgcalls = PyTgCalls(app)

# Spotify setup
if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    try:
        auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
        sp = spotipy.Spotify(auth_manager=auth_manager)
        logger.info("Spotify integration enabled")
    except Exception as e:
        sp = None
        logger.error(f"Spotify setup failed: {e}")
else:
    sp = None
    logger.warning("Spotify credentials missing. Spotify features disabled.")

# Global variables
current_streams: Dict[int, Dict] = {}
queues: Dict[int, List[Dict]] = {}
paused_streams: Dict[int, bool] = {}
search_results: Dict[int, List[Dict]] = {}
auth_users: List[int] = SUDO_USERS.copy()