from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import API_CONFIG
from modules.filter import clean_record
from functions.hidder import block
from functions.misc.utils import render_value, print_record

def of_data_search(query=None):
    if not query:
        query = v2i('Введите название, ИНН или ОГРН', f'{USERNAME}@{UUID}').strip()
        if block(query, 'domain'): return
    
    if block(query, 'domain'): return
    if not query:
        return

    console.print(f'\n[secondary]Поиск через OfData:[/secondary] {query}\n')
    
    console.print("[primary]1.[/primary] По названию (Организация/ИП)")
    console.print("[primary]2.[/primary] По ИНН (Организация/ИП)")
    console.print("[primary]3.[/primary] По ИНН (Физлицо/Руководитель)")
    console.print("[primary]4.[/primary] По ОГРН (Инфо)")
    console.print("[primary]5.[/primary] По ОГРН (Проверки)")
    console.print("[primary]6.[/primary] По ФИО учредителя")
    
    choice = v2i('Выберите тип поиска (по умолчанию 1)', f'{USERNAME}@{UUID}').strip()
    
    cfg = API_CONFIG[11]
    url = cfg['url']
    params = {'key': cfg['payload'].get('key')}
    by_type = 'name'
    
    if choice == '3':
        url = "https://api.ofdata.ru/v2/person"
        params['inn'] = query
        by_type = 'inn'
    elif choice == '5':
        url = "https://api.ofdata.ru/v2/inspections"
        params['ogrn'] = query
        by_type = 'ogrn'
    elif choice == '6':
        params.update({'query': query, 'by': 'founder-name', 'obj': 'org'})
        by_type = 'founder-name'
    elif choice == '2':
        console.print("\n[primary]1.[/primary] Юридические лица (org)")
        console.print("[primary]2.[/primary] Индивидуальные предприниматели (ip)")
        obj_choice = v2i('Выберите объект (по умолчанию 1)', f'{USERNAME}@{UUID}').strip()
        obj_type = 'ip' if obj_choice == '2' else 'org'
        params.update({'query': query, 'by': 'inn', 'obj': obj_type})
        by_type = 'inn'
    elif choice == '4':
        params.update({'query': query, 'by': 'ogrn', 'obj': 'org'})
        by_type = 'ogrn'
    else:
        console.print("\n[primary]1.[/primary] Юридические лица (org)")
        console.print("[primary]2.[/primary] Индивидуальные предприниматели (ip)")
        obj_choice = v2i('Выберите объект (по умолчанию 1)', f'{USERNAME}@{UUID}').strip()
        obj_type = 'ip' if obj_choice == '2' else 'org'
        params.update({'query': query, 'by': 'name', 'obj': obj_type})
        by_type = 'name'

    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            data = r.json()
            records = []
            if 'data' in data:
                if isinstance(data['data'], list):
                    records = data['data']
                elif isinstance(data['data'], dict):
                    records = data['data'].get('Записи', [data['data']])
            
            if records:
                console.print(f'[success]Найдено записей: {len(records)}[/success]')
                user_input = v2i('Сколько записей вывести? (Enter = все)', f'{USERNAME}@{UUID}').strip().lower()
                limit = len(records)
                if user_input.isdigit(): limit = int(user_input)
                
                for idx, record in enumerate(records[:limit], 1):
                    record = clean_record(record)
                    if record:
                        print_record(record, title=f"Результат #{idx}")
            else:
                console.print('[warning]Информация не найдена[/warning]')
        else:
            console.print('[error]Ошибка источника[/error]')
    except Exception:
        console.print('[error]Ошибка при запросе[/error]')

    if by_type == 'inn' and API_CONFIG[12].get('working', True):
        console.print(f'\n[secondary]Поиск через дополнительный источник...[/secondary]')
        m_cfg = API_CONFIG[12]
        m_params = m_cfg['payload'].copy()
        m_params['search'] = query
        try:
            mr = requests.get(m_cfg['url'], params=m_params, timeout=30)
            if mr.status_code == 200:
                mr.encoding = 'utf-8'
                m_data = mr.json()
                if m_data.get('status') == 'success' and m_data.get('data'):
                    m_records = m_data['data']
                    console.print(f'[success]Найдено записей (API 12): {len(m_records)}[/success]')
                    for idx, item in enumerate(m_records, 1):
                        fields = item.get('data', {})
                        if isinstance(fields, dict):
                            fields['_source'] = item.get('file', 'Неизвестно')
                            fields = clean_record(fields)
                            if fields:
                                print_record(fields, title=f"Запись #{idx}")
                else:
                    console.print('[warning]Информация не найдена[/warning]')
            else:
                console.print('[error]Ошибка источника[/error]')
        except Exception:
            console.print('[error]Ошибка обработки данных[/error]')