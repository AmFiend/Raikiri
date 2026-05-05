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
import json
import requests

# --- COLORED BUTTONS BRIDGE ---
original_init = InlineKeyboardButton.__init__
def patched_init(self, text, callback_data=None, url=None, web_app=None, login_url=None, 
                 user_id=None, switch_inline_query=None, switch_inline_query_current_chat=None, 
                 callback_game=None, style=None):
    original_init(self, text, callback_data, url, web_app, login_url, 
                  user_id, switch_inline_query, switch_inline_query_current_chat, 
                  callback_game)
    self.style = style
InlineKeyboardButton.__init__ = patched_init

async def send_colored_msg(client, chat_id, text, reply_markup=None, is_edit=False, message_id=None, parse_mode="HTML", is_video=False):
    bot_token = getattr(client, "bot_token", None)
    if not bot_token:
        if is_edit:
            if is_video: return await client.edit_message_caption(chat_id, message_id, text, reply_markup=reply_markup)
            return await client.edit_message_text(chat_id, message_id, text, reply_markup=reply_markup)
        return await client.send_message(chat_id, text, reply_markup=reply_markup)
    method = "editMessageCaption" if (is_edit and is_video) else ("editMessageText" if is_edit else "sendMessage")
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    payload = {"chat_id": chat_id, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if is_video or method == "editMessageCaption": payload["caption"] = text
    else: payload["text"] = text
    if is_edit: payload["message_id"] = message_id
    if reply_markup:
        keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for btn in row:
                b_dict = {"text": btn.text}
                if hasattr(btn, "callback_data") and btn.callback_data: b_dict["callback_data"] = btn.callback_data
                if hasattr(btn, "url") and btn.url: b_dict["url"] = btn.url
                if hasattr(btn, "style") and btn.style: b_dict["style"] = btn.style
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())

async def send_colored_video(client, chat_id, video, caption, reply_markup=None):
    bot_token = getattr(client, "bot_token", None)
    if not bot_token: return await client.send_video(chat_id, video, caption=caption, reply_markup=reply_markup)
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    payload = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
    files = None
    if os.path.exists(str(video)): files = {"video": open(video, "rb")}
    else: payload["video"] = video
    if reply_markup:
        keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for btn in row:
                b_dict = {"text": btn.text}
                if hasattr(btn, "callback_data") and btn.callback_data: b_dict["callback_data"] = btn.callback_data
                if hasattr(btn, "url") and btn.url: b_dict["url"] = btn.url
                if hasattr(btn, "style") and btn.style: b_dict["style"] = btn.style
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    loop = asyncio.get_event_loop()
    if files: return await loop.run_in_executor(None, lambda: requests.post(url, data=payload, files=files).json())
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())
# ------------------------------

# Original functionality imports
from FUNC.defs import *
from FUNC.usersdb_func import *


async def safe_edit(client, chat_id, message_id, text, reply_markup=None):
    await send_colored_msg(client, chat_id, text, reply_markup=reply_markup, is_edit=True, message_id=message_id, is_video=True)


async def animated_edit(client, chat_id, message_id, text, reply_markup=None, delay=0.01):
    # Removed delay logic as requested, just performs the edit
    await send_colored_msg(client, chat_id, text, reply_markup=reply_markup, is_edit=True, message_id=message_id, is_video=True)


current_menu_video_index = 0
MENU_VIDEOS = [f"VID/menu{i}.mp4" for i in range(1, 11)]
VIDEO_FILE_IDS = {} # This will be loaded from a file


VIDEO_CACHE_FILE = 'video_cache.json'

def load_video_cache():
    global VIDEO_FILE_IDS
    if os.path.exists(VIDEO_CACHE_FILE):
        try:
            with open(VIDEO_CACHE_FILE, 'r') as f:
                VIDEO_FILE_IDS = json.load(f)
        except Exception as e:
            print(f"Error loading video cache: {e}")

def save_video_cache():
    try:
        with open(VIDEO_CACHE_FILE, 'w') as f:
            json.dump(VIDEO_FILE_IDS, f)
    except Exception as e:
        print(f"Error saving video cache: {e}")

