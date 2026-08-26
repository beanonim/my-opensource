from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.cache import *
from modules.filter import clean_record
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import render_value, print_record, whitesearch_fetch, nyx_fetch, whitesearch_records

def vin_search(vin=None):
    if not vin: vin = v2i('Введите VIN-номер или Гос.номер', f'{USERNAME}@{UUID}').strip()
    if block(vin, 'vin'): return
    if not vin: return
    console.print(f'\n[secondary]Поиск по авто (VIN/номер):[/secondary] {vin}\n')
    
    active_apis = [api_num for api_num, cfg in API_CONFIG.items() if cfg.get('is_vin_search', False) and cfg.get('working', True)]
    
    if not active_apis:
        console.print('[error]Нет активных API для поиска по авто[/error]')
        return

    results_found = False
    for idx, api_num in enumerate(active_apis, 1):
        cfg = API_CONFIG[api_num]
        label = f'Источник {idx}'
        
        cached_data = load_cache("vin", vin, api_num)
        data = None
        is_cached = False

        if cached_data:
            data = cached_data
            is_cached = True
        else:
            console.print(f'[secondary]Поиск через {label}...[/secondary]')
            try:
                url = cfg['url']
                headers = cfg['headers'].copy()
                payload = cfg['payload'].copy()
                
                if api_num == 7:
                    payload.pop('phone', None)
                    payload['vin'] = vin
                elif api_num == 10:
                    payload['field'] = 'auto'
                    payload['value'] = vin
                elif api_num == 30:
                    payload['type'] = 'vin'
                    payload['quest'] = vin
                elif api_num == 38:
                    payload['search'] = vin
                elif api_num == 42:
                    data, err = whitesearch_fetch(cfg, '/search/vin', {'vin': vin})
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("vin", vin, api_num, data)
                elif api_num == 43:
                    data, err = nyx_fetch(cfg, vin)
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("vin", vin, api_num, data)
                else:
                    for k, v in payload.items():
                        if v is None: payload[k] = vin
                        
                if api_num in (42, 43):
                    pass
                else:
                    method = cfg.get('method', 'POST')
                    if method == 'POST':
                        r = requests.post(url, json=payload, headers=headers, timeout=30)
                    else:
                        r = requests.get(url, params=payload, headers=headers, timeout=30)

                    if r.status_code == 200:
                        data = r.json()
                        save_cache("vin", vin, api_num, data)
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
            records = []
            if api_num == 10:
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
            elif api_num == 42:
                records = whitesearch_records(data)
            elif api_num == 43:
                text = data.get('text') if isinstance(data, dict) else str(data)
                if text:
                    records = [{'Результат': text}]
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
            elif isinstance(data, dict) and 'results' in data and data['results']:
                records = data['results']
            elif api_num == 38:
                ds_record = _normalize_deepscan(data)
                if ds_record:
                    records = [ds_record]
            elif isinstance(data, dict) and 'vin' in data and isinstance(data['vin'], dict):
                records = [data['vin']]
            elif isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = [data]

            if records:
                results_found = True
                status_text = " (кэшировано)" if is_cached else ""
                console.print(f'[success]Найдено в {label}{status_text}:[/success]')
                for r_idx, record in enumerate(records, 1):
                    record = clean_record(record)
                    if record:
                        print_record(record, title=f'{label} - Запись #{r_idx}')
            else:
                if not is_cached:
                    console.print(f'[warning]{label}: Информация не найдена[/warning]')
            
    if not results_found:
        console.print('\n[warning]Ни в одном из источников информация не найдена[/warning]')
    