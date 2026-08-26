from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *

def discord_tool():
    webhook_url = v2i('Введите Discord webhook URL', f'{USERNAME}@{UUID}').strip()
    if not webhook_url: return
    
    console.print('\n[primary][1][/primary] Написать сообщение\n[primary][2][/primary] Спамить')
    choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()
    
    if choice == '1':
        message = v2i('Введите сообщение', f'{USERNAME}@{UUID}')
        try:
            r = requests.post(webhook_url, json={"content": message})
            if r.status_code == 204: console.print('[success]Отправлено![/]')
            else: console.print('[error]Ошибка отправки[/error]')
        except Exception: console.print('[error]Ошибка соединения[/error]')
    
    elif choice == '2':
        spam_type = v2i('Тип: 1 - Кастом, 2 - Lightwave', f'{USERNAME}@{UUID}').strip()
        text = v2i('Текст', f'{USERNAME}@{UUID}') if spam_type == '1' else 'This spam by lightwave software, buy it at t.me/hatedfame'
        console.print('[dim]Нажмите Ctrl+C для остановки[/dim]')
        try:
            while True:
                r = requests.post(webhook_url, json={"content": text})
                if r.status_code != 204: break
        except KeyboardInterrupt: console.print('\n[dim]Остановлено[/dim]')
    