from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def commands_menu_ui():
    text = """🎵 **Welcome to Music Bot**

Stream music, videos, and live content in Telegram voice chats!

🔍 **Quick Actions:**
• `/play song_name` - Stream music
• `/vplay video_name` - Stream video
• `/live m3u8_url` - Stream live
• `/help` - Full command list

Select an option below:"""
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Commands", callback_data="help_menu"), InlineKeyboardButton("⚙️ System", callback_data="system_menu")],
        [InlineKeyboardButton("👨‍💻 About", callback_data="dev_menu"), InlineKeyboardButton("🔍 Search", callback_data="search_menu")]
    ])
    return text, buttons