# Load cache on startup
load_video_cache()

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
    """Send a message when the command /start is issued."""
    first_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    user_status = find["status"] if find and find.get("status") else "FREE"
    credit = find["credit"] if find and find.get("credit") else "0"

    keyboard = [
        [
            InlineKeyboardButton("✧ ɢᴀᴛᴇꜱ ✧", callback_data="gates", style="primary"),
            InlineKeyboardButton("◈ ʀᴇɢɪꜱᴛᴇʀ ◈", callback_data="register", style="success"),
        ],
        [
            InlineKeyboardButton("✧ ᴛᴏᴏʟꜱ ✧", callback_data="tools", style="primary"),
            InlineKeyboardButton("◈ ʜᴇʟᴘᴇʀ ◈", callback_data="helper", style="primary"),
        ],
        [
            InlineKeyboardButton("✧ ᴇxɪᴛ ✧", callback_data="exit", style="danger"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"[✧](https://t.me/elitechkbot?start=start) ꜱᴘʏᴅᴇ ᴄʜᴋ ✧\n\n"
        f"◈ ɴᴀᴍᴇ : {first_name}\n"
        f"◈ ꜱᴛᴀᴛᴜꜱ : {user_status}\n"
        f"◈ ᴄʀᴇᴅɪᴛꜱ : {credit}\n\n"
        f"Speed unmatched. Security reinforced.\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"[↪](https://t.me/elitechkbot?start=start) ꜱᴛᴀʀᴛ : /start\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        video_file = get_next_menu_video()
        video_source = VIDEO_FILE_IDS.get(video_file, video_file)
        resp = await send_colored_video(client, message.chat.id, video_source, caption, reply_markup=reply_markup)
        if resp and resp.get("ok") and "video" in resp["result"]:
            file_id = resp["result"]["video"]["file_id"]
            if video_file not in VIDEO_FILE_IDS:
                VIDEO_FILE_IDS[video_file] = file_id
                save_video_cache()
    except Exception as e:
        print(f"Error in start command: {e}")
        await send_colored_msg(client, message.chat.id, caption, reply_markup=reply_markup, parse_mode="Markdown")


@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    """Handle /register command with original logic and new style"""
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)

    is_new, uid, uname = await register_user_logic(user_id, username)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    credit = find["credit"] if find and find.get("credit") else "100"

    if is_new:
        resp = (
            f"<a href='https://t.me/elitechkbot?start=start'>✧ ꜱᴘʏᴅᴇ ᴄʜᴋ ✧</a>\n\n"
            f"<b>◈ ꜱᴛᴀᴛᴜꜱ :</b> ʀᴇɢɪꜱᴛᴇʀᴇᴅ ✓\n"
            f"<b>◈ ᴜꜱᴇʀ :</b> {uname}\n"
            f"<b>◈ ɪᴅ :</b> {uid}\n"
            f"<b>◈ ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>↪ ꜱᴛᴀʀᴛ :</b> /start"
        )
    else:
        resp = (
            f"<a href='https://t.me/elitechkbot?start=start'>✧ ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ✧</a>\n\n"
            f"<b>◈ ꜱᴛᴀᴛᴜꜱ :</b> ᴀᴄᴛɪᴠᴇ\n"
            f"<b>◈ ɪᴅ :</b> {uid}\n"
            f"<b>◈ ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>↪ ᴘʀᴏᴄᴇᴇᴅ.</b>"
        )

    keyboard = [[InlineKeyboardButton("✧ ɢᴀᴛᴇꜱ ✧", callback_data="gates", style="success")]]
    await send_colored_msg(client, message.chat.id, resp, reply_markup=InlineKeyboardMarkup(keyboard))


@Client.on_callback_query()
async def button_callback(client, callback_query):
    """Handle button callbacks"""
    query = callback_query
    await query.answer()

    first_name = query.from_user.first_name
    uid_q = str(query.from_user.id)
    find_q = usersdb.find_one({"id": uid_q}, {"_id": 0})
    user_status_q = find_q["status"] if find_q and find_q.get("status") else "FREE"
    credit = find_q["credit"] if find_q and find_q.get("credit") else "0"
    plan = find_q["plan"] if find_q and find_q.get("plan") else "N/A"

    original_message = (
        f"[✧](https://t.me/elitechkbot?start=start) ꜱᴘʏᴅᴇ ᴄʜᴋ ✧\n\n"
        f"◈ ɴᴀᴍᴇ : {first_name}\n"
        f"◈ ꜱᴛᴀᴛᴜꜱ : {user_status_q}\n"
        f"◈ ᴄʀᴇᴅɪᴛꜱ : {credit}\n\n"
        f"Speed unmatched. Security reinforced.\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"[↪](https://t.me/elitechkbot?start=start) ꜱᴛᴀʀᴛ : /start\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    if query.data == "register":
        user_id = str(query.from_user.id)
        username = str(query.from_user.username)
        is_new, uid, uname = await register_user_logic(user_id, username)

        if is_new:
            resp = (
                f"<a href='https://t.me/elitechkbot?start=start'>✧ ꜱᴘʏᴅᴇ ᴄʜᴋ ✧</a>\n\n"
                f"<b>◈ ꜱᴛᴀᴛᴜꜱ :</b> ʀᴇɢɪꜱᴛᴇʀᴇᴅ ✓\n"
                f"<b>◈ ᴜꜱᴇʀ :</b> {uname}\n"
                f"<b>◈ ɪᴅ :</b> {uid}\n"
                f"<b>◈ ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>↪ ꜱᴛᴀʀᴛ :</b> /start"
            )
        else:
            resp = (
                f"<a href='https://t.me/elitechkbot?start=start'>✧ ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ✧</a>\n\n"
                f"<b>◈ ꜱᴛᴀᴛᴜꜱ :</b> ᴀᴄᴛɪᴠᴇ\n"
                f"<b>◈ ɪᴅ :</b> {uid}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"<b>↪ ᴘʀᴏᴄᴇᴇᴅ.</b>"
            )

        keyboard = [[InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="back", style="danger")]]
        await send_colored_msg(client, query.message.chat.id, resp, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "gates":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ɢᴀᴛᴇᴡᴀʏꜱ</b> ✧\n\n"
            "◈ <a href='https://t.me/elitechkbot?start=start'>ᴛᴏᴛᴀʟ</a> : 3\n"
            "◈ <a href='https://t.me/elitechkbot?start=start'>ᴏɴ</a> : 3 ✓\n"
            "◈ <a href='https://t.me/elitechkbot?start=start'>ᴏꜰꜰ</a> : 0 ✗\n"
            "◈ <a href='https://t.me/elitechkbot?start=start'>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</a> : 0\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "<a href='https://t.me/elitechkbot?start=start'>↪</a> ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ᴛʏᴘᴇ ᴏꜰ ɢᴀᴛᴇ ꜰᴏʀ ʏᴏᴜʀ ᴜꜱᴇ\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [
            [
                InlineKeyboardButton("◈ ᴀᴜᴛʜ ◈", callback_data="AUTH", style="primary"),
                InlineKeyboardButton("◈ ᴄʜᴀʀɢᴇ ◈", callback_data="CHARGE", style="success"),
                InlineKeyboardButton("◈ ᴍᴀꜱꜱ ◈", callback_data="MASS", style="primary"),
            ],
            [InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="back", style="danger")]
        ]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "AUTH":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ɢᴀᴛᴇᴡᴀʏꜱ ━ ᴀᴜᴛʜ</b> ✧\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Square Auth\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /sq\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [[InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="gates", style="danger")]]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "CHARGE":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ɢᴀᴛᴇᴡᴀʏꜱ ━ ᴄʜᴀʀɢᴇ</b> ✧ (1/2)\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : PayPal charge 2$\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /pp\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Auto Shopify\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /sh\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [
            [InlineKeyboardButton("◈ ᴘᴀɢᴇ 2 ➡ ◈", callback_data="CHARGE_PAGE2", style="primary")],
            [InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="gates", style="danger")]
        ]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "CHARGE_PAGE2":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ɢᴀᴛᴇᴡᴀʏꜱ ━ ᴄʜᴀʀɢᴇ</b> ✧ (2/2)\n\n"
            "soon 🔜\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [
            [InlineKeyboardButton("◈ ⬅ ᴘᴀɢᴇ 1 ◈", callback_data="CHARGE", style="primary")],
            [InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="gates", style="danger")]
        ]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "MASS":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ɢᴀᴛᴇᴡᴀʏꜱ ━ ᴍᴀꜱꜱ</b> ✧\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : PayPal Mass\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /mpp\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Shopify Mass\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /msh\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [[InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="gates", style="danger")]]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "tools":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴛᴏᴏʟꜱ</b> ✧\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Generate CC\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /gen -xxxx\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Info Bin\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /bin\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Filter CC\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /fl\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Fake Location\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /fake\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Claim Credits\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /claim\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Fetch IP\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /ip\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Sort CC\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /sort\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [
            [InlineKeyboardButton("✧ ʙᴀᴄᴋ ✧", callback_data="back", style="danger")],
            [InlineKeyboardButton("◈ ɴᴇxᴛ ◈", callback_data="tools2", style="primary")]
        ]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "tools2":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴛᴏᴏʟꜱ</b> ✧ ᴘ.2\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Redeem Keys\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /claim key-xxxx\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Get ID\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /id\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Membership Info\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /plan\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Group Membership\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /plang\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [
            [InlineKeyboardButton("◈ ⬅ ʙᴀᴄᴋ ◈", callback_data="tools", style="primary")],
            [InlineKeyboardButton("✧ ᴍᴇɴᴜ ✧", callback_data="back", style="danger")]
        ]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "helper":
        message = (
            "<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ʜᴇʟᴘᴇʀ</b> ✧\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Buy Premium\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /buy\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Credits\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /howcrd\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : Check Credits\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /credits\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ɴᴀᴍᴇ : How To Add Bot\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ᴄᴍᴅ  : /howgp\n"
            "<a href='https://t.me/elitechkbot?start=start'>◈</a> ꜱᴛᴀᴛᴜꜱ : ᴏɴ ✓\n\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = [[InlineKeyboardButton("✧ ʜᴏᴍᴇ ✧", callback_data="back", style="danger")]]
        await send_colored_msg(client, query.message.chat.id, message, reply_markup=InlineKeyboardMarkup(keyboard), is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "exit" or query.data == "close":
        await query.message.delete()

    elif query.data == "back":
        keyboard = [
        [
            InlineKeyboardButton("✧ ɢᴀᴛᴇꜱ ✧", callback_data="gates", style="primary"),
            InlineKeyboardButton("◈ ʀᴇɢɪꜱᴛᴇʀ ◈", callback_data="register", style="success"),
        ],
        [
            InlineKeyboardButton("✧ ᴛᴏᴏʟꜱ ✧", callback_data="tools", style="primary"),
            InlineKeyboardButton("◈ ʜᴇʟᴘᴇʀ ◈", callback_data="helper", style="primary"),
        ],
        [
            InlineKeyboardButton("✧ ᴇxɪᴛ ✧", callback_data="exit", style="danger"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        try:
            video_file = "VID/menu1.mp4"
            if video_file in VIDEO_FILE_IDS:
                media = InputMediaVideo(media=VIDEO_FILE_IDS[video_file], caption=original_message, parse_mode=ParseMode.MARKDOWN)
                await query.edit_message_media(media=media, reply_markup=reply_markup)
            elif os.path.exists(video_file) and os.path.getsize(video_file) > 0:
                media = InputMediaVideo(media=video_file, caption=original_message, parse_mode=ParseMode.MARKDOWN)
                await query.edit_message_media(media=media, reply_markup=reply_markup)
            else:
                await send_colored_msg(client, query.message.chat.id, original_message, reply_markup=reply_markup, is_edit=True, message_id=query.message.id, is_video=True, parse_mode="Markdown")
        except Exception as e:
            print(f"Error in back button: {e}")
            await send_colored_msg(client, query.message.chat.id, original_message, reply_markup=reply_markup, is_edit=True, message_id=query.message.id, is_video=True, parse_mode="Markdown")


def main():
    """Start the bot folders setup"""
    folders = ["VID", "Banned", "Maintenance", "HIT", "B3"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")


if __name__ == "__main__":
    main()
