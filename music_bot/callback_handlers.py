from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pytgcalls.types import AudioPiped, HighQualityAudio, VideoPiped, HighQualityVideo
from config import HELP_IMG, SYSTEM_IMG, DEV_IMG, MAIN_MENU_IMG, SEARCH_IMG, SPOTIFY_IMG, ERROR_IMG, NOW_PLAYING_IMG, QUEUE_IMG, AUTH_IMG, COMMAND_DETAILS, FFMPEG_PROCESSES, MAX_DURATION, MAX_QUEUE_SIZE, logger, SUDO_USERS
from client import app, pytgcalls, sp, current_streams, queues, paused_streams, search_results, auth_users
from helpers import is_sudo, format_duration, extract_info, extract_video_info, play_spotify_track
from ui_menus import commands_menu_ui
from play_next import play_next
from datetime import datetime

@app.on_callback_query(filters.regex(r"^help_menu$|^show_commands$"))
async def help_menu(_, callback: CallbackQuery):
    help_text = "📜 **Command Guide**\n\n"
    for category, details in COMMAND_DETAILS.items():
        help_text += f"**{details['title']}**\n_{details['description']}_\n\n"
        for cmd in details['commands']:
            help_text += f"• `{cmd}`\n"
        help_text += "\n"
    await callback.message.edit_media(
        InputMediaPhoto(media=HELP_IMG, caption=help_text),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu"), InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]
        ])
    )
    await callback.answer("Help menu opened")

@app.on_callback_query(filters.regex(r"^system_menu$|^settings_menu$"))
async def system_menu(_, callback: CallbackQuery):
    spotify_status = "✅ Enabled" if sp else "❌ Disabled"
    active_streams = len(current_streams)
    total_queued = sum(len(q) for q in queues.values())
    await callback.message.edit_media(
        InputMediaPhoto(
            media=SYSTEM_IMG,
            caption=f"""⚙️ **System Status**

**Overview:**
🟢 **Status:** Online
🚀 **Performance:** Optimal
🎵 **Spotify:** {spotify_status}

**Resources:**
🔊 Active Streams: {active_streams}
📋 Queued Tracks: {total_queued}
⚙️ FFmpeg Processes: {FFMPEG_PROCESSES}
⏳ Max Duration: {MAX_DURATION//60} min
📊 Max Queue: {MAX_QUEUE_SIZE}

**Last Updated:** {datetime.now().strftime('%H:%M:%S %Z')}"""
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh", callback_data="settings_menu"), InlineKeyboardButton("🔙 Back", callback_data="main_menu")],
            [InlineKeyboardButton("📈 Check Updates", callback_data="check_updates")]
        ])
    )
    await callback.answer("System status displayed")

@app.on_callback_query(filters.regex(r"^dev_menu$|^dev_info$"))
async def dev_menu(_, callback: CallbackQuery):
    await callback.message.edit_media(
        InputMediaPhoto(
            media=DEV_IMG,
            caption="""👨‍💻 **About Developer**

🌟 **Bot Version:** v3.2.1
📅 **Updated:** 2025-05-17
🧠 **AI Core:** GPT-4o

**Created By:** Music Bot Team
📢 **Channel:** @MusicBotUpdates
📧 **Support:** Contact via channel"""
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu"), InlineKeyboardButton("📢 Join Channel", url="https://t.me/MusicBotUpdates")]
        ])
    )
    await callback.answer("Developer info displayed")

@app.on_callback_query(filters.regex(r"^main_menu$"))
async def main_menu(_, callback: CallbackQuery):
    text, buttons = await commands_menu_ui()
    await callback.message.edit_media(
        InputMediaPhoto(media=MAIN_MENU_IMG, caption=text),
        reply_markup=buttons
    )
    await callback.answer("Main menu opened")

@app.on_callback_query(filters.regex(r"^quick_start$"))
async def quick_start(_, callback: CallbackQuery):
    await callback.message.edit_media(
        InputMediaPhoto(
            media=HELP_IMG,
            caption="""🚀 **Quick Start Guide**

1. **Join Voice Chat** and add @MusicBot
2. **Grant Admin** permissions
3. Use **/play song_name** or **/play youtube_link**
4. Try **/vplay** for videos or **/live** for streams
5. Control with **/pause**, **/resume**, **/skip**, **/stop**

Need help? Check /help"""
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu"), InlineKeyboardButton("📜 Full Guide", callback_data="help_menu")]
        ])
    )
    await callback.answer("Quick start guide displayed")

