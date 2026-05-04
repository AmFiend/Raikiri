import asyncio, httpx, os
from io import BytesIO
from pyrogram import Client, filters
from pyrogram.types import Message
import time

sem = asyncio.Semaphore(20)

# Format for Telegram message
def format_result_telegram(site, item):
    return f"""<b>┏━━━━━━━⍟
┃Cheapest Product
┗━━━━━━━━━━━⊛</b>

⊙ <b>Product Variant:</b> {item.get('variant', 'N/A')}
⊙ <b>Product ◈ <b>ɴᴀᴍᴇ :</b></b> {item['title']}
⊙ <b>Product Price:</b> ${item['price']}
⊙ <b>Product URL:</b> <code>{item['url']}</code>

<b>❛ ━━━━･⌁ 𝑩𝑨𝑹𝑹𝒀 ⌁･━━━━ ❜</b>"""

# Format for plain text file
def format_result_txt(site, item):
    return f"""┏━━━━━━━⍟
┃Cheapest Product
┗━━━━━━━━━━━⊛

⊙ Product Variant: {item.get('variant', 'N/A')}
⊙ Product ◈ <b>ɴᴀᴍᴇ :</b> {item['title']}
⊙ Product Price: ${item['price']}
⊙ Product URL: {item['url']}

❛ ━━━━･⌁ 𝑩𝑨𝑹𝑹𝒀 ⌁･━━━━ ❜"""

# Fetch product data
async def fetch_top_products(session, site):
    async with sem:
        try:
            if not site.startswith("http"):
                site = "https://" + site
            base_url = site.rstrip('/')
            products_url = base_url + "/products.json"

            r = await session.get(products_url, timeout=8)
            if r.status_code != 200:
                return {"error": f"❌ {base_url}\nFailed to fetch products."}

            data = r.json()
            products = data.get("products", [])
            if not products:
                return {"error": f"❌ {base_url}\nNo products found."}

            valid_items = []
            for product in products:
                handle = product.get("handle")
                for variant in product.get("variants", []):
                    try:
                        price = float(variant.get("price", "0.00"))
                        if price == 0.0:
                            continue
                        valid_items.append({
                            "title": product.get("title", "No Title"),
                            "price": price,
                            "url": f"{base_url}/products/{handle}",
                            "variant": variant.get("title", "Default Title")
                        })
                    except:
                        continue

            if not valid_items:
                return {"error": f"❌ {base_url}\nNo valid priced products."}

            best_item = sorted(valid_items, key=lambda x: x["price"])[0]
            return {"success": best_item, "site": base_url}

        except Exception as e:
            return {"error": f"❌ {site}\nError: {str(e)}"}

# /ssc command (up to 10 sites)
@Client.on_message(filters.command("ssc", ["/", "."]))
async def ssc_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply("❌ Usage:\n<code>/ssc </code>\nMax 10 sites.")

    sites = args[1:]
    if len(sites) > 10:
        return await message.reply("❌ You can check up to 10 sites at once.")

    m = await message.reply("🔍 Checking sites... Please wait ⌛")

    results = []
    async with httpx.AsyncClient(follow_redirects=True) as session:
        tasks = [fetch_top_products(session, site) for site in sites]
        fetches = await asyncio.gather(*tasks)

        for res in fetches:
            if "success" in res:
                results.append(format_result_telegram(res['site'], res["success"]))
            else:
                results.append(res["error"])

    final_text = "\n\n".join(results)
    if len(final_text) > 4096:
        file = BytesIO(final_text.encode("utf-8"))
        file.name = "cheapest_results.txt"
        await message.reply_document(file, caption="📦 Cheapest Products List")
    else:
        await m.edit_text(final_text, disable_web_page_preview=True)

# /sctxt command (reads from .txt file)
@Client.on_message(filters.command("sctxt", ["/", "."]))
async def sctxt_cmd(client: Client, message: Message):
    sites = []

    # Load sites from file or reply text
    if message.reply_to_message and message.reply_to_message.document:
        file = await message.reply_to_message.download()
        with open(file, "r") as f:
            sites = [line.strip() for line in f if line.strip()]
        os.remove(file)
    elif message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text
        sites = [line.strip() for line in text.splitlines() if line.strip()]
    else:
        return await message.reply("❌ Reply to a .txt file or list of Shopify sites.")

    total = len(sites)
    if total == 0:
        return await message.reply("❌ No valid Shopify URLs found.")

    m = await message.reply(f"Reading site list... ⌛\n◈ <b>ᴛᴏᴛᴀʟ :</b> {total} sites")

    start = time.time()
    results_telegram = []
    results_txt = []

    async with httpx.AsyncClient(follow_redirects=True) as session:
        tasks = [fetch_top_products(session, site) for site in sites]
        fetches = await asyncio.gather(*tasks)

        for res in fetches:
            if "success" in res:
                item = res["success"]
                site = res["site"]
                results_telegram.append(format_result_telegram(site, item))
                results_txt.append(format_result_txt(site, item))
            else:
                results_telegram.append(res["error"])
                results_txt.append(res["error"])

    end = time.time()
    elapsed = round(end - start, 2)

    final_telegram = "\n\n".join(results_telegram)
    final_txt = f"📦 Checked {total} sites in {elapsed} sec.\n\n" + "\n\n".join(results_txt)

    if len(final_telegram) > 4096:
        file = BytesIO(final_txt.encode("utf-8"))
        file.name = "cheapest_results.txt"
        await m.edit_text(f"📦 Checked {total} sites in {elapsed} sec. Results sent as .txt file.")
        await message.reply_document(file, caption=f"📦 Checked {total} sites in {elapsed} sec.")
    else:
        await m.edit_text(final_telegram, disable_web_page_preview=True)
