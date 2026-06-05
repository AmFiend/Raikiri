import asyncio
import os
import time
from datetime import datetime, date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from pyrogram.enums import ParseMode
import importlib.util
import sys
import json
import requests

# ----------------------------- PREMIUM EMOJI MAPPING -----------------------------
# Dictionary of Custom Emoji IDs for buttons
EMOJI_IDS = {
    "GATES": "5042328396193864923",
    "REGISTER": "6235253239080555488",
    "TOOLS": "5042302287087666158",
    "HELPER": "6237585380552480043",
    "EXIT": "5042112436648281096",
    "BACK": "5042102141611672423",
    "NEXT": "5039753786638205957",
    "HOME": "5895702479097564641",
    "AUTH": "5039727497143387500",
    "CHARGE": "5447319442562251569",
    "MASS": "5402258956385024488",
    "TXT": "5039600026809009149",
    "STAR": "5895702479097564641",
    "GHOST": "5197219760294614064"
}

# Message Text Tags (for captions)
GATES_MSG    = f'<tg-emoji emoji-id="{EMOJI_IDS["GATES"]}">🛡️</tg-emoji>'
REGISTER_MSG = f'<tg-emoji emoji-id="{EMOJI_IDS["REGISTER"]}">✅</tg-emoji>'
TOOLS_MSG    = f'<tg-emoji emoji-id="{EMOJI_IDS["TOOLS"]}">🔮</tg-emoji>'
HELPER_MSG   = f'<tg-emoji emoji-id="{EMOJI_IDS["HELPER"]}">🦁</tg-emoji>'
EXIT_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["EXIT"]}">❌</tg-emoji>'
BACK_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["BACK"]}">🔝</tg-emoji>'
NEXT_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["NEXT"]}">▶️</tg-emoji>'
HOME_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["HOME"]}">⭐</tg-emoji>'
AUTH_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["AUTH"]}">👑</tg-emoji>'
CHARGE_MSG   = f'<tg-emoji emoji-id="{EMOJI_IDS["CHARGE"]}">🛒</tg-emoji>'
MASS_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["MASS"]}">🌋</tg-emoji>'
TXT_MSG      = f'<tg-emoji emoji-id="{EMOJI_IDS["TXT"]}">📌</tg-emoji>'
STAR_MSG     = f'<tg-emoji emoji-id="{EMOJI_IDS["STAR"]}">⭐</tg-emoji>'

# Other message-only emojis
ONLINE_MSG   = '<tg-emoji emoji-id="5278426871623602220">📱</tg-emoji>'
OFFLINE_MSG  = '<tg-emoji emoji-id="5280734694990699216">✔️</tg-emoji>'
TOTAL_MSG    = '<tg-emoji emoji-id="5042050649248760772">💎</tg-emoji>'
MAINT_MSG    = '<tg-emoji emoji-id="5447453226498552490">💳</tg-emoji>'
BULLET_MSG   = '<tg-emoji emoji-id="5447602197439218445">🌐</tg-emoji>'
LINK_MSG     = '<tg-emoji emoji-id="5042101437237036298">🔗</tg-emoji>'
CREDIT_MSG   = '<tg-emoji emoji-id="6235445786759402354">💸</tg-emoji>'
THUMBS_MSG   = '<tg-emoji emoji-id="5042022607407285100">👍</tg-emoji>'
LIGHT_MSG    = '<tg-emoji emoji-id="5041790387115524994">💡</tg-emoji>'
POINT_MSG    = '<tg-emoji emoji-id="5042156073516008537">👈</tg-emoji>'

# ----------------------------- COLORED BUTTONS & CUSTOM EMOJI BRIDGE -----------------------------
original_init = InlineKeyboardButton.__init__
def patched_init(self, text, callback_data=None, url=None, web_app=None, login_url=None,
                 user_id=None, switch_inline_query=None, switch_inline_query_current_chat=None,
                 callback_game=None, style=None, icon_custom_emoji_id=None):
    original_init(self, text, callback_data, url, web_app, login_url,
                  user_id, switch_inline_query, switch_inline_query_current_chat,
                  callback_game)
    self.style = style
    self.icon_custom_emoji_id = icon_custom_emoji_id
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
                if hasattr(btn, "icon_custom_emoji_id") and btn.icon_custom_emoji_id:
                    b_dict["icon_custom_emoji_id"] = btn.icon_custom_emoji_id
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = {"inline_keyboard": keyboard}
        
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())

