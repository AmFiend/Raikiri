from FUNC.defs import *
from pyrogram import Client, filters
import time


@Client.on_message(filters.command("ping", [".", "/"]))
async def cmd_ping(client, message):
    try:
        start = time.perf_counter()
        resp  = """✦ <b>ꜱᴘʏᴅᴇ ━ ᴄʜᴇᴄᴋɪɴɢ ᴘɪɴɢ...</b> ✦"""
        edit  = await message.reply_text(resp, quote=True)
        end   = time.perf_counter()
        
        textb = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴘɪɴɢ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ʙᴏᴛ :</b> ꜱᴘʏᴅᴇ ᴄʜᴋ
⟢ <b>ꜱᴛᴀᴛᴜꜱ :</b> ʀᴜɴɴɪɴɢ ✓
◈ <b>ᴘɪɴɢ :</b> {(end-start)*1000:.2f} ᴍꜱ

━━━━━━━━━━━━━━━━━━━━"""
        await client.edit_message_text(message.chat.id, edit.id, textb)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
