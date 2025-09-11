from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Store results for each user
mass_results = {}

@Client.on_message(filters.command("mchk", [".", "/"]))
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

        if not checkall[0]:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if getcc[0] == False:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]

        # Init result store
        mass_results[user_id] = {"approved": [], "declined": []}

        nov = await message.reply_text(
            f"🔎 Mass Braintree Auth Started\nTotal Cards: {len(ccs)}\n\nProcessing...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"✅ Approved (0)", callback_data=f"mass_show|{user_id}|approved")],
                [InlineKeyboardButton(f"❌ Declined (0)", callback_data=f"mass_show|{user_id}|declined")]
            ])
        )

        start = time.perf_counter()
        works = [mchkfunc(i, user_id) for i in ccs]
        worker_num = int(json.loads(open("FILES/config.json", "r", encoding="utf-8").read())["THREADS"])
        amt = 0

        while works:
            batch = works[:worker_num]
            batch = await asyncio.gather(*batch)
            for res in batch:
                amt += 1
                if "Approved ✅" in res:
                    mass_results[user_id]["approved"].append(res)
                else:
                    mass_results[user_id]["declined"].append(res)

                # Update buttons dynamically
                await nov.edit_reply_markup(
                    InlineKeyboardMarkup([
                        [InlineKeyboardButton(f"✅ Approved ({len(mass_results[user_id]['approved'])})",
                                              callback_data=f"mass_show|{user_id}|approved")],
                        [InlineKeyboardButton(f"❌ Declined ({len(mass_results[user_id]['declined'])})",
                                              callback_data=f"mass_show|{user_id}|declined")]
                    ])
                )
            works = works[worker_num:]

        proxy_status = "Live ✨"
        taken = time.perf_counter() - start

        await nov.edit_text(
            f"✅ Mass Check Finished!\n\n"
            f"Approved: {len(mass_results[user_id]['approved'])}\n"
            f"Declined: {len(mass_results[user_id]['declined'])}\n\n"
            f"Checked by: <a href='tg://user?id={message.from_user.id}'>{first_name}</a> [{role}]\n"
            f"T/t: {taken:0.2f}s | Proxy: {proxy_status}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"✅ Approved ({len(mass_results[user_id]['approved'])})",
                                      callback_data=f"mass_show|{user_id}|approved")],
                [InlineKeyboardButton(f"❌ Declined ({len(mass_results[user_id]['declined'])})",
                                      callback_data=f"mass_show|{user_id}|declined")]
            ])
        )

        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


@Client.on_callback_query(filters.regex(r"^mass_show\|"))
async def mass_show_handler(client, cq):
    _, uid, result_type = cq.data.split("|")
    uid = str(uid)

    if uid not in mass_results:
        await cq.answer("⚠️ Session expired!", show_alert=True)
        return

    results = mass_results[uid][result_type]
    if not results:
        await cq.answer(f"No {result_type} cards found.", show_alert=True)
        return

    # Split results into chunks (Telegram limit ~4000 chars)
    chunk_size = 30
    for i in range(0, len(results), chunk_size):
        part = results[i:i + chunk_size]
        text = f"**{result_type.capitalize()} Cards ({len(part)}/{len(results)})**\n\n" + "\n".join(part)
        await cq.message.reply_text(text)

    await cq.answer()
        
