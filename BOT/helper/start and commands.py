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

# ---------- USER REGISTRATION (unchanged) ----------
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

# ---------- MAIN START COMMAND (NEW NEON TECH STYLE) ----------
@Client.on_message(filters.command(["start", "Start"], prefixes=[".", "/", "!", "$"]))
async def start_command(client, message):
    first_name = message.from_user.first_name
    user_id = str(message.from_user.id)
    username = message.from_user.username or "N/A"

    caption = (
        "┌─────────────────────────────────┐\n"
        "│         ⬤  R₳IKIRI  ⬤          │\n"
        "├─────────────────────────────────┤\n"
        f"│  ◉  ID    : {user_id}\n"
        f"│  ◉  NAME  : {first_name}\n"
        f"│  ◉  USER  : @{username}\n"
        "├─────────────────────────────────┤\n"
        "│  ◆  SYSTEM ONLINE                │\n"
        "│  ◆  CARD VERIFIER ACTIVE         │\n"
        "│  ◆  VERSION 1.3                  │\n"
        "├─────────────────────────────────┤\n"
        "│  ⬤  OWNER : @Rai_God             │\n"
        "│  ⬤  BOT   : @Rai_chkbot          │\n"
        "└─────────────────────────────────┘\n\n"
        "<i>> Welcome to the R₳IKIRI terminal.</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⫷  GATES  ⫸", callback_data="gates_menu")],
        [InlineKeyboardButton("⫷  TOOLS  ⫸", callback_data="tools_menu")],
        [InlineKeyboardButton("⫷  CLOSE  ⫸", callback_data="exit_now")]
    ])

    await message.reply_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# ---------- REGISTER COMMAND (same style) ----------
