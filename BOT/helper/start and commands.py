import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.defs import *
from FUNC.usersdb_func import *


@Client.on_message(filters.command("cmds", [".", "/"]))
async def cmd_scr(client, message):
    try:
        WELCOME_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 <a href="tg://user?id={message.from_user.id}"> {message.from_user.first_name}</a> !

𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑 𝗛𝗮𝘀 𝗽𝗹𝗲𝗻𝘁𝘆 𝗼𝗳 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀. 𝗪𝗲 𝗛𝗮𝘃𝗲 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀, 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀, 𝗧𝗼𝗼𝗹𝘀, 𝗔𝗻𝗱 𝗢𝘁𝗵𝗲𝗿 𝗧𝗵𝗶𝗻𝗴𝘀.

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
        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_command(client, message):
    try:
        WELCOME_TEXT = f"""
<b>𝗛𝗲𝗹𝗹𝗼 𝗨𝘀𝗲𝗿!

𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑  𝗛𝗮𝘀 𝗽𝗹𝗲𝗻𝘁𝘆 𝗼𝗳 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀. 𝗪𝗲 𝗛𝗮𝘃𝗲 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀, 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀, 𝗧𝗼𝗼𝗹𝘀, 𝗔𝗻𝗱 𝗢𝘁𝗵𝗲𝗿 𝗧𝗵𝗶𝗻𝗴𝘀.

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
        await message.reply(
            text=WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(WELCOME_BUTTONS))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("start", [".", "/"]))
async def cmd_start(Client, message):
    try:
        user = message.from_user
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'


        frames = [
            "<b>[▱▱▱▱▱▱] Booting System...</b>",
            "<b>[▰▱▱▱▱▱] Initializing Core</b>",
            "<b>[▰▰▱▱▱▱] Loading ⚡Modules...</b>",
            "<b>[▰▰▰▱▱▱] Injecting Scripts...</b>",
            "<b>[▰▰▰▰▱▱] Connecting to Gateways...</b>",
            "<b>[▰▰▰▰▰▱] Launching Interface...</b>",
            "<b>[▰▰▰▰▰▰] ✅ Ready</b>",
            "<b>𝗖𝗛𝗔𝗥𝗚𝗘 𝗠𝗔𝗦𝗧𝗘𝗥™ ONLINE ⚙️</b>"
        ]

        edit = await message.reply_text(frames[0])
        for frame in frames[1:]:
            await asyncio.sleep(0.5)
            await Client.edit_message_text(chat_id=message.chat.id, message_id=edit.id, text=frame)
            
        # Typing Effect Simulation
        typing_texts = [
            "<i>Typing.</i>",
            "<i>Typing..</i>",
            "<i>Typing...</i>",
            
        ]
        for t in typing_texts:
            await asyncio.sleep(0.3)
            await Client.edit_message_text(chat_id=message.chat.id, message_id=edit.id, text=t)

        await asyncio.sleep(0.1)

        text = f"""
<b>🌟 𝗛𝗲𝗹𝗹𝗼 <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>!</b>

<b>𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗮𝗯𝗼𝗮𝗿𝗱 𝘁𝗵𝗲 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑! 🚀</b>

<b>𝗜 𝗮𝗺 𝘆𝗼𝘂𝗿 𝗴𝗼-𝘁𝗼 𝗯𝗼𝘁, 𝗽𝗮𝗰𝗸𝗲𝗱 𝘄𝗶𝘁𝗵 𝗮 𝘃𝗮𝗿𝗶𝗲𝘁𝘆 𝗼𝗳 𝗴𝗮𝘁𝗲𝘀, 𝘁𝗼𝗼𝗹𝘀, 𝗮𝗻𝗱 𝗰𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝘁𝗼 𝗲𝗻𝗵𝗮𝗻𝗰𝗲 𝘆𝗼𝘂𝗿 𝗲𝘅𝗽𝗲𝗿𝗶𝗲𝗻𝗰𝗲. 𝗘𝘅𝗰𝗶𝘁𝗲𝗱 𝘁𝗼 𝘀𝗲𝗲 𝘄𝗵𝗮𝘁 𝗜 𝗰𝗮𝗻 𝗱𝗼?</b>

<b>👇 𝗧𝗮𝗽 𝘁𝗵𝗲 <i>𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿</i> 𝗯𝘂𝘁𝘁𝗼𝗻 𝘁𝗼 𝗯𝗲𝗴𝗶𝗻 𝘆𝗼𝘂𝗿 𝗷𝗼𝘂𝗿𝗻𝗲𝘆.</b>
<b>👇 𝗗𝗶𝘀𝗰𝗼𝘃𝗲𝗿 𝗺𝘆 𝗳𝘂𝗹𝗹 𝗰𝗮𝗽𝗮𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗯𝘆   
𝘁𝗮𝗽𝗽𝗶𝗻𝗴 𝘁𝗵𝗲 <i>𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀</i> 𝗯𝘂𝘁𝘁𝗼𝗻.</b>

