import os
import sys
import logging
from typing import List, Dict

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_ID = int(os.getenv("API_ID", 12345))
API_HASH = os.getenv("API_HASH", "abcdef12345")
BOT_TOKEN = os.getenv("BOT_TOKEN", "12345:abcdef")
FFMPEG_PROCESSES = int(os.getenv("FFMPEG_PROCESSES", 1))
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", "123456789").split()))
MAX_DURATION = int(os.getenv("MAX_DURATION", 3600))  # 1 hour max
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 50))  # Max queue size

# Validate config
if not all([API_ID, API_HASH, BOT_TOKEN]):
    logger.error("Missing required environment variables")
    sys.exit(1)

# Image URLs
IMAGE_BASE = "https://cdn.jhoom.io/"
IMAGE_FALLBACK = "https://i.imgur.com/4M34hi2.jpg"
MAIN_MENU_IMG = os.getenv("MAIN_MENU_IMG", IMAGE_BASE + "main_menu.jpg") or IMAGE_FALLBACK
HELP_IMG = os.getenv("HELP_IMG", IMAGE_BASE + "help.jpg") or IMAGE_FALLBACK
SYSTEM_IMG = os.getenv("SYSTEM_IMG", IMAGE_BASE + "system.jpg") or IMAGE_FALLBACK
DEV_IMG = os.getenv("DEV_IMG", IMAGE_BASE + "dev.jpg") or IMAGE_FALLBACK
NOW_PLAYING_IMG = os.getenv("NOW_PLAYING_IMG", IMAGE_BASE + "now_playing.jpg") or IMAGE_FALLBACK
SEARCH_IMG = os.getenv("SEARCH_IMG", IMAGE_BASE + "search.jpg") or IMAGEhale
SPOTIFY_IMG = os.getenv("SPOTIFY_IMG", IMAGE_BASE + "spotify.jpg") or IMAGE_FALLBACK
LIVE_IMG = os.getenv("LIVE_IMG", IMAGE_BASE + "live.jpg") or IMAGE_FALLBACK
AUTH_IMG = os.getenv("AUTH_IMG", IMAGE_BASE + "auth.jpg") or IMAGE_FALLBACK
QUEUE_IMG = os.getenv("QUEUE_IMG", IMAGE_BASE + "queue.jpg") or IMAGE_FALLBACK
ERROR_IMG = os.getenv("ERROR_IMG", IMAGE_BASE + "error.jpg") or IMAGE_FALLBACK

# Command details
COMMAND_DETAILS = {
    "playback": {
        "title": "🎵 Playback Controls",
        "description": "Stream and control music/video playback",
        "commands": [
            "/play [query|youtube_link|spotify_link] - Stream audio from YouTube or Spotify",
            "/vplay [query|youtube_link] - Stream video from YouTube",
            "/live [m3u8_url] - Stream live M3U8 content",
            "/pause - Pause current playback",
            "/resume - Resume paused playback",
            "/skip - Skip to next track",
            "/stop - Stop playback and clear queue",
            "/queue - View current queue"
        ]
    },
    "auth": {
        "title": "🔐 Authorization",
        "description": "Manage user access permissions",
        "commands": [
            "/auth [user_id] - Authorize a user (private chat)",
            "/unauth [user_id] - Revoke user access (private chat)",
            "/authusers - List authorized users (private chat)"
        ]
    },
    "broadcast": {
        "title": "📢 Broadcast",
        "description": "Send messages to all groups (sudo only)",
        "commands": [
            "/broadcast [message] - Broadcast a message to all groups"
        ]
    }
}
