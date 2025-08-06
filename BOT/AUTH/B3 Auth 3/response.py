import traceback
from FUNC.defs import *
from FUNC.usersdb_func import *


async def get_charge_resp(result, user_id, fullcc):
    try:
        if type(result) == str:
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            code_text = result
            hits = "NO"

            if "Status code avs: Gateway Rejected: avs" in result:
                status = "Approved ✅"
                response = "1000: Approved"
                hits = "YES"
                await forward_resp(fullcc, "BRAINTREE AUTH", response)

            elif "Status code cvv: Gateway Rejected: cvv" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Gateway Rejected: cvv"
                hits = "NO"

            elif "Status code 2047: Call Issuer. Pick Up Card. (57 : TRAN NOT ALLOWED)" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2047: Call Issuer. Pick Up Card"
                hits = "NO"

            elif "Cannot Authorize at this time" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Cannot Authorize at this time (Policy)"
                hits = "NO"

            elif "Status code 2000: Do Not Honor (51 : DECLINED)" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2000: Do Not Honor"
                hits = "NO"

            elif "Status code avs_and_cvv: Gateway Rejected: avs_and_cvv" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Avs_and_Cvv"
                hits = "NO"

            elif "Status code 2038: Processor Declined (63 : SERV NOT ALLOWED)" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2038: Processor Declined"
                hits = "NO"

            elif "Status code risk_threshold: Gateway Rejected: risk_threshold" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Gateway Rejected: risk_threshold"
                hits = "NO"

            elif "Status code 2004: Expired Card (54 : EXPIRED CARD)" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2004: Expired Card"
                hits = "NO"

            elif "Status code 2108: Closed Card (51 : DECLINED)" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2108: Closed Card (51 : DECLINED)"
                hits = "NO"

            elif ("Status code 2057: Issuer or Cardholder has put a restriction on the card (63 : SERV NOT ALLOWED)" in result
                  or "Status code 2057" in result):
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "2057: Issuer or Cardholder has put a restriction on the card"
                hits = "NO"

            elif "ProxyError" in result:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                response = "Proxy Connection Refused"
                hits = "NO"
                await refundcredit(user_id)

            else:
                status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
                try:
                    response = result.split('"message": "')[1].split('"')[0] + " ❌"
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