"""
        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Register", callback_data="register"),
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        await Client.edit_message_text(message.chat.id, edit.id, text, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except:
        import traceback
        await error_log(traceback.format_exc())


async def register_user(user_id, username, antispam_time, reg_at):
    info = {
        "id": f"{user_id}",
        "username": f"{username}",
        "user_proxy":f"N/A",
        "dcr": "N/A",
        "dpk": "N/A",
        "dsk": "N/A",
        "amt": "N/A",
        "status": "FREE",
        "plan": f"N/A",
        "expiry": "N/A",
        "credit": "100",
        "antispam_time": f"{antispam_time}",
        "totalkey": "0",
        "reg_at": f"{reg_at}",
    }
    usersdb.insert_one(info)


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("register", [".", "/"]))
async def cmd_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


async def callback_register(Client, message):
    try:
        user_id = str(message.from_user.id)
        username = str(message.from_user.username)
        antispam_time = int(time.time())
        yy, mm, dd = str(date.today()).split("-")
        reg_at = f"{dd}-{mm}-{yy}"
        find = usersdb.find_one({"id": f"{user_id}"}, {"_id": 0})
        registration_check = str(find)

        WELCOME_BUTTON = [
            [
                InlineKeyboardButton("Commands", callback_data="cmds")
            ],
            [
                InlineKeyboardButton("Close", callback_data="close")
            ]
        ]
        if registration_check == "None":
            await register_user(user_id, username, antispam_time, reg_at)
            resp = f"""<b>
𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹 ♻️ 
━━━━━━━━━━━━━━
● 𝗡𝗮𝗺𝗲: {message.from_user.first_name}
● 𝗨𝘀𝗲𝗿 𝗜𝗗: {message.from_user.id}
● 𝗥𝗼𝗹𝗲: Free
● 𝗖𝗿𝗲𝗱𝗶𝘁𝘀: 50

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗚𝗼𝘁 50 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗮𝘀 𝗮       𝗿𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗯𝗼𝗻𝘂𝘀 . 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗖𝗿𝗲𝗱𝗶𝘁𝘀  𝗦𝘆𝘀𝘁𝗲𝗺 /howcrd


𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀         𝗕𝘂𝘁𝘁𝗼𝗻.  
            </b>"""

        else:
            resp = f"""<b>
𝗔𝗹𝗿𝗲𝗮𝗱𝘆 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗶𝗻 𝗼𝘂𝗿 𝗯𝗼𝘁 . 𝗡𝗼 𝗻𝗲𝗲𝗱 𝘁𝗼 𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗻𝗼𝘄 

𝗘𝘅𝗽𝗹𝗼𝗿𝗲 𝗠𝘆 𝗩𝗮𝗿𝗶𝗼𝘂𝘀 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗔𝗻𝗱 𝗔𝗯𝗶𝗹𝗶𝘁𝗶𝗲𝘀 𝗕𝘆 𝗧𝗮𝗽𝗽𝗶𝗻𝗴 𝗼𝗻 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗕𝘂𝘁𝘁𝗼𝗻  
            </b>"""

        await message.reply_text(resp, reply_markup=InlineKeyboardMarkup(WELCOME_BUTTON))

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

𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑 𝗛𝗮𝘀 𝗽𝗹𝗲𝗻𝘁𝘆 𝗼𝗳 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀.𝗪𝗲 𝗛𝗮𝘃𝗲 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀, 𝗖𝗵𝗮𝗿𝗴𝗲 𝗚𝗮𝘁𝗲𝘀,𝗧𝗼𝗼𝗹𝘀 𝗔𝗻𝗱 𝗢𝘁𝗵𝗲𝗿 𝗧𝗵𝗶𝗻𝗴𝘀.

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

𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀.

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
🔹 𝗦𝗧𝗥𝗜𝗣𝗘 𝗔𝗨𝗧𝗛 𝗚𝗔𝗧𝗘𝗦
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
🔹 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵 𝗚𝗮𝘁𝗲𝘀
🔹 𝗦𝘁𝗮𝘁𝘂𝘀: 𝗔𝗰𝘁𝗶𝘃𝗲 ✅

🚀 𝗤𝘂𝗶𝗰𝗸 𝗖𝗼𝗺𝗺𝗮𝗻𝗱𝘀 𝗢𝘃𝗲𝗿𝘃𝗶𝗲𝘄:

👤 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵 𝗢𝗽𝘁𝗶𝗼𝗻𝘀:
   1. 𝗔𝗱𝘆𝗲𝗻 𝗔𝘂𝘁𝗵:
      ➜ 𝗦𝗶𝗻𝗴𝗹𝗲: /ad cc|mm|yy|cvv ✅
      ➜ 𝗠𝗮𝘀𝘀: /mad cc|mm|yy|cvv ✅

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
🔹 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗚𝗮𝘁𝗲𝘀
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
🔹 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲 𝗔𝘂𝘁𝗵
🔹 𝗦𝘁
