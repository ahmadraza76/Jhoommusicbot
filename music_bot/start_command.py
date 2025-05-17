from pyrogram import Client, filters
from pyrogram.types import Message
from config import MAIN_MENU_IMG
from client import app
from ui_menus import commands_menu_ui

@app.on_message(filters.command("start"))
async def start_command(_, message: Message):
    text, buttons = await commands_menu_ui()
    await message.reply_photo(photo=MAIN_MENU_IMG, caption=text, reply_markup=buttons)
