from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from functions.hidder import block

def _print_field(label, value):
    if value:
        if isinstance(value, list):
            value = ', '.join(str(v) for v in value)
        console.print(f"  [success]•[/success] [secondary]{label:.<20}[/secondary] {value}")

def email_mx_check(email):
    if block(email, 'email'): return
    if not email:
        console.print('[error]Введите email[/error]')
        return

    email = email.strip().lower()
    domain = email.split('@')[1] if '@' in email else None

    if not domain:
        console.print('[error]Некорректный email[/error]')
        return

    console.print(f'\n[secondary]Проверка:[/secondary] [bold]{email}[/bold]\n')
    console.print(f'[success]━━━ Домен: {domain} ━━━[/success]\n')

    try:
        import dns.resolver
    except ImportError:
        console.print('[error]Модуль dnspython не установлен[/error]')
        return

    record_types = ['MX', 'A', 'AAAA', 'NS', 'TXT', 'SOA', 'CNAME']
    found_any = False

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records = []
            for r in answers:
                if rtype == 'MX':
                    records.append(f"{r.preference} {r.exchange}")
                elif rtype == 'SOA':
                    records.append(f"MNAME={r.mname}, RNAME={r.rname}, serial={r.serial}")
                elif rtype == 'TXT':
                    for txt in r.strings:
                        records.append(txt.decode() if isinstance(txt, bytes) else str(txt))
                else:
                    records.append(str(r))

            if records:
                found_any = True
                console.print(f'  [success]•[/success] [secondary]{rtype:.<20}[/secondary]')
                for rec in records:
                    console.print(f'      {rec}')
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            pass
        except Exception:
            pass

    console.print()
    console.print(f'[success]━━━ Дополнительная информация ━━━[/success]\n')

    try:
        ip = socket.gethostbyname(domain)
        _print_field('IP (A record)', ip)
    except Exception:
        pass

    try:
        ips = socket.getaddrinfo(domain, None)
        unique_ips = list(set(addr[4][0] for addr in ips))
        if len(unique_ips) > 1:
            _print_field('Все IP', unique_ips)
    except Exception:
        pass

    try:
        import ssl
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()
            _print_field('SSL Issuer', dict(x[0] for x in cert.get('issuer', [])))
            _print_field('SSL Subject', dict(x[0] for x in cert.get('subject', [])))
            _print_field('SSL Выдан', cert.get('notBefore'))
            _print_field('SSL Истекает', cert.get('notAfter'))
            san = cert.get('subjectAltName', [])
            if san:
                _print_field('SSL SAN', ', '.join(s[1] for s in san[:10]))
    except Exception:
        pass

    if not found_any:
        console.print('[warning]DNS записи не найдены[/warning]')

    console.print()
