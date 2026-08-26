import re
import requests
from modules.config import USERNAME, UUID
from modules.theme_manager import load_config
from modules.console import console
from modules.api import API_CONFIG
from modules.cache import load_cache, save_cache

_FIO_KEYS    = {'fio', 'full_name', 'fullname', 'ФИО', 'name', 'имя', 'ф_и_о',
                'firstname', 'lastname', 'surname', 'first_name', 'last_name'}
_EMAIL_KEYS  = {'email', 'mail', 'Почта', 'e-mail', 'emails', 'e_mail', 'почта'}
_VK_KEYS     = {'vk', 'vkontakte', 'vk_id', 'vk_link', 'vk_profile',
                'ID ВКонтакте', 'VK ID', 'ВКонтакте', 'ВК'}
_PHONE_KEYS  = {'phone', 'phones', 'Телефон', 'mobile', 'tel',
                'mobile_phone', 'home_phone', 'телефон', 'номер'}

_BLACKLIST_VALS = {'none', 'false', 'null', '', '-', 'n/a', 'неизвестно', 'не указан'}


def _clean(v) -> str | None:
    if v is None:
        return None
    s = str(v).strip()
    if s.lower() in _BLACKLIST_VALS or len(s) < 2:
        return None
    return s


def _extract(data, keys, max_depth: int = 8) -> set:
    found = set()
    if max_depth <= 0:
        return found

    if isinstance(data, dict):
        for k, v in data.items():
            k_lo = str(k).lower().strip()
            if any(kw.lower() == k_lo or kw.lower() in k_lo for kw in keys):
                if isinstance(v, str):
                    c = _clean(v)
                    if c:
                        found.add(c)
                elif isinstance(v, list):
                    for item in v:
                        c = _clean(item)
                        if c:
                            found.add(c)
                elif isinstance(v, (int, float)):
                    c = _clean(str(v))
                    if c:
                        found.add(c)
            elif isinstance(v, (dict, list)):
                found |= _extract(v, keys, max_depth - 1)

    elif isinstance(data, list):
        for item in data:
            found |= _extract(item, keys, max_depth - 1)

    return found


def _is_fio(s: str) -> bool:
    parts = s.strip().split()
    if len(parts) < 2:
        return False
    return all(re.match(r'^[а-яёА-ЯЁa-zA-Z\-]+$', p) for p in parts)


def _is_email(s: str) -> bool:
    return bool(re.match(r'^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$', s.strip()))


def _is_vk(s: str) -> bool:
    s = s.strip()
    return s.isdigit() or bool(re.match(r'^(https?://)?(vk\.com/)?[a-zA-Z0-9_\.\-]{3,}$', s))


def _silent_search(search_type: str, query: str, api_flag: str,
                   payload_builder=None) -> dict:
    leads = {'fio': set(), 'email': set(), 'vk': set(), 'phone': set()}

    active = [n for n, c in API_CONFIG.items()
              if c.get(api_flag) and c.get('working', True)]

    for api_num in active:
        cfg = API_CONFIG[api_num]

        data = load_cache(search_type, query, api_num)

        if not data:
            if api_num in (42, 43):
                try:
                    from functions.misc.utils import whitesearch_fetch, nyx_fetch
                    if api_num == 42:
                        _ws_endpoint = {'fio': '/search/fio', 'email': '/search/email'}.get(search_type, '/search')
                        _ws_param = {'fio': 'fio', 'email': 'email'}.get(search_type, 'q')
                        data, _err = whitesearch_fetch(cfg, _ws_endpoint, {_ws_param: query})
                    else:
                        data, _err = nyx_fetch(cfg, query)
                    if data:
                        save_cache(search_type, query, api_num, data)
                except Exception:
                    continue
            else:
                try:
                    url = cfg['url']
                    headers = cfg.get('headers', {}).copy()
                    payload = cfg.get('payload', {}).copy()

                    if '{query}' in url:
                        url = url.format(query=query)
                    elif callable(payload_builder):
                        payload = payload_builder(api_num, payload, query)
                    else:
                        for k, v in payload.items():
                            if v is None:
                                payload[k] = query

                    method = cfg.get('method', 'POST')
                    pf = cfg.get('post_format', 'json')
                    params = {k: v for k, v in payload.items() if v is not None}

                    if method == 'POST':
                        r = (requests.post(url, data=params, headers=headers, timeout=20)
                             if pf == 'form' else
                             requests.post(url, json=payload, headers=headers, timeout=20))
                    else:
                        r = requests.get(url, params=params, headers=headers, timeout=20)

                    if r.status_code == 200:
                        try:
                            data = r.json()
                            save_cache(search_type, query, api_num, data)
                        except Exception:
                            continue
                except Exception:
                    continue

        if data:
            leads['fio']   |= _extract(data, _FIO_KEYS)
            leads['email'] |= _extract(data, _EMAIL_KEYS)
            leads['vk']    |= _extract(data, _VK_KEYS)
            leads['phone'] |= _extract(data, _PHONE_KEYS)

    return leads


