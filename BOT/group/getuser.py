from pyrogram import Client, filters


@Client.on_message(filters.command("getuser", [".", "/"]))
async def cmd_getuser(client, message):
    try:
        user = message.text.split(" ")[1]
    except IndexError:
        resp = """✦ <b>ꜱᴘʏᴅᴇ ━ ᴜꜱᴀɢᴇ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ /getuser ɪᴅ_ᴏʀ_ᴜꜱᴇʀɴᴀᴍᴇ
━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, quote=True)
        return

    try:
        get         = await client.get_users(user)
        name        = get.first_name
        id          = get.id
        username    = get.username
        restriction = get.restriction_reason
        scam        = get.scam
        premium     = get.is_premium

        resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴜꜱᴇʀ ɪɴꜰᴏ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ɴᴀᴍᴇ :</b> {name}
⟢ <b>ɪᴅ :</b> {id}
◈ <b>ᴜꜱᴇʀɴᴀᴍᴇ :</b> @{username}
⟢ <b>ᴘʀᴏꜰɪʟᴇ :</b> <a href="tg://user?id={id}">ʟɪɴᴋ</a>
◈ <b>ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ :</b> {restriction}
⟢ <b>ꜱᴄᴀᴍᴛᴀɢ :</b> {scam}
◈ <b>ᴘʀᴇᴍɪᴜᴍ :</b> {premium}

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, quote=True)

    except Exception:
        try:
            await message.reply_text("✦ ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪɴᴄᴏʀʀᴇᴄᴛ ɪᴅ ✗ ✦", quote=True)
        except Exception:
            pass
