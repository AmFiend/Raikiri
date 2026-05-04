from FUNC.usersdb_func import *
import time
from FUNC.defs import *

gate_active    = json.loads(open("FILES/deadsk.json", "r" , encoding="utf-8").read())["gate_active"]


async def check_all_thing(Client , message):
    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""✦ <b>ᴜɴʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴍᴇ ᴜɴʟᴇꜱꜱ ʏᴏᴜ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ.

↪ ᴛʏᴘᴇ /register ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False , False

        if any(command in message.text for command in gate_active):
            resp = "✦ ᴛʜɪꜱ ɢᴀᴛᴇ ɪꜱ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɴᴏᴡ. ᴛʀʏ ʟᴀᴛᴇʀ. ✦"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return False, False, False

        getuser        = await getuserinfo(user_id)
        status         = getuser["status"]
        credit         = int(getuser["credit"])
        antispam_time  = int(getuser["antispam_time"])
        now            = int(time.time())
        count_antispam = now - antispam_time
        checkgroup     = await getchatinfo(chat_id)
        checkgroup     = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            resp = f"""✦ <b>ᴘʀᴇᴍɪᴜᴍ ʀᴇǫᴜɪʀᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ᴏɴʟʏ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ʙᴏᴛ ɪɴ ᴘᴍ.
◈ ꜰʀᴇᴇ ᴜꜱᴇ ʜᴇʀᴇ ↴

 ⟢ https://t.me/+nxCmq8lCNjNlYjZl

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""✦ <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴄʜᴀᴛ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ᴏɴʟʏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴄʜᴀᴛꜱ ᴄᴀɴ ᴜꜱᴇ ᴍᴇ.
◈ ꜰᴏʟʟᴏᴡ ᴛʜᴇ ꜱᴛᴇᴘꜱ ᴛᴏ ɢᴇᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.

↪ ᴛʏᴘᴇ /howgp ᴛᴏ ᴋɴᴏᴡ ᴛʜᴇ ꜱᴛᴇᴘꜱ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if credit < 5:
            resp = f"""✦ <b>ɪɴꜱᴜꜰꜰɪᴄɪᴇɴᴛ ᴄʀᴇᴅɪᴛꜱ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ᴄʀᴇᴅɪᴛꜱ.
◈ ʀᴇᴄʜᴀʀɢᴇ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ.

↪ ᴛʏᴘᴇ /buy ᴛᴏ ʀᴇᴄʜᴀʀɢᴇ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "PREMIUM" and count_antispam < 5:
            after = 5 - count_antispam
            resp = f"""✦ <b>ᴀɴᴛɪꜱᴘᴀᴍ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ꜱʟᴏᴡ ᴅᴏᴡɴ. ᴛʀʏ ᴀꜰᴛᴇʀ {after}s

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ꜰᴀꜱᴛᴇʀ ᴀᴄᴄᴇꜱꜱ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        if status == "FREE" and count_antispam < 20:
            after = 20 - count_antispam
            resp = f"""✦ <b>ᴀɴᴛɪꜱᴘᴀᴍ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ꜱʟᴏᴡ ᴅᴏᴡɴ. ᴛʀʏ ᴀꜰᴛᴇʀ {after}s

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ꜰᴀꜱᴛᴇʀ ᴀᴄᴄᴇꜱꜱ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status
    

    except:
        import traceback
        await error_log(traceback.format_exc())
        try:
            await message.reply_text("✦ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ✦" ,  reply_to_message_id = message.id)
        except:
            pass
        return False , False 


async def check_some_thing(Client , message):
    try:
        user_id   = str(message.from_user.id)
        chat_type = str(message.chat.type)
        chat_id   = str(message.chat.id)
        regdata   = await getuserinfo(user_id)
        regdata   = str(regdata)
        if regdata == "None":
            resp = f"""✦ <b>ᴜɴʀᴇɢɪꜱᴛᴇʀᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜꜱᴇ ᴍᴇ ᴜɴʟᴇꜱꜱ ʏᴏᴜ ʀᴇɢɪꜱᴛᴇʀ ꜰɪʀꜱᴛ.

↪ ᴛʏᴘᴇ /register ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        getuser    = await getuserinfo(user_id)
        status     = getuser["status"]
        checkgroup = await getchatinfo(chat_id)
        checkgroup = str(checkgroup)
        await plan_expirychk(user_id)

        if chat_type == "ChatType.PRIVATE" and status == "FREE":
            resp = """✦ <b>ᴘʀᴇᴍɪᴜᴍ ʀᴇǫᴜɪʀᴇᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ᴏɴʟʏ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ᴄᴀɴ ᴜꜱᴇ ʙᴏᴛ ɪɴ ᴘᴍ.
◈ ꜰʀᴇᴇ ᴜꜱᴇ ʜᴇʀᴇ ↴

 ⟢ https://t.me/+nxCmq8lCNjNlYjZl

↪ ᴛʏᴘᴇ /buy ꜰᴏʀ ᴘʀᴇᴍɪᴜᴍ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp , message_id=message.id)
            return False , False

        if (
            chat_type == "ChatType.GROUP"
            or chat_type == "ChatType.SUPERGROUP"
            and checkgroup == "None"
        ):
            resp = f"""✦ <b>ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴄʜᴀᴛ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ ᴏɴʟʏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴄʜᴀᴛꜱ ᴄᴀɴ ᴜꜱᴇ ᴍᴇ.
◈ ꜰᴏʟʟᴏᴡ ᴛʜᴇ ꜱᴛᴇᴘꜱ ᴛᴏ ɢᴇᴛ ᴀᴘᴘʀᴏᴠᴇᴅ.

↪ ᴛʏᴘᴇ /howgp ᴛᴏ ᴋɴᴏᴡ ᴛʜᴇ ꜱᴛᴇᴘꜱ
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp ,  reply_to_message_id = message.id)
            return False , False

        return True , status

    except:
        import traceback
        await error_log(traceback.format_exc())
        try:
            await message.reply_text("✦ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ✦" ,  reply_to_message_id = message.id)
        except:
            pass
        return False , False
