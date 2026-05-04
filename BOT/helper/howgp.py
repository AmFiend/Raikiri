from pyrogram import Client, filters
from FUNC.defs import *


@Client.on_message(filters.command("howgp", [".", "/"]))
async def cmd_howgp(Client, message):
    try:
        texta = f"""<a href='https://t.me/elitechkbot?start=start'>✧</a> <b>ꜱᴘʏᴅᴇ ━ ɢʀᴏᴜᴘ ꜱᴇᴛᴜᴘ</b> ✧
━━━━━━━━━━━━━━━━━━━━

◈ <b>Requirement:</b> Your Group Must Have Atleast 100 Members.

◈ <b>Steps To Get Your Group Authorised:</b>
   ➔ Add This Bot To Your Group As Admin
   ➔ Copy Your Group Username or Group Invite Link
   ➔ Knock @pipin_o And Give Him The Group Username or Group Invite Link

↪ Once He is online, He will Approve Your Group ✓
━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(texta, message.id)

    except Exception as e:
        import traceback

        await error_log(traceback.format_exc())
