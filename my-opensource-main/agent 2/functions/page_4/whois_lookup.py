from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from functions.hidder import block

BLACKEYE_DNS_URL = 'https://blackeyebot.duckdns.org/api/v1/dns'
BLACKEYE_KEY = 'jn87axW1a3MSh8x83AJtDg'

def _print_field(label, value):
    if value:
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value)
        console.print(f"  [success]•[/success] [secondary]{label:.<20}[/secondary] {value}")

def whois_lookup(query):
    if block(query, 'domain'): return
    if not query:
        console.print('[error]Введите домен[/error]')
        return

    query = query.strip().replace("https://", "").replace("http://", "").split('/')[0].split(':')[0]
    console.print(f'\n[secondary]Анализ домена:[/secondary] [bold]{query}[/bold]\n')

    # whois
    try:
        import whois
        w = whois.whois(query)
        whois_ok = True
    except Exception:
        whois_ok = False

    if whois_ok:
        console.print('[success]━━━ WHOIS информация ━━━[/success]\n')
        _print_field('Домен', w.domain_name)
        _print_field('Registrar', w.registrar)
        _print_field('WHOIS сервер', w.whois_server)

        if w.creation_date:
            date = w.creation_date
            if isinstance(date, list): date = date[0]
            _print_field('Дата регистрации', date)

        if w.expiration_date:
            date = w.expiration_date
            if isinstance(date, list): date = date[0]
            _print_field('Истекает', date)

        if w.updated_date:
            date = w.updated_date
            if isinstance(date, list): date = date[0]
            _print_field('Обновлён', date)

        _print_field('NS серверы', w.name_servers)
        _print_field('DNSSEC', w.dnssec)
        _print_field('Страна', w.country)
        _print_field('Город', w.city)
        _print_field('Регион', w.state)
        _print_field('Организация', w.org)

        if w.emails:
            emails = w.emails if isinstance(w.emails, list) else [w.emails]
            _print_field('Email', ', '.join(emails))
        console.print()
    else:
        console.print('[warning]WHOIS: не удалось получить данные[/warning]\n')

    # dns (blackeye)
    console.print('[secondary]Запрос DNS записей (BlackEye)...[/secondary]')
    headers = {
        'Authorization': f'Bearer {BLACKEYE_KEY}',
        'Content-Type': 'application/json'
    }

    try:
        r = requests.get(BLACKEYE_DNS_URL, params={'domain': query}, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data.get('success'):
                records = data.get('records', {})
                has_records = any(records.get(rt) for rt in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR'])

                if has_records:
                    console.print('[success]━━━ DNS записи (BlackEye) ━━━[/success]\n')
                    for rtype in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV', 'PTR']:
                        if records.get(rtype):
                            _print_field(rtype, records[rtype])
                    console.print()
    except Exception:
        pass
