import asyncio
import time
from datetime import date
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.defs import *
from FUNC.usersdb_func import *


# ============================
# /cmds COMMAND
# ============================

@Client.on_message(filters.command("cmds", [".", "/"]))
async def cmd_scr(client, message):
    try:
        WELCOME_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> !

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊 provides AUTH, CHARGE, TOOLS and more.

Tap a button below:</b>
"""

        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH / B3 / VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]

        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS)
        )

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


# ============================
# START COMMAND WITH ANIMATION
# ============================

@Client.on_message(filters.command("start", [".", "/"]))
async def cmd_start(client, message):
    try:
        frames = [
            "<b>𝐒</b>",
            "<b>𝐒𝐏</b>",
            "<b>𝐒𝐏𝐘</b>",
            "<b>𝐒𝐏𝐘𝐃</b>",
            "<b>𝐒𝐏𝐘𝐃𝐄</b>",
            "<b>𝐒𝐏𝐘𝐃𝐄_</b>",
            "<b>𝐒𝐏𝐘𝐃𝐄 𝐂</b>",
            "<b>𝐒𝐏𝐘𝐃𝐄 𝐂𝐇</b>",
            "<b>𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊</b>"
        ]

        edit = await message.reply_text(frames[0])
        await asyncio.sleep(0.2)

        for frame in frames[1:]:
            await edit.edit_text(frame)
            await asyncio.sleep(0.2)

        final_text = f"""
<b>🌟 Hello <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b>

<b>Welcome to SPYDE CHK 🚀</b>

<b>Your bot for gates, tools, checkers & more.</b>
<b>Tap Register to begin.</b>
"""

        buttons = [
            [
                InlineKeyboardButton("Register", callback_data="register"),
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]

        await edit.edit_text(final_text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


# ============================
# REGISTER DATABASE FUNCTION
# ============================

async def register_user(user_id, username, antispam_time, reg_at):
    info = {
        "id": str(user_id),
        "username": str(username),
        "user_proxy": "N/A",
        "dcr": "N/A",
        "dpk": "N/A",
        "dsk": "N/A",
        "amt": "N/A",
        "status": "FREE",
        "plan": "N/A",
        "expiry": "N/A",
        "credit": "50",
        "antispam_time": str(antispam_time),
        "totalkey": "0",
        "reg_at": reg_at,
    }
    usersdb.insert_one(info)


# ============================
# /register COMMAND
# ============================

@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(client, message):
    try:
        user = message.from_user
        user_id = user.id
        username = user.username
        antispam_time = int(time.time())

        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"

        check = usersdb.find_one({"id": str(user_id)}, {"_id": 0})

        buttons = [
            [InlineKeyboardButton("Commands", callback_data="cmds")],
            [InlineKeyboardButton("Close", callback_data="close")]
        ]

        if check is None:
            await register_user(user_id, username, antispam_time, reg_at)

            resp = f"""
<b>✔ Registration Successful!</b>

● Name: {user.first_name}  
● User ID: {user_id}  
● Role: Free  
● Credits: 50  

<b>You received 50 bonus credits!</b>
"""

        else:
            resp = f"""
<b>⚠ You Are Already Registered</b>
"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


# ============================
# REGISTER BUTTON CALLBACK FIXED
# ============================

