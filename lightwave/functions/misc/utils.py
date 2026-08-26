from modules.console import console
import requests, json, time, re

def render_value(value, indent=0):
    pad = ' ' * indent
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.extend(render_value(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {v}")
        return lines
    if isinstance(value, list):
        lines = []
        for i, item in enumerate(value, 1):
            if isinstance(item, (dict, list)):
                lines.append(f"{pad}{i}):")
                lines.extend(render_value(item, indent + 2))
            else:
                lines.append(f"{pad}{i}): {item}")
        return lines
    return [f"{pad}{value}"]


def print_record(data: dict, title: str | None = None):
    if not data:
        return
    if title:
        console.print(f"\n[success]{title}[/success]")
    for key, value in data.items():
        if value is None:
            continue
        if isinstance(value, (dict, list)):
            console.print(f"  [success]•[/success] [secondary]{key: <20}[/secondary]:")
            for line in render_value(value, 2):
                console.print(f"      {line}")
        else:
            console.print(f"  [success]•[/success] [secondary]{key: <20}[/secondary] {value}")


def _api_payload(cfg, query, search_type):
    payload = cfg['payload'].copy()
    if search_type:
        payload['type'] = search_type
    for k, v in payload.items():
        if v is None and k != 'type':
            payload[k] = query
    return payload


def _base_domain(url):
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc or url
    parts = netloc.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])
    return netloc


def _strip_watermarks(data, domain):
    if isinstance(data, dict):
        return {k: _strip_watermarks(v, domain) for k, v in data.items()}
    if isinstance(data, list):
        return [_strip_watermarks(v, domain) for v in data]
    if isinstance(data, str) and domain:
        pat = re.compile(r'\s*<[^>]*>\s*by\s+' + re.escape(domain) + r'[^<\s]*\s*<[^>]*>', re.I)
        out = pat.sub('', data)
        out = re.sub(re.escape(domain), '', out, flags=re.I)
        return re.sub(r'\n{2,}', '\n', out).strip()
    return data


def jitler_fetch(cfg, query, search_type=None, timeout=30):
    """Jitler: POST /search, при получении id — опрос GET /search/{id}."""
    payload = _api_payload(cfg, query, search_type)
    domain = _base_domain(cfg.get('url', ''))
    try:
        r = requests.post(cfg['url'], json=payload, headers=cfg['headers'], timeout=15)
    except Exception:
        return None, 'Ошибка подключения'

    if r.status_code == 429:
        return None, 'Cooldown'
    if r.status_code == 501:
        return None, 'Повторите позже'
    if r.status_code != 200:
        return None, f'HTTP {r.status_code}'

    try:
        data = r.json()
    except json.JSONDecodeError:
        return None, 'Невалидный ответ'

    if not isinstance(data, dict):
        return None, 'Невалидный ответ'

    if 'response' in data:
        response = data['response']
        if response:
            response = _strip_watermarks(response, domain)
        return (response if response else None), None

    if 'id' in data:
        task_id = data['id']
        result_url = cfg.get('result_url', 'https://api.jitler.top/search/{id}').format(id=task_id)
        start = time.time()
        while time.time() - start < timeout:
            time.sleep(2)
            try:
                r2 = requests.get(result_url, headers=cfg['headers'], timeout=10)
            except Exception:
                continue
            if r2.status_code == 501:
                continue
            if r2.status_code != 200:
                return None, f'HTTP {r2.status_code}'
            try:
                res = r2.json()
            except json.JSONDecodeError:
                continue
            if isinstance(res, dict) and 'response' in res:
                response = res['response']
                if response:
                    response = _strip_watermarks(response, domain)
                return (response if response else None), None

    return None, 'Таймаут'


def core_fetch(cfg, query, search_type=None, timeout=15):
    """Core API. Ошибки и лимит не всплывают наружу (скрытый источник)."""
    payload = _api_payload(cfg, query, search_type)
    try:
        r = requests.post(cfg['url'], json=payload, headers=cfg['headers'], timeout=timeout)
    except Exception:
        return None, None

    if r.status_code != 200:
        return None, None

    try:
        data = r.json()
    except json.JSONDecodeError:
        return None, None

    if isinstance(data, dict):
        if 'data' in data:
            inner = data['data']
            return (inner if inner else None), None
        return data or None, None

    return data or None, None


