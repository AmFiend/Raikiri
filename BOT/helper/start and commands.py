import asyncio
import os
import time
from datetime import datetime, date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageNotModified
import importlib.util
import sys

# Original functionality imports
from FUNC.defs import *
from FUNC.usersdb_func import *

async def safe_edit(client, chat_id, message_id, text, reply_markup=None):
    try:
        await client.edit_message_text(
            chat_id,
            message_id,
            text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except MessageNotModified:
        pass

async def animated_edit(client, chat_id, message_id, text, reply_markup=None, delay=0.01):
    current_text = ""
    for char in text:
        current_text += char
        try:
            await client.edit_message_text(
                chat_id,
                message_id,
                current_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except MessageNotModified:
            pass
        await asyncio.sleep(delay)

current_menu_video_index = 0
MENU_VIDEOS = [f"VID/menu{i}.mp4" for i in range(1, 11)]

def get_next_menu_video():
    global current_menu_video_index
    video = MENU_VIDEOS[current_menu_video_index]
    current_menu_video_index = (current_menu_video_index + 1) % len(MENU_VIDEOS)
    return video

async def register_user_logic(user_id, username):
    antispam_time = int(time.time())
    yy, mm, dd = str(date.today()).split("-")
    reg_at = f"{dd}-{mm}-{yy}"

    find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
    if str(find) == "None":
        info = {
            "id": f"{user_id}",
            "username": f"{username}",
            "user_proxy": "N/A",
            "dcr": "N/A", "dpk": "N/A", "dsk": "N/A", "amt": "N/A",
            "status": "FREE", "plan": "N/A", "expiry": "N/A",
            "credit": "100", "antispam_time": f"{antispam_time}",
            "totalkey": "0", "reg_at": f"{reg_at}",
        }
        usersdb.insert_one(info)
        return True, user_id, username

    return False, user_id, username

@Client.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    keyboard = [
        [
            InlineKeyboardButton("Gates ♻️", callback_data="gates"),
            InlineKeyboardButton("Tools 🛠", callback_data="tools"),
            InlineKeyboardButton("Helper 🫥", callback_data="helper"),
        ],
        [
            InlineKeyboardButton("Register 📝", callback_data="register"),
            InlineKeyboardButton("Channel 🥷", url="https://t.me/migeldumps"),
        ],
        [
            InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"[朱](https://t.me/elitechkbot?start=start) 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙈𝙞𝙜𝙚𝙡 𝘾𝙝𝙚𝙘𝙠𝙚𝙧\n\n"
        f"[㊄](https://t.me/elitechkbot?start=start) Migel is renewed, fast and secure checks.\n\n"
        f"[╰┈➤](https://t.me/elitechkbot?start=start) 𝙑𝙚𝙧𝙨𝙞𝙤𝙣 -» 1.0"
    )

    try:
        video_file = get_next_menu_video()
        if os.path.exists(video_file):
            await message.reply_video(
                video=video_file,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            await message.reply_text(
                caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(e)

@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)

    is_new, uid, uname = await register_user_logic(user_id, username)

    if is_new:
        resp = f"<b>REGISTERED SUCCESSFULLY</b>\nUSER: {uid}"
    else:
        resp = f"<b>ALREADY REGISTERED</b>\nUSER: {uid}"

    keyboard = [[InlineKeyboardButton("Gates ♻️", callback_data="gates")]]
    await message.reply_text(resp, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

@Client.on_callback_query()
async def button_callback(client, query):
    await query.answer()

    if query.data == "tools":
        message = "TOOLS MENU"
        keyboard = [
            [InlineKeyboardButton("Back", callback_data="back")],
            [InlineKeyboardButton("NEXT", callback_data="tools2")]
        ]
        await query.edit_message_caption(caption=message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "tools2":
        message = "MORE TOOLS"
        keyboard = [
            [InlineKeyboardButton("◀️ Back", callback_data="tools")],
            [InlineKeyboardButton("Main Menu", callback_data="start")]
        ]
        await query.edit_message_caption(caption=message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "helper":
        message = "HELPER MENU"
        keyboard = [[InlineKeyboardButton("Home", callback_data="start")]]
        await query.edit_message_caption(caption=message, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "exit":
        await query.message.delete()

    elif query.data == "back":
        keyboard = [[InlineKeyboardButton("Gates ♻️", callback_data="gates")]]
        await query.edit_message_caption(caption="MAIN MENU", reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    folders = ["VID", "Banned", "Maintenance", "HIT", "B3"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

if __name__ == "__main__":
    main()
