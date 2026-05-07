import re
import json
import random

decline_reasons = {
    "incorrect card number": "Incorrect Card Number",
    "generic declined": "Generic Declined", 
    "do not honor": "Do Not Honor",
    "card declined": "Card Declined",
    "insufficient funds": "Insufficient Funds",
    "expired card": "Expired Card",
    "fail": "Failed",
    "error": "Error",
    "your card was declined": "Card Declined",
    "declined": "Card Declined",
}

stripe_decline_codes = [
    "Do Not Honor",
    "Insufficient Funds", 
    "Expired Card",
    "Incorrect Card Number",
    "Card Declined",
    "Lost Card",
    "Stolen Card",
    "Restricted Card",
    "Processing Error",
    "Invalid CVV",
    "CVV Failure",
    "Issuer Unavailable"
]

approve_reasons = {
    "ccN": "CCN",
    "charge successful": "Charge Successful ✅",
    "00": "Approved",
    "08": "Honor with Identification",
    "10": "Approved for Partial Amount",
    "11": "Approved VIP",
    "16": "Approved, Update Track 3",
    "91": "Issuer or switch is inoperative",
    "card approved": "Card Approved",
    "payment succeeded": "Payment Succeeded",
    "payment successful": "Payment Successful",
}

def clean_html_response(raw_response: str):
    """
    Optimized for tokens.php endpoint:
    - generic_decline → rotates real Stripe codes
    - Preserves any detailed Response if available
    """
    if not raw_response or raw_response.strip() == "":
        return "Declined ❌", "Card Declined ❌"

    # Try JSON parsing first
    try:
        response_data = json.loads(raw_response)
        api_status = response_data.get("status", False)
        api_response = response_data.get("Response", "").lower().strip()
        api_status_text = response_data.get("Status", "").lower()
        
        if api_status is True:
            return "Approved ✅", "Payment Success ✅"
        
        # tokens.php pattern: "Declined ❌" + "generic_decline" → ROTATE
        if "generic_decline" in api_status_text:
            rotated_decline = random.choice(stripe_decline_codes)
            return "DECLINED ❌", rotated_decline
        
        # Map any detailed decline reasons
        for key, val in decline_reasons.items():
            if key in api_response or key in api_status_text:
                return "Declined ❌", val
        
        return "Declined ❌", "Card Declined ❌"
        
    except json.JSONDecodeError:
        pass

    # HTML fallback
    text_only = re.sub(r"<[^>]*>", "", raw_response).strip()
    text_lower = text_only.lower()

    for key, val in decline_reasons.items():
        if key in text_lower:
            return "Declined ❌", val

    if re.search(r"aprovada|successfully charged|success|approved|payment succeeded|payment successful", text_lower):
        for key, val in approve_reasons.items():
            if key.lower() in text_lower:
                return "Approved ✅", val
        return "Approved ✅", "Payment Success"

    return "Declined ❌", "Card Declined ❌"

def extract_decline_reason(text: str):
    lower = text.lower()
    for key, val in decline_reasons.items():
        if key in lower:
            return val
    return None