def core_label(data):
    """Переводит ключи Core API в человекочитаемые русские названия."""
    labels = {
        'fio': 'ФИО', 'surname': 'Фамилия', 'name': 'Имя', 'patronymic': 'Отчество',
        'birthdate': 'Дата рождения', 'birthday': 'Дата рождения', 'phone': 'Телефон',
        'email': 'Email', 'passport': 'Паспорт', 'snils': 'СНИЛС', 'inn': 'ИНН',
        'address': 'Адрес', 'city': 'Город', 'region': 'Регион', 'country': 'Страна',
        'street': 'Улица', 'house': 'Дом', 'apartment': 'Квартира',
        'postal_index': 'Почтовый индекс', 'gender': 'Пол', 'operator': 'Оператор',
        'timezone': 'Часовой пояс', 'login': 'Логин', 'nickname': 'Никнейм',
        'vk_id': 'VK ID', 'skype': 'Skype', 'school': 'Школа',
        'school_number': 'Номер школы', 'class_grade': 'Класс', 'class_letter': 'Буква класса',
        'admission_date': 'Дата поступления', 'position': 'Должность', 'salary': 'Зарплата',
        'education': 'Образование', 'schedule': 'График', 'skills': 'Навыки',
        'experience': 'Опыт', 'employment_type': 'Тип занятости', 'apteka': 'Аптека',
        'relation': 'Тип родства', 'fio1': 'ФИО родственника 1', 'fio2': 'ФИО родственника 2',
        'birthdate1': 'Дата рождения 1', 'birthdate2': 'Дата рождения 2',
        'ip': 'IP-адрес', 'datereg': 'Дата регистрации', 'issue_date': 'Дата выдачи',
    }

    def _apply(item):
        if not isinstance(item, dict):
            return item
        out = {}
        for k, v in item.items():
            out[labels.get(k, k)] = v
        return out

    if isinstance(data, list):
        return [_apply(item) for item in data]
    return _apply(data)


def sanitize_error(e):
    """Вычищает из сообщения об ошибке URL, IP и ключи серверов."""
    msg = str(e)
    msg = re.sub(r'https?://[^\s\'\"\)]+', '[скрыто]', msg)
    msg = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}(?::\d{1,5})?\b', '[IP скрыт]', msg)
    msg = re.sub(r'(?i)token[=:\s][^\s&\"\']+', 'token=[скрыто]', msg)
    msg = re.sub(r'(?i)\bkey[=:\s][^\s&\"\']+', 'key=[скрыто]', msg)
    msg = re.sub(r'(?i)api[_-]?key[=:\s][^\s&\"\']+', 'api_key=[скрыто]', msg)
    msg = re.sub(r'(?i)bearer\s+[A-Za-z0-9._\-]+', 'Bearer [скрыто]', msg)
    msg = re.sub(r'(?i)authorization[=: ]+[^\s\"\']+', 'Authorization: [скрыто]', msg)
    msg = re.sub(r'(?i)x-api-key[=: ]+[^\s\"\']+', 'X-API-Key: [скрыто]', msg)
    return msg.strip() or '[скрытая ошибка]'


def whitesearch_fetch(cfg, endpoint, params, timeout=30):
    """WhiteSearch: GET-запрос с X-API-Key по конкретному эндпоинту."""
    url = f"{cfg['url'].rstrip('/')}{endpoint}"
    try:
        r = requests.get(url, params=params, headers=cfg.get('headers', {}), timeout=timeout)
        if r.status_code == 200:
            return r.json(), None
        if r.status_code == 429:
            return None, 'Daily limit exceeded'
        return None, f'HTTP {r.status_code}'
    except Exception:
        return None, 'Ошибка подключения'


def nyx_fetch(cfg, query, timeout=180):
    """Nyx: получает одноразовый ключ и выполняет универсальный поиск."""
    base = cfg['url'].rstrip('/')
    try:
        r_key = requests.get(f"{base}/key", headers=cfg.get('headers', {}), timeout=15)
        if r_key.status_code != 200:
            return None, f'HTTP {r_key.status_code}'
        try:
            key_data = r_key.json()
        except json.JSONDecodeError:
            return None, 'Невалидный ответ'
        nyx_key = key_data.get('key') if isinstance(key_data, dict) else None
        if not nyx_key:
            return None, 'Невалидный ответ'

        headers = dict(cfg.get('headers', {}))
        headers['X-Nyx-Key'] = nyx_key
        r = requests.post(f"{base}/search", json={'query': query}, headers=headers, timeout=timeout)
        if r.status_code != 200:
            return None, f'HTTP {r.status_code}'
        try:
            data = r.json()
        except json.JSONDecodeError:
            return None, 'Невалидный ответ'
        if isinstance(data, dict) and data.get('error'):
            return None, data['error']
        return data or None, None
    except Exception as e:
        return None, f'Ошибка запроса: {e}'


def whitesearch_records(data):
    """Извлекает записи из ответа WhiteSearch."""
    if not data:
        return []
    if isinstance(data, list):
        return [item for item in data if item]
    if isinstance(data, dict):
        if data.get('message') == 'Not found' or data.get('error'):
            return []
        inner = data.get('data')
        if inner is not None:
            return whitesearch_records(inner)
        return [data]
    return [{'Результат': str(data)}] if str(data).strip() else []
