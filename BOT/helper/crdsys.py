from FUNC.defs import *
from pyrogram import Client, filters


@Client.on_message(filters.command("howcrd", [".", "/"]))
async def cmd_crdsystem(client, message):
    try:
        resp = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ᴄʀᴇᴅɪᴛ ꜱʏꜱᴛᴇᴍ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>AUTH GATES</b>
   ➔ 1 credit per CC check

◈ <b>CHARGE GATES</b>
   ➔ 1 credit per CC check

◈ <b>MASS AUTH GATES</b>
   ➔ 1 credit per CC check

◈ <b>MASS CHARGE GATES</b>
   ➔ 1 credit per CC check

◈ <b>CC SCRAPER GATES</b>
   ➔ 1 credit per scraping

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, quote=True)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
