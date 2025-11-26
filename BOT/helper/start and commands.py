from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from utilsdf.functions import symbol   # your symbol function

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

async def send_video_or_text(message, text, buttons):
    video_file = get_next_menu_video()
    try:
        with open(video_file, "rb") as v:
            await message.reply_video(
                video=v,
                caption=text,
                reply_markup=buttons
            )
    except:
        await message.reply(
            text,
            reply_markup=buttons
        )

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
            InlineKeyboardButton("𝘼𝙪𝙩𝙝", "auths"),
            InlineKeyboardButton("𝘾𝙝𝙖𝙧𝙜𝙚𝙙", "chargeds"),
        ],
        [InlineKeyboardButton("𝙎𝙥𝙚𝙘𝙞𝙖𝙡", "specials")],
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
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
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
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
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
        [InlineKeyboardButton("𝙍𝙚𝙩𝙪𝙧𝙣 🔄", "gates")],
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
# CALLBACK HANDLERS WITH VIDEO (ADDED)
# ----------------------------------------------------

@Client.on_message(filters.command("start"))
async def start_menu(client: Client, message: Message):
    user_id = message.from_user.id
    await send_video_or_text(message, text_home.format(user_id), buttons_home)

@Client.on_callback_query(filters.regex("^home$"))
async def cb_home(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    await query.message.delete()
    await send_video_or_text(query.message, text_home.format(user_id), buttons_home)
    await query.answer()

@Client.on_callback_query(filters.regex("^gates$"))
async def cb_gates(client: Client, query: CallbackQuery):
    await query.message.delete()
    await send_video_or_text(
        query.message,
        "<a href='https://t.me/spid_3r'>〄</a>𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙩𝙤 𝙎𝙥𝙮𝙙𝙚\n\n"
        "║<a href='https://t.me/spid_3r'>㊕</a>║ 𝙏𝙤𝙩𝙖𝙡 -» 5\n"
        "║<a href='https://t.me/spid_3r'>㊡</a>║ 𝙊𝙣 -» 1 ✓\n"
        "║<a href='https://t.me/spid_3r'>㊤</a>║ 𝙊𝙛𝙛 -» 4 ❌\n"
        "║<a href='https://t.me/spid_3r'>㊬</a> 》𝙈𝙖𝙣𝙩𝙚𝙣𝙞𝙚𝙣𝙘𝙚 -» 4 ⚠️\n\n"
        "〈<a href='https://t.me/spid_3r'>ゼ</a>〉 𝙎𝙚𝙡𝙚𝙘𝙩 𝙮𝙤𝙪𝙧 𝙜𝙖𝙩𝙚!",
        buttons_gates
    )
    await query.answer()

@Client.on_callback_query(filters.regex("^auths$"))
async def cb_auth(client: Client, query: CallbackQuery):
    await query.message.delete()
    await send_video_or_text(query.message, text_gates_auth, buttons_auth_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^chargeds$"))
async def cb_charged(client: Client, query: CallbackQuery):
    await query.message.delete()
    await send_video_or_text(query.message, text_gates_charged, buttons_charged_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^specials$"))
async def cb_specials(client: Client, query: CallbackQuery):
    await query.message.delete()
    await send_video_or_text(query.message, text_gates_specials, buttons_specials_page_1)
    await query.answer()

@Client.on_callback_query(filters.regex("^tools$"))
async def cb_tools(client: Client, query: CallbackQuery):
    await query.message.delete()
    await send_video_or_text(query.message, text_tools, return_home_and_exit)
    await query.answer()

@Client.on_callback_query(filters.regex("^exit$"))
async def cb_exit(client: Client, query: CallbackQuery):
    await query.message.edit_text(
        "𝙀𝙭𝙞𝙩𝙚𝙙 𝙢𝙚𝙣𝙪 ⚠️\n\nUse /start to open it again."
    )
    await query.answer("Exited.")
