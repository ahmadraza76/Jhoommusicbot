from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import ERROR_IMG, HELP_IMG, AUTH_IMG, SUDO_USERS
from client import app, auth_users
from helpers import is_sudo

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
