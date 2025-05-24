from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import ERROR_IMG, NOW_PLAYING_IMG, MAX_QUEUE_SIZE, logger
from client import app, sp, pytgcalls, current_streams, queues
from helpers import search_yt, extract_info, format_duration, get_spotify_track
from pytgcalls.types import AudioPiped, HighQualityAudio

async def play_spotify_track(chat_id: int, track_id: str, message: Message = None):
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
        
        is_now_playing = False
        if chat_id in current_streams:
            if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                raise ValueError(f"Queue limit reached ({MAX_QUEUE_SIZE})")
            queues.setdefault(chat_id, []).append(yt_track)
            reply_text = f"➕ **Added to Queue**\n\n**{yt_track['title'][:35]}{'...' if len(yt_track['title']) > 35 else ''}**\n"
            if yt_track.get('album'):
                reply_text += f"💿 Album: {yt_track['album']}\n"
            reply_text += f"⏳ Duration: {await format_duration(yt_track['duration'])}"
            final_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("✨ View Queue", callback_data="show_queue")]])
        else:
            current_streams[chat_id] = yt_track
            try:
                await pytgcalls.join_group_call(chat_id, AudioPiped(yt_track['url'], HighQualityAudio()))
                is_now_playing = True
                reply_text = f"🎧 **Now Playing**\n\n**{yt_track['title'][:35]}{'...' if len(yt_track['title']) > 35 else ''}**\n"
                if yt_track.get('album'):
                    reply_text += f"💿 Album: {yt_track['album']}\n"
                reply_text += f"⏳ Duration: {await format_duration(yt_track['duration'])}"
                final_reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton("✨ View Queue", callback_data="show_queue"), InlineKeyboardButton("❌ Close", callback_data="close_player")]
                ])
            except Exception as e:
                if chat_id in current_streams: # Clean up if join_group_call failed
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
            # This case might ideally not happen if 'message' is always passed for Spotify commands
            # but handling it for robustness
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
