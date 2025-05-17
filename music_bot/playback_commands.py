from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import ERROR_IMG, HELP_IMG, SEARCH_IMG, SPOTIFY_IMG, LIVE_IMG, MAX_QUEUE_SIZE, logger
from client import app, sp, current_streams, queues, search_results
from helpers import is_sudo, SUDO_USERS, search_yt, search_spotify, extract_info, extract_video_info, extract_m3u8_info, play_spotify_track, format_duration

@app.on_message(filters.command("play") & filters.group)
async def play_music(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if len(message.command) < 2:
        return await message.reply_photo(photo=HELP_IMG, caption="🔍 **Usage**\n\n`/play song_name`\n`/play youtube_link`\n`/play spotify_link`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    if "open.spotify.com/track/" in query:
        if not sp:
            return await message.reply_photo(photo=ERROR_IMG, caption="❌ **Spotify Not Available**\n\nConfigure Spotify credentials.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Learn More", url="https://developer.spotify.com/documentation/general/guides/authorization-guide/")]]))
        try:
            track_id = query.split("open.spotify.com/track/")[1].split("?")[0].split("/")[0]
            await play_spotify_track(chat_id, track_id, message)
        except Exception as e:
            await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_spotify")]]))
        return
    if "youtube.com/watch" in query or "youtu.be/" in query:
        try:
            track = await extract_info(query)
            if chat_id in current_streams:
                if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                    return await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Queue Full**\n\nMax size ({MAX_QUEUE_SIZE}) reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
                queues.setdefault(chat_id, []).append(track)
                await message.reply_photo(photo=track.get('thumbnail', NOW_PLAYING_IMG), caption=f"➕ **Added to Queue**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
            else:
                current_streams[chat_id] = track
                try:
                    await pytgcalls.join_group_call(chat_id, AudioPiped(track['url'], HighQualityAudio()))
                    await message.reply_photo(photo=track.get('thumbnail', NOW_PLAYING_IMG), caption=f"🎵 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")], [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]]))
                except Exception as e:
                    del current_streams[chat_id]
                    await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Voice Chat Error**\n\n`{str(e)}`\n\nCheck VC permissions.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_play")]]))
        except Exception as e:
            await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_play")]]))
        return
    msg = await message.reply_photo(photo=SEARCH_IMG, caption=f"🔍 **Searching**\n\n`{query}`\n\nPlease wait...")
    results = []
    if sp:
        spotify_results = await search_spotify(query)
        results.extend(spotify_results)
    yt_results = await search_yt(query)
    results.extend(yt_results)
    if not results:
        await msg.edit_media(InputMediaPhoto(media=ERROR_IMG, caption="❌ **No Results**\n\nTry a different query."), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Try Again", callback_data="search_menu")]]))
        return
    search_results[chat_id] = results
    buttons = []
    for i, result in enumerate(results[:5], start=1):
        title = result['title'][:30] + ("..." if len(result['title']) > 30 else "")
        duration = await format_duration(result['duration']) if 'duration' in result else "Unknown"
        callback_data = f"spotify_{result['id']}" if result.get('is_spotify') else f"play_{result['id']}"
        buttons.append([InlineKeyboardButton(f"{i}. {title} ({duration})", callback_data=callback_data)])
    buttons.append([InlineKeyboardButton("🔍 More Results", callback_data="more_results"), InlineKeyboardButton("❌ Close", callback_data="close_search")])
    await msg.edit_media(InputMediaPhoto(media=SEARCH_IMG, caption=f"🔍 **Search Results**\n\n`{query}`\n\nSelect a track:"), reply_markup=InlineKeyboardMarkup(buttons))

@app.on_message(filters.command(["vplay", "vp"]) & filters.group)
async def play_video(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if len(message.command) < 2:
        return await message.reply_photo(photo=HELP_IMG, caption="🔍 **Usage**\n\n`/vplay video_name`\n`/vplay youtube_link`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    if "youtube.com/watch" in query or "youtu.be/" in query:
        try:
            track = await extract_video_info(query)
            if chat_id in current_streams:
                if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                    return await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Queue Full**\n\nMax size ({MAX_QUEUE_SIZE}) reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
                queues.setdefault(chat_id, []).append(track)
                await message.reply_photo(photo=track.get('thumbnail', NOW_PLAYING_IMG), caption=f"➕ **Added to Queue**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
            else:
                current_streams[chat_id] = track
                try:
                    await pytgcalls.join_group_call(chat_id, VideoPiped(track['url'], HighQualityVideo()))
                    await message.reply_photo(photo=track.get('thumbnail', NOW_PLAYING_IMG), caption=f"🎥 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")], [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]]))
                except Exception as e:
                    del current_streams[chat_id]
                    await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Voice Chat Error**\n\n`{str(e)}`\n\nCheck VC permissions.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_vplay")]]))
        except Exception as e:
            await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_vplay")]]))
        return
    msg = await message.reply_photo(photo=SEARCH_IMG, caption=f"🔍 **Searching**\n\n`{query}`\n\nPlease wait...")
    results = await search_yt(query)
    if not results:
        await msg.edit_media(InputMediaPhoto(media=ERROR_IMG, caption="❌ **No Results**\n\nTry a different query."), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Try Again", callback_data="search_menu")]]))
        return
    search_results[chat_id] = results
    buttons = [[InlineKeyboardButton(f"{i}. {result.get('title', 'Unknown Video')[:30]}{'...' if len(result.get('title', '')) > 30 else ''} ({await format_duration(result.get('duration', 0))})", callback_data=f"vplay_{result['id']}")] for i, result in enumerate(results[:5], start=1)]
    buttons.append([InlineKeyboardButton("🔍 More Results", callback_data="more_results"), InlineKeyboardButton("❌ Close", callback_data="close_search")])
    await msg.edit_media(InputMediaPhoto(media=SEARCH_IMG, caption=f"🔍 **Search Results**\n\n`{query}`\n\nSelect a video:"), reply_markup=InlineKeyboardMarkup(buttons))

@app.on_message(filters.command(["live", "stream"]) & filters.group)
async def live_stream(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if len(message.command) < 2:
        return await message.reply_photo(photo=HELP_IMG, caption="🔍 **Usage**\n\n`/live m3u8_url`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    url = message.command[1]
    chat_id = message.chat.id
    if not (url.startswith('http') and ('m3u8' in url)):
        return await message.reply_photo(photo=ERROR_IMG, caption="❌ **Invalid URL**\n\nProvide a valid M3U8 URL.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Learn More", url="https://en.wikipedia.org/wiki/M3U")]]))
    try:
        track = await extract_m3u8_info(url)
        if not track:
            raise ValueError("Invalid M3U8 stream")
        if chat_id in current_streams:
            if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                return await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Queue Full**\n\nMax size ({MAX_QUEUE_SIZE}) reached.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
            queues.setdefault(chat_id, []).append(track)
            await message.reply_photo(photo=LIVE_IMG, caption="➕ **Added to Queue**\n\n**Live Stream**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
        else:
            current_streams[chat_id] = track
            try:
                await pytgcalls.join_group_call(chat_id, AudioPiped(track['url'], HighQualityAudio(), **track.get('ffmpeg_options', {})))
                await message.reply_photo(photo=LIVE_IMG, caption="📡 **Live Stream Started**\n\n**Live Stream**", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")], [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]]))
            except Exception as e:
                del current_streams[chat_id]
                await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Voice Chat Error**\n\n`{str(e)}`\n\nCheck VC permissions.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_live")]]))
    except Exception as e:
        await message.reply_photo(photo=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_live")]]))
