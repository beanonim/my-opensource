from modules.imports import *
from modules.config import *
from modules.theme_manager import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.cache import *
from modules.filter import clean_record, clean_display_data
from functions.page_3.getcontact import GetcontactLookup
from functions.hidder import block
from functions.misc.utils import render_value, print_record, jitler_fetch, core_fetch, whitesearch_fetch, nyx_fetch, whitesearch_records, sanitize_error
from bs4 import BeautifulSoup
import threading


def _normalize_record(item):
    if isinstance(item, dict):
        return {k: v for k, v in item.items() if v is not None}
    return {'value': item}


def _sanitize_error(e):
    msg = str(e)
    msg = re.sub(r'https?://[^\s\'\"\)]+', '[скрыто]', msg)
    msg = re.sub(r'token=[^\s&\"\']+', 'token=[скрыто]', msg)
    msg = re.sub(r'key=[^\s&\"\']+', 'key=[скрыто]', msg)
    msg = re.sub(r'api[_-]?key=[^\s&\"\']+', 'api_key=[скрыто]', msg)
    return msg

def _prepare_api_payload(payload_template: dict, phone: str):
    payload = payload_template.copy()
    for k, v in payload.items():
        if v is None:
            payload[k] = phone
    return payload


def _filter_api1_data(data):
    if not isinstance(data, dict):
        return data
    
    sensitive_fields = {
        'free_request', 'success', 'user', 'login', 
        'api_token', 'subscribe', 'subscribe_queries', 'queries', 
        'balance', 'referral_stats', 'referral_url', 'rate', 'hidden'
    }
    
    filtered = {}
    for key, value in data.items():
        if key not in sensitive_fields:
            filtered[key] = value
    
    return filtered if filtered else None


def _find_deep(data, target_keys, blacklist=None, max_depth=10):
    if max_depth <= 0: return None
    if blacklist is None: blacklist = set()
    
    if isinstance(data, dict):
        for k in target_keys:
            if k in data and data[k] is not None and k not in blacklist:
                val = data[k]
                if str(val).strip().lower() in ('none', ''): continue
                if isinstance(val, (dict, list)):
                    inner_keys = ['value', 'val', '1', '0', 0, 1, 'full', 'content', 'text']
                    res = _find_deep(val, inner_keys, blacklist=blacklist, max_depth=max_depth - 1)
                    if res is not None and not isinstance(res, (dict, list)): return res
                    return res if res else val
                return val
        
        for k, v in data.items():
            if k in blacklist: continue
            if isinstance(v, (dict, list)):
                res = _find_deep(v, target_keys, blacklist=blacklist, max_depth=max_depth - 1)
                if res: return res
                
    elif isinstance(data, list):
        for item in data:
            res = _find_deep(item, target_keys, blacklist=blacklist, max_depth=max_depth - 1)
            if res: return res
            
    return None


def _calculate_age(birthdate):
    if not birthdate or str(birthdate).lower() in ('false', 'none', ''): return None
    try:
        s = str(birthdate).split(' ')[0].split('T')[0]
        for fmt in ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y'):
            try:
                dt = datetime.datetime.strptime(s, fmt)
                today = datetime.date.today()
                age = today.year - dt.year - ((today.month, today.day) < (dt.month, dt.day))
                return age if 0 < age < 120 else None
            except: continue
    except: pass
    return None

def _parse_getscam(phone_number, headers):
    url = f"https://getscam.com/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", class_="top__info-item")
        if not table:
            return None

        target_fields = [
            "Номер", "Язык устройства", "Состояние", "Тип",
            "IP адрес", "Сайт оператора", "Оператор", "Код",
            "Страна", "Город"
        ]

        cells = table.find_all("td")
        parsed_data = {}
        for cell in cells:
            p_tag = cell.find("p", class_="grey")
            span_tag = cell.find("span")
            if p_tag and span_tag:
                title = p_tag.get_text(strip=True)
                value = span_tag.get_text(strip=True)
                if title in target_fields:
                    parsed_data[title] = value

        return parsed_data if parsed_data else None
    except Exception:
        return None


