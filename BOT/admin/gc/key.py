import json
from pyrogram import Client, filters
from FUNC.defs import error_log
from .func import gcgenfunc, insert_variable_gc   # adjust import path

@Client.on_message(filters.command(["key", "genkey"], [".", "/"]))
async def cmd_generate_variable_keys(Client, message):
    try:
        user_id = str(message.from_user.id)
        OWNER_ID = json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["OWNER_ID"]
        if user_id not in OWNER_ID:
            await message.reply_text(
                "<b>You don't have permission to use this command.\nContact @pipin_o</b>",
                message.id
            )
            return

        args = message.text.split()
        if len(args) != 3:
            await message.reply_text(
                "<b>Usage:</b> <code>/key &lt;days&gt; &lt;quantity&gt;</code>\n"
                "Example: <code>/key 1 1</code> → generates 1 key valid for 1 day.",
                message.id
            )
            return

        try:
            days = int(args[1])
            qty = int(args[2])
            if days <= 0 or qty <= 0:
                raise ValueError
        except:
            await message.reply_text("❌ Days and quantity must be positive integers.", message.id)
            return

        text = f"""<b>✧ ɢɪꜰᴛᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ ✓ ✧
◈ <b>ᴀᴍᴏᴜɴᴛ :</b> {qty}
◈ <b>ᴠᴀʟɪᴅɪᴛʏ :</b> {days} days</b>\n"""

        for _ in range(qty):
            code = f"SPYDE-XXXX-XXXX-XXXX-CHK-{gcgenfunc()}-{gcgenfunc()}-{gcgenfunc()}-CHK"
            await insert_variable_gc(code, days)
            text += f"""
⟢ <code>{code}</code>
<b>Value : Premium Plan – {days} days</b>\n"""

        text += f"""
<b>For Redeem SPYDE-XXXX-XXXX-XXXXX-CHK</b>"""
        await message.reply_text(text, message.id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