@Client.on_callback_query(filters.regex("register"))
async def callback_register(client, query):
    try:
        user = query.from_user
        user_id = user.id
        username = user.username
        antispam_time = int(time.time())

        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"

        check = usersdb.find_one({"id": str(user_id)}, {"_id": 0})

        buttons = [
            [InlineKeyboardButton("Commands", callback_data="cmds")],
            [InlineKeyboardButton("Close", callback_data="close")]
        ]

        if check is None:
            await register_user(user_id, username, antispam_time, reg_at)

            resp = f"""
<b>✔ Registration Successful!</b>

● Name: {user.first_name}
● User ID: {user_id}
● Role: Free
● Credits: 50

<b>You got 50 registration credits!</b>
"""

        else:
            resp = f"""
<b>⚠ Already Registered</b>
"""

        await query.message.edit_text(resp, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

@Client.on_callback_query()
@Client.on_callback_query()
async def callback_query(Client, CallbackQuery):
    if CallbackQuery.data == "cmds":
        await callback_command(Client, CallbackQuery.message)

    if CallbackQuery.data == "register":
        await callback_register(Client, CallbackQuery.message)

    if CallbackQuery.data == "HOME":
        WELCOME_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 User!

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊𝗛𝗮𝘀 𝗽𝗹𝗲𝗻𝘁𝘆 𝗼𝗳 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀.𝗪𝗲 𝗛𝗮𝘃𝗲 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀, 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀,𝗧𝗼𝗼𝗹𝘀 𝗔𝗻𝗱 𝗢𝘁𝗵𝗲𝗿 𝗧𝗵𝗶𝗻𝗴𝘀.

𝗖𝗹𝗶𝗰𝗸 𝗘𝗮𝗰𝗵 𝗼𝗳 𝗧𝗵𝗲𝗺 𝗕𝗲𝗹𝗼𝘄 𝘁𝗼 𝗞𝗻𝗼𝘄 𝗧𝗵𝗲𝗺 𝗕𝗲𝘁𝘁𝗲𝗿.</b>
    """
        WELCOME_BUTTONS = [
            [
                InlineKeyboardButton("AUTH/B3/VBV", callback_data="AUTH"),
                InlineKeyboardButton("CHARGE", callback_data="CHARGE")
            ],
            [
                InlineKeyboardButton("TOOLS", callback_data="TOOLS"),
                InlineKeyboardButton("HELPER", callback_data="HELPER")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    if CallbackQuery.data == "close":
        await CallbackQuery.message.delete()
        await CallbackQuery.message.reply_text("𝗘𝗻𝗷𝗼𝘆")


    if CallbackQuery.data == "AUTH":
        AUTH_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 𝗨𝘀𝗲𝗿!

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀.

𝗖𝗹𝗶𝗰𝗸 𝗼𝗻 𝗲𝗮𝗰𝗵 𝗼𝗳 𝘁𝗵𝗲𝗺 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝘁𝗼  𝗸𝗻𝗼𝘄 𝘁𝗵𝗲𝗺 𝗯𝗲𝘁𝘁𝗲𝗿.</b>
    """
        AUTH_BUTTONS = [
    [
        InlineKeyboardButton("Stripe Auth", callback_data="Auth2"),
        InlineKeyboardButton("Adyen Auth", callback_data="Adyen2"),
    ],
    [
        InlineKeyboardButton("Braintree B3", callback_data="BRAINTREEB3"),
        InlineKeyboardButton("Braintree VBV", callback_data="BRAINTREEVBV"),
    ],
    [
        InlineKeyboardButton("Clover Auth", callback_data="CLOVERAUTH"),
        InlineKeyboardButton("Square Auth", callback_data="SQUAREAUTH"),
    ],
    [
        InlineKeyboardButton("Back", callback_data="HOME"),
        InlineKeyboardButton("Close", callback_data="close")
    ]
]
        await CallbackQuery.edit_message_text(
            text=AUTH_TEXT,
            reply_markup=InlineKeyboardMarkup(AUTH_BUTTONS))
    if CallbackQuery.data == "Auth2":
        CHARGE_TEXT = """
🔹 𝗦𝗧𝗥𝗜𝗣𝗘 𝗔𝗨𝗧𝗛 𝗚𝗔𝗧𝗘𝗦 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗦𝘁𝗿𝗶𝗽𝗲 𝗔𝘂𝘁𝗵 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:

   1. 𝗦𝘁𝗿𝗶𝗽𝗲 𝗔𝘂𝘁𝗵:
     ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /au cc|mm|yy|cvv ✅
      ➜ 𝗠𝗮𝘀𝘀: /mass cc|mm|yy|cvv ✅

𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "Adyen2":
        CHARGE_TEXT = """
🔹 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: 𝗔𝗰𝘁𝗶𝘃𝗲 ❌

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /ad cc|mm|yy|cvv ❌
      ➜ 𝗠𝗮𝘀𝘀: /mad cc|mm|yy|cvv ❌

𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BRAINTREEVBV":
        CHARGE_TEXT = """
🔹 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗩𝗕𝗩 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗩𝗕𝗩 𝗟𝗼𝗼𝗸𝘂𝗽 𝗚𝗮𝘁𝗲:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /vbv cc|mm|yy|cvv ✅
      ➜ 𝗠𝗮𝘀𝘀 (𝗟𝗶𝗺𝗶𝘁=𝟮𝟱): /mvbv cc|mm|yy|cvv ✅

𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )

    if CallbackQuery.data == "BRAINTREEB3":
        CHARGE_TEXT = """
🔹 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵 𝗼𝗳 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵 1 𝗚𝗮𝘁𝗲: ✅
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /chk cc|mm|yy|cvv 
      ➜ 𝗠𝗮𝘀𝘀 : /mchk cc|mm|yy|cvv        
   2. 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵 2 𝗚𝗮𝘁𝗲: ✅
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /b3 cc|mm|yy|cvv 
      ➜ 𝗠𝗮𝘀𝘀 (𝗟𝗶𝗺𝗶𝘁=25): /mb3 cc|mm|yy|cvv 
   3. 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵 3 𝗚𝗮𝘁𝗲: ✅
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /b4 cc|mm|yy|cvv 
      ➜ 𝗠𝗮𝘀𝘀: /mb4 cc|mm|yy|cvv
      
  𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 3  

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
        
    if CallbackQuery.data == "SQUAREAUTH":
        CHARGE_TEXT = """
🔹 𝗦𝗾𝘂𝗮𝗿𝗲 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ❌ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗦𝗾𝘂𝗮𝗿𝗲 𝗔𝘂𝘁𝗵 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗦𝗾𝘂𝗮𝗿𝗲 𝗔𝘂𝘁𝗵:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /sq cc|mm|yy|cvv ❌
      ➜ 𝗠𝗮𝘀𝘀: /msq cc|mm|yy|cvv ❌

𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    
    if CallbackQuery.data == "CLOVERAUTH":
        CHARGE_TEXT = """
🔹 𝗖𝗹𝗼𝘃𝗲𝗿 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ❌ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗖𝗹𝗼𝘃𝗲𝗿 𝗔𝘂𝘁𝗵 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗖𝗹𝗼𝘃𝗲𝗿 𝗔𝘂𝘁𝗵:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /cl cc|mm|yy|cvv ❌
      ➜ 𝗠𝗮𝘀𝘀: /mcl cc|mm|yy|cvv ❌

𝗧𝗼𝘁𝗮𝗹 𝗔𝘂𝘁𝗵 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="AUTH"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON))





    if CallbackQuery.data == "CHARGE":
        CHARGE_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 𝗨𝘀𝗲𝗿!

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀.

