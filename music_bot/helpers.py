import asyncio
import yt_dlp
from typing import Dict, List, Optional
from config import logger, MAX_DURATION, SPOTIFY_IMG
from client import sp

async def is_sudo(user_id: int, auth_users: List[int], sudo_users: List[int]) -> bool:
    return user_id in sudo_users or user_id in auth_users

async def search_yt(query: str, max_results: int = 5) -> List[Dict]:
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'extract_flat': True,
        'noplaylist': True,
        'default_search': 'ytsearch',
        'max_downloads': max_results
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(f"ytsearch{max_results}:{query}", download=False))
            return info.get('entries', [])
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []

async def search_spotify(query: str, max_results: int = 5) -> List[Dict]:
    if not sp:
        return []
    try:
        results = sp.search(q=query, limit=max_results, type='track')
        tracks = []
        for track in results['tracks']['items']:
            artists = ", ".join([artist['name'] for artist in track['artists']])
            album = track['album']['name']
            tracks.append({
                'title': f"{artists} - {track['name']}",
                'duration': track['duration_ms'] // 1000,
                'id': track['id'],
                'url': f"https://open.spotify.com/track/{track['id']}",
                'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else SPOTIFY_IMG,
                'is_spotify': True,
                'album': album
            })
        return tracks
    except Exception as e:
        logger.error(f"Spotify search error: {e}")
        return []

async def get_spotify_track(track_id: str) -> Dict:
    if not sp:
        raise ValueError("Spotify not configured")
    try:
        track = sp.track(track_id)
        artists = ", ".join([artist['name'] for artist in track['artists']])
        album = track['album']['name']
        return {
            'title': f"{artists} - {track['name']}",
            'duration': track['duration_ms'] // 1000,
            'id': track['id'],
            'url': f"https://open.spotify.com/track/{track['id']}",
            'thumbnail': track['album']['images'][0]['url'] if track['album']['images'] else SPOTIFY_IMG,
            'is_spotify': True,
            'album': album
        }
    except Exception as e:
        logger.error(f"Spotify track error: {e}")
        raise

async def extract_info(video_id: str) -> Dict:
    ydl_opts = {'format': 'bestaudio', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(video_id, download=False))
            if info.get('duration', 0) > MAX_DURATION:
                raise ValueError(f"Duration exceeds {MAX_DURATION} seconds")
            return {
                'title': info.get('title', 'Unknown Track'),
                'url': info['url'],
                'thumbnail': info.get('thumbnail', NOW_PLAYING_IMG),
                'duration': info.get('duration', 0),
                'id': info.get('id'),
                'video': False
            }
    except Exception as e:
        logger.error(f"Extract info error: {e}")
        raise

async def extract_video_info(video_id: str) -> Dict:
    ydl_opts = {'format': 'bestvideo[height<=720]+bestaudio', 'quiet': True, 'noplaylist': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.get_event_loop().run_in_executor(None, lambda: ydl.extract_info(video_id, download=False))
            if info.get('duration', 0) > MAX_DURATION:
                raise ValueError(f"Duration exceeds {MAX_DURATION} seconds")
            return {
                'title': info.get('title', 'Unknown Video'),
                'url': info['url'],
                'thumbnail': info.get('thumbnail', NOW_PLAYING_IMG),
                'duration': info.get('duration', 0),
                'id': info.get('id'),
                'video': True
            }
    except Exception as e:
        logger.error(f"Extract video info error: {e}")
        raise

async def extract_m3u8_info(url: str) -> Optional[Dict]:
    try:
        return {
            'title': "Live Stream",
            'duration': 0,
            'url': url,
            'thumbnail': LIVE_IMG,
            'is_live': True,
            'ffmpeg_options': {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
        }
    except Exception as e:
        logger.error(f"M3U8 extract error: {e}")
        return None

async def format_duration(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"
