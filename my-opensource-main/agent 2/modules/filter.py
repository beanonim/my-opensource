
METADATA_KEYS = {
    'status', 'query', 'data', 'external', 'success',
    'error', 'message', 'total', 'count', 'page', 'limit',
    'api', 'api_name', 'api_version', 'request_id', 'timestamp',
    'time', 'elapsed', 'cached', 'provider', 'service',
    '_type', 'type', 'ok', 'result', 'response',
}

API_WATERMARKS = {
    'blackeye', 'bigbase', 'deepscan', 'krampus', 'atlas',
    'cryven', 'linkor', 'leakcheck', 'snusbase', 'leakosint',
    'epicapi', 'ofdata', 'mikusearch', 'leaxix', 'htmlweb',
    'emailrep', 'xposedornot', 'rapid', 'numverify', 'ipgeo',
    'skskskakann', 'checkhost', 'rdap', 'ipqualityscore', 'abuseipdb',
    'infinitysearch', 'tracesearch', 'depsearch', 'leakcheckpublic',
    'getscam', 'reviewssite', 'mysmsbox', 'whatsapp', 'telegram',
    'github', 'geeklog', 'dns', 'ipinfo', 'whois', 'gift',
    'funstat', 'combined', 'none', 'null', 'undefined',
    'osint', 'search', 'api', 'depsearch'
}


def clean_record(record):
    if not isinstance(record, dict):
        return record

    cleaned = {}
    for key, value in record.items():
        key_lower = str(key).lower().strip()

        if key_lower in METADATA_KEYS:
            continue

        if key_lower in API_WATERMARKS:
            continue

        if key_lower.startswith('_') and key_lower != '_source':
            continue

        if isinstance(value, str) and value.lower().strip() in ('none', 'null', 'undefined', ''):
            continue

        if isinstance(value, dict):
            cleaned_inner = clean_record(value)
            if cleaned_inner:
                cleaned[key] = cleaned_inner
        elif isinstance(value, list):
            cleaned_list = []
            for item in value:
                if isinstance(item, dict):
                    cleaned_item = clean_record(item)
                    if cleaned_item:
                        cleaned_list.append(cleaned_item)
                elif item is not None and str(item).lower().strip() not in ('none', 'null', ''):
                    cleaned_list.append(item)
            if cleaned_list:
                cleaned[key] = cleaned_list
        else:
            cleaned[key] = value

    return cleaned


def clean_display_data(data):
    if isinstance(data, list):
        return [clean_record(item) for item in data if clean_record(item)]
    elif isinstance(data, dict):
        return clean_record(data)
    return data
