import asyncio
import yt_dlp
from typing import Dict, List, Optional
from config import logger, MAX_DURATION, SPOTIFY_IMG, NOW_PLAYING_IMG, LIVE_IMG
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
            info = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            )
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
            info = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: ydl.extract_info(video_id, download=False)
            )
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
            info = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: ydl.extract_info(video_id, download=False)
            )
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

async def play_spotify_track(chat_id: int, track_id: str, message):
    """Helper function to play Spotify tracks by searching YouTube"""
    from client import app, sp, pytgcalls, current_streams, queues
    from config import ERROR_IMG, NOW_PLAYING_IMG, MAX_QUEUE_SIZE
    from pytgcalls.types import AudioPiped, HighQualityAudio
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
    
    if not sp:
        if message:
            await message.reply_photo(
                photo=ERROR_IMG,
                caption="❌ **Spotify Not Available**\n\nConfigure Spotify credentials.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Learn More", url="https://developer.spotify.com/documentation/general/guides/authorization-guide/")]])
            )
        return
    
    try:
        spotify_track = await get_spotify_track(track_id)
        query = f"{spotify_track['title']} official audio"
        
        msg = None
        if message:
            msg = await message.reply_photo(
                photo=spotify_track['thumbnail'],
                caption=f"🔍 **Searching YouTube**\n\n`{query}`\n\nPlease wait..."
            )
        
        yt_results = await search_yt(query, 1)
        if not yt_results:
            raise ValueError("No YouTube results found")
        
        yt_track = await extract_info(yt_results[0]['url'])
        yt_track['thumbnail'] = spotify_track['thumbnail']
        yt_track['album'] = spotify_track.get('album')
        
        if chat_id in current_streams:
            if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                raise ValueError(f"Queue limit reached ({MAX_QUEUE_SIZE})")
            queues.setdefault(chat_id, []).append(yt_track)
            reply_text = f"➕ **Added to Queue**\n\n**{yt_track['title'][:35]}{'...' if len(yt_track['title']) > 35 else ''}**\n"
            if yt_track.get('album'):
                reply_text += f"💿 Album: {yt_track['album']}\n"
            reply_text += f"⏳ Duration: {await format_duration(yt_track['duration'])}"
            final_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
        else:
            current_streams[chat_id] = yt_track
            try:
                await pytgcalls.join_group_call(chat_id, AudioPiped(yt_track['url'], HighQualityAudio()))
                reply_text = f"🎧 **Now Playing**\n\n**{yt_track['title'][:35]}{'...' if len(yt_track['title']) > 35 else ''}**\n"
                if yt_track.get('album'):
                    reply_text += f"💿 Album: {yt_track['album']}\n"
                reply_text += f"⏳ Duration: {await format_duration(yt_track['duration'])}"
                final_reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")],
                    [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]
                ])
            except Exception as e:
                if chat_id in current_streams:
                    del current_streams[chat_id]
                raise Exception(f"Failed to join VC: {e}")
        
        if msg:
            await msg.edit_media(
                InputMediaPhoto(
                    media=yt_track['thumbnail'],
                    caption=reply_text
                ),
                reply_markup=final_reply_markup
            )
        else:
            await app.send_photo(
                chat_id,
                photo=yt_track['thumbnail'],
                caption=reply_text,
                reply_markup=final_reply_markup
            )
    except Exception as e:
        error_msg = f"❌ **Error**\n\n`{str(e)}`\n\nTry again."
        if msg:
            await msg.edit_media(
                InputMediaPhoto(media=ERROR_IMG, caption=error_msg),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_spotify")]])
            )
        else:
            await app.send_photo(
                chat_id,
                photo=ERROR_IMG,
                caption=error_msg,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_spotify")]])
            )