def _fio_payload(api_num, payload, fullname):
    if api_num == 29:
        payload.pop('phone', None)
        payload['fio'] = fullname
    elif api_num == 30:
        payload['type'] = 'name'
        payload['quest'] = fullname
    else:
        for k, v in payload.items():
            if v is None:
                payload[k] = fullname
    return payload


def _email_payload(api_num, payload, email):
    if api_num == 29:
        payload.pop('phone', None)
        payload['email'] = email
    elif api_num == 30:
        payload['type'] = 'email'
        payload['quest'] = email
    elif api_num == 32:
        payload['check'] = email
    else:
        for k, v in payload.items():
            if v is None:
                payload[k] = email
    return payload


def _silent_fio(fullname: str) -> dict:
    return _silent_search('fio', fullname, 'is_fio_search', _fio_payload)


def _silent_email(email: str) -> dict:
    return _silent_search('email', email, 'is_email_search', _email_payload)


def _silent_vk(vk_id: str) -> dict:
    leads = {'fio': set(), 'email': set(), 'vk': set(), 'phone': set()}
    try:
        from bs4 import BeautifulSoup
        headers = {"User-Agent": "Mozilla/5.0"}

        url = (f"https://looka.one/vk_user/id{vk_id}"
               if str(vk_id).isdigit()
               else f"https://looka.one/vk_user/{vk_id}")
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            name_el = soup.select_one('.main > h1:nth-child(1)')
            phone_el = soup.select_one('.home_phone')
            if name_el:
                fio = name_el.text.strip()
                if _is_fio(fio):
                    leads['fio'].add(fio)
            if phone_el and phone_el.text.strip():
                ph = _clean(phone_el.text)
                if ph:
                    leads['phone'].add(ph)
    except Exception:
        pass

    vk_tokens = [
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    ]
    for token in vk_tokens:
        try:
            vk_resp = requests.get(
                "https://api.vk.com/method/users.get",
                params={
                    "user_ids": vk_id,
                    "fields": "bdate,city,country,home_phone,mobile_phone",
                    "access_token": token,
                    "v": "5.131",
                },
                timeout=10,
            )
            if vk_resp.status_code == 200:
                vk_data = vk_resp.json()
                if "response" in vk_data and vk_data["response"]:
                    user = vk_data["response"][0]
                    full = f"{user.get('first_name','')} {user.get('last_name','')}".strip()
                    if _is_fio(full):
                        leads['fio'].add(full)
                    for field in ('home_phone', 'mobile_phone'):
                        ph = _clean(user.get(field, ''))
                        if ph:
                            leads['phone'].add(ph)
                    break
        except Exception:
            continue

    return leads


_TYPE_LABEL = {
    'fio':   'ФИО',
    'email': 'Email',
    'vk':    'ВКонтакте',
    'phone': 'Телефон',
}

