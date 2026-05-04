from FUNC.defs import *
import re


async def getcc_for_mass(message, role):
    try:
        ccs = []

        if message.reply_to_message:
            text = message.reply_to_message.text
        else:
            text = message.text

        for i in text.split("\n"):
            get = await getcards(i)
            if get is not None:
                cc = get[0]
                mes = get[1]
                ano = get[2]
                cvv = get[3]
                fullcc = f"{cc}|{mes}|{ano}|{cvv}"
                ccs.append(fullcc)

        if role == "FREE" and len(ccs) > 16:
            resp = f"""✦ <b>ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ ᴄʜᴇᴄᴋ 15 ᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ.
◈ ʙᴜʏ ᴀ ᴘʟᴀɴ ᴛᴏ ɪɴᴄʀᴇᴀꜱᴇ ʏᴏᴜʀ ʟɪᴍɪᴛ.

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ᴘᴀɪᴅ ᴘʟᴀɴ
━━━━━━━━━━━━━━━━━━━━"""
            return False, resp
        if (role == "PREMIUM" or role == "LIFETIME") and len(ccs) > 50000:            
            resp = f"""✦ <b>ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ ᴄʜᴇᴄᴋ 25 ᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ.
◈ ꜰᴏʀ ʜɪɢʜᴇʀ ʟɪᴍɪᴛ, ᴋɴᴏᴄᴋ @pipin_o

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ᴘᴀɪᴅ ᴘʟᴀɴ
━━━━━━━━━━━━━━━━━━━━"""
            return False, resp
        if len(ccs) == 0:
            resp = f"""✦ <b>ᴄᴄ ɴᴏᴛ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ᴜɴᴀʙʟᴇ ᴛᴏ ꜰɪɴᴅ ᴀɴʏ ᴄᴄ ꜰʀᴏᴍ ʏᴏᴜʀ ɪɴᴘᴜᴛ.
◈ ᴘʀᴏᴠɪᴅᴇ ᴄᴄ ᴅᴇᴛᴀɪʟꜱ ᴛᴏ ᴄʜᴇᴄᴋ.
━━━━━━━━━━━━━━━━━━━━"""
            return False, resp
        else:
            return True, ccs

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        return False, "✦ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ✦"
