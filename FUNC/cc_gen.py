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

    if mes not in ["None", "rnd"] and len(mes) == 1:
        mes = "0" + mes
    if ano not in ["None", "rnd"] and len(ano) == 2:
        ano = "20" + ano

    # Fill X with random digits
    for i in range(len(cc)):
        if cc[i] in ["x", "X"]:
            cc = cc[:i] + str(random.randint(0, 9)) + cc[i+1:]

    if mes in ["None", "rnd"] or "x" in mes.lower():
        mes = str(random.randint(1, 12)).zfill(2)
    if ano in ["None", "rnd"] or "x" in ano.lower():
        ano = str(random.randint(2024, 2035))
    if cvv in ["None", "rnd"] or "x" in cvv.lower():
        if cc[:2] in ["34", "37"]:
            cvv = str(random.randint(1000, 9999))
        else:
            cvv = str(random.randint(100, 999))
    
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


async def get_bin_info(bin_number):
    """
    Returns BIN details.
    Replace with real BIN database if available.
    """
    # Dummy info for now
    brand = "MASTERCARD"
    type_ = "DEBIT"
    level = "GIFT"
    bank = "BANCORP BANK"
    country = "United States"
    flag = "🇺🇸"
    currency = "USD"
    return brand, type_, level, bank, country, flag, currency
            
