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

# Utility functions from original start.py
async def safe_edit(client, chat_id, message_id, text, reply_markup=None):
    try:
        await client.edit_message_text(chat_id, message_id, text, reply_markup=reply_markup)
    except MessageNotModified:
        pass

async def animated_edit(client, chat_id, message_id, text, reply_markup=None, delay=0.01):
    current_text = ""
    for char in text:
        current_text += char
        try:
            await client.edit_message_text(chat_id, message_id, current_text, reply_markup=reply_markup)
        except MessageNotModified:
            pass
        await asyncio.sleep(delay)

# Video rotation for menu (from new style)
current_menu_video_index = 0
MENU_VIDEOS = [f"VID/menu{i}.mp4" for i in range(1, 11)]

def get_next_menu_video():
    """Get next video in rotation"""
    global current_menu_video_index
    video = MENU_VIDEOS[current_menu_video_index]
    current_menu_video_index = (current_menu_video_index + 1) % len(MENU_VIDEOS)
    return video

async def register_user_logic(user_id, username):
    """Original registration database logic"""
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
    """Send a message when the command /start is issued."""
    # New style layout and buttons
    keyboard = [
        [
            InlineKeyboardButton("Gates ♻️", callback_data="gates"),
            InlineKeyboardButton("Tools 🛠", callback_data="tools"),
        ],
        [
            InlineKeyboardButton("Register 📝", callback_data="register"),
            InlineKeyboardButton("Channel 🥷", url="https://t.me/+mHjmygCKHU5lMjBl"),
        ],
        [
            InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # New style caption
    caption = (
        f"[朱](t.me/amspidr) 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝙘𝙝𝙠\n\n"
        f"[㊄](t.me/amspidr) Migel is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"[╰┈➤](t.me/amspidr) 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 2.6"
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
                reply_markup=reply_markup
            )
    except Exception as e:
        print(f"Error in start command: {e}")
        await message.reply_text(
            caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    """Handle /register command with original logic and new style"""
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    
    is_new, uid, uname = await register_user_logic(user_id, username)
    
    if is_new:
        resp = (
            f"<b>registration module r\n"
            f"<b>> STATUS:</b> SUCCESSFUL\n"
            f"<b>> USER_ID:</b> {uid}\n"
            f"<b>> USERNAME:</b> {uname}\n"
            f"<b>> ACCESS_LEVEL:</b> FREE TIER\n"
            f"<b>> CREDITS_ALLOCATED:</b> 100 UNITS\n\n"
            f"<b>[!] BONUS:</b> 100 CREDITS GRANTED FOR INITIAL REGISTRATION.\n"
            f"<b>[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.</b>"
        )
    else:
        resp = (
            f"<b>[ REGISTRATION PROTOCOL ]</b>\n"
            f"<b>> STATUS:</b> ALREADY REGISTERED\n"
            f"<b>> USER_ID:</b> {uid}\n\n"
            f"<b>[!] MESSAGE:</b> USER PROFILE DETECTED. NO FURTHER REGISTRATION REQUIRED.\n"
            f"<b>[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.</b>"
        )

    keyboard = [[InlineKeyboardButton("Gates ♻️", callback_data="gates")]]
    await message.reply_text(resp, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

@Client.on_callback_query()
async def button_callback(client, callback_query):
    """Handle button callbacks"""
    query = callback_query
    await query.answer()
    
    original_message = (
        f"<a href='https://t.me/amspidr'>朱</a> 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝙘𝙝𝙠\n\n"
        f"<a href='https://t.me/amspidr'>㊄</a> 𝗦𝗸1𝗺𝗺𝗲𝗿 is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"<a href='https://t.me/amspidr'>╰┈➤</a> 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 2.6"
    )
    
    if query.data == "register":
        user_id = str(query.from_user.id)
        username = str(query.from_user.username)
        is_new, uid, uname = await register_user_logic(user_id, username)
        
        if is_new:
            resp = (
                f"<b>[ REGISTRATION PROTOCOL ]</b>\n"
                f"<b>> STATUS:</b> SUCCESSFUL\n"
                f"<b>> USER_ID:</b> {uid}\n"
                f"<b>> USERNAME:</b> {uname}\n"
                f"<b>> ACCESS_LEVEL:</b> FREE TIER\n"
                f"<b>> CREDITS_ALLOCATED:</b> 100 UNITS\n\n"
                f"<b>[!] BONUS:</b> 100 CREDITS GRANTED FOR INITIAL REGISTRATION.\n"
                f"<b>[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.</b>"
            )
        else:
            resp = (
                f"<b>[ REGISTRATION PROTOCOL ]</b>\n"
                f"<b>> STATUS:</b> ALREADY REGISTERED\n"
                f"<b>> USER_ID:</b> {uid}\n\n"
                f"<b>[!] MESSAGE:</b> USER PROFILE DETECTED. NO FURTHER REGISTRATION REQUIRED.\n"
                f"<b>[!] PROCEED TO COMMAND INTERFACE FOR SYSTEM EXPLORATION.</b>"
            )
        
        keyboard = [[InlineKeyboardButton("Back", callback_data="back")]]
        await query.edit_message_caption(caption=resp, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "gates":
        message = (
            "#MigelAktz                                                                                𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝙘𝙝𝙠 -» >_\n\n"
            "║<a href='https://t.me/amspidr'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» 5\n"
            "║<a href='https://t.me/amspidr'>㊡</a>║ 𝙊𝙣 -» 1 ✅\n"
            "║<a href='https://t.me/amspidr'>㊤</a>║ 𝙊𝙛𝙛 -» 4 ❌\n"
            "║<a href='https://t.me/amspidr'>㊬</a> 》𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» 4 ⚠️\n\n"
            "〈<a href='https://t.me/amspidr'>ゼ</a>〉𝙎𝙚𝙡𝙚𝙘𝙩 𝙩𝙝𝙚 𝙩𝙮𝙥𝙚 𝙤𝙛 𝙜𝙖𝙩𝙚 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙛𝙤𝙧 𝙮𝙤𝙪𝙧 𝙪𝙨𝙚!"
        )
        keyboard = [
            [
                InlineKeyboardButton("Auth", callback_data="AUTH"),
                InlineKeyboardButton("Charge", callback_data="CHARGE"),
            ],
            [InlineKeyboardButton("Back", callback_data="back")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    elif query.data == "AUTH":
        message = (
            "〈<a href='https://t.me/amspidr'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝\n\n"
            "〈<a href='https://t.me/amspidr'>朱</a>〉 𝗔𝗱𝘆𝗲𝗻 -» Adyen -» Auth\n"
            "〈<a href='https://t.me/amspidr'>零</a>〉 𝘾𝙢𝙙 -» .ad -» Free\n"
            "〈<a href='https://t.me/amspidr'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    elif query.data == "CHARGE":
        message = (
            "〈<a href='https://t.me/amspidr'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙\n\n"
            "〈<a href='https://t.me/amspidr'>朱</a>〉 𝙉𝙞𝙜𝙝𝙩 -» Moneris -» $0.01\n"
            "〈<a href='https://t.me/amspidr'>零</a>〉 𝘾𝙢𝙙 -» .ni -» Premium \n"
            "〈<a href='https://t.me/amspidr'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="gates")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    elif query.data == "tools":
        message = (
            "〈<a href='https://t.me/amspidr'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙏𝙤𝙤𝙡𝙨 🛠\n\n"
            "<a href='https://t.me/amspidr'>朱</a> 𝘽𝙞𝙣 -» info bin\n"
            "<a href='https://t.me/amspidr'>零</a> 𝘾𝙢𝙙 -» .bin -» Free\n"
            "<a href='https://t.me/amspidr'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=message,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    
    elif query.data == "exit" or query.data == "close":
        await query.message.delete()
    
    elif query.data == "back":
        keyboard = [
            [
                InlineKeyboardButton("Gates ♻️", callback_data="gates"),
                InlineKeyboardButton("Tools 🛠", callback_data="tools"),
            ],
            [
                InlineKeyboardButton("Register 📝", callback_data="register"),
                InlineKeyboardButton("Channel 🥷", url="https://t.me/+mHjmygCKHU5lMjBl"),
            ],
            [
                InlineKeyboardButton("Exit ⚠️", callback_data="exit"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            video_file = "VID/menu1.mp4"
            if os.path.exists(video_file):
                media = InputMediaVideo(media=video_file, caption=original_message, parse_mode=ParseMode.HTML)
                await query.edit_message_media(media=media, reply_markup=reply_markup)
            else:
                await query.edit_message_caption(
                    caption=original_message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup
                )
        except Exception as e:
            print(f"Error in back button: {e}")
            await query.edit_message_caption(
                caption=original_message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

def main():
    """Start the bot folders setup"""
    # Create necessary folders
    folders = ["VID", "Banned", "Maintenance", "HIT", "B3"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Created folder: {folder}")

if __name__ == "__main__":
    main()
