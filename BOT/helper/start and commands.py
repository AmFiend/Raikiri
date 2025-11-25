from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from utilsdf.functions import symbol   # your symbol function

# ----------------------------------------------------
# TEXTS
# ----------------------------------------------------

text_home = """[朱] 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝘾𝙝𝙚𝙘𝙠𝙚𝙧 »
<code>[㊄] Akatsuki is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.</code>

<a href='tg://user?id={}'>╰┈➤ 𝙑𝙚𝙧𝙨𝙞𝙤𝙣 </a> -» <code>1.4</code>"""

# ----------------------------------------------------
# BUTTONS
# ----------------------------------------------------
              InlineKeyboardButton("朱", callback_data="start_again")
exit_button = InlineKeyboardButton("𝙀𝙭𝙞𝙩 ⚠️", "exit")

buttons_home = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("𝙂𝙖𝙩𝙚𝙨 ♻️", "gates"),
            InlineKeyboardButton("𝙏𝙤𝙤𝙡𝙨 🛠", "tools"),
        ],
        [InlineKeyboardButton("𝘾𝙝𝙖𝙣𝙣𝙚𝙡 💫", url="https://t.me/example")],
        [exit_button],
    ]
)

buttons_gates = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("𝘼𝙪𝙩𝙝 ", "auths"),
            InlineKeyboardButton("𝘾𝙝𝙖𝙧𝙜𝙚𝙙 ", "chargeds"),
        ],
        [InlineKeyboardButton("𝙎𝙥𝙚𝙘𝙞𝙖𝙡 ", "specials")],
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "home")],
        [exit_button],
    ]
)

return_home_and_exit = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "home")],
        [exit_button],
    ]
)

return_and_exit_gates = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — AUTH PAGE
# ----------------------------------------------------

text_gates_auth = f"""
𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝

{symbol("朱 𝙀𝙭𝙖𝙢𝙥𝙡𝙚")} -» <code>Sample Auth System</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.auth_demo</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙎𝙚𝙘𝙪𝙧𝙚")} -» <code>User Validation</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.verify</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>
"""

buttons_auth_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — CHARGED PAGE
# ----------------------------------------------------

text_gates_charged = f"""
𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙

{symbol("朱 𝙁𝙚𝙚 𝙎𝙞𝙢𝙪𝙡𝙖𝙩𝙤𝙧")} -» <code>Fee Calculator</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.fees</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙏𝙚𝙨𝙩 𝙋𝙖𝙮")} -» <code>Demo Transaction</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.demo_pay</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>
"""

buttons_charged_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# GATES — SPECIAL PAGE
# ----------------------------------------------------

text_gates_specials = f"""
𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙎𝙥𝙚𝙘𝙞𝙖𝙡

{symbol("朱 𝙋𝙧𝙤 𝙏𝙤𝙤𝙡")} -» <code>Advanced Checker</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.procheck</code> -» <code>Premium</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙎𝙘𝙖𝙣𝙣𝙚𝙧")} -» <code>System Scanner</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.scan</code> -» <code>Premium</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>
"""

buttons_specials_page_1 = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
        [exit_button],
    ]
)

# ----------------------------------------------------
# TOOLS
# ----------------------------------------------------

text_tools = f"""
𝙏𝙤𝙤𝙡𝙨 🛠

{symbol("朱 𝙄𝙣𝙛𝙤")} -» <code>user info lookup</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.info</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙍𝙖𝙣𝙙𝙤𝙢")} -» <code>random generator</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.rnd</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙀𝙘𝙝𝙤")} -» <code>echo text</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.echo text</code> -» <code>Free</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>
"""

# ----------------------------------------------------
# CALLBACK HANDLERS
# ----------------------------------------------------



@Client.on_message(filters.command("start"))
async def start_menu(client: Client, message: Message):
    user_id = message.from_user.id
    await message.reply(
        text_home.format(user_id),
        reply_markup=buttons_home
    )

@Client.on_callback_query(filters.regex("^home$"))
async def cb_home(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    await query.message.edit_text(
        text_home.format(user_id),
        reply_markup=buttons_home
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^gates$"))
async def cb_gates(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 ♻️",
        reply_markup=buttons_gates
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^auths$"))
async def cb_auth(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text_gates_auth,
        reply_markup=buttons_auth_page_1
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^chargeds$"))
async def cb_charged(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text_gates_charged,
        reply_markup=buttons_charged_page_1
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^specials$"))
async def cb_specials(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text_gates_specials,
        reply_markup=buttons_specials_page_1
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^tools$"))
async def cb_tools(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        text_tools,
        reply_markup=return_home_and_exit
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^exit$"))
async def cb_exit(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "𝙀𝙭𝙞𝙩𝙚𝙙 𝙢𝙚𝙣𝙪 ⚠️\n\nUse /start to open it again."
    )
    await query.answer("Exited.")
