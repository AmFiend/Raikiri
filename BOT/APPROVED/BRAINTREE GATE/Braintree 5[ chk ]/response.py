import urllib.parse
import json
import re

async def get_charge_resp(result, user_id=None, fullcc=None):
    try:
        # Ensure result is string
        if isinstance(result, bytes):
            result_str = result.decode('utf-8', errors='ignore')
        elif isinstance(result, str):
            result_str = result
        else:
            return {
                "status": "Declined ❌",
                "response": "Invalid response format",
                "hits": "NO",
                "fullz": fullcc,
            }

        # Try parse JSON first (for JSON error structured responses)
        try:
            resp_json = json.loads(result_str)
            if "success" in resp_json and not resp_json["success"]:
                # Extract error messages from common keys or fallback
                error_msg = resp_json.get("error_messages") or resp_json.get("message") or "Transaction declined"
                # Clean possible codes with regex e.g. 15005-This ...
                clean_msg = re.sub(r"^\d+-", "", error_msg).strip()
                return {
                    "status": "Declined ❌",
                    "response": clean_msg,
                    "hits": "NO",
                    "fullz": fullcc,
                }
            else:  # success case
                return {
                    "status": "Approved ✅",
                    "response": resp_json.get("message", "Transaction approved"),
                    "hits": "YES",
                    "fullz": fullcc,
                }
        except (json.JSONDecodeError, TypeError):
            # Not JSON, proceed with legacy URL-encoded parsing
            response_dict = dict(urllib.parse.parse_qsl(result_str))
            result_code = int(response_dict.get("RESULT", "-1"))
            resp_msg = response_dict.get("RESPMSG", "")
            resp_msg_lower = resp_msg.lower()

            # Check decline first
            if result_code != 0:
                # Similar clean code removal from raw message if present
                clean_msg = re.sub(r"^\d+-", "", resp_msg).strip()
                decline_msg = clean_msg or "Transaction declined"
                return {
                    "status": "Declined ❌",
                    "response": decline_msg,
                    "hits": "NO",
                    "fullz": fullcc,
                }

            # Check challenge-required states
            challenge_keywords = ["challenge required", "3d secure", "authentication required"]
            if any(kw in resp_msg_lower for kw in challenge_keywords):
                return {
                    "status": "Challenge 🔒",
                    "response": "3D Secure Challenge Required",
                    "hits": "MAYBE",
                    "fullz": fullcc,
                }

            # Else approved
            approved_message = resp_msg or "Approved or completed successfully"
            return {
                "status": "Approved ✅",
                "response": approved_message,
                "hits": "YES",
                "fullz": fullcc,
            }

    except Exception as e:
        return {
            "status": "Declined ❌",
            "response": f"Exception parsing response: {str(e)}",
            "hits": "NO",
            "fullz": fullcc,
        }
