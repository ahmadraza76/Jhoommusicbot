from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ERROR_IMG, HELP_IMG, AUTH_IMG
from client import app, auth_users
from helpers import is_sudo, SUDO_USERS

@app.on_message(filters.command("auth") & filters.private)
async def auth_user(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nOnly sudo users can use this.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if len(message.command) < 2:
        return await message.reply_photo(photo=HELP_IMG, caption="🔍 **Usage**\n\n`/auth user_id`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    try:
        user_id = int(message.command[1])
        if user_id not in auth_users:
            auth_users.append(user_id)
            await message.reply_photo(photo=AUTH_IMG, caption=f"✅ **User Authorized**\n\nUser ID: `{user_id}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 View Authorized", callback_data="show_auth_users")]]))
        else:
            await message.reply_photo(photo=AUTH_IMG, caption=f"ℹ️ **Already Authorized**\n\nUser ID: `{user_id}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 View Authorized", callback_data="show_auth_users")]]))
    except ValueError:
        await message.reply_photo(photo=ERROR_IMG, caption="❌ **Invalid User ID**\n\nProvide a numeric ID.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))

@app.on_message(filters.command("unauth") & filters.private)
async def unauth_user(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nOnly sudo users can use this.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if len(message.command) < 2:
        return await message.reply_photo(photo=HELP_IMG, caption="🔍 **Usage**\n\n`/unauth user_id`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    try:
        user_id = int(message.command[1])
        if user_id in auth_users:
            auth_users.remove(user_id)
            await message.reply_photo(photo=AUTH_IMG, caption=f"✅ **User Unauthorized**\n\nUser ID: `{user_id}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 View Authorized", callback_data="show_auth_users")]]))
        else:
            await message.reply_photo(photo=AUTH_IMG, caption=f"ℹ️ **Not Authorized**\n\nUser ID: `{user_id}` not in list.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 View Authorized", callback_data="show_auth_users")]]))
    except ValueError:
        await message.reply_photo(photo=ERROR_IMG, caption="❌ **Invalid User ID**\n\nProvide a numeric ID.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))

@app.on_message(filters.command("authusers") & filters.private)
async def show_auth_users(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(photo=ERROR_IMG, caption="🚫 **Access Denied**\n\nOnly sudo users can use this.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]]))
    if not auth_users:
        await message.reply_photo(photo=AUTH_IMG, caption="❗ **No Authorized Users**\n\nAdd with `/auth`.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]]))
    else:
        users_list = "\n".join([f"• `{user_id}`" for user_id in auth_users])
        await message.reply_photo(photo=AUTH_IMG, caption=f"👥 **Authorized Users**\n\n{users_list}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Refresh", callback_data="show_auth_users")]]))
</x client.py, helpers.py, config.py, ui_menus.py>

---

#### 7. broadcast_command.py
Implements the new `/broadcast` command for sudo users to send messages to all groups.

<xaiArtifact artifact_id="6dfd15a5-4048-4f36-8596-e6b310bab6b2" artifact_version_id="69e82c86-65a9-40e4-b839-676f7aa036b1" title="broadcast_command.py" contentType="text/python">
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ERROR_IMG, HELP_IMG, logger
from client import app
from helpers import is_sudo, SUDO_USERS

@app.on_message(filters.command("broadcast") & filters.private)
async def broadcast_message(_, message: Message):
    if not await is_sudo(message.from_user.id, auth_users, SUDO_USERS):
        return await message.reply_photo(
            photo=ERROR_IMG,
            caption="🚫 **Access Denied**\n\nOnly sudo users can use this command.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ℹ️ Contact Admin", url="https://t.me/MusicBotUpdates")]])
        )
    if len(message.command) < 2:
        return await message.reply_photo(
            photo=HELP_IMG,
            caption="🔍 **Usage**\n\n`/broadcast message`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📚 Quick Start", callback_data="quick_start")]])
        )
    broadcast_text = " ".join(message.command[1:])
    sent = 0
    failed = 0
    try:
        async for dialog in app.get_dialogs():
            if dialog.chat.type in ['group', 'supergroup']:
                try:
                    await app.send_message(
                        dialog.chat.id,
                        f"📢 **Broadcast Message**\n\n{broadcast_text}\n\n*Visible only to sudo users.*",
                        disable_notification=True
                    )
                    sent += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to {dialog.chat.id}: {e}")
                    failed += 1
        await message.reply_photo(
            photo=HELP_IMG,
            caption=f"📢 **Broadcast Completed**\n\nSent to {sent} groups.\nFailed for {failed} groups.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
        )
    except Exception as e:
        logger.error(f"Broadcast error: {e}")
        await message.reply_photo(
            photo=ERROR_IMG,
            caption=f"❌ **Error**\n\n`{str(e)}`\n\nTry again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry", callback_data="retry_broadcast")]])
        )

