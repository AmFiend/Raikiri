import json
import requests
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *




def check_proxy(proxy_url):
    try:
        proxy_parts = proxy_url.split(":")
        if len(proxy_parts) != 4:
            raise ValueError("Proxy URL format is incorrect. Should be ip:port:user:password")

        proxy_ip = proxy_parts[0]
        proxy_port = proxy_parts[1]
        proxy_user = proxy_parts[2]
        proxy_password = proxy_parts[3]
        
        proxies = {
            "http": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
            "https": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
        }
        
        response = requests.get("http://www.google.com", proxies=proxies, timeout=5)
        response.raise_for_status()
        return response.status_code == 200
    except requests.exceptions.ProxyError as e:
        return False
    except requests.exceptions.ConnectTimeout as e:
        return False
    except requests.exceptions.HTTPError as e:
        return False
    except Exception as e:
        return False
    




# @Client.on_message(filters.command("setproxy", [".", "/"]))
async def addproxy(client, message):
    try:
        user_id = str(message.from_user.id)
        get_user_info = await getuserinfo(user_id)
        proxy_url = message.text.split()[1]

        if check_proxy(proxy_url):
            await updateuserinfo(user_id, "user_proxy", proxy_url)
            
            resp = f"""✧ <b>ᴘʀᴏxʏ ᴀᴅᴅᴇᴅ ✓</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ᴘʀᴏxʏ :</b> {proxy_url}
⟢ <b>ꜱᴛᴀᴛᴜꜱ :</b> ʟɪᴠᴇ ✓

━━━━━━━━━━━━━━━━━━━━"""
        else:
            resp = "✦ ᴘʀᴏxʏ ɪꜱ ᴅᴇᴀᴅ ✗ ✦"
        
        await message.reply_text(resp, message.id)
    except IndexError:
        await message.reply_text("✦ ɪɴᴠᴀʟɪᴅ ᴘʀᴏxʏ ꜰᴏʀᴍᴀᴛ ✗ ✦", message.id)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦", message.id)




# @Client.on_message(filters.command("rmproxy", [".", "/"]))
async def removeproxy(client, message):
    try:
        user_id = str(message.from_user.id)
        await updateuserinfo(user_id, "user_proxy", "N/A")
        resp = "✧ ᴘʀᴏxʏ ʀᴇᴍᴏᴠᴇᴅ ✓ ✧"
        await message.reply_text(resp, message.id)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦", message.id)




# @Client.on_message(filters.command("viewproxy", [".", "/"]))
async def viewproxy(client, message):
    try:
        user_id = str(message.from_user.id)
        user_info = await getuserinfo(user_id)
        proxy_url = user_info.get("user_proxy", "N/A")
        resp = f"""✧ <b>ʏᴏᴜʀ ᴘʀᴏxʏ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ {proxy_url}

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, message.id)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦", message.id)








# /////////////////////////////////////////////////////user sk //////////////////////////////



@Client.on_message(filters.command("setamt", [".", "/"]))
async def add_brod(client, message):
    try:
        user_id = str(message.from_user.id)

        if len(message.command) > 1:
            amount = message.command[1].strip()
        elif message.reply_to_message and message.reply_to_message.text:
            amount = message.reply_to_message.text.strip()
        else:
            resp = "✦ ᴘʀᴏᴠɪᴅᴇ ᴀᴍᴏᴜɴᴛ ᴀꜱ ᴀʀɢᴜᴍᴇɴᴛ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ✗ ✦"
            await message.reply_text(resp, reply_to_message_id=message.id)
            return

        await updateuserinfo(user_id, "damt", amount)

        resp = f"""✧ <b>ᴄʜᴀʀɢᴇ ᴀᴍᴏᴜɴᴛ ꜱᴇᴛ ✓</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ᴀᴍᴏᴜɴᴛ :</b> {amount}$

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, reply_to_message_id=message.id)

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())