@app.on_callback_query(filters.regex(r"^check_updates$"))
async def check_updates(_, callback: CallbackQuery):
    await callback.message.edit_media(
        InputMediaPhoto(
            media=SYSTEM_IMG,
            caption="""📈 **Update Status**

✅ **Up to Date**
🌟 **Version:** v3.2.1
📅 **Last Checked:** 2025-05-17

Join our channel for updates!"""
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="settings_menu"), InlineKeyboardButton("📢 Join Channel", url="https://t.me/MusicBotUpdates")]
        ])
    )
    await callback.answer("Update status checked")

@app.on_callback_query(filters.regex(r"^search_menu$"))
async def search_menu(_, callback: CallbackQuery):
    await callback.message.edit_media(
        InputMediaPhoto(
            media=SEARCH_IMG,
            caption="🔍 **Search Music**\n\nEnter `/play song_name` or `/vplay video_name` to search."
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="main_menu")]
        ])
    )
    await callback.answer("Search menu opened")

@app.on_callback_query(filters.regex(r"^play_(.+)$"))
async def play_selected(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    video_id = callback.data.split("_")[1]
    try:
        track = await extract_info(video_id)
        if chat_id in current_streams:
            if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                await callback.message.edit_media(
                    InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Queue Full**\n\nMax size ({MAX_QUEUE_SIZE}) reached."),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
                )
                await callback.answer("Queue full")
                return
            queues.setdefault(chat_id, []).append(track)
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=track.get('thumbnail', NOW_PLAYING_IMG),
                    caption=f"➕ **Added to Queue**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}"
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
            )
        else:
            current_streams[chat_id] = track
            try:
                await pytgcalls.join_group_call(chat_id, AudioPiped(track['url'], HighQualityAudio()))
                await callback.message.edit_media(
                    InputMediaPhoto(
                        media=track.get('thumbnail', NOW_PLAYING_IMG),
                        caption=f"🎵 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")],
                        [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]
                    ])
                )
            except Exception as e:
                del current_streams[chat_id]
                await callback.message.edit_media(
                    InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Voice Chat Error**\n\n`{str(e)}`\n\nCheck VC permissions."),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data=f"retry_play_{video_id}")]])
                )
                await callback.answer("Voice chat error")
                return
        await callback.answer("Track added/playing")
    except Exception as e:
        await callback.message.edit_media(
            InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data=f"retry_play_{video_id}")]])
        )
        await callback.answer("Error occurred")

@app.on_callback_query(filters.regex(r"^vplay_(.+)$"))
async def vplay_selected(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    video_id = callback.data.split("_")[1]
    try:
        track = await extract_video_info(video_id)
        if chat_id in current_streams:
            if len(queues.get(chat_id, [])) >= MAX_QUEUE_SIZE:
                await callback.message.edit_media(
                    InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Queue Full**\n\nMax size ({MAX_QUEUE_SIZE}) reached."),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
                )
                await callback.answer("Queue full")
                return
            queues.setdefault(chat_id, []).append(track)
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=track.get('thumbnail', NOW_PLAYING_IMG),
                    caption=f"➕ **Added to Queue**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}"
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
            )
        else:
            current_streams[chat_id] = track
            try:
                await pytgcalls.join_group_call(chat_id, VideoPiped(track['url'], HighQualityVideo()))
                await callback.message.edit_media(
                    InputMediaPhoto(
                        media=track.get('thumbnail', NOW_PLAYING_IMG),
                        caption=f"🎥 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n⏳ Duration: {await format_duration(track['duration'])}"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")],
                        [InlineKeyboardButton("📋 Queue", callback_data="show_queue"), InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]
                    ])
                )
            except Exception as e:
                del current_streams[chat_id]
                await callback.message.edit_media(
                    InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Voice Chat Error**\n\n`{str(e)}`\n\nCheck VC permissions."),
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data=f"retry_vplay_{video_id}")]])
                )
                await callback.answer("Voice chat error")
                return
        await callback.answer("Video added/playing")
    except Exception as e:
        await callback.message.edit_media(
            InputMediaPhoto(media=ERROR_IMG, caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data=f"retry_vplay_{video_id}")]])
        )
        await callback.answer("Error occurred")

