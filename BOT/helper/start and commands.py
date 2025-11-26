from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from utilsdf.functions import symbol   # your symbol function

# DB imports (your setup)
from FUNC.usersdb_func import getuserinfo  # existing helper you already have
from mongodb import usersdb                # your actual collection

# ----------------------------------------------------
# VIDEO ROTATION SYSTEM (ADDED)
# ----------------------------------------------------

MENU_VIDEOS = ["menu1.mp4", "menu2.mp4", "menu3.mp4", "menu4.mp4", "menu5.mp4"]
current_video_index = 0

def get_next_menu_video():
    global current_video_index
    video = MENU_VIDEOS[current_video_index % len(MENU_VIDEOS)]
    current_video_index += 1
    return video

# original send helper (used when we need to send a new message)
async def send_video_or_text(message, text, buttons):
    video_file = get_next_menu_video()
    try:
        with open(video_file, "rb") as v:
            await message.reply_video(
                video=v,
                caption=text,
                reply_markup=buttons,
                parse_mode="html"
            )
    except Exception:
        await message.reply(
            text,
            reply_markup=buttons,
            parse_mode="html"
        )

# NEW: edit-in-place helper (for smooth instant UI updates)
async def edit_message_in_place(message, text, buttons):
    """
    Try to edit caption (if media message), otherwise edit text.
    Falls back to replying if edit fails.
    """
    try:
        # Try edit caption (works if original message is a media with caption)
        await message.edit_caption(caption=text, reply_markup=buttons, parse_mode="html")
        return
    except Exception:
        pass

    try:
        # Try edit text
        await message.edit_text(text, reply_markup=buttons, parse_mode="html")
        return
    except Exception:
        pass

    # Fallback: send a fresh reply (rare)
    try:
        await send_video_or_text(message, text, buttons)
    except Exception:
        # last resort: simple reply_text
        await message.reply(text, reply_markup=buttons, parse_mode="html")


# ----------------------------------------------------
# TEXTS
# ----------------------------------------------------

text_home = (
    "[<a href='https://t.me/spid_3r'>朱</a>] 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝘾𝙝𝙚𝙘𝙠𝙚𝙧\n\n"
    "[<a href='https://t.me/spid_3r'>㊄</a>] Spyde is renewed, we present our new improved version, "
    "with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
    "<a href='https://t.me/spid_3_'>╰┈➤</a> 𝙑𝙚𝙧𝙨𝙞𝙤𝙣 -» 1.0"
)

# ----------------------------------------------------
# BUTTONS
# ----------------------------------------------------

exit_button = InlineKeyboardButton("𝙀𝙭𝙞𝙩 ⚠️", callback_data="exit")

buttons_home = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("𝙂𝙖𝙩𝙚𝙨 ♻️", callback_data="gates"),
            InlineKeyboardButton("𝙏𝙤𝙤𝙡𝙨 🛠", callback_data="tools"),
        ],
        [InlineKeyboardButton("𝘾𝙝𝙖𝙣𝙣𝙚𝙡 💫", url="https://t.me/example")],
        [exit_button],
    ]
)

buttons_gates = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("𝘼𝙪𝙩𝙝", callback_data="auths"),
            InlineKeyboardButton("𝘾𝙝𝙖𝙧𝙜𝙚𝙙", callback_data="chargeds"),
        ],
        [InlineKeyboardButton("𝙎𝙥𝙚𝙘𝙞𝙖𝙡", callback_data="specials")],
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="home")],
        [exit_button],
    ]
)

return_home_and_exit = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="home")],
        [exit_button],
    ]
)

return_and_exit_gates = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — AUTH PAGE
# ----------------------------------------------------

text_gates_auth = (
    "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝\n\n"
    "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐒𝐭𝐫𝐢𝐩𝐞 -» Zuora + Stripe -» Auth\n"
    "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .chk -» Free\n"
    "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
    "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐚𝐮𝐭𝐨 𝐬𝐭𝐫𝐢𝐩𝐞 -» Auto stripe -» Auth\n"
    "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .as -» Free\n"
    "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
    "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐒𝐭𝐫𝐢𝐩𝐞 𝐚𝐮𝐭𝐡𝟏 -» Auth1 -» Auth\n"
    "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .au -» Premium\n"
    "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅"
    "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞  -» Braintree Premium -» Auth\n"
    "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .b3 -» Premium\n"
    "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅"
)

buttons_auth_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — CHARGED PAGE
# ----------------------------------------------------

