from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.cache import *
from modules.filter import clean_record
from functions.hidder import block
from functions.misc.utils import render_value, print_record, core_fetch, core_label, whitesearch_fetch, nyx_fetch, whitesearch_records

EMAIL_SEARCH_APIS = [1, 24, 30, 41, 42, 43]

def _sanitize_error(e):
    msg = str(e)
    msg = re.sub(r'https?://[^\s\'\"\)]+', '[скрыто]', msg)
    msg = re.sub(r'token=[^\s&\"\']+', 'token=[скрыто]', msg)
    msg = re.sub(r'key=[^\s&\"\']+', 'key=[скрыто]', msg)
    msg = re.sub(r'api[_-]?key=[^\s&\"\']+', 'api_key=[скрыто]', msg)
    msg = re.sub(r'\{[^}]*\}', '[скрыто]', msg)
    return msg

def email_search(email):
    if not email:
        console.print('[error]Ошибка: введите email[/error]')
        return
    
    email = email.strip()
    console.print(f'\n[secondary]Поиск информации по email:[/secondary] {email}\n')

    if block(email, 'email'):
        input()
        return
    
    active_apis = [api_num for api_num in EMAIL_SEARCH_APIS if API_CONFIG.get(api_num, {}).get('working', False)]
    
    if not active_apis:
        console.print('[error]Нет активных API для поиска по email[/error]')
        return

    results_found = False
    for idx, api_num in enumerate(active_apis, 1):
        cfg = API_CONFIG[api_num]
        label = f'Источник {idx}'
        
        cached_data = load_cache("email", email, api_num)
        data = None
        is_cached = False

        if cached_data:
            data = cached_data
            is_cached = True
        elif cfg.get('hide_source'):
            data, _err = core_fetch(cfg, email, search_type='email')
            if data:
                save_cache("email", email, api_num, data)
        else:
            console.print(f'[secondary]Поиск через {label}...[/secondary]')
            try:
                url = cfg['url']
                if '{query}' in url:
                    url = url.format(query=email)
                
                headers = cfg['headers'].copy()
                payload = cfg['payload'].copy() if 'payload' in cfg else {}
                
                if api_num == 1:
                    payload['search'] = email
                elif api_num == 24:
                    payload['request'] = email
                elif api_num == 30:
                    payload['type'] = 'email'
                    payload['quest'] = email
                elif api_num == 29:
                    payload.pop('phone', None)
                    payload['email'] = email
                elif api_num == 32:
                    payload['check'] = email
                elif api_num == 33:
                    payload['type'] = 'email'
                    payload['term'] = email
                elif api_num == 38:
                    payload['search'] = email
                elif api_num == 42:
                    data, err = whitesearch_fetch(cfg, '/search/email', {'email': email})
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("email", email, api_num, data)
                elif api_num == 43:
                    data, err = nyx_fetch(cfg, email)
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("email", email, api_num, data)
                else:
                    for k, v in payload.items():
                        if v is None: payload[k] = email
                
                if api_num in (42, 43):
                    pass
                else:
                    method = cfg.get('method', 'POST')
                    if method == 'POST':
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                    else:
                        p_clean = {k: v for k, v in payload.items() if v is not None}
                        response = requests.get(url, params=p_clean, headers=headers, timeout=30)
                    
                    if response.status_code == 200:
                        if api_num == 12:
                            response.encoding = 'utf-8'
                        data = response.json()
                        save_cache("email", email, api_num, data)
                    elif response.status_code == 404:
                        console.print(f'[warning]{label}: Информация не найдена[/warning]')
                        continue
                    else:
                        console.print(f'[warning]{label}: ошибка источника[/warning]')
                        continue
            except Exception:
                console.print(f'[warning]{label}: не удалось подключиться[/warning]')
                continue

        if data:
            records = []
            
            if api_num == 41:
                if isinstance(data, dict):
                    records = [core_label(data)]
                elif isinstance(data, list):
                    records = [core_label(r) for r in data if isinstance(r, dict)]
            elif api_num == 1:
                if isinstance(data, dict) and 'records' in data:
                    recs = data['records']
                    if isinstance(recs, dict):
                        recs = list(recs.values())
                    if isinstance(recs, list):
                        for rec in recs:
                            if isinstance(rec, dict) and 'base_record' in rec:
                                base = rec['base_record']
                                if isinstance(base, list):
                                    for item in base:
                                        if isinstance(item, list) and len(item) == 2:
                                            rec[str(item[0])] = item[1]
                                        elif isinstance(item, dict) and '1' in item and '2' in item:
                                            rec[str(item['1'])] = item['2']
                                elif isinstance(base, dict):
                                    for item in base.values():
                                        if isinstance(item, list) and len(item) == 2:
                                            rec[str(item[0])] = item[1]
                                        elif isinstance(item, dict) and '1' in item and '2' in item:
                                            rec[str(item['1'])] = item['2']
                            records.append(rec)
            elif api_num == 24:
                if isinstance(data, dict):
                    if 'list' in data and isinstance(data['list'], dict):
                        for base_name, base_data in data['list'].items():
                            if isinstance(base_data, dict) and 'Data' in base_data:
                                items = base_data['Data']
                                if isinstance(items, list):
                                    for item in items:
                                        if isinstance(item, dict) and item:
                                            item['_source'] = base_name
                                            records.append(item)
                    elif 'Data' in data and isinstance(data['Data'], list):
                        records.extend([r for r in data['Data'] if r])
            elif api_num == 30:
                if isinstance(data, dict) and 'results' in data and data['results']:
                    records = data['results']
            elif api_num == 42:
                records = whitesearch_records(data)
            elif api_num == 43:
                text = data.get('text') if isinstance(data, dict) else str(data)
                if text:
                    records = [{'Результат': text}]
            elif api_num == 32:
                if isinstance(data, dict) and data.get('success') and data.get('sources'):
                    for s in data['sources']:
                        records.append({
                            'Источник утечки': s.get('name', '?'),
                            'Дата': s.get('date', 'неизвестна'),
                        })
            elif api_num == 16:
                records = [{
                    'Репутация': data.get('reputation'),
                    'Подозрительный': 'Да' if data.get('suspicious') else 'Нет',
                    'Черный список': 'Да' if data.get('blacklisted') else 'Нет',
                    'Первое упоминание': data.get('details', {}).get('first_seen')
                }]
            elif api_num == 17:
                if 'breaches' in data:
                    breaches = data['breaches'][0] if isinstance(data['breaches'], list) and data['breaches'] else []
                    records = [{'Утечки': breaches}]
            elif api_num == 18:
                val = data.get('validations', {})
                records = [{
                    'Синтаксис': 'Ок' if val.get('syntax') else 'Ошибка',
                    'Домен': 'Да' if val.get('domain_exists') else 'Нет',
                    'MX записи': 'Да' if val.get('mx_records') else 'Нет',
                    'Почтовый ящик': 'Да' if val.get('mailbox_exists') else 'Нет',
                    'Рейтинг': data.get('score')
                }]
            elif api_num == 10:
                if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                    for coll in data['data']:
                        coll_name = coll.get('collection', 'Unknown')
                        if 'documents' in coll and isinstance(coll['documents'], list):
                            for doc in coll['documents']:
                                if isinstance(doc, dict):
                                    doc['_source'] = coll_name
                                    records.append(doc)
                elif isinstance(data, dict) and 'results' in data and data['results']:
                    records = data['results']
            elif api_num == 13:
                if isinstance(data, dict) and 'List' in data and isinstance(data['List'], dict):
                    for db_name, db_info in data['List'].items():
                        if isinstance(db_info, dict) and 'Data' in db_info and isinstance(db_info['Data'], list):
                            for doc in db_info['Data']:
                                if isinstance(doc, dict):
                                    doc['_source_database'] = db_name
                                    if 'InfoLeak' in db_info:
                                        doc['_info_leak'] = db_info['InfoLeak']
                                    records.append(doc)
            elif api_num == 12:
                if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                    for item in data['data']:
                        fields = item.get('data', {})
                        if isinstance(fields, dict):
                            fields['_source'] = item.get('file', 'Неизвестно')
                            records.append(fields)
            elif isinstance(data, dict) and 'results' in data and data['results']:
                records = data['results']
            elif isinstance(data, dict) and 'email' in data and isinstance(data['email'], dict):
                records = [data['email']]
            elif api_num == 38:
                from functions.page_1.phone import _normalize_deepscan
                ds_record = _normalize_deepscan(data)
                if ds_record:
                    records = [ds_record]
            elif isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]
            
            if records:
                results_found = True
                status_text = " (кэшировано)" if is_cached else ""
                if not cfg.get('hide_source'):
                    console.print(f'[success]Найдено в {label}{status_text}:[/success]')
                for r_idx, record in enumerate(records, 1):
                    record = clean_record(record)
                    if record:
                        if cfg.get('hide_source'):
                            print_record(record, title=f'Запись #{r_idx}')
                        else:
                            print_record(record, title=f'{label} - Запись #{r_idx}')
            else:
                if not is_cached and not cfg.get('hide_source'):
                    console.print(f'[warning]{label}: Информация не найдена[/warning]')
    
    if not results_found:
        console.print('\n[warning]Ни в одном из источников информация не найдена[/warning]')