_VALID = {
    'fio':   _is_fio,
    'email': _is_email,
    'vk':    _is_vk,
    'phone': lambda s: bool(re.match(r'^\+?\d[\d\s\-\(\)]{9,}$', s.strip())),
}


def run_connections(initial_leads: dict):
    config = load_config(USERNAME)
    max_depth = int(config.get('connections_depth', 5))

    console.print('\nПоиск по связям\n')

    visited: dict[str, set] = {t: set() for t in _TYPE_LABEL}
    queue: list[tuple[str, str, str]] = []

    source_label = 'Телефон'
    for lead_type in ('fio', 'email', 'vk'):
        for val in initial_leads.get(lead_type, set()):
            v = _clean(val)
            if v and _VALID[lead_type](v):
                queue.append((lead_type, v, source_label))

    if not queue:
        console.print('[warning]Нет начальных данных для построения цепочки[/warning]\n')
        return

    depth = 0
    total_processed = 0

    while queue and depth < max_depth:
        next_queue: list[tuple[str, str, str]] = []
        depth_label = f'Глубина {depth + 1}'

        console.print(f'[secondary]── {depth_label} {"─" * (38 - len(depth_label))}[/secondary]')

        for lead_type, value, from_source in queue:
            if value in visited[lead_type]:
                continue
            visited[lead_type].add(value)
            total_processed += 1

            type_name = _TYPE_LABEL[lead_type]
            console.print(
                f'\n[secondary][/secondary] [dim]{from_source}[/dim] '
                f'[dim]→[/dim] [secondary]{type_name}:[/secondary] [bold]{value}[/bold]'
            )

            new_leads: dict[str, set] = {t: set() for t in _TYPE_LABEL}

            if lead_type == 'fio':
                try:
                    from functions.page_2.fio import fio_search
                    fio_search(value)
                except Exception:
                    console.print('[error]Ошибка поиска ФИО[/error]')
                new_leads = _silent_fio(value)

            elif lead_type == 'email':
                try:
                    from functions.page_2.email import email_search
                    email_search(value)
                except Exception:
                    console.print('[error]Ошибка поиска Email[/error]')
                new_leads = _silent_email(value)

            elif lead_type == 'vk':
                try:
                    from functions.page_1.vk import vk_search
                    vk_search(value)
                except Exception:
                    console.print('[error]Ошибка поиска ВК[/error]')
                new_leads = _silent_vk(value)

            elif lead_type == 'phone':
                try:
                    from functions.page_1.phone import phone_search
                    phone_search(value, from_connections=True)
                except Exception:
                    console.print('[error]Ошибка поиска телефона[/error]')

            found_new = False
            for ntype, nvals in new_leads.items():
                for nval in nvals:
                    nv = _clean(nval)
                    if not nv:
                        continue
                    if not _VALID[ntype](nv):
                        continue
                    if nv in visited[ntype]:
                        continue

                    console.print(
                        f'[success]Новая связь:[/success] '
                        f'[secondary]{_TYPE_LABEL[ntype]}[/secondary] → [bold]{nv}[/bold]'
                    )
                    next_queue.append((ntype, nv, value))
                    found_new = True

            if not found_new:
                console.print('[dim]Новых связей не обнаружено[/dim]')

        queue = next_queue
        depth += 1

        if queue:
            console.print(
                f'\n[secondary]Найдено {len(queue)} новых связей, '
                f'углубляемся...[/secondary]'
            )

    console.print('\nПоиск по связям завершён\n')

    console.print(f' [success]•[/success] Обработано узлов: [bold]{total_processed}[/bold]')
    for t, s in visited.items():
        if s:
            console.print(
                f' [success]•[/success] Уникальных {_TYPE_LABEL[t]}: '
                f'[bold]{len(s)}[/bold]  '
                f'[dim]({", ".join(list(s)[:3])}{"..." if len(s) > 3 else ""})[/dim]'
            )
    console.print()
