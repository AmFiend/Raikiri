from pyrogram import Client, filters
from FUNC.usersdb_func import *

@Client.on_message(filters.command("info", [".", "/"]))
async def cmd_info(client, message):
    try:
        user_id = str(message.from_user.id)
        regdata = await getuserinfo(user_id)
        results = str(regdata)

        if results == "None":
            resp = """✦ <b>ᴜɴʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴍᴇ ᴜɴʟᴇꜱꜱ ʏᴏᴜ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ.

↪ ᴛʏᴘᴇ /register ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp)
            return

        if message.reply_to_message:
            user_info = message.reply_to_message.from_user
        else:
            user_info = message.from_user

        user_id = str(user_info.id)
        username = str(user_info.username)
        first_name = str(user_info.first_name)
        results = await getuserinfo(user_id)

        status = results["status"]
        plan = results["plan"]
        expiry = results["expiry"]
        credit = results["credit"]
        totalkey = results["totalkey"]
        reg_at = results["reg_at"]

        send_info = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ʏᴏᴜʀ ɪɴꜰᴏ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ɴᴀᴍᴇ :</b> {first_name}
⟢ <b>ɪᴅ :</b> <code>{user_id}</code>
◈ <b>ᴜꜱᴇʀɴᴀᴍᴇ :</b> @{username}
⟢ <b>ᴘʀᴏꜰɪʟᴇ :</b> <a href="tg://user?id={user_info.id}">ʟɪɴᴋ</a>
◈ <b>ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ :</b> {user_info.is_restricted}
⟢ <b>ꜱᴄᴀᴍᴛᴀɢ :</b> {user_info.is_scam}
◈ <b>ᴘʀᴇᴍɪᴜᴍ :</b> {user_info.is_premium}
⟢ <b>ꜱᴛᴀᴛᴜꜱ :</b> {status}
◈ <b>ᴄʀᴇᴅɪᴛ :</b> {credit}
⟢ <b>ᴘʟᴀɴ :</b> {plan}
◈ <b>ᴇxᴘɪʀʏ :</b> {expiry}
⟢ <b>ᴋᴇʏꜱ ʀᴇᴅᴇᴇᴍᴇᴅ :</b> {totalkey}
◈ <b>ʀᴇɢɪꜱᴛᴇʀᴇᴅ :</b> {reg_at}

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(send_info)

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