𝗖𝗹𝗶𝗰𝗸 𝗼𝗻 𝗲𝗮𝗰𝗵 𝗼𝗳 𝘁𝗵𝗲𝗺 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝘁𝗼 𝗸𝗻𝗼𝘄 𝘁𝗵𝗲𝗺 𝗯𝗲𝘁𝘁𝗲𝗿.</b>
    """
        
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("SK Based", callback_data="SKBASED"),
                InlineKeyboardButton("Braintree", callback_data="BRAINTREE"),
            ],
            [
                InlineKeyboardButton("Stripe Api", callback_data="SITE"),
                InlineKeyboardButton("Shopify", callback_data="SHOPIFY"),
            ],
            [
                InlineKeyboardButton("Authnet", callback_data="AUTHNET"),
            ],
            [
                InlineKeyboardButton("Paypal", callback_data="PAYPAL"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))
    if CallbackQuery.data == "PAYPAL":
        CHARGE_TEXT = """
🔹 𝗣𝗮𝘆𝗣𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ❌ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:
👤 𝗣𝗮𝘆𝗣𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗣𝗮𝘆𝗣𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 0.01$: ❌
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /pp cc|mm|yy|cvv [ON] 
      ➜ 𝗠𝗮𝘀𝘀: /mpp cc|mm|yy|cvv [ON] 

   2. 𝗣𝗮𝘆𝗣𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 1$: ❌
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /py cc|mm|yy|cvv [OFF] 
      ➜ 𝗠𝗮𝘀𝘀: /mpy cc|mm|yy|cvv [OFF] 

𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 2

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )  


    if CallbackQuery.data == "SKBASED":
        CHARGE_TEXT = """
🔹 𝗦𝗧𝗥𝗜𝗣𝗘 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:
👤 𝗦𝘁𝗿𝗶𝗽𝗲 𝗖𝗵𝗮𝗿𝗴𝗲 𝗢𝗽𝘁𝗶𝗼𝗻𝘀: ✅
   1. SK BASED CHARGE 0.5$ CVV:
      ➜ Single: /svv cc|mm|yy|cvv ✅
      ➜ Mass: /msvv cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /svvtxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

   2. SK BASED 0.5$ CCN CHARGE:
      ➜ Single: /ccn cc|mm|yy|cvv ✅
      ➜ Mass: /mccn cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /ccntxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

   3. SK BASED 0.5$ CVV CHARGE:
      ➜ Single: /cvv cc|mm|yy|cvv ✅
      ➜ Mass: /mcvv cc|mm|yy|cvv ✅
      ➜ Mass txt (Limit=3k): /cvvtxt [in reply to file] ✅
      ➜ Self SK also added, check: /selfcmd ✅

𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 3

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SITE":
        CHARGE_TEXT = """
🔹 𝗦𝗶𝘁𝗲 𝗕𝗮𝘀𝗲𝗱 𝗔𝗽𝗶 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 Site Charge Options:
   1. 𝗡𝗢𝗡 𝗦𝗞 𝗖𝗩𝗩 5$ 𝗖𝗛𝗔𝗥𝗚𝗘𝗗: ✅
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /sch cc|mm|yy|cvv 
      ➜ 𝗠𝗮𝘀𝘀: /msch cc|mm|yy|cvv
      
   2. 𝗡𝗢𝗡 𝗦𝗞 𝗖𝗩𝗩 5$ 𝗖𝗛𝗔𝗥𝗚𝗘𝗗: ✅
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /st1 cc|mm|yy|cvv 
      ➜ 𝗠𝗮𝘀𝘀: /mst1 cc|mm|yy|cvv

   𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 2

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BRAINTREE":
        CHARGE_TEXT = """
🔹 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ❌ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗖𝗵𝗮𝗿𝗴𝗲 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗖𝗵𝗮𝗿𝗴𝗲 1£:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /br cc|mm|yy|cvv [off]
      ➜ 𝗠𝗮𝘀𝘀: /mbr cc|mm|yy|cvv [off]

𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SHOPIFY":
        CHARGE_TEXT = """

🔹 Shopify Charge Gates of 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 Status: ✅ Active

🚀 Quick Commands Overview:

👤 Shopify Charge Options:
   1. Shopify Charge 10$:
      ➜ Single: /sh cc|mm|yy|cvv ✅
      ➜ Mass: /msh cc|mm|yy|cvv ✅

   2. Shopify Charge 27.51$:
      ➜ Single: /so cc|mm|yy|cvv ✅
      ➜ Mass: /mso cc|mm|yy|cvv ✅

   3. Shopify Charge 20$:
      ➜ Single: /sho cc|mm|yy|cvv ✅
      ➜ Mass: /msho cc|mm|yy|cvv ✅

   4. Shopify Charge 20$:
      ➜ Single: /sg cc|mm|yy|cvv ✅
      ➜ Mass: /msg cc|mm|yy|cvv ✅

𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 4

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "AUTHNET":
        CHARGE_TEXT = """
🔹 Authnet Charge 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 Authnet 𝗖𝗵𝗮𝗿𝗴𝗲 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. Authnet 𝗖𝗵𝗮𝗿𝗴𝗲 $3:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /nt cc|mm|yy|cvv 
      
𝗧𝗼𝘁𝗮𝗹 𝗖𝗵𝗮𝗿𝗴𝗲 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 1

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="CHARGE"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )    
        
    if CallbackQuery.data == "TOOLS":
        TOOLS_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 𝗨𝘀𝗲𝗿!

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊𝗧𝗼𝗼𝗹𝘀.

𝗖𝗹𝗶𝗰𝗸 𝗼𝗻 𝗲𝗮𝗰𝗵 𝗼𝗳 𝘁𝗵𝗲𝗺 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝘁𝗼 𝗸𝗻𝗼𝘄 𝘁𝗵𝗲𝗺 𝗯𝗲𝘁𝘁𝗲𝗿.</b>
    """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("Scrapper", callback_data="SCRAPPER"),
                InlineKeyboardButton("SK TOOLS", callback_data="SKSTOOL"),
            ],
            [
                InlineKeyboardButton(
                    "Genarator", callback_data="GENARATORTOOLS"),
                InlineKeyboardButton(
                    "Bin & Others", callback_data="BINANDOTHERS"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=TOOLS_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))

    if CallbackQuery.data == "SKSTOOL":
        CHARGE_TEXT = """
🔹 𝗦𝗞 𝗧𝗼𝗼𝗹𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗦𝗞 𝗧𝗼𝗼𝗹𝘀:
   1. 𝗦𝗞 𝗞𝗲𝘆 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗚𝗮𝘁𝗲: /sk sk_live_xxxxxx ✅ (𝗟𝗶𝗺𝗶𝘁: 𝗦𝗶𝗻𝗴𝗹𝗲)
   2. 𝗦𝗞 𝗧𝗼 𝗣𝗞 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿 𝗚𝗮𝘁𝗲: /pk sk_live_xxxxxx ✅ (𝗟𝗶𝗺𝗶𝘁: 𝗦𝗶𝗻𝗴𝗹𝗲)
   3. 𝗦𝗞 𝗨𝘀𝗲𝗿 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗚𝗮𝘁𝗲: /skuser sk_live_xxxxxx ✅ (𝗟𝗶𝗺𝗶𝘁: 𝗦𝗶𝗻𝗴𝗹𝗲)
   4. 𝗦𝗞 𝗜𝗻𝗳𝗼 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗚𝗮𝘁𝗲: /skinfo sk_live_xxxxxx ✅ (𝗟𝗶𝗺𝗶𝘁: 𝗦𝗶𝗻𝗴𝗹𝗲)

𝗧𝗼𝘁𝗮𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 4

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "SCRAPPER":
        CHARGE_TEXT = """
🔹 𝗦𝗰𝗿𝗮𝗽𝗽𝗲𝗿 𝗧𝗼𝗼𝗹𝘀 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 𝗧𝗼𝗼𝗹𝘀:
   1. 𝗖𝗖 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 𝗚𝗮𝘁𝗲: /scr channel_username 100 ✅ (𝗟𝗶𝗺𝗶𝘁: 5K)
   2. 𝗕𝗶𝗻 𝗕𝗮𝘀𝗲𝗱 𝗖𝗖 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 𝗚𝗮𝘁𝗲: /scrbin 440393 channel_username 100 ✅ (𝗟𝗶𝗺𝗶𝘁: 5K)
   3. 𝗦𝗞 𝗦𝗰𝗿𝗮𝗽𝗲𝗿 𝗚𝗮𝘁𝗲: /scrsk channel_username 100 ✅ (𝗟𝗶𝗺𝗶𝘁: 5K)

𝗧𝗼𝘁𝗮𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 3

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "GENARATORTOOLS":
        CHARGE_TEXT = """
🔹 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿 𝗧𝗼𝗼𝗹𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿 𝗧𝗼𝗼𝗹𝘀:
   1. 𝗥𝗮𝗻𝗱𝗼𝗺 𝗖𝗖 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿 𝗚𝗮𝘁𝗲: /gen 440393 500 ✅ (𝗟𝗶𝗺𝗶𝘁: 10k)
   2. 𝗙𝗮𝗸𝗲 𝗔𝗱𝗱𝗿𝗲𝘀𝘀 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗼𝗿 𝗚𝗮𝘁𝗲: /fake us ✅

𝗧𝗼𝘁𝗮𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 2

"""
        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )
    if CallbackQuery.data == "BINANDOTHERS":
        CHARGE_TEXT = """
🔹 𝗕𝗶𝗻 𝗮𝗻𝗱 𝗢𝘁𝗵𝗲𝗿 𝗧𝗼𝗼𝗹𝘀 𝗢𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼 𝗖𝗵𝗲𝗰𝗸𝗲𝗿𝘀:
   1. 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗚𝗮𝘁𝗲: /bin 440393 ✅ (𝗦𝗶𝗻𝗴𝗹𝗲 𝗟𝗶𝗺𝗶𝘁)
   2. 𝗧𝗲𝘅𝘁 𝗧𝗼 𝗖𝗖 𝗙𝗶𝗹𝘁𝗲𝗿 𝗚𝗮𝘁𝗲: /fl [in reply to text] ✅
   3. 𝗠𝗮𝘀𝘀 𝗕𝗜𝗡 𝗜𝗻𝗳𝗼 𝗖𝗵𝗲𝗰𝗸𝗲𝗿 𝗚𝗮𝘁𝗲: /massbin 440393 ❌ (𝗟𝗶𝗺𝗶𝘁: 30)

💡 𝗔𝗱𝗱𝗶𝘁𝗶𝗼𝗻𝗮𝗹 𝗧𝗼𝗼𝗹𝘀:
   4. 𝗜𝗣 𝗟𝗼𝗼𝗸𝘂𝗽 𝗚𝗮𝘁𝗲: /ip your_ip ✅
   5. 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀 𝗛𝘂𝗻𝘁𝗲𝗿 𝗚𝗮𝘁𝗲: /url website_url ✅ (𝗟𝗶𝗺𝗶𝘁: 20)
   6. 𝗚𝗣𝗧-𝟰: /gpt Promote ❌

𝗧𝗼𝘁𝗮𝗹  𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 6


"""

        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="TOOLS"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )

    if CallbackQuery.data == "HELPER":
        HELPER_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 𝗨𝘀𝗲𝗿!

𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊 𝗛𝗲𝗹𝗽𝗲𝗿.

𝗖𝗹𝗶𝗰𝗸 𝗼𝗻 𝗲𝗮𝗰𝗵 𝗼𝗳 𝘁𝗵𝗲𝗺 𝗯𝗲𝗹𝗼𝘄 𝘁𝗼 𝗴𝗲𝘁 𝘁𝗼 𝗸𝗻𝗼𝘄 𝘁𝗵𝗲𝗺 𝗯𝗲𝘁𝘁𝗲𝗿.</b>
    """
        CHARGE_BUTTONS = [
            [
                InlineKeyboardButton("Helper", callback_data="INFO"),
                # InlineKeyboardButton("SK TOOLS", callback_data="SKTOOLS"),
            ],
            [
                InlineKeyboardButton("Back", callback_data="HOME"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=HELPER_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTONS))
    if CallbackQuery.data == "INFO":
        CHARGE_TEXT = """
🔹 𝗛𝗲𝗹𝗽𝗲𝗿 𝗚𝗮𝘁𝗲𝘀 𝗼𝗳 𝐒𝐏𝐈𝐋𝐔𝐗 𝐂𝐂 𝐁𝐎𝐓
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: ✅ 𝗔𝗰𝘁𝗶𝘃𝗲

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁:
   1. 𝗦𝘁𝗮𝗿𝘁 𝗕𝗼𝘁: /start
   2. 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿: /register
   3. 𝗨𝘀𝗲𝗿 𝗜𝗗: /id
   4. 𝗨𝘀𝗲𝗿 𝗜𝗻𝗳𝗼: /info
   5. 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗕𝗮𝗹𝗮𝗻𝗰𝗲: /credits

💡 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 & 𝗣𝗿𝗲𝗺𝗶𝘂𝗺𝘀:
   6. 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗦𝘆𝘀𝘁𝗲𝗺: /howcrd
   7. 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗿𝗶𝘃𝗶𝗹𝗲𝗴𝗲𝘀: /howpm
   8. 𝗕𝘂𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺: /buy

👥 𝗖𝗼𝗺𝗺𝘂𝗻𝗶𝘁𝘆 𝗧𝗼𝗼𝗹𝘀:
   9. 𝗔𝗱𝗱 𝘁𝗼 𝗚𝗿𝗼𝘂𝗽: /howgp

📡 𝗧𝗲𝗰𝗵 𝗦𝘂𝗽𝗽𝗼𝗿𝘁:
   10. 𝗣𝗶𝗻𝗴 𝗦𝘁𝗮𝘁𝘂𝘀: /ping

𝗧𝗼𝘁𝗮𝗹 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀: 10

        """

        CHARGE_BUTTON = [
            [
                InlineKeyboardButton("Back", callback_data="HELPER"),
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await CallbackQuery.edit_message_text(
            text=CHARGE_TEXT,
            reply_markup=InlineKeyboardMarkup(CHARGE_BUTTON)
        )


