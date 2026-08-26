from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.console import *
from rich.live import Live
from rich.text import Text
import re
import urllib.parse
from bs4 import BeautifulSoup
from functions.hidder import block

def endpoint_finder(url):
    if block(url, 'domain'): return
    try:
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            
        parsed_base = urllib.parse.urlparse(url)
        domain = parsed_base.netloc
        
        console.print(f"\n[secondary]Поиск эндпоинтов для:[/secondary] [bold]{url}[/bold]\n")
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        endpoints = set()
        visited = set()
        
        def extract_endpoints_from_text(text):
            pattern = r'(?:"|\')(/[a-zA-Z0-9_\-\./]+)(?:"|\')'
            matches = re.findall(pattern, text)
            for match in matches:
                if match == '/': continue
                if any(match.endswith(ext) for ext in ['.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ico', '.ttf']): continue
                endpoints.add(match)

        with Live(Text("Получение главной страницы...", style="secondary"), console=console, transient=True) as live:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                extract_endpoints_from_text(resp.text)
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    parsed_href = urllib.parse.urlparse(href)
                    if parsed_href.path and parsed_href.path != '/':
                        if not parsed_href.netloc or parsed_href.netloc == domain:
                            clean_path = parsed_href.path
                            endpoints.add(clean_path)
                            
                scripts = soup.find_all('script', src=True)
                for idx, script in enumerate(scripts):
                    src = script['src']
                    script_url = urllib.parse.urljoin(url, src)
                    parsed_script_url = urllib.parse.urlparse(script_url)
                    
                    if parsed_script_url.netloc == domain or (not parsed_script_url.netloc and src.startswith('/')):
                        live.update(Text(f"Анализ скриптов... [{idx+1}/{len(scripts)}] {src}", style="secondary"))
                        try:
                            s_resp = requests.get(script_url, headers=headers, timeout=10)
                            extract_endpoints_from_text(s_resp.text)
                        except:
                            pass
            except Exception:
                console.print("[error]Ошибка при доступе к сайту[/error]")
                return

        clean_endpoints = set()
        for ep in endpoints:
            ep_clean = ep.split('?')[0].split('#')[0]
            if len(ep_clean) > 1 and ep_clean.startswith('/'):
                clean_endpoints.add(ep_clean)

        if not clean_endpoints:
            console.print("[warning]Эндпоинты не найдены.[/warning]")
        else:
            console.print(f"[success]━━━ Найденные эндпоинты ({len(clean_endpoints)}) ━━━[/success]")
            for ep in sorted(clean_endpoints):
                console.print(f" [success]•[/success] [secondary]{ep}[/secondary]")
                
        console.print("\n[success]✓ Поиск завершен.[/success]")

    except Exception:
        console.print("[error]Ошибка[/error]")
    