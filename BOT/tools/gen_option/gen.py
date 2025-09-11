import threading
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from FUNC.cc_gen import luhn_card_genarator, get_bin_info  # adjust with your actual function names
from TOOLS.check_all_func import check_all_thing

# Buttons for regen
buttons = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔄 Regen", callback_data="regen")],
        [InlineKeyboardButton("❌ Exit", callback_data="exit")]
    ]
)

def generate_code_blocks(all_cards):
    return "\n".join(f"<code>{c}</code>" for c in all_cards.split("\n"))

@Client.on_message(filters.command("gen", [".", "/"]))
def multi(client, message: Message):
    threading.Thread(target=bcall, args=(client, message)).start()

def bcall(client, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gen_cmd(client, message))
    loop.close()

async def gen_cmd(client: Client, message: Message):
    try:
        user_id = str(message.from_user.id)
        check = await check_all_thing(client, message)
        if not check[0]:
            return
        role = check[1]

        # Parse user input
        try:
            parts = message.text.split()[1].split("|")
            cc = parts[0]
            mes = parts[1] if len(parts) > 1 else None
            ano = parts[2] if len(parts) > 2 else None
            cvv = parts[3] if len(parts) > 3 else None
        except IndexError:
            await message.reply_text(
                "❌ Wrong format!\nUsage:\n/gen 447697|12|23|000", quote=True
            )
            return

        amount = 10
        try:
            amount = int(message.text.split()[2])
        except (IndexError, ValueError):
            pass

        delete_msg = await message.reply_text("<b>Generating...</b>", parse_mode="html")
        start = time.perf_counter()

        # Get BIN info from your existing function
        bin_info = await get_bin_info(cc[:6])
        if bin_info is None:
            await delete_msg.edit_text("❌ No BIN info found!", parse_mode="html")
            return
        brand, type_, level, bank, country, flag, currency = bin_info

        # Generate cards
        all_cards = await luhn_card_genarator(cc, mes, ano, cvv, amount)
        cards_text = generate_code_blocks(all_cards)

        # Build response
        response_text = (
            f"- 𝐂𝐂 Generated Successfully\n"
            f"- BIN: <code>{cc}</code>\n"
            f"- Amount: {amount}\n\n"
            f"{cards_text}"
            f"- Info: {brand} - {type_} - {level}\n"
            f"- Bank: {bank} 🏛\n"
            f"- Country: {country} {flag}\n\n"
            f"- Time: {time.perf_counter()-start:.2f}s\n"
            f"- Checked by: <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> [{role}]"
        )

        await client.delete_messages(message.chat.id, delete_msg.id)
        await message.reply_text(response_text, parse_mode="html", reply_markup=buttons)

    except Exception as e:
        import traceback
        print(traceback.format_exc())

@Client.on_callback_query(filters.regex("regen"))
async def regen_call(client: Client, cq: CallbackQuery):
    # Read BIN from the existing message
    import re
    text = cq.message.text
    match = re.search(r"BIN: <code>(\d+)", text)
    if not match:
        await cq.answer("❌ Cannot find BIN!", show_alert=True)
        return
    cc = match.group(1)

    # Generate new random cards with the same BIN
    delete_msg = await cq.message.edit_text("<b>Regenerating...</b>", parse_mode="html")
    start = time.perf_counter()
    all_cards = await luhn_card_genarator(cc, None, None, None, 10)
    cards_text = generate_code_blocks(all_cards)

    # Get BIN info again
    bin_info = await get_bin_info(cc[:6])
    brand, type_, level, bank, country, flag, currency = bin_info

    # Build response
    user_id = cq.from_user.id
    rol = "User"  # replace with role fetching if needed
    response_text = (
        f"- 𝐂𝐂 Regenerated Successfully\n"
        f"- BIN: <code>{cc}</code>\n\n"
        f"{cards_text}"
        f"- Info: {brand} - {type_} - {level}\n"
        f"- Bank: {bank} 🏛\n"
        f"- Country: {country} {flag}\n\n"
        f"- Time: {time.perf_counter()-start:.2f}s\n"
        f"- Checked by: <a href='tg://user?id={user_id}'>{cq.from_user.first_name}</a> [{rol}]"
    )

    await cq.message.edit_text(response_text, parse_mode="html", reply_markup=buttons)
        
