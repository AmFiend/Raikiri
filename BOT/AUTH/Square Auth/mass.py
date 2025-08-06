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
from TOOLS.getbin import *

async def mchkfunc(fullcc, user_id):
    try:
        proxies = await get_proxy_format()
        session = httpx.AsyncClient(timeout=30)
        result = await create_cvv_charge(fullcc, session)
        getresp = await get_charge_resp(result, user_id, fullcc)
        response = getresp["response"]
        status = getresp["status"]
        await session.aclose()
        return f"[そ] 𝐂𝐚𝐫𝐝↯ <code>{fullcc}</code>\n<b>[ヸ] 𝑺𝒕𝒂𝒕𝒖𝒔 - {status}</b>\n<b>[仝] 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆 - ⤿ {response} ⤾</b>\n\n"

    except:
        import traceback
        await error_log(traceback.format_exc())
        return f"<code>{fullcc}</code>\n<b>[仝] 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆 - Declined ❌</b>\n"

@Client.on_message(filters.command("msq", [".", "/"]))
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
        resp = f"""
- [ヸ] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  Square Auth

- [そ] 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- [仝] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - Checking CC For {first_name}

- [ヸ] 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
        """
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ Square Auth</b> \n
"""
        amt = 0
        start = time.perf_counter()
        works = [mchkfunc(i, user_id) for i in ccs]
        worker_num = int(json.loads(
            open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])

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
━━━━━━━━━━━━━
[ϟ] T/t : {time.perf_counter() - start:0.2f}s
[ϟ] 𝗖𝗵𝗲𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ϟ] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=6622603977">𝑵𝒂𝒊𝒓𝒐𝒃𝒊𝒂𝒏𝒈𝒐𝒐𝒏</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄𝐑」━━━━━━╝
"""
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except:
        import traceback
        await error_log(traceback.format_exc())