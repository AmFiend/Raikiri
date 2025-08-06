import traceback
from FUNC.defs import *
from FUNC.usersdb_func import *


async def get_charge_resp(result, user_id, fullcc):
    try:

        if type(result) == str:
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            code_text = result
            hits = "NO"

            if (
                "Payment method successfully added." in result
            ):
                status = "Approved ✅"
                # response = "Approved ✅"
                response = "1000: Approved"
                hits = "YES"
                await forward_resp(fullcc, "BRAINTREE AUTH", response)

            elif ("Status code cvv: Gateway Rejected: cvv" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Gateway Rejected: cvv"
                hits = "NO"

            elif ("Declined - Call Issuer" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Declined - Call Issuer"
                hits = "NO"
                
            elif ("2004: Expired Card (54 : EXPIRED CARD)" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2004: Expired Card"
                hits = "NO"
                                
                
            elif ("81724: Duplicate card exists in the vault." in result):
                status = "Approved ✅"
                response = "1000: Approved"
                hits = "YES"

            elif ("Cannot Authorize at this time" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2106: Cannot Authorize at this time (Policy)"
                hits = "NO"

            elif ("Processor Declined - Fraud Suspected" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Fraud Suspected"
                hits = "NO"

            elif "risk_threshold: Gateway Rejected: risk_threshold" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Gateway Rejected: risk_threshold."
                hits = "NO"

            elif ("We're sorry, but the payment validation failed. Declined - Call Issuer" in result or
                  "Payment failed: Declined - Call Issuer" in result
                  ):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2044: Declined - Call Issuer"
                hits = "NO"

            elif "ProxyError" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Proxy Connection Refused"
                hits = "NO"
                await refundcredit(user_id)

            else:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                try:
                    response = result.split('"message": "')[
                        1].split('"')[0] + " ❌"
                except:
                    response = result
                    await result_logs(fullcc, "Braintree Auth", result)
                hits = "NO"

        json = {
            "status": status,
            "response": response,
            "hits": hits,
            "fullz": fullcc,
        }
        return json

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