@app.on_callback_query(filters.regex(r"^spotify_(.+)$"))
async def spotify_selected(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    track_id = callback.data.split("_")[1]
    await play_spotify_track(chat_id, track_id, callback.message)
    await callback.answer("Spotify track selected")

@app.on_callback_query(filters.regex(r"^retry_play_(.+)$"))
async def retry_play(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    video_id = callback.data.split("_")[2]
    await callback.message.edit_media(
        InputMediaPhoto(media=SEARCH_IMG, caption="🔄 **Retrying**\n\nPlease wait...")
    )
    await play_selected(None, callback.__setattr__('data', f"play_{video_id}"))
    await callback.answer("Retrying play")

@app.on_callback_query(filters.regex(r"^retry_vplay_(.+)$"))
async def retry_vplay(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    video_id = callback.data.split("_")[2]
    await callback.message.edit_media(
        InputMediaPhoto(media=SEARCH_IMG, caption="🔄 **Retrying**\n\nPlease wait...")
    )
    await vplay_selected(None, callback.__setattr__('data', f"vplay_{video_id}"))
    await callback.answer("Retrying video play")

@app.on_callback_query(filters.regex(r"^retry_spotify$"))
async def retry_spotify(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    await callback.message.edit_media(
        InputMediaPhoto(
            media=SPOTIFY_IMG,
            caption="🔄 **Retry Spotify**\n\nEnter `/play spotify_link` to try again."
        ),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="search_menu")]])
    )
    await callback.answer("Retry Spotify prompted")

@app.on_callback_query(filters.regex(r"^retry_live$"))
async def retry_live(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    await callback.message.edit_media(
        InputMediaPhoto(
            media=SEARCH_IMG,
            caption="🔄 **Retry Live Stream**\n\nEnter `/live m3u8_url` to try again."
        ),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="search_menu")]])
    )
    await callback.answer("Retry live stream prompted")

@app.on_callback_query(filters.regex(r"^pause$"))
async def pause_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    if chat_id in current_streams:
        if chat_id not in paused_streams:
            await pytgcalls.pause_stream(chat_id)
            paused_streams[chat_id] = True
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=NOW_PLAYING_IMG,
                    caption="⏸ **Playback Paused**\n\nUse 'Resume' to continue."
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("▶️ Resume", callback_data="resume")]])
            )
            await callback.answer("Playback paused")
        else:
            await callback.answer("Already paused!", show_alert=True)
    else:
        await callback.answer("Nothing is playing!", show_alert=True)

@app.on_callback_query(filters.regex(r"^resume$"))
async def resume_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    if chat_id in current_streams:
        if chat_id in paused_streams:
            await pytgcalls.resume_stream(chat_id)
            del paused_streams[chat_id]
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=NOW_PLAYING_IMG,
                    caption="▶️ **Playback Resumed**\n\nEnjoy!"
                ),
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏸ Pause", callback_data="pause")]])
            )
            await callback.answer("Playback resumed")
        else:
            await callback.answer("Not paused!", show_alert=True)
    else:
        await callback.answer("Nothing is playing!", show_alert=True)

@app.on_callback_query(filters.regex(r"^skip$"))
async def skip_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    if chat_id in current_streams:
        await callback.message.edit_media(
            InputMediaPhoto(
                media=NOW_PLAYING_IMG,
                caption="⏭ **Track Skipped**\n\nPlaying next track..."
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 View Queue", callback_data="show_queue")]])
        )
        await play_next(chat_id)
        await callback.answer("Track skipped")
    else:
        await callback.answer("Nothing is playing!", show_alert=True)

@app.on_callback_query(filters.regex(r"^stop$"))
async def stop_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    if chat_id in current_streams:
        await pytgcalls.leave_group_call(chat_id)
        if chat_id in current_streams:
            del current_streams[chat_id]
        if chat_id in queues:
            del queues[chat_id]
        if chat_id in paused_streams:
            del paused_streams[chat_id]
        await callback.message.edit_media(
            InputMediaPhoto(
                media=NOW_PLAYING_IMG,
                caption="⏹ **Playback Stopped**\n\nQueue cleared. Start with /play."
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]])
        )
        await callback.answer("Playback stopped")
    else:
        await callback.answer("Nothing is playing!", show_alert=True)

@app.on_callback_query(filters.regex(r"^show_queue$"))
async def show_queue_callback(_, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in queues and queues[chat_id]:
        queue_text = "📋 **Queue**\n\n"
        for i, track in enumerate(queues[chat_id][:8], start=1):
            duration = await format_duration(track['duration']) if not track.get('is_live') else 'Live'
            title = track['title'][:35] + ("..." if len(track['title']) > 35 else "")
            queue_text += f"{i}. {title} ({duration})\n"
        if len(queues[chat_id]) > 8:
            queue_text += f"\n...and {len(queues[chat_id]) - 8} more tracks"
        await callback.message.edit_media(
            InputMediaPhoto(media=QUEUE_IMG, caption=queue_text),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="show_queue"), InlineKeyboardButton("🗑 Clear Queue", callback_data="clear_queue")],
                [InlineKeyboardButton("🔍 Show More", callback_data="show_more_queue") if len(queues[chat_id]) > 8 else InlineKeyboardButton("🎵 Now Playing", callback_data="now_playing")]
            ])
        )
        await callback.answer("Queue displayed")
    else:
        await callback.message.edit_media(
            InputMediaPhoto(media=QUEUE_IMG, caption="❗ **Queue Empty**\n\nAdd tracks with /play."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]])
        )
        await callback.answer("Queue is empty")

