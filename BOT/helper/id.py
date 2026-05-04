from pyrogram import Client, filters
from FUNC.usersdb_func import *


async def get_user_info(user_id, client, message):
    try:
        user_id     = str(message.text.split(" ")[1])
        get         = await client.get_users(user_id)
        name        = get.first_name
        id          = get.id
        username    = get.username
        restriction = get.restriction_reason
        scam        = get.scam
        premium     = get.is_premium

        resp = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴜꜱᴇʀ ɪɴꜰᴏ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>ɴᴀᴍᴇ :</b> {name}
◈ <b>ɪᴅ :</b> {id}
◈ <b>ᴜꜱᴇʀɴᴀᴍᴇ :</b> @{username}
◈ <b>ᴘʀᴏꜰɪʟᴇ :</b> <a href="tg://user?id={id}">ʟɪɴᴋ</a>
◈ <b>ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ :</b> {restriction}
◈ <b>ꜱᴄᴀᴍᴛᴀɢ :</b> {scam}
◈ <b>ᴘʀᴇᴍɪᴜᴍ :</b> {premium}

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, quote=True)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_message(filters.command("id", [".", "/"]))
async def cmd_id(client, message):
    try:
        if len(message.text.split(" ")) > 1:
            await get_user_info(message.text.split(" ")[1], client, message)
        else:
            if message.reply_to_message:
                user_info = message.reply_to_message.from_user
            else:
                user_info = message.from_user

            texta = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ɪᴅ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>ɴᴀᴍᴇ :</b> <a href="tg://user?id={user_info.id}">{user_info.first_name}</a>
◈ <b>ᴜꜱᴇʀ ɪᴅ :</b> <code>{user_info.id}</code>
◈ <b>ᴄʜᴀᴛ ɪᴅ :</b> <code>{message.chat.id}</code>

━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(texta, quote=True)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())
