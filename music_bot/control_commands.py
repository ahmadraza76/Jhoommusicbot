from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from config import ERROR_IMG, NOW_PLAYING_IMG, QUEUE_IMG, SUDO_USERS
from client import app, pytgcalls, current_streams, queues, paused_streams, auth_users
from helpers import is_sudo, format_duration
from play_next import play_next

@app.on_message(filters.command(["pause", "p"]) & filters.group)
async def pause_music(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    chat_id = message.chat.id
    if chat_id in current_streams:
        if chat_id not in paused_streams:
            await pytgcalls.pause_stream(chat_id)
            paused_streams[chat_id] = True
            await message.reply_photo(photo=NOW_PLAYING_IMG, caption="⏸ **Playback Paused**\n\nUse `/resume` to continue.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Resume", callback_data="resume")]]))
        else:
            await message.reply_photo(photo=ERROR_IMG, caption="❗ **Already Paused**\n\nUse `/resume` to continue.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Resume", callback_data="resume")]]))
    else:
        await message.reply_photo(photo=ERROR_IMG, caption="❗ **Nothing Playing**\n\nStart with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))

@app.on_message(filters.command(["resume", "r"]) & filters.group)
async def resume_music(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    chat_id = message.chat.id
    if chat_id in current_streams:
        if chat_id in paused_streams:
            await pytgcalls.resume_stream(chat_id)
            del paused_streams[chat_id]
            await message.reply_photo(photo=NOW_PLAYING_IMG, caption="▶️ **Playback Resumed**\n\nEnjoy!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause")]]))
        else:
            await message.reply_photo(photo=ERROR_IMG, caption="❗ **Not Paused**\n\nPlayback is running.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause")]]))
    else:
        await message.reply_photo(photo=ERROR_IMG, caption="❗ **Nothing Playing**\n\nStart with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))

@app.on_message(filters.command("skip") & filters.group)
async def skip_music(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    chat_id = message.chat.id
    if chat_id in current_streams:
        await message.reply_photo(photo=NOW_PLAYING_IMG, caption="⏭ **Track Skipped**\n\nPlaying next track...", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]]))
        await play_next(chat_id)
    else:
        await message.reply_photo(photo=ERROR_IMG, caption="❗ **Nothing Playing**\n\nStart with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))

@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_music(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nYou need permission.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    chat_id = message.chat.id
    if chat_id in current_streams:
        await pytgcalls.leave_group_call(chat_id)
        if chat_id in current_streams:
            del current_streams[chat_id]
        if chat_id in queues:
            del queues[chat_id]
        if chat_id in paused_streams:
            del paused_streams[chat_id]
        await message.reply_photo(photo=NOW_PLAYING_IMG, caption="⏹ **Playback Stopped**\n\nQueue cleared. Start with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))
    else:
        await message.reply_photo(photo=ERROR_IMG, caption="❗ **Nothing Playing**\n\nStart with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))

@app.on_message(filters.command(["queue", "q"]) & filters.group)
async def show_queue(_, message: Message):
    chat_id = message.chat.id
    if chat_id in queues and queues[chat_id]:
        queue_text = "📋 **Queue**\n\n"
        for i, track in enumerate(queues[chat_id][:8], start=1):
            duration = await format_duration(track['duration']) if not track.get('is_live') else 'Live'
            title = track['title'][:35] + ("..." if len(track['title']) > 35 else "")
            queue_text += f"{i}. {title} ({duration})\n"
        if len(queues[chat_id]) > 8:
            queue_text += f"\n...and {len(queues[chat_id]) - 8} more tracks"
        await message.reply_photo(photo=QUEUE_IMG, caption=queue_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="show_queue"), InlineKeyboardButton("🗑 Clear Queue", callback_data="clear_queue")], [InlineKeyboardButton("🔍 Show More", callback_data="show_more_queue") if len(queues[chat_id]) > 8 else InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]]))
    else:
        await message.reply_photo(photo=QUEUE_IMG, caption="❗ **Queue Empty**\n\nAdd tracks with `/play`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]]))
