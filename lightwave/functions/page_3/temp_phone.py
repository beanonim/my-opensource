import time
import requests
import re
from bs4 import BeautifulSoup
from modules.console import *
from modules.input import *

BASE_URL = "https://quackr.io"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def get_available_numbers():
    try:
        r = requests.get(f"{BASE_URL}/temporary-numbers", headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        
        links = re.findall(r'href="(/temporary-numbers/[a-z-]+/[0-9]+)"', r.text)
        
        unique_numbers = []
        seen = set()
        for link in links:
            parts = link.split('/')
            if len(parts) >= 4:
                country = parts[2].replace('-', ' ').title()
                number = parts[3]
                if number not in seen:
                    seen.add(number)
                    unique_numbers.append({
                        "country": country,
                        "number": f"+{number}",
                        "url": f"{BASE_URL}{link}"
                    })
        return unique_numbers
    except Exception as e:
        return []

def get_messages(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return []
        
        soup = BeautifulSoup(r.text, 'html.parser')
        messages = []
        
        rows = soup.find_all('tr')
        if not rows:
            pass
            
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                sender = cols[0].text.strip()
                content = cols[1].text.strip()
                time_ago = cols[2].text.strip()
                
                if content:
                    messages.append({
                        "from": sender,
                        "text": content,
                        "date": time_ago
                    })
        return messages
    except Exception as e:
        return []

def temp_phone_tool():
    console.print('\n[secondary]Инициализация временных номеров (сервис quackr.io)...[/secondary]')
    
    numbers = get_available_numbers()
    if not numbers:
        console.print('[error]Не удалось получить список номеров. Попробуйте позже или используйте другой сервис.[/error]')
        return

    console.print(f'\n[success]Доступно номеров:[/success] {len(numbers)}\n')
    
    for i, item in enumerate(numbers[:20], 1):
        console.print(f' [primary]{i})[/primary] [success]{item["country"]}[/success]: {item["number"]}')

    choice = v2i('\nВыберите номер (номер в списке)', f'{USERNAME}@{UUID}').strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(numbers):
            console.print('[error]Неверный выбор[/error]')
            return
        
        selected = numbers[idx]
        console.print(f'\n[success]Выбран номер:[/success] [primary]{selected["number"]}[/primary] ({selected["country"]})')
        console.print('[dim]Ожидание SMS... (Ctrl+C для выхода)[/dim]\n')
        
        seen_messages = []
        
        while True:
            msgs = get_messages(selected["url"])
            
            for msg in msgs:
                msg_hash = f"{msg['from']}{msg['text']}"
                if msg_hash not in [f"{m['from']}{m['text']}" for m in seen_messages]:
                    seen_messages.append(msg)
                    
                    console.print(f'\n[success]━━━ НОВОЕ SMS ━━━[/success]')
                    console.print(f'[secondary]От:[/secondary] {msg.get("from")}')
                    console.print(f'[secondary]Текст:[/secondary] {msg.get("text")}')
                    console.print(f'[secondary]Когда:[/secondary] {msg.get("date")}')
                    console.print(f'[success]━━━━━━━━━━━━━━━━━━[/success]\n')
            
            if not msgs:
                sys.stdout.write('.')
                sys.stdout.flush()
            
            time.sleep(10)
            
    except ValueError:
        console.print('[error]Введите число[/error]')
    except KeyboardInterrupt:
        console.print('\n[dim]Работа с временным номером завершена[/dim]')
    except Exception:
        console.print('[error]Ошибка[/error]')