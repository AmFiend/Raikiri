import asyncio
import os
import time
from datetime import datetime, date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaVideo
from pyrogram.enums import ParseMode
import json
import requests

# ---------- FALLBACK FOR MISSING MODULES (in case your custom modules aren't available) ----------
try:
    from FUNC.defs import *
    from FUNC.usersdb_func import *
except ImportError:
    # Dummy fallback – will not interfere with your actual bot if modules exist
    async def error_log(e): print(f"Error: {e}")
    class usersdb:
        @staticmethod
        def find_one(query, projection=None):
            return None
        @staticmethod
        def insert_one(doc): pass

# ---------- COLORED BUTTONS BRIDGE (supports `style` parameter) ----------
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
    """Send or edit a message with styled inline keyboard (colored buttons)."""
    bot_token = getattr(client, "bot_token", None)
    if not bot_token:
        # Fallback to normal pyrogram methods if no bot token (unlikely)
        if is_edit:
            if is_video:
                return await client.edit_message_caption(chat_id, message_id, text, reply_markup=reply_markup)
            return await client.edit_message_text(chat_id, message_id, text, reply_markup=reply_markup)
        return await client.send_message(chat_id, text, reply_markup=reply_markup)
    
    method = "editMessageCaption" if (is_edit and is_video) else ("editMessageText" if is_edit else "sendMessage")
    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    payload = {"chat_id": chat_id, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if is_video or method == "editMessageCaption":
        payload["caption"] = text
    else:
        payload["text"] = text
    if is_edit:
        payload["message_id"] = message_id
    if reply_markup:
        keyboard = []
        for row in reply_markup.inline_keyboard:
            new_row = []
            for btn in row:
                b_dict = {"text": btn.text}
                if hasattr(btn, "callback_data") and btn.callback_data:
                    b_dict["callback_data"] = btn.callback_data
                if hasattr(btn, "url") and btn.url:
                    b_dict["url"] = btn.url
                if hasattr(btn, "style") and btn.style:
                    b_dict["style"] = btn.style
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())

async def send_colored_video(client, chat_id, video, caption, reply_markup=None):
    """Send a video with styled inline keyboard."""
    bot_token = getattr(client, "bot_token", None)
    if not bot_token:
        return await client.send_video(chat_id, video, caption=caption, reply_markup=reply_markup)
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
                if hasattr(btn, "callback_data") and btn.callback_data:
                    b_dict["callback_data"] = btn.callback_data
                if hasattr(btn, "url") and btn.url:
                    b_dict["url"] = btn.url
                if hasattr(btn, "style") and btn.style:
                    b_dict["style"] = btn.style
                new_row.append(b_dict)
            keyboard.append(new_row)
        payload["reply_markup"] = json.dumps({"inline_keyboard": keyboard})
    loop = asyncio.get_event_loop()
    if files:
        return await loop.run_in_executor(None, lambda: requests.post(url, data=payload, files=files).json())
    return await loop.run_in_executor(None, lambda: requests.post(url, json=payload).json())

# ---------- VIDEO CACHE ----------
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

# ---------- USER REGISTRATION LOGIC (uses your existing usersdb) ----------
async def register_user_logic(user_id, username):
    antispam_time = int(time.time())
    yy, mm, dd = str(date.today()).split("-")
    reg_at = f"{dd}-{mm}-{yy}"
    find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
    if find is None:
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

