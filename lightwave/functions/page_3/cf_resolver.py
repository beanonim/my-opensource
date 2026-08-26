from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from functions.hidder import block

def cf_resolver(domain):
    if block(domain, 'domain'): return
    try:
        domain = domain.replace("https://", "").replace("http://", "").split('/')[0]
        console.print(f"\n[secondary]Исследование для:[/secondary] [bold]{domain}[/bold]")
        
        try:
            current_ip = socket.gethostbyname(domain)
            console.print(f" [success]•[/success] [secondary]Текущий IP (через DNS):[/secondary] {current_ip}")
        except:
            console.print(" [error]•[/error] [error]Не удалось разрешить основной домен[/error]")
            return

        results = []

        def check_sub(sub):
            host = f"{sub}.{domain}"
            try:
                ip = socket.gethostbyname(host)
                results.append({
                    "method": "Subdomain",
                    "data": host,
                    "ip": ip,
                    "info": "Найдено"
                })
                return True
            except:
                return False

        common_subs = ["direct", "dev", "stage", "test", "mail", "cpanel", "admin", "webmail", "blog", "api", "vpn", "m"]
        
        emojis = ['🌍', '🌎', '🌏']
        with Live(Text(""), console=console, transient=True) as live:
            for idx, s in enumerate(common_subs):
                live.update(Text(f"{emojis[idx % 3]} Проверка поддоменов... [{idx+1}/{len(common_subs)}]", style="secondary"))
                check_sub(s)
                
            live.update(Text("Поиск в SSL логах (crt.sh)...", style="secondary"))
            try:
                url = f"https://crt.sh/?q={domain}&output=json"
                resp = requests.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    found_certs = set()
                    for entry in data:
                        name = entry['common_name']
                        if name not in found_certs and domain in name:
                            found_certs.add(name)
                            try:
                                ip = socket.gethostbyname(name)
                                results.append({
                                    "method": "SSL Log",
                                    "data": name,
                                    "ip": ip,
                                    "info": "Из сертификата"
                                })
                            except:
                                pass
            except:
                pass

        if not results:
            console.print("\n[warning]Ничего интересного не найдено. Сайт надежно защищен или origin скрыт.[/warning]")
        else:
            console.print(f"\n[success]━━━ Результаты исследования ({len(results)}) ━━━[/success]")
            for idx, item in enumerate(results, 1):
                console.print(f"\n [success]Запись #{idx}[/success]")
                console.print(f"  [success]•[/success] [secondary]Метод          [/secondary] {item['method']}")
                console.print(f"  [success]•[/success] [secondary]Данные         [/secondary] {item['data']}")
                console.print(f"  [success]•[/success] [secondary]IP             [/secondary] [success]{item['ip']}[/success]")
                console.print(f"  [success]•[/success] [secondary]Инфо           [/secondary] {item['info']}")

            console.print("\n[success]✓ Проверка завершена.[/success]")

    except Exception:
        console.print("[error]Ошибка резольвера[/error]")
    