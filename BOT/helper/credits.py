from pyrogram import Client, filters
from FUNC.usersdb_func import *


@Client.on_message(filters.command("credits", [".", "/"]))
async def cmd_credit(Client, message):
    try:
        user_id = str(message.from_user.id)
        regdata = await getuserinfo(user_id)
        regdata = str(regdata)
        if regdata == "None":
            resp = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ᴜɴʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴍᴇ ᴜɴʟᴇꜱꜱ ʏᴏᴜ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ.

↪ ᴛʏᴘᴇ /register ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, message.id)
            return

        getuser    = await getuserinfo(user_id)
        status     = getuser["status"]
        credit     = getuser["credit"]
        plan       = getuser["plan"]
        first_name = str(message.from_user.first_name)

        resp = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴄʀᴇᴅɪᴛꜱ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>ɴᴀᴍᴇ :</b> {first_name}
◈ <b>ᴄʀᴇᴅɪᴛꜱ :</b> {credit}
◈ <b>ꜱᴛᴀᴛᴜꜱ :</b> {status}
◈ <b>ᴘʟᴀɴ :</b> {plan}

↪ ᴡᴀɴᴛ ᴍᴏʀᴇ? ᴛʏᴘᴇ /buy
━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, message.id)
    except:
        import traceback
        await error_log(traceback.format_exc())