# ---------- BOT COMMANDS ----------
@Client.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    first_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    user_status = find["status"] if find and find.get("status") else "𝙁𝙍𝙀𝙀"
    credit = find["credit"] if find and find.get("credit") else "0"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝙂𝙖𝙩𝙚𝙨", callback_data="gates", style="primary")],
        [InlineKeyboardButton("𝙏𝙤𝙤𝙡𝙨", callback_data="tools", style="primary")],
        [InlineKeyboardButton("𝘾𝙡𝙤𝙨𝙚", callback_data="exit", style="danger")]
    ])

    caption = (
        "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙡𝙤𝙜𝙞𝙣』</b>\n\n"
        f"└ <i>𝙄𝙙</i> → <code>{user_id}</code>\n"
        f"└ <i>𝙉𝙖𝙢𝙚</i> → <code>{first_name}</code>\n"
        f"└ <i>𝙐𝙨𝙚𝙧</i> → @{message.from_user.username or '𝙉/𝘼'}\n\n"
        "⟦㊣⟧ <b>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙍₳𝙄𝙆𝙄𝙍𝙄 𝘾𝙝𝙚𝙘𝙠𝙚𝙧</b>\n\n"
        "⟦㊅⟧ 𝙁𝙖𝙨𝙩, 𝙨𝙚𝙘𝙪𝙧𝙚, 𝙖𝙣𝙙 𝙧𝙚𝙡𝙞𝙖𝙗𝙡𝙚 𝙘𝙖𝙧𝙙 𝙫𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣.\n\n"
        f"⟦㊎⟧ 𝙑𝙚𝙧𝙨𝙞𝙤𝙣 → <b>1.3</b>\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "⟦㊗⟧ 𝙊𝙬𝙣𝙚𝙧: @Rai_God\n"
        "⟦㊤⟧ 𝘽𝙤𝙩: @Rai_chkbot"
    )

    try:
        video_file = get_next_menu_video()
        video_source = VIDEO_FILE_IDS.get(video_file, video_file)
        await send_colored_video(client, message.chat.id, video_source, caption, reply_markup=keyboard)
        if video_source not in VIDEO_FILE_IDS and os.path.exists(video_file):
            # Cache the file_id if we have a fresh upload
            pass  # The API response parsing is omitted for simplicity; you can keep your existing logic.
    except Exception as e:
        print(f"Start error: {e}")
        await send_colored_msg(client, message.chat.id, caption, reply_markup=keyboard, parse_mode="HTML")

