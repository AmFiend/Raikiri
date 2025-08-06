import httpx
import random
import pycountry
from faker import Faker
from pyrogram import Client, filters
from FUNC.usersdb_func import *
from TOOLS.check_all_func import *
from countryinfo import CountryInfo
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import re
import unicodedata

# Import database functions (for API management)
from FUNC.defs import error_log

# Comprehensive world regions for better organization
WORLD_REGIONS = {
    'AFRICA_NORTH': ['ma', 'dz', 'tn', 'ly', 'eg', 'sd', 'er', 'dj', 'so', 'mr', 'eh'],
    'AFRICA_WEST': ['ng', 'gh', 'ci', 'sn', 'ml', 'bf', 'bj', 'gm', 'gn', 'gw', 'lr', 'ne', 'sl', 'tg', 'cv'],
    'AFRICA_CENTRAL': ['cd', 'cm', 'cg', 'ga', 'gq', 'cf', 'st', 'td'],
    'AFRICA_EAST': ['ke', 'tz', 'ug', 'et', 'ss', 'so', 'rw', 'bi', 'dj', 'er', 'km', 'mg', 'mu', 'sc', 'yt', 're'],
    'AFRICA_SOUTH': ['za', 'na', 'bw', 'ls', 'sz', 'zw', 'mz', 'zm', 'mw', 'ao'],
    
    'AMERICAS_NORTH': ['us', 'ca', 'gl', 'pm', 'bm'],
    'AMERICAS_CENTRAL': ['mx', 'gt', 'bz', 'sv', 'hn', 'ni', 'cr', 'pa'],
    'AMERICAS_CARIBBEAN': ['cu', 'jm', 'ht', 'do', 'pr', 'bs', 'bb', 'tt', 'dm', 'lc', 'vc', 'gd', 'kn', 'ag', 'tc', 'vg', 'ai', 'aw', 'cw', 'sx', 'bq', 'ms', 'ky', 'mq', 'gp', 'bl', 'mf'],
    'AMERICAS_SOUTH': ['br', 'ar', 'cl', 'co', 'pe', 've', 'ec', 'bo', 'py', 'uy', 'gy', 'sr', 'gf', 'fk', 'gs'],
    
    'ASIA_CENTRAL': ['kz', 'uz', 'tm', 'kg', 'tj'],
    'ASIA_EAST': ['cn', 'jp', 'kr', 'kp', 'tw', 'hk', 'mo', 'mn'],
    'ASIA_SOUTH': ['in', 'pk', 'bd', 'np', 'lk', 'bt', 'mv'],
    'ASIA_SOUTHEAST': ['id', 'th', 'vn', 'my', 'ph', 'sg', 'mm', 'kh', 'la', 'bn', 'tl'],
    'ASIA_WEST': ['tr', 'ir', 'iq', 'sa', 'ye', 'sy', 'ae', 'il', 'jo', 'lb', 'om', 'kw', 'qa', 'bh', 'ps', 'cy', 'ge', 'am', 'az'],
    
    'EUROPE_NORTH': ['se', 'no', 'fi', 'dk', 'is', 'ee', 'lv', 'lt', 'fo', 'sj', 'ax'],
    'EUROPE_WEST': ['uk', 'ie', 'fr', 'de', 'nl', 'be', 'lu', 'ch', 'at', 'li', 'mc', 'im', 'gg', 'je'],
    'EUROPE_EAST': ['ru', 'ua', 'by', 'pl', 'ro', 'cz', 'hu', 'bg', 'sk', 'md'],
    'EUROPE_SOUTH': ['es', 'it', 'pt', 'gr', 'hr', 'rs', 'ba', 'al', 'mk', 'si', 'me', 'mt', 'sm', 'va', 'gi', 'ad'],
    
    'OCEANIA_AUSTRALIA': ['au', 'nz', 'cc', 'cx', 'hm', 'nf'],
    'OCEANIA_MELANESIA': ['pg', 'fj', 'sb', 'vu', 'nc'],
    'OCEANIA_MICRONESIA': ['fm', 'gu', 'ki', 'mh', 'nr', 'mp', 'pw'],
    'OCEANIA_POLYNESIA': ['pf', 'ws', 'to', 'tv', 'ck', 'nu', 'pn', 'tk', 'wf'],
    
    'ANTARCTICA': ['aq', 'bv', 'tf', 'gs']
}

# Global dictionary to map countries to regions
COUNTRY_TO_REGION = {}
for region, countries in WORLD_REGIONS.items():
    for country in countries:
        COUNTRY_TO_REGION[country] = region

# Expanded locales dictionary with nearly all world countries and flags
LOCALES = {
    # North America
    'us': ('en_US', '🇺🇸'), 'ca': ('en_CA', '🇨🇦'), 'mx': ('es_MX', '🇲🇽'),
    'gl': ('kl_GL', '🇬🇱'), 'pm': ('fr_PM', '🇵🇲'), 'bm': ('en_BM', '🇧🇲'),
    
    # Central America
    'gt': ('es_GT', '🇬🇹'), 'bz': ('en_BZ', '🇧🇿'), 'sv': ('es_SV', '🇸🇻'), 
    'hn': ('es_HN', '🇭🇳'), 'ni': ('es_NI', '🇳🇮'), 'cr': ('es_CR', '🇨🇷'), 
    'pa': ('es_PA', '🇵🇦'),
    
    # Caribbean
    'cu': ('es_CU', '🇨🇺'), 'jm': ('en_JM', '🇯🇲'), 'ht': ('fr_HT', '🇭🇹'), 
    'do': ('es_DO', '🇩🇴'), 'pr': ('es_PR', '🇵🇷'), 'bs': ('en_BS', '🇧🇸'), 
    'bb': ('en_BB', '🇧🇧'), 'tt': ('en_TT', '🇹🇹'), 'dm': ('en_DM', '🇩🇲'), 
    'lc': ('en_LC', '🇱🇨'), 'vc': ('en_VC', '🇻🇨'), 'gd': ('en_GD', '🇬🇩'), 
    'kn': ('en_KN', '🇰🇳'), 'ag': ('en_AG', '🇦🇬'),
    
    # South America
    'br': ('pt_BR', '🇧🇷'), 'ar': ('es_AR', '🇦🇷'), 'cl': ('es_CL', '🇨🇱'), 
    'co': ('es_CO', '🇨🇴'), 'pe': ('es_PE', '🇵🇪'), 've': ('es_VE', '🇻🇪'),
    'ec': ('es_EC', '🇪🇨'), 'bo': ('es_BO', '🇧🇴'), 'py': ('es_PY', '🇵🇾'), 
    'uy': ('es_UY', '🇺🇾'), 'gy': ('en_GY', '🇬🇾'), 'sr': ('nl_SR', '🇸🇷'), 
    'gf': ('fr_GF', '🇬🇫'),
    
    # Northern Europe
    'se': ('sv_SE', '🇸🇪'), 'no': ('no_NO', '🇳🇴'), 'fi': ('fi_FI', '🇫🇮'), 
    'dk': ('da_DK', '🇩🇰'), 'is': ('is_IS', '🇮🇸'), 'ee': ('et_EE', '🇪🇪'), 
    'lv': ('lv_LV', '🇱🇻'), 'lt': ('lt_LT', '🇱🇹'), 'fo': ('fo_FO', '🇫🇴'),
    
    # Western Europe
    'uk': ('en_GB', '🇬🇧'), 'ie': ('en_IE', '🇮🇪'), 'fr': ('fr_FR', '🇫🇷'), 
    'de': ('de_DE', '🇩🇪'), 'nl': ('nl_NL', '🇳🇱'), 'be': ('nl_BE', '🇧🇪'), 
    'lu': ('fr_LU', '🇱🇺'), 'ch': ('de_CH', '🇨🇭'), 'at': ('de_AT', '🇦🇹'),
    
    # Eastern Europe
    'ru': ('ru_RU', '🇷🇺'), 'ua': ('uk_UA', '🇺🇦'), 'by': ('be_BY', '🇧🇾'), 
    'pl': ('pl_PL', '🇵🇱'), 'ro': ('ro_RO', '🇷🇴'), 'cz': ('cs_CZ', '🇨🇿'), 
    'hu': ('hu_HU', '🇭🇺'), 'bg': ('bg_BG', '🇧🇬'), 'sk': ('sk_SK', '🇸🇰'), 
    'md': ('ro_MD', '🇲🇩'),
    
    # Southern Europe
    'es': ('es_ES', '🇪🇸'), 'it': ('it_IT', '🇮🇹'), 'pt': ('pt_PT', '🇵🇹'), 
    'gr': ('el_GR', '🇬🇷'), 'hr': ('hr_HR', '🇭🇷'), 'rs': ('sr_RS', '🇷🇸'), 
    'ba': ('bs_BA', '🇧🇦'), 'al': ('sq_AL', '🇦🇱'), 'mk': ('mk_MK', '🇲🇰'), 
    'si': ('sl_SI', '🇸🇮'), 'me': ('sr_ME', '🇲🇪'), 'mt': ('mt_MT', '🇲🇹'),
    
    # Northern Africa
    'ma': ('ar_MA', '🇲🇦'), 'dz': ('ar_DZ', '🇩🇿'), 'tn': ('ar_TN', '🇹🇳'), 
    'ly': ('ar_LY', '🇱🇾'), 'eg': ('ar_EG', '🇪🇬'), 'sd': ('ar_SD', '🇸🇩'),
    
    # Western Africa
    'ng': ('en_NG', '🇳🇬'), 'gh': ('en_GH', '🇬🇭'), 'ci': ('fr_CI', '🇨🇮'), 
    'sn': ('fr_SN', '🇸🇳'), 'ml': ('fr_ML', '🇲🇱'), 'bf': ('fr_BF', '🇧🇫'),
    
    # Eastern Africa - Using fallback locales for unsupported countries
    'ke': ('en_US', '🇰🇪'), 'tz': ('en_US', '🇹🇿'), 'ug': ('en_US', '🇺🇬'), 
    'et': ('en_US', '🇪🇹'), 'rw': ('fr_FR', '🇷🇼'), 'bi': ('fr_FR', '🇧🇮'),
    
    # Southern Africa
    'za': ('en_ZA', '🇿🇦'), 'na': ('en_NA', '🇳🇦'), 'bw': ('en_BW', '🇧🇼'), 
    'zw': ('en_ZW', '🇿🇼'), 'mz': ('pt_MZ', '🇲🇿'), 'zm': ('en_ZM', '🇿🇲'),
    
    # Central Asia
    'kz': ('kk_KZ', '🇰🇿'), 'uz': ('uz_UZ', '🇺🇿'), 'tm': ('tk_TM', '🇹🇲'), 
    'kg': ('ky_KG', '🇰🇬'), 'tj': ('tg_TJ', '🇹🇯'),
    
    # East Asia
    'cn': ('zh_CN', '🇨🇳'), 'jp': ('ja_JP', '🇯🇵'), 'kr': ('ko_KR', '🇰🇷'), 
    'kp': ('ko_KP', '🇰🇵'), 'tw': ('zh_TW', '🇹🇼'), 'hk': ('zh_HK', '🇭🇰'), 
    'mo': ('zh_MO', '🇲🇴'), 'mn': ('mn_MN', '🇲🇳'),
    
    # South Asia
    'in': ('en_IN', '🇮🇳'), 'pk': ('ur_PK', '🇵🇰'), 'bd': ('bn_BD', '🇧🇩'), 
    'np': ('ne_NP', '🇳🇵'), 'lk': ('si_LK', '🇱🇰'), 'bt': ('dz_BT', '🇧🇹'), 
    'mv': ('dv_MV', '🇲🇻'),
    
    # Southeast Asia
    'id': ('id_ID', '🇮🇩'), 'th': ('th_TH', '🇹🇭'), 'vn': ('vi_VN', '🇻🇳'), 
    'my': ('ms_MY', '🇲🇾'), 'ph': ('en_PH', '🇵🇭'), 'sg': ('en_SG', '🇸🇬'), 
    'mm': ('my_MM', '🇲🇲'), 'kh': ('km_KH', '🇰🇭'), 'la': ('lo_LA', '🇱🇦'), 
    'bn': ('ms_BN', '🇧🇳'), 'tl': ('pt_TL', '🇹🇱'),
    
    # Western Asia / Middle East
    'tr': ('tr_TR', '🇹🇷'), 'ir': ('fa_IR', '🇮🇷'), 'iq': ('ar_IQ', '🇮🇶'), 
    'sa': ('ar_SA', '🇸🇦'), 'ye': ('ar_YE', '🇾🇪'), 'sy': ('ar_SY', '🇸🇾'), 
    'ae': ('ar_AE', '🇦🇪'), 'il': ('he_IL', '🇮🇱'), 'jo': ('ar_JO', '🇯🇴'), 
    'lb': ('ar_LB', '🇱🇧'), 'om': ('ar_OM', '🇴🇲'), 'kw': ('ar_KW', '🇰🇼'), 
    'qa': ('ar_QA', '🇶🇦'), 'bh': ('ar_BH', '🇧🇭'), 'ps': ('ar_PS', '🇵🇸'), 
    'ge': ('ka_GE', '🇬🇪'), 'am': ('hy_AM', '🇦🇲'), 'az': ('az_AZ', '🇦🇿'),
    'cy': ('el_CY', '🇨🇾'), 'af': ('fa_AF', '🇦🇫'),
    
    # Oceania
    'au': ('en_AU', '🇦🇺'), 'nz': ('en_NZ', '🇳🇿'), 'pg': ('en_PG', '🇵🇬'), 
    'fj': ('en_FJ', '🇫🇯'), 'sb': ('en_SB', '🇸🇧'), 'vu': ('bi_VU', '🇻🇺'), 
    'fm': ('en_FM', '🇫🇲'), 'ki': ('en_KI', '🇰🇮'), 'ws': ('sm_WS', '🇼🇸'), 
    'to': ('to_TO', '🇹🇴'),
    
    # Small countries and territories with fallback locales
    'ad': ('ca_AD', '🇦🇩'), 'as': ('en_AS', '🇦🇸'), 'ai': ('en_AI', '🇦🇮'),
    'aw': ('nl_AW', '🇦🇼'), 'ax': ('sv_AX', '🇦🇽'), 'bj': ('fr_BJ', '🇧🇯'),
    'bq': ('nl_BQ', '🇧🇶'), 'cd': ('fr_CD', '🇨🇩'), 'cf': ('fr_CF', '🇨🇫'),
    'cg': ('fr_CG', '🇨🇬'), 'ck': ('en_CK', '🇨🇰'), 'cm': ('fr_CM', '🇨🇲'),
    'cv': ('pt_CV', '🇨🇻'), 'cw': ('nl_CW', '🇨🇼'), 'dj': ('fr_DJ', '🇩🇯'),
    'er': ('ti_ER', '🇪🇷'), 'fk': ('en_FK', '🇫🇰'), 'ga': ('fr_GA', '🇬🇦'),
    'gf': ('fr_GF', '🇬🇫'), 'gi': ('en_GI', '🇬🇮'), 'gm': ('en_GM', '🇬🇲'),
    'gn': ('fr_GN', '🇬🇳'), 'gp': ('fr_GP', '🇬🇵'), 'gq': ('es_GQ', '🇬🇶'),
    'gs': ('en_GS', '🏴'), 'gu': ('en_GU', '🇬🇺'), 'gw': ('pt_GW', '🇬🇼'),
    'gy': ('en_GY', '🇬🇾'), 'im': ('en_IM', '🇮🇲'), 'je': ('en_JE', '🇯🇪'),
    'km': ('ar_KM', '🇰🇲'), 'ky': ('en_KY', '🇰🇾'), 'li': ('de_LI', '🇱🇮'),
    'lr': ('en_LR', '🇱🇷'), 'ls': ('en_LS', '🇱🇸'), 'mc': ('fr_MC', '🇲🇨'),
    'mf': ('fr_MF', '🇲🇫'), 'mg': ('fr_MG', '🇲🇬'), 'mh': ('en_MH', '🇲🇭'),
    'mp': ('en_MP', '🇲🇵'), 'mq': ('fr_MQ', '🇲🇶'), 'mr': ('ar_MR', '🇲🇷'),
    'ms': ('en_MS', '🇲🇸'), 'mu': ('en_MU', '🇲🇺'), 'mw': ('en_MW', '🇲🇼'),
    'nc': ('fr_NC', '🇳🇨'), 'ne': ('fr_NE', '🇳🇪'), 'nf': ('en_NF', '🇳🇫'),
    'nr': ('en_NR', '🇳🇷'), 'nu': ('en_NU', '🇳🇺'), 'pf': ('fr_PF', '🇵🇫'),
    'pm': ('fr_PM', '🇵🇲'), 'pn': ('en_PN', '🇵🇳'), 'pw': ('en_PW', '🇵🇼'),
    're': ('fr_RE', '🇷🇪'), 'sc': ('fr_SC', '🇸🇨'), 'sh': ('en_SH', '🇸🇭'),
    'sj': ('no_SJ', '🇸🇯'), 'sl': ('en_SL', '🇸🇱'), 'sm': ('it_SM', '🇸🇲'),
    'so': ('so_SO', '🇸🇴'), 'sr': ('nl_SR', '🇸🇷'), 'ss': ('en_SS', '🇸🇸'),
    'st': ('pt_ST', '🇸🇹'), 'sx': ('nl_SX', '🇸🇽'), 'sz': ('en_SZ', '🇸🇿'),
    'tc': ('en_TC', '🇹🇨'), 'td': ('fr_TD', '🇹🇩'), 'tf': ('fr_TF', '🇹🇫'),
    'tg': ('fr_TG', '🇹🇬'), 'tk': ('en_TK', '🇹🇰'), 'tv': ('en_TV', '🇹🇻'),
    'va': ('it_VA', '🇻🇦'), 'vg': ('en_VG', '🇻🇬'), 'wf': ('fr_WF', '🇼🇫'),
    'yt': ('fr_YT', '🇾🇹'),
    
    # Antarctica and remote territories (using appropriate regional locales)
    'aq': ('en_US', '🇦🇶'), 'bv': ('no_NO', '🇧🇻'), 'hm': ('en_AU', '🇭🇲'),
    'io': ('en_IO', '🇮🇴'), 'um': ('en_UM', '🇺🇲')
}

# Generate automated mapping of country names to country codes
COUNTRY_NAME_TO_CODE = {}

# Add all country codes from pycountry
for country in pycountry.countries:
    code = country.alpha_2.lower()
    if code in LOCALES:
        # Add official name
        COUNTRY_NAME_TO_CODE[country.name.lower()] = code
        
        # Add common name variations
        if hasattr(country, 'common_name'):
            COUNTRY_NAME_TO_CODE[country.common_name.lower()] = code
            
        # Add official name without special characters
        norm_name = unicodedata.normalize('NFKD', country.name.lower())
        norm_name = ''.join([c for c in norm_name if not unicodedata.combining(c)])
        COUNTRY_NAME_TO_CODE[norm_name] = code

# Add manual common name variations and abbreviations
COMMON_VARIATIONS = {
    # Common abbreviations and alternative names
    'usa': 'us', 'america': 'us', 'united states of america': 'us', 
    'uk': 'gb', 'britain': 'gb', 'great britain': 'gb', 'england': 'gb',
    'uae': 'ae', 'emirates': 'ae',
    'russia': 'ru', 'russian federation': 'ru',
    'korea': 'kr', 'south korea': 'kr', 'north korea': 'kp',
    'china': 'cn', 'mainland china': 'cn', 'prc': 'cn',
    'taiwan': 'tw', 'roc': 'tw',
    'holland': 'nl', 'the netherlands': 'nl',
    'czech republic': 'cz', 'czechia': 'cz',
    'palestine': 'ps', 'palestinian territories': 'ps',
    'hong kong': 'hk', 'macau': 'mo', 'macao': 'mo',
    'bosnia': 'ba', 'myanmar': 'mm', 'burma': 'mm',
    'ivory coast': 'ci', 'congo': 'cd', 'drc': 'cd',
    'tanzania': 'tz', 'fiji': 'fj', 'micronesia': 'fm',
    
    # Regional/informal terms
    'scandinavia': 'se', 'nordic': 'no', 'baltics': 'lv',
    'eastern europe': 'ru', 'western europe': 'fr', 'southern europe': 'it',
    'middle east': 'ae', 'gulf': 'sa', 'maghreb': 'ma',
    'caribbean': 'jm', 'west indies': 'bb', 'central america': 'mx',
    'south america': 'br', 'latin america': 'mx', 'central asia': 'kz',
    'southeast asia': 'th', 'south asia': 'in', 'east asia': 'jp',
    'oceania': 'au', 'polynesia': 'pf', 'micronesia': 'fm', 'melanesia': 'fj',
    'africa': 'za', 'west africa': 'ng', 'east africa': 'ke', 'north africa': 'eg'
}
COUNTRY_NAME_TO_CODE.update(COMMON_VARIATIONS)

# Cache storage for API responses (in-memory, will reset on bot restart)
API_CACHE = {}

def get_country_code(country_query: str) -> str:
    """Convert country name or code to a valid country code."""
    country_query = country_query.lower().strip()
    
    # Direct country code match
    if country_query in LOCALES:
        return country_query
    
    # Country name match
    if country_query in COUNTRY_NAME_TO_CODE:
        return COUNTRY_NAME_TO_CODE[country_query]
    
    # Try to find partial matches
    for country_name, code in COUNTRY_NAME_TO_CODE.items():
        if country_query in country_name:
            return code
    
    # Default to US if no match found
    return 'us'

