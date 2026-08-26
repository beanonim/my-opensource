from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.cache import *
from modules.filter import clean_record
from functions.page_1.ai_chat import get_ai_answer
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import whitesearch_fetch, nyx_fetch, whitesearch_records

def _print_record(data: dict, title: str | None = None):
    if not data: return
    if title: console.print(f"\n[success]{title}[/success]")
    for key, value in data.items():
        if value is None: continue
        console.print(f"  [success]•[/success] [secondary]{key: <20}[/secondary] {value}")
    console.print()

def ip_search(ip):
    if block(ip, 'ip'): return
    console.print(f'\n[secondary]Поиск информации по IP:[/secondary] {ip}\n')

    all_data = []

    current_idx = 1
    try:
        label = f"Источник {current_idx}"
        cached_ipinfo = load_cache("ip", ip, "ipinfo_io")
        if cached_ipinfo:
            res = cached_ipinfo
            _print_record(res, title=f'Источник: {label} (кэшировано)')
            all_data.append({'source': 'ipinfo.io', 'data': res})
            current_idx += 1
        else:
            console.print(f'[secondary]Поиск через {label}...[/secondary]')
            r1 = requests.get(f'https://ipinfo.io/{ip}/json', timeout=10)
            current_idx += 1
            if r1.status_code == 200:
                d = r1.json()
                res = {'IP': d.get('ip', 'N/A'), 'Host': d.get('hostname', 'N/A'), 'City': d.get('city', 'N/A'), 'Region': d.get('region', 'N/A'), 'Country': d.get('country', 'N/A')}
                if 'org' in d and d['org']: res['Provider'] = ' '.join(d['org'].split(' ')[1:])
                if 'loc' in d: res['Location'] = d['loc']
                save_cache("ip", ip, "ipinfo_io", res)
                _print_record(res, title=f'Источник: {label}')
                all_data.append({'source': 'ipinfo.io', 'data': res})
    except Exception:
        pass

    active_apis = [api_num for api_num, cfg in API_CONFIG.items() if cfg.get('is_ip_search', False) and cfg.get('working', True)]

    for api_num in active_apis:
        cfg = API_CONFIG[api_num]
        label = f"Источник {api_num}"
        current_idx += 1
        
        cached_data = load_cache("ip", ip, api_num)
        data = None
        is_cached = False

        if cached_data:
            data = cached_data
            is_cached = True
        else:
            try:
                console.print(f'[secondary]Поиск через {label}...[/secondary]')
                url = cfg['url']
                if '{query}' in url:
                    url = url.format(query=ip)
                
                headers = cfg['headers'].copy()
                payload = cfg['payload'].copy() if 'payload' in cfg else {}
                
                if api_num == 7:
                    payload.pop('phone', None)
                    payload['ip'] = ip
                elif api_num == 10:
                    payload['field'] = 'ip'
                    payload['value'] = ip
                elif api_num == 25:
                    payload['host'] = ip
                    r = requests.get(url, params=payload, headers=headers, timeout=20)
                    if r.status_code == 200:
                        init_data = r.json()
                        if init_data.get('ok') == 1 and 'request_id' in init_data:
                            request_id = init_data['request_id']
                            result_url = cfg.get('result_url', 'https://check-host.net/check-result')
                            import time
                            for _ in range(10):  
                                time.sleep(1)
                                r_result = requests.get(f'{result_url}/{request_id}', headers=headers, timeout=20)
                                if r_result.status_code == 200:
                                    result_data = r_result.json()
                                    has_results = any(
                                        v is not None and v != [] and not (isinstance(v, list) and len(v) > 0 and v[0] is None)
                                        for v in result_data.values()
                                    )
                                    if has_results:
                                        data = {
                                            'request_id': request_id,
                                            'permanent_link': init_data.get('permanent_link'),
                                            'nodes': init_data.get('nodes'),
                                            'results': result_data
                                        }
                                        save_cache("ip", ip, api_num, data)
                                        break
                            if not data:
                                data = {'error': 'Results not ready after polling'}
                                console.print(f'[warning]{label}: {data["error"]}[/warning]')
                        else:
                            data = {'error': 'Failed to initiate check'}
                            console.print(f'[error]{label}: {data["error"]}[/error]')
                    else:
                        console.print(f'[warning]{label}: ошибка источника[/warning]')
                    continue
                elif api_num == 28:
                    payload['ipAddress'] = ip
                elif api_num == 33:
                    payload['type'] = 'lastip'
                    payload['term'] = ip
                elif api_num == 38:
                    payload['search'] = ip
                elif api_num == 39:
                    url = 'https://blackeyebot.duckdns.org/api/v1/ipinfo'
                    r = requests.get(url, params={'ip': ip}, headers=headers, timeout=15)
                    if r.status_code == 200:
                        data = r.json()
                        save_cache("ip", ip, api_num, data)
                    else:
                        console.print(f'[warning]{label}: ошибка источника[/warning]')
                    continue
                elif api_num == 42:
                    data, err = whitesearch_fetch(cfg, '/search/ip', {'ip': ip})
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("ip", ip, api_num, data)
                elif api_num == 43:
                    data, err = nyx_fetch(cfg, ip)
                    if err:
                        console.print(f'[warning]{label}: {err}[/warning]')
                        continue
                    if data:
                        save_cache("ip", ip, api_num, data)
                else:
                    for k, v in payload.items():
                        if v is None: payload[k] = ip

                if api_num in (42, 43):
                    pass
                else:
                    method = cfg.get('method', 'POST')
                    if method == 'POST':
                        r = requests.post(url, json=payload, headers=headers, timeout=20)
                    else:
                        r = requests.get(url, params=payload, headers=headers, timeout=20)

                    if r.status_code == 200:
                        data = r.json()
                        save_cache("ip", ip, api_num, data)
                    else:
                        console.print(f'[warning]{label}: ошибка источника[/warning]')
                        continue
            except Exception:
                console.print(f'[warning]{label}: не удалось подключиться[/warning]')
                continue

        if data:
            try:
                records = []
                if api_num == 13:
                    leaks = data.get('Leaks', [])
                    services = data.get('Services', [])
                    if leaks or services:
                        res = {}
                        if services:
                            res['Сервисы'] = ", ".join([f"{s.get('port')}/{s.get('type')}" for s in services[:5]])
                        if leaks:
                            res['Утечки'] = ", ".join([l.get('type') for l in leaks[:5]])
                        records = [res]
                elif api_num == 14:
                    if isinstance(data, dict) and 'country' in data:
                        records = [{
                            'Страна': data.get('country', {}).get('name'),
                            'Регион': data.get('region', {}).get('name'),
                            'Город': data.get('city', {}).get('name'),
                            'Таймзона': data.get('city', {}).get('time_zone')
                        }]
                elif api_num == 22:
                    if isinstance(data, dict):
                        record = {}
                        for key, value in data.items():
                            if value is None or value == '':
                                continue
                            if isinstance(value, dict):
                                if key == 'time_zone':
                                    record['Часовой пояс'] = value.get('name', 'N/A')
                                    record['Смещение'] = f"{value.get('offset', 0)}ч"
                                elif key == 'currency':
                                    record['Валюта'] = f"{value.get('name', 'N/A')} ({value.get('symbol', 'N/A')})"
                                else:
                                    record[key] = str(value)
                            else:
                                record[key] = value
                        if record:
                            records = [record]
                elif api_num == 25:
                    if 'results' in data and 'nodes' in data:
                        results = data['results']
                        nodes = data['nodes']
                        records = []
                        for node_id, node_info in nodes.items():
                            node_results = results.get(node_id, [])
                            if node_results and node_results != [None] and node_results != []:
                                location = f"{node_info[1]}, {node_info[2]}" if len(node_info) > 2 else node_info[0]
                                record = {
                                    'Узел': location,
                                    'IP узла': node_info[3] if len(node_info) > 3 else 'N/A',
                                }
                                pings = node_results[0] if isinstance(node_results, list) and node_results else []
                                successful = 0
                                failed = 0
                                times = []
                                for ping in pings:
                                    if isinstance(ping, list) and len(ping) >= 2:
                                        status = ping[0]
                                        time_val = ping[1]
                                        if status == 'OK':
                                            successful += 1
                                            times.append(f"{time_val:.3f}s")
                                        else:
                                            failed += 1
                                if successful > 0 or failed > 0:
                                    record['Успешно'] = successful
                                    record['Ошибки'] = failed
                                    if times:
                                        record['Время отклика'] = ", ".join(times)
                                    records.append(record)
                        if records:
                            if data.get('permanent_link'):
                                records.append({'Подробности': data.get('permanent_link')})
                elif api_num == 26:
                    if isinstance(data, dict):
                        record = {}
                        if 'name' in data:
                            record['Организация'] = data['name']
                        elif 'entities' in data and data['entities']:
                            for entity in data['entities']:
                                if 'vcardArray' in entity:
                                    vcard = entity['vcardArray']
                                    if isinstance(vcard, list) and len(vcard) > 1:
                                        for item in vcard[1]:
                                            if isinstance(item, list) and len(item) > 3:
                                                if item[0] == 'fn':
                                                    record['Организация'] = item[3]
                                                    break
                        if 'handle' in data:
                            record['Handle'] = data['handle']
                        if 'country' in data:
                            record['Страна'] = data['country']
                        if 'events' in data:
                            for event in data['events']:
                                if event.get('eventAction') == 'registration':
                                    record['Регистрация'] = event.get('eventDate', 'N/A')
                                elif event.get('eventAction') == 'last changed':
                                    record['Обновление'] = event.get('eventDate', 'N/A')
                        if 'cidr0_cidrs' in data:
                            cidrs = [c.get('v4prefix') or c.get('v6prefix') for c in data['cidr0_cidrs']]
                            if cidrs:
                                record['CIDR'] = ", ".join(cidrs)
                        if 'status' in data:
                            record['Статус'] = ", ".join(data['status'])
                        if record:
                            records = [record]
                elif api_num == 27:
                    if isinstance(data, dict):
                        record = {}
                        if 'fraud_score' in data:
                            fraud_score = data['fraud_score']
                            if fraud_score >= 75:
                                record['Риск мошенничества'] = f'{fraud_score}/100 (Высокий)'
                            elif fraud_score >= 50:
                                record['Риск мошенничества'] = f'{fraud_score}/100 (Средний)'
                            else:
                                record['Риск мошенничества'] = f'{fraud_score}/100 (Низкий)'
                        flags = []
                        if data.get('proxy'):
                            flags.append('Прокси')
                        if data.get('vpn'):
                            flags.append('VPN')
                        if data.get('tor'):
                            flags.append('Tor')
                        if data.get('active_vpn'):
                            flags.append('Активный VPN')
                        if data.get('active_tor'):
                            flags.append('Активный Tor')
                        if data.get('datacenter'):
                            flags.append('Датацентр')
                        if data.get('bot_status'):
                            flags.append('Бот')
                        if flags:
                            record['Флаги'] = ", ".join(flags)
                        if 'connection_type' in data:
                            record['Тип соединения'] = data['connection_type']
                        if 'ISP' in data:
                            record['ISP'] = data['ISP']
                        if 'ASN' in data:
                            record['ASN'] = data['ASN']
                        if 'country_code' in data:
                            record['Страна'] = data['country_code']
                        if 'city' in data:
                            record['Город'] = data['city']
                        if 'mobile' in data:
                            record['Мобильный'] = 'Да' if data['mobile'] else 'Нет'
                        if record:
                            records = [record]
                elif api_num == 28:
                    if isinstance(data, dict) and 'data' in data:
                        abuse_data = data['data']
                        record = {}
                        if 'abuseConfidenceScore' in abuse_data:
                            score = abuse_data['abuseConfidenceScore']
                            if score >= 75:
                                record['Риск злоупотребления'] = f'{score}% (Высокий)'
                            elif score >= 25:
                                record['Риск злоупотребления'] = f'{score}% (Средний)'
                            else:
                                record['Риск злоупотребления'] = f'{score}% (Низкий)'
                        if 'countryCode' in abuse_data:
                            record['Страна'] = abuse_data['countryCode']
                        if 'isp' in abuse_data:
                            record['ISP'] = abuse_data['isp']
                        if 'usageType' in abuse_data:
                            record['Тип использования'] = abuse_data['usageType']
                        if 'domain' in abuse_data:
                            record['Домен'] = abuse_data['domain']
                        if 'hostnames' in abuse_data and abuse_data['hostnames']:
                            record['Хостнеймы'] = ", ".join(abuse_data['hostnames'][:5])
                        if 'totalReports' in abuse_data:
                            record['Всего репортов'] = abuse_data['totalReports']
                        if 'lastReportedAt' in abuse_data:
                            record['Последний репорт'] = abuse_data['lastReportedAt']
                        if record:
                            records = [record]
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
                elif api_num == 38:
                    ds_record = _normalize_deepscan(data)
                    if ds_record:
                        records = [ds_record]
                elif api_num == 39:
                    if isinstance(data, dict) and data.get('success') and isinstance(data.get('data'), dict):
                        be = data['data']
                        record = {}
                        if be.get('country'): record['Страна'] = be['country']
                        if be.get('countryCode'): record['Код страны'] = be['countryCode']
                        if be.get('regionName'): record['Регион'] = be['regionName']
                        if be.get('city'): record['Город'] = be['city']
                        if be.get('zip'): record['Индекс'] = be['zip']
                        if be.get('isp'): record['ISP'] = be['isp']
                        if be.get('org'): record['Организация'] = be['org']
                        if be.get('as'): record['AS'] = be['as']
                        if be.get('lat') and be.get('lon'): record['Координаты'] = f"{be['lat']}, {be['lon']}"
                        if be.get('timezone'): record['Таймзона'] = be['timezone']
                        if record:
                            records = [record]
                elif api_num == 42:
                    records = whitesearch_records(data)
                elif api_num == 43:
                    text = data.get('text') if isinstance(data, dict) else str(data)
                    if text:
                        records = [{'Результат': text}]
                elif isinstance(data, dict) and 'results' in data and data['results']:
                    records = data['results']
                elif isinstance(data, dict) and 'ip' in data and isinstance(data['ip'], dict):
                    records = [data['ip']]
                elif isinstance(data, list):
                    records = data
                elif isinstance(data, dict):
                    record = {}
                    for key, value in data.items():
                        if value is None or value == '':
                            continue
                        if isinstance(value, (dict, list)):
                            continue
                        record[key] = value
                    if record:
                        records = [record]

                if records:
                    status_text = " (кэшировано)" if is_cached else ""
                    for r_idx, record in enumerate(records, 1):
                        record = clean_record(record)
                        if not record:
                            continue
                        _print_record(record, title=f'{label} - Запись #{r_idx}{status_text}')
                        all_data.append({'source': label, 'data': record})
                else:
                    if not is_cached:
                        console.print(f'[warning]{label}: Информация не найдена[/warning]')
            except Exception:
                console.print(f'[warning]{label}: ошибка обработки данных[/warning]')

    if all_data:
        console.print('\n[secondary]ИИ анализ данных...[/secondary]')
        data_summary = "\n".join([f"{d['source']}: {d['data']}" for d in all_data])
        prompt = f"""Проанализируй следующие данные об IP адресе {ip}:

{data_summary}

Определи:
1. Это реальный пользовательский IP или датацентр/VPN/прокси?
2. Есть ли признаки подозрительной активности?
3. Какова вероятность того, что это обычный человек?

А также дай:
1. Основную инорфмацию об IP.
2. Является ли айпи серверным.
3. Возможный тип устройства.

Ответь кратко и по делу на русском.
А также без всякого форматирования."""
        models_to_try = ['mistral', 'chatgpt', 'voicemos']
        ai_success = False
        for model in models_to_try:
            try:
                ai_response = get_ai_answer(prompt, model_name=model)
                console.print('\n[success]ИИ анализ:[/]\n')
                console.print(ai_response)
                console.print()
                ai_success = True
                break
            except Exception:
                pass
        if not ai_success:
            console.print('[warning]ИИ анализ временно недоступен (провайдер перегружен)[/warning]')