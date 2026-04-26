CONTINENTS = {
    'Europe': [
        'AL', 'AD', 'AT', 'BY', 'BE', 'BA', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE',
        'FI', 'FR', 'DE', 'GR', 'HU', 'IS', 'IE', 'IT', 'XK', 'LV', 'LI', 'LT',
        'LU', 'MT', 'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'RU',
        'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'UA', 'GB', 'VA',
        # Territories
        'FO', 'GI', 'GG', 'IM', 'JE', 'SJ', 'XR',
    ],
    'Asia': [
        'AF', 'AM', 'AZ', 'BH', 'BD', 'BT', 'BN', 'KH', 'CN', 'GE', 'IN', 'ID',
        'IR', 'IQ', 'IL', 'JP', 'JO', 'KZ', 'KW', 'KG', 'LA', 'LB', 'MY', 'MV',
        'MN', 'MM', 'NP', 'KP', 'OM', 'PK', 'PS', 'PH', 'QA', 'SA', 'SG', 'KR',
        'LK', 'SY', 'TW', 'TJ', 'TH', 'TL', 'TR', 'TM', 'AE', 'UZ', 'VN', 'YE',
        # Territories
        'HK', 'MO', 'XG', 'XW',
    ],
    'Africa': [
        'DZ', 'AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG',
        'CD', 'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'CI',
        'KE', 'LS', 'LR', 'LY', 'MG', 'MW', 'ML', 'MR', 'MU', 'MA', 'MZ', 'NA',
        'NE', 'NG', 'RW', 'ST', 'SN', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ',
        'TG', 'TN', 'UG', 'ZM', 'ZW',
        # Territories
        'RE', 'YT', 'SH', 'SC', 'CX', 'FK',
    ],
    'North America': [
        'AG', 'BS', 'BB', 'BZ', 'CA', 'CR', 'CU', 'DM', 'DO', 'SV', 'GD', 'GT',
        'HT', 'HN', 'JM', 'MX', 'NI', 'PA', 'KN', 'LC', 'VC', 'TT', 'US',
        # Territories
        'AI', 'AW', 'BM', 'BQ', 'VG', 'KY', 'CW', 'GL', 'GP', 'GU', 'MQ', 'MS',
        'MP', 'PR', 'BL', 'MF', 'PM', 'SX', 'TC', 'VI',
    ],
    'South America': [
        'AR', 'BO', 'BR', 'CL', 'CO', 'EC', 'GY', 'PY', 'PE', 'SR', 'UY', 'VE',
        # Territories
        'GF',
    ],
    'Oceania': [
        'AU', 'FJ', 'KI', 'MH', 'FM', 'NR', 'NZ', 'PW', 'PG', 'WS', 'SB', 'TO',
        'TV', 'VU',
        # Territories
        'AS', 'CK', 'PF', 'NU', 'NF', 'PN', 'WF', 'NC',
    ],
}


def group_countries_by_continent(countries):
    code_to_continent = {
        code: continent
        for continent, codes in CONTINENTS.items()
        for code in codes
    }

    grouped = {}
    for country in countries:
        code = country.code.upper() if country.code and country.code != 'nan' else 'NA'
        if code not in code_to_continent:
            continue
        continent = code_to_continent[code]
        grouped.setdefault(continent, []).append(country)
    return grouped
