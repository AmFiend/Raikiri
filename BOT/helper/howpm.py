from pyrogram import Client, filters
from FUNC.usersdb_func import *


@Client.on_message(filters.command("howpm", [".", "/"]))
async def cmd_howgp(client, message):
    try:
        user_id = str(message.from_user.id)
        texta = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ꜰʀᴇᴇ ᴠꜱ ᴘʀᴇᴍɪᴜᴍ ᴠꜱ ᴘᴀɪᴅ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <u>ꜱᴛʀɪᴘᴇ ᴀᴜᴛʜ ɢᴀᴛᴇ (/au)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 30s
    ᴘʀᴇᴍɪᴜᴍ — 5s
    ᴘᴀɪᴅ — 5s

◈ <u>ꜱᴛʀɪᴘᴇ ᴍᴀꜱꜱ ᴀᴜᴛʜ ɢᴀᴛᴇ (/mass)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 120s
    ᴘʀᴇᴍɪᴜᴍ — 80s
    ᴘᴀɪᴅ — 30s
  <b>ᴄʜᴇᴄᴋɪɴɢ ʟɪᴍɪᴛ :</b>
    ꜰʀᴇᴇ — 8
    ᴘʀᴇᴍɪᴜᴍ — 15
    ᴘᴀɪᴅ — 25

◈ <u>ꜱᴛʀɪᴘᴇ ᴄʜᴀʀɢᴇ ɢᴀᴛᴇ (/chk)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 30s
    ᴘʀᴇᴍɪᴜᴍ — 5s
    ᴘᴀɪᴅ — 5s

◈ <u>ꜱᴛʀɪᴘᴇ ᴍᴀꜱꜱ ᴄʜᴀʀɢᴇ ɢᴀᴛᴇ (/mchk)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 120s
    ᴘʀᴇᴍɪᴜᴍ — 80s
    ᴘᴀɪᴅ — 30s
  <b>ᴄʜᴇᴄᴋɪɴɢ ʟɪᴍɪᴛ :</b>
    ꜰʀᴇᴇ — 8
    ᴘʀᴇᴍɪᴜᴍ — 15
    ᴘᴀɪᴅ — 25

◈ <u>ꜱᴛʀɪᴘᴇ ꜱᴋ ʙᴀꜱᴇᴅ ᴄʜᴀʀɢᴇ ɢᴀᴛᴇ ᴡɪᴛʜ ᴛxᴛ ꜰɪʟᴇ ᴄʜᴇᴄᴋɪɴɢ (/cvv sk)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 120s
    ᴘʀᴇᴍɪᴜᴍ — 80s
    ᴘᴀɪᴅ — 50s
  <b>ᴄʜᴇᴄᴋɪɴɢ ʟɪᴍɪᴛ :</b>
    ꜰʀᴇᴇ — 200
    ᴘʀᴇᴍɪᴜᴍ — 1000
    ᴘᴀɪᴅ — 1500

◈ <u>ᴄᴄ ꜱᴄʀᴀᴘᴇʀ ɢᴀᴛᴇ (/scr)</u>
  <b>ꜱᴄʀᴀᴘɪɴɢ ʟɪᴍɪᴛ :</b>
    ꜰʀᴇᴇ — 3000
    ᴘʀᴇᴍɪᴜᴍ — 6000
    ᴘᴀɪᴅ — 12000

◈ <u>ᴄᴄ ɢᴇɴᴇʀᴀᴛᴏʀ ᴡɪᴛʜ ʟᴜʜɴ ᴀʟɢᴏ ᴀɴᴅ ᴄᴜꜱᴛᴏᴍ ᴀᴍᴏᴜɴᴛ ɢᴀᴛᴇ (/gen)</u>
  <b>ɢᴇɴᴇʀᴀᴛɪɴɢ ʟɪᴍɪᴛ :</b>
    ꜰʀᴇᴇ — 2000
    ᴘʀᴇᴍɪᴜᴍ — 4000
    ᴘᴀɪᴅ — 10000

◈ <u>ꜱᴛʀɪᴘᴇ ᴀᴜᴛʜ ɢᴀᴛᴇ (/au)</u>
  <b>ᴀɴᴛɪꜱᴘᴀᴍ :</b>
    ꜰʀᴇᴇ — 3
    ᴘʀᴇᴍɪᴜᴍ — 3
    ᴘᴀɪᴅ — 3

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(texta, quote=True)
        await plan_expirychk(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
