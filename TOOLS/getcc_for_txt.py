import  os
from FUNC.defs import *


async def getcc_for_txt(file_name, role):
    try:
        file = open(f"downloads/{file_name}").read().splitlines()
        os.remove(f"downloads/{file_name}")
        ccs = []
        for i in file:
            get = await getcards(i)
            if get != None:
                cc     = get[0]
                mes    = get[1]
                ano    = get[2]
                cvv    = get[3]
                fullcc = f"{cc}|{mes}|{ano}|{cvv}"
                ccs.append(fullcc)

        if role == "FREE" and len(ccs) > 1501:
            resp = f"""✦ <b>ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ ᴄʜᴇᴄᴋ 1500 ᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ.
◈ ʙᴜʏ ᴀ ᴘʟᴀɴ ᴛᴏ ɪɴᴄʀᴇᴀꜱᴇ ʏᴏᴜʀ ʟɪᴍɪᴛ.

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ᴘᴀɪᴅ ᴘʟᴀɴ
━━━━━━━━━━━━━━━━━━━━"""
            return False, resp
        if (role == "PREMIUM" or role == "LIFETIME") and len(ccs) > 3001:            
            resp = f"""✦ <b>ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ ᴄʜᴇᴄᴋ 3001 ᴄᴄ ᴀᴛ ᴀ ᴛɪᴍᴇ.
◈ ʙᴜʏ ᴀ ᴘʟᴀɴ ᴛᴏ ɪɴᴄʀᴇᴀꜱᴇ ʏᴏᴜʀ ʟɪᴍɪᴛ.

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

    except:
        return False , "✦ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ✦"