text_gates_charged = f"""
〈<a href='https://t.me/spid_3r'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙\n\n"
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐀𝐔𝐓𝐇𝐍𝐄𝐓 -» authnet -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .authnet1 -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐀𝐔𝐓𝐎 𝐒𝐇𝐎𝐏𝐈𝐅𝐘  -» ePay -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .sh -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐂𝐇𝐄𝐂𝐊 -» Authorize.net -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .check -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» om ✅\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐑𝐚𝐳𝐨𝐩𝐚𝐲 -» razopay -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .rz -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝐒𝐄𝐋𝐅 𝐒𝐇𝐎𝐏𝐈𝐅𝐘  -» self shopify -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .sh -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙏𝙧𝙞𝙙𝙚𝙣𝙩 -» Transax Gateway -» $0.01
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .tr -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Mantenience ⚠️\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙋𝙚𝙧𝙞𝙘𝙤 -» wc Sagepay(Opayo) -» €1.00
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .pr -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n
〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙅𝙪𝙖𝙣 -» WorldPay -» ₤0.89
〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .jn -» Premium
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌
"""

buttons_charged_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — SPECIAL PAGE
# ----------------------------------------------------

text_gates_specials = f"""
𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙎𝙥𝙚𝙘𝙞𝙖𝙡

〈<a href='https://t.me/spid_3r'>朱</a>〉 -» <code>payflow Mass</code>
〈<a href='https://t.me/spid_3r'>零</a>〉 -» <code>.mpy</code> -» <code>Premium</code>
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 -» <code>On ✓</code>

〈<a href='https://t.me/spid_3r'>朱</a>〉 -» <code>mass stripe</code>
〈<a href='https://t.me/spid_3r'>零</a>〉 -» <code>.mstxt</code> -» <code>Premium</code>
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 -» <code>On ✓</code>

〈<a href='https://t.me/spid_3r'>朱</a>〉 -» <code>mass Auto stripe</code>
〈<a href='https://t.me/spid_3r'>零</a>〉 -» <code>.asm</code> -» <code>Premium</code>
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 -» <code>On ✓</code>

〈<a href='https://t.me/spid_3r'>朱</a>〉 -» <code>mass stipe</code>
〈<a href='https://t.me/spid_3r'>零</a>〉 -» <code>.mchk</code> -» <code>Premium</code>
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 -» <code>On ✓</code>
"""

buttons_specials_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", callback_data="gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# TOOLS
# ----------------------------------------------------

text_tools = f"""
𝙏𝙤𝙤𝙡𝙨 🛠

〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙍𝙚𝙛𝙚 -» add group  
〈<a href='https://t.me/spid_3r'>零</a>〉 .howgp -» Free  
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 On ✓  

〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘽𝙞𝙣 -» info bin  
〈<a href='https://t.me/spid_3r'>零</a>〉 .bin -» Free  
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 On ✓  

〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘾𝙝𝙖𝙩 GPT -» filter cc  
〈<a href='https://t.me/spid_3r'>零</a>〉 .fl -» Premium  
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 Off ❌  

〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘼𝙙𝙙𝙧𝙚𝙨𝙨 -» fake address  
〈<a href='https://t.me/spid_3r'>零</a>〉 .fake -» Free  
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 On ✓  

〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙎𝙠 -» credits  
〈<a href='https://t.me/spid_3r'>零</a>〉 .claim -» Free  
〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 On ✓  
"""

# ----------------------------------------------------
# REGISTRATION HELPERS & COMMAND
# ----------------------------------------------------

async def is_registered(user_id):
    """Return True if user exists in DB"""
    user = await getuserinfo(user_id)
    return user is not None

def create_user_in_db(user_id):
    """Insert default user doc (sync insert as your other code uses insert_one sync)"""
    usersdb.insert_one({
        "id": str(user_id),
        "username": None,
        "status": "FREE",
        "plan": "N/A",
        "credit": 50,
        "expiry": "N/A",
        "antispam_time": 0,
        "reg_at": None
    })

@Client.on_message(filters.command("register"))
async def register_cmd(client, message):
    """
    /register command — creates user in usersdb if not exists
    """
    user_id = message.from_user.id

    usr = await getuserinfo(str(user_id))
    if usr is not None:
        return await message.reply(
            "<b>✅ You are already registered.</b>\nUse /start to open the menu.",
            parse_mode="html"
        )

    # build reg date
    from datetime import date
    import time
    yy, mm, dd = str(date.today()).split("-")
    reg_at = f"{dd}-{mm}-{yy}"

    # insert
    usersdb.insert_one({
        "id": str(user_id),
        "username": str(getattr(message.from_user, "username", "") or ""),
        "status": "FREE",
        "plan": "N/A",
        "credit": 50,
        "expiry": "N/A",
        "antispam_time": int(time.time()),
        "reg_at": reg_at
    })

    WELCOME_BUTTON = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Commands", callback_data="cmds")],
            [InlineKeyboardButton("Close", callback_data="exit")]
        ]
    )

    resp = f"""<b>Registration Successful ♻️</b>

● Name: {message.from_user.first_name}
● User ID: {user_id}
● Role: Free
● Credits: 50

Use /start to open the menu.
"""
    await message.reply_text(resp, reply_markup=WELCOME_BUTTON, parse_mode="html")


