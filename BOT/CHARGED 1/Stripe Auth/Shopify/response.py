import json
import html

async def get_charge_resp(result, user_id, fullcc):
    try:
        try:
            res_json = json.loads(result) if result.strip().startswith("{") else None
            resp_text = res_json.get("Response", "") if res_json else result
            price = res_json.get("Price", "") if res_json else ""
        except Exception:
            resp_text = result
            price = ""

        sanitized_resp = resp_text.replace('<br>', '\n').replace('<br />', '\n').replace('<br/>', '\n')
        sanitized_resp = html.unescape(sanitized_resp)
        upper_resp = sanitized_resp.upper()

        approved_tokens_special = ["3D CC", "INVALID_CVC", "INSUFFICIENT_FUNDS", "INCORRECT_CVC"]
        approved_tokens_generic = ["THANK YOU", "THANKYOU", "THANK YOU FOR YOUR PURCHASE", "ORDER IS CONFIRMED", "SUCCESS"]
        declined_tokens = ["PROXYERROR"]

        if any(token in upper_resp for token in approved_tokens_special):
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            response = sanitized_resp
            hits = "YES"
        elif any(token in upper_resp for token in approved_tokens_generic):
            status = "𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 ✅"
            response = f"Thank You For Your donation of ${price}" if price else "Thank You"
            hits = "YES"
        elif any(token in upper_resp for token in declined_tokens):
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            response = "Proxy Connection Refused"
            hits = "NO"
        else:
            status = "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌"
            response = sanitized_resp if sanitized_resp else "Card was declined"
            hits = "NO"

        return {
            "status": status,
            "response": response,
            "hits": hits,
            "price": price,
            "fullz": fullcc
        }
    except Exception as e:
        return {
            "status": "𝐃𝐞𝐜𝐥𝐢𝐧𝐞𝐝 ❌",
            "response": str(e),
            "hits": "NO",
            "price": "",
            "fullz": fullcc
        }