@app.on_callback_query(filters.regex(r"^clear_queue$"))
async def clear_queue_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    chat_id = callback.message.chat.id
    if chat_id in queues:
        queues[chat_id].clear()
        await callback.message.edit_media(
            InputMediaPhoto(media=QUEUE_IMG, caption="🗑 **Queue Cleared**\n\nAdd tracks with /play."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]])
        )
        await callback.answer("Queue cleared")
    else:
        await callback.answer("Queue is already empty!", show_alert=True)

@app.on_callback_query(filters.regex(r"^show_more_queue$"))
async def show_more_queue_callback(_, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in queues and len(queues[chat_id]) > 8:
        queue_text = "📋 **Queue (Extended)**\n\n"
        for i, track in enumerate(queues[chat_id], start=1):
            duration = await format_duration(track['duration']) if not track.get('is_live') else 'Live'
            title = track['title'][:35] + ("..." if len(track['title']) > 35 else "")
            queue_text += f"{i}. {title} ({duration})\n"
        await callback.message.edit_media(
            InputMediaPhoto(media=QUEUE_IMG, caption=queue_text),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="show_queue"), InlineKeyboardButton("🗑 Clear Queue", callback_data="clear_queue")]
            ])
        )
        await callback.answer("Extended queue displayed")
    else:
        await callback.answer("No more tracks to show!", show_alert=True)

@app.on_callback_query(filters.regex(r"^now_playing$"))
async def now_playing_callback(_, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in current_streams:
        track = current_streams[chat_id]
        caption = f"🎵 **Now Playing**\n\n**{track['title'][:35]}{'...' if len(track['title']) > 35 else ''}**\n"
        if track.get('album'):
            caption += f"💿 Album: {track['album']}\n"
        caption += f"⏳ Duration: {'LIVE' if track.get('is_live') else await format_duration(track['duration'])}"
        await callback.message.edit_media(
            InputMediaPhoto(media=track.get('thumbnail', NOW_PLAYING_IMG), caption=caption),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏸ Pause", callback_data="pause"), InlineKeyboardButton("⏭ Skip", callback_data="skip"), InlineKeyboardButton("⏹ Stop", callback_data="stop")],
                [InlineKeyboardButton("📋 Queue", callback_data="show_queue")]
            ])
        )
        await callback.answer("Now playing displayed")
    else:
        await callback.message.edit_media(
            InputMediaPhoto(media=NOW_PLAYING_IMG, caption="❗ **Nothing Playing**\n\nStart with /play."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔍 Search Songs", callback_data="search_menu")]])
        )
        await callback.answer("Nothing is playing")

@app.on_callback_query(filters.regex(r"^more_results$"))
async def more_results_callback(_, callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id in search_results and len(search_results[chat_id]) > 5:
        results = search_results[chat_id][5:10]
        buttons = []
        for i, result in enumerate(results, start=6):
            title = result['title'][:30] + ("..." if len(result['title']) > 30 else "")
            duration = await format_duration(result['duration']) if 'duration' in result else "Unknown"
            callback_data = f"spotify_{result['id']}" if result.get('is_spotify') else f"play_{result['id']}"
            buttons.append([InlineKeyboardButton(f"{i}. {title} ({duration})", callback_data=callback_data)])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="search_menu"), InlineKeyboardButton("❌ Close", callback_data="close_search")])
        await callback.message.edit_media(
            InputMediaPhoto(media=SEARCH_IMG, caption="🔍 **More Search Results**\n\nSelect a track:"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await callback.answer("More results displayed")
    else:
        await callback.answer("No more results!", show_alert=True)

@app.on_callback_query(filters.regex(r"^close_search$"))
async def close_search_callback(_, callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Search closed")

@app.on_callback_query(filters.regex(r"^show_auth_users$"))
async def show_auth_users_callback(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    if not auth_users:
        await callback.message.edit_media(
            InputMediaPhoto(media=AUTH_IMG, caption="❗ **No Authorized Users**\n\nAdd with /auth."),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]])
        )
    else:
        users_list = "\n".join([f"• `{user_id}`" for user_id in auth_users])
        await callback.message.edit_media(
            InputMediaPhoto(media=AUTH_IMG, caption=f"👥 **Authorized Users**\n\n{users_list}"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="show_auth_users")]])
        )
    await callback.answer("Authorized users displayed")
