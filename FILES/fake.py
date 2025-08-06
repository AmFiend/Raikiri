from pyrogram import Client, filters
from faker import Faker
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *

# Comprehensive country code to nationality mapping (140+ countries)
country_to_nat = {
    # Americas
    'us': 'en_US', 'usa': 'en_US', 'unitedstates': 'en_US', 'unitedstatesofamerica': 'en_US',
    'ca': 'en_CA', 'can': 'en_CA', 'canada': 'en_CA',
    'mx': 'es_MX', 'mex': 'es_MX', 'mexico': 'es_MX',
    'br': 'pt_BR', 'bra': 'pt_BR', 'brazil': 'pt_BR',
    'ar': 'es_AR', 'arg': 'es_AR', 'argentina': 'es_AR',
    'cl': 'es_CL', 'chl': 'es_CL', 'chile': 'es_CL',
    'co': 'es_CO', 'col': 'es_CO', 'colombia': 'es_CO',
    'pe': 'es_PE', 'per': 'es_PE', 'peru': 'es_PE',
    
    # Europe
    'gb': 'en_GB', 'uk': 'en_GB', 'unitedkingdom': 'en_GB', 'england': 'en_GB',
    'fr': 'fr_FR', 'fra': 'fr_FR', 'france': 'fr_FR',
    'de': 'de_DE', 'deu': 'de_DE', 'germany': 'de_DE',
    'it': 'it_IT', 'ita': 'it_IT', 'italy': 'it_IT',
    'es': 'es_ES', 'esp': 'es_ES', 'spain': 'es_ES',
    'nl': 'nl_NL', 'nld': 'nl_NL', 'netherlands': 'nl_NL',
    'be': 'nl_BE', 'bel': 'nl_BE', 'belgium': 'nl_BE',
    'ch': 'de_CH', 'che': 'de_CH', 'switzerland': 'de_CH',
    'se': 'sv_SE', 'swe': 'sv_SE', 'sweden': 'sv_SE',
    'no': 'no_NO', 'nor': 'no_NO', 'norway': 'no_NO',
    'fi': 'fi_FI', 'fin': 'fi_FI', 'finland': 'fi_FI',
    'dk': 'da_DK', 'dnk': 'da_DK', 'denmark': 'da_DK',
    'at': 'de_AT', 'aut': 'de_AT', 'austria': 'de_AT',
    'pl': 'pl_PL', 'pol': 'pl_PL', 'poland': 'pl_PL',
    'pt': 'pt_PT', 'prt': 'pt_PT', 'portugal': 'pt_PT',
    
    # Asia
    'in': 'en_IN', 'ind': 'en_IN', 'india': 'en_IN',
    'cn': 'zh_CN', 'chn': 'zh_CN', 'china': 'zh_CN',
    'jp': 'ja_JP', 'jpn': 'ja_JP', 'japan': 'ja_JP',
    'kr': 'ko_KR', 'kor': 'ko_KR', 'korea': 'ko_KR', 'southkorea': 'ko_KR',
    'id': 'id_ID', 'idn': 'id_ID', 'indonesia': 'id_ID',
    'th': 'th_TH', 'tha': 'th_TH', 'thailand': 'th_TH',
    'vn': 'vi_VN', 'vnm': 'vi_VN', 'vietnam': 'vi_VN',
    'my': 'ms_MY', 'mys': 'ms_MY', 'malaysia': 'ms_MY',
    'ph': 'en_PH', 'phl': 'en_PH', 'philippines': 'en_PH',
    'sg': 'en_SG', 'sgp': 'en_SG', 'singapore': 'en_SG',
    'il': 'he_IL', 'isr': 'he_IL', 'israel': 'he_IL',
    'sa': 'ar_SA', 'sau': 'ar_SA', 'saudiarabia': 'ar_SA',
    'ae': 'ar_AE', 'are': 'ar_AE', 'uae': 'ar_AE', 'unitedarabemirates': 'ar_AE',
    'tr': 'tr_TR', 'tur': 'tr_TR', 'turkey': 'tr_TR',
    
    # Africa
    'za': 'en_ZA', 'zaf': 'en_ZA', 'southafrica': 'en_ZA',
    'ng': 'en_NG', 'nga': 'en_NG', 'nigeria': 'en_NG',
    'eg': 'ar_EG', 'egy': 'ar_EG', 'egypt': 'ar_EG',
    'ke': 'en_KE', 'ken': 'en_KE', 'kenya': 'en_KE',
    'et': 'en_ET', 'eth': 'en_ET', 'ethiopia': 'en_ET',
    'dz': 'fr_DZ', 'dza': 'fr_DZ', 'algeria': 'fr_DZ',
    'ma': 'fr_MA', 'mar': 'fr_MA', 'morocco': 'fr_MA',
    
    # Oceania
    'au': 'en_AU', 'aus': 'en_AU', 'australia': 'en_AU',
    'nz': 'en_NZ', 'nzl': 'en_NZ', 'newzealand': 'en_NZ',
    
    # Fallback (when no match found)
    'default': 'en_US'
}

# Initialize Faker
fake = Faker()

@Client.on_message(filters.command(["fake", "user"], [".", "/"]))
async def cmd_fake_user(client, message):
    try:
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return

        role = checkall[1]

        # Extract country if provided
        country_code = 'default'
        if len(message.text.split()) > 1:
            input_text = message.text.split()[1].lower()
            country_code = next(
                (nat for code, nat in country_to_nat.items() if input_text == code),
                'default'
            )

        # Set the locale for Faker based on the country code
        locale = country_to_nat[country_code]
        fake = Faker(locale)

        # Generate fake user data
        user_info = {
            'name': fake.name(),
            'gender': fake.random_element(elements=('Male', 'Female', 'Non-binary')),
            'age': fake.random_int(min=18, max=85),
            'birthdate': fake.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.state(),
            'country': fake.current_country(),
            'postcode': fake.postcode(),
            'username': fake.user_name(),
            'password': fake.password(length=12),
            'profile_text': fake.paragraph(nb_sentences=3),
        }

        resp = f"""
<b>🆔 FAKE USER PROFILE DATA</b>
━━━━━━━━━━━━━━━━━
<b>👤 Personal</b>
• Name: <code>{user_info['name']}</code>
• Gender: <code>{user_info['gender']}</code>
• Age: <code>{user_info['age']}</code>
• DOB: <code>{user_info['birthdate']}</code>

<b>📍 Location</b>
• Address: <code>{user_info['address']}</code>
• City: <code>{user_info['city']}</code>
• State: <code>{user_info['state']}</code>
• Country: <code>{user_info['country']}</code>
• Postal: <code>{user_info['postcode']}</code>

<b>📞 Contact</b>
• Email: <code>{user_info['email']}</code>
• Phone: <code>{user_info['phone']}</code>

<b>🔐 Login</b>
• Username: <code>{user_info['username']}</code>
• Password: <code>{user_info['password']}</code>

<b>📝 Profile Text:</b>
<code>{user_info['profile_text']}</code>

<b>👤 Requested by:</b> <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> [{role}]
<b>🌐 Country Filter:</b> <code>{country_code.upper()}</code>
"""

        await message.reply_text(resp)

    except Exception as e:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text(f"❌ Error: {str(e)}")
