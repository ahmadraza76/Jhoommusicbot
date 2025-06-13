from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from config import ERROR_IMG, HELP_IMG, logger
from client import app, auth_users
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
                        f"📢 **Broadcast Message**\n\n{broadcast_text}\n\n*From Music Bot Admin*",
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