def _parse_reviews_site(phone_number, headers):
    url = f"https://xn---7-elctgilofd3b.xn--p1ai/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        review_headers = soup.find_all("div", class_="review-header")

        reviews_list = []
        for header in review_headers:
            name_tag = header.find("span", class_="review-name")
            date_tag = header.find("span", class_="review-date")
            badge_tag = header.find("div", class_="review-rating-badge")

            name = name_tag.get_text(strip=True) if name_tag else "Аноним"
            date = date_tag.get_text(strip=True) if date_tag else "Не указана"
            badge = badge_tag.get_text(strip=True) if badge_tag else "Без категории"

            text_tag = header.find_next_sibling("p", class_="review-text")
            text = text_tag.get_text(strip=True) if text_tag else None

            reviews_list.append({
                "name": name,
                "date": date,
                "badge": badge,
                "text": text
            })

        return reviews_list if reviews_list else None
    except Exception:
        return None


def _parse_mysmsbox(phone_number, headers):
    url = f"https://mysmsbox.ru/phone-search/{phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        result = {}

        categories_ul = soup.find("ul", class_="blog-tags")
        if categories_ul:
            categories = []
            for li in categories_ul.find_all("li"):
                a_tag = li.find("a")
                badge_tag = li.find("span", class_="badge-for-button")
                if a_tag:
                    cat_name = a_tag.get_text(strip=True)
                    votes = badge_tag.get_text(strip=True) if badge_tag else "0"
                    categories.append(f"{cat_name} ({votes})")
            if categories:
                result["categories"] = ", ".join(categories)

        rating_p = None
        for p in soup.find_all("p"):
            if p.get_text().strip().startswith("Оценки"):
                rating_p = p
                break

        if rating_p:
            result["rating"] = rating_p.get_text(" ", strip=True)

        comments_div = soup.find("div", class_="item-list")
        if comments_div:
            comments = []
            for li in comments_div.find_all("li", class_="comment"):
                comments.append(li.get_text(strip=True))
            if comments:
                result["comments"] = comments

        return result if result else None
    except Exception:
        return None


def _parse_whatsapp(phone_number, headers):
    url = f"https://umnico.com/api/tools/checker?phone={phone_number}"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("exists", False)
        return False
    except Exception:
        return False


def _normalize_deepscan(data):
    if not isinstance(data, dict) or not data.get('ok'):
        return None
    record = {}
    fast = data.get('fast-result', {})
    if isinstance(fast, dict):
        if fast.get('name'):
            record['ФИО'] = fast['name']
        if fast.get('operator'):
            record['Оператор'] = fast['operator']
        if fast.get('region'):
            record['Регион'] = fast['region']
    if data.get('type'):
        record['Тип запроса'] = data['type']
    banks = data.get('banks-result', [])
    if banks:
        record['Банки'] = ', '.join(banks)
    links = data.get('links', [])
    if links:
        record['Ссылки'] = links
    names = data.get('possible-names', [])
    if names:
        record['Возможные имена'] = ', '.join(names)
    full = data.get('full-result', [])
    if full:
        for item in full:
            if isinstance(item, dict):
                for k, v in item.items():
                    if v and k not in record:
                        record[k] = v
    add = data.get('additional-result', {})
    if isinstance(add, dict) and add:
        for k, v in add.items():
            if v:
                record[k] = v
    return record if record else None


def _normalize_phone_record(record, api_num):
    if not isinstance(record, dict):
        return {'Данные': str(record)}

    schema = {
        'ФИО': ['fio', 'full_name', 'fullname', 'ФИО', 'Имя', 'f_i_o', 'name'],
        'Дата рождения': ['birthday', 'birthdate', 'dob', 'Дата рождения', 'born', 'birthdays', 'bday'],
        'Email': ['email', 'mail', 'Почта', 'emails', 'e-mail'],
        'TG ID': ['telegram_id', 'tg_id', 'id', 'uid', 'telegram', 'username'],
        'Город': ['city', 'town', 'village', 'Город', 'Населенный пункт', 'location_city'],
        'Регион': ['region', 'state', 'province', 'Регион', 'Область', 'address_region'],
        'Адрес': ['address', 'street', 'Адрес', 'место жительства', 'address_place', 'addresses'],
        'Работа': ['work', 'job', 'company', 'employer', 'Работа', 'Организация', 'Должность', 'occupation'],
        'Пол': ['gender', 'sex', 'Пол'],
        'Соцсети': ['social', 'profiles', 'vk', 'facebook', 'instagram', 'ok', 'sn', 'links', 'telegram'],
        'Оператор': ['operator', 'carrier', 'service', 'Оператор', 'Связь', 'network'],
    }

    normalized = {}
    blacklist = {'source', 'base_info', 'head', 'connections', 'records', 'dossier', 'base_record', 'results'}
    
    for label, keys in schema.items():
        found_val = _find_deep(record, keys, blacklist=blacklist)
        if found_val and str(found_val).strip().lower() not in ('none', 'false', ''):
             normalized[label] = found_val
        else:
             normalized[label] = None

    if normalized.get('Дата рождения') and str(normalized['Дата рождения']).lower() != 'false':
        age = _calculate_age(normalized['Дата рождения'])
        if age: normalized['Возраст'] = str(age)

    other_data = {}
    tech_keys = {'success', 'status', 'id', 'uuid', 'type', 'search_time', 'time', 'api', 'label'}
    known_keys = set()
    for keys in schema.values(): 
        for k in keys: known_keys.add(k.lower())

    for k, v in record.items():
        if k.lower() not in tech_keys and k.lower() not in known_keys and v is not None:
             if str(v).strip().lower() not in ('none', 'false', ''):
                other_data[k] = v

    if other_data:
        normalized['Дополнительно'] = other_data

    return normalized