@Client.on_message(filters.command(["register", "Register"], prefixes=[".", "/", "!", "$"]))
async def cmd_register(client, message):
    user_id = str(message.from_user.id)
    username = str(message.from_user.username)
    is_new, uid, uname = await register_user_logic(user_id, username)
    find = usersdb.find_one({"id": user_id}, {"_id": 0})
    credit = find["credit"] if find and find.get("credit") else "100"

    if is_new:
        resp = (
            "┌─────────────────────────────────┐\n"
            "│      ⬤  REGISTRATION  ⬤       │\n"
            "├─────────────────────────────────┤\n"
            f"│  ◉  STATUS : ✓ REGISTERED       │\n"
            f"│  ◉  USER   : {uname}\n"
            f"│  ◉  ID     : {uid}\n"
            f"│  ◉  CREDITS: {credit}\n"
            "└─────────────────────────────────┘\n\n"
            "> Use /start to access the system."
        )
    else:
        resp = (
            "┌─────────────────────────────────┐\n"
            "│      ⬤  REGISTRATION  ⬤       │\n"
            "├─────────────────────────────────┤\n"
            f"│  ◉  STATUS : ALREADY REGISTERED │\n"
            f"│  ◉  ID     : {uid}\n"
            "└─────────────────────────────────┘\n\n"
            "> Proceed with /start."
        )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⫷  GATES  ⫸", callback_data="gates_menu")]])
    await message.reply_text(resp, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# ---------- CALLBACK HANDLERS ----------
@Client.on_callback_query()
async def button_callback(client, callback_query):
    data = callback_query.data
    await callback_query.answer()

    # ---------- GATES MENU (with same tech borders) ----------
    if data == "gates_menu":
        msg = (
            "┌─────────────────────────────────┐\n"
            "│         ⬤  GATEWAYS  ⬤         │\n"
            "├─────────────────────────────────┤\n"
            "│  总  TOTAL       : 12           │\n"
            "│  上  ONLINE      : 10  ✅       │\n"
            "│  休  OFFLINE     : 0   ❌       │\n"
            "│  監  MAINTENANCE : 2   🔧       │\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  Select a category:          │\n"
            "└─────────────────────────────────┘"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⫷  AUTH  ⫸", callback_data="auth_gates")],
            [InlineKeyboardButton("⫷  CHARGED  ⫸", callback_data="charged_gates")],
            [InlineKeyboardButton("⫷  CEN  ⫸", callback_data="special_gates")],
            [InlineKeyboardButton("⫷  HOME  ⫸", callback_data="main_menu"), InlineKeyboardButton("⫷  CLOSE  ⫸", callback_data="exit_now")]
        ])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- AUTH GATEWAYS ----------
    elif data == "auth_gates":
        msg = (
            "┌─────────────────────────────────┐\n"
            "│           ⬤  AUTH  ⬤            │\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  Shopify Auth                │\n"
            "│      > /chk (Single)            │\n"
            "│  ◆  3DS Lookup                  │\n"
            "│      > /vbv (Single)            │\n"
            "│  ◆  Stripe Auth (Premium)       │\n"
            "│      > /stripe_auth             │\n"
            "├─────────────────────────────────┤\n"
            "│  ◉  Returns 3DS / AVS results.  │\n"
            "└─────────────────────────────────┘"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⫷  BACK  ⫸", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- CHARGED GATEWAYS ----------
    elif data == "charged_gates":
        msg = (
            "┌─────────────────────────────────┐\n"
            "│         ⬤  CHARGED  ⬤          │\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  PayPal $1                   │\n"
            "│      > /pp                      │\n"
            "│  ◆  Braintree $5                │\n"
            "│      > /b3                      │\n"
            "│  ◆  Shopify                     │\n"
            "│      > /sh                      │\n"
            "│  ◆  Stripe $1 (Premium)         │\n"
            "│      > /stripe_charge           │\n"
            "├─────────────────────────────────┤\n"
            "│  ◉  Real monetary transactions. │\n"
            "└─────────────────────────────────┘"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⫷  BACK  ⫸", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- SPECIAL / CEN GATEWAYS ----------
    elif data == "special_gates":
        msg = (
            "┌─────────────────────────────────┐\n"
            "│          ⬤  CEN  ⬤              │\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  CCN Stripe $1 (Premium)     │\n"
            "│      > /or                      │\n"
            "│  ◆  CCN Stripe $26 (Premium)    │\n"
            "│      > /bo                      │\n"
            "├─────────────────────────────────┤\n"
            "│  ◉  Advanced bypass methods.    │\n"
            "└─────────────────────────────────┘"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⫷  BACK  ⫸", callback_data="gates_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- TOOLS MENU ----------
    elif data == "tools_menu":
        msg = (
            "┌─────────────────────────────────┐\n"
            "│          ⬤  TOOLS  ⬤            │\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  BIN Info                    │\n"
            "│      > /bin 123456              │\n"
            "│  ◆  Generate CC                 │\n"
            "│      > /gen 10                  │\n"
            "│  ◆  Generate BINs               │\n"
            "│      > /gbin 6                  │\n"
            "│  ◆  SK Checker                  │\n"
            "│      > /sk sk_live_...          │\n"
            "│  ◆  Random Address              │\n"
            "│      > /rnd us                  │\n"
            "│  ◆  My Info                     │\n"
            "│      > /my                      │\n"
            "│  ◆  Plan Info                   │\n"
            "│      > /plan                    │\n"
            "├─────────────────────────────────┤\n"
            "│  ◉  All tools are free.         │\n"
            "└─────────────────────────────────┘"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⫷  HOME  ⫸", callback_data="main_menu")]])
        await callback_query.edit_message_text(msg, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- MAIN MENU (HOME) – return to start ----------
    elif data == "main_menu":
        first_name = callback_query.from_user.first_name
        user_id = str(callback_query.from_user.id)
        username = callback_query.from_user.username or "N/A"
        caption = (
            "┌─────────────────────────────────┐\n"
            "│         ⬤  R₳IKIRI  ⬤          │\n"
            "├─────────────────────────────────┤\n"
            f"│  ◉  ID    : {user_id}\n"
            f"│  ◉  NAME  : {first_name}\n"
            f"│  ◉  USER  : @{username}\n"
            "├─────────────────────────────────┤\n"
            "│  ◆  SYSTEM ONLINE                │\n"
            "│  ◆  CARD VERIFIER ACTIVE         │\n"
            "│  ◆  VERSION 1.3                  │\n"
            "├─────────────────────────────────┤\n"
            "│  ⬤  OWNER : @Rai_God             │\n"
            "│  ⬤  BOT   : @Rai_chkbot          │\n"
            "└─────────────────────────────────┘\n\n"
            "<i>> Welcome to the R₳IKIRI terminal.</i>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⫷  GATES  ⫸", callback_data="gates_menu")],
            [InlineKeyboardButton("⫷  TOOLS  ⫸", callback_data="tools_menu")],
            [InlineKeyboardButton("⫷  CLOSE  ⫸", callback_data="exit_now")]
        ])
        await callback_query.edit_message_text(caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # ---------- EXIT / CLOSE ----------
    elif data == "exit_now":
        await callback_query.message.delete()

    # ---------- DEFAULT ----------
    else:
        await callback_query.answer("Unknown option", show_alert=True)