# ----------------------------------------------------
# UTILITY: block non-registered for callbacks
# ----------------------------------------------------

async def block_if_not_registered(client, query: CallbackQuery):
    usr = await getuserinfo(str(query.from_user.id))
    if usr is None:
        # Ask them to register: alert
        await query.answer("⚠️ You must register first. Use /register", show_alert=True)
        return False
    return True


# ----------------------------------------------------
# CALLBACK HANDLERS WITH EDIT-IN-PLACE (NO FLICKER)
# ----------------------------------------------------

@Client.on_message(filters.command("start"))
async def start_menu(client: Client, message: Message):
    user_id = message.from_user.id

    # If not registered, show register prompt with button
    if not await is_registered(user_id):
        btns = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Register ✅", callback_data="register")],
                [InlineKeyboardButton("Close", callback_data="exit")]
            ]
        )
        return await message.reply(
            "<b>⚠️ You are not registered.\nPress Register to create your account.</b>",
            reply_markup=btns,
            parse_mode="html"
        )

    # Registered → show normal menu (send new video/text)
    await send_video_or_text(message, text_home, buttons_home)


# Helper to update an existing menu message (used in callbacks)
async def update_menu_for_query(query: CallbackQuery, text, buttons):
    """
    Edits the same message (caption or text) to change menu instantly.
    """
    try:
        await edit_message_in_place(query.message, text, buttons)
    except Exception:
        # if edit failed, as a fallback send a fresh message
        await send_video_or_text(query.message, text, buttons)


@Client.on_callback_query(filters.regex("^home$"))
async def cb_home(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    # update in place
    await update_menu_for_query(query, text_home, buttons_home)
    await query.answer()

@Client.on_callback_query(filters.regex("^gates$"))
async def cb_gates(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    gates_text = (
        "<a href='https://t.me/spid_3r'>〄</a>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚\n\n"
        "║<a href='https://t.me/spid_3r'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» 5\n"
        "║<a href='https://t.me/spid_3r'>㊡</a>║ 𝙊𝙣 -» 1 ✓\n"
        "║<a href='https://t.me/spid_3r'>㊤</a>║ 𝙊𝙛𝙛 -» 4 ❌\n"
        "║<a href='https://t.me/spid_3r'>㊬</a> 》𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» 4 ⚠️\n\n"
        "〈<a href='https://t.me/spid_3r'>ゼ</a>〉 𝙎𝙚𝙡𝙚𝙘𝙩 𝙮𝙤𝙪𝙧 𝙜𝙖𝙩𝙚!"
    )
    await update_menu_for_query(query, gates_text, buttons_gates)
    await query.answer()

@Client.on_callback_query(filters.regex("^auths$"))
async def cb_auth(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    await update_menu_for_query(query, text_gates_auth, buttons_auth_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^chargeds$"))
async def cb_charged(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    await update_menu_for_query(query, text_gates_charged, buttons_charged_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^specials$"))
async def cb_specials(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    await update_menu_for_query(query, text_gates_specials, buttons_specials_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^tools$"))
async def cb_tools(client: Client, query: CallbackQuery):
    if not await block_if_not_registered(client, query):
        return

    await update_menu_for_query(query, text_tools, return_home_and_exit)
    await query.answer()

@Client.on_callback_query(filters.regex("^register$"))
async def cb_register_button(client: Client, query: CallbackQuery):
    # user pressed inline "Register" button
    # run the same logic as /register
    user_id = query.from_user.id

    usr = await getuserinfo(str(user_id))
    if usr is not None:
        await query.answer("✅ You are already registered.", show_alert=True)
        return

    import time
    from datetime import date
    yy, mm, dd = str(date.today()).split("-")
    reg_at = f"{dd}-{mm}-{yy}"

    usersdb.insert_one({
        "id": str(user_id),
        "username": str(getattr(query.from_user, "username", "") or ""),
        "status": "FREE",
        "plan": "N/A",
        "credit": 50,
        "expiry": "N/A",
        "antispam_time": int(time.time()),
        "reg_at": reg_at
    })

    await query.answer("🎉 Registered! Use /start", show_alert=True)
    # optionally update the same message to show main menu immediately
    await update_menu_for_query(query, "<b>Registered! Press /start to open menu.</b>", InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="home")]]))

@Client.on_callback_query(filters.regex("^exit$"))
async def cb_exit(client: Client, query: CallbackQuery):
    # gentle exit: edit text
    try:
        await query.message.edit_text(
            "𝙀𝙭𝙞𝙩𝙚𝙙 𝙢𝙚𝙣𝙪 ⚠️\n\nUse /start to open it again.",
            parse_mode="html"
        )
    except Exception:
        # fallback
        await query.answer("Exited.")
    await query.answer("Exited.")
