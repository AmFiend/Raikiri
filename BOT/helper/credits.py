from pyrogram import Client, filters
from FUNC.usersdb_func import *


@Client.on_message(filters.command("credits", [".", "/"]))
async def cmd_credit(Client, message):
    try:
        user_id = str(message.from_user.id)
        regdata = await getuserinfo(user_id)
        regdata = str(regdata)
        if regdata == "None":
            resp = f"""<b>
𝗨𝗻𝗿𝗲𝗴𝗶𝘀𝘁𝗲𝗿𝗲𝗱 𝗨𝘀𝗲𝗿𝘀 ⚠️

𝗬𝗼𝘂 𝗖𝗮𝗻'𝘁 𝗨𝘀𝗲 𝗠𝗲 𝗨𝗻𝗹𝗲𝘀𝘀 𝗬𝗼𝘂 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿   𝗙𝗶𝗿𝘀𝘁 .

𝗧𝘆𝗽𝗲 /register 𝘁𝗼 𝗖𝗼𝗻𝘁𝗶𝗻𝘂𝗲
</b>"""
            await message.reply_text(resp, message.id)
            return

        getuser    = await getuserinfo(user_id)
        status     = getuser["status"]
        credit     = getuser["credit"]
        plan       = getuser["plan"]
        first_name = str(message.from_user.first_name)

        resp = f"""<b>
Name: {first_name}
Credits: {credit}
Status: {status}
Plan: {plan}

Want More ? Type /buy to Get more.
    </b>"""
        await message.reply_text(resp, message.id)
    except:
        import traceback
        await error_log(traceback.format_exc())
