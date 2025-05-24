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
async def show_auth_users(_, message: Message

---

#### 4. Fix broadcast_command.py (Complete retry_broadcast)
Complete the `retry_broadcast` callback handler to prompt the user to retry the broadcast.

<xaiArtifact artifact_id="e1e8fa42-5aef-4189-8a6e-d728efa67084" artifact_version_id="a502ad4c-38a6-4bb0-8879-67ddfcf6cabc" title="broadcast_command.py" contentType="text/python">
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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
async def retry_broadcast(_, callback: CallbackQuery):
    if not await is_sudo(callback.from_user.id, auth_users, SUDO_USERS):
        await callback.answer("🚫 You don't have permission!", show_alert=True)
        return
    await callback.message.edit_media(
        InputMediaPhoto(
            media=HELP_IMG,
            caption="🔍 **Retry Broadcast**\n\nUse `/broadcast message` to try again."
        ),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]])
    )
    await callback.answer("Retry broadcast prompted")