@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    is_new, uid, uname = await register_user_logic(user_id, username)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    credit = find["credit"] if find and find.get("credit") else "100"
    if is_new:
        resp = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 𝘾𝙝𝙠</b> ⟦㊕⟧\n\n"
            "└ ⟦㊣⟧ 𝙎𝙩𝙖𝙩𝙪𝙨: 𝙍𝙀𝙂𝙄𝙎𝙏𝙀𝙍𝙀𝘿 ✓\n"
            f"└ ⟦㊅⟧ 𝙐𝙨𝙚𝙧: {uname}\n"
            f"└ ⟦㊎⟧ 𝙄𝘿: {uid}\n"
            f"└ ⟦㊗⟧ 𝘾𝙧𝙚𝙙𝙞𝙩𝙨: {credit}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊤⟧ 𝙎𝙩𝙖𝙧𝙩: /start"
        )
    else:
        resp = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 𝘾𝙝𝙠</b> ⟦㊕⟧\n\n"
            "└ ⟦㊣⟧ 𝙎𝙩𝙖𝙩𝙪𝙨: 𝘼𝙇𝙍𝙀𝘼𝘿𝙔 𝙍𝙀𝙂𝙄𝙎𝙏𝙀𝙍𝙀𝘿\n"
            f"└ ⟦㊅⟧ 𝙄𝘿: {uid}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊎⟧ 𝙋𝙧𝙤𝙘𝙚𝙚𝙙."
        )
    keyboard = [[InlineKeyboardButton("⟦㊕⟧ 𝙂𝙖𝙩𝙚𝙨", callback_data="gates", style="success")]]
    await send_colored_msg(client, message.chat.id, resp, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# ---------- CALLBACK HANDLERS ----------
@Client.on_callback_query()
async def button_callback(client, callback_query):
    query = callback_query
    await query.answer()
    data = query.data

    # Main menu (Gates)
    if data == "gates":
        msg = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨』</b>\n\n"
            "⟦㊣⟧ 𝙏𝙤𝙩𝙖𝙡 → 12\n"
            "⟦㊅⟧ 𝙊𝙣 → 10 ✅\n"
            "⟦㊎⟧ 𝙊𝙛𝙛 → 0 ❌\n"
            "⟦㊗⟧ 𝙈𝙖𝙞𝙣𝙩𝙚𝙣𝙖𝙣𝙘𝙚 → 2 🔧\n\n"
            "⟦㊤⟧ 𝙎𝙚𝙡𝙚𝙘𝙩 𝙖 𝙘𝙖𝙩𝙚𝙜𝙤𝙧𝙮:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("𝙰𝚞𝚝𝚑", callback_data="auth_gates", style="primary")],
            [InlineKeyboardButton("𝙲𝚑𝚊𝚛𝚐𝚎𝚍", callback_data="charge_gates", style="success")],
            [InlineKeyboardButton("𝙲𝚎𝚗", callback_data="special_gates", style="primary")],
            [InlineKeyboardButton("𝙷𝚘𝚖𝚎", callback_data="home", style="secondary"), InlineKeyboardButton("𝙲𝚕𝚘𝚜𝚎", callback_data="exit", style="danger")]
        ])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Auth gateways
    elif data == "auth_gates":
        msg = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙰𝚞𝚝𝚑』</b>\n\n"
            "⟦㊣⟧ 𝙽𝚊𝚖𝚎: 𝚂𝚑𝚘𝚙𝚒𝚏𝚢 𝙰𝚞𝚝𝚑\n"
            "   └─ 𝙲𝚖𝚍: <code>/chk</code> (𝚂𝚒𝚗𝚐𝚕𝚎)\n"
            "⟦㊅⟧ 𝙽𝚊𝚖𝚎: 𝟹𝙳𝚂 𝙻𝚘𝚘𝚔𝚞𝚙\n"
            "   └─ 𝙲𝚖𝚍: <code>/vbv</code> (𝚂𝚒𝚗𝚐𝚕𝚎)\n"
            "⟦㊎⟧ 𝙽𝚊𝚖𝚎: 𝚂𝚝𝚛𝚒𝚙𝚎 𝙰𝚞𝚝𝚑\n"
            "   └─ 𝙲𝚖𝚍: <code>/stripe_auth</code> (𝙿𝚛𝚎𝚖𝚒𝚞𝚖)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊗⟧ 𝚁𝚎𝚝𝚞𝚛𝚗𝚜 𝟹𝙳𝚂 / 𝙰𝚅𝚂 𝚛𝚎𝚜𝚞𝚕𝚝𝚜."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("𝙱𝚊𝚌𝚔", callback_data="gates", style="danger")]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Charged gateways
    elif data == "charge_gates":
        msg = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙲𝚑𝚊𝚛𝚐𝚎𝚍』</b>\n\n"
            "⟦㊣⟧ 𝙽𝚊𝚖𝚎: 𝙿𝚊𝚢𝙿𝚊𝚕 $𝟷\n"
            "   └─ 𝙲𝚖𝚍: <code>/pp</code>\n"
            "⟦㊅⟧ 𝙽𝚊𝚖𝚎: 𝙱𝚛𝚊𝚒𝚗𝚝𝚛𝚎𝚎 $𝟻\n"
            "   └─ 𝙲𝚖𝚍: <code>/b3</code>\n"
            "⟦㊎⟧ 𝙽𝚊𝚖𝚎: 𝚂𝚑𝚘𝚙𝚒𝚏𝚢\n"
            "   └─ 𝙲𝚖𝚍: <code>/sh</code>\n"
            "⟦㊗⟧ 𝙽𝚊𝚖𝚎: 𝚂𝚝𝚛𝚒𝚙𝚎 $𝟷\n"
            "   └─ 𝙲𝚖𝚍: <code>/stripe_charge</code> (𝙿𝚛𝚎𝚖𝚒𝚞𝚖)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊤⟧ 𝚁𝚎𝚊𝚕 𝚖𝚘𝚗𝚎𝚝𝚊𝚛𝚢 𝚝𝚛𝚊𝚗𝚜𝚊𝚌𝚝𝚒𝚘𝚗𝚜."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("𝙱𝚊𝚌𝚔", callback_data="gates", style="danger")]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Special / Cen gateways
    elif data == "special_gates":
        msg = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙲𝚎𝚗』</b>\n\n"
            "⟦㊣⟧ 𝙽𝚊𝚖𝚎: 𝙲𝙲𝙽 𝚂𝚝𝚛𝚒𝚙𝚎 $𝟷\n"
            "   └─ 𝙲𝚖𝚍: <code>/or</code> (𝙿𝚛𝚎𝚖𝚒𝚞𝚖)\n"
            "⟦㊅⟧ 𝙽𝚊𝚖𝚎: 𝙲𝙲𝙽 𝚂𝚝𝚛𝚒𝚙𝚎 $𝟸𝟼\n"
            "   └─ 𝙲𝚖𝚍: <code>/bo</code> (𝙿𝚛𝚎𝚖𝚒𝚞𝚖)\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊎⟧ 𝙰𝚍𝚟𝚊𝚗𝚌𝚎𝚍 𝚋𝚢𝚙𝚊𝚜𝚜 𝚖𝚎𝚝𝚑𝚘𝚍𝚜."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("𝙱𝚊𝚌𝚔", callback_data="gates", style="danger")]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Tools menu
    elif data == "tools":
        msg = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙏𝙤𝙤𝙡𝙨』</b>\n\n"
            "⟦㊣⟧ 𝙱𝙸𝙽 𝙸𝚗𝚏𝚘: <code>/bin 123456</code>\n"
            "⟦㊅⟧ 𝙶𝚎𝚗𝚎𝚛𝚊𝚝𝚎 𝙲𝙲: <code>/gen 10</code>\n"
            "⟦㊎⟧ 𝙶𝚎𝚗𝚎𝚛𝚊𝚝𝚎 𝙱𝙸𝙽𝚜: <code>/gbin 6</code>\n"
            "⟦㊗⟧ 𝚂𝙺 𝙲𝚑𝚎𝚌𝚔𝚎𝚛: <code>/sk sk_live_...</code>\n"
            "⟦㊤⟧ 𝚁𝚊𝚗𝚍𝚘𝚖 𝙰𝚍𝚍𝚛𝚎𝚜𝚜: <code>/rnd us</code>\n"
            "⟦㊥⟧ 𝙼𝚢 𝙸𝚗𝚏𝚘: <code>/my</code>\n"
            "⟦㊦⟧ 𝙿𝚕𝚊𝚗 𝙸𝚗𝚏𝚘: <code>/plan</code>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊧⟧ 𝙰𝚕𝚕 𝚝𝚘𝚘𝚕𝚜 𝚊𝚛𝚎 𝚏𝚛𝚎𝚎."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("𝙷𝚘𝚖𝚎", callback_data="home", style="danger")]])
        await send_colored_msg(client, query.message.chat.id, msg, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Home – return to start screen
    elif data == "home":
        first_name = query.from_user.first_name
        user_id = str(query.from_user.id)
        find = usersdb.find_one({"id": user_id}, {"_id": 0})
        user_status = find["status"] if find and find.get("status") else "𝙁𝙍𝙀𝙀"
        credit = find["credit"] if find and find.get("credit") else "0"
        caption = (
            "⟦㊕⟧ <b>𝙍₳𝙄𝙆𝙄𝙍𝙄 → 『𝙡𝙤𝙜𝙞𝙣』</b>\n\n"
            f"└ <i>𝙄𝙙</i> → <code>{user_id}</code>\n"
            f"└ <i>𝙉𝙖𝙢𝙚</i> → <code>{first_name}</code>\n"
            f"└ <i>𝙐𝙨𝙚𝙧</i> → @{query.from_user.username or '𝙉/𝘼'}\n\n"
            "⟦㊣⟧ <b>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙍₳𝙄𝙆𝙄𝙍𝙄 𝘾𝙝𝙚𝙘𝙠𝙚𝙧</b>\n\n"
            "⟦㊅⟧ 𝙁𝙖𝙨𝙩, 𝙨𝙚𝙘𝙪𝙧𝙚, 𝙖𝙣𝙙 𝙧𝙚𝙡𝙞𝙖𝙗𝙡𝙚 𝙘𝙖𝙧𝙙 𝙫𝙚𝙧𝙞𝙛𝙞𝙘𝙖𝙩𝙞𝙤𝙣.\n\n"
            f"⟦㊎⟧ 𝙑𝙚𝙧𝙨𝙞𝙤𝙣 → <b>1.3</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⟦㊗⟧ 𝙊𝙬𝙣𝙚𝙧: @Rai_God\n"
            "⟦㊤⟧ 𝘽𝙤𝙩: @Rai_chkbot"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("𝙂𝙖𝙩𝙚𝙨", callback_data="gates", style="primary")],
            [InlineKeyboardButton("𝙏𝙤𝙤𝙡𝙨", callback_data="tools", style="primary")],
            [InlineKeyboardButton("𝘾𝙡𝙤𝙨𝙚", callback_data="exit", style="danger")]
        ])
        try:
            video_file = "VID/menu1.mp4"
            video_source = VIDEO_FILE_IDS.get(video_file, video_file)
            if video_source == video_file and os.path.exists(video_file):
                await send_colored_video(client, query.message.chat.id, video_source, caption, reply_markup=keyboard)
            else:
                await send_colored_msg(client, query.message.chat.id, caption, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)
        except Exception as e:
            await send_colored_msg(client, query.message.chat.id, caption, reply_markup=keyboard, is_edit=True, message_id=query.message.id, is_video=True)

    # Exit – delete the message
    elif data == "exit":
        await query.message.delete()

    # Fallback
    else:
        await query.answer("Unknown option", show_alert=True)

# ---------- CREATE FOLDERS (if not exist) ----------
def create_folders():
    for folder in ["VID", "Banned", "Maintenance", "HIT", "B3"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")

create_folders()