async def send_colored_video(client, chat_id, video, caption, reply_markup=None):
    bot_token = getattr(client, "bot_token", None)
    if not bot_token:
        return await client.send_video(chat_id, video, caption=caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    payload = {"chat_id": chat_id, "caption": caption, "parse_mode": "HTML"}
    files = None
    if os.path.exists(str(video)):
        files = {"video": open(video, "rb")}
    else:
        payload["video"] = video
        
    if reply_markup:
        keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for btn in row:
                b_dict = {"text": btn.text}
                if hasattr(btn, "callback_data") and btn.callback_data: b_dict["callback_data"] = btn.callback_data
                if hasattr(btn, "url") and btn.url: b_dict["url"] = btn.url
                if hasattr(btn, "style") and btn.style: b_dict["style"] = btn.style
                if hasattr(btn, "icon_custom_emoji_id") and btn.icon_custom_emoji_id:
                    b_dict["icon_custom_emoji_id"] = btn.icon_custom_emoji_id
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
        
    loop = asyncio.get_event_loop()
    if files:
        return await loop.run_in_executor(None, lambda: requests.post(url, data=payload, files=files).json())
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())

# ------------------------------
from FUNC.defs import *
from FUNC.usersdb_func import *

async def safe_edit(client, chat_id, message_id, text, reply_markup=None):
    await send_colored_msg(client, chat_id, text, reply_markup=reply_markup, is_edit=True, message_id=message_id, is_video=True)

async def animated_edit(client, chat_id, message_id, text, reply_markup=None, delay=0.01):
    await send_colored_msg(client, chat_id, text, reply_markup=reply_markup, is_edit=True, message_id=message_id, is_video=True)

current_menu_video_index = 0
MENU_VIDEOS = [f"VID/menu{i}.mp4" for i in range(1, 11)]
VIDEO_FILE_IDS = {}
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