def _fetch_api(api_num: int, phone: str, results: dict, stop_event: threading.Event):
    """Выполняет запрос к одному API в отдельном потоке. Записывает результат в results."""
    cfg = API_CONFIG[api_num]
    label = f'Источник'
    
    if stop_event.is_set():
        results[api_num] = {'error': 'Остановлено'}
        return
    
    cached_data = load_cache("phone", phone, api_num)
    if cached_data:
        results[api_num] = {'data': cached_data, 'cached': True}
        return

    if cfg.get('is_async'):
        data, err = jitler_fetch(cfg, phone, search_type='number')
        if err:
            results[api_num] = {'error': err}
        elif data:
            results[api_num] = {'data': data}
            save_cache("phone", phone, api_num, data)
        else:
            results[api_num] = {'empty': True}
        return

    if cfg.get('hide_source'):
        data, _err = core_fetch(cfg, phone, search_type='phone')
        if data:
            results[api_num] = {'data': data}
            save_cache("phone", phone, api_num, data)
        else:
            results[api_num] = {'empty': True}
        return

    if api_num == 42:
        data, err = whitesearch_fetch(cfg, '/search/phone', {'phone': phone})
        if err:
            results[api_num] = {'error': err}
        elif data:
            results[api_num] = {'data': data}
            save_cache("phone", phone, api_num, data)
        else:
            results[api_num] = {'empty': True}
        return

    if api_num == 43:
        data, err = nyx_fetch(cfg, phone)
        if err:
            results[api_num] = {'error': err}
        elif data:
            results[api_num] = {'data': data}
            save_cache("phone", phone, api_num, data)
        else:
            results[api_num] = {'empty': True}
        return

    try:
        url = cfg['url']
        if '{query}' in url:
            url = url.format(query=phone)
        
        payload = _prepare_api_payload(cfg.get('payload', {}), phone)
        
        if api_num == 30:
            payload['type'] = 'phone'
        elif api_num == 32:
            payload['check'] = phone
        elif api_num == 33:
            payload['type'] = 'username'
            payload['term'] = phone
        
        method = cfg.get('method', 'POST')
        post_format = cfg.get('post_format', 'json')
        headers = cfg.get('headers', {}).copy()
        params = {}
        
        if api_num == 1:
            response_data = None
            records_accumulated = []
            api_failed = False
            
            for page_idx in range(3):
                if stop_event.is_set():
                    results[api_num] = {'error': 'Остановлено'}
                    return
                
                page_payload = payload.copy()
                page_payload['page'] = page_idx
                
                if method == 'POST':
                    if post_format == 'form':
                        r = requests.post(url, data=page_payload, headers=headers, params=params, timeout=10)
                    else:
                        r = requests.post(url, json=page_payload, headers=headers, params=params, timeout=10)
                else:
                    p_clean = {k: v for k, v in page_payload.items() if v is not None}
                    r = requests.get(url, params={**p_clean, **params}, headers=headers, timeout=10)
                
                if r.status_code == 429:
                    if page_idx == 0:
                        try:
                            err_data = r.json()
                        except Exception:
                            pass
                        results[api_num] = {'error': 'Cooldown'}
                        api_failed = True
                    break
                
                if r.status_code != 200:
                    if page_idx == 0:
                        results[api_num] = {'error': f'HTTP {r.status_code}'}
                        api_failed = True
                    break
                
                try:
                    page_data = r.json()
                except json.JSONDecodeError:
                    if page_idx == 0:
                        results[api_num] = {'error': 'Невалидный ответ'}
                        api_failed = True
                    break
                
                if r.status_code != 200:
                    if page_idx == 0:
                        results[api_num] = {'error': f'{label}: HTTP {r.status_code}'}
                        api_failed = True
                    break
                
                try:
                    page_data = r.json()
                except json.JSONDecodeError:
                    if page_idx == 0:
                        results[api_num] = {'error': f'{label}: Invalid JSON response'}
                        api_failed = True
                    break
                
                if page_idx == 0:
                    response_data = page_data
                
                if "dossier" in page_data:
                    break
                
                records_in_page = page_data.get('records', [])
                if isinstance(records_in_page, dict):
                    records_in_page = list(records_in_page.values())
                
                if isinstance(records_in_page, list) and records_in_page:
                    records_accumulated.extend(records_in_page)
                
                count_in_page = page_data.get('count_in_page', 50)
                try:
                    count_in_page = int(count_in_page)
                except (ValueError, TypeError):
                    count_in_page = 50
                    
                if "dossier" not in page_data and count_in_page > 0 and len(records_in_page) == count_in_page:
                    pass
                else:
                    break
            
            if api_failed:
                return
            
            if response_data and "dossier" not in response_data:
                response_data['records'] = records_accumulated
        
        else:
            if method == 'POST':
                if post_format == 'form':
                    r = requests.post(url, data=payload, headers=headers, params=params, timeout=10)
                else:
                    r = requests.post(url, json=payload, headers=headers, params=params, timeout=10)
            else:
                p_clean = {k: v for k, v in payload.items() if v is not None}
                r = requests.get(url, params={**p_clean, **params}, headers=headers, timeout=10)

            if r.status_code == 429:
                try:
                    err_data = r.json()
                    results[api_num] = {'error': 'Cooldown'}
                except:
                    results[api_num] = {'error': 'HTTP 429'}
                return

            if r.status_code != 200:
                results[api_num] = {'error': f'HTTP {r.status_code}'}
                return

            if api_num == 12:
                r.encoding = 'utf-8'
            
            try:
                response_data = r.json()
            except json.JSONDecodeError:
                results[api_num] = {'error': 'Невалидный ответ'}
                return
        
        if api_num == 1:
            response_data = _filter_api1_data(response_data)
        
        if api_num == 9:
            if response_data.get('success'):
                response_data = response_data.get('data', {})
                for key, val in response_data.items():
                    if isinstance(val, list) and val:
                        if all(isinstance(x, str) for x in val):
                            response_data[key] = ", ".join(val)
                        elif key == 'telegram':
                            tgs = []
                            for t in val:
                                if isinstance(t, dict):
                                    uname = t.get('username', 'N/A')
                                    tgs.append(f"@{uname} ({t.get('id')})")
                            response_data[key] = ", ".join(tgs)
            else:
                results[api_num] = {'error': response_data.get('error', 'Ошибка API')}
                return
        
        if response_data:
            results[api_num] = {'data': response_data}
            save_cache("phone", phone, api_num, response_data)
        else:
            results[api_num] = {'empty': True}

    except Exception as e:
        results[api_num] = {'error': sanitize_error(e)}


