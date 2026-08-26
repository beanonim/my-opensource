from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.filter import clean_record
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import core_fetch, core_label, whitesearch_fetch, nyx_fetch, sanitize_error, whitesearch_fetch, nyx_fetch, whitesearch_records

def snils_search(snils):
    if block(snils, 'snils'): return
    if not snils:
        console.print('[error]Введите номер СНИЛС[/error]')
        return
    snils = snils.strip()
    console.print(f'\n[secondary]Поиск по СНИЛС:[/secondary] {snils}\n')

    found_any = False

    # Query all is_snils_search APIs
    active_apis = [api_num for api_num, cfg in API_CONFIG.items()
                   if cfg.get('is_snils_search', False) and cfg.get('working', True)]

    for api_num in active_apis:
        label = f'API {api_num}'
        data = None
        try:
            if api_num == 41:  # Core
                data, _err = core_fetch(API_CONFIG[api_num], snils, search_type='snils')
            elif api_num == 42:  # WhiteSearch
                data, _err = whitesearch_fetch(API_CONFIG[api_num], '/search/snils', {'snils': snils})
            elif api_num == 43:  # Nyx
                data, _err = nyx_fetch(API_CONFIG[api_num], snils)
            else:
                continue
            if data:
                records = []
                if api_num == 41:
                    records = [core_label(data)]
                elif api_num == 42:
                    from functions.misc.utils import whitesearch_records
                    records = whitesearch_records(data)
                elif api_num == 43:
                    text = data.get('text') if isinstance(data, dict) else str(data)
                    if text:
                        records = [{'Результат': text}]

                for rec in records:
                    rec = clean_record(rec)
                    if rec:
                        found_any = True
                        console.print(f'\n[success]━━━ {label} ━━━[/success]')
                        for k, v in rec.items():
                            if isinstance(v, list):
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                            else:
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
        except Exception as e:
            console.print(f'[dim]{label} ошибка: {sanitize_error(e)}[/dim]')

    # DeepScan (API 38)
    try:
        ds_cfg = API_CONFIG[38]
        ds_payload = ds_cfg['payload'].copy()
        ds_payload['search'] = snils
        ds_resp = requests.post(ds_cfg['url'], json=ds_payload, headers=ds_cfg['headers'], timeout=15)
        if ds_resp.status_code == 200:
            ds_data = ds_resp.json()
            ds_record = _normalize_deepscan(ds_data)
            if ds_record:
                ds_record = clean_record(ds_record)
                if ds_record:
                    found_any = True
                    console.print('\n[success]━━━ API 38 ━━━[/success]')
                    for k, v in ds_record.items():
                        if isinstance(v, list):
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                        else:
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
    except Exception:
        pass

    if not found_any:
        console.print('[warning]Информация не найдена[/warning]')