@app.on_callback_query(filters.regex(r"^retry_broadcast$"))
async def retry_broadcast(_, callback: CallbackQuery:Is there any code missing from the provided artifacts that would prevent the bot from functioning as intended? If so, please provide the missing code in the appropriate files.

To determine if any code is missing from the provided artifacts that would prevent the music bot from functioning as intended, I’ll carefully analyze the original `music_bot.py` code and compare it with the modularized files provided in the artifacts. The goal is to ensure all functionality, including commands, callback handlers, helper functions, UI/UX components, and the new `/broadcast` command, is fully preserved. I’ll also verify that dependencies between files are correctly maintained and that no critical logic is omitted.

### Analysis of Provided Artifacts

The provided artifacts include:

1. **config.py**: Defines configuration variables, environment settings, image URLs, and command details (including the new broadcast command).
2. **client.py**: Initializes the Pyrogram client, PyTgCalls, Spotify client, and global variables (`current_streams`, `queues`, `paused_streams`, `search_results`, `auth_users`).
3. **helpers.py**: Contains helper functions for searching YouTube/Spotify, extracting track/video info, handling M3U8 streams, formatting durations, and checking sudo status.
4. **playback_commands.py**: Implements playback commands (`/play`, `/vplay`, `/live`).
5. **control_commands.py**: Implements playback control commands (`/pause`, `/resume`, `/skip`, `/stop`, `/queue`).
6. **auth_commands.py**: Implements authorization commands (`/auth`, `/unauth`, `/authusers`).
7. **broadcast_command.py**: Implements the new `/broadcast` command and a `retry_broadcast` callback (though the callback is incomplete).
8. **callback_handlers.py**: Missing in the provided artifacts, but critical as it contains all callback query handlers.
9. **ui_menus.py**: Missing in the provided artifacts, but contains UI/UX components like `commands_menu_ui`.
10. **main.py**: Missing in the provided artifacts, but contains the main execution logic to start the bot.

Additionally, the original code includes:

- The `/start` command handler.
- The `play_next` and `play_spotify_track` helper functions.
- All callback query handlers for UI interactions (e.g., `help_menu`, `system_menu`, `play_selected`, etc.).
- The main execution loop (`main` function and `asyncio.run`).

### Missing Components

After comparing the original code with the provided artifacts, the following components are missing or incomplete:

1. **callback_handlers.py**: The original code contains numerous callback query handlers (e.g., `help_menu`, `system_menu`, `play_selected`, `pause`, etc.), which are not included in any artifact. These are critical for handling inline button interactions.
2. **ui_menus.py**: The `commands_menu_ui` function, which generates the main menu UI, is missing. This is used by the `/start` command and other callbacks.
3. **main.py**: The main execution logic to start the bot and PyTgCalls is missing.
4. **start_command.py**: The `/start` command handler is not included in any artifact.
5. **play_next.py**: The `play_next` function, which handles queue progression, is missing (though referenced in `control_commands.py`).
6. **play_spotify_track.py**: The `play_spotify_track` function, which handles Spotify track playback, is missing (though referenced in `playback_commands.py`).
7. **Incomplete broadcast_command.py**: The `retry_broadcast` callback handler is incomplete in the provided `broadcast_command.py` artifact.
8. **Imports and Dependencies**: Some files reference variables or functions from other modules, but the imports are incomplete or incorrect in `auth_commands.py` (e.g., it incorrectly references `client.py, helpers.py, config.py, ui_menus.py` at the end).
9. **auth_users Initialization**: In `client.py`, `auth_users` is initialized as an empty list (`auth_users: List[int] = []`), but in the original code, it’s initialized with `SUDO_USERS.copy()` to include sudo users by default.
10. **Missing Imports in helpers.py**: The `NOW_PLAYING_IMG` and `LIVE_IMG` constants are used in `extract_info` and `extract_m3u8_info` but not imported from `config.py`.

These missing or incomplete components would prevent the bot from functioning fully, as they include critical UI interactions, bot startup, queue management, Spotify playback, and proper initialization of authorized users.

### Provided Fixes

Below, I’ll provide the missing files and fix the incomplete ones, ensuring all functionality is restored. Each file will be wrapped in an `<xaiArtifact>` tag with a unique UUID, as they are new or corrected artifacts. I’ll also correct the `auth_users` initialization in `client.py` and fix imports in `helpers.py` and `auth_commands.py`.

---

#### 1. Fix client.py (Correct auth_users Initialization)
The `auth_users` list should be initialized with `SUDO_USERS.copy()` to include sudo users by default.

<xaiArtifact artifact_id="bcad6b9f-8d5b-4396-8d72-0fce9ac56caf" artifact_version_id="6bb8bc26-78fb-496e-af54-8423f5326078" title="client.py" contentType="text/python">
from pyrogram import Client
from pytgcalls import PyTgCalls
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from config import API_ID, API_HASH, BOT_TOKEN, FFMPEG_PROCESSES, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SUDO_USERS, logger
from typing import Dict, List

# Initialize bot
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app, cache_duration=100, overload_quiet_mode=True, multi_threading=FFMPEG_PROCESSES > 1)

# Spotify setup
if SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET:
    auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
else:
    sp = None
    logger.warning("Spotify credentials missing. Spotify features disabled.")

# Global variables
current_streams: Dict[int, Dict] = {}
queues: Dict[int, List[Dict]] = {}
paused_streams: Dict[int, bool] = {}
search_results: Dict[int, List[Dict]] = {}
auth_users: List[int] = SUDO_USERS.copy()