def get_address_format(country_code: str) -> Dict:
    """Get the appropriate address format based on country."""
    # Comprehensive address formats for all regions of the world
    formats = {
        # North American format (US, Canada, etc.)
        'AMERICAS_NORTH': {
            'order': ['street', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'city': '🏙️ <b>City:</b>',
                'state': '🌆 <b>State/Province:</b>',
                'postal_code': '📮 <b>ZIP/Postal Code:</b>'
            }
        },
        
        # Latin American format
        'AMERICAS_CENTRAL': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Avenue:</b>',
                'district': '🏘️ <b>Neighborhood/Colony:</b>',
                'city': '🏙️ <b>City/Municipality:</b>',
                'state': '🌆 <b>State/Department:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district']
        },
        
        # South American format
        'AMERICAS_SOUTH': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Avenue:</b>',
                'district': '🏘️ <b>Neighborhood/District:</b>',
                'city': '🏙️ <b>City/Municipality:</b>',
                'state': '🌆 <b>State/Province:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district']
        },
        
        # Caribbean format
        'AMERICAS_CARIBBEAN': {
            'order': ['street', 'city', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Road:</b>',
                'city': '🏙️ <b>City/Settlement:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['postal_code']
        },
        
        # Western European format
        'EUROPE_WEST': {
            'order': ['street', 'postal_code', 'city', 'state'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Region/County:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['state']
        },
        
        # UK specific format
        'UK': {
            'order': ['street', 'city', 'postal_town', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Road:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'postal_town': '📍 <b>Postal Town:</b>',
                'postal_code': '📮 <b>Postcode:</b>'
            },
            'optional': ['postal_town']
        },
        
        # Northern European format
        'EUROPE_NORTH': {
            'order': ['street', 'postal_code', 'city'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'city': '🏙️ <b>City/Municipality:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            }
        },
        
        # Eastern European format
        'EUROPE_EAST': {
            'order': ['street', 'postal_code', 'city', 'state'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'city': '🏙️ <b>City:</b>',
                'state': '🌆 <b>Oblast/Region/County:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['state']
        },
        
        # Southern European format
        'EUROPE_SOUTH': {
            'order': ['street', 'postal_code', 'city', 'state'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Province/Region:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['state']
        },
        
        # East Asian format (Japan, Korea, etc.)
        'ASIA_EAST': {
            'order': ['postal_code', 'state', 'city', 'district', 'street'],
            'labels': {
                'postal_code': '📮 <b>Postal Code:</b>',
                'state': '🌆 <b>Prefecture/Province:</b>',
                'city': '🏙️ <b>City/District:</b>',
                'district': '🏘️ <b>Ward/Neighborhood:</b>',
                'street': '🏠 <b>Street/Block:</b>'
            },
            'optional': ['district']
        },
        
        # South Asian format (India, etc.)
        'ASIA_SOUTH': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'district': '🏘️ <b>Area/Locality:</b>',
                'city': '🏙️ <b>City:</b>',
                'state': '🌆 <b>State/UT:</b>',
                'postal_code': '📮 <b>PIN Code:</b>'
            },
            'optional': ['district']
        },
        
        # Southeast Asian format
        'ASIA_SOUTHEAST': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'district': '🏘️ <b>Subdistrict/Locality:</b>',
                'city': '🏙️ <b>City/Municipality:</b>',
                'state': '🌆 <b>Province/Region:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district']
        },
        
        # Middle Eastern format
        'ASIA_WEST': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'district': '🏘️ <b>District/Area:</b>',
                'city': '🏙️ <b>City:</b>',
                'state': '🌆 <b>Governorate/Province:</b>',
                'postal_code': '📮 <b>Postal Code/P.O. Box:</b>'
            },
            'optional': ['district', 'postal_code']
        },
        
        # Central Asian format
        'ASIA_CENTRAL': {
            'order': ['street', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'city': '🏙️ <b>City/Settlement:</b>',
                'state': '🌆 <b>Region/Oblast:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            }
        },
        
        # African format (General)
        'AFRICA_GENERAL': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'district': '🏘️ <b>Area/District:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Region/Province:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district', 'postal_code']
        },
        
        # East African format (Kenya, Tanzania, Uganda, etc.)
        'AFRICA_EAST': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Plot:</b>',
                'district': '🏘️ <b>Estate/Area:</b>',
                'city': '🏙️ <b>Town/City:</b>',
                'state': '🌆 <b>County/Region:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district']
        },
        
        # West African format (Nigeria, Ghana, Senegal, etc.)
        'AFRICA_WEST': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/House:</b>',
                'district': '🏘️ <b>Area/Locality:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>State/Region:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['postal_code']
        },
        
        # Southern African format (South Africa, Zimbabwe, Botswana, etc.)
        'AFRICA_SOUTH': {
            'order': ['street', 'suburb', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/House:</b>',
                'suburb': '🏘️ <b>Suburb:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Province:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            }
        },
        
        # Central African format (DR Congo, Cameroon, etc.)
        'AFRICA_CENTRAL': {
            'order': ['street', 'district', 'city', 'state'],
            'labels': {
                'street': '🏠 <b>Street/Avenue:</b>',
                'district': '🏘️ <b>Quarter/District:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Province/Region:</b>'
            },
            'optional': ['district']
        },
        
        # North African format
        'AFRICA_NORTH': {
            'order': ['street', 'district', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Building:</b>',
                'district': '🏘️ <b>District/Quarter:</b>',
                'city': '🏙️ <b>City/Municipality:</b>',
                'state': '🌆 <b>Governorate/Province:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['district']
        },
        
        # South African specific format
        'AFRICA_SOUTH': {
            'order': ['street', 'suburb', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'suburb': '🏘️ <b>Suburb:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>Province:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['suburb']
        },
        
        # Oceania format (Australia, NZ, etc.)
        'OCEANIA_AUSTRALIA': {
            'order': ['street', 'suburb', 'city', 'state', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street:</b>',
                'suburb': '🏘️ <b>Suburb:</b>',
                'city': '🏙️ <b>City/Town:</b>',
                'state': '🌆 <b>State/Territory:</b>',
                'postal_code': '📮 <b>Postcode:</b>'
            },
            'optional': ['suburb', 'city']
        },
        
        # Pacific Islands format
        'OCEANIA_PACIFIC': {
            'order': ['street', 'city', 'postal_code'],
            'labels': {
                'street': '🏠 <b>Street/Village:</b>',
                'city': '🏙️ <b>City/Island:</b>',
                'postal_code': '📮 <b>Postal Code:</b>'
            },
            'optional': ['postal_code']
        }
    }
    
    # Country-specific overrides
    country_specific = {
        'uk': 'UK', 'gb': 'UK',  # United Kingdom
        'jp': 'ASIA_EAST',       # Japan
        'kr': 'ASIA_EAST',       # South Korea
        'cn': 'ASIA_EAST',       # China
        'in': 'ASIA_SOUTH',      # India
        'au': 'OCEANIA_AUSTRALIA', # Australia
        'nz': 'OCEANIA_AUSTRALIA', # New Zealand
        'za': 'AFRICA_SOUTH',    # South Africa
        
        # Small island nations and territories
        'pg': 'OCEANIA_PACIFIC', 'fj': 'OCEANIA_PACIFIC', 'sb': 'OCEANIA_PACIFIC',
        'vu': 'OCEANIA_PACIFIC', 'fm': 'OCEANIA_PACIFIC', 'ki': 'OCEANIA_PACIFIC',
        'ws': 'OCEANIA_PACIFIC', 'to': 'OCEANIA_PACIFIC', 'tv': 'OCEANIA_PACIFIC',
        'pf': 'OCEANIA_PACIFIC', 'ck': 'OCEANIA_PACIFIC',
        
        # Countries with unique addressing
        'nl': 'EUROPE_WEST',     # Netherlands
        'sg': 'ASIA_SOUTHEAST',  # Singapore
        'hk': 'ASIA_EAST',       # Hong Kong
        'mo': 'ASIA_EAST',       # Macau
    }
    
    # First check for country-specific format
    if country_code in country_specific:
        format_key = country_specific[country_code]
    # Then check which region the country belongs to
    elif country_code in COUNTRY_TO_REGION:
        region = COUNTRY_TO_REGION[country_code]
        # Map region to format
        if region in formats:
            format_key = region
        elif region.startswith('AFRICA_'):
            format_key = 'AFRICA_GENERAL'
        elif region.startswith('OCEANIA_') and region != 'OCEANIA_AUSTRALIA':
            format_key = 'OCEANIA_PACIFIC'
        else:
            format_key = 'EUROPE_WEST'  # Default format
    else:
        format_key = 'EUROPE_WEST'  # Default format
    
    return formats[format_key]

# Functions to generate regionally appropriate names
def get_african_name(gender: str, country_code: str, preselected_ethnicity=None, return_ethnicity=False) -> Union[str, Tuple[str, str]]:
    """
    Generate culturally appropriate African names based on country and region.
    
    Args:
        gender: Male or female identifier
        country_code: Two-letter country code
        preselected_ethnicity: Optional pre-selected ethnicity for consistent naming
        return_ethnicity: If True, returns tuple of (name, ethnicity)
        
    Returns:
        Either the name string or tuple of (name, ethnicity) if return_ethnicity=True
    """
    # Initialize variables to avoid UnboundLocalError
    selected_ethnicity = 'generic'
    first_name = None
    # Common East African names (Kenya, Tanzania, Uganda)
    east_african_male_names = [
        "Adamu", "Baraka", "Chege", "David", "Emmanuel", "Francis", "George", "Hakim",
        "Ibrahim", "John", "Kamau", "Lemayian", "Moses", "Mutai", "Njoroge", "Ochieng",
        "Peter", "Ruto", "Samuel", "Thomas", "Wanjala", "Wekesa", "Kipchoge", "Kimutai",
        "Kipruto", "Mwangi", "Waithaka", "Gathoga", "Gacheru", "Karanja", "Kinuthia"
    ]
    east_african_female_names = [
        "Akello", "Atieno", "Bahati", "Charity", "Dada", "Elizabeth", "Faith", "Grace",
        "Halima", "Imani", "Joyce", "Kadija", "Latifa", "Mary", "Naomi", "Nyambura",
        "Pendo", "Ruth", "Sarah", "Tabitha", "Wangari", "Zawadi", "Njeri", "Wambui",
        "Nyokabi", "Wanjiku", "Akinyi", "Awino", "Auma", "Adhiambo", "Moraa", "Kerubo"
    ]
    
    # West African names (Nigeria, Ghana, Senegal, etc.)
    west_african_male_names = {
        # Nigeria - by ethnic group
        'ng_yoruba': ["Adebayo", "Oluwaseun", "Olumide", "Adewale", "Babatunde", "Temitope", 
                      "Olamide", "Oluwafemi", "Gbenga", "Kayode", "Segun", "Yinka"],
        'ng_igbo': ["Chukwudi", "Emeka", "Chisom", "Ikenna", "Oluchi", "Chinua", 
                   "Ebuka", "Nnamdi", "Uchenna", "Chinedu", "Obinna", "Chidera"],
        'ng_hausa': ["Ibrahim", "Musa", "Yusuf", "Abdullahi", "Aliyu", "Hassan", 
                    "Umar", "Abubakar", "Suleiman", "Ismail", "Harun", "Bashir"],
        # Ghana
        'gh': ["Kofi", "Kwame", "Kwesi", "Ato", "Kojo", "Kwabena", 
              "Akwasi", "Yaw", "Fiifi", "Mensah", "Annan", "Boateng"],
        # Senegal
        'sn': ["Abdou", "Mamadou", "Ousmane", "Ibrahima", "Cheikh", "Moussa", 
              "Amadou", "Seydou", "Modou", "Idrissa", "Babacar", "Demba"],
        # Côte d'Ivoire
        'ci': ["Kouame", "Koffi", "Kouassi", "Yao", "Kouadio", "Konan", 
              "Adama", "Lassana", "Bakary", "Souleymane", "Sekou", "Ismael"],
        # Generic West African
        'generic': ["Abayomi", "Folami", "Jawara", "Lamidi", "Oluwaseun", "Tunde", 
                   "Zuberi", "Kweku", "Addo", "Kofi", "Kwame", "Mensah"]
    }
    
    west_african_female_names = {
        # Nigeria - by ethnic group
        'ng_yoruba': ["Abimbola", "Adenike", "Oluwaseun", "Yewande", "Folake", "Temitope", 
                     "Olufunke", "Abiodun", "Ifeoma", "Adebisi", "Jadesola", "Adunni"],
        'ng_igbo': ["Chioma", "Adaeze", "Ngozi", "Nneka", "Oluchi", "Chinelo", 
                   "Amarachi", "Ihuoma", "Obioma", "Chidinma", "Uchenna", "Chizoba"],
        'ng_hausa': ["Amina", "Fatima", "Zainab", "Aisha", "Hauwa", "Maryam", 
                    "Halima", "Khadijah", "Nafisa", "Rahama", "Habiba", "Jamila"],
        # Ghana
        'gh': ["Ama", "Akua", "Abena", "Akosua", "Adwoa", "Afia", 
              "Adjoa", "Yaa", "Afua", "Esi", "Efua", "Aba"],
        # Senegal
        'sn': ["Awa", "Aminata", "Fatou", "Aida", "Astou", "Maimouna", 
              "Coumba", "Khady", "Ndeye", "Sokhna", "Mariama", "Dieynaba"],
        # Côte d'Ivoire
        'ci': ["Adjoua", "Amenan", "Affoue", "Ahou", "Akissi", "Aya", 
              "Fanta", "Kadiatou", "Mariam", "Rokia", "Fatoumata", "Aminata"],
        # Generic West African
        'generic': ["Abimbola", "Adenike", "Bisi", "Damilola", "Folami", "Gbemisola",
                   "Ife", "Kemi", "Monifa", "Precious", "Temi", "Yejide"]
    }
    
    # North African names (Morocco, Egypt, Algeria, etc.)
    north_african_male_names = {
        # Arabic/Muslim names common in North Africa
        'ma': ["Mohammed", "Ahmed", "Youssef", "Mehdi", "Hamza", "Omar", 
              "Khalid", "Samir", "Jamal", "Karim", "Tarik", "Bilal"],
        'eg': ["Mohamed", "Ahmed", "Mahmoud", "Ali", "Hassan", "Hussein", 
              "Mostafa", "Omar", "Khaled", "Ibrahim", "Karim", "Youssef"],
        'dz': ["Mohammed", "Ahmed", "Ali", "Hamza", "Younes", "Amine", 
              "Ayoub", "Bilal", "Karim", "Mehdi", "Sofiane", "Youcef"],
        # Generic North African
        'generic': ["Farid", "Malik", "Tariq", "Jamal", "Nasser", "Rachid", 
                   "Amir", "Samir", "Hakim", "Akram", "Khalil", "Zakaria"]
    }
    
    north_african_female_names = {
        # Arabic/Muslim names common in North Africa
        'ma': ["Fatima", "Aisha", "Amina", "Leila", "Nadia", "Samira", 
              "Karima", "Layla", "Khadija", "Malika", "Naima", "Zahra"],
        'eg': ["Fatma", "Amira", "Laila", "Hoda", "Aisha", "Dina", 
              "Mariam", "Nour", "Rana", "Sara", "Yasmin", "Zeinab"],
        'dz': ["Amina", "Karima", "Leila", "Naima", "Salima", "Yamina", 
              "Fatima", "Khadija", "Meryem", "Nadia", "Sabrina", "Samira"],
        # Generic North African
        'generic': ["Laila", "Samira", "Jamila", "Nadia", "Farida", "Amina", 
                   "Malika", "Karima", "Dalila", "Fatima", "Saida", "Zohra"]
    }
    
    # Southern African names (South Africa, Zimbabwe, Zambia, etc.)
    southern_african_male_names = {
        # South Africa - by ethnicity
        'za_zulu': ["Sipho", "Thabo", "Themba", "Mandla", "Nkosi", "Bongani", 
                   "Siyabonga", "Xolani", "Nkosinathi", "Sibusiso", "Vusi", "Zolani"],
        'za_xhosa': ["Luthando", "Lubabalo", "Anele", "Siyabonga", "Mthobeli", "Andile", 
                    "Sisanda", "Bathandwa", "Thembani", "Khanyisa", "Ayanda", "Onke"],
        'za_sotho': ["Thabiso", "Thabo", "Tumelo", "Kagiso", "Tebogo", "Lesego", 
                    "Tshepo", "Mpho", "Karabo", "Katlego", "Lerato", "Kamogelo"],
        # Zimbabwe
        'zw': ["Tafadzwa", "Tatenda", "Tendai", "Tapera", "Tinashe", "Tavonga", 
              "Tanaka", "Takudzwa", "Tongai", "Themba", "Kudakwashe", "Tapiwa"],
        # Zambia
        'zm': ["Chipo", "Chilufya", "Daliso", "Kondwani", "Mulenga", "Mutale", 
              "Mwamba", "Nkonde", "Sitali", "Thokozani", "Wezi", "Zakeyo"],
        # Generic Southern African
        'generic': ["Blessing", "Gift", "Justice", "Innocent", "Prince", "Fortune", 
                   "Dumisani", "Happiness", "Emmanuel", "Welcome", "Prosper", "Wisdom"]
    }
    
    southern_african_female_names = {
        # South Africa - by ethnicity
        'za_zulu': ["Thandi", "Nomvula", "Zanele", "Ntombi", "Nonhlanhla", "Siphokazi", 
                   "Nobuhle", "Zandile", "Nolwazi", "Sithembile", "Nomusa", "Bongiwe"],
        'za_xhosa': ["Nomvula", "Nosipho", "Nontle", "Nwabisa", "Nomfundo", "Nosizwe", 
                    "Nolitha", "Noxolo", "Nompumelelo", "Nolusindiso", "Nonceba", "Nontando"],
        'za_sotho': ["Dikeledi", "Lerato", "Lesedi", "Palesa", "Refilwe", "Thabisile", 
                    "Mmathabo", "Puleng", "Kgomotso", "Bontle", "Basetsana", "Mpho"],
        # Zimbabwe
        'zw': ["Chiedza", "Nyasha", "Ruvarashe", "Rutendo", "Shamiso", "Tadiwanashe", 
              "Tariro", "Tendai", "Tsitsi", "Vimbai", "Yeukai", "Rudo"],
        # Zambia
        'zm': ["Chansa", "Chikondi", "Chikwado", "Chimwemwe", "Chisomo", "Mutinta", 
              "Nakamba", "Natasha", "Thandi", "Thandiwe", "Thokozile", "Zara"],
        # Generic Southern African
        'generic': ["Blessing", "Faith", "Hope", "Joy", "Mercy", "Patience", 
                   "Queen", "Precious", "Grace", "Beauty", "Harmony", "Peace"]
    }
    
    # East African names by country (Kenya, Tanzania, Uganda, etc.)
    east_african_country_male_names = {
        # Kenya - by ethnicity
        'ke_kikuyu': ["Kamau", "Njoroge", "Mwangi", "Waweru", "Karanja", "Kimani", 
                     "Kiarie", "Njenga", "Githinji", "Mugo", "Wambugu", "Gathogo"],
        'ke_luo': ["Ochieng", "Omondi", "Otieno", "Owino", "Odhiambo", "Oduor", 
                  "Okello", "Ojwang", "Ojuka", "Ouko", "Okoth", "Onyango"],
        'ke_kalenjin': ["Kipchoge", "Kiprop", "Kipruto", "Kiptoo", "Kiplagat", "Kiplimo", 
                       "Koech", "Kemboi", "Kibet", "Kipketer", "Kipchirchir", "Kipyegon"],
        # Tanzania
        'tz': ["Baraka", "Emmanuel", "Isaya", "Joseph", "Nuru", "Rajabu", 
              "Salehe", "Tumaini", "Zawadi", "Juma", "Said", "Hamisi"],
        # Uganda
        'ug': ["Akiki", "Mwebaze", "Kato", "Wasswa", "Mutumba", "Muwonge", 
              "Mukasa", "Ssekabira", "Lutalo", "Sserwadda", "Tusiime", "Ouma"],
        # Ethiopia - more comprehensive with ethnic diversity
        'et_amhara': ["Abebe", "Bekele", "Demeke", "Endalkachew", "Fasil", "Getachew", 
                    "Haile", "Ketema", "Melaku", "Negasi", "Tadesse", "Zerihun", 
                    "Teshome", "Berhanu", "Girma", "Sisay", "Tesfaye", "Mulugeta", 
                    "Dereje", "Amanuel", "Alemu", "Yohannes", "Tsegaye", "Mengistu"],
        'et_oromo': ["Gemechu", "Lemessa", "Tolasa", "Dagnachew", "Bekele", "Kumsa", 
                    "Teshome", "Tesfaye", "Negash", "Deressa", "Wakjira", "Abera", 
                    "Tadesse", "Geleta", "Ayana", "Berhanu", "Degefa", "Mulatu"],
        'et_tigray': ["Hagos", "Berhe", "Gebremichael", "Hailu", "Tesfay", "Gebreselassie", 
                     "Gebrehiwot", "Tekle", "Araya", "Girmay", "Abraha", "Alem"],
        'et_gurage': ["Mohammed", "Ahmed", "Ibrahim", "Jemal", "Awol", "Abdi", 
                     "Omar", "Hussein", "Abdulkadir", "Kemal", "Abubeker", "Adem"],
        'et': ["Abebe", "Bekele", "Demeke", "Endalkachew", "Fasil", "Getachew", 
              "Haile", "Ketema", "Melaku", "Negasi", "Tadesse", "Zerihun",
              "Solomon", "Daniel", "Dawit", "Samuel", "Michael", "Henok",
              "Eyasu", "Biniam", "Natnael", "Yared", "Bereket", "Amanuel"],
        # Rwanda/Burundi
        'rw_bi': ["Bizimana", "Hakizimana", "Mugisha", "Ndayishimiye", "Niyonzima", "Nsengiyumva", 
                 "Nshimiyimana", "Habimana", "Twagiramungu", "Uwimana", "Nkurunziza", "Nduwimana"],
        # Generic East African
        'generic': ["Baraka", "Emmanuel", "Francis", "Hakim", "Ibrahim", "John", 
                   "Moses", "Samuel", "Thomas", "William", "Daniel", "Joseph"]
    }
    
    east_african_country_female_names = {
        # Kenya - by ethnicity
        'ke_kikuyu': ["Wanjiku", "Nyambura", "Wangari", "Njeri", "Wanjiru", "Waithera", 
                     "Wambui", "Nyokabi", "Muthoni", "Wairimu", "Njoki", "Gathoni"],
        'ke_luo': ["Achieng", "Adhiambo", "Akoth", "Anyango", "Atieno", "Awino", 
                  "Awuor", "Auma", "Akinyi", "Apiyo", "Akeyo", "Adongo"],
        'ke_kalenjin': ["Chebet", "Chepkoech", "Chepkurui", "Cherono", "Cheptoo", "Jelagat", 
                       "Jemutai", "Jepkosgei", "Jeptoo", "Jeruto", "Kigen", "Kiplagat"],
        # Tanzania
        'tz': ["Bahati", "Furaha", "Grace", "Halima", "Imani", "Joyce", 
              "Neema", "Rehema", "Subira", "Tumaini", "Upendo", "Zawadi"],
        # Uganda
        'ug': ["Akoragye", "Atuhaire", "Babirye", "Kagoya", "Namugwanya", "Namulindwa", 
              "Nankya", "Nabirye", "Namazzi", "Nakimuli", "Nakato", "Nambi"],
        # Ethiopia - more comprehensive with ethnic diversity
        'et_amhara': ["Abeba", "Bethlehem", "Desta", "Emnet", "Feven", "Genet", 
                     "Hiwot", "Kidist", "Meron", "Rahel", "Seble", "Yeshi",
                     "Tigist", "Meskerem", "Tizita", "Tsehay", "Yordanos", "Nigist",
                     "Zinash", "Hirut", "Almaz", "Emebet", "Netsanet", "Mimi"],
        'et_oromo': ["Chaltu", "Aberash", "Aregash", "Dinkinesh", "Etenesh", "Gadise", 
                    "Hawi", "Lelise", "Makeda", "Obse", "Wubet", "Zema",
                    "Taju", "Saba", "Biftu", "Bontu", "Ebise", "Fana"],
        'et_tigray': ["Selam", "Sara", "Wegahta", "Mehret", "Nitsuh", "Axum", 
                     "Liya", "Nebiat", "Eden", "Semhal", "Fana", "Solyana"],
        'et_gurage': ["Amina", "Fatima", "Mariam", "Zainab", "Aisha", "Khadija", 
                     "Saada", "Raiyan", "Safiya", "Rokia", "Leila", "Naeema"],
        'et': ["Abeba", "Bethlehem", "Desta", "Emnet", "Feven", "Genet", 
              "Hiwot", "Kidist", "Meron", "Rahel", "Seble", "Yeshi",
              "Eden", "Selam", "Sara", "Helen", "Martha", "Tigist",
              "Meseret", "Rediet", "Mahlet", "Emebet", "Jerusalem", "Lydia"],
        # Rwanda/Burundi
        'rw_bi': ["Agathe", "Clementine", "Francoise", "Germaine", "Immaculee", "Josephine", 
                 "Marie", "Monique", "Odette", "Pelagie", "Therese", "Vestine"],
        # Generic East African
        'generic': ["Akello", "Bahati", "Charity", "Elizabeth", "Faith", "Grace", 
                   "Imani", "Joyce", "Mary", "Naomi", "Ruth", "Sarah"]
    }
    
    # Central African names (DRC, Cameroon, etc.)
    central_african_male_names = {
        # DRC
        'cd': ["Bosco", "Etienne", "Jean", "Joseph", "Kabila", "Kanda", 
              "Lumumba", "Mobutu", "Mutombo", "Patrice", "Pierre", "Tshisekedi"],
        # Cameroon
        'cm': ["Assou", "Biya", "Cyrille", "Emmanuel", "Kotto", "Mbarga", 
              "Mbia", "Ndong", "Nkodo", "Olinga", "Simo", "Tobie"],
        # Generic Central African
        'generic': ["Antoine", "Bernard", "Christian", "Daniel", "Emmanuel", "Francis", 
                   "Gabriel", "Henri", "Jacques", "Laurent", "Michel", "Paul"]
    }
    
    central_african_female_names = {
        # DRC
        'cd': ["Albertine", "Antoinette", "Beatrice", "Charlotte", "Denise", "Emilie", 
              "Francine", "Gertrude", "Henriette", "Jeanette", "Josephine", "Marie"],
        # Cameroon
        'cm': ["Agathe", "Aissatou", "Anastasie", "Angeline", "Carine", "Charlotte", 
              "Emilienne", "Esther", "Jacqueline", "Josephine", "Marie", "Solange"],
        # Generic Central African
        'generic': ["Adele", "Agnes", "Bernadette", "Catherine", "Cecile", "Colette", 
                   "Delphine", "Diane", "Florence", "Louise", "Marguerite", "Sophie"]
    }
    
    # Determine which name set to use based on country code and region
    region = None
    if country_code in COUNTRY_TO_REGION:
        region = COUNTRY_TO_REGION[country_code]
    
    is_male = gender.lower().startswith('m')
    
    # East Africa
    if country_code in ['ke', 'tz', 'ug', 'et', 'rw', 'bi', 'ss', 'so', 'dj', 'er']:
        if country_code == 'ke':
            # Kenya - select from different ethnic groups
            ethnicities = ['ke_kikuyu', 'ke_luo', 'ke_kalenjin']
            
            # Use preselected ethnicity if valid, otherwise random
            if preselected_ethnicity in ethnicities:
                ethnicity = preselected_ethnicity
            else:
                ethnicity = random.choice(ethnicities)
                
            selected_ethnicity = ethnicity
                
            if is_male:
                first_name = random.choice(east_african_country_male_names[ethnicity])
            else:
                first_name = random.choice(east_african_country_female_names[ethnicity])
                
        elif country_code == 'et':
            # Ethiopia - select from different ethnic groups with appropriate distribution
            # Distribution roughly based on demographics: 
            # Amhara (~27%), Oromo (~34%), Tigray (~6%), other groups
            ethnicities = ['et_amhara', 'et_oromo', 'et_tigray', 'et_gurage', 'et']
            
            # Use preselected ethnicity if valid, otherwise weighted random
            if preselected_ethnicity in ethnicities:
                ethnicity = preselected_ethnicity
            else:
                weights = [27, 34, 6, 8, 25]  # Approximate population distribution
                ethnicity = random.choices(ethnicities, weights=weights, k=1)[0]
            
            selected_ethnicity = ethnicity
            
            if is_male:
                first_name = random.choice(east_african_country_male_names[ethnicity])
            else:
                first_name = random.choice(east_african_country_female_names[ethnicity])
        elif country_code in east_african_country_male_names:
            # Specific country in East Africa
            selected_ethnicity = country_code
            
            if is_male:
                first_name = random.choice(east_african_country_male_names[country_code])
            else:
                first_name = random.choice(east_african_country_female_names[country_code])
        elif country_code in ['rw', 'bi']:
            # Rwanda/Burundi share similar naming patterns
            selected_ethnicity = 'rw_bi'
            
            if is_male:
                first_name = random.choice(east_african_country_male_names['rw_bi'])
            else:
                first_name = random.choice(east_african_country_female_names['rw_bi'])
        else:
            # Generic East African
            selected_ethnicity = 'east_africa_generic'
            
            if is_male:
                first_name = random.choice(east_african_country_male_names['generic'])
            else:
                first_name = random.choice(east_african_country_female_names['generic'])
    
    # West Africa
    elif country_code in ['ng', 'gh', 'sn', 'ci', 'lr', 'sl', 'gm', 'tg', 'bj', 'ml', 'ne', 'bf', 'gn', 'gw']:
        if country_code == 'ng':
            # Nigeria - select from different ethnic groups
            ethnicities = ['ng_yoruba', 'ng_igbo', 'ng_hausa']
            ethnicity = random.choice(ethnicities)
            if is_male:
                first_name = random.choice(west_african_male_names[ethnicity])
            else:
                first_name = random.choice(west_african_female_names[ethnicity])
        elif country_code in west_african_male_names:
            # Specific country in West Africa
            if is_male:
                first_name = random.choice(west_african_male_names[country_code])
            else:
                first_name = random.choice(west_african_female_names[country_code])
        else:
            # Generic West African
            if is_male:
                first_name = random.choice(west_african_male_names['generic'])
            else:
                first_name = random.choice(west_african_female_names['generic'])
    
    # North Africa
    elif country_code in ['ma', 'dz', 'tn', 'ly', 'eg', 'sd', 'mr', 'eh']:
        if country_code in north_african_male_names:
            # Specific country in North Africa
            if is_male:
                first_name = random.choice(north_african_male_names[country_code])
            else:
                first_name = random.choice(north_african_female_names[country_code])
        else:
            # Generic North African
            if is_male:
                first_name = random.choice(north_african_male_names['generic'])
            else:
                first_name = random.choice(north_african_female_names['generic'])
    
    # Southern Africa
    elif country_code in ['za', 'zw', 'zm', 'na', 'bw', 'ls', 'sz', 'mz', 'mw', 'ao']:
        if country_code == 'za':
            # South Africa - select from different ethnic groups
            ethnicities = ['za_zulu', 'za_xhosa', 'za_sotho']
            ethnicity = random.choice(ethnicities)
            if is_male:
                first_name = random.choice(southern_african_male_names[ethnicity])
            else:
                first_name = random.choice(southern_african_female_names[ethnicity])
        elif country_code in southern_african_male_names:
            # Specific country in Southern Africa
            if is_male:
                first_name = random.choice(southern_african_male_names[country_code])
            else:
                first_name = random.choice(southern_african_female_names[country_code])
        else:
            # Generic Southern African
            if is_male:
                first_name = random.choice(southern_african_male_names['generic'])
            else:
                first_name = random.choice(southern_african_female_names['generic'])
    
    # Central Africa
    elif country_code in ['cd', 'cg', 'cm', 'ga', 'gq', 'cf', 'st', 'td']:
        if country_code in central_african_male_names:
            # Specific country in Central Africa
            if is_male:
                first_name = random.choice(central_african_male_names[country_code])
            else:
                first_name = random.choice(central_african_female_names[country_code])
        else:
            # Generic Central African
            if is_male:
                first_name = random.choice(central_african_male_names['generic'])
            else:
                first_name = random.choice(central_african_female_names['generic'])
    
    # Default for any other African country
    else:
        # Use general African names based on region if available
        if region and region.startswith('AFRICA_'):
            sub_region = region.split('_')[1].lower()
            if sub_region == 'east':
                if is_male:
                    first_name = random.choice(east_african_country_male_names['generic'])
                else:
                    first_name = random.choice(east_african_country_female_names['generic'])
            elif sub_region == 'west':
                if is_male:
                    first_name = random.choice(west_african_male_names['generic'])
                else:
                    first_name = random.choice(west_african_female_names['generic'])
            elif sub_region == 'north':
                if is_male:
                    first_name = random.choice(north_african_male_names['generic'])
                else:
                    first_name = random.choice(north_african_female_names['generic'])
            elif sub_region == 'south':
                if is_male:
                    first_name = random.choice(southern_african_male_names['generic'])
                else:
                    first_name = random.choice(southern_african_female_names['generic'])
            elif sub_region == 'central':
                if is_male:
                    first_name = random.choice(central_african_male_names['generic'])
                else:
                    first_name = random.choice(central_african_female_names['generic'])
            else:
                # Fallback to generic African names
                if is_male:
                    first_name = random.choice(east_african_male_names)
                else:
                    first_name = random.choice(east_african_female_names)
        else:
            # Fallback to generic African names
            selected_ethnicity = 'africa_generic'
            
            if is_male:
                first_name = random.choice(east_african_male_names)
            else:
                first_name = random.choice(east_african_female_names)
    
    # Return either just the name or a tuple with ethnicity info based on return_ethnicity parameter
    if return_ethnicity:
        return first_name, selected_ethnicity
    else:
        return first_name

async def get_random_info_from_api(country_code: str) -> Optional[Dict]:
    """
    Try to get additional random user info from an API.
    
    Note: This function has been disabled in favor of our own comprehensive
    country-specific data generation system to ensure consistency across all fields.
    """
    # Disable external API to ensure consistent data generation
    return None
    
    # Original code commented out for reference
    """
    try:
        # Check cache first
        cache_key = f"randomuser_{country_code}"
        if cache_key in API_CACHE:
            cache_entry = API_CACHE[cache_key]
            # Use cache if it's less than 6 hours old
            if datetime.now() - cache_entry["timestamp"] < timedelta(hours=6):
                # Return a random entry from the cached batch
                return random.choice(cache_entry["data"])
                
        # RandomUser API supports a limited set of nationalities
        supported_nat = {
            'au': 'au', 'br': 'br', 'ca': 'ca', 'ch': 'ch', 'de': 'de', 
            'dk': 'dk', 'es': 'es', 'fi': 'fi', 'fr': 'fr', 'gb': 'gb', 
            'uk': 'gb', 'ie': 'ie', 'in': 'in', 'ir': 'ir', 'mx': 'mx', 
            'nl': 'nl', 'no': 'no', 'nz': 'nz', 'rs': 'rs', 'tr': 'tr', 
            'ua': 'ua', 'us': 'us'
        }
        
        # If country is supported, use it; otherwise use a regional fallback
        nat = supported_nat.get(country_code)
        if not nat:
            # Try a region-based fallback
            region_map = {
                # European countries fall back to GB
                'it': 'gb', 'pl': 'gb', 'se': 'gb', 'cz': 'gb', 'hu': 'gb',
                # Asian countries fall back to IN
                'jp': 'in', 'cn': 'in', 'kr': 'in', 'th': 'in', 'vn': 'in',
                # Middle Eastern countries fall back to IR
                'sa': 'ir', 'ae': 'ir', 'il': 'ir',
                # Default to US for others
            }
            nat = region_map.get(country_code, 'us')
        
        async with httpx.AsyncClient() as session:
            response = await session.get(f"https://randomuser.me/api/?nat={nat}&results=10")
            if response.status_code == 200:
                data = response.json()
                
                # Cache the results
                API_CACHE[cache_key] = {
                    "timestamp": datetime.now(),
                    "data": data['results']
                }
                
                return data['results'][0]
            return None
    except Exception:
        return None
    """

def format_phone_number(phone: str, country_code: str, region: str = None) -> str:
    """
    Format phone number based on country with region-specific patterns.
    
    Args:
        phone: The phone number to format
        country_code: Two-letter country code
        region: Optional region/state/province within the country for region-specific area codes
    """
    
    # Country-region specific area codes 
    # This is a comprehensive dictionary that maps countries to their internal regions and area codes
    # This allows for globally consistent phone number generation with regional specificity
    REGION_AREA_CODES = {
        # Ethiopia
        'et': {
            'Addis Ababa': '11',
            'Dire Dawa': '25',
            'Amhara': '33',
            'Oromia': '22',
            'Tigray': '34',
            'SNNPR': '46',
            'Sidama': '47',
            'Somali': '42',
            'Afar': '33',
            'Gambela': '45',
            'Benishangul-Gumuz': '57',
            'Harari': '25',
        },
        
        # Kenya
        'ke': {
            'Nairobi': '020',
            'Mombasa': '041',
            'Kisumu': '057',
            'Nakuru': '051',
            'Eldoret': '053',
            'Thika': '067',
            'Kiambu': '066',
            'Machakos': '044',
            'Muranga': '060',
            'Nyeri': '061',
            'Garissa': '046',
            'Kitale': '054',
            'Kericho': '052',
            'Kakamega': '056',
            'Meru': '064',
            'Naivasha': '050',
            'Malindi': '042',
            'Lamu': '042',
            'Isiolo': '064',
            'Voi': '043',
        },
        
        # Nigeria
        'ng': {
            'Lagos': '01',
            'Abuja': '09',
            'Kano': '064',
            'Port Harcourt': '084',
            'Kaduna': '062',
            'Ibadan': '02',
            'Benin City': '052',
            'Enugu': '042',
            'Jos': '073',
            'Calabar': '087',
        },
        
        # South Africa
        'za': {
            'Cape Town': '021',
            'Johannesburg': '011',
            'Pretoria': '012',
            'Durban': '031',
            'Port Elizabeth': '041',
            'Bloemfontein': '051',
            'East London': '043',
            'Kimberley': '053',
            'Pietermaritzburg': '033',
            'Polokwane': '015',
        },
        
        # Ghana
        'gh': {
            'Accra': '030',
            'Kumasi': '032',
            'Sekondi-Takoradi': '031',
            'Tamale': '037',
            'Cape Coast': '033',
            'Sunyani': '035',
        },
        
        # United Kingdom
        'gb': {
            'London': '020',
            'Birmingham': '0121',
            'Manchester': '0161',
            'Glasgow': '0141',
            'Edinburgh': '0131',
            'Liverpool': '0151',
            'Leeds': '0113',
            'Sheffield': '0114',
            'Bristol': '0117',
            'Cardiff': '029',
            'Belfast': '028',
            'Newcastle': '0191',
            'Nottingham': '0115',
        },
        
        # Germany
        'de': {
            'Berlin': '030',
            'Hamburg': '040',
            'Munich': '089',
            'Cologne': '0221',
            'Frankfurt': '069',
            'Stuttgart': '0711',
            'Düsseldorf': '0211',
            'Dortmund': '0231',
            'Essen': '0201',
            'Leipzig': '0341',
            'Bremen': '0421',
            'Dresden': '0351',
        },
        
        # France
        'fr': {
            'Paris': '01',
            'Marseille': '04',
            'Lyon': '04',
            'Toulouse': '05',
            'Nice': '04',
            'Nantes': '02',
            'Strasbourg': '03',
            'Montpellier': '04',
            'Bordeaux': '05',
            'Lille': '03',
            'Rennes': '02',
            'Reims': '03',
        },
        
        # Brazil
        'br': {
            'São Paulo': '11',
            'Rio de Janeiro': '21',
            'Brasília': '61',
            'Salvador': '71',
            'Fortaleza': '85',
            'Belo Horizonte': '31',
            'Manaus': '92',
            'Curitiba': '41',
            'Recife': '81',
            'Porto Alegre': '51',
            'Belém': '91',
            'Goiânia': '62',
        },
        
        # India
        'in': {
            'Mumbai': '022',
            'Delhi': '011',
            'Bangalore': '080',
            'Hyderabad': '040',
            'Chennai': '044',
            'Kolkata': '033',
            'Ahmedabad': '079',
            'Pune': '020',
            'Jaipur': '0141',
            'Lucknow': '0522',
            'Kanpur': '0512',
            'Nagpur': '0712',
        },
        
        # Add more countries and their regional area codes as needed
    }
    # Dictionary of country calling codes
    CALLING_CODES = {
        # North America
        'us': '1', 'ca': '1', 'mx': '52',
        
        # Europe
        'uk': '44', 'gb': '44', 'fr': '33', 'de': '49', 'it': '39', 'es': '34',
        'pt': '351', 'nl': '31', 'be': '32', 'ch': '41', 'at': '43', 'se': '46',
        'no': '47', 'dk': '45', 'fi': '358', 'pl': '48', 'ru': '7', 'ua': '380',
        'cz': '420', 'hu': '36', 'ro': '40', 'bg': '359', 'gr': '30', 'tr': '90',
        'ie': '353', 'hr': '385', 'rs': '381', 'ba': '387', 'sk': '421',
        'si': '386', 'al': '355', 'mk': '389', 'by': '375', 'ee': '372',
        'lv': '371', 'lt': '370', 'lu': '352', 'mt': '356', 'is': '354',
        
        # Asia
        'cn': '86', 'jp': '81', 'kr': '82', 'kp': '850', 'in': '91', 'pk': '92',
        'bd': '880', 'sg': '65', 'my': '60', 'id': '62', 'th': '66', 'vn': '84',
        'ph': '63', 'mm': '95', 'np': '977', 'lk': '94', 'tw': '886', 'hk': '852',
        'mo': '853', 'kh': '855', 'la': '856', 'bn': '673', 'mv': '960', 
        
        # Middle East
        'il': '972', 'sa': '966', 'ae': '971', 'qa': '974', 'kw': '965', 'bh': '973',
        'om': '968', 'jo': '962', 'lb': '961', 'sy': '963', 'ir': '98', 'iq': '964',
        'ye': '967', 'ps': '970', 'tr': '90', 'cy': '357', 'af': '93', 'am': '374',
        'az': '994', 'ge': '995',
        
        # Africa
        'za': '27', 'ng': '234', 'eg': '20', 'ma': '212', 'dz': '213', 'tn': '216',
        'ke': '254', 'gh': '233', 'tz': '255', 'ug': '256', 'et': '251', 'ci': '225',
        'sn': '221', 'cm': '237', 'cg': '242', 'cd': '243', 'zw': '263', 'na': '264',
        'ao': '244', 'mz': '258', 'zw': '260', 'bw': '267', 'rw': '250', 'bi': '257',
        'ly': '218', 'sd': '249', 'so': '252', 'dj': '253', 'mr': '222', 'ml': '223',
        'bf': '226', 'ne': '227', 'tg': '228', 'bj': '229', 'gm': '220', 'gn': '224',
        
        # Oceania
        'au': '61', 'nz': '64', 'pg': '675', 'fj': '679', 'sb': '677', 'vu': '678',
        'fm': '691', 'ki': '686', 'mh': '692', 'pw': '680', 'ws': '685', 'to': '676',
        
        # South/Central America and Caribbean
        'br': '55', 'ar': '54', 'cl': '56', 'co': '57', 'pe': '51', 've': '58',
        'ec': '593', 'bo': '591', 'py': '595', 'uy': '598', 'cr': '506', 'pa': '507',
        'gt': '502', 'sv': '503', 'hn': '504', 'ni': '505', 'cu': '53', 'jm': '1876',
        'do': '1809', 'ht': '509', 'bs': '1242', 'bb': '1246', 'tt': '1868',
    }
    
    # Phone number formatting patterns by region
    PHONE_PATTERNS = {
        # North American pattern: +1 XXX-XXX-XXXX
        'NORTH_AMERICA': lambda digits: f"+1 {digits[:3]}-{digits[3:6]}-{digits[6:10]}",
        
        # European standard: +XX YYY YYY YYY
        'EUROPE': lambda digits, code: f"+{code} {digits[:3]} {digits[3:6]} {digits[6:9]}",
        
        # UK: +44 YYYY XXXXXX
        'UK': lambda digits: f"+44 {digits[:4]} {digits[4:10]}",
        
        # Japan: +81 XX-XXXX-XXXX
        'JAPAN': lambda digits: f"+81 {digits[:2]}-{digits[2:6]}-{digits[6:10]}",
        
        # China: +86 XXX-XXXX-XXXX
        'CHINA': lambda digits: f"+86 {digits[:3]}-{digits[3:7]}-{digits[7:11]}",
        
        # India: +91 XXXXX-XXXXX
        'INDIA': lambda digits: f"+91 {digits[:5]}-{digits[5:10]}",
        
        # Australia: +61 X XXXX XXXX
        'AUSTRALIA': lambda digits: f"+61 {digits[0]} {digits[1:5]} {digits[5:9]}",
        
        # Middle East: +XXX XX XXX XXXX
        'MIDDLE_EAST': lambda digits, code: f"+{code} {digits[:2]} {digits[2:5]} {digits[5:9]}",
        
        # South America: +XX (XXX) XXX-XXXX
        'SOUTH_AMERICA': lambda digits, code: f"+{code} ({digits[:3]}) {digits[3:6]}-{digits[6:10]}",
        
        # Southeast Asia: +XX XX-XXXX-XXXX
        'SOUTHEAST_ASIA': lambda digits, code: f"+{code} {digits[:2]}-{digits[2:6]}-{digits[6:10]}",
        
        # Universal format with regional codes
        'UNIVERSAL': lambda digits, code, area_code=None:
            f"+{code} {area_code or digits[:2]} {digits[2:5]} {digits[5:9]}",
            
        # African: +XXX XX XXX XXXX - Generic format
        'AFRICA': lambda digits, code: f"+{code} {digits[:2]} {digits[2:5]} {digits[5:9]}",
    }
    
    # Region mapping for phone patterns - expanded with many more countries
    # The UNIVERSAL pattern allows for region-specific area codes based on the city/region
    # This approach provides more realistic, location-aware phone numbers that match
    # the generated address data, creating higher quality fake data
    REGION_PHONE_PATTERN = {
        # North America
        'us': 'NORTH_AMERICA', 'ca': 'NORTH_AMERICA', 
        
        # UK & Ireland - using universal format with regional area codes
        'gb': 'UNIVERSAL', 'uk': 'UNIVERSAL', 'ie': 'UNIVERSAL',
        
        # East Asia
        'jp': 'JAPAN', 'kr': 'JAPAN',
        'cn': 'CHINA', 'tw': 'CHINA', 'hk': 'CHINA', 'mo': 'CHINA',
        
        # South Asia
        'in': 'UNIVERSAL',  # India using region-specific area codes
        'pk': 'INDIA', 'bd': 'INDIA', 'np': 'INDIA', 'lk': 'INDIA',
        
        # Southeast Asia
        'my': 'SOUTHEAST_ASIA', 'id': 'SOUTHEAST_ASIA', 'sg': 'SOUTHEAST_ASIA', 
        'th': 'SOUTHEAST_ASIA', 'vn': 'SOUTHEAST_ASIA', 'ph': 'SOUTHEAST_ASIA',
        'mm': 'SOUTHEAST_ASIA', 'kh': 'SOUTHEAST_ASIA', 'la': 'SOUTHEAST_ASIA',
        
        # Oceania
        'au': 'AUSTRALIA', 'nz': 'AUSTRALIA',
        
        # Africa (with more specific country formats)
        'za': 'AFRICA', 'ng': 'AFRICA', 'gh': 'AFRICA', 
        'eg': 'AFRICA', 'ma': 'AFRICA', 'dz': 'AFRICA', 'tz': 'AFRICA',
        'ug': 'AFRICA', 'cm': 'AFRICA', 'ci': 'AFRICA',
        'zw': 'AFRICA', 'zm': 'AFRICA', 'cd': 'AFRICA', 'sn': 'AFRICA',
        'rw': 'AFRICA', 'mg': 'AFRICA', 'mu': 'AFRICA',
        
        # Use universal format with regional area codes for all countries
        'et': 'UNIVERSAL',  # Ethiopia
        'ke': 'UNIVERSAL',  # Kenya
        'ng': 'UNIVERSAL',  # Nigeria
        'za': 'UNIVERSAL',  # South Africa
        'gh': 'UNIVERSAL',  # Ghana
        
        # Middle East
        'sa': 'MIDDLE_EAST', 'ae': 'MIDDLE_EAST', 'qa': 'MIDDLE_EAST', 
        'kw': 'MIDDLE_EAST', 'om': 'MIDDLE_EAST', 'bh': 'MIDDLE_EAST',
        'il': 'MIDDLE_EAST', 'tr': 'MIDDLE_EAST', 'jo': 'MIDDLE_EAST', 
        'lb': 'MIDDLE_EAST', 'iq': 'MIDDLE_EAST', 'ir': 'MIDDLE_EAST',
        'ye': 'MIDDLE_EAST', 'sy': 'MIDDLE_EAST',
        
        # Latin America
        'mx': 'SOUTH_AMERICA', 'br': 'UNIVERSAL', 'ar': 'SOUTH_AMERICA',  # Brazil using region-specific area codes
        'co': 'SOUTH_AMERICA', 'pe': 'SOUTH_AMERICA', 'cl': 'SOUTH_AMERICA',
        've': 'SOUTH_AMERICA', 'ec': 'SOUTH_AMERICA', 'bo': 'SOUTH_AMERICA',
        'py': 'SOUTH_AMERICA', 'uy': 'SOUTH_AMERICA', 'gt': 'SOUTH_AMERICA',
        'cr': 'SOUTH_AMERICA', 'do': 'SOUTH_AMERICA', 'hn': 'SOUTH_AMERICA',
        'sv': 'SOUTH_AMERICA', 'ni': 'SOUTH_AMERICA', 'pa': 'SOUTH_AMERICA',
        
        # Europe - major countries use UNIVERSAL format with regional area codes
        'de': 'UNIVERSAL', 'fr': 'UNIVERSAL',  # Using region-specific area codes
        # Other European countries - will migrate to UNIVERSAL as area codes are added
        'it': 'EUROPE', 'es': 'EUROPE', 'nl': 'EUROPE', 'be': 'EUROPE', 
        'ch': 'EUROPE', 'at': 'EUROPE', 'se': 'EUROPE', 'no': 'EUROPE', 
        'dk': 'EUROPE', 'fi': 'EUROPE', 'pl': 'EUROPE', 'ru': 'EUROPE', 
        'ua': 'EUROPE', 'ro': 'EUROPE', 'pt': 'EUROPE', 'gr': 'EUROPE', 
        'cz': 'EUROPE', 'hu': 'EUROPE', 'bg': 'EUROPE', 'hr': 'EUROPE', 
        'rs': 'EUROPE', 'sk': 'EUROPE',
    }
    
    # Default region mappings
    DEFAULT_REGION_MAPPINGS = {
        'AMERICAS_NORTH': 'NORTH_AMERICA',
        'AMERICAS_CENTRAL': 'SOUTH_AMERICA',
        'AMERICAS_SOUTH': 'SOUTH_AMERICA',
        'AMERICAS_CARIBBEAN': 'NORTH_AMERICA',
        'EUROPE_NORTH': 'EUROPE',
        'EUROPE_WEST': 'EUROPE',
        'EUROPE_EAST': 'EUROPE',
        'EUROPE_SOUTH': 'EUROPE',
        'ASIA_CENTRAL': 'MIDDLE_EAST',
        'ASIA_EAST': 'SOUTHEAST_ASIA',
        'ASIA_SOUTH': 'INDIA',
        'ASIA_SOUTHEAST': 'SOUTHEAST_ASIA',
        'ASIA_WEST': 'MIDDLE_EAST',
        'AFRICA_NORTH': 'AFRICA',
        'AFRICA_WEST': 'AFRICA',
        'AFRICA_CENTRAL': 'AFRICA',
        'AFRICA_EAST': 'AFRICA',
        'AFRICA_SOUTH': 'AFRICA',
        'OCEANIA_AUSTRALIA': 'AUSTRALIA',
        'OCEANIA_MELANESIA': 'AUSTRALIA',
        'OCEANIA_MICRONESIA': 'AUSTRALIA',
        'OCEANIA_POLYNESIA': 'AUSTRALIA',
    }
    
    try:
        # Clean the phone number (remove all non-digit characters)
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Ensure we have enough digits to work with
        if len(clean_phone) < 8:
            # If too short, pad it with random digits
            clean_phone = clean_phone + ''.join([str(random.randint(0, 9)) for _ in range(10 - len(clean_phone))])
        
        # Get the calling code
        calling_code = CALLING_CODES.get(country_code.lower())
        
        if not calling_code:
            # If calling code not found directly, try to get it from CountryInfo as fallback
            try:
                country = pycountry.countries.get(alpha_2=country_code.upper())
                if country:
                    country_info = CountryInfo(country.name)
                    calling_code = country_info.calling_code()
            except Exception:
                # If all else fails, default to a random common code
                calling_code = random.choice(['1', '44', '33', '49'])
        
        # Determine the phone pattern to use
        pattern_key = REGION_PHONE_PATTERN.get(country_code.lower())
        
        if not pattern_key and country_code in COUNTRY_TO_REGION:
            # Get the region and look up the default pattern for that region
            region = COUNTRY_TO_REGION[country_code]
            pattern_key = DEFAULT_REGION_MAPPINGS.get(region, 'EUROPE')
        
        # Format the phone number using the appropriate pattern
        pattern_key_safe = pattern_key if pattern_key else 'EUROPE'
        
        if pattern_key_safe == 'NORTH_AMERICA':
            # Ensure exactly 10 digits for North American numbers
            while len(clean_phone) < 10:
                clean_phone += str(random.randint(0, 9))
            clean_phone = clean_phone[:10]
            return PHONE_PATTERNS['NORTH_AMERICA'](clean_phone)
            
        elif pattern_key_safe == 'UNIVERSAL':
            # Universal format with region-specific area codes for any country
            while len(clean_phone) < 9:
                clean_phone += str(random.randint(0, 9))
            clean_phone = clean_phone[:9]
            
            # Use region-specific area code if region is provided and country has area code mappings
            area_code = None
            if region and country_code.lower() in REGION_AREA_CODES:
                # Get the country's area code mappings
                country_area_codes = REGION_AREA_CODES[country_code.lower()]
                
                # Try exact match first
                if region in country_area_codes:
                    area_code = country_area_codes[region]
                else:
                    # Try partial match (e.g., if region is "Nairobi County" and we have "Nairobi")
                    for region_name, code in country_area_codes.items():
                        if region_name in region or region in region_name:
                            area_code = code
                            break
            
            return PHONE_PATTERNS[pattern_key_safe](clean_phone, calling_code, area_code)
            
        elif pattern_key_safe in ['UK', 'JAPAN', 'CHINA', 'INDIA', 'AUSTRALIA']:
            # Special formatting for specific countries
            # Ensure enough digits
            while len(clean_phone) < 10:
                clean_phone += str(random.randint(0, 9))
            # Limit to appropriate length
            clean_phone = clean_phone[:10]
            return PHONE_PATTERNS[pattern_key_safe](clean_phone)
            
        else:
            # General regional patterns that need a calling code
            # Ensure enough digits
            while len(clean_phone) < 9:
                clean_phone += str(random.randint(0, 9))
            # Limit to appropriate length
            clean_phone = clean_phone[:9]
            
            # Use the pattern if it exists, otherwise fallback to EUROPE
            if pattern_key_safe in PHONE_PATTERNS:
                return PHONE_PATTERNS[pattern_key_safe](clean_phone, calling_code)
            else:
                return PHONE_PATTERNS['EUROPE'](clean_phone, calling_code)
            
    except Exception as e:
        # Fallback to a simple international format if anything goes wrong
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone:
            clean_phone = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        calling_code = CALLING_CODES.get(country_code.lower(), '1')
        return f"+{calling_code} {clean_phone}"
    
    # If all else fails, return the original
    return phone

# Function to generate accurate postal codes for each country
def generate_postal_code(country_code: str) -> str:
    """Generate realistic postal codes specific to each country."""
    postal_code_formats = {
        # North America
        'us': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ca': lambda: f"{random.choice('ABCEGHJKLMNPRSTVXY')}{random.randint(0,9)}{random.choice('ABCEGHJKLMNPRSTVWXYZ')} {random.randint(0,9)}{random.choice('ABCEGHJKLMNPRSTVWXYZ')}{random.randint(0,9)}", # ANA NAN
        'mx': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        
        # Europe
        'uk': lambda: f"{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.randint(1,99)} {random.randint(1,9)}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}", # AA9 9AA
        'gb': lambda: f"{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.randint(1,99)} {random.randint(1,9)}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}", # same as UK
        'fr': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'de': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'it': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'es': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'pt': lambda: f"{random.randint(1000, 9999)}-{random.randint(100, 999)}", # 4+3 digits
        'nl': lambda: f"{random.randint(1000, 9999)} {random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}{random.choice('ABCDEFGHJKLMNOPRSTUWXYZ')}", # 4 digits + 2 letters
        'be': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'se': lambda: f"{random.randint(100, 999)} {random.randint(10, 99)}", # 3 digits + 2 digits
        'no': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'fi': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'dk': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'pl': lambda: f"{random.randint(10, 99)}-{random.randint(100, 999)}", # 2+3 digits
        'ru': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        'ua': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ch': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'at': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        
        # Asia
        'cn': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        'jp': lambda: f"{random.randint(100, 999)}-{random.randint(1000, 9999)}", # 3+4 digits
        'kr': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'in': lambda: f"{random.randint(100000, 999999)}", # 6 digits PIN code
        'sg': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        'my': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ph': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'th': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'id': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'vn': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        
        # Middle East
        'il': lambda: f"{random.randint(1000000, 9999999)}", # 7 digits
        'sa': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ae': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'tr': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        
        # Africa
        'za': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'ng': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        'eg': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ma': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'ke': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'gh': lambda: f"{random.choice('ABCDEFGHJK')}{random.choice('ABCDEFGHJK')}-{random.randint(100, 999)}", # Ghana digital addressing format
        
        # Oceania
        'au': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        'nz': lambda: f"{random.randint(1000, 9999)}", # 4 digits
        
        # South/Central America
        'br': lambda: f"{random.randint(10000, 99999)}-{random.randint(100, 999)}", # 5+3 digits
        'ar': lambda: f"{random.choice('ABCDEFGHJK')}{random.randint(1000, 9999)}{random.choice('ABCDEFGHJK')}{random.choice('ABCDEFGHJK')}{random.choice('ABCDEFGHJK')}", # Letter+4 digits+3 letters
        'mx': lambda: f"{random.randint(10000, 99999)}", # 5 digits
        'cl': lambda: f"{random.randint(1000000, 9999999)}", # 7 digits
        'co': lambda: f"{random.randint(100000, 999999)}", # 6 digits
        
        # Generic fallback format
        'xx': lambda: f"{random.randint(10000, 99999)}", # 5 digits
    }
    
    # Use country-specific format if available, otherwise use generic fallback
    if country_code.lower() in postal_code_formats:
        return postal_code_formats[country_code.lower()]()
    else:
        # For countries without postal code systems or specific formats, use region-based fallbacks
        region = COUNTRY_TO_REGION.get(country_code.lower(), 'unknown')
        
        if region == 'AFRICA_EAST' or region == 'AFRICA_CENTRAL':
            # Many East/Central African countries don't use postal codes or use very simple ones
            return f"{random.randint(100, 999)}"
        elif region == 'AFRICA_NORTH':
            return f"{random.randint(1000, 9999)}"
        elif region == 'AFRICA_SOUTH':
            return f"{random.randint(1000, 9999)}"
        elif region == 'AFRICA_WEST':
            return f"{random.randint(100000, 999999)}"
        elif 'AMERICAS' in region:
            return f"{random.randint(10000, 99999)}"
        elif 'ASIA' in region:
            return f"{random.randint(100000, 999999)}"
        elif 'EUROPE' in region:
            return f"{random.randint(10000, 99999)}"
        elif 'OCEANIA' in region:
            return f"{random.randint(1000, 9999)}"
        else:
            # Default generic postal code
            return f"{random.randint(10000, 99999)}"

def get_data_quality(country_code: str, api_source: str) -> Tuple[str, str]:
    """Determine data quality for the given country and data source."""
    # Data quality levels for different countries
    
    # Countries with highest quality data from both API and Faker
    TIER_1_COUNTRIES = [
        'us', 'gb', 'uk', 'ca', 'au', 'de', 'fr', 'es', 'it', 'nl', 'br',
        'in', 'jp', 'nz', 'dk', 'fi', 'no', 'se', 'ch', 'ie', 'be'
    ]
    
    # Countries with good quality data from either API or Faker
    TIER_2_COUNTRIES = [
        'mx', 'ar', 'cl', 'za', 'ng', 'eg', 'sa', 'ae', 'tr', 'kr', 'cn',
        'id', 'th', 'vn', 'ph', 'my', 'pl', 'ru', 'ua', 'cz', 'at', 'pt',
        'gr', 'ro', 'hu', 'bg', 'rs', 'hr', 'il', 'sg', 'hk', 'ir', 'co',
        'pe', 've', 'pk', 'bd', 'dz', 'ma', 'ke', 'gh', 'tz'
    ]
    
    # Countries with specialized regional handling
    TIER_3_COUNTRIES = [
        # Middle East
        'jo', 'kw', 'qa', 'bh', 'om', 'lb', 'sy', 'iq', 'ye', 'ps', 
        # Asia
        'tw', 'hk', 'mo', 'mn', 'lk', 'np', 'mm', 'kh', 'la', 'bn', 'pg', 'fj', 'bt', 'mv',
        # Central Asia
        'kz', 'uz', 'tm', 'kg', 'tj',
        # Caribbean
        'pr', 'do', 'cu', 'jm', 'tt', 'bs', 'bb', 'dm', 'ht', 'ag', 'vc', 'lc', 'gd', 'kn',
        # Central/South America
        'cr', 'pa', 'uy', 'py', 'ec', 'bo', 'gt', 'sv', 'hn', 'ni', 'gy', 'sr', 'gf',
        # Africa - Extended coverage
        'ly', 'tn', 'sd', 'ss', 'er', 'dj', 'so', 'mr', 'ml', 'ne', 'td', 'bf', 'sn', 'gm', 
        'gw', 'gn', 'sl', 'lr', 'ci', 'tg', 'bj', 'cd', 'cg', 'ga', 'gq', 'cm', 'cf', 'rw', 
        'bi', 'ug', 'zm', 'zw', 'mw', 'mz', 'zw', 'bw', 'na', 'sz', 'ls', 'et', 'sc', 'km',
        # Europe
        'sk', 'si', 'ee', 'lv', 'lt', 'lu', 'mt', 'cy', 'is', 'fo', 'ad', 'mc', 'li', 'sm', 'va', 
        'ba', 'mk', 'al', 'me', 'md', 'by', 'am', 'ge', 'az'
    ]
    
    # Determine API-specific quality
    if api_source == "api":
        # RandomUser API directly supported countries
        api_supported = [
            'au', 'br', 'ca', 'ch', 'de', 'dk', 'es', 'fi', 'fr', 'gb', 'uk', 
            'ie', 'in', 'ir', 'mx', 'nl', 'no', 'nz', 'rs', 'tr', 'ua', 'us'
        ]
        
        if country_code in api_supported:
            return "🟢", f"High (RandomUser API Native)"
        elif country_code in TIER_1_COUNTRIES:
            return "🟡", f"Medium (API Approximation)"
        elif country_code in TIER_2_COUNTRIES:
            return "🟠", f"Fair (Regional API Mapping)"
        else:
            return "🔴", f"Basic (Generic API Data)"
    else:
        # Faker library quality levels
        # Region-specific quality assessment
        if country_code in TIER_1_COUNTRIES:
            region_info = ""
            if country_code in COUNTRY_TO_REGION:
                region = COUNTRY_TO_REGION[country_code]
                region_display = region.replace('_', ' ').title()
                region_info = f" - {region_display}"
            return "🟡", f"Medium (Complete Locale{region_info})"
            
        elif country_code in TIER_2_COUNTRIES:
            # Check if country has a specific locale
            has_specific_locale = False
            locale_code = LOCALES.get(country_code, ('en_US', ''))[0]
            if locale_code.split('_')[0].lower() != 'en' or country_code in ['in', 'sg', 'ph']:
                has_specific_locale = True
                
            if has_specific_locale:
                return "🟡", f"Medium (Country-Specific Locale)"
            else:
                return "🟠", f"Fair (Regional Adaptation)"
                
        elif country_code in TIER_3_COUNTRIES:
            # For countries with some regional handling
            if country_code in COUNTRY_TO_REGION:
                region = COUNTRY_TO_REGION[country_code]
                region_display = region.replace('_', ' ').title()
                return "🟠", f"Fair (Regional Format - {region_display})"
            else:
                return "🟠", f"Fair (Regional Format)"
                
        else:
            # Basic fallback for the rest of the world
            if country_code in COUNTRY_TO_REGION:
                region = COUNTRY_TO_REGION[country_code]
                region_display = region.replace('_', ' ').title()
                return "🔴", f"Basic (Pattern-Based - {region_display})"
            else:
                return "🔴", f"Basic (Pattern-Based)"

@Client.on_message(filters.command("fake", [".", "/"]))
async def cmd_fake(client, message):
    try:
        # Check user permissions
        checkall = await check_all_thing(client, message)
        if not checkall[0]:
            return
        
        role = checkall[1]
        
        # Parse country code from command if provided
        country_code = 'us'  # Default
        country_query = ""
        
        if len(message.text.split(" ")) > 1:
            country_query = message.text.split(" ", 1)[1].strip()
            country_code = get_country_code(country_query)
        
        # Get locale and flag for the country
        locale, flag = LOCALES.get(country_code, ('en_US', '🇺🇸'))
        
        # Get region information for more context
        region_display = ""
        if country_code in COUNTRY_TO_REGION:
            region = COUNTRY_TO_REGION[country_code]
            region_display = region.replace('_', ' ').title()
        
        # Create Faker instance with the appropriate locale (with validation)
        try:
            fake = Faker(locale)
        except (AttributeError, ImportError) as e:
            # If invalid locale, fallback to a safe default
            await error_log(f"Invalid Faker locale '{locale}' for country '{country_code}', falling back to en_US")
            fake = Faker('en_US')
        
        # Get additional data from RandomUser API if possible
        api_data = await get_random_info_from_api(country_code)
        api_source = "api" if api_data else "faker"
        
        # For specific regions (like Africa, especially Ethiopia), ensure we always use 
        # our own consistent data generators rather than mixing API data
        use_custom_generation = country_code in [
            # East Africa - always use our custom data to avoid mixing
            'et', 'ke', 'tz', 'ug', 'rw', 'bi', 'ss', 'so', 'dj', 'er',
            # West Africa
            'ng', 'gh', 'ci', 'sn', 'ml', 'bf', 'bj', 'gm', 'gn', 'gw', 'lr', 'ne', 'sl', 'tg',
            # North Africa
            'eg', 'ma', 'dz', 'tn', 'ly', 'sd', 'mr',
            # Southern Africa
            'za', 'zw', 'zm', 'na', 'bw', 'mz', 'ao', 'ls', 'sz'
        ]
        if use_custom_generation:
            api_data = None
            api_source = "faker"
        
        # Generate the fake info
        try:
            # Get country name based on locale first (we need this for various localization)
            try:
                country_obj = pycountry.countries.get(alpha_2=country_code.upper())
                fake_country = country_obj.name if country_obj else fake.country()
            except:
                fake_country = fake.country()
            
            # Generate birth date (30-70 years ago)
            fake_birthdate = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%Y-%m-%d")
            age = datetime.now().year - int(fake_birthdate.split('-')[0])
            
            # Get name - use API data if available and appropriate, otherwise use our regional patterns
            if api_data and 'name' in api_data and not use_custom_generation:
                # Use API data for name
                first_name = api_data['name']['first']
                last_name = api_data['name']['last']
                fake_name = f"{first_name} {last_name}"
                fake_first_name = first_name
                fake_last_name = last_name
            else:
                # Generate names with regional and country-specific patterns
                fake_gender = fake.random_element(['Male', 'Female'])
                
                # East Asian countries with family name first
                if country_code in ['cn', 'jp', 'kr', 'tw', 'hk', 'mo', 'vn']:
                    # East Asian name format (family name first)
                    if country_code == 'cn' or country_code == 'hk':
                        # Chinese names
                        chinese_last_names = ["Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao", "Wu", 
                                           "Zhou", "Xu", "Sun", "Ma", "Zhu", "Hu", "Guo", "Lin", "He", "Gao", "Luo"]
                        chinese_first_names_male = ["Wei", "Jie", "Min", "Yong", "Hao", "Jun", "Xiang", "Bo", "Feng", 
                                                "Cheng", "Ming", "Lei", "Yu", "Tao", "Hui", "Kai", "Long", "Bin", "Peng"]
                        chinese_first_names_female = ["Yan", "Na", "Li", "Juan", "Xin", "Fang", "Ying", "Mei", "Hong", 
                                                 "Hua", "Lin", "Xue", "Qian", "Jing", "Lei", "Min", "Ping", "Qi", "Yu"]
                                              
                        fake_last_name = random.choice(chinese_last_names)
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(chinese_first_names_male)
                        else:
                            fake_first_name = random.choice(chinese_first_names_female)
                    
                    elif country_code == 'jp':
                        # Japanese names
                        japanese_last_names = ["Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito", "Yamamoto", 
                                            "Nakamura", "Kobayashi", "Kato", "Yoshida", "Yamada", "Sasaki", "Yamaguchi"]
                        japanese_first_names_male = ["Hiroshi", "Takashi", "Kazuo", "Akira", "Kenji", "Shigeru", 
                                                  "Toshio", "Yasuo", "Masao", "Hideo", "Yutaka", "Osamu", "Susumu"]
                        japanese_first_names_female = ["Yoko", "Keiko", "Yukiko", "Akiko", "Yumiko", "Kimiko", 
                                                    "Kazuko", "Sachiko", "Junko", "Masako", "Tomoko", "Naoko"]
                        
                        fake_last_name = random.choice(japanese_last_names)
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(japanese_first_names_male)
                        else:
                            fake_first_name = random.choice(japanese_first_names_female)
                    
                    elif country_code == 'kr':
                        # Korean names
                        korean_last_names = ["Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Cho", "Han", "Lim", 
                                          "Hong", "Song", "Yoon", "Jang", "Shin", "Yang", "Ahn", "Hwang", "Yoo"]
                        korean_first_names_male = ["Min-ho", "Ji-hoon", "Seung-hyun", "Dong-hyun", "Joon-ho", 
                                               "Sung-min", "Hyun-woo", "Tae-hyung", "Joon-young", "Seok-jin"]
                        korean_first_names_female = ["Ji-young", "Min-ji", "Soo-jin", "Hye-jin", "Ji-eun", 
                                                 "Eun-jung", "Yoo-jin", "Sung-hee", "Hye-won", "Ji-hye"]
                        
                        fake_last_name = random.choice(korean_last_names)
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(korean_first_names_male)
                        else:
                            fake_first_name = random.choice(korean_first_names_female)
                    
                    elif country_code == 'vn':
                        # Vietnamese names
                        vietnamese_last_names = ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Huynh", "Vu", "Vo", 
                                              "Dang", "Bui", "Do", "Ho", "Ngo", "Duong", "Ly", "Dao", "Dinh"]
                        vietnamese_first_names_male = ["Minh", "Hieu", "Tuan", "Duc", "Hung", "Thanh", "Dat", 
                                                    "Anh", "Quan", "Son", "Khanh", "Tung", "Khoa", "Thang"]
                        vietnamese_first_names_female = ["Huong", "Hoa", "Lan", "Thuy", "Trang", "Mai", "Hong", 
                                                      "Lien", "Phuong", "Van", "Hanh", "My", "Ngoc", "Linh"]
                        
                        fake_last_name = random.choice(vietnamese_last_names)
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(vietnamese_first_names_male)
                        else:
                            fake_first_name = random.choice(vietnamese_first_names_female)
                    else:
                        # Default East Asian pattern
                        fake_last_name = fake.last_name()
                        fake_first_name = fake.first_name()
                
                    # For all East Asian countries, family name comes first
                    fake_name = f"{fake_last_name} {fake_first_name}"
                
                # African countries
                elif country_code in ['ke', 'tz', 'ug', 'et', 'rw', 'bi', 'ng', 'gh', 'za', 'zm', 'zw', 'cm', 'cd', 
                                    'eg', 'ma', 'dz', 'tn', 'sd', 'ss', 'so', 'ci', 'ml', 'sn', 'mg', 'bj', 'gm',
                                    'bw', 'na', 'mz', 'ao', 'ls', 'sz']:
                    # Enhanced African names with culturally appropriate patterns
                    # Get ethnicity group before generating first name so we can match last name
                    if country_code == 'et':
                        # For Ethiopia, get the ethnicity first for matching
                        ethnicities = ['et_amhara', 'et_oromo', 'et_tigray', 'et_gurage', 'et']
                        weights = [27, 34, 6, 8, 25]  # Population distribution
                        ethnicity = random.choices(ethnicities, weights=weights, k=1)[0]
                        # Save ethnicity for later matching with last name
                        selected_ethnicity = ethnicity
                    else:
                        selected_ethnicity = None
                        
                    # Get culturally appropriate first name with potential ethnicity info
                    fake_first_name, name_ethnicity = get_african_name(fake_gender, country_code, 
                                                                      preselected_ethnicity=selected_ethnicity,
                                                                      return_ethnicity=True)
                    
                    # East African last names
                    east_african_last_names = {
                        'ke': ["Kamau", "Mwangi", "Wanjiku", "Ochieng", "Otieno", "Odhiambo", "Njoroge", 
                             "Karanja", "Kimani", "Wambui", "Kinyua", "Onyango", "Korir", "Kipchoge"],
                        'tz': ["Mohammed", "Hassan", "Ali", "Juma", "Hamisi", "Salehe", "Rajabu", "Musa", 
                              "Mbwana", "Mtoro", "Khalfan", "Fadhili", "Nyerere", "Mazengo", "Magesa"],
                        'ug': ["Okello", "Opio", "Onyango", "Wasswa", "Kato", "Mukasa", "Ssekabira", 
                              "Mugisha", "Tumusiime", "Kirabo", "Nakimuli", "Byaruhanga", "Tusiime"],
                        # Ethiopian last names by ethnic groups
                        'et_amhara': ["Demeke", "Bekele", "Abebe", "Tesfaye", "Girma", "Assefa", "Tilahun", 
                                    "Tadesse", "Haile", "Mengiste", "Mulatu", "Fisseha", "Melaku", "Zerihun"],
                        'et_oromo': ["Gemechu", "Bekele", "Wakjira", "Kumsa", "Degefa", "Deressa", "Mulatu",
                                   "Negash", "Geleta", "Serbessa", "Tafesse", "Dugassa", "Lemessa", "Wako"],
                        'et_tigray': ["Hagos", "Berhe", "Gebremichael", "Tesfay", "Gebreselassie", "Araya",
                                    "Gebrehiwot", "Girmay", "Tekle", "Abraha", "Alem", "Mehari", "Woldu"],
                        'et_gurage': ["Ahmed", "Mohammed", "Ibrahim", "Abdi", "Hussein", "Omar", "Abubeker",
                                    "Jemal", "Kemal", "Awol", "Abdulkadir", "Ismael", "Mahmoud"],
                        'et': ["Demeke", "Bekele", "Abebe", "Tesfaye", "Girma", "Assefa", "Tilahun", 
                              "Tadesse", "Haile", "Mengiste", "Mulatu", "Fisseha", "Melaku", "Zerihun",
                              "Solomon", "Daniel", "Dawit", "Samuel", "Michael", "Messele", "Worku", "Seyoum"],
                        'rw': ["Bizimana", "Hakizimana", "Nshimiyimana", "Uwimana", "Mukamana", "Nsengimana", 
                              "Niyonzima", "Ndayishimiye", "Niyonsaba", "Murenzi", "Uwase", "Mukankusi"],
                        'bi': ["Nzeyimana", "Nduwimana", "Nkurunziza", "Nsabimana", "Nsengiyumva", 
                              "Hakizimana", "Bigirimana", "Ndayishimiye", "Bizimana", "Harushimana"]
                    }
                    
                    # Get culturally appropriate last names based on region/country
                    if country_code == 'et':
                        # For Ethiopia, we want to match the ethnicity used for first name
                        # First, determine which ethnic group was used for the first name
                        ethnicity = 'et'  # Default

                        # Check all ethnic-specific name lists to see which one contains our first name
                        for ethnic_group in ['et_amhara', 'et_oromo', 'et_tigray', 'et_gurage', 'et']:
                            if ethnic_group in east_african_country_male_names:
                                male_names = east_african_country_male_names[ethnic_group]
                                female_names = east_african_country_female_names[ethnic_group]
                                
                                # Check if the first name is in this ethnic group's list
                                if (fake_gender.lower().startswith('m') and fake_first_name in male_names) or \
                                   (not fake_gender.lower().startswith('m') and fake_first_name in female_names):
                                    ethnicity = ethnic_group
                                    break
                        
                        # Get a last name that matches the ethnicity of the first name
                        if ethnicity in east_african_last_names:
                            fake_last_name = random.choice(east_african_last_names[ethnicity])
                        else:
                            fake_last_name = random.choice(east_african_last_names['et'])
                            
                    elif country_code in ['ke', 'tz', 'ug', 'rw', 'bi']:
                        # Use the country's last names from our master list
                        fake_last_name = random.choice(east_african_last_names[country_code])
                        country_lastnames = east_african_last_names.get(country_code, east_african_last_names['ke'])
                        fake_last_name = random.choice(country_lastnames)
                        
                    elif country_code in ['ng', 'gh', 'ci', 'sn', 'ml', 'bj', 'gm']:
                        # West African last names
                        west_african_last_names = {
                            'ng': ["Adeyemi", "Okafor", "Okonkwo", "Adebayo", "Eze", "Nwachukwu", "Afolabi", 
                                 "Obasanjo", "Ademola", "Odusanya", "Nwosu", "Okeke", "Chukwu", "Ibrahim"],
                            'gh': ["Mensah", "Owusu", "Osei", "Boateng", "Agyemang", "Acheampong", "Appiah", 
                                  "Asante", "Amoah", "Addo", "Kufuor", "Agyapong", "Frimpong", "Nkrumah"],
                            'ci': ["Kouassi", "Koffi", "Konan", "N'Guessan", "Kouame", "Kone", "Yao", "Outtara", 
                                  "Bamba", "Coulibaly", "Traore", "Fofana", "Toure", "Keita", "Drogba"],
                            'sn': ["Diop", "Seck", "Ndiaye", "Fall", "Diallo", "Gueye", "Cisse", "Diouf", 
                                  "Mbaye", "Sarr", "Thiam", "Sow", "Ndour", "Toure", "Samb", "Faye"],
                            'ml': ["Traore", "Keita", "Coulibaly", "Diarra", "Sissoko", "Toure", "Diallo", 
                                  "Kone", "Dembele", "Maiga", "Camara", "Sako", "Sidibe", "Sangare"],
                            'bj': ["Adjayi", "Agbodjan", "Amoussou", "Assogba", "Dossou", "Hounsou", 
                                  "Koudogbo", "Mensah", "Ouinsou", "Sossou", "Tossou", "Zinsou"],
                            'gm': ["Jallow", "Ceesay", "Touray", "Sowe", "Njie", "Jobe", "Faal", 
                                  "Secka", "Manneh", "Bah", "Camara", "Jammeh", "Sanneh", "Gaye"]
                        }
                        country_lastnames = west_african_last_names.get(country_code, west_african_last_names['ng'])
                        fake_last_name = random.choice(country_lastnames)
                        
                    elif country_code in ['za', 'zm', 'zw', 'bw', 'na', 'mz', 'ao', 'ls', 'sz']:
                        # Southern African last names
                        southern_african_last_names = {
                            'za': ["Nkosi", "Dlamini", "Mkhize", "Ndlovu", "Zuma", "Sithole", "Mahlangu", 
                                 "Mokoena", "Tshabalala", "Molefe", "Mthembu", "Khumalo", "Mashaba", "Modise"],
                            'zm': ["Banda", "Mwanza", "Phiri", "Mulenga", "Daka", "Zulu", "Bwalya", 
                                  "Mbewe", "Ngoma", "Mwaba", "Nkonde", "Tembo", "Mwila", "Lungu"],
                            'zw': ["Moyo", "Ncube", "Dube", "Sibanda", "Mpofu", "Ndlovu", "Nyoni", 
                                  "Mlilo", "Nkomo", "Sithole", "Siziba", "Tshuma", "Mugabe", "Mujuru"],
                            'bw': ["Modise", "Nkate", "Moremi", "Motsumi", "Molosiwa", "Seretse", 
                                  "Mogae", "Matambo", "Molefhe", "Kedikilwe", "Balopi", "Mokaila"],
                            'na': ["Namises", "Ndeitunga", "Haingura", "Nghidinwa", "Haufiku", 
                                  "Nujoma", "Shanghala", "Uutoni", "Iyambo", "Namoloh", "Ekandjo"],
                            'mz': ["Machel", "Mondlane", "Chissano", "Guebuza", "Dhlakama", "Nyusi", 
                                  "Chipande", "Simango", "Chingoka", "Tembe", "Matusse", "Mabunda"]
                        }
                        country_lastnames = southern_african_last_names.get(country_code, southern_african_last_names['za'])
                        fake_last_name = random.choice(country_lastnames)
                        
                    elif country_code in ['cm', 'cd', 'cg', 'ga', 'gq', 'cf', 'st', 'td']:
                        # Central African last names
                        central_african_last_names = {
                            'cm': ["Kamga", "Nana", "Ngono", "Mbarga", "Atangana", "Fouda", "Meka", 
                                 "Biya", "Samba", "Mbida", "Mvondo", "Oyono", "Essomba", "Eto'o"],
                            'cd': ["Kabila", "Tshisekedi", "Mobutu", "Kasavubu", "Lumumba", "Katumbi", 
                                  "Mbemba", "Lukaku", "Mulumba", "Kasongo", "Mutombo", "Ilunga"],
                            'cg': ["Nguesso", "Lissouba", "Yhombi-Opango", "Kolélas", "Mabiala", 
                                  "Bokamba", "Mokoko", "Youlou", "Balou", "Dambendzet", "Poungui"],
                            'ga': ["Bongo", "Mba", "Aubameyang", "Mebiame", "Oyé-Mba", "Ping", 
                                  "Moussavou", "Ntoutoume", "Obame", "Ndong", "Ondo", "Mezui"]
                        }
                        country_lastnames = central_african_last_names.get(country_code, central_african_last_names['cd'])
                        fake_last_name = random.choice(country_lastnames)
                        
                    elif country_code in ['eg', 'ma', 'dz', 'tn', 'sd', 'ss', 'so']:
                        # North African last names
                        north_african_last_names = {
                            'eg': ["Ahmed", "Mohamed", "Ali", "Ibrahim", "Hassan", "Mahmoud", "Hussein", 
                                 "Mustafa", "Farouk", "Osman", "Abdel-Rahman", "El-Sayed", "Morsi"],
                            'ma': ["El Fassi", "Bennani", "Alaoui", "El Moutawakel", "Berrada", "Tazi", 
                                  "Bakkali", "Lamrani", "Belhaj", "El Bouazzaoui", "Chraibi", "Saadi"],
                            'dz': ["Bouteflika", "Belhadj", "Krim", "Zidane", "Fekir", "Brahimi", 
                                  "Bentaleb", "Mekhloufi", "Madjer", "Belmadi", "Bendebka", "Slimani"],
                            'tn': ["Ben Ali", "Bourguiba", "Jebali", "Marzouki", "Ghannouchi", "Jendoubi", 
                                  "Essebsi", "Sfar", "Maaloul", "Khazri", "Sliti", "Sassi", "Badri"],
                            'sd': ["Bashir", "Al-Mahdi", "Ibrahim", "Abdelrahman", "Ali", "Hamad", 
                                  "Ahmed", "El-Shafie", "Khalil", "Al-Mirghani", "Salih", "Hamdok"]
                        }
                        country_lastnames = north_african_last_names.get(country_code, north_african_last_names['eg'])
                        fake_last_name = random.choice(country_lastnames)
                    else:
                        # For other African countries, use generic African last names
                        generic_african_last_names = ["Abubakar", "Ibrahim", "Mohammed", "Abebe", "Bekele", 
                                                    "Okafor", "Mensah", "Nkosi", "Dlamini", "Banda", "Moyo"]
                        fake_last_name = random.choice(generic_african_last_names)
                    
                    fake_name = f"{fake_first_name} {fake_last_name}"
                
                # Middle Eastern countries
                elif country_code in ['sa', 'ae', 'jo', 'lb', 'sy', 'iq', 'kw', 'qa', 'bh', 'om', 'ye', 'tr', 'il']:
                    # Middle Eastern names
                    if country_code in ['sa', 'ae', 'jo', 'lb', 'sy', 'iq', 'kw', 'qa', 'bh', 'om', 'ye']:
                        # Arabic names
                        arabic_first_names_male = ["Mohammed", "Ahmed", "Abdullah", "Ali", "Omar", "Khaled", 
                                                "Saeed", "Ibrahim", "Youssef", "Mahmoud", "Hassan", "Mustafa"]
                        arabic_first_names_female = ["Fatima", "Aisha", "Amina", "Layla", "Noor", "Sara", 
                                                  "Mariam", "Huda", "Zainab", "Rana", "Leila", "Nadia"]
                        arabic_last_names = ["Al-Saud", "Al-Thani", "Al-Nahyan", "Al-Sabah", "Al-Said", 
                                          "Al-Hashemi", "Al-Husseini", "Al-Rashid", "Al-Sharif", "Al-Atrash",
                                          "Al-Qahtani", "Al-Ghamdi", "Al-Shammari", "Al-Mutairi", "Al-Dosari"]
                        
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(arabic_first_names_male)
                        else:
                            fake_first_name = random.choice(arabic_first_names_female)
                        fake_last_name = random.choice(arabic_last_names)
                    
                    elif country_code == 'tr':
                        # Turkish names
                        turkish_first_names_male = ["Ahmet", "Mehmet", "Mustafa", "Ibrahim", "Ali", "Hasan", 
                                                "Hüseyin", "Osman", "Kemal", "Orhan", "Emre", "Yusuf", "Burak"]
                        turkish_first_names_female = ["Ayşe", "Fatma", "Zeynep", "Elif", "Meryem", "Emine", 
                                                   "Esra", "Özlem", "Yasemin", "Merve", "Hatice", "Selin"]
                        turkish_last_names = ["Yılmaz", "Kaya", "Demir", "Şahin", "Çelik", "Öztürk", "Kılıç", 
                                           "Yıldız", "Aydın", "Özdemir", "Arslan", "Doğan", "Erdoğan"]
                        
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(turkish_first_names_male)
                        else:
                            fake_first_name = random.choice(turkish_first_names_female)
                        fake_last_name = random.choice(turkish_last_names)
                    
                    elif country_code == 'il':
                        # Israeli/Hebrew names
                        hebrew_first_names_male = ["Moshe", "David", "Yosef", "Avraham", "Yitzhak", "Yaakov", 
                                                "Shlomo", "Daniel", "Chaim", "Yehuda", "Ari", "Noam", "Eitan"]
                        hebrew_first_names_female = ["Sarah", "Rivka", "Rachel", "Leah", "Miriam", "Esther", 
                                                  "Hannah", "Tamar", "Yael", "Shira", "Noa", "Maya", "Talia"]
                        hebrew_last_names = ["Cohen", "Levy", "Mizrahi", "Peretz", "Bitton", "Dahan", "Avraham", 
                                          "Friedman", "Shapiro", "Rosenberg", "Goldstein", "Weiss", "Klein"]
                        
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(hebrew_first_names_male)
                        else:
                            fake_first_name = random.choice(hebrew_first_names_female)
                        fake_last_name = random.choice(hebrew_last_names)
                    
                    fake_name = f"{fake_first_name} {fake_last_name}"
                
                # Indian subcontinent
                elif country_code in ['in', 'pk', 'bd', 'np', 'lk']:
                    if country_code == 'in':
                        # Indian names with regional diversity
                        indian_names = {
                            'north': {
                                'male': ["Raj", "Vikram", "Amit", "Rahul", "Sanjay", "Ajay", "Vivek", "Rajesh", 
                                       "Sunil", "Anil", "Suresh", "Rakesh", "Pankaj", "Ashok", "Deepak"],
                                'female': ["Priya", "Neha", "Pooja", "Anjali", "Anita", "Sunita", "Kavita", 
                                         "Meena", "Geeta", "Asha", "Rita", "Kiran", "Shobha", "Rekha"],
                                'last': ["Sharma", "Patel", "Verma", "Gupta", "Singh", "Kumar", "Yadav", "Jha", 
                                       "Mishra", "Chauhan", "Agarwal", "Joshi", "Trivedi", "Desai", "Shah"]
                            },
                            'south': {
                                'male': ["Krishna", "Venkat", "Ramesh", "Suresh", "Rajesh", "Prakash", "Mahesh", 
                                       "Ganesh", "Srinivas", "Mohan", "Raghavan", "Harish", "Karthik"],
                                'female': ["Lakshmi", "Padma", "Sunitha", "Anitha", "Savitha", "Kavitha", "Radha", 
                                         "Shanthi", "Geetha", "Meena", "Saraswathi", "Vijaya", "Usha"],
                                'last': ["Reddy", "Naidu", "Rao", "Pillai", "Nair", "Menon", "Iyer", "Iyengar", 
                                       "Krishnan", "Subramaniam", "Swamy", "Gopal", "Hegde", "Kamath"]
                            }
                        }
                        region = random.choice(['north', 'south'])
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(indian_names[region]['male'])
                        else:
                            fake_first_name = random.choice(indian_names[region]['female'])
                        fake_last_name = random.choice(indian_names[region]['last'])
                    
                    elif country_code == 'pk':
                        # Pakistani names
                        pakistani_first_names_male = ["Ahmed", "Mohammed", "Ali", "Hassan", "Hussain", "Imran", 
                                                    "Farhan", "Faisal", "Tariq", "Zain", "Bilal", "Hamza"]
                        pakistani_first_names_female = ["Fatima", "Ayesha", "Sana", "Amina", "Maryam", "Zainab", 
                                                      "Saima", "Nadia", "Asma", "Samina", "Hina", "Rabia"]
                        pakistani_last_names = ["Khan", "Malik", "Chaudhry", "Ahmed", "Ali", "Shah", "Syed", 
                                              "Qureshi", "Baig", "Rizvi", "Butt", "Mirza", "Awan", "Sheikh"]
                        
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(pakistani_first_names_male)
                        else:
                            fake_first_name = random.choice(pakistani_first_names_female)
                        fake_last_name = random.choice(pakistani_last_names)
                    
                    elif country_code == 'bd':
                        # Bangladeshi names
                        bangladeshi_first_names_male = ["Mohammed", "Abdullah", "Rahman", "Kamal", "Jamal", 
                                                      "Hossain", "Islam", "Alam", "Ahmed", "Rahim", "Kazi"]
                        bangladeshi_first_names_female = ["Fatima", "Ayesha", "Nasreen", "Jasmine", "Momtaz", 
                                                        "Farzana", "Salma", "Nargis", "Taslima", "Rabeya"]
                        bangladeshi_last_names = ["Khan", "Rahman", "Ahmed", "Hossain", "Islam", "Alam", 
                                                "Uddin", "Ahamed", "Chowdhury", "Ali", "Miah", "Molla"]
                        
                        if fake_gender.lower().startswith('m'):
                            fake_first_name = random.choice(bangladeshi_first_names_male)
                        else:
                            fake_first_name = random.choice(bangladeshi_first_names_female)
                        fake_last_name = random.choice(bangladeshi_last_names)
                    
                    fake_name = f"{fake_first_name} {fake_last_name}"
                
                # Default pattern for other countries - use Faker's own patterns
                else:
                    # Standard Western name format
                    try:
                        fake_first_name = fake.first_name()
                        fake_last_name = fake.last_name()
                        fake_name = f"{fake_first_name} {fake_last_name}"
                    except:
                        # Fallback if Faker fails for some reason
                        common_first_names = ["James", "John", "Robert", "Michael", "William", "David", "Mary", 
                                            "Patricia", "Linda", "Elizabeth", "Susan", "Jennifer", "Thomas"]
                        common_last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", 
                                           "Garcia", "Rodriguez", "Wilson", "Martinez", "Anderson", "Taylor"]
                        fake_first_name = random.choice(common_first_names)
                        fake_last_name = random.choice(common_last_names)
                        fake_name = f"{fake_first_name} {fake_last_name}"
            
            # Generate address components with fallbacks
            district = suburb = postal_town = None
            
            # Get address info (try multiple sources)
            if api_data and 'location' in api_data and not use_custom_generation:
                # Use API data for location if available and not a "use_custom_generation" country
                loc = api_data['location']
                fake_address = f"{loc['street']['number']} {loc['street']['name']}" if 'street' in loc and isinstance(loc['street'], dict) else fake.street_address()
                fake_city = loc.get('city', fake.city())
                fake_state = loc.get('state', getattr(fake, 'state', lambda: fake.administrative_unit())())
                fake_postal = str(loc.get('postcode', getattr(fake, 'postcode', lambda: fake.random_number(digits=5))()))
            else:
                # Generate address components with country-specific street formats and city names
                def generate_street_address(country_code):
                    # North American style
                    def north_american_address():
                        number = random.randint(1, 9999)
                        streets = ["Main St", "Park Ave", "Oak Dr", "Maple Rd", "Washington Blvd", "Cedar Ln", 
                                  "Lake St", "Hill Rd", "River Dr", "Sunset Blvd", "Pine St", "Forest Ave"]
                        return f"{number} {random.choice(streets)}"
                    
                    # UK/Ireland style
                    def uk_address():
                        number = random.randint(1, 150)
                        streets = ["High Street", "Church Road", "Station Road", "Victoria Road", "Green Lane", 
                                  "Mill Lane", "Park Road", "London Road", "School Lane", "King Street", 
                                  "Queen Street", "Manor Road", "York Road", "Church Street", "Windsor Road"]
                        return f"{number} {random.choice(streets)}"
                    
                    # European style
                    def european_address():
                        number = random.randint(1, 150)
                        streets = ["Hauptstraße", "Kirchstraße", "Schulstraße", "Bahnhofstraße", "Avenue des Champs-Élysées", 
                                  "Rue de la Paix", "Via Roma", "Via Nazionale", "Plaza Mayor", "Calle Mayor", 
                                  "Rambla Catalunya", "Kurfürstendamm", "Avenue Louise", "Kalverstraat"]
                        return f"{random.choice(streets)} {number}"
                    
                    # East Asian style
                    def east_asian_address():
                        district = random.randint(1, 15)
                        block = random.randint(1, 50)
                        number = random.randint(1, 50)
                        
                        if country_code == 'jp':
                            return f"{district}-{block}-{number}, Chome"
                        elif country_code in ['kr', 'cn', 'tw']:
                            return f"Block {block}, No. {number}, District {district}"
                        else:
                            return f"No. {number}, Block {block}, District {district}"
                    
                    # Middle Eastern style
                    def middle_eastern_address():
                        streets = ["Al Nahyan", "Al Karama", "Al Mankhool", "Al Rigga", "Al Muraqqabat", 
                                  "Al Khaleej", "Al Wasl", "Al Saffa", "Al Falah", "Al Nahda"]
                        number = random.randint(1, 200)
                        block = random.choice(["A", "B", "C", "D", "E"])
                        
                        return f"Villa {number}, {random.choice(streets)} Street, Block {block}"
                    
                    # Indian subcontinent style
                    def indian_address():
                        number = random.randint(1, 999)
                        sectors = ["Sector", "Phase", "Block", "Colony", "Nagar", "Enclave", "Extension", "Garden"]
                        sector = f"{random.choice(sectors)} {random.randint(1, 20)}"
                        
                        return f"House No. {number}, {sector}"
                    
                    # African style addresses
                    def african_address():
                        # Different styles based on region
                        if country_code == 'et':  # Ethiopia specific
                            plots = ["House", "Villa", "Residence", "Condominium", "Apartment", "Flat"]
                            roads = ["Road", "Street", "Avenue", "Lane", "Way", "Drive", "Marg", "Sefer"]
                            # Ethiopian neighborhoods/areas
                            areas = ["Bole", "Kazanchis", "Piassa", "Arat Kilo", "Sidist Kilo", "Mexico", 
                                   "Gerji", "CMC", "Summit", "Sarbet", "Jemo", "Ayat", "Megenagna", 
                                   "Haya Hulet", "Lebu", "Kality", "Akaki", "Legetafo", "Sululta", "Shiro Meda"]
                            
                            # Ethiopian street naming patterns
                            building_types = ["Building", "Tower", "Plaza", "Center", "Complex"]
                            building = f"{random.choice(building_types)}"
                            
                            # Options for Ethiopian addresses
                            options = [
                                f"{random.choice(plots)} No. {random.randint(100, 9999)}, {random.choice(areas)}",
                                f"{random.choice(areas)}, {random.choice(roads)} {random.randint(1, 50)}",
                                f"{random.choice(areas)}, Behind {random.choice(building)}",
                                f"Kebele {random.randint(1, 30)}, House No. {random.randint(100, 9999)}",
                                f"{random.choice(areas)}, {random.choice(areas)} Road"
                            ]
                            
                            return random.choice(options)
                            
                        elif country_code in ['ke', 'tz', 'ug', 'rw', 'bi']:  # Other East Africa
                            plots = ["Plot", "House", "Residence", "Villa", "Estate"]
                            roads = ["Road", "Street", "Avenue", "Lane", "Way", "Drive"]
                            areas = ["Karen", "Lavington", "Kilimani", "Westlands", "Muthaiga", "Runda", 
                                   "Gigiri", "Nyali", "Mtwapa", "Nakasero", "Kololo", "Ntinda"]
                            
                            plot = f"{random.choice(plots)} {random.randint(100, 9999)}"
                            road = f"{random.choice(areas)} {random.choice(roads)}"
                            
                            return f"{plot}, {road}"
                            
                        elif country_code in ['ng', 'gh', 'sn', 'ci', 'ml', 'bf', 'bj', 'gm']:  # West Africa
                            plots = ["House", "Plot", "Compound", "Block", "No."]
                            roads = ["Road", "Street", "Avenue", "Close", "Way", "Drive"]
                            areas = ["Ikeja", "Lekki", "Victoria Island", "Ikoyi", "Surulere", "Accra Central", 
                                   "East Legon", "Cantonments", "Labone", "Airport Residential"]
                            
                            plot = f"{random.choice(plots)} {random.randint(10, 500)}"
                            road = f"{random.choice(areas)} {random.choice(roads)}"
                            
                            return f"{plot}, {road}"
                            
                        elif country_code in ['za', 'zw', 'zm', 'bw', 'na', 'mz', 'ao', 'ls', 'sz']:  # Southern Africa
                            number = random.randint(1, 999)
                            streets = ["Main Road", "Park Street", "Church Road", "River Lane", "Mountain Drive", 
                                     "Lake View", "Acacia Avenue", "Jacaranda Street", "Baobab Lane", "Mopani Road"]
                            
                            return f"{number} {random.choice(streets)}"
                            
                        elif country_code in ['eg', 'ma', 'dz', 'tn', 'ly', 'sd', 'mr']:  # North Africa
                            number = random.randint(1, 150)
                            streets = ["El Tahrir Street", "El Nasr Road", "Mohammed V Avenue", "Habib Bourguiba Avenue", 
                                     "El Nil Street", "El Gomhuria Street", "Hassan II Avenue", "Sharia El Haram"]
                            
                            return f"{number} {random.choice(streets)}"
                            
                        else:  # Generic African
                            number = random.randint(1, 500)
                            streets = ["Main Road", "Central Avenue", "Independence Street", "Unity Road", 
                                     "Liberation Avenue", "Freedom Street", "Peace Road", "National Way"]
                            
                            return f"{number} {random.choice(streets)}"
                    
                    # Determine appropriate address format based on country/region
                    if country_code in ['us', 'ca', 'mx']:
                        return north_american_address()
                    elif country_code in ['gb', 'uk', 'ie']:
                        return uk_address()
                    elif country_code in ['de', 'fr', 'it', 'es', 'nl', 'be', 'ch', 'at', 'se', 'no', 'dk', 'fi', 'pl']:
                        return european_address()
                    elif country_code in ['jp', 'kr', 'cn', 'tw', 'hk', 'mo', 'vn']:
                        return east_asian_address()
                    elif country_code in ['ae', 'sa', 'qa', 'kw', 'om', 'bh', 'jo', 'lb', 'sy', 'iq', 'ir', 'il']:
                        return middle_eastern_address()
                    elif country_code in ['in', 'pk', 'bd', 'np', 'lk']:
                        return indian_address()
                    elif country_code in ['ke', 'tz', 'ug', 'et', 'ng', 'gh', 'za', 'eg', 'ma', 'cm', 'rw', 'bi',
                                        'zw', 'zm', 'bw', 'na', 'mz', 'ao', 'ls', 'sz', 'sn', 'ci', 'ml', 'bf',
                                        'bj', 'gm', 'dz', 'tn', 'ly', 'sd', 'mr']:
                        return african_address()
                    else:
                        # Default fallback
                        return north_american_address()
                
                # Generate country-specific street address
                fake_address = generate_street_address(country_code)
                
                # Use country-specific cities
                country_cities = {
                    # African countries - major cities by country
                    'ke': ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Nyeri", "Thika", "Malindi", "Kitale", "Garissa"],
                    'tz': ["Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya", "Morogoro", "Tanga", "Zanzibar", "Kigoma", "Mtwara"],
                    'ug': ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja", "Mbale", "Masaka", "Entebbe", "Kasese", "Soroti"],
                    'et': ["Addis Ababa", "Dire Dawa", "Mek'ele", "Gondar", "Adama", "Hawassa", "Bahir Dar", "Jimma", "Dessie", "Jijiga", 
                          "Shashamane", "Bishoftu", "Harar", "Debre Markos", "Sodo", "Arba Minch", "Hosaena", "Nekemte", "Debre Birhan", "Asella"],
                    'ng': ["Lagos", "Kano", "Ibadan", "Abuja", "Port Harcourt", "Benin City", "Kaduna", "Zaria", "Maiduguri", "Jos"],
                    'gh': ["Accra", "Kumasi", "Tamale", "Sekondi-Takoradi", "Ashaiman", "Sunyani", "Cape Coast", "Obuasi", "Tema", "Koforidua"],
                    'za': ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein", "Nelspruit", "Kimberley", "Polokwane", "Pietermaritzburg"],
                    'cm': ["Douala", "Yaoundé", "Bamenda", "Bafoussam", "Garoua", "Maroua", "Ngaoundéré", "Kumba", "Edéa", "Buea"],
                    'eg': ["Cairo", "Alexandria", "Giza", "Shubra El-Kheima", "Port Said", "Suez", "Luxor", "Aswan", "Mansoura", "Tanta"],
                    'ma': ["Casablanca", "Rabat", "Fez", "Marrakesh", "Tangier", "Agadir", "Meknes", "Oujda", "Kenitra", "Tetouan"],
                    
                    # Asian countries
                    'jp': ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Sapporo", "Nagoya", "Kobe", "Fukuoka", "Hiroshima", "Sendai"],
                    'cn': ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Wuhan", "Xi'an", "Tianjin", "Hangzhou", "Chongqing"],
                    'in': ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"],
                    'kr': ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Suwon", "Ulsan", "Seongnam", "Goyang"],
                    'sg': ["Singapore Central", "Woodlands", "Tampines", "Jurong East", "Punggol", "Bedok", "Hougang", "Yishun", "Ang Mo Kio", "Clementi"],
                    'my': ["Kuala Lumpur", "Johor Bahru", "Penang", "Ipoh", "Kuching", "Kota Kinabalu", "Shah Alam", "Melaka", "Alor Setar", "Miri"],
                    
                    # Middle Eastern countries
                    'ae': ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Al Ain", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain", "Khor Fakkan", "Dibba Al-Fujairah"],
                    'sa': ["Riyadh", "Jeddah", "Mecca", "Medina", "Dammam", "Taif", "Tabuk", "Buraidah", "Khamis Mushait", "Abha"],
                    'tr': ["Istanbul", "Ankara", "Izmir", "Bursa", "Adana", "Gaziantep", "Konya", "Antalya", "Kayseri", "Mersin"],
                    'il': ["Jerusalem", "Tel Aviv", "Haifa", "Rishon LeZion", "Petah Tikva", "Ashdod", "Netanya", "Beer Sheva", "Holon", "Bnei Brak"],
                    
                    # European countries
                    'uk': ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool", "Edinburgh", "Bristol", "Leeds", "Sheffield", "Newcastle"],
                    'de': ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Leipzig", "Dortmund", "Essen"],
                    'fr': ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier", "Bordeaux", "Lille"],
                    'it': ["Rome", "Milan", "Naples", "Turin", "Palermo", "Genoa", "Bologna", "Florence", "Catania", "Bari"],
                    'es': ["Madrid", "Barcelona", "Valencia", "Seville", "Zaragoza", "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao"],
                    'ru': ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Nizhny Novgorod", "Kazan", "Chelyabinsk", "Samara", "Rostov-on-Don", "Omsk"],
                    
                    # North American countries
                    'us': ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"],
                    'ca': ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg", "Quebec City", "Hamilton", "Kitchener"],
                    'mx': ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "León", "Juárez", "Zapopan", "Mérida", "Querétaro"],
                    
                    # South American countries
                    'br': ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre"],
                    'ar': ["Buenos Aires", "Córdoba", "Rosario", "Mendoza", "Tucumán", "La Plata", "Mar del Plata", "Salta", "Santa Fe", "San Juan"],
                    'co': ["Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena", "Cúcuta", "Soledad", "Ibagué", "Bucaramanga", "Pereira"],
                    
                    # Oceania
                    'au': ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Gold Coast", "Newcastle", "Canberra", "Wollongong", "Hobart"],
                    'nz': ["Auckland", "Wellington", "Christchurch", "Hamilton", "Tauranga", "Napier-Hastings", "Dunedin", "Palmerston North", "Nelson", "Rotorua"]
                }
                
                # Create a mapping of cities to their regions for geographic consistency
                city_to_region_map = {
                    # USA - major cities mapped to their states
                    'us': {
                        "New York": "New York", 
                        "Los Angeles": "California",
                        "Chicago": "Illinois",
                        "Houston": "Texas",
                        "Phoenix": "Arizona",
                        "Philadelphia": "Pennsylvania",
                        "San Antonio": "Texas",
                        "San Diego": "California",
                        "Dallas": "Texas",
                        "San Jose": "California",
                        "Austin": "Texas",
                        "Jacksonville": "Florida",
                        "Fort Worth": "Texas",
                        "Columbus": "Ohio",
                        "San Francisco": "California",
                        "Charlotte": "North Carolina",
                        "Indianapolis": "Indiana",
                        "Seattle": "Washington",
                        "Denver": "Colorado",
                        "Washington": "District of Columbia"
                    },
                    # UK - major cities mapped to their counties/regions
                    'gb': {
                        "London": "Greater London",
                        "Birmingham": "West Midlands",
                        "Manchester": "Greater Manchester",
                        "Glasgow": "Scotland",
                        "Newcastle": "Tyne and Wear",
                        "Liverpool": "Merseyside",
                        "Nottingham": "Nottinghamshire",
                        "Sheffield": "South Yorkshire",
                        "Bristol": "Bristol",
                        "Belfast": "Northern Ireland",
                        "Leicester": "Leicestershire",
                        "Edinburgh": "Scotland",
                        "Leeds": "West Yorkshire",
                        "Cardiff": "Wales",
                        "Coventry": "West Midlands"
                    },
                    # Nigeria - cities mapped to their states
                    'ng': {
                        "Lagos": "Lagos",
                        "Kano": "Kano",
                        "Ibadan": "Oyo",
                        "Abuja": "Federal Capital Territory",
                        "Port Harcourt": "Rivers",
                        "Benin City": "Edo",
                        "Kaduna": "Kaduna",
                        "Zaria": "Kaduna",
                        "Maiduguri": "Borno",
                        "Jos": "Plateau"
                    },
                    # Kenya - each city mapped to its actual county
                    'ke': {
                        "Nairobi": "Nairobi",
                        "Mombasa": "Mombasa",
                        "Kisumu": "Kisumu",
                        "Nakuru": "Nakuru",
                        "Eldoret": "Uasin Gishu",
                        "Nyeri": "Nyeri",
                        "Thika": "Kiambu",
                        "Malindi": "Kilifi",
                        "Kitale": "Trans-Nzoia",
                        "Garissa": "Garissa"
                    },
                    # Ethiopia - cities mapped to their regions
                    'et': {
                        "Addis Ababa": "Addis Ababa",
                        "Dire Dawa": "Dire Dawa",
                        "Mek'ele": "Tigray",
                        "Gondar": "Amhara",
                        "Adama": "Oromia",
                        "Hawassa": "Sidama",
                        "Bahir Dar": "Amhara",
                        "Jimma": "Oromia",
                        "Dessie": "Amhara",
                        "Jijiga": "Somali",
                        "Shashamane": "Oromia",
                        "Bishoftu": "Oromia",
                        "Harar": "Harari",
                        "Debre Markos": "Amhara",
                        "Sodo": "Southern Nations, Nationalities, and Peoples' Region",
                        "Arba Minch": "Southern Nations, Nationalities, and Peoples' Region",
                        "Hosaena": "Southern Nations, Nationalities, and Peoples' Region",
                        "Nekemte": "Oromia",
                        "Debre Birhan": "Amhara",
                        "Asella": "Oromia"
                    },
                    # Tanzania - cities mapped to their regions
                    'tz': {
                        "Dar es Salaam": "Dar es Salaam",
                        "Mwanza": "Mwanza",
                        "Arusha": "Arusha",
                        "Dodoma": "Dodoma",
                        "Mbeya": "Mbeya",
                        "Morogoro": "Morogoro",
                        "Tanga": "Tanga",
                        "Zanzibar": "Zanzibar",
                        "Kigoma": "Kigoma",
                        "Mtwara": "Mtwara"
                    },
                    # Uganda - cities mapped to their districts
                    'ug': {
                        "Kampala": "Kampala",
                        "Gulu": "Gulu",
                        "Lira": "Lira",
                        "Mbarara": "Mbarara",
                        "Jinja": "Jinja",
                        "Mbale": "Mbale",
                        "Masaka": "Masaka",
                        "Entebbe": "Wakiso",
                        "Kasese": "Kasese",
                        "Soroti": "Soroti"
                    },
                    # India - major cities mapped to their states
                    'in': {
                        "Mumbai": "Maharashtra",
                        "Delhi": "Delhi",
                        "Bangalore": "Karnataka",
                        "Hyderabad": "Telangana",
                        "Chennai": "Tamil Nadu",
                        "Kolkata": "West Bengal",
                        "Ahmedabad": "Gujarat",
                        "Pune": "Maharashtra",
                        "Jaipur": "Rajasthan",
                        "Lucknow": "Uttar Pradesh",
                        "Kanpur": "Uttar Pradesh",
                        "Nagpur": "Maharashtra",
                        "Indore": "Madhya Pradesh",
                        "Thane": "Maharashtra",
                        "Bhopal": "Madhya Pradesh"
                    },
                    # South Africa - cities mapped to their provinces
                    'za': {
                        "Johannesburg": "Gauteng",
                        "Cape Town": "Western Cape",
                        "Durban": "KwaZulu-Natal",
                        "Pretoria": "Gauteng",
                        "Port Elizabeth": "Eastern Cape",
                        "Bloemfontein": "Free State",
                        "Nelspruit": "Mpumalanga",
                        "Kimberley": "Northern Cape",
                        "Polokwane": "Limpopo",
                        "Pietermaritzburg": "KwaZulu-Natal"
                    },
                    # Brazil - major cities mapped to their states
                    'br': {
                        "São Paulo": "São Paulo",
                        "Rio de Janeiro": "Rio de Janeiro",
                        "Brasília": "Distrito Federal",
                        "Salvador": "Bahia",
                        "Fortaleza": "Ceará",
                        "Belo Horizonte": "Minas Gerais",
                        "Manaus": "Amazonas",
                        "Curitiba": "Paraná",
                        "Recife": "Pernambuco",
                        "Porto Alegre": "Rio Grande do Sul"
                    },
                    # Australia - cities mapped to their states/territories
                    'au': {
                        "Sydney": "New South Wales",
                        "Melbourne": "Victoria",
                        "Brisbane": "Queensland",
                        "Perth": "Western Australia",
                        "Adelaide": "South Australia",
                        "Gold Coast": "Queensland",
                        "Newcastle": "New South Wales",
                        "Canberra": "Australian Capital Territory",
                        "Wollongong": "New South Wales",
                        "Hobart": "Tasmania"
                    }
                }
                
                # If country has specific city list, use it, otherwise use Faker's city
                if country_code in country_cities:
                    fake_city = random.choice(country_cities[country_code])
                    
                    # If we have region mapping for this country, set the region based on city
                    if country_code in city_to_region_map and fake_city in city_to_region_map[country_code]:
                        # Use the corresponding region for this city
                        region_for_city = city_to_region_map[country_code][fake_city]
                        # Save for later use when setting state/region
                        city_region_match = region_for_city
                    else:
                        city_region_match = None
                else:
                    fake_city = fake.city()
                    city_region_match = None
                
                # Generate state/region name appropriate to the country
                # Country-specific states/provinces/regions
                country_states = {
                    # USA states
                    'us': ["Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
                          "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
                          "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", 
                          "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
                          "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", 
                          "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
                          "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
                          "Wisconsin", "Wyoming"],
                          
                    # Canadian provinces
                    'ca': ["Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador",
                          "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan",
                          "Northwest Territories", "Nunavut", "Yukon"],
                          
                    # Mexican states
                    'mx': ["Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas",
                          "Chihuahua", "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo",
                          "Jalisco", "México", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca",
                          "Puebla", "Querétaro", "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora",
                          "Tabasco", "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas"],
                          
                    # UK regions
                    'gb': ["England", "Scotland", "Wales", "Northern Ireland", "Greater London", "West Midlands",
                          "North West", "North East", "Yorkshire and the Humber", "East Midlands", "South West",
                          "South East", "East of England"],
                    'uk': ["England", "Scotland", "Wales", "Northern Ireland", "Greater London", "West Midlands",
                          "North West", "North East", "Yorkshire and the Humber", "East Midlands", "South West",
                          "South East", "East of England"],
                          
                    # German states
                    'de': ["Baden-Württemberg", "Bavaria", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hesse",
                          "Lower Saxony", "Mecklenburg-Vorpommern", "North Rhine-Westphalia", "Rhineland-Palatinate",
                          "Saarland", "Saxony", "Saxony-Anhalt", "Schleswig-Holstein", "Thuringia"],
                          
                    # Chinese provinces
                    'cn': ["Anhui", "Fujian", "Gansu", "Guangdong", "Guizhou", "Hainan", "Hebei", "Heilongjiang",
                          "Henan", "Hubei", "Hunan", "Jiangsu", "Jiangxi", "Jilin", "Liaoning", "Qinghai",
                          "Shaanxi", "Shandong", "Shanxi", "Sichuan", "Yunnan", "Zhejiang", "Inner Mongolia",
                          "Guangxi", "Ningxia", "Xinjiang", "Tibet", "Beijing", "Tianjin", "Shanghai", "Chongqing"],
                          
                    # Japanese prefectures
                    'jp': ["Hokkaido", "Aomori", "Iwate", "Miyagi", "Akita", "Yamagata", "Fukushima", "Ibaraki",
                          "Tochigi", "Gunma", "Saitama", "Chiba", "Tokyo", "Kanagawa", "Niigata", "Toyama",
                          "Ishikawa", "Fukui", "Yamanashi", "Nagano", "Gifu", "Shizuoka", "Aichi", "Mie",
                          "Shiga", "Kyoto", "Osaka", "Hyogo", "Nara", "Wakayama", "Tottori", "Shimane",
                          "Okayama", "Hiroshima", "Yamaguchi", "Tokushima", "Kagawa", "Ehime", "Kochi",
                          "Fukuoka", "Saga", "Nagasaki", "Kumamoto", "Oita", "Miyazaki", "Kagoshima", "Okinawa"],
                          
                    # Indian states
                    'in': ["Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
                          "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
                          "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
                          "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"],
                          
                    # Australian states
                    'au': ["New South Wales", "Victoria", "Queensland", "Western Australia", "South Australia", 
                          "Tasmania", "Australian Capital Territory", "Northern Territory"],
                          
                    # Brazilian states
                    'br': ["Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará", "Distrito Federal", "Espírito Santo",
                          "Goiás", "Maranhão", "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba",
                          "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro", "Rio Grande do Norte", "Rio Grande do Sul",
                          "Rondônia", "Roraima", "Santa Catarina", "São Paulo", "Sergipe", "Tocantins"],
                          
                    # South African provinces
                    'za': ["Eastern Cape", "Free State", "Gauteng", "KwaZulu-Natal", "Limpopo", "Mpumalanga",
                          "Northern Cape", "North West", "Western Cape"],
                          
                    # Nigerian states
                    'ng': ["Abia", "Adamawa", "Akwa Ibom", "Anambra", "Bauchi", "Bayelsa", "Benue", "Borno", "Cross River",
                          "Delta", "Ebonyi", "Edo", "Ekiti", "Enugu", "Gombe", "Imo", "Jigawa", "Kaduna", "Kano", "Katsina",
                          "Kebbi", "Kogi", "Kwara", "Lagos", "Nasarawa", "Niger", "Ogun", "Ondo", "Osun", "Oyo", "Plateau",
                          "Rivers", "Sokoto", "Taraba", "Yobe", "Zamfara", "Federal Capital Territory"],
                          
                    # Kenyan counties
                    'ke': ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Uasin Gishu", "Kiambu", "Kilifi", "Machakos", 
                          "Kajiado", "Bungoma", "Kakamega", "Kisii", "Nyeri", "Meru", "Embu", "Garissa", "Kitui",
                          "Makueni", "Turkana", "Homa Bay", "Laikipia", "Nandi", "Trans-Nzoia", "Bomet"],
                          
                    # Ugandan districts
                    'ug': ["Kampala", "Wakiso", "Mukono", "Jinja", "Arua", "Gulu", "Masaka", "Lira", "Mbale", "Mbarara",
                          "Tororo", "Kasese", "Hoima", "Kabale", "Soroti", "Masindi", "Moroto", "Busia", "Entebbe"],
                          
                    # Tanzanian regions
                    'tz': ["Dar es Salaam", "Dodoma", "Arusha", "Mwanza", "Tanga", "Kilimanjaro", "Morogoro", "Zanzibar",
                          "Mbeya", "Iringa", "Kigoma", "Tabora", "Kagera", "Lindi", "Mtwara", "Ruvuma", "Singida"],
                          
                    # Ethiopian regions
                    'et': ["Addis Ababa", "Afar", "Amhara", "Benishangul-Gumuz", "Dire Dawa", "Gambela", "Harari", 
                          "Oromia", "Sidama", "Somali", "Southern Nations, Nationalities, and Peoples' Region", 
                          "Tigray", "South West Ethiopia", 
                          # Specific areas within regions
                          "Bole", "Kirkos", "Yeka", "Akaki Kaliti", "Nefas Silk-Lafto", "Lideta", "Addis Ketema", "Kolfe Keranio", "Gulele", "Arada",
                          "Bahir Dar Zuria", "Dessie Zuria", "Jimma Zone", "East Shewa", "West Shewa", "North Shewa", "South Wollo", "North Wollo",
                          "East Hararghe", "West Hararghe", "Arsi Zone", "Bale Zone", "Illubabor Zone", "Keffa Zone"],
                          
                    # Egyptian governorates
                    'eg': ["Cairo", "Alexandria", "Giza", "Qalyubia", "Gharbia", "Dakahlia", "Sharqia", "Beheira",
                          "Suez", "Aswan", "Qena", "Luxor", "South Sinai", "North Sinai", "Port Said", "Ismailia",
                          "Fayoum", "Beni Suef", "Damietta", "Asyut"],
                          
                    # Morocco regions
                    'ma': ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Tanger-Tétouan-Al Hoceima", "Fès-Meknès",
                          "Marrakech-Safi", "Souss-Massa", "Oriental", "Béni Mellal-Khénifra", "Drâa-Tafilalet",
                          "Guelmim-Oued Noun", "Laâyoune-Sakia El Hamra"]
                }
                
                # First, check if we have a matched region from the city
                if city_region_match:
                    fake_state = city_region_match
                # Otherwise, check if we have specific states/regions for this country
                elif country_code in country_states:
                    fake_state = random.choice(country_states[country_code])
                # Otherwise use Faker's built-in providers if available
                elif hasattr(fake, 'state'):
                    fake_state = fake.state()
                elif hasattr(fake, 'prefecture'):
                    fake_state = fake.prefecture()
                elif hasattr(fake, 'province'):
                    fake_state = fake.province()
                elif hasattr(fake, 'administrative_unit'):
                    fake_state = fake.administrative_unit()
                # Use region-based fallbacks if no specific data is available
                else:
                    # For countries with known city-region mappings, try to use a suitable generic region
                    if country_code in city_to_region_map and fake_city not in city_to_region_map[country_code]:
                        # If we have region mappings but this city isn't in it, pick a region from the existing mappings
                        # This ensures we use real administrative divisions even for unlisted cities
                        regions = list(set(city_to_region_map[country_code].values()))
                        if regions:
                            fake_state = random.choice(regions)
                            # Data quality note: This is a real region but may not be geographically accurate for this city
                        else:
                            # Generate a generic region if no valid regions available
                            if country_code in COUNTRY_TO_REGION:
                                region_name = COUNTRY_TO_REGION[country_code].split('_')[0].lower()
                                if region_name == 'europe':
                                    fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Region'
                                elif region_name == 'asia':
                                    fake_state = random.choice(['North', 'South', 'East', 'West', 'Central']) + ' Province'
                                elif region_name == 'africa':
                                    fake_state = random.choice(['Upper', 'Lower', 'Central', 'Eastern', 'Western']) + ' Region'
                                elif region_name == 'americas':
                                    fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' District'
                                elif region_name == 'oceania':
                                    fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Territory'
                                else:
                                    fake_state = random.choice(['North', 'South', 'East', 'West', 'Central']) + ' Region'
                            else:
                                fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Region'
                    else:
                        # Generate a generic region
                        if country_code in COUNTRY_TO_REGION:
                            region_name = COUNTRY_TO_REGION[country_code].split('_')[0].lower()
                            if region_name == 'europe':
                                fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Region'
                            elif region_name == 'asia':
                                fake_state = random.choice(['North', 'South', 'East', 'West', 'Central']) + ' Province'
                            elif region_name == 'africa':
                                fake_state = random.choice(['Upper', 'Lower', 'Central', 'Eastern', 'Western']) + ' Region'
                            elif region_name == 'americas':
                                fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' District'
                            elif region_name == 'oceania':
                                fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Territory'
                            else:
                                fake_state = random.choice(['North', 'South', 'East', 'West', 'Central']) + ' Region'
                        else:
                            fake_state = random.choice(['Northern', 'Southern', 'Eastern', 'Western', 'Central']) + ' Region'
                
                # Use our enhanced postal code generator for more accurate regional formats
                fake_postal = generate_postal_code(country_code)
                
                # Generate extra address components for specific regions with enhanced region-specific naming
                if country_code in ['gb', 'uk', 'ie']:
                    # UK/Ireland postal towns
                    uk_towns = {
                        'gb': ["Chesterfield", "Coventry", "Derby", "Doncaster", "Gloucester", "Leicester", 
                              "Lincoln", "Nottingham", "Oxford", "Peterborough", "Plymouth", "Preston", 
                              "Southampton", "Stoke-on-Trent", "Wolverhampton", "Canterbury", "Chelmsford",
                              "Exeter", "Lichfield", "Salisbury", "Truro", "Wakefield", "Wells", "Winchester"],
                        'uk': ["Chesterfield", "Coventry", "Derby", "Doncaster", "Gloucester", "Leicester", 
                              "Lincoln", "Nottingham", "Oxford", "Peterborough", "Plymouth", "Preston", 
                              "Southampton", "Stoke-on-Trent", "Wolverhampton", "Canterbury", "Chelmsford",
                              "Exeter", "Lichfield", "Salisbury", "Truro", "Wakefield", "Wells", "Winchester"],
                        'ie': ["Dublin", "Cork", "Limerick", "Galway", "Waterford", "Drogheda", "Dundalk", 
                              "Swords", "Bray", "Navan", "Ennis", "Carlow", "Tralee", "Newbridge", "Kilkenny"]
                    }
                    postal_town = random.choice(uk_towns.get(country_code, uk_towns['gb']))
                
                elif country_code == 'au':
                    # Australia suburbs have specific naming patterns
                    aus_suburbs = [
                        "Bondi", "Surry Hills", "Darlinghurst", "Redfern", "Newtown", "Paddington", "Balmain",
                        "Rozelle", "Leichhardt", "Marrickville", "Coogee", "Randwick", "Maroubra", "Kensington",
                        "Alexandria", "Erskineville", "St Kilda", "South Yarra", "Prahran", "Richmond", "Fitzroy",
                        "Carlton", "Brunswick", "Footscray", "Yarraville", "Williamstown", "Seddon", "Newport",
                        "Moonee Ponds", "Essendon", "Ascot Vale", "Flemington", "Kensington", "North Melbourne",
                        "South Brisbane", "West End", "Paddington", "New Farm", "Teneriffe", "Fortitude Valley",
                        "Spring Hill", "Red Hill", "Kelvin Grove", "Ashgrove", "Auchenflower", "Toowong", "Taringa"
                    ]
                    suburb = random.choice(aus_suburbs)
                
                elif country_code == 'nz':
                    # New Zealand suburbs
                    nz_suburbs = [
                        "Ponsonby", "Grey Lynn", "Parnell", "Newmarket", "Mount Eden", "Kingsland", "Remuera",
                        "Mission Bay", "St Heliers", "Takapuna", "Devonport", "Birkenhead", "Herne Bay", "Epsom",
                        "Greenlane", "Ellerslie", "Mount Wellington", "Mount Albert", "Kelburn", "Thorndon", 
                        "Wadestown", "Karori", "Northland", "Hataitai", "Kilbirnie", "Miramar", "Seatoun", 
                        "Lyall Bay", "Newtown", "Berhampore", "Mount Victoria", "Mount Cook", "Aro Valley"
                    ]
                    suburb = random.choice(nz_suburbs)
                
                elif country_code == 'za':  
                    # South African suburbs
                    za_suburbs = [
                        "Sandton", "Rosebank", "Parkhurst", "Parktown", "Melville", "Greenside", "Emmarentia",
                        "Northcliff", "Linden", "Randburg", "Hyde Park", "Houghton", "Illovo", "Bryanston",
                        "Fourways", "Morningside", "Craighall", "Observatory", "Woodstock", "Gardens",
                        "Tamboerskloof", "Green Point", "Sea Point", "Camps Bay", "Bantry Bay", "Clifton",
                        "Muizenberg", "Kalk Bay", "Hout Bay", "Constantia", "Bishopscourt", "Newlands",
                        "Claremont", "Rondebosch", "Wynberg", "Kenilworth", "Plumstead", "Bergvliet", "Meadowridge"
                    ]
                    suburb = random.choice(za_suburbs)
                
                elif country_code == 'jp':
                    # Japanese wards/districts
                    jp_districts = [
                        "千代田区", "Chiyoda-ku", "中央区", "Chuo-ku", "港区", "Minato-ku", "新宿区", "Shinjuku-ku", 
                        "文京区", "Bunkyo-ku", "台東区", "Taito-ku", "墨田区", "Sumida-ku", "江東区", "Koto-ku", 
                        "品川区", "Shinagawa-ku", "目黒区", "Meguro-ku", "大田区", "Ota-ku", "世田谷区", "Setagaya-ku",
                        "渋谷区", "Shibuya-ku", "中野区", "Nakano-ku", "杉並区", "Suginami-ku", "豊島区", "Toshima-ku",
                        "北区", "Kita-ku", "荒川区", "Arakawa-ku", "板橋区", "Itabashi-ku", "練馬区", "Nerima-ku",
                        "足立区", "Adachi-ku", "葛飾区", "Katsushika-ku", "江戸川区", "Edogawa-ku"
                    ]
                    district = random.choice(jp_districts)
                
                elif country_code == 'kr':
                    # Korean districts (Seoul)
                    kr_districts = [
                        "강남구", "Gangnam-gu", "서초구", "Seocho-gu", "송파구", "Songpa-gu", "강동구", "Gangdong-gu",
                        "마포구", "Mapo-gu", "용산구", "Yongsan-gu", "성동구", "Seongdong-gu", "광진구", "Gwangjin-gu",
                        "중구", "Jung-gu", "종로구", "Jongno-gu", "서대문구", "Seodaemun-gu", "은평구", "Eunpyeong-gu",
                        "동대문구", "Dongdaemun-gu", "중랑구", "Jungnang-gu", "도봉구", "Dobong-gu", "강북구", "Gangbuk-gu",
                        "노원구", "Nowon-gu", "구로구", "Guro-gu", "금천구", "Geumcheon-gu", "영등포구", "Yeongdeungpo-gu",
                        "동작구", "Dongjak-gu", "관악구", "Gwanak-gu", "양천구", "Yangcheon-gu", "강서구", "Gangseo-gu"
                    ]
                    district = random.choice(kr_districts)
                
                elif country_code in ['cn', 'hk', 'tw']:
                    # Chinese districts
                    cn_districts = {
                        'cn': ["朝阳区", "Chaoyang District", "海淀区", "Haidian District", "东城区", "Dongcheng District",
                               "西城区", "Xicheng District", "丰台区", "Fengtai District", "石景山区", "Shijingshan District",
                               "通州区", "Tongzhou District", "昌平区", "Changping District", "大兴区", "Daxing District",
                               "顺义区", "Shunyi District", "房山区", "Fangshan District", "门头沟区", "Mentougou District"],
                        'hk': ["中西区", "Central and Western", "湾仔区", "Wan Chai", "东区", "Eastern", "南区", "Southern",
                               "油尖旺区", "Yau Tsim Mong", "深水埗区", "Sham Shui Po", "九龙城区", "Kowloon City",
                               "黄大仙区", "Wong Tai Sin", "观塘区", "Kwun Tong", "北区", "North", "大埔区", "Tai Po",
                               "沙田区", "Sha Tin", "西贡区", "Sai Kung", "荃湾区", "Tsuen Wan", "屯门区", "Tuen Mun",
                               "元朗区", "Yuen Long", "葵青区", "Kwai Tsing", "离岛区", "Islands"],
                        'tw': ["大安区", "Da'an District", "信义区", "Xinyi District", "中正区", "Zhongzheng District",
                               "中山区", "Zhongshan District", "松山区", "Songshan District", "万华区", "Wanhua District",
                               "文山区", "Wenshan District", "南港区", "Nangang District", "内湖区", "Neihu District",
                               "士林区", "Shilin District", "北投区", "Beitou District", "三重区", "Sanchong District"]
                    }
                    districts = cn_districts.get(country_code, cn_districts['cn'])
                    district = random.choice(districts)
                
                elif country_code == 'in':
                    # Indian localities
                    in_districts = {
                        'delhi': ["Connaught Place", "Karol Bagh", "Chandni Chowk", "Civil Lines", "Defence Colony",
                                 "Greater Kailash", "Hauz Khas", "Lajpat Nagar", "Mayur Vihar", "Pitampura",
                                 "Rohini", "Saket", "Vasant Kunj", "Dwarka", "Paschim Vihar"],
                        'mumbai': ["Andheri", "Bandra", "Colaba", "Dadar", "Juhu", "Khar", "Malad", "Powai",
                                  "Santacruz", "Worli", "Goregaon", "Chembur", "Borivali", "Vile Parle", "Malabar Hill"],
                        'bangalore': ["Koramangala", "Indiranagar", "Jayanagar", "JP Nagar", "Whitefield", "HSR Layout",
                                     "Marathahalli", "Electronic City", "Malleshwaram", "Rajajinagar", "Banashankari"]
                    }
                    all_districts = []
                    for city_districts in in_districts.values():
                        all_districts.extend(city_districts)
                    district = random.choice(all_districts)
                
                elif country_code in ['sg', 'my', 'ph', 'id', 'th']:
                    # Southeast Asian neighborhoods
                    sea_districts = {
                        'sg': ["Ang Mo Kio", "Bedok", "Bishan", "Bukit Batok", "Bukit Merah", "Bukit Panjang",
                              "Bukit Timah", "Clementi", "Geylang", "Hougang", "Jurong East", "Jurong West",
                              "Kallang", "Marine Parade", "Novena", "Pasir Ris", "Punggol", "Queenstown", "Sembawang"],
                        'my': ["Ampang", "Bangsar", "Bukit Bintang", "Cheras", "Damansara", "Desa ParkCity",
                              "Kepong", "Klang", "Mont Kiara", "Petaling Jaya", "Puchong", "Shah Alam", "Subang Jaya"],
                        'ph': ["Makati", "Bonifacio Global City", "Ortigas", "Quezon City", "Alabang", "Pasig",
                              "Mandaluyong", "San Juan", "Pasay", "Parañaque", "Marikina", "Malabon"],
                        'id': ["Menteng", "Kebayoran Baru", "Kemang", "Kuningan", "Sudirman", "Senayan",
                              "Pondok Indah", "Pantai Indah Kapuk", "Kelapa Gading", "Pluit", "Gading Serpong"],
                        'th': ["Sukhumvit", "Silom", "Sathorn", "Asok", "Thonglor", "Phrom Phong", "Ekkamai",
                              "Ratchathewi", "Lat Phrao", "Chatuchak", "Huai Khwang", "Ramkhamhaeng", "Bang Na"]
                    }
                    if country_code in sea_districts:
                        district = random.choice(sea_districts[country_code])
                    else:
                        # Generic Southeast Asian pattern
                        district = random.choice([
                            "Sector", "Block", "Phase", "Area", "Colony", "Extension", "Enclave", "Garden"
                        ]) + " " + str(random.randint(1, 50))
                
                elif country_code in ['ke', 'tz', 'ug', 'ng', 'gh', 'za', 'eg', 'ma']:
                    # African localities/estates/areas
                    african_areas = {
                        'ke': ["Kilimani", "Kileleshwa", "Lavington", "Karen", "Westlands", "Runda", 
                              "Muthaiga", "Kitisuru", "Loresho", "Nyari", "Gigiri", "Parklands", "Ngong", "Langata"],
                        'tz': ["Masaki", "Oyster Bay", "Mikocheni", "Mbezi Beach", "Msasani", 
                              "Upanga", "Kijitonyama", "Sinza", "Kinondoni", "Kariakoo", "Tegeta", "Tabata"],
                        'ug': ["Nakasero", "Kololo", "Bugolobi", "Muyenga", "Naguru", "Ntinda", 
                              "Kiwatule", "Bukoto", "Makindye", "Munyonyo", "Entebbe", "Lubowa"],
                        'ng': ["Ikoyi", "Victoria Island", "Lekki", "Ajah", "Ikeja", "Surulere", 
                              "Yaba", "Maryland", "Magodo", "Gbagada", "Festac", "Apapa", "Opebi", "Jabi", "Gwarinpa"],
                        'gh': ["East Legon", "Cantonments", "Airport Residential", "Labone", "Osu", 
                              "Ridge", "Dzorwulu", "Roman Ridge", "Abelemkpe", "Tesano", "Spintex", "Adjiringanor"],
                        'eg': ["Maadi", "Zamalek", "Heliopolis", "New Cairo", "6th of October", 
                              "Dokki", "Mohandessin", "Nasr City", "Garden City", "Rehab", "Tagamoa"],
                        'ma': ["Anfa", "Hay Hassani", "Gauthier", "Racine", "Maarif", "Bourgogne", 
                              "Les Princesses", "Californie", "Ain Diab", "Val d'Anfa", "Palmier"]
                    }
                    if country_code in african_areas:
                        district = random.choice(african_areas[country_code])
                    else:
                        district = None
            
            # Generate gender and phone
            if api_data and 'gender' in api_data and not use_custom_generation:
                # Use API gender only for non-custom generation countries
                fake_gender = api_data['gender'].title()
            else:
                # Use random gender
                fake_gender = fake.random_element(['Male', 'Female'])
                
            if api_data and 'phone' in api_data and not use_custom_generation:
                # Use API phone only for non-custom generation countries
                fake_phone = api_data['phone']
            else:
                # Use faker to generate a base phone number
                fake_phone = fake.phone_number()
                
            # Format phone with country code and region for area code selection
            fake_phone = format_phone_number(fake_phone, country_code, fake_state)
            
            # Generate email
            if api_data and 'email' in api_data and not use_custom_generation:
                # Use API email only for non-custom generation countries
                fake_email = api_data['email']
            else:
                # Create more realistic email based on name components with country-specific patterns
                
                # Normalize name components for email (remove spaces, hyphens and special characters)
                first_email = re.sub(r'[^a-zA-Z0-9]', '', fake_first_name).lower()
                last_email = re.sub(r'[^a-zA-Z0-9]', '', fake_last_name).lower()
                
                # Different email patterns depending on region/country
                email_patterns = [
                    lambda f, l: f"{f}",                      # first
                    lambda f, l: f"{f}.{l}",                  # first.last
                    lambda f, l: f"{f}_{l}",                  # first_last
                    lambda f, l: f"{f[0]}{l}",                # flast
                    lambda f, l: f"{f}{l[0]}",                # firstl
                    lambda f, l: f"{l}.{f}",                  # last.first
                    lambda f, l: f"{l}{f[0]}",                # lastf
                    lambda f, l: f"{f}{random.randint(1, 999)}"  # first123
                ]
                
                # Weights for different regions
                pattern_weights = {
                    'default': [20, 30, 10, 15, 5, 10, 5, 15],  # Western/default
                    'east_asia': [10, 20, 5, 30, 5, 5, 15, 10], # East Asia (more initials)
                    'south_asia': [15, 25, 5, 20, 10, 5, 5, 15], # South Asia
                    'africa': [25, 20, 5, 10, 10, 10, 5, 15],   # Africa
                    'middle_east': [20, 25, 5, 15, 10, 10, 5, 10], # Middle East
                    'eastern_europe': [15, 25, 15, 10, 5, 15, 5, 10] # Eastern Europe
                }
                
                # Select appropriate region based on country code
                if country_code in ['cn', 'jp', 'kr', 'tw', 'hk', 'mo', 'vn']:
                    region_weight = pattern_weights['east_asia']
                elif country_code in ['in', 'pk', 'bd', 'np', 'lk']:
                    region_weight = pattern_weights['south_asia']
                elif country_code in ['ru', 'ua', 'by', 'pl', 'ro', 'cz', 'hu', 'bg', 'sk', 'rs', 'ba', 'hr']:
                    region_weight = pattern_weights['eastern_europe']
                elif country_code in ['ke', 'tz', 'ug', 'ng', 'gh', 'za', 'eg', 'ma']:
                    region_weight = pattern_weights['africa']
                elif country_code in ['sa', 'ae', 'jo', 'lb', 'sy', 'iq', 'kw', 'qa', 'bh', 'om', 'ye', 'tr', 'il']:
                    region_weight = pattern_weights['middle_east']
                else:
                    region_weight = pattern_weights['default']
                
                # Choose pattern based on weighted probability
                pattern_func = random.choices(email_patterns, weights=region_weight, k=1)[0]
                email_name = pattern_func(first_email, last_email)
                
                # Sometimes add birth year
                if random.random() < 0.3:  # 30% chance
                    birth_year = fake_birthdate.split('-')[0]
                    email_name += random.choice(["", ".", "_"]) + birth_year[-2:]
                
                # Select appropriate email domain for country - expanded with more country-specific domains
                country_domains = {
                    # North America
                    'us': ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com', 'icloud.com', 'msn.com', 'comcast.net', 'verizon.net'],
                    'ca': ['gmail.com', 'yahoo.ca', 'hotmail.com', 'outlook.com', 'icloud.com', 'rogers.com', 'bell.net', 'shaw.ca', 'telus.net'],
                    'mx': ['gmail.com', 'yahoo.com.mx', 'hotmail.com', 'outlook.com', 'prodigy.net.mx', 'live.com.mx'],
                    
                    # Europe
                    'gb': ['gmail.com', 'yahoo.co.uk', 'hotmail.co.uk', 'outlook.com', 'btinternet.com', 'icloud.com', 'sky.com', 'live.co.uk', 'virginmedia.com'],
                    'uk': ['gmail.com', 'yahoo.co.uk', 'hotmail.co.uk', 'outlook.com', 'btinternet.com', 'icloud.com', 'sky.com', 'live.co.uk', 'virginmedia.com'],
                    'de': ['gmail.com', 'yahoo.de', 'hotmail.de', 'web.de', 'gmx.de', 'outlook.de', 't-online.de', 'freenet.de', 'mail.de'],
                    'fr': ['gmail.com', 'yahoo.fr', 'hotmail.fr', 'orange.fr', 'outlook.com', 'free.fr', 'laposte.net', 'sfr.fr', 'wanadoo.fr'],
                    'es': ['gmail.com', 'yahoo.es', 'hotmail.es', 'outlook.com', 'telefonica.es', 'movistar.es', 'correo.es', 'terra.es'],
                    'it': ['gmail.com', 'yahoo.it', 'hotmail.it', 'outlook.com', 'libero.it', 'alice.it', 'tin.it', 'virgilio.it', 'tiscali.it'],
                    'nl': ['gmail.com', 'hotmail.nl', 'outlook.com', 'ziggo.nl', 'live.nl', 'kpn.nl', 'planet.nl', 'xs4all.nl'],
                    'se': ['gmail.com', 'hotmail.se', 'outlook.com', 'telia.com', 'live.se', 'yahoo.se', 'spray.se', 'comhem.se'],
                    'no': ['gmail.com', 'hotmail.no', 'outlook.com', 'online.no', 'telenor.no', 'live.no'],
                    'fi': ['gmail.com', 'hotmail.fi', 'outlook.com', 'kolumbus.fi', 'luukku.com', 'suomi24.fi', 'pp.inet.fi'],
                    'dk': ['gmail.com', 'hotmail.dk', 'outlook.com', 'yahoo.dk', 'mail.dk', 'live.dk'],
                    'pl': ['gmail.com', 'wp.pl', 'onet.pl', 'interia.pl', 'o2.pl', 'gazeta.pl', 'yahoo.pl', 'outlook.com'],
                    'cz': ['gmail.com', 'seznam.cz', 'email.cz', 'volny.cz', 'centrum.cz', 'atlas.cz', 'outlook.com'],
                    'ru': ['gmail.com', 'yandex.ru', 'mail.ru', 'rambler.ru', 'outlook.com', 'inbox.ru', 'list.ru', 'bk.ru', 'ya.ru'],
                    'ua': ['gmail.com', 'ukr.net', 'i.ua', 'meta.ua', 'bigmir.net', 'mail.ru', 'yandex.ru', 'outlook.com'],
                    
                    # Asia Pacific
                    'au': ['gmail.com', 'yahoo.com.au', 'hotmail.com', 'outlook.com', 'bigpond.com', 'optusnet.com.au', 'iinet.net.au', 'icloud.com'],
                    'nz': ['gmail.com', 'yahoo.co.nz', 'hotmail.com', 'outlook.com', 'xtra.co.nz', 'clear.net.nz', 'icloud.com'],
                    'jp': ['gmail.com', 'yahoo.co.jp', 'outlook.jp', 'hotmail.co.jp', 'icloud.com', 'ezweb.ne.jp', 'docomo.ne.jp', 'softbank.ne.jp'],
                    'kr': ['gmail.com', 'naver.com', 'daum.net', 'hanmail.net', 'nate.com', 'yahoo.co.kr', 'outlook.kr'],
                    'cn': ['gmail.com', '163.com', 'qq.com', '126.com', 'outlook.com', 'sina.com', 'sohu.com', '139.com', 'yeah.net'],
                    'hk': ['gmail.com', 'yahoo.com.hk', 'hotmail.com', 'outlook.com', 'netvigator.com', 'icloud.com'],
                    'tw': ['gmail.com', 'yahoo.com.tw', 'hotmail.com', 'outlook.com', 'pchome.com.tw', 'seed.net.tw'],
                    'sg': ['gmail.com', 'yahoo.com.sg', 'hotmail.com', 'outlook.com', 'singnet.com.sg', 'icloud.com'],
                    'in': ['gmail.com', 'yahoo.in', 'hotmail.com', 'outlook.com', 'rediffmail.com', 'indiatimes.com', 'sify.com', 'ymail.com'],
                    'ph': ['gmail.com', 'yahoo.com.ph', 'hotmail.com', 'outlook.com', 'icloud.com', 'mail.com'],
                    'my': ['gmail.com', 'yahoo.com.my', 'hotmail.com', 'outlook.com', 'icloud.com'],
                    'id': ['gmail.com', 'yahoo.co.id', 'hotmail.com', 'outlook.com', 'rocketmail.com'],
                    'th': ['gmail.com', 'yahoo.co.th', 'hotmail.com', 'outlook.com', 'live.com'],
                    
                    # Latin America
                    'br': ['gmail.com', 'yahoo.com.br', 'hotmail.com', 'outlook.com', 'uol.com.br', 'bol.com.br', 'terra.com.br', 'ig.com.br', 'globo.com'],
                    'ar': ['gmail.com', 'yahoo.com.ar', 'hotmail.com', 'outlook.com', 'live.com.ar', 'ciudad.com.ar', 'fibertel.com.ar'],
                    'mx': ['gmail.com', 'yahoo.com.mx', 'hotmail.com', 'outlook.com', 'live.com.mx', 'prodigy.net.mx'],
                    'cl': ['gmail.com', 'yahoo.cl', 'hotmail.com', 'outlook.com', 'live.cl'],
                    'co': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com', 'yahoo.es'],
                    'pe': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'terra.com.pe'],
                    
                    # Middle East & Africa - Enhanced with more regional providers
                    # East Africa
                    'et': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'ethionet.et', 'telecom.net.et', 'edu.et'],
                    'ke': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'safaricom.co.ke', 'ke-africa.com', 'jambo.co.ke'],
                    'tz': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'tz-online.com', 'africaonline.co.tz'],
                    'ug': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'mtn.co.ug', 'africaonline.co.ug'],
                    'rw': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rwandatel.rw', 'mtn.co.rw'],
                    'bi': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'africaonline.bi'],
                    # West and Central Africa
                    'ng': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'ymail.com', 'nigeria-mail.com', 'naijamail.com'],
                    'gh': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'africaonline.com.gh', 'ghana-mail.com'],
                    # North Africa
                    'eg': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'yahoo.com.eg', 'egyptmail.com', 'link.net'],
                    # Southern Africa
                    'za': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'webmail.co.za', 'mweb.co.za', 'vodamail.co.za', 'telkomsa.net'],
                    'sa': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'hotmail.sa', 'yahoo.com.sa'],
                    'ae': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'emirates.net.ae', 'etisalat.ae'],
                    'il': ['gmail.com', 'walla.co.il', 'yahoo.com', 'hotmail.com', 'outlook.com', 'bezeqint.net'],
                    'tr': ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'mynet.com', 'turkcell.com.tr', 'yandex.com.tr']
                }
                
                # Use appropriate domain or default to common ones
                domains = country_domains.get(country_code, ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])
                fake_email = f"{email_name}@{random.choice(domains)}"
            
            # Get address format for the country
            address_format = get_address_format(country_code)
            
            # Get data quality indicator
            quality_emoji, quality_text = get_data_quality(country_code, api_source)
            
            # Build response message - include region in header if available
            region_text = f" ({region_display})" if region_display else ""
            # Start timer before building the full response
            start = time.perf_counter()
            resp = f"""
<b>Fake Info Created Successfully ✅</b>
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
🌍 <b>Country:</b> <code>{fake_country}{region_text}</code> {flag}
🆔 <b>Full Name:</b> <code>{fake_name}</code>
👤 <b>Gender:</b> <code>{fake_gender}</code>
🎂 <b>Age:</b> <code>{age} years</code>
"""
            
            # Add address fields in the correct order for this country
            address_data = {
                'street': fake_address,
                'city': fake_city,
                'state': fake_state,
                'postal_code': fake_postal,
                'suburb': suburb,
                'district': district,
                'postal_town': postal_town
            }
            
            # Use the address format order, only including fields in the format
            for field in address_format['order']:
                if field in address_format['labels']:
                    label = address_format['labels'][field]
                    value = address_data.get(field, "")
                    
                    # Skip optional fields if they're empty or None
                    if value and value != "None" and value != "N/A":
                        resp += f"{label} <code>{value}</code>\n"
                    elif 'optional' not in address_format or field not in address_format['optional']:
                        # For non-optional fields, use placeholder value
                        resp += f"{label} <code>{value if value else 'N/A'}</code>\n"
            
            # Add contact information
            resp += f"📞 <b>Phone Number:</b> <code>{fake_phone}</code>\n"
            resp += f"📧 <b>Email:</b> <code>{fake_email}</code>\n"
            
            # Add data quality indicator
            resp += f"{quality_emoji} <b>Data Quality:</b> <code>{quality_text}</code>\n"

            # Add footer with original query if present
            query_text = f"\n🔍 <b>country :</b> <code>{country_query}</code>" if country_query else ""
            resp += f"""━━━━━━━━━━━━━━{query_text}
━━━━━━━━━━━━━━
[ﾒ] Checked By ➺ <a href='tg://user?id={message.from_user.id}'> {message.from_user.first_name}</a> [ {role} ]
[ﾒ] Dev ➺ ⏤‌‌‌‌ <a href="tg://user?id=7941175119">ᶻⒺ𝓡𝐎</a>
━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━ ━
[ﾒ] T/t ➺ [{time.perf_counter() - start:0.2f} seconds]
"""
            
            await message.reply_text(resp)
            
        except Exception as e:
            import traceback
            await error_log(traceback.format_exc())
            await message.reply_text(f"<b>Error generating fake data: {str(e)}</b>")
            
    except Exception as outer_exception:
        import traceback
        await error_log(traceback.format_exc())
        await message.reply_text("<b>An unexpected error occurred</b>")
