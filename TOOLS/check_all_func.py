from FUNC.usersdb_func import *
import time
from FUNC.defs import *

gate_active    = json.loads(open("FILES/deadsk.json", "r" , encoding="utf-8").read())["gate_active"]


async def check_all_thing(Client , message):
    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""<b>
𝗨𝗻𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗖𝗮𝗻'𝘁 𝗨𝘀𝗲 𝗠𝗲 𝗨𝗻𝗹𝗲𝘀𝘀 𝗬𝗼𝘂 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗙𝗶𝗿𝘀𝘁 .

𝗧𝘆𝗽𝗲 /register 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False , False

        if any(command in message.text for command in gate_active):
            resp = "<b>This gate not available now, please try later 👍</b>"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return False, False, False

        getuser        = await getuserinfo(user_id)
        status         = getuser["status"]
        credit         = int(getuser["credit"])
        antispam_time  = int(getuser["antispam_time"])
        now            = int(time.time())
        count_antispam = now - antispam_time
        checkgroup     = await getchatinfo(chat_id)
        checkgroup     = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            resp = f"""<b>
𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 ⚠️
𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗢𝗻𝗹𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀 𝗮𝗿𝗲 𝗔𝗹𝗹𝗼𝘄𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝗯𝗼𝘁 𝗶𝗻 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 . 𝗔𝗹𝘁𝗵𝗼𝘂𝗴𝗵 𝗬𝗼𝘂 𝗖𝗮𝗻 𝗨𝘀𝗲 𝗕𝗼𝘁 𝗙𝗿𝗲𝗲 𝗛𝗲𝗿𝗲

 👉 https://t.me/+nxCmq8lCNjNlYjZl

𝗕𝘂𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗹𝗮𝗻 𝗨𝘀𝗶𝗻𝗴 /buy 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""<b>
𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗖𝗵𝗮𝘁𝘀 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗢𝗻𝗹𝘆 𝗖𝗵𝗮𝘁𝘀 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗕𝘆 𝗠𝘆 𝗠𝗮𝘀𝘁𝗲𝗿 𝗖𝗮𝗻 𝗢𝗻𝗹𝘆 𝗨𝘀𝗲 𝗠𝗲 . 𝗧𝗼 𝗚𝗲𝘁 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗬𝗼𝘂𝗿 𝗖𝗵𝗮𝘁𝘀 𝗙𝗼𝗹𝗹𝗼𝘄 𝗧𝗵𝗲 𝗦𝘁𝗲𝗽𝘀 .

𝗧𝘆𝗽𝗲 /howgp 𝘁𝗼 𝗞𝗻𝗼𝘄 𝗧𝗵𝗲 𝗦𝘁𝗲𝗽
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if credit < 5:
            resp = f"""<b>
𝗜𝗻𝘀𝘂𝗳𝗳𝗶𝗰𝗶𝗲𝗻𝘁 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗛𝗮𝘃𝗲 𝗜𝗻𝘀𝘂𝗳𝗳𝗶𝗰𝗶𝗲𝗻𝘁 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝘁𝗼 𝗨𝘀𝗲 𝗠𝗲 . 𝗥𝗲𝗰𝗵𝗮𝗿𝗴𝗲 𝗖𝗿𝗲𝗱𝗶𝘁 𝗙𝗼𝗿 𝗨𝘀𝗶𝗻𝗴 𝗠𝗲

𝗧𝘆𝗽𝗲 /buy 𝘁𝗼 𝗥𝗲𝗰𝗵𝗮𝗿𝗴𝗲
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "PREMIUM" and count_antispam < 5:
            after = 5 - count_antispam
            resp = f"""<b>
𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗗𝗼𝗶𝗻𝗴 𝘁𝗵𝗶𝗻𝗴𝘀 𝗩𝗲𝗿𝘆 𝗙𝗮𝘀𝘁 . 𝗧𝗿𝘆 𝗔𝗳𝘁𝗲𝗿 {after}s 𝘁𝗼 𝗨𝘀𝗲 𝗠𝗲 𝗔𝗴𝗮𝗶𝗻 .

𝗥𝗲𝗱𝘂𝗰𝗲 𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 𝗧𝗶𝗺𝗲 /buy 𝗨𝘀𝗶𝗻𝗴 𝗣𝗮𝗶𝗱 𝗣𝗹𝗮𝗻
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "FREE" and count_antispam < 20:
            after = 20 - count_antispam
            resp = f"""<b>
𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗔𝗿𝗲 𝗗𝗼𝗶𝗻𝗴 𝘁𝗵𝗶𝗻𝗴𝘀 𝗩𝗲𝗿𝘆 𝗙𝗮𝘀𝘁 . 𝗧𝗿𝘆 𝗔𝗳𝘁𝗲𝗿 {after}s 𝘁𝗼 𝗨𝘀𝗲 𝗠𝗲 𝗔𝗴𝗮𝗶𝗻 .

𝗥𝗲𝗱𝘂𝗰𝗲 𝗔𝗻𝘁𝗶𝘀𝗽𝗮𝗺 𝗧𝗶𝗺𝗲 /buy 𝗨𝘀𝗶𝗻𝗴 𝗣𝗮𝗶𝗱 𝗣𝗹𝗮𝗻
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status
    

    except:
        import traceback
        await error_log(traceback.format_exc())
        try:
            await message.reply_text("Try Again later" ,  reply_to_message_id = message.id)
        except:
            pass
        return False , False 


async def check_some_thing(Client , message):
    try:
        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""<b>
𝗨𝗻𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗬𝗼𝘂 𝗖𝗮𝗻'𝘁 𝗨𝘀𝗲 𝗠𝗲 𝗨𝗻𝗹𝗲𝘀𝘀 𝗬𝗼𝘂 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝗙𝗶𝗿𝘀𝘁 .

𝗧𝘆𝗽𝗲 /register 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        getuser    = await getuserinfo(user_id)
        status     = getuser["status"]
        checkgroup = await getchatinfo(chat_id)
        checkgroup = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            resp = """<b>
𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀 𝗥𝗲𝗾𝘂𝗶𝗿𝗲𝗱 ⚠️
𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗢𝗻𝗹𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗨𝘀𝗲𝗿𝘀 𝗮𝗿𝗲 𝗔𝗹𝗹𝗼𝘄𝗲𝗱 𝘁𝗼 𝘂𝘀𝗲 𝗯𝗼𝘁 𝗶𝗻 𝗣𝗲𝗿𝘀𝗼𝗻𝗮𝗹 . 𝗔𝗹𝘁𝗵𝗼𝘂𝗴𝗵 𝗬𝗼𝘂 𝗖𝗮𝗻 𝗨𝘀𝗲 𝗕𝗼𝘁 𝗙𝗿𝗲𝗲 𝗛𝗲𝗿𝗲

 👉 https://t.me/+nxCmq8lCNjNlYjZl

𝗕𝘂𝘆 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗣𝗹𝗮𝗻 𝗨𝘀𝗶𝗻𝗴 /buy 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
</b>"""
            await message.reply_text(resp , message_id=message.id)
            return False , False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""<b>
𝗨𝗻𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝗖𝗵𝗮𝘁𝘀 ⚠️

𝗠𝗲𝘀𝘀𝗮𝗴𝗲: 𝗢𝗻𝗹𝘆 𝗖𝗵𝗮𝘁𝘀 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗕𝘆 𝗠𝘆 𝗠𝗮𝘀𝘁𝗲𝗿 𝗖𝗮𝗻 𝗢𝗻𝗹𝘆 𝗨𝘀𝗲 𝗠𝗲 . 𝗧𝗼 𝗚𝗲𝘁 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗬𝗼𝘂𝗿 𝗖𝗵𝗮𝘁𝘀 𝗙𝗼𝗹𝗹𝗼𝘄 𝗧𝗵𝗲 𝗦𝘁𝗲𝗽𝘀 .

𝗧𝘆𝗽𝗲 /howgp 𝘁𝗼 𝗞𝗻𝗼𝘄 𝗧𝗵𝗲 𝗦𝘁𝗲𝗽
</b>"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status

    except:
        import traceback
        await error_log(traceback.format_exc())
        try:
            await message.reply_text("Try Again later" ,  reply_to_message_id = message.id)
        except:
            pass
        return False , False



