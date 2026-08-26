from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.cache import *
from modules.filter import clean_record
from functions.hidder import block
from functions.misc.utils import render_value, print_record, core_fetch, core_label, whitesearch_fetch, nyx_fetch, whitesearch_records

def fio_search(fullname):
    if block(fullname, 'fio'): return
    if not fullname:
        console.print('[error]Ошибка: введите ФИО[/error]')
        return
    fullname = fullname.strip()
    console.print(f'\n[secondary]Поиск по ФИО:[/secondary] {fullname}\n')
    
    active_apis = [api_num for api_num, cfg in API_CONFIG.items() if cfg.get('is_fio_search', False) and cfg.get('working', True)]
    
    if not active_apis:
        console.print('[error]Нет активных API для поиска по ФИО[/error]')
        return

    results_found = False
    for idx, api_num in enumerate(active_apis, 1):
        cfg = API_CONFIG[api_num]
        label = f'Источник {idx}'
        
        cached_data = load_cache("fio", fullname, api_num)
        data = None
        is_cached = False

        if cached_data:
            data = cached_data
            is_cached = True
        elif cfg.get('hide_source'):
            data, _err = core_fetch(cfg, fullname, search_type='name')
            if data:
                save_cache("fio", fullname, api_num, data)
        else:
            try:
                console.print(f'[secondary]Поиск через {label}...[/secondary]')
                url = cfg['url']
                headers = cfg['headers'].copy()
                payload = cfg['payload'].copy()
                
                if '{query}' in url:
                    url = url.format(query=fullname)
                elif api_num == 7:
                    payload.pop('phone', None)
                    payload['fullname'] = fullname
                elif api_num == 10:
                    payload['field'] = 'fio'
                    payload['value'] = fullname
                elif api_num == 29:
                    payload.pop('phone', None)
                    payload['fio'] = fullname
                elif api_num == 30:
                    payload['type'] = 'name'
                    payload['quest'] = fullname
                elif api_num == 33:
                    payload['type'] = 'name'
                    payload['term'] = fullname
                elif api_num == 38:
                    payload['search'] = fullname
                elif api_num == 42:
                    data, err = whitesearch_fetch(cfg, '/search/fio', {'fio': fullname})
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("fio", fullname, api_num, data)
                elif api_num == 43:
                    data, err = nyx_fetch(cfg, fullname)
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("fio", fullname, api_num, data)
                else:
                    for k, v in payload.items():
                        if v is None: payload[k] = fullname
                        
                if api_num in (42, 43):
                    pass
                else:
                    method = cfg.get('method', 'POST')
                    if method == 'POST':
                        r = requests.post(url, json=payload, headers=headers, timeout=30)
                    else:
                        r = requests.get(url, params=payload, headers=headers, timeout=30)

                    if r.status_code == 200:
                        if api_num == 12:
                            r.encoding = 'utf-8'
                        data = r.json()
                        save_cache("fio", fullname, api_num, data)
                    elif r.status_code == 404:
                        console.print(f'[warning]{label}: Информация не найдена[/warning]')
                        continue
                    else:
                        console.print(f'[warning]{label}: ошибка источника[/warning]')
                        continue
            except Exception:
                console.print(f'[warning]{label}: не удалось подключиться[/warning]')
                continue

        if data:
            try:
                records = []
                if api_num == 41:
                    if isinstance(data, dict):
                        records = [core_label(data)]
                    elif isinstance(data, list):
                        records = [core_label(r) for r in data if isinstance(r, dict)]
                elif api_num == 42:
                    records = whitesearch_records(data)
                elif api_num == 43:
                    text = data.get('text') if isinstance(data, dict) else str(data)
                    if text:
                        records = [{'Результат': text}]
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
                elif isinstance(data, dict) and 'fullname' in data and isinstance(data['fullname'], dict):
                    records = [data['fullname']]
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
            except Exception:
                if not cfg.get('hide_source'):
                    console.print(f'[warning]{label}: ошибка обработки данных[/warning]')
            
    if not results_found:
        console.print('\n[warning]Ни в одном из источников информация не найдена[/warning]')
    