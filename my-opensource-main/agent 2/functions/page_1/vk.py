from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.filter import clean_record
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import render_value, print_record, jitler_fetch, whitesearch_fetch, nyx_fetch, sanitize_error, whitesearch_fetch, nyx_fetch, whitesearch_records


def vk_search(vk_id):
    if block(vk_id, 'vk_id'):
        return
    if not vk_id:
        return
    vk_id = vk_id.strip()

    results = []

    def _clean(v):
        if v is None:
            return None
        if hasattr(v, 'text'):
            v = v.text
        return html.unescape(v).strip() if isinstance(v, str) else str(v)

    console.print('[secondary]Поиск... API 1[/secondary]')
    try:
        url = f"https://vk.com/id{vk_id}" if vk_id.isdigit() else f"https://vk.com/{vk_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and len(resp.text) > 2000:
            soup = BeautifulSoup(resp.text, 'html.parser')
            vk_res = {'source': 'API 1', 'full_name': _clean(soup.select_one('.page_name')), 'status': _clean(soup.select_one('.page_status'))}
            city_label = soup.find(string=lambda s: isinstance(s, str) and 'Город' in s)
            if city_label and city_label.parent:
                vk_res['city'] = _clean(city_label.parent.find_next_sibling())
            bdate_label = soup.find(string=lambda s: isinstance(s, str) and 'Дата рождения' in s)
            if bdate_label and bdate_label.parent:
                vk_res['birthday'] = _clean(bdate_label.parent.find_next_sibling())
            if any(v for k, v in vk_res.items() if k != 'source' and v):
                results.append(vk_res)
    except requests.exceptions.SSLError:
        console.print('[dim]vk.com: SSL ошибка[/dim]')
    except requests.exceptions.ConnectionError:
        console.print('[dim]vk.com: нет соединения (DNS/блокировка)[/dim]')
    except requests.exceptions.Timeout:
        console.print('[dim]vk.com: таймаут[/dim]')
    except Exception as e:
        console.print(f'[dim]API 1 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 2[/secondary]')
    vk_tokens = [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ]
    for token in vk_tokens:
        try:
            vk_url = "https://api.vk.com/method/users.get"
            vk_params = {
                "user_ids": vk_id,
                "fields": "bdate,city,country,home_phone,mobile_phone,career,status,followers_count,links",
                "access_token": token,
                "v": "5.131"
            }
            vk_resp = requests.get(vk_url, params=vk_params, timeout=10)
            if vk_resp.status_code == 200:
                vk_data = vk_resp.json()
                if "error" in vk_data:
                    console.print(f'[dim]VK API: {vk_data["error"].get("error_msg", "unknown")}[/dim]')
                    continue
                if "response" in vk_data and vk_data["response"]:
                    user = vk_data["response"][0]
                    results.append({
                            'source': 'API 2',
                            'full_name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                            'birthday': user.get('bdate'),
                            'city': user.get('city', {}).get('title'),
                            'country': user.get('country', {}).get('title'),
                            'phone': f"{user.get('home_phone', '')} {user.get('mobile_phone', '')}".strip() or None,
                            'status': user.get('status'),
                            'followers': user.get('followers_count')
                        })
                    break
        except Exception as e:
            console.print(f'[dim]API 2 ошибка: {sanitize_error(e)}[/dim]')
            continue

    console.print('[secondary]Поиск... API 3[/secondary]')
    try:
        bb_cfg = API_CONFIG[1]
        bb_payload = bb_cfg['payload'].copy()
        bb_payload['search'] = vk_id
        bb_resp = requests.post(bb_cfg['url'], json=bb_payload, headers=bb_cfg['headers'], timeout=15)
        if bb_resp.status_code == 200:
            bb_data = bb_resp.json()
            if bb_data.get('success') == 'ok' and bb_data.get('records'):
                for record in bb_data['records']:
                    base_record = record.get('base_record', [])
                    connections = record.get('connections', [])
                    entry = {'source': 'API 3', 'vk_id': vk_id}
                    for item in base_record:
                        if isinstance(item, list) and len(item) >= 2:
                            key, val = item[0], item[1]
                            if val:
                                entry[key] = val
                    for conn in connections:
                        if conn.get('type') == 'person':
                            fio = conn.get('fio', [])
                            if fio and isinstance(fio, list):
                                for f in fio:
                                    if f.get('value'):
                                        entry['ФИО'] = f['value']
                            bday = conn.get('birthday', [])
                            if bday and isinstance(bday, list):
                                for b in bday:
                                    if b.get('value'):
                                        entry['Дата рождения'] = b['value']
                            social = conn.get('social', [])
                            if social:
                                for s in social:
                                    if s.get('type') == 'vk':
                                        entry['VK ID'] = s.get('id')
                                    elif s.get('type') == 'phone':
                                        entry['Телефон'] = s.get('value') or s.get('phone')
                                    elif s.get('type') == 'email':
                                        entry['Email'] = s.get('value') or s.get('email')
                    if len(entry) > 2:
                        results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 3 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 4[/secondary]')
    try:
        lc_cfg = API_CONFIG[32]
        lc_params = lc_cfg['payload'].copy()
        lc_params['check'] = vk_id
        lc_resp = requests.get(lc_cfg['url'], params=lc_params, headers=lc_cfg['headers'], timeout=15)
        if lc_resp.status_code == 200:
            lc_data = lc_resp.json()
            if lc_data.get('success') and lc_data.get('found', 0) > 0:
                entry = {'source': 'API 4', 'vk_id': vk_id, 'found': lc_data['found'], 'sources': []}
                for src in lc_data.get('sources', []):
                    entry['sources'].append(src.get('name', ''))
                if len(entry) > 2:
                    results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 4 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 5[/secondary]')
    try:
        sb_cfg = API_CONFIG[33]
        sb_payload = sb_cfg['payload'].copy()
        sb_payload['type'] = 'username'
        sb_payload['term'] = vk_id
        sb_resp = requests.post(sb_cfg['url'], json=sb_payload, headers=sb_cfg['headers'], timeout=15)
        if sb_resp.status_code == 200:
            sb_data = sb_resp.json()
            if sb_data.get('results'):
                entry = {'source': 'API 5', 'vk_id': vk_id, 'results': sb_data['results']}
                results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 5 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 6[/secondary]')
    try:
        lo_cfg = API_CONFIG[24]
        lo_payload = lo_cfg['payload'].copy()
        lo_payload['request'] = vk_id
        lo_resp = requests.post(lo_cfg['url'], json=lo_payload, headers=lo_cfg['headers'], timeout=20)
        if lo_resp.status_code == 200:
            lo_data = lo_resp.json()
            if lo_data.get('List'):
                entry = {'source': 'API 6', 'vk_id': vk_id}
                for src_name, records in lo_data['List'].items():
                    if isinstance(records, list):
                        for rec in records:
                            if isinstance(rec, dict):
                                for k, v in rec.items():
                                    if v and k not in entry:
                                        entry[k] = v
                if len(entry) > 2:
                    results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 6 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 7[/secondary]')
    try:
        ts_cfg = API_CONFIG[30]
        ts_params = ts_cfg['payload'].copy()
        ts_params['type'] = 'vk'
        ts_params['quest'] = vk_id
        ts_resp = requests.get(ts_cfg['url'], params=ts_params, headers=ts_cfg['headers'], timeout=15)
        if ts_resp.status_code == 200:
            ts_data = ts_resp.json()
            if ts_data.get('data'):
                entry = {'source': 'API 7', 'vk_id': vk_id}
                for item in ts_data['data']:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if v and k not in entry:
                                entry[k] = v
                if len(entry) > 2:
                    results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 7 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 8[/secondary]')
    try:
        ds_cfg = API_CONFIG[31]
        ds_url = ds_cfg['url'].replace('{query}', requests.utils.quote(vk_id))
        ds_resp = requests.get(ds_url, headers=ds_cfg['headers'], timeout=15)
        if ds_resp.status_code == 200:
            ds_data = ds_resp.json()
            if ds_data.get('data'):
                for item in ds_data['data']:
                    if isinstance(item, dict):
                        entry = {'source': 'API 8', 'vk_id': vk_id}
                        for k, v in item.items():
                            if v:
                                entry[k] = v
                        if len(entry) > 2:
                            results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 8 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 9[/secondary]')
    try:
        be_cfg = API_CONFIG[39]
        be_payload = be_cfg['payload'].copy()
        be_payload['type'] = 'username'
        be_payload['q'] = vk_id
        be_resp = requests.post(be_cfg['url'], json=be_payload, headers=be_cfg['headers'], timeout=15)
        if be_resp.status_code == 200:
            be_data = be_resp.json()
            if be_data.get('results'):
                entry = {'source': 'API 9', 'vk_id': vk_id}
                for item in be_data['results']:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if v and k not in entry:
                                entry[k] = v
                if len(entry) > 2:
                    results.append(entry)
    except Exception as e:
        console.print(f'[dim]API 9 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 10[/secondary]')
    try:
        ds_cfg = API_CONFIG[38]
        ds_payload = ds_cfg['payload'].copy()
        ds_payload['search'] = vk_id
        ds_resp = requests.post(ds_cfg['url'], json=ds_payload, headers=ds_cfg['headers'], timeout=15)
        if ds_resp.status_code == 200:
            ds_data = ds_resp.json()
            ds_record = _normalize_deepscan(ds_data)
            if ds_record:
                ds_record['source'] = 'API 10'
                ds_record['vk_id'] = vk_id
                results.append(ds_record)
    except Exception as e:
        console.print(f'[dim]API 10 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 11[/secondary]')
    try:
        ws_cfg = API_CONFIG[42]
        ws_data, ws_err = whitesearch_fetch(ws_cfg, '/search/vk', {'id': vk_id})
        if ws_data:
            ws_records = whitesearch_records(ws_data)
            for rec in ws_records:
                if isinstance(rec, dict):
                    entry = {'source': 'API 11', 'vk_id': vk_id}
                    for k, v in rec.items():
                        if v and k not in entry:
                            entry[k] = v
                    if len(entry) > 2:
                        results.append(entry)
                elif rec:
                    results.append({'source': 'WhiteSearch', 'vk_id': vk_id, 'data': rec})
    except Exception as e:
        console.print(f'[dim]API 11 ошибка: {sanitize_error(e)}[/dim]')

    console.print('[secondary]Поиск... API 12[/secondary]')
    try:
        nx_cfg = API_CONFIG[43]
        nx_data, nx_err = nyx_fetch(nx_cfg, vk_id)
        if nx_data:
            text = nx_data.get('text') if isinstance(nx_data, dict) else str(nx_data)
            if text:
                results.append({'source': 'API 12', 'vk_id': vk_id, 'Результат': text})
    except Exception as e:
        console.print(f'[dim]API 12 ошибка: {sanitize_error(e)}[/dim]')

    try:
        jit_cfg = API_CONFIG[40]
        jit_data, jit_err = jitler_fetch(jit_cfg, vk_id, search_type='vks')
        if jit_data:
            entries = jit_data if isinstance(jit_data, list) else [jit_data]
            for j in entries:
                if not isinstance(j, dict):
                    continue
                jrec = clean_record(j)
                if not jrec:
                    continue
                console.print('\n[success]━━━ Дополнительная информация ━━━[/success]')
                print_record(jrec)
    except Exception:
        pass

    if results:
        console.print('\n[success]Найдена информация:[/]\n')
        seen = set()
        for entry in results:
            key = (entry.get('source'), entry.get('vk_id'), entry.get('ФИО'), entry.get('Телефон'), entry.get('Email'))
            if key in seen:
                continue
            seen.add(key)
            entry = clean_record(entry)
            if entry:
                print_record(entry, title=f"Источник: {entry.get('source')}")
    else:
        console.print('\n[error]Информация не найдена[/error]')
        console.print('[dim]DNS/блокировка может мешать запросам. Если API токены валидны — включите working: true в modules/api.py для нужных API.[/dim]')