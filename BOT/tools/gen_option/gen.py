import asyncio
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from FUNC.cc_gen import luhn_card_genarator, get_bin_details  # make sure get_bin_details exists

# Store user regen data
regen_store = {}

buttons = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🔄 Regen", callback_data="regen")],
        [InlineKeyboardButton("❌ Exit", callback_data="exit")]
    ]
)

def generate_code_blocks(all_cards):
    code_blocks = ""
    cards = all_cards.split('\n')
    for card in cards:
        if card.strip():
            code_blocks += f"<code>{card}</code>\n"
    return code_blocks

async def gen_cmd(client, message, from_regen=False, user_data=None):
    try:
        user_id = str(message.from_user.id)

        # Get BIN and other info
        if not from_regen:
            try:
                ccsdata = message.text.split()[1]
                cc_parts = ccsdata.split("|")
                cc = cc_parts[0]
                mes = cc_parts[1] if len(cc_parts) > 1 else None
                ano = cc_parts[2] if len(cc_parts) > 2 else None
                cvv = cc_parts[3] if len(cc_parts) > 3 else None
            except IndexError:
                await message.reply_text(
                    "<b>Wrong Format ❌\nUsage: /gen 515462xxxxxx|11|2030|123</b>",
                    parse_mode="html"
                )
                return

            try:
                amount = int(message.text.split()[2])
            except (IndexError, ValueError):
                amount = 10
            # Save for regen
            regen_store[user_id] = {"cc": cc, "mes": mes, "ano": ano, "cvv": cvv, "amount": amount}
        else:
            cc = user_data["cc"]
            mes = user_data["mes"]
            ano = user_data["ano"]
            cvv = user_data["cvv"]
            amount = user_data["amount"]

        # Send "Generating..." placeholder
        gen_msg = await message.reply_text("<b>Generating...</b>", parse_mode="html")

        start = time.perf_counter()
        getbin = await get_bin_details(cc[:6])  # make sure this function exists
        brand, type_, level, bank, country, flag, currency = getbin

        all_cards = await luhn_card_genarator(cc, mes, ano, cvv, amount)
        code_blocks = generate_code_blocks(all_cards)

        # Build response
        response_text = (
            f"- 𝐂𝐂 Generated Successfully\n"
            f"- BIN: <code>{cc}</code>\n"
            f"- Amount: {amount}\n\n"
            f"{code_blocks}"
            f"- Info: {brand} - {type_} - {level}\n"
            f"- Bank: {bank} 🏛\n"
            f"- Country: {country} {flag}\n"
            f"- Time: {time.perf_counter() - start:.2f} sec"
        )

        # Edit original "Generating..." message
        await gen_msg.edit_text(response_text, parse_mode="html", reply_markup=buttons)

    except Exception as e:
        await message.reply_text(f"<b>Error:</b> {e}", parse_mode="html")


@Client.on_message(filters.command("gen", [".", "/"]))
async def gen_handler(client, message):
    await gen_cmd(client, message)


@Client.on_callback_query(filters.regex(r"^regen"))
async def regen_call(client, callback_query):
    user_id = str(callback_query.from_user.id)
    if user_id not in regen_store:
        await callback_query.answer("⚠️ No previous generation found.", show_alert=True)
        return
    user_data = regen_store[user_id]
    await regen_cards(client, callback_query, user_data)


async def regen_cards(client, callback_query, user_data):
    # Regenerate in-place
    await gen_cmd(client, callback_query.message, from_regen=True, user_data=user_data)
    await callback_query.answer("🔄 Cards regenerated!", show_alert=False)
                
