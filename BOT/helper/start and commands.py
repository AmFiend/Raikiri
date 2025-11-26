from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from utilsdf.functions import symbol   # your symbol function

# ----------------------------------------------------
# TEXTS
# ----------------------------------------------------

text_home = """        f"<a href='https://t.me/spid_3r'>朱</a> 𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚 𝘾𝙝𝙚𝙘𝙠𝙚𝙧\n\n"
        f"<a href='https://t.me/spid_3r'>㊄</a> Spyde is renewed, we present our new improved version, with fast and secure checks with different payment gateways and perfect tools for your use.\n\n"
        f"<a href='https://t.me/spid_3r'>╰┈➤</a> 𝙑𝙚𝙧𝙨𝙞𝙤𝙣  -» 1.0"
# ----------------------------------------------------
# BUTTONS
# ----------------------------------------------------
            
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
            "〈<a href='https://t.me/spid_3r'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘼𝙪𝙩𝙝\n\n"
            "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝗔𝗱𝗿𝗶 -» Zuora + Stripe -» Auth\n"
            "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .adr -» Free\n"
            "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌️\n\n"
            "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘼𝙠𝙩𝙯 -» braintree -» Auth\n"
            "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .b3 -» Free\n"
            "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙎𝙚𝙭 -» Intuit -» Auth\n"
            "〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .sx -» Premium\n"
            "〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌"

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
"〈<a href='https://t.me/spid_3r'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝘾𝙝𝙖𝙧𝙜𝙚𝙙\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙉𝙞𝙜𝙝𝙩 -» Moneris -» $0.01\n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .ni -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙁𝙧𝙞𝙚𝙣𝙙 -» ePay -» $0.01\n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .fr -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘼𝙨𝙪𝙢𝙖 -» Authorize.net -» $0.01\n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .as -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝘿𝙞𝙤𝙢𝙚𝙙𝙚𝙨 -» Tunl -» $0.01\n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .di -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙋𝙖𝙮𝙋𝙖𝙡 -» PayPal -» $0.01\n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .pp -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌>\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙏𝙧𝙞𝙙𝙚𝙣𝙩 -» Transax Gateway -» $0.01 \n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .tr -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Mantenience ⚠️\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙋𝙚𝙧𝙞𝙘𝙤 -» wc Sagepay(Opayo) -» €1.00 \n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .pr -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
"〈<a href='https://t.me/spid_3r'>朱</a>〉 𝙅𝙪𝙖𝙣 -» WorldPay -» ₤0.89 \n"
"〈<a href='https://t.me/spid_3r'>零</a>〉 𝘾𝙢𝙙 -» .jn -» Premium \n"
"〈<a href='https://t.me/spid_3r'>ᥫ᭡</a>〉 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌"
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

{symbol("朱 𝙋𝙧𝙤 𝙏𝙤𝙤𝙡")} -» <code>payflow nass</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.mpy</code> -» <code>Premium</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙎𝙘𝙖𝙣𝙣𝙚𝙧")} -» <code>mass stripe</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.mstxt</code> -» <code>Premium</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙎𝙘𝙖𝙣𝙣𝙚𝙧")} -» <code>mass Auto stripe</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.asm</code> -» <code>Premium</code>
{symbol("ᥫ᭡ 𝙎𝙩𝙖𝙩𝙪𝙨")} -» <code>On ✅</code>

{symbol("朱 𝙎𝙘𝙖𝙣𝙣𝙚𝙧")} -» <code>mass stipe</code>
{symbol("零 𝘾𝙢𝙙")} -» <code>.mchk</code> -» <code>Premium</code>
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

            "〈<a href='https://t.me/spid_3r'>朱</a>〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮𝙨 𝙏𝙤𝙤𝙡𝙨 🛠\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙍𝙚𝙛𝙚 -» send review reference\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .refe -» reply message -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝘽𝙞𝙣 -» info bin\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .bin -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝘾𝙝𝙖𝙩 𝙂𝙋𝙏 -» ChatGPT\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .gpt hola -» Premium\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» Off ❌\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝘼𝙙𝙙𝙧𝙚𝙨𝙨 -» generate address\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .rnd us -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙎𝙠 -» info sk\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .sk -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙂𝘽𝙞𝙣 -» generate bins\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .gbin -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝘾𝘾 𝙂𝙚𝙣 -» generate ccs\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .gen -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙄𝙣𝙛𝙤 -» info user\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .my -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙋𝙡𝙖𝙣 -» info plan user\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .plan -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅\n\n"
            "<a href='https://t.me/spid_3r'>朱</a> 𝙋𝙡𝙖𝙣𝙂 -» info plan group\n"
            "<a href='https://t.me/spid_3r'>零</a> 𝘾𝙢𝙙 -» .plang -» Free\n"
            "<a href='https://t.me/spid_3r'>ᥫ᭡</a> 𝙎𝙩𝙖𝙩𝙪𝙨 -» On ✅"
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
        "<a href='https://t.me/spid_3r'>〄</a>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚\n\n"
        "║<a href='https://t.me/spid_3r'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» 5\n"
        "║<a href='https://t.me/spid_3r'>㊡</a>║ 𝙊𝙣 -» 1 ✅\n"
        "║<a href='https://t.me/spid_3r'>㊤</a>║ 𝙊𝙛𝙛 -» 4 ❌\n"
        "║<a href='https://t.me/spid_3r'>㊬</a> 》𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» 4 ⚠️\n\n"
        "〈<a href='https://t.me/spid_3r'>ゼ</a>〉𝙎𝙚𝙡𝙚𝙘𝙩 𝙩𝙝𝙚 𝙩𝙮𝙥𝙚 𝙤𝙛 𝙜𝙖𝙩𝙚 𝙮𝙤𝙪 𝙬𝙖𝙣𝙩 𝙛𝙤𝙧 𝙮𝙤𝙪𝙧 𝙪𝙨𝙚!",
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
