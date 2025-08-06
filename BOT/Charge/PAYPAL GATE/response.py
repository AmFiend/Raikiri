import traceback
from FUNC.defs import *
from FUNC.usersdb_func import *


async def get_charge_resp(result, user_id, fullcc):
    try:
        status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
        response = "Card Declined ❌"
        hits = "NO"

        # Successful charges
        if (
            '"status": "succeeded"' in result or
            "Thank You For Donation" in result or
            "Your payment has already been processed" in result or
            "ADD_SHIPPING_ERROR" in result or
            "Success" in result
        ):
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response = "Payment Approved [CVV] 🔥"
            hits = "YES"
            await forward_resp(fullcc, "PayPal Charge", response)

        # 3D Secure requirements
        elif "is3DSecureRequired" in result or "OTP" in result:
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response = "3D Secure Challenge Required 🔐"
            hits = "YES"
            await forward_resp(fullcc, "PayPal Charge", response)

        # CVC-related approvals
        elif "INVALID_SECURITY_CODE" in result:
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response = "CCN Live [CVV2] ✅"
            hits = "YES"
            await forward_resp(fullcc, "PayPal Charge", response)

        # Address-related approvals
        elif "INVALID_BILLING_ADDRESS" in result:
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response = "Approved - Invalid Address 🏠"
            hits = "YES"
            await forward_resp(fullcc, "PayPal Charge", response)

        # Account restrictions
        elif "EXISTING_ACCOUNT_RESTRICTED" in result:
            status = "𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅"
            response = "Approved - Account Limited ⚠️"
            hits = "YES"
            await forward_resp(fullcc, "PayPal Charge", response)

        # Proxy errors
        elif "ProxyError" in result or "ConnectionError" in result:
            status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
            response = "Proxy Connection Failed 🔌"
            hits = "NO"
            await refundcredit(user_id)

        # Standard declines
        elif any(x in result for x in ["CARD_DECLINED", "declined", "invalid_card"]):
            status = "𝗗𝗲𝗰𝗹𝗶𝗻𝗲𝗱 ❌"
            response = "Generic Decline ❌"
            hits = "NO"

        # Fallback error logging
        else:
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            response = await find_between(result.text, "System was not able to complete the payment. ", ".")
            if response is None:
                response = "Card Declined"
                await result_logs(fullcc, "PayPal Charge", result)
            response = response + " ❌"
            hits = "NO"

        json_response = {
            "status": status,
            "response": response,
            "hits": hits,
            "fullz": fullcc,
        }
        return json_response

    except Exception as e:
        status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
        response = str(e) + " ❌"
        hits = "NO"

        json = {
            "status": status,
            "response": response,
            "hits": hits,
            "fullz": fullcc,
        }
        return json
