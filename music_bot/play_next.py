from pytgcalls.types import AudioPiped, VideoPiped
from pytgcalls.types.input_stream.quality import HighQualityAudio, HighQualityVideo
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import NOW_PLAYING_IMG, ERROR_IMG, logger
from client import app, pytgcalls, current_streams, queues, paused_streams
from helpers import format_duration

async def play_next(chat_id: int):
    if chat_id in queues and queues[chat_id]:
        track = queues[chat_id].pop(0)
        current_streams[chat_id] = track
        try:
            if track.get('video'):
                await pytgcalls.change_stream(chat_id, VideoPiped(track['url'], HighQualityVideo()))
            else:
                await pytgcalls.change_stream(chat_id, AudioPiped(track['url'], HighQualityAudio(), **track.get('ffmpeg_options', {})))
            caption = f"🎵 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n"
            if track.get('album'):
                caption += f"💿 Album: {track['album']}\n"
            caption += f"⏳ Duration: {'LIVE' if track.get('is_live') else await format_duration(track['duration'])}"
            await app.send_photo(
                chat_id,
                photo=track.get('thumbnail', NOW_PLAYING_IMG),
                caption=caption,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")],
                    [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]
                ])
            )
        except Exception as e:
            logger.error(f"Play next error: {e}")
            await app.send_photo(
                chat_id,
                photo=ERROR_IMG,
                caption=f"❌ **Error:** {e}\n\nTry again.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_play")]])
            )
            await play_next(chat_id)
    else:
        if chat_id in current_streams:
            del current_streams[chat_id]
        if chat_id in paused_streams:
            del paused_streams[chat_id]
        try:
            await pytgcalls.leave_group_call(chat_id)
            await app.send_photo(
                chat_id,
                photo=NOW_PLAYING_IMG,
                caption="🎶 **Playback Ended**\n\nQueue empty. Add tracks with /play!",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]])
            )
        except Exception as e:
            logger.error(f"Error leaving group call: {e}")
