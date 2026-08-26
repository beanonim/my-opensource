from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from functions.hidder import block

BLACKEYE_URL = 'https://blackeyebot.duckdns.org/api/v1/dns'
BLACKEYE_KEY = 'jn87axW1a3MSh8x83AJtDg'

def _print_field(label, value):
    if value is None:
        return
    if isinstance(value, list):
        if not value:
            return
        value = ', '.join(str(v) for v in value)
    console.print(f"  [success]•[/success] [secondary]{label:.<25}[/secondary] {value}")

def site_search(domain):
    if block(domain, 'domain'): return
    if not domain:
        console.print('[error]Введите домен[/error]')
        return

    domain = domain.strip().replace("https://", "").replace("http://", "").split('/')[0].split(':')[0]
    console.print(f'\n[secondary]Поиск информации по домену:[/secondary] [bold]{domain}[/bold]\n')

    headers = {
        'Authorization': f'Bearer {BLACKEYE_KEY}',
        'Content-Type': 'application/json'
    }

    console.print('[secondary]Запрос DNS записей...[/secondary]')

    try:
        r = requests.get(BLACKEYE_URL, params={'domain': domain}, headers=headers, timeout=15)
    except requests.exceptions.RequestException as e:
        console.print(f'[error]Ошибка подключения: {e}[/error]')
        return

    if r.status_code != 200:
        console.print(f'[error]HTTP ошибка: {r.status_code}[/error]')
        return

    try:
        data = r.json()
    except json.JSONDecodeError:
        console.print('[error]Невалидный JSON ответ[/error]')
        return

    if not data.get('success'):
        error_msg = data.get('error', 'Неизвестная ошибка')
        console.print(f'[error]API ошибка: {error_msg}[/error]')
        return

    console.print('[success]━━━ DNS записи ━━━[/success]\n')

    records = data.get('records', {})

    _print_field('Домен', domain)

    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR']:
        if rtype in records and records[rtype]:
            _print_field(rtype, records[rtype])

    has_any = any(records.get(rt) for rt in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR'])
    if not has_any:
        console.print('[warning]DNS записи не найдены[/warning]')

    console.print()
