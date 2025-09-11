import random

async def checkLuhn(cardNo):
    nDigits = len(cardNo)
    nSum = 0
    isSecond = False
    for i in range(nDigits - 1, -1, -1):
        d = ord(cardNo[i]) - ord("0")
        if isSecond:
            d *= 2
        nSum += d // 10
        nSum += d % 10
        isSecond = not isSecond
    return nSum % 10 == 0


async def cc_genarator(cc, mes, ano, cvv):
    cc, mes, ano, cvv = str(cc), str(mes), str(ano), str(cvv)

    if mes not in ("None", "rnd") and len(mes) == 1:
        mes = "0" + mes
    if ano not in ("None", "rnd") and len(ano) == 2:
        ano = "20" + ano

    numbers = list("0123456789")
    random.shuffle(numbers)
    result = "".join(numbers)
    result = cc + result

    if cc[:2] in ("37", "34"):
        cc = result[:15]
    else:
        cc = result[:16]

    # Replace Xs with random digits
    cc = ''.join(str(random.randint(0, 9)) if c == 'x' else c for c in cc)

    # Expiration month
    if mes in ("None", "rnd") or 'x' in mes.lower():
        mes = str(random.randint(1, 12)).zfill(2)
    # Expiration year
    if ano in ("None", "rnd") or 'x' in ano.lower():
        ano = str(random.randint(2024, 2035))
    # CVV
    if cvv in ("None", "rnd") or 'x' in cvv.lower():
        cvv = str(random.randint(1000, 9999) if cc[:2] in ("37", "34") else random.randint(100, 999))

    return f"{cc}|{mes}|{ano}|{cvv}"


async def luhn_card_genarator(cc, mes, ano, cvv, amount):
    all_cards = ""
    for _ in range(amount):
        while True:
            result = await cc_genarator(cc, mes, ano, cvv)
            ccx, mesx, anox, cvvx = result.split("|")
            if await checkLuhn(ccx):
                all_cards += f"{ccx}|{mesx}|{anox}|{cvvx}\n"
                break
    return all_cards


# --------- BIN Info Function ---------
# This is the replacement for get_bin_info/get_bin_details
async def get_bin_details(bin_number):
    """
    Return BIN info for first 6 digits of a card.
    For simplicity, this example returns dummy data.
    Replace with real BIN lookup if needed.
    """
    # bin_number = str(bin_number)[:6]  # already assumed
    brand = "MASTERCARD"
    type_ = "DEBIT"
    level = "GIFT"
    bank = "BANCORP BANK, THE"
    country = "United States"
    flag = "🇺🇸"
    currency = "USD"
    return brand, type_, level, bank, country, flag, currency
    