# ----------------------------- BOT COMMANDS -----------------------------
@Client.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    first_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    user_status = find["status"] if find and find.get("status") else "FREE"
    credit = find["credit"] if find and find.get("credit") else "0"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ɢᴀᴛᴇꜱ", callback_data="gates", style="primary", icon_custom_emoji_id=EMOJI_IDS["GATES"]),
         InlineKeyboardButton("ʀᴇɢɪꜱᴛᴇʀ", callback_data="register", style="success", icon_custom_emoji_id=EMOJI_IDS["REGISTER"])],
        [InlineKeyboardButton("ᴛᴏᴏʟꜱ", callback_data="tools", style="primary", icon_custom_emoji_id=EMOJI_IDS["TOOLS"]),
         InlineKeyboardButton("ʜᴇʟᴘᴇʀ", callback_data="helper", style="primary", icon_custom_emoji_id=EMOJI_IDS["HELPER"])],
        [InlineKeyboardButton("ᴇxɪᴛ", callback_data="exit", style="danger", icon_custom_emoji_id=EMOJI_IDS["EXIT"])]
    ])

    caption = (
        f"{STAR_MSG} <b>ꜱᴘʏᴅᴇ ᴄʜᴋ</b> {STAR_MSG}\n\n"
        f"{BULLET_MSG} <b>ɴᴀᴍᴇ :</b> {first_name}\n"
        f"{BULLET_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> {user_status}\n"
        f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
        f"{LIGHT_MSG} <i>Speed unmatched. Security reinforced.</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{LINK_MSG} <b>ꜱᴛᴀʀᴛ :</b> /start\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        video_file = get_next_menu_video()
        video_source = VIDEO_FILE_IDS.get(video_file, video_file)
        resp = await send_colored_video(client, message.chat.id, video_source, caption, keyboard)
        if resp and resp.get("ok") and "video" in resp["result"]:
            file_id = resp["result"]["video"]["file_id"]
            if video_file not in VIDEO_FILE_IDS:
                VIDEO_FILE_IDS[video_file] = file_id
                save_video_cache()
    except Exception as e:
        print(f"Start error: {e}")
        await send_colored_msg(client, message.chat.id, caption, reply_markup=keyboard)

@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    is_new, uid, uname = await register_user_logic(user_id, username)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    credit = find["credit"] if find and find.get("credit") else "100"

    if is_new:
        resp = (
            f"{STAR_MSG} <b>ꜱᴘʏᴅᴇ ᴄʜᴋ – ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ</b> {STAR_MSG}\n\n"
            f"{THUMBS_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> ʀᴇɢɪꜱᴛᴇʀᴇᴅ\n"
            f"{BULLET_MSG} <b>ᴜꜱᴇʀ :</b> {uname}\n"
            f"{TOTAL_MSG} <b>ɪᴅ :</b> {uid}\n"
            f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{LINK_MSG} <b>ꜱᴛᴀʀᴛ :</b> /start"
        )
    else:
        resp = (
            f"{STAR_MSG} <b>ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> {STAR_MSG}\n\n"
            f"{ONLINE_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> ᴀᴄᴛɪᴠᴇ\n"
            f"{TOTAL_MSG} <b>ɪᴅ :</b> {uid}\n"
            f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{NEXT_MSG} <b>ᴘʀᴏᴄᴇᴇᴅ.</b>"
        )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ɢᴀᴛᴇꜱ", callback_data="gates", style="success", icon_custom_emoji_id=EMOJI_IDS["GATES"])]])
    await send_colored_msg(client, message.chat.id, resp, reply_markup=keyboard)

@Client.on_callback_query()
async def button_callback(client, callback_query):
    query = callback_query
    await query.answer()

    first_name = query.from_user.first_name
    uid_q = str(query.from_user.id)
    find_q = usersdb.find_one({"id": uid_q}, {"_id": 0})
    user_status_q = find_q["status"] if find_q and find_q.get("status") else "FREE"
    credit = find_q["credit"] if find_q and find_q.get("credit") else "0"

    original_message_caption = (
        f"{STAR_MSG} <b>ꜱᴘʏᴅᴇ ᴄʜᴋ</b> {STAR_MSG}\n\n"
        f"{BULLET_MSG} <b>ɴᴀᴍᴇ :</b> {first_name}\n"
        f"{BULLET_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> {user_status_q}\n"
        f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
        f"{LIGHT_MSG} <i>Speed unmatched. Security reinforced.</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{LINK_MSG} <b>ꜱᴛᴀʀᴛ :</b> /start\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    if query.data == "register":
        user_id = str(query.from_user.id)
        username = str(query.from_user.username)
        is_new, uid, uname = await register_user_logic(user_id, username)
        if is_new:
            resp = (
                f"{STAR_MSG} <b>ꜱᴘʏᴅᴇ ᴄʜᴋ – ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ</b> {STAR_MSG}\n\n"
                f"{THUMBS_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> ʀᴇɢɪꜱᴛᴇʀᴇᴅ\n"
                f"{BULLET_MSG} <b>ᴜꜱᴇʀ :</b> {uname}\n"
                f"{TOTAL_MSG} <b>ɪᴅ :</b> {uid}\n"
                f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{LINK_MSG} <b>ꜱᴛᴀʀᴛ :</b> /start"
            )
        else:
            resp = (
                f"{STAR_MSG} <b>ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> {STAR_MSG}\n\n"
                f"{ONLINE_MSG} <b>ꜱᴛᴀᴛᴜꜱ :</b> ᴀᴄᴛɪᴠᴇ\n"
                f"{TOTAL_MSG} <b>ɪᴅ :</b> {uid}\n"
                f"{CREDIT_MSG} <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"{NEXT_MSG} <b>ᴘʀᴏᴄᴇᴇᴅ.</b>"
            )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]])
        await send_colored_msg(client, query.message.chat.id, resp, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "gates":
        msg = (
            f"{GATES_MSG} <b>ꜱᴘʏᴅᴇ – ɢᴀᴛᴇᴡᴀʏꜱ</b> {GATES_MSG}\n\n"
            f"{TOTAL_MSG} <b>ᴛᴏᴛᴀʟ :</b> 10\n"
            f"{ONLINE_MSG} <b>ᴏɴ :</b> 10\n"
            f"{OFFLINE_MSG} <b>ᴏꜰꜰ :</b> 0\n"
            f"{MAINT_MSG} <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ :</b> 1\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{POINT_MSG} ꜱᴇʟᴇᴄᴛ ᴛʜᴇ ᴛʏᴘᴇ ᴏꜰ ɢᴀᴛᴇ\n"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴀᴜᴛʜ", callback_data="AUTH", style="primary", icon_custom_emoji_id=EMOJI_IDS["AUTH"]),
             InlineKeyboardButton("ᴄʜᴀʀɢᴇ", callback_data="CHARGE", style="success", icon_custom_emoji_id=EMOJI_IDS["CHARGE"]),
             InlineKeyboardButton("ᴍᴀꜱꜱ", callback_data="MASS", style="primary", icon_custom_emoji_id=EMOJI_IDS["MASS"])],
            [InlineKeyboardButton("ᴛxᴛ", callback_data="TXT", style="primary", icon_custom_emoji_id=EMOJI_IDS["TXT"])],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "AUTH":
        msg = (
            f"{AUTH_MSG} <b>ɢᴀᴛᴇᴡᴀʏꜱ – ᴀᴜᴛʜ</b> {AUTH_MSG}\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth $0\n{LINK_MSG} ᴄᴍᴅ : /sa\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth (alt)\n{LINK_MSG} ᴄᴍᴅ : /au\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : 3DS Lookup\n{LINK_MSG} ᴄᴍᴅ : /vbv\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="gates", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "CHARGE":
        msg = (
            f"{CHARGE_MSG} <b>ɢᴀᴛᴇᴡᴀʏꜱ – ᴄʜᴀʀɢᴇ</b> {CHARGE_MSG} (1/2)\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Adyen Charge 1$\n{LINK_MSG} ᴄᴍᴅ : /Charge\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Square charge 2$\n{LINK_MSG} ᴄᴍᴅ : /sq\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Shopify Payments\n{LINK_MSG} ᴄᴍᴅ : /sh\n{MAINT_MSG} ꜱᴛᴀᴛᴜꜱ : Maintenance 🔧\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Charge 9$\n{LINK_MSG} ᴄᴍᴅ : /st9\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : HiBurma 1£\n{LINK_MSG} ᴄᴍᴅ : /hb\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe charge 2$\n{LINK_MSG} ᴄᴍᴅ : /bf\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴘᴀɢᴇ 2", callback_data="CHARGE_PAGE2", style="primary", icon_custom_emoji_id=EMOJI_IDS["NEXT"])],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="gates", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "CHARGE_PAGE2":
        msg = (
            f"{CHARGE_MSG} <b>ɢᴀᴛᴇᴡᴀʏꜱ – ᴄʜᴀʀɢᴇ</b> {CHARGE_MSG} (2/2)\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Soon\n{LINK_MSG} ᴄᴍᴅ : /*\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴘᴀɢᴇ 1", callback_data="CHARGE", style="primary", icon_custom_emoji_id=EMOJI_IDS["BACK"])],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="gates", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "MASS":
        msg = (
            f"{MASS_MSG} <b>ɢᴀᴛᴇᴡᴀʏꜱ – ᴍᴀꜱꜱ</b> {MASS_MSG}\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth Mass\n{LINK_MSG} ᴄᴍᴅ : /msauth\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth (alt) Mass\n{LINK_MSG} ᴄᴍᴅ : /mass\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : 3DS Mass Lookup\n{LINK_MSG} ᴄᴍᴅ : /mvbv\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Adyen Charge Mass\n{LINK_MSG} ᴄᴍᴅ : /mcharge\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Square Charge Mass\n{LINK_MSG} ᴄᴍᴅ : /msq\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Shopify Payments Mass\n{LINK_MSG} ᴄᴍᴅ : /msh\n{MAINT_MSG} ꜱᴛᴀᴛᴜꜱ : Maintenance 🔧\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Charge 9$ Mass\n{LINK_MSG} ᴄᴍᴅ : /mst9\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : HiBurma Mass\n{LINK_MSG} ᴄᴍᴅ : /mhb\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Charge 2$ Mass\n{LINK_MSG} ᴄᴍᴅ : /mbf\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Soon (Mass)\n{LINK_MSG} ᴄᴍᴅ : —\n{STAR_MSG} ꜱᴛᴀᴛᴜꜱ : ᴄᴏᴍɪɴɢ 🔜\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="gates", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "TXT":
        msg = (
            f"{TXT_MSG} <b>ɢᴀᴛᴇᴡᴀʏꜱ – ᴛxᴛ</b> {TXT_MSG}\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth .txt\n{LINK_MSG} ᴄᴍᴅ : /tsauth\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Auth (alt) .txt\n{LINK_MSG} ᴄᴍᴅ : /tmass\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : 3DS .txt\n{LINK_MSG} ᴄᴍᴅ : /tvbv\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Adyen Charge .txt\n{LINK_MSG} ᴄᴍᴅ : /tcharge\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Square Charge .txt\n{LINK_MSG} ᴄᴍᴅ : /tsq\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Shopify Payments .txt\n{LINK_MSG} ᴄᴍᴅ : /tsh\n{MAINT_MSG} ꜱᴛᴀᴛᴜꜱ : Maintenance 🔧\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Charge 9$ .txt\n{LINK_MSG} ᴄᴍᴅ : /tst9\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : HiBurma .txt\n{LINK_MSG} ᴄᴍᴅ : /thb\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Stripe Charge 2$ .txt\n{LINK_MSG} ᴄᴍᴅ : /tbf\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Soon (.txt)\n{LINK_MSG} ᴄᴍᴅ : —\n{STAR_MSG} ꜱᴛᴀᴛᴜꜱ : ᴄᴏᴍɪɴɢ 🔜\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="gates", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "tools":
        msg = (
            f"{TOOLS_MSG} <b>ꜱᴘʏᴅᴇ – ᴛᴏᴏʟꜱ</b> {TOOLS_MSG}\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Generate CC\n{LINK_MSG} ᴄᴍᴅ : /gen -xxxx\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Info Bin\n{LINK_MSG} ᴄᴍᴅ : /bin\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Filter CC\n{LINK_MSG} ᴄᴍᴅ : /fl\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Fake Location\n{LINK_MSG} ᴄᴍᴅ : /fake\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Claim Credits\n{LINK_MSG} ᴄᴍᴅ : /claim\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Fetch IP\n{LINK_MSG} ᴄᴍᴅ : /ip\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Sort CC\n{LINK_MSG} ᴄᴍᴅ : /sort\n{ONLINE_MSG} ꜱᴛᴀᴛ_ᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="back", style="danger", icon_custom_emoji_id=EMOJI_IDS["BACK"])],
            [InlineKeyboardButton("ɴᴇxᴛ", callback_data="tools2", style="primary", icon_custom_emoji_id=EMOJI_IDS["NEXT"])]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "tools2":
        msg = (
            f"{TOOLS_MSG} <b>ꜱᴘʏᴅᴇ – ᴛᴏᴏʟꜱ</b> {TOOLS_MSG} ᴘ.2\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Redeem Keys\n{LINK_MSG} ᴄᴍᴅ : /claim key-xxxx\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Get ID\n{LINK_MSG} ᴄᴍᴅ : /id\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Membership Info\n{LINK_MSG} ᴄᴍᴅ : /plan\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Group Membership\n{LINK_MSG} ᴄᴍᴅ : /plang\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="tools", style="primary", icon_custom_emoji_id=EMOJI_IDS["BACK"])],
            [InlineKeyboardButton("ᴍᴇɴᴜ", callback_data="back", style="danger", icon_custom_emoji_id=EMOJI_IDS["HOME"])]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "helper":
        msg = (
            f"{HELPER_MSG} <b>ꜱᴘʏᴅᴇ – ʜᴇʟᴘᴇʀ</b> {HELPER_MSG}\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Buy Premium\n{LINK_MSG} ᴄᴍᴅ : /buy\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Credits\n{LINK_MSG} ᴄᴍᴅ : /howcrd\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : Check Credits\n{LINK_MSG} ᴄᴍᴅ : /credits\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"{BULLET_MSG} ɴᴀᴍᴇ : How To Add Bot\n{LINK_MSG} ᴄᴍᴅ : /howgp\n{ONLINE_MSG} ꜱᴛᴀᴛᴜꜱ : ᴏɴ\n\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("ʜᴏᴍᴇ", callback_data="back", style="danger", icon_custom_emoji_id=EMOJI_IDS["GHOST"])]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    elif query.data == "exit" or query.data == "close":
        await query.message.delete()

    elif query.data == "back":
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ɢᴀᴛᴇꜱ", callback_data="gates", style="primary", icon_custom_emoji_id=EMOJI_IDS["GATES"]),
             InlineKeyboardButton("ʀᴇɢɪꜱᴛᴇʀ", callback_data="register", style="success", icon_custom_emoji_id=EMOJI_IDS["REGISTER"])],
            [InlineKeyboardButton("ᴛᴏᴏʟꜱ", callback_data="tools", style="primary", icon_custom_emoji_id=EMOJI_IDS["TOOLS"]),
             InlineKeyboardButton("ʜᴇʟᴘᴇʀ", callback_data="helper", style="primary", icon_custom_emoji_id=EMOJI_IDS["HELPER"])],
            [InlineKeyboardButton("ᴇxɪᴛ", callback_data="exit", style="danger", icon_custom_emoji_id=EMOJI_IDS["EXIT"])]
        ])
        await send_colored_msg(client, query.message.chat.id, original_message_caption, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True, parse_mode="HTML")

# ----------------------------- MAIN -----------------------------
def main():
    folders = ["VID", "Banned", "Maintenance", "HIT", "B3"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

if __name__ == "__main__":
    main()
