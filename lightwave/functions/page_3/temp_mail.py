import time
import requests
import random
import string
from modules.console import *
from modules.input import *

BASE_URL = "https://api.mail.tm"

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def get_domains():
    try:
        r = requests.get(f"{BASE_URL}/domains", timeout=10)
        if r.status_code == 200:
            data = r.json()
            return [d['domain'] for d in data.get('hydra:member', [])]
        return ["mail.tm"]
    except:
        return ["mail.tm"]

def temp_mail_tool():
    console.print("\n[warning]Внимание: Появление нового сообщения может быть немного долгим![/warning]")
    console.print('\n[secondary]Инициализация временной почты...[/secondary]')
    
    try:
        domains = get_domains()
        if not domains:
             console.print('[error]Не удалось получить список доменов. Попробуйте позже.[/error]')
             return

        choice = v2i('Использовать случайный логин? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
        if choice in ('n', 'no', 'н', 'нет'):
            login = v2i('Введите желаемый логин', f'{USERNAME}@{UUID}').strip().lower()
            if not login:
                login = generate_random_string()
        else:
            login = generate_random_string()
            
        domain = domains[0]
        address = f"{login}@{domain}"
        password = generate_random_string(12)
        
        account_data = {"address": address, "password": password}
        r_acc = requests.post(f"{BASE_URL}/accounts", json=account_data, timeout=15)
        
        if r_acc.status_code not in (200, 201):
            console.print('[error]Ошибка при создании почты[/error]')
            if r_acc.status_code == 422:
                console.print('[warning]Возможно, этот логин уже занят. Попробуйте другой.[/warning]')
            return

        r_token = requests.post(f"{BASE_URL}/token", json=account_data, timeout=15)
        if r_token.status_code != 200:
             console.print('[error]Ошибка авторизации[/error]')
             return
        
        token = r_token.json().get('token')
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        console.print(f'\n[success]Ваш временный адрес:[/success] [primary]{address}[/primary]')
        console.print('[dim]Ожидание писем... (Ctrl+C для выхода)[/dim]\n')
        
        debug_choice = v2i('Включить дебаггер? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
        debug_mode = debug_choice in ('y', 'yes', 'д', 'да')
        
        seen_ids = set()
        checks = 0
        
        while True:
            checks += 1
            try:
                msg_url = f"/messages"
                msg_urlr = f"{BASE_URL}/messages"
                if debug_mode:
                    console.print(f'[dim][{checks}] GET {msg_url}[/dim]')
                else:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                
                r_msgs = requests.get(msg_urlr, headers=headers, timeout=10)
                
                if debug_mode:
                    console.print(f'[dim]Response: {r_msgs.status_code} | Size: {len(r_msgs.text)}[/dim]')
                
                if r_msgs.status_code == 200:
                    messages = r_msgs.json().get('hydra:member', [])
                    for msg in messages:
                        msg_id = msg.get('id')
                        if msg_id not in seen_ids:
                            seen_ids.add(msg_id)
                            
                            read_url = f"{BASE_URL}/messages/{msg_id}"
                            r_full = requests.get(read_url, headers=headers, timeout=10)
                            if r_full.status_code == 200:
                                data = r_full.json()
                                if not debug_mode:
                                    print()
                                console.print(f'\n[success] Новое письмо (ID: {msg_id[:8]})[/success]')
                                console.print(f'[secondary]От:[/secondary] {data.get("from", {}).get("address")}')
                                console.print(f'[secondary]Тема:[/secondary] {data.get("subject")}')
                                console.print(f'[secondary]Дата:[/secondary] {data.get("createdAt")}')
                                
                                body = data.get("text") or data.get("html") or "[Пустое сообщение]"
                                console.print(f'[secondary]Сообщение:[/secondary]\n{body}')
                                console.print(f'[success][/success]\n')
                
                time.sleep(3)
            except Exception:
                if debug_mode:
                    console.print('[error]Ошибка во время проверки[/error]')
                time.sleep(3)
                
    except KeyboardInterrupt:
        console.print('\n[dim]Работа с временной почтой завершена[/dim]')
    except Exception:
        console.print('[error]Критическая ошибка[/error]')