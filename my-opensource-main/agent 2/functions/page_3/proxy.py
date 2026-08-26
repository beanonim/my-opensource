from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *

def upload_to_litterbox(filepath):
    try:
        with open(filepath, 'rb') as f:
            r = requests.post('https://litterbox.catbox.moe/resources/internals/api.php', files={'fileToUpload': f}, data={'reqtype': 'fileupload', 'time': '24h'})
        if r.status_code == 200:
            link = r.text.strip()
            return link if link.startswith('https://') else None
    except Exception: return None

def proxy_scraper():
    try:
        console.print("\n[secondary]Сбор прокси...[/secondary]")
        r = requests.get("https://vakhov.github.io/fresh-proxy-list/proxylist.json", timeout=15)
        if r.status_code != 200: return
        data = r.json()
        if not data: return
        console.print(f"[success]Найдено {len(data)} прокси.[/success]\n")
        console.print("[primary]1[/primary] CSV\n[primary]2[/primary] Python")
        choice = v2i("Формат", f'{USERNAME}@{UUID}').strip()
        if choice not in ['1', '2']: return
        suffix = '.csv' if choice == '1' else '.py'
        temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix=suffix, delete=False)
        temp_path = temp_file.name
        try:
            with temp_file as f:
                if choice == '1':
                    f.write("IP;Port;Country;Type\n")
                    for p in data: f.write(f"{p.get('ip')};{p.get('port')};{p.get('country_name')};{p.get('type','http')}\n")
                else:
                    f.write(f"PROXIES = {data}\n")
            console.print("[secondary]Загружаю...[/secondary]")
            link = upload_to_litterbox(temp_path)
            if link: console.print(f"\n[success]Готово: {link}[/success]")
            else: console.print("\n[error]Ошибка загрузки[/error]")
        finally:
            if os.path.exists(temp_path): os.remove(temp_path)
    except Exception: console.print("\n[error]Ошибка[/error]")
    