from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.filter import clean_record
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import whitesearch_fetch, nyx_fetch, sanitize_error
from functions.misc.utils import whitesearch_fetch, nyx_fetch, whitesearch_records

def check_username(session, url, username):
    try:
        response = session.get(url.format(username=username), timeout=15)
        return response.status_code == 200
    except Exception:
        return False

def _render_result(site_name, url, status):
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column('Параметр', style='secondary', width=18)
    table.add_column('Значение', style='text')
    table.add_row('Сайт', site_name)
    table.add_row('URL', f'[primary][link={url}]{url}[/link][/primary]')
    table.add_row('Статус', status)
    console.print(table)

def nickname_search(username):
    if block(username, 'username'): return
    sites = [
        ('GitHub', 'https://github.com/{username}'),
        ('Twitter', 'https://twitter.com/{username}'),
        ('Instagram', 'https://www.instagram.com/{username}'),
        ('Facebook', 'https://www.facebook.com/{username}'),
        ('YouTube', 'https://www.youtube.com/@{username}'),
        ('Reddit', 'https://www.reddit.com/user/{username}'),
        ('TikTok', 'https://www.tiktok.com/@{username}'),
        ('LinkedIn', 'https://www.linkedin.com/in/{username}'),
        ('Pinterest', 'https://pinterest.com/{username}'),
        ('Twitch', 'https://www.twitch.tv/{username}'),
        ('VK', 'https://vk.com/{username}'),
        ('Steam', 'https://steamcommunity.com/id/{username}'),
        ('Spotify', 'https://open.spotify.com/user/{username}'),
        ('Telegram', 'https://t.me/{username}'),
        ('DeviantArt', 'https://www.deviantart.com/{username}'),
        ('Behance', 'https://www.behance.net/{username}'),
        ('Medium', 'https://medium.com/@{username}'),
        ('GitLab', 'https://gitlab.com/{username}'),
        ('Flickr', 'https://www.flickr.com/people/{username}'),
        ('SoundCloud', 'https://soundcloud.com/{username}')
    ]
    console.print('[secondary]Идет поиск...[/secondary]')
    found = 0
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    })
    for site_name, url in sites:
        exists = check_username(session, url, username)
        status = '[success]Найден[/]' if exists else '[error]Не найден[/]'
        _render_result(site_name, url.format(username=username), status)
        if exists: found += 1
    
    console.print(f'\n[success]Найдено упоминаний:[/] {found} из {len(sites)}')
    try:
        api = LeakCheckAPI_v2(api_key=LEAKCHECK_API_KEY)
        leak_results = api.lookup(query=username, query_type='username', limit=100)
        console.print("\n[secondary]LeakCheck[/secondary]")
        if not leak_results:
            console.print('[warning]LeakCheck: результатов нет[/warning]')
        else:
            console.print(f'[success]Найдено записей:[/] {len(leak_results)}')
            for idx, entry in enumerate(leak_results, 1):
                entry_dict = entry.dict if hasattr(entry, 'dict') else entry
                console.print(f"\n[success]Запись {idx}[/success]")
                for k, v in entry_dict.items():
                    console.print(f'[secondary]{k}[/secondary]: {v}')
    except Exception as e:
        console.print(f'[error]LeakCheck ошибка: {sanitize_error(e)}[/error]')

    try:
        ds_cfg = API_CONFIG[38]
        ds_payload = ds_cfg['payload'].copy()
        ds_payload['search'] = username
        ds_resp = requests.post(ds_cfg['url'], json=ds_payload, headers=ds_cfg['headers'], timeout=15)
        if ds_resp.status_code == 200:
            ds_data = ds_resp.json()
            ds_record = _normalize_deepscan(ds_data)
            if ds_record:
                ds_record = clean_record(ds_record)
                if ds_record:
                    console.print('\n[success]━━━ API 38 ━━━[/success]')
                    for k, v in ds_record.items():
                        if isinstance(v, list):
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                        else:
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
    except Exception as e:
        console.print(f'[error]API 38 ошибка: {sanitize_error(e)}[/error]')

    try:
        ws_cfg = API_CONFIG[42]
        ws_data, ws_err = whitesearch_fetch(ws_cfg, '/search/nick', {'nick': username})
        if ws_data:
            for rec in whitesearch_records(ws_data):
                rec = clean_record(rec)
                if rec:
                    console.print('\n[success]━━━ API 42 ━━━[/success]')
                    for k, v in rec.items():
                        if isinstance(v, list):
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                        else:
                            console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
    except Exception as e:
        console.print(f'[error]API 42 ошибка: {sanitize_error(e)}[/error]')

    try:
        nx_cfg = API_CONFIG[43]
        nx_data, nx_err = nyx_fetch(nx_cfg, username)
        if nx_data:
            text = nx_data.get('text') if isinstance(nx_data, dict) else str(nx_data)
            if text:
                console.print('\n[success]━━━ API 43 ━━━[/success]')
                console.print(text)
    except Exception as e:
        console.print(f'[error]API 43 ошибка: {sanitize_error(e)}[/error]')
    