def phone_search(phone: str, silent: bool = False, from_connections: bool = False):
    if not silent:
        console.print(f'\n[secondary]Поиск информации по номеру:[/secondary] {phone}\n')

    if block(phone, 'phone'):
        if not silent:
            input()
        return

    phone_info = None
    try:
        parsed = phonenumbers.parse(phone, None)
        phone_info = {
            'Страна': geocoder.country_name_for_number(parsed, 'ru') or 'Не определена',
            'Регион': geocoder.description_for_number(parsed, 'ru') or 'Не определен',
            'Оператор': carrier.name_for_number(parsed, 'ru') or 'Не определен',
            'Таймзона': ", ".join(timezone.time_zones_for_number(parsed)),
            'Формат': phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        }
    except Exception:
        pass

    results = {}
    emojis = ['🌍', '🌎', '🌏']
    start_time = time.time()
    
    all_phone_apis = [api_num for api_num, cfg in API_CONFIG.items() if cfg.get('is_phone_search', False)]
    active_apis = [api_num for api_num in all_phone_apis if API_CONFIG[api_num].get('working', True)]
    
    total_relevant = len(all_phone_apis)
    all_normalized_records = []
    
    # все апи + парсеры в потоках
    threads = []
    stop_event = threading.Event()

    def _fetch_avito(phone, results, stop_event):
        if stop_event.is_set():
            return
        try:
            page = requests.get('https://mirror.bullshit.agency/search_by_phone/' + phone.replace('+', ''), timeout=10)
            if page.status_code == 200:
                soup = BeautifulSoup(page.text, 'html.parser')
                namesell = soup.find_all('h4')
                nametext = soup.find_all('span')
                avito_data = {}
                if namesell:
                    avito_data['Объявления (Avito)'] = [n.text.strip() for n in namesell if n.text.strip()]
                if nametext:
                    avito_data['Адреса/Даты (Avito)'] = [t.text.strip() for t in nametext if t.text.strip()]
                if avito_data:
                    results[98] = {'data': [avito_data]}
        except Exception:
            pass

    def _fetch_getcontact(phone, results, stop_event):
        if stop_event.is_set():
            return
        try:
            with GetcontactLookup() as lookup:
                gc_res = lookup.search(phone)
                if gc_res:
                    combined_gc = {}
                    if "callerid_aunumber" in gc_res:
                        combined_gc.update(gc_res["callerid_aunumber"])
                    if "centralevents" in gc_res:
                        combined_gc.update(gc_res["centralevents"])
                    if combined_gc:
                        results[99] = {'data': [combined_gc]}
        except Exception:
            pass
    
    # сортируем по скорости, быстрые вперед
    sorted_active = sorted(active_apis, key=lambda a: API_CONFIG[a].get('eta_weight', 5.0))
    
    with Live(Text(""), refresh_per_second=10, console=console, transient=True) as live:
        emoji_index = 0
        for idx, api_num in enumerate(sorted(all_phone_apis), 1):
            cfg = API_CONFIG[api_num]
            label = cfg.get('label', f'API {api_num}')
            
            remaining_apis = sorted(all_phone_apis)[idx-1:]
            eta = int(sum(API_CONFIG[a].get('eta_weight', 5.0) for a in remaining_apis))

            if not cfg.get('working', True):
                results[api_num] = {
                    'disabled': True,
                    'label': label,
                    'message': cfg.get('note', 'API отключено')
                }
                continue

            try:
                live.update(
                    Text(
                        f'{emojis[emoji_index % 3]} Идет поиск... [ETA: {eta} сек] [{idx}/{total_relevant}]',
                        style='secondary'
                    )
                )
                emoji_index += 1

                if api_num in active_apis:
                    t = threading.Thread(target=_fetch_api, args=(api_num, phone, results, stop_event), daemon=True)
                    t.start()
                    threads.append(t)
                    
            except Exception as e:
                results[api_num] = {'error': sanitize_error(e)}
                continue

        t_avito = threading.Thread(target=_fetch_avito, args=(phone, results, stop_event), daemon=True)
        t_avito.start()
        threads.append(t_avito)

        t_gc = threading.Thread(target=_fetch_getcontact, args=(phone, results, stop_event), daemon=True)
        t_gc.start()
        threads.append(t_gc)
        
        # ждем пока все потоки закончат (сек 15 на все)
        for t in threads:
            t.join(timeout=15)
        
        # если первый не ответил - остальным тоже конец
        alive_count = sum(1 for t in threads if t.is_alive())
        
        # если первый упал - остальным тоже надо упасть
        # первый - самый быстрый, если он не ответил - остальным тем более
        if sorted_active:
            first_api = sorted_active[0]
            first_result = results.get(first_api)
            
            if not first_result or 'error' in first_result or 'empty' in first_result:
                # главное апи упало - остальным тоже падать
                stop_event.set()
                if not first_result:
                    results[first_api] = {'error': 'Таймаут'}
                
                # ждем завершения остальных потоков
                for t in threads:
                    t.join(timeout=2)
                
                # остальные тоже помечаем как упавшие
                for api_num in active_apis:
                    if api_num not in results:
                        results[api_num] = {
                            'error': 'Не ответил',
                            'no_response': True
                        }
                    elif 'data' not in results[api_num] and 'error' not in results[api_num] and 'empty' not in results[api_num] and 'disabled' not in results[api_num]:
                        results[api_num] = {
                            'error': 'Не ответил',
                            'no_response': True
                        }

    # хтмл парсеры тоже в потоки
    def _fetch_html_parsers(phone, results, headers):
        try:
            scam_data = _parse_getscam(phone, headers)
            if scam_data:
                results[34] = {'data': scam_data}
        except Exception:
            pass
        try:
            reviews_data = _parse_reviews_site(phone, headers)
            if reviews_data:
                results[35] = {'data': reviews_data}
        except Exception:
            pass
        try:
            smsbox_data = _parse_mysmsbox(phone, headers)
            if smsbox_data:
                results[36] = {'data': smsbox_data}
        except Exception:
            pass
        try:
            whatsapp_exists = _parse_whatsapp(phone, headers)
            if whatsapp_exists is not None:
                results[37] = {'data': {'registered': whatsapp_exists}}
        except Exception:
            pass

    t_html = threading.Thread(target=_fetch_html_parsers, args=(phone, results, {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }), daemon=True)
    t_html.start()

    if phone_info:
        print_record(phone_info, title='Информация о номере')

    total_records = 0
    found = 0

    for api_num in sorted(results.keys()):
        result = results[api_num]
        if 'data' not in result:
            continue
        data = result['data']
        
        if api_num == 12:
            if isinstance(data, dict) and data.get('status') == 'success' and isinstance(data.get('data'), list):
                count = len(data['data'])
                if count > 0:
                    total_records += count
                    found += 1
                else:
                    result['empty'] = True
                    del result['data']
            else:
                if isinstance(data, dict) and data.get('status') == 'error':
                    result['error'] = data.get('message', 'API returned error status')
                    del result['data']
                else:
                    result['empty'] = True
                    del result['data']
            continue

        if api_num == 13:
            count = 0
            if isinstance(data, dict) and 'List' in data and isinstance(data['List'], dict):
                for db_name, db_info in data['List'].items():
                    if isinstance(db_info, dict) and 'Data' in db_info and isinstance(db_info['Data'], list):
                        count += len(db_info['Data'])
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        elif api_num == 10:
            count = 0
            if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                for coll in data['data']:
                    if 'documents' in coll and isinstance(coll['documents'], list):
                        count += len(coll['documents'])
            elif isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
                count = len(data['results'])
            
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 1:
            count = 0
            if isinstance(data, dict) and 'records' in data:
                if isinstance(data['records'], dict) or isinstance(data['records'], list):
                    count = len(data['records'])
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 32:
            count = 0
            if isinstance(data, dict) and data.get('success') and data.get('sources'):
                count = len(data['sources'])
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 34:
            count = 1 if isinstance(data, dict) and data else 0
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 35:
            count = len(data) if isinstance(data, list) and data else 0
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 36:
            count = 1 if isinstance(data, dict) and data else 0
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 37:
            count = 1 if isinstance(data, dict) and 'registered' in data else 0
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 38:
            count = len(data) if isinstance(data, list) else (1 if isinstance(data, dict) and data else 0)
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 39:
            count = 0
            if isinstance(data, dict) and 'data' in data:
                be_data = data['data']
                if isinstance(be_data, dict) and 'blackeye' in be_data:
                    groups = be_data['blackeye'].get('groups', {})
                    for g_name, g_info in groups.items():
                        if isinstance(g_info, dict):
                            count += len(g_info.get('records', []))
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 42:
            count = len(whitesearch_records(data))
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if api_num == 43:
            text = data.get('text') if isinstance(data, dict) else str(data)
            count = 1 if text else 0
            if count > 0:
                total_records += count
                found += 1
            else:
                result['empty'] = True
                del result['data']
            continue

        if isinstance(data, list):
            count = len(data)
        elif isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
            count = len(data['results'])
        else:
            count = 1
        
        if count > 0:
            total_records += count
            found += 1
        else:
            result['empty'] = True
            del result['data']

    if found == 0:
        if not silent:
            console.print('[error]Информация не найдена[/error]')
            for api_num, res in sorted(results.items()):
                if 'error' in res and not API_CONFIG.get(api_num, {}).get('hide_source'):
                    console.print(f'[dim]Дополнительный источник: ошибка запроса[/dim]')
        return None

    if not silent and not from_connections:
        console.print(f'[success]Найдено:[/success] {total_records} результатов')
        while True:
            user_input = v2i(
                'Сколько записей вывести? (Enter = все)',
                f'{USERNAME}@{UUID}'
            ).strip().lower()

            if user_input in ('все', 'all', ''):
                limit = total_records
                break
            else:
                try:
                    limit = int(user_input)
                    if limit > 0:
                        break
                except ValueError:
                    pass
            
            console.print('[warning]Пожалуйста, введите корректное число или просто нажмите Enter для вывода всех записей[/warning]')
    else:
        limit = total_records

    current_count = 0

    for api_num in sorted(results.keys()):
        result = results[api_num]

        if result.get('disabled'):
            if not silent:
                console.print(f'[success]━━━ Источник ━━━[/success]')
                console.print(f'[warning]{result["message"]}[/warning]')
            continue

        if 'error' in result:
            continue

        if 'empty' in result:
            continue

        data = result.get('data')
        if data is None:
            if not silent:
                console.print(f'[success]━━━ Источник ━━━[/success]')
                console.print('[warning]В этом источнике записей не найдено[/warning]')
            continue

        status_text = " (кэшировано)" if result.get('cached') else ""
        if not silent and not API_CONFIG.get(api_num, {}).get('hide_source'):
            if api_num == 99:
                console.print(f'[success]━━━ GETCONTACT{status_text} ━━━[/success]')
            elif api_num == 98:
                console.print(f'[success]━━━ AVITO{status_text} ━━━[/success]')
            else:
                console.print(f'[success]━━━ Источник {api_num}{status_text} ━━━[/success]')

        records = []
        if api_num == 1:
            if isinstance(data, dict):
                recs = data.get('records', [])
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
                
                if not records and data:
                    filtered = _filter_api1_data(data)
                    if filtered:
                        records.append(filtered)
        elif api_num == 15:
            if isinstance(data, dict):
                res = {}
                country = data.get('country', {})
                if isinstance(country, dict):
                    res['Страна'] = country.get('name')
                    res['Город'] = data.get('capital', {}).get('name')
                
                oper_info = data.get('0', {})
                if isinstance(oper_info, dict):
                    res['Оператор'] = f"{oper_info.get('oper')} ({oper_info.get('oper_brand')})"
                    res['Тип'] = "Мобильный" if oper_info.get('mobile') else "Стационарный"
                
                if res:
                    records.append(res)
        
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
        
        elif api_num == 10:
            if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                for coll in data['data']:
                    coll_name = coll.get('collection', 'Unknown')
                    if 'documents' in coll and isinstance(coll['documents'], list):
                        for doc in coll['documents']:
                            if isinstance(doc, dict):
                                doc['_source_collection'] = coll_name
                                records.append(doc)
            elif isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
                 records.extend(data['results'])
        elif api_num == 13:
            if isinstance(data, dict) and 'List' in data and isinstance(data['List'], dict):
                for db_name, db_info in data['List'].items():
                    if isinstance(db_info, dict) and 'Data' in db_info and isinstance(db_info['Data'], list):
                        for doc in db_info['Data']:
                            if isinstance(doc, dict):
                                doc['_source_database'] = db_name
                                records.append(doc)
        elif api_num == 12:
            if isinstance(data, dict) and 'data' in data and isinstance(data['data'], list):
                for item in data['data']:
                    fields = item.get('data', {})
                    if isinstance(fields, dict):
                        fields['_source_database'] = item.get('file', 'Неизвестно')
                        records.append(fields)
        elif api_num == 32:
            if isinstance(data, dict) and data.get('success') and data.get('sources'):
                for s in data['sources']:
                    records.append({
                        'Источник утечки': s.get('name', '?'),
                        'Дата': s.get('date', 'неизвестна'),
                    })
        elif api_num == 39:
            if isinstance(data, dict) and 'data' in data:
                be_data = data['data']
                if isinstance(be_data, dict) and 'blackeye' in be_data:
                    groups = be_data['blackeye'].get('groups', {})
                    for g_name, g_info in groups.items():
                        if isinstance(g_info, dict):
                            for rec in g_info.get('records', []):
                                if isinstance(rec, dict):
                                    rec['_source'] = g_name
                                    records.append(rec)
        elif api_num == 42:
            records = whitesearch_records(data)
        elif api_num == 43:
            text = data.get('text') if isinstance(data, dict) else str(data)
            if text:
                records = [{'Результат': text}]
        elif isinstance(data, dict) and 'results' in data and isinstance(data['results'], list):
            records.extend(data['results'])
        elif isinstance(data, list):
            records.extend(data)
        else:
            records.append(data)

        if not records:
            if not silent:
                console.print('[warning]В этом источнике записей не найдено[/warning]')
            continue

        for record in records:
            if current_count >= limit:
                break

            record = clean_record(record)
            if not record:
                continue

            table_data = _normalize_phone_record(record, api_num)
            all_normalized_records.append(table_data)
            
            if not silent:
                print_record(
                    table_data,
                    title=f'Запись #{current_count}'
                )
            current_count += 1

    if all_normalized_records:
        if not silent:
            console.print('\n[success]━━━ ИТОГОВАЯ ИНФОРМАЦИЯ (ПРОФИЛЬ) ━━━[/success]')
        summary = {}
        for rec in all_normalized_records:
            for k, v in rec.items():
                if k == 'Дополнительно': continue
                if v and str(v).lower() != 'false':
                    if k not in summary: summary[k] = set()
                    summary[k].add(str(v))
        
        if summary and not silent:
            priority_keys = ['ФИО', 'Возраст', 'Дата рождения', 'Пол', 'Город', 'Регион', 'Адрес', 'Email', 'TG ID', 'Работа', 'Соцсети']
            
            for k in priority_keys:
                if k in summary:
                    vals = sorted(list(summary[k]))
                    list_str = ", ".join(vals)
                    console.print(f' [success]\u2022[/success] [secondary]{k:.<15}[/secondary] {list_str}')
            
            for k, vals in summary.items():
                if k not in priority_keys:
                    list_str = ", ".join(sorted(list(vals)))
                    console.print(f' [success]\u2022[/success] [secondary]{k:.<15}[/secondary] {list_str}')
        elif not summary and not silent:
            console.print('[warning]Общих данных не найдено.[/warning]')

    if not silent:
        console.print(
            f'\n[success]\u2713 Выведено {current_count} из {total_records} результатов[/success]'
        )

    if all_normalized_records:
        if False and not silent and not from_connections and load_config(USERNAME).get('connections_enabled', 'false') == 'true':
            conn_choice = v2i('\nЗапустить поиск по связям? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
            if conn_choice in ('y', 'yes', 'д', 'да'):
                initial_leads = {'fio': set(), 'email': set(), 'vk': set(), 'phone': set()}
                
                _fio_labels   = {'ФИО', 'Имя (Centralevents)', 'Имя'}
                _vk_labels    = {'ВК', 'VK', 'ID ВКонтакте', 'VK ID', 'Соцсети'}
                _email_labels = {'Email', 'Почта'}

                for k, vals in summary.items():
                    if k in _fio_labels:
                        initial_leads['fio'].update(vals)
                    elif k in _vk_labels:
                        initial_leads['vk'].update(vals)
                    elif k in _email_labels:
                        initial_leads['email'].update(vals)

                from functions.misc.connections import run_connections
                run_connections(initial_leads)

        if not from_connections and (silent or load_config(USERNAME).get('use_ai', 'true') == 'true'):
            if silent:
                ai_choice = 'y'
            else:
                ai_choice = v2i('\nЗапустить ИИ-анализ найденных данных? (y/n)', f'{USERNAME}@{UUID}').strip().lower()

            if ai_choice in ('y', 'yes', 'д', 'да'):
                from functions.page_1.ai_chat import get_ai_answer
                console.print('\n[secondary]Анализ данных нейросетью (Может занять время)...[/secondary]')

                dumped_data = json.dumps(all_normalized_records, ensure_ascii=False)
                prompt = (
                    "Ты — опытный OSINT-аналитик. Я передаю тебе собранные разрозненные данные по номеру телефона в формате JSON. "
                    "Твоя задача — проанализировать их, сопоставить факты, найти наиболее вероятные правдивые "
                    "значения (ФИО, дата рождения/возраст, соцсети, почты, адреса, работа) и выдать структурированное итоговое досье. "
                    "Пиши обычным текстом, БЕЗ использования Markdown (без звездочек, решеток и жирного шрифта). "
                    "Не пиши ничего лишнего, только итоговый отчет. Отсеивай явные ошибки или противоречивый мусор. "
                    f"Данные: {dumped_data}"
                )

                try:
                    answer = get_ai_answer(prompt, 'groq')
                    clean_answer = answer.replace('*', '').replace('#', '').strip()
                    if silent:
                        return clean_answer
                    console.print('\n[success]\u2501\u2501\u2501 ДОСЬЕ ОТ НЕЙРОСЕТИ \u2501\u2501\u2501[/success]')
                    console.print(clean_answer)
                except Exception as e:
                    if silent:
                        return f'Ошибка ИИ: {e}'
                    console.print(f'\n[error]Ошибка ИИ: {e}[/error]')
            elif silent:
                return "Данные собраны, но ИИ-анализ отключен."

    elif silent:
        return "Не удалось найти информацию по этому номеру."
