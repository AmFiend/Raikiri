import time
from datetime import date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# ---------- FALLBACK FOR MISSING MODULES ----------
try:
    from FUNC.defs import *
    from FUNC.usersdb_func import *
except ImportError:
    async def error_log(e): print(f"Error: {e}")
    class usersdb:
        @staticmethod
        def find_one(query, projection=None): return None
        @staticmethod
        def insert_one(doc): pass

# ---------- USER REGISTRATION ----------
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

# ---------- MAIN START COMMAND ----------
@Client.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    first_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    username = message.from_user.username or "N/A"

    # Build the start message exactly like the screenshot
    caption = (
        "Akatsuki → 『ログイン』\n\n"
        f"<空> Id -> {user_id}\n"
        f"<空> Name -> {first_name}\n"
        f"<空> User -> @{username}\n\n"
        "[朱] Welcome to Akatsuki Checker\n\n"
        "[五] Akatsuki is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        "Version -> 1.9"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Gateways", callback_data="gates_menu")],
        [InlineKeyboardButton("Tools", callback_data="tools_menu")],
        [InlineKeyboardButton("Close", callback_data="exit_now")]
    ])

    await message.reply_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

# ---------- REGISTER COMMAND ----------
@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    is_new, uid, uname = await register_user_logic(user_id, username)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    credit = find["credit"] if find and find.get("credit") else "100"
    if is_new:
        resp = (
            "Akatsuki → 『ログイン』\n\n"
            f"<空> Id -> {uid}\n"
            f"<空> User -> @{uname}\n\n"
            "[朱] Registration successful! You have 100 credits.\n"
            "Use /start to begin."
        )
    else:
        resp = (
            "Akatsuki → 『ログイン』\n\n"
            f"<空> Id -> {uid}\n\n"
            "[朱] You are already registered.\n"
            "Use /start to continue."
        )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Go to Gateways", callback_data="gates_menu")]])
    await message.reply_text(resp, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# ---------- CALLBACK HANDLERS ----------
@Client.on_callback_query()
async def button_callback(client, callback_query):
    data = callback_query.data
    await callback_query.answer()

    # ---------- GATEWAYS MENU (stats + buttons) ----------
    if data == "gates_menu":
        msg = (
            "<Welcome to Akatsuki →>\n\n"
            "| 特 | Total → 91 |\n"
            "| 休 | On → 69 ✅ |\n"
            "| 上 | Off → 16 ❌ |\n"
            "| 監 | Maintenance → 6 ❌ |\n\n"
            "<七> Select the type of gate you want for your use!"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Auth", callback_data="auth_gates")],
            [InlineKeyboardButton("Charged", callback_data="charged_gates")],
            [InlineKeyboardButton("Cen", callback_data="special_gates")],
            [InlineKeyboardButton("Home", callback_data="main_menu"), InlineKeyboardButton("Close", callback_data="exit_now")]
        ])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- AUTH GATEWAYS ----------
    elif data == "auth_gates":
        msg = (
            "Auth Gateways\n\n"
            "⟦㊕⟧ Shopify Auth\n"
            "   └─ Cmd: /chk (Single)\n"
            "⟦㊣⟧ 3DS Lookup\n"
            "   └─ Cmd: /vbv (Single)\n"
            "⟦㊅⟧ Stripe Auth\n"
            "   └─ Cmd: /stripe_auth (Premium)\n\n"
            "Returns 3DS / AVS results."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- CHARGED GATEWAYS ----------
    elif data == "charged_gates":
        msg = (
            "Charged Gateways\n\n"
            "⟦㊕⟧ PayPal $1\n"
            "   └─ Cmd: /pp\n"
            "⟦㊣⟧ Braintree $5\n"
            "   └─ Cmd: /b3\n"
            "⟦㊅⟧ Shopify\n"
            "   └─ Cmd: /sh\n"
            "⟦㊎⟧ Stripe $1\n"
            "   └─ Cmd: /stripe_charge (Premium)\n\n"
            "Real monetary transactions."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- SPECIAL / CEN GATEWAYS ----------
    elif data == "special_gates":
        msg = (
            "Cen Gateways\n\n"
            "⟦㊕⟧ CCN Stripe $1\n"
            "   └─ Cmd: /or (Premium)\n"
            "⟦㊣⟧ CCN Stripe $26\n"
            "   └─ Cmd: /bo (Premium)\n\n"
            "Advanced bypass methods."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- TOOLS MENU ----------
    elif data == "tools_menu":
        msg = (
            "Tools\n\n"
            "⟦㊕⟧ BIN Info: /bin 123456\n"
            "⟦㊣⟧ Generate CC: /gen 10\n"
            "⟦㊅⟧ Generate BINs: /gbin 6\n"
            "⟦㊎⟧ SK Checker: /sk sk_live_...\n"
            "⟦㊗⟧ Random Address: /rnd us\n"
            "⟦㊤⟧ My Info: /my\n"
            "⟦㊥⟧ Plan Info: /plan\n\n"
            "All tools are free."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Home", callback_data="main_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- MAIN MENU (HOME) ----------
    elif data == "main_menu":
        first_name = callback_query.from_user.first_name
        user_id = str(callback_query.from_user.id)
        username = callback_query.from_user.username or "N/A"
        caption = (
            "Akatsuki → 『ログイン』\n\n"
            f"<空> Id -> {user_id}\n"
            f"<空> Name -> {first_name}\n"
            f"<空> User -> @{username}\n\n"
            "[朱] Welcome to Akatsuki Checker\n\n"
            "[五] Akatsuki is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
            "Version -> 1.9"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Gateways", callback_data="gates_menu")],
            [InlineKeyboardButton("Tools", callback_data="tools_menu")],
            [InlineKeyboardButton("Close", callback_data="exit_now")]
        ])
        await callback_query.edit_message_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- EXIT / CLOSE ----------
    elif data == "exit_now":
        await callback_query.message.delete()

    # ---------- DEFAULT ----------
    else:
        await callback_query.answer("Unknown option", show_alert=True)