@Client.on_message(filters.command("rmsk", [".", "/"]))
async def removesk(client, message):
    user_id = str(message.from_user.id)
    user_info = await getuserinfo(user_id)
    sk_key = user_info.get("dsk", "N/A")

    if sk_key == "N/A":
        await message.reply_text("✦ ɴᴏ ꜱᴋ ꜱᴇᴛ. ᴜꜱᴇ /setsk ᴛᴏ ᴀᴅᴅ ᴏɴᴇ. ✦")
        return

    try:
        await updateuserinfo(user_id, "dsk", "N/A")
        await updateuserinfo(user_id, "dpk", "N/A")
        await updateuserinfo(user_id, "dcr", "N/A")

        user_info = await getuserinfo(user_id)
        sk_key = user_info.get("dsk", "N/A")
        pk_key = user_info.get("dpk", "N/A")
        currency = user_info.get("dcr", "N/A")

        resp = f"""✧ <b>ꜱᴋ ʀᴇᴍᴏᴠᴇᴅ ✓</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ꜱᴋ :</b> {sk_key}
⟢ <b>ᴘᴋ :</b> {pk_key}
◈ <b>ᴄᴜʀʀᴇɴᴄʏ :</b> {currency}
⟢ <b>ꜱᴛᴀᴛᴜꜱ :</b> ʀᴇᴍᴏᴠᴇᴅ ✓

━━━━━━━━━━━━━━━━━━━━"""

        await message.reply_text(resp)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦")








@Client.on_message(filters.command("mysk", [".", "/"]))
async def mysk(client, message):

    user_id = str(message.from_user.id)
    user_info = await getuserinfo(user_id)
    sk_key = user_info.get("dsk", "N/A")

    if sk_key == "N/A":
        await message.reply_text("✦ ɴᴏ ꜱᴋ ꜱᴇᴛ. ᴜꜱᴇ /setsk ᴛᴏ ᴀᴅᴅ ᴏɴᴇ. ✦")
        return

    try:
        user_id = str(message.from_user.id)
        user_info = await getuserinfo(user_id)
        sk_key = user_info.get("dsk", "N/A")
        pk_key = user_info.get("dpk", "N/A")
        currency = user_info.get("dcr", "N/A")
        amount = user_info.get("damt", "N/A")
        resp = f"""✧ <b>ʏᴏᴜʀ ꜱᴋ ɪɴꜰᴏ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

◈ <b>ꜱᴋ :</b> {sk_key}
⟢ <b>ᴘᴋ :</b> {pk_key}
◈ <b>ᴄᴜʀʀᴇɴᴄʏ :</b> {currency}
⟢ <b>ᴄʜᴀʀɢᴇ :</b> {amount}$
◈ <b>ꜱᴛᴀᴛᴜꜱ :</b> ᴀᴄᴛɪᴠᴇ ✓

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, message.id)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦", message.id)












@Client.on_message(filters.command("selfcmd", [".", "/"]))
async def selfcmd(client, message):
    try:
        user_id = str(message.from_user.id)
        resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ꜱᴇʟꜰ ᴄᴏᴍᴍᴀɴᴅ ᴢᴏɴᴇ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

✦ <b>ᴘʀᴏxʏ ꜱᴇᴛᴜᴘ</b> ✦ <i>(ᴜɴᴀᴄᴛɪᴠᴇ)</i>

⟢ ᴜꜱᴇ ʏᴏᴜʀ ᴏᴡɴ ᴘʀᴏxʏ ᴏʀ ʀᴇᴍᴏᴠᴇ ɪᴛ.
◈ /setproxy ɪᴘ:ᴘᴏʀᴛ:ᴜꜱᴇʀ:ᴘᴀꜱꜱ
⟢ /rmproxy
◈ /viewproxy

✦ <b>ꜱᴋ_ʟɪᴠᴇ ꜱᴇᴛᴜᴘ</b> ✦ <i>(ꜱᴠᴠ ɢᴀᴛᴇ ᴏɴʟʏ)</i>

⟢ ᴜꜱᴇ ʏᴏᴜʀ ᴏᴡɴ ʟɪᴠᴇ ꜱᴋ ᴛᴏ ᴄʜᴇᴄᴋ ᴄᴄ.
◈ /setsk ꜱᴋ_ᴋᴇʏ — ᴀᴜᴛᴏ ɢᴇɴᴇʀᴀᴛᴇꜱ ᴘᴋ
⟢ /mysk — ᴄʜᴇᴄᴋ ʏᴏᴜʀ ꜱᴋ
◈ /rmsk — ʀᴇᴍᴏᴠᴇ ʏᴏᴜʀ ꜱᴋ
⟢ /setamt — ꜱᴇᴛ ᴄʜᴀʀɢᴇ ᴀᴍᴏᴜɴᴛ

━━━━━━━━━━━━━━━━━━━━"""
        await message.reply_text(resp, reply_to_message_id=message.id)
    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"✦ ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ ✗ : {e} ✦", reply_to_message_id=message.id)

async def error_log(error_message):
    pass
