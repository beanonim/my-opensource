# -*- coding: utf-8 -*-
from colorama import init, Fore, Style
from bs4 import BeautifulSoup
import requests
import json
import re
import os
import sys
import time
import random
import string
import datetime
import base64
import zlib
import marshal
import lzma
import gzip
import concurrent.futures
import urllib.parse
import phonenumbers
import asyncio
import aiohttp
import fake_useragent
import pycountry
import socket
import smtplib
from urllib.parse import urlparse
from threading import Thread
from phonenumbers import geocoder, carrier

init(autoreset=True)

COLOR_SCHEMES = {
    "default": {
        "g": Fore.GREEN + Style.BRIGHT,
        "w": Fore.WHITE + Style.BRIGHT,
        "c": Fore.LIGHTGREEN_EX + Style.BRIGHT
    },
    "blue": {
        "g": Fore.BLUE + Style.BRIGHT,
        "w": Fore.WHITE + Style.BRIGHT,
        "c": Fore.WHITE + Style.BRIGHT,
    },
    "red": {
        "g": Fore.RED + Style.BRIGHT,
        "w": Fore.WHITE + Style.BRIGHT,
        "c": Fore.WHITE + Style.BRIGHT,
    },
    "purple": {
        "g": Fore.MAGENTA + Style.BRIGHT,
        "w": Fore.WHITE + Style.BRIGHT,
        "c": Fore.WHITE + Style.BRIGHT,
    },
    "yellow": {
        "g": Fore.YELLOW + Style.BRIGHT,
        "w": Fore.WHITE + Style.BRIGHT,
        "c": Fore.WHITE + Style.BRIGHT,
    }
}

current_color_scheme = "default"
g = Fore.GREEN + Style.BRIGHT
w = Fore.WHITE + Style.BRIGHT
c = Fore.LIGHTGREEN_EX + Style.BRIGHT


def update_color_scheme(scheme_name):
    global g, w, c, current_color_scheme
    if scheme_name in COLOR_SCHEMES:
        current_color_scheme = scheme_name
        g = COLOR_SCHEMES[scheme_name]["g"]
        w = COLOR_SCHEMES[scheme_name]["w"]
        c = COLOR_SCHEMES[scheme_name]["c"]
        return True
    return False

def apply_colors_to_banner(banner_text):
    scheme = COLOR_SCHEMES[current_color_scheme]
    return banner_text.replace("{g}", scheme["g"]).replace("{w}", scheme["w"]).replace("{c}", scheme["c"])

COLOR_CODE = {
    "RESET": "\033[0m",
    "RED": "\033[31m",
    "WHITE": "\033[37m",
    "BOLD": "\033[01m",
    "LIGHT_RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
}

LOGGED_USER = os.getenv('LOGGED_USER', 'user')



def show_loading_animation(seconds=3):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start_time = time.time()
    frame_index = 0
    
    sys.stdout.write(f"{g}[{w}Поиск{g}] ")
    sys.stdout.flush()
    
    while time.time() - start_time < seconds:
        frame = frames[frame_index % len(frames)]
        sys.stdout.write(f"\r{g}[{w}{frame}{g}] Поиск... {int(time.time() - start_time)}/{seconds}s")
        sys.stdout.flush()
        frame_index += 1
        time.sleep(0.1)
    
    sys.stdout.write(f"\r{g}[{w}✓{g}] Поиск завершен {seconds}/{seconds}s\n")
    sys.stdout.flush()

def format_nihilist_result(data, source_name=""):
    result_lines = []
    
    if source_name:
        result_lines.append(f"\n{g}=== {source_name.upper()} ===")
    
    def process_item(item, indent="", is_last=True, is_root=False):
        if isinstance(item, dict):
            items = list(item.items())
            if not items:
                return
                
            for i, (key, value) in enumerate(items):
                if key in ['user', 'header', '_id']:
                    continue
                    
                if i == len(items) - 1:
                    prefix = f"{indent}└──"
                else:
                    prefix = f"{indent}├──"
                
                if isinstance(value, dict):
                    if not value:
                        result_lines.append(f"{g}{prefix}   |  {key}: {w}{{}}")
                    else:
                        result_lines.append(f"{g}{prefix}   |  {key}:")
                        process_item(value, indent + "    ", i == len(items) - 1)
                elif isinstance(value, list):
                    if not value:
                        result_lines.append(f"{g}{prefix}   |  {key}: {w}[]")
                    else:
                        result_lines.append(f"{g}{prefix}   |  {key} [{len(value)}]")
                        for j, list_item in enumerate(value):
                            if j == len(value) - 1:
                                list_prefix = f"{indent}    └──"
                            else:
                                list_prefix = f"{indent}    ├──"
                            
                            if isinstance(list_item, dict):
                                result_lines.append(f"{g}{list_prefix}")
                                process_item(list_item, indent + "        ", j == len(value) - 1)
                            else:
                                result_lines.append(f"{g}{list_prefix}   |  {j}: {w}{list_item}")
                else:
                    result_lines.append(f"{g}{prefix}   |  {key}: {w}{value}")
        elif isinstance(item, list):
            if not item:
                return
                
            for i, list_item in enumerate(item):
                if i == len(item) - 1:
                    prefix = f"{indent}└──"
                else:
                    prefix = f"{indent}├──"
                
                if isinstance(list_item, dict):
                    result_lines.append(f"{g}{prefix}[{i}]")
                    process_item(list_item, indent + "    ", i == len(item) - 1)
                else:
                    result_lines.append(f"{g}{prefix}   |  {i}: {w}{list_item}")
    
    if isinstance(data, dict):
        process_item(data, "", True, True)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if i == len(data) - 1:
                prefix = "└──"
            else:
                prefix = "├──"
            
            if isinstance(item, dict):
                result_lines.append(f"{g}{prefix}[{i}]")
                process_item(item, "    ", i == len(data) - 1)
            else:
                result_lines.append(f"{g}{prefix}   |  {i}: {w}{item}")
    
    return '\n'.join(result_lines)

def byrevesnik_search(query, search_type):
    url = "https://atlas-in.cc/app"
    headers = {"Content-Type": "application/json"}
    data = {"token": "661709807:78X6KN5TF4", "type": search_type, "search": query, "method": "full"}
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def bigbase_search(query):
    try:
        response = requests.post(
            "https://bigbase.top/api/search",
            headers={"Authorization": "yhWCFGkla7-lT4ldeiIkVgFVYtHauETM"},
            json={"search": query, "page": 0},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def cryven_search(query, search_type):
    try:
        api_key = "jIqixbIwixiOqxgIaOqhxtBqoOs"
        url = "https://cryven.biz/api/v1/search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        search_data = {"time": "fast"}
        
        if search_type == "phone":
            search_data["phone"] = query
        elif search_type == "email":
            search_data["email"] = query
        elif search_type == "nick":
            search_data["username"] = query
        elif search_type == "telegram":
            search_data["tg"] = query
        elif search_type == "vk":
            search_data["vk"] = query
        elif search_type == "auto":
            search_data["vin"] = query
        elif search_type == "fio":
            parts = query.split()
            if len(parts) >= 2:
                search_data["name"] = parts[0]
                search_data["last_name"] = " ".join(parts[1:])
        elif search_type == "inn":
            search_data["inn"] = query
        elif search_type == "ip":
            search_data["ip"] = query
        elif search_type == "card":
            search_data["card"] = query
        elif search_type == "password":
            search_data["password"] = query
        elif search_type == "pikabu":
            search_data["pikabu"] = query
        elif search_type == "shodan":
            search_data["shodan"] = query
        else:
            search_data["query"] = query
        
        response = requests.post(url, headers=headers, json=search_data, timeout=30)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def depsearch_search(query):
    try:
        url = f"https://api.depsearch.sbs/quest={query}?token=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'results' in data:
                return data['results']
            return data
        return None
    except Exception as e:
        return None

def wikipedia_search(query):
    try:
        url = f"https://ru.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "utf8": 1,
            "srlimit": 10
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        results = []
        if "query" in data and "search" in data["query"]:
            for item in data["query"]["search"]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": BeautifulSoup(item.get("snippet", ""), "html.parser").get_text(),
                    "timestamp": item.get("timestamp", "")
                })
        
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e)}

def smtp_validator(email, mail_from="postmaster@example.com", timeout=10):
    EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    
    def is_valid_format(email):
        return bool(EMAIL_REGEX.match(email.strip()))
    
    def domain_from_email(email):
        return email.split("@", 1)[1].lower()
    
    def get_mx_records(domain):
        try:
            answers = dns.resolver.resolve(domain, "MX")
            mxs = sorted([(r.preference, str(r.exchange).rstrip(".")) for r in answers], key=lambda x: x[0])
            return [host for _, host in mxs]
        except Exception:
            return []
    
    result = {
        "email": email,
        "valid_format": is_valid_format(email),
        "mx_records": [],
        "attempts": [],
        "steps": [],
        "final_status": "invalid",
        "smtp_code": None,
    }
    
    if not result["valid_format"]:
        return result
    
    domain = domain_from_email(email)
    mx_hosts = get_mx_records(domain)
    result["mx_records"] = mx_hosts
    
    if not mx_hosts:
        return result
    
    last_exception = None
    
    for mx in mx_hosts:
        attempt_steps = []
        rcpt_code = None
        rcpt_msg = None
        
        try:
            server = smtplib.SMTP(timeout=timeout)
            code, msg = server.connect(mx, 25)
            attempt_steps.append({"connect": {"mx": mx, "code": code, "msg": str(msg)}})
            
            try:
                code, msg = server.ehlo()
                attempt_steps.append({"ehlo": {"code": code, "msg": str(msg)}})
            except Exception:
                try:
                    code, msg = server.helo()
                    attempt_steps.append({"helo": {"code": code, "msg": str(msg)}})
                except Exception as e:
                    attempt_steps.append({"helo_error": {"error": str(e)}})
            
            try:
                code, msg = server.mail(mail_from)
                attempt_steps.append({"mail_from": {"code": code, "msg": str(msg)}})
            except Exception as e:
                attempt_steps.append({"mail_from_error": {"error": str(e)}})
                try:
                    server.quit()
                except Exception:
                    pass
                server.close()
                last_exception = e
                result["attempts"].append({"mx": mx, "steps": attempt_steps})
                continue
            
            try:
                code, msg = server.rcpt(email)
                rcpt_code = int(code) if code is not None else None
                rcpt_msg = str(msg)
                attempt_steps.append({"rcpt_to": {"email": email, "code": rcpt_code, "msg": rcpt_msg}})
            except Exception as e:
                attempt_steps.append({"rcpt_error": {"error": str(e)}})
                rcpt_code = None
                rcpt_msg = str(e)
            
            try:
                code_q, msg_q = server.quit()
                attempt_steps.append({"quit": {"code": code_q, "msg": str(msg_q)}})
            except Exception as e:
                attempt_steps.append({"quit_error": {"error": str(e)}})
                try:
                    server.close()
                except Exception:
                    pass
            
            result["attempts"].append({"mx": mx, "steps": attempt_steps})
            
            if rcpt_code == 250:
                result["final_status"] = "valid"
                result["smtp_code"] = rcpt_code
                result["steps"] = attempt_steps
                return result
            else:
                if rcpt_code is not None:
                    result["smtp_code"] = rcpt_code
                last_exception = None
                continue
                
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout, socket.gaierror) as e:
            attempt_steps.append({"error": str(e)})
            result["attempts"].append({"mx": mx, "steps": attempt_steps})
            last_exception = e
            continue
        except Exception as e:
            attempt_steps.append({"error": str(e)})
            result["attempts"].append({"mx": mx, "steps": attempt_steps})
            last_exception = e
            continue
    
    if result["attempts"]:
        result["steps"] = result["attempts"][-1]["steps"]
    if result["smtp_code"] is None and last_exception is not None:
        result["error"] = str(last_exception)
    
    return result

async def phone_search():
    query = input(f"{g}Введите номер телефона: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "phone")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "phone")
    depsearch_data = depsearch_search(query)
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if depsearch_data:
        print(f"\n{g}=== DEPSEARCH ===")
        print(format_nihilist_result(depsearch_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data and not depsearch_data:
        print(f"{w}Данные не найдены")

async def email_search():
    query = input(f"{g}Введите email: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "email")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "email")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")
        
async def nick_search():
    query = input(f"{g}Введите никнейм: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "nick")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "nick")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def telegram_search():
    query = input(f"{g}Введите Telegram username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "telegram")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "telegram")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def vk_search():
    query = input(f"{g}Введите VK ID/username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "vk")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "vk")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def auto_search():
    query = input(f"{g}Введите номер автомобиля: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "auto")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "auto")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def fio_search():
    query = input(f"{g}Введите ФИО: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "fio")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "fio")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def inn_search():
    query = input(f"{g}Введите ИНН: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "inn")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "inn")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def snils_search():
    query = input(f"{g}Введите СНИЛС: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "snils")
    bigbase_data = bigbase_search(query)
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if not byrevesnik_data and not bigbase_data:
        print(f"{w}Данные не найдены")

async def ip_search():
    query = input(f"{g}Введите IP-адрес: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    byrevesnik_data = byrevesnik_search(query, "ip")
    bigbase_data = bigbase_search(query)
    cryven_data = cryven_search(query, "ip")
    
    if byrevesnik_data:
        print(f"\n{g}=== BYREVESNIK ===")
        print(format_nihilist_result(byrevesnik_data))
    
    if bigbase_data:
        print(f"\n{g}=== BIGBASE ===")
        print(format_nihilist_result(bigbase_data))
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    
    if not byrevesnik_data and not bigbase_data and not cryven_data:
        print(f"{w}Данные не найдены")

async def ok_search():
    phone = input(f"{g}Введите номер телефона: {w}").strip()
    if not phone: return
    
    show_loading_animation(3)
    
    OK_LOGIN_URL = 'https://www.ok.ru/dk?st.cmd=anonymMain&st.accRecovery=on&st.error=errors.password.wrong'
    OK_RECOVER_URL = 'https://www.ok.ru/dk?st.cmd=anonymRecoveryAfterFailedLogin&st._aid=LeftColumn_Login_ForgotPassword'
    USERAGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    ]
    
    try:
        session = requests.Session()
        headers = {"User-Agent": random.choice(USERAGENTS)}
        login_response = session.get(f'{OK_LOGIN_URL}&st.email={phone}', headers=headers, timeout=10)
        if login_response.status_code != 200:
            print(f"{w}Не удалось подключиться к Одноклассникам")
            return
        
        request = session.get(OK_RECOVER_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(request.content, 'html.parser')
        
        if soup.find('div', {'data-l': 'registrationContainer,offer_contact_rest'}):
            account_info = soup.find('div', {'class': 'ext-registration_tx taCenter'})
            name = account_info.find('div', {'class': 'ext-registration_username_header'})
            name = name.get_text() if name else "Не указано"
            account_details = account_info.findAll('div', {'class': 'lstp-t'})
            profile_info = account_details[0].get_text() if account_details and len(account_details) >= 1 else "Не указано"
            profile_registered = account_details[1].get_text() if account_details and len(account_details) >= 2 else "Не указано"
            
            result = {
                "found": True,
                "phone": phone,
                "name": name,
                "profile_info": profile_info,
                "registered": profile_registered
            }
            
            print(f"\n{g}=== ОДНОКЛАССНИКИ ===")
            print(f"{g}├─ phone: {w}{phone}")
            print(f"{g}├─ name: {w}{name}")
            print(f"{g}├─ profile_info: {w}{profile_info}")
            print(f"{g}└─ registered: {w}{profile_registered}")
        else:
            print(f"{w}Аккаунт не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def tiktok_search():
    username = input(f"{g}Введите @username TikTok: {w}").replace('@', '').strip()
    if not username: return
    
    show_loading_animation(3)
    
    headers = {
        "Host": "www.tiktok.com",
        "sec-ch-ua": "\" Not A;Brand\";v\u003d\"99\", \"Chromium\";v\u003d\"99\", \"Google Chrome\";v\u003d\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q\u003d0.9,image/avif,image/webp,image/apng,*/*;q\u003d0.8,application/signed-exchange;v\u003db3;q\u003d0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q\u003d0.9"
    }
    
    try:
        response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers)
        
        if response.status_code != 200:
            print(f"{w}Ошибка запроса: {response.status_code}")
            return
        
        data = str(response.text.split('webapp.user-detail"')[1]).split('"RecommendUserList"')[0]
        
        user_info = {
            "id": str(data.split('id":"')[1]).split('",')[0],
            "name": str(data.split('nickname":"')[1]).split('",')[0],
            "bio": str(data.split('signature":"')[1]).split('",')[0],
            "country": str(data.split('region":"')[1]).split('",')[0],
            "private": str(data.split('privateAccount":')[1]).split(',"')[0],
            "followers": str(data.split('followerCount":')[1]).split(',"')[0],
            "following": str(data.split('followingCount":')[1]).split(',"')[0],
            "likes": str(data.split('heart":')[1]).split(',"')[0],
            "videos": str(data.split('videoCount":')[1]).split(',"')[0],
            "secUid": str(data.split('secUid":"')[1]).split('"')[0]
        }
        
        print(f"\n{g}=== TIKTOK ===")
        for key, value in user_info.items():
            print(f"{g}├─ {key}: {w}{value}")
            
    except Exception as e:
        print(f"{w}Ошибка: Неверный username или пользователь не найден")

async def instagram_search():
    query = input(f"{g}Введите Instagram username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://www.instagram.com/{query}/?__a=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            user_data = data.get('graphql', {}).get('user', {})
            
            result = {
                "username": user_data.get('username'),
                "full_name": user_data.get('full_name'),
                "biography": user_data.get('biography'),
                "followers": user_data.get('edge_followed_by', {}).get('count'),
                "following": user_data.get('edge_follow', {}).get('count'),
                "posts": user_data.get('edge_owner_to_timeline_media', {}).get('count'),
                "private": user_data.get('is_private'),
                "verified": user_data.get('is_verified'),
                "profile_pic": user_data.get('profile_pic_url_hd')
            }
            
            print(f"\n{g}=== INSTAGRAM ===")
            for key, value in result.items():
                print(f"{g}├─ {key}: {w}{value}")
        else:
            print(f"{w}Пользователь не найден или профиль приватный")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def mac_search():
    query = input(f"{g}Введите MAC-адрес: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://api.macvendors.com/{query}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            result = {"mac": query, "vendor": response.text}
            print(f"\n{g}=== MAC VENDORS ===")
            print(f"{g}├─ mac: {w}{query}")
            print(f"{g}└─ vendor: {w}{response.text}")
        else:
            print(f"{w}Производитель не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def github_search():
    query = input(f"{g}Введите GitHub username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://api.github.com/users/{query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{g}=== GITHUB ===")
            for key, value in data.items():
                if value:
                    print(f"{g}├─ {key}: {w}{value}")
        else:
            print(f"{w}Пользователь не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def wikipedia_search_menu():
    query = input(f"{g}Введите запрос для поиска в Wikipedia: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    result = wikipedia_search(query)
    
    if "error" in result:
        print(f"{w}Ошибка: {result['error']}")
    else:
        print(f"\n{g}=== WIKIPEDIA ===")
        print(f"{g}├─ query: {w}{query}")
        print(f"{g}├─ count: {w}{result['count']}")
        
        for i, item in enumerate(result['results'], 1):
            print(f"\n{g}├─ Result #{i}")
            print(f"{g}│  ├─ title: {w}{item['title']}")
            print(f"{g}│  ├─ snippet: {w}{item['snippet'][:100]}...")
            if item['timestamp']:
                print(f"{g}│  └─ timestamp: {w}{item['timestamp']}")

async def steam_search():
    query = input(f"{g}Введите Steam ID/никнейм: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        if query.isdigit() and len(query) == 17:
            steam_id = query
            url = f"https://steamcommunity.com/profiles/{steam_id}"
        else:
            url = f"https://steamcommunity.com/id/{query}"
            
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            persona_name = soup.find('span', {'class': 'actual_persona_name'})
            online_state = soup.find('div', {'class': 'profile_in_game_header'})
            location = soup.find('div', {'class': 'header_real_name'})
            level = soup.find('span', {'class': 'friendPlayerLevelNum'})
            
            print(f"\n{g}=== STEAM ===")
            print(f"{g}├─ url: {w}{url}")
            print(f"{g}├─ persona_name: {w}{persona_name.text.strip() if persona_name else 'Не указано'}")
            print(f"{g}├─ online_state: {w}{online_state.text.strip() if online_state else 'Не в сети'}")
            print(f"{g}├─ location: {w}{location.text.strip() if location else 'Не указано'}")
            print(f"{g}└─ level: {w}{level.text.strip() if level else 'Не указано'}")
        else:
            print(f"{w}Профиль не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def company_search():
    query = input(f"{g}Введите название компании: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://api.ofdata.ru/v2/search?key=KBnpz1CHKNngFXxK&by=name&obj=org&query={query}"
        response = requests.get(url)
        data = response.json()
        print(f"\n{g}=== COMPANY INFO ===")
        print(format_nihilist_result(data))
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def hlr_search():
    def validate_phone_number(phone_number: str):
        try:
            return phonenumbers.parse(phone_number)
        except:
            return None
    
    phone = input(f"{g}Введите номер телефона: {w}").strip()
    if not phone: return
    
    show_loading_animation(3)
    
    try:
        parsed_number = validate_phone_number(phone)
        if not parsed_number:
            print(f"{w}Неверный номер")
            return
            
        clean_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        hlr_results = {}
        
        try:
            url = f"https://www.freephonenum.com/validate/{clean_number[1:]}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "valid" in response.text.lower():
                    hlr_results["freephonenum"] = "Valid"
                elif "invalid" in response.text.lower():
                    hlr_results["freephonenum"] = "Invalid"
                else:
                    hlr_results["freephonenum"] = "Unknown"
        except:
            hlr_results["freephonenum"] = "Error"
        
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            hlr_results["carrier"] = carrier_name if carrier_name else "Unknown"
        except:
            hlr_results["carrier"] = "Unknown"
        
        try:
            url = f"https://www.phonevalidator.com/result?phone={clean_number}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "active" in response.text.lower():
                    hlr_results["status"] = "Active"
                elif "inactive" in response.text.lower():
                    hlr_results["status"] = "Inactive"
                else:
                    hlr_results["status"] = "Unknown"
        except:
            hlr_results["status"] = "Unknown"
        
        if hlr_results.get("status") == "Active" or hlr_results.get("freephonenum") == "Valid":
            overall_status = "Active"
        elif hlr_results.get("status") == "Inactive" or hlr_results.get("freephonenum") == "Invalid":
            overall_status = "Inactive"
        else:
            overall_status = "Unknown"
        
        print(f"\n{g}=== HLR SEARCH ===")
        print(f"{g}├─ phone_number: {w}{clean_number}")
        print(f"{g}├─ hlr_status: {w}{overall_status}")
        print(f"{g}├─ carrier: {w}{hlr_results.get('carrier', 'Unknown')}")
        print(f"{g}├─ country: {w}{geocoder.description_for_number(parsed_number, 'en')}")
        print(f"{g}└─ number_type: {w}{'Mobile' if phonenumbers.number_type(parsed_number) == 1 else 'Other'}")
            
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def whatsapp_search():
    query = input(f"{g}Введите номер телефона: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://wa.me/{query}"
        response = requests.head(url, allow_redirects=True, timeout=5)
        if 'message/' in response.url:
            result = {"phone": query, "registered": False}
        else:
            parsed_url = urlparse(response.url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            name = query_params.get('text', [None])[0]
            result = {"phone": query, "registered": True, "name": name}
        
        print(f"\n{g}=== WHATSAPP ===")
        print(f"{g}├─ phone: {w}{query}")
        print(f"{g}├─ registered: {w}{result['registered']}")
        if result.get('name'):
            print(f"{g}└─ name: {w}{result['name']}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def domain_search():
    query = input(f"{g}Введите домен: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        whois_url = f"https://api.hackertarget.com/whois/?q={query}"
        whois_response = requests.get(whois_url, timeout=10)
        
        dns_url = f"https://api.hackertarget.com/dnslookup/?q={query}"
        dns_response = requests.get(dns_url, timeout=10)
        
        print(f"\n{g}=== DOMAIN INFO ===")
        print(f"{g}├─ domain: {w}{query}")
        print(f"{g}├─ whois: {w}{'Available' if whois_response.status_code == 200 else 'Error'}")
        print(f"{g}└─ dns_records: {w}{'Available' if dns_response.status_code == 200 else 'Error'}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def dork_search():
    query = input(f"{g}Введите запрос для дорков: {w}").strip()
    if not query: return
    
    show_loading_animation(2)
    
    dorks = [
        f'"{query}"',
        f'"{query}" site:github.com',
        f'"{query}" site:twitter.com',
        f'"{query}" filetype:pdf',
        f'"{query}" "password" OR "login"',
        f'"{query}" site:pastebin.com',
        f'"{query}" site:reddit.com',
        f'"{query}" intitle:"index of"',
        f'"{query}" inurl:admin',
        f'"{query}" filetype:sql'
    ]
    
    print(f"\n{g}=== GOOGLE DORKS ===")
    print(f"{g}├─ query: {w}{query}")
    for i, dork in enumerate(dorks):
        print(f"{g}├─ dork_{i+1}: {w}{dork}")

async def port_scanner():
    query = input(f"{g}Введите IP или домен: {w}").strip()
    if not query: return
    
    show_loading_animation(5)
    
    ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080, 8443]
    open_ports = []
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((query, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    
    print(f"\n{g}=== PORT SCANNER ===")
    print(f"{g}├─ target: {w}{query}")
    print(f"{g}├─ scanned_ports: {w}{len(ports)}")
    print(f"{g}└─ open_ports: {w}{open_ports if open_ports else 'None'}")

async def coordinates_search():
    query = input(f"{g}Введите координаты (широта,долгота): {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        lat, lon = map(float, query.split(","))
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        print(f"\n{g}=== GEOLOCATION ===")
        print(f"{g}├─ coordinates: {w}{query}")
        print(f"{g}└─ address: {w}{data.get('display_name', 'Не найден')}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def card_search():
    query = input(f"{g}Введите BIN (первые 6 цифр карты): {w}").strip()
    if not query or not query.isdigit() or len(query) < 6: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://lookup.binlist.net/{query[:6]}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{g}=== BIN LOOKUP ===")
            for key, value in data.items():
                if value:
                    print(f"{g}├─ {key}: {w}{value}")
        else:
            print(f"{w}BIN не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def ai_analysis():
    query = input(f"{g}Введите данные для AI анализа: {w}").strip()
    if not query: return
    
    show_loading_animation(5)
    
    try:
        analysis_result = {
            "input": query,
            "analysis": {
                "sentiment": "нейтральный",
                "entities": ["данные", "анализ"],
                "language": "русский",
                "confidence": 0.85
            },
            "recommendations": [
                "Провести дополнительный поиск по найденным сущностям",
                "Проверить связанные данные",
                "Использовать другие методы поиска"
            ]
        }
        
        print(f"\n{g}=== AI ANALYSIS ===")
        print(f"{g}├─ input: {w}{query}")
        print(f"{g}├─ sentiment: {w}нейтральный")
        print(f"{g}├─ language: {w}русский")
        print(f"{g}├─ confidence: {w}0.85")
        print(f"{g}└─ recommendations: {w}3 рекомендации")
        
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def smtp_validator_menu():
    email = input(f"{g}Введите email для проверки: {w}").strip()
    if not email: return
    
    show_loading_animation(5)
    
    result = smtp_validator(email)
    
    print(f"\n{g}=== SMTP VALIDATOR ===")
    print(f"{g}├─ email: {w}{result['email']}")
    print(f"{g}├─ format: {w}{'валидный' if result['valid_format'] else 'невалидный'}")
    print(f"{g}├─ status: {w}{result['final_status']}")
    
    if result['mx_records']:
        print(f"{g}├─ mx_records: {w}{', '.join(result['mx_records'])}")
    
    if result.get('smtp_code'):
        print(f"{g}└─ smtp_code: {w}{result['smtp_code']}")

async def mailer():
    receiver = input(f"{g}Введите почту получателя: {w}")
    subject = input(f"{g}Введите тему письма: {w}")
    body = input(f"{g}Введите текст письма: {w}")
    
    show_loading_animation(3)
    
    senders = {
        "miranovseverov@gmail.com": "kdbc vmdb djxf pmiq",
        "alenaveterov@gmail.com": "hmiq xwmr yfmw prsa",
        "linadurov@gmail.com": "gsbp xyts brbu dlpw",
        "dlatt6677@gmail.com": "usun ruef otzx zcrh"
    }
    
    print(f"\n{g}=== MAILER ===")
    print(f"{g}├─ receiver: {w}{receiver}")
    print(f"{g}├─ subject: {w}{subject}")
    print(f"{g}└─ status: {w}Используются тестовые аккаунты")

class NihilistBomber:
    def __init__(self):
        self.urls = [
            'https://oauth.telegram.org/auth/request?bot_id=1852523856&origin=https%3A%2F%2Fcabinet.presscode.app&embed=1&return_to=https%3A%2F%2Fcabinet.presscode.app%2Flogin',
            'https://translations.telegram.org/auth/request',
            'https://oauth.telegram.org/auth?bot_id=5444323279&origin=https%3A%2F%2Ffragment.com&request_access=write&return_to=https%3A%2F%2Ffragment.com%2F',
            'https://oauth.telegram.org/auth?bot_id=1199558236&origin=https%3A%2F%2Fbot-t.com&embed=1&request_access=write&return_to=https%3A%2F%2Fbot-t.com%2Flogin',
            'https://oauth.telegram.org/auth/request?bot_id=1093384146&origin=https%3A%2F%2Foff-bot.ru&embed=1&request_access=write&return_to=https%3A%2F%2Foff-bot.ru%2Fregister%2Fconnected-accounts%2Fsmodders_telegram%2F%3Fsetup%3D1'
        ]
        self.proxies_list = [
            '8.218.149.193:80',
            '47.57.233.126:80',
            '47.243.70.197:80',
            '8.222.193.208:80'
        ]
    
    def send_request(self, url, phone_number):
        try:
            proxies = {'http': random.choice(self.proxies_list)}
            user = fake_useragent.UserAgent().random
            headers = {'user-agent': user}
            response = requests.post(url, headers=headers, data={'phone': phone_number}, timeout=10)
            
            if response.status_code == 200:
                print(f"{g}[+] Код отправлен на {url}")
            else:
                print(f"{g}[!] Ошибка на {url} - {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"{g}[!] Ошибка на {url}: {e}")
            return False
    
    def start_bombing(self, phone_number):
        print(f"{g}Запуск TG Bomber на номер: {phone_number}")
        
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                futures = []
                for url in self.urls:
                    for _ in range(3):
                        futures.append(executor.submit(self.send_request, url, phone_number))
                
                for future in concurrent.futures.as_completed(futures):
                    future.result()
            
            time.sleep(random.uniform(0.3, 0.7))

async def spam_codes():
    phone = input(f"{g}Введите номер телефона: {w}")
    show_loading_animation(2)
    
    bomber = NihilistBomber()
    bomber.start_bombing(phone)

async def bomber():
    print(f"\n{g}=== BOMBER ===")
    print(f"{g}├─ status: {w}В разработке")
    print(f"{g}└─ note: {w}Функция будет добавлена в следующем обновлении")

async def exif_search():
    query = input(f"{g}Введите путь к изображению: {w}").strip()
    if not os.path.exists(query): return
    
    show_loading_animation(3)
    
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        image = Image.open(query)
        exifdata = image.getexif()
        
        print(f"\n{g}=== EXIF ===")
        print(f"{g}├─ file: {w}{query}")
        
        for tag_id, value in exifdata.items():
            tag = TAGS.get(tag_id, tag_id)
            print(f"{g}├─ {tag}: {w}{value}")
            
    except ImportError:
        print(f"{w}Требуется установить библиотеку Pillow: pip install Pillow")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def db_cleaner():
    def clean_directory(directory: str, file_patterns: list = None) -> dict:
        if file_patterns is None:
            file_patterns = ['*.csv', '*.txt', '*.sql', '*.json', '*.db', '*.sqlite']
        
        results = {'processed': 0, 'success': 0, 'errors': 0}
        
        import pathlib
        path = pathlib.Path(directory)
        
        for pattern in file_patterns:
            for file_path in path.glob(pattern):
                results['processed'] += 1
                try:
                    os.remove(file_path)
                    results['success'] += 1
                except Exception as e:
                    results['errors'] += 1
        
        return results
    
    show_loading_animation(2)
    
    folders = ["byrevesnik_results", "bigbase_results", "results", "user_databases", "html_dumps"]
    
    print(f"\n{g}=== DATABASE CLEANER ===")
    for folder in folders:
        if os.path.exists(folder):
            results = clean_directory(folder)
            print(f"{g}├─ {folder}: {w}удалено {results['success']}, ошибок {results['errors']}")
    
    print(f"{g}└─ status: {w}Очистка завершена")

async def web_crawler():
    query = input(f"{g}Введите URL: {w}").strip()
    if not query: return
    
    show_loading_animation(4)
    
    try:
        response = requests.get(query, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        urls = []
        for link in links[:10]:
            href = link.get('href')
            if href:
                urls.append(href[:50] + "..." if len(href) > 50 else href)
        
        print(f"\n{g}=== WEB CRAWLER ===")
        print(f"{g}├─ url: {w}{query}")
        print(f"{g}├─ links_found: {w}{len(links)}")
        for i, url in enumerate(urls):
            print(f"{g}├─ link_{i+1}: {w}{url}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def create_db():
    show_loading_animation(2)
    
    print(f"\n{g}=== CREATE DATABASE ===")
    db_name = input(f"{g}Введите название БД: {w}").strip()
    if not db_name: return
    
    import csv
    columns_input = input(f"{g}Введите названия колонок через запятую: {w}").strip()
    
    if not columns_input:
        columns = ["id", "имя", "возраст", "город"]
    else:
        columns = [col.strip() for col in columns_input.split(",")]
    
    os.makedirs("user_databases", exist_ok=True)
    csv_file = f"user_databases/{db_name}.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
    
    print(f"{g}├─ database: {w}{db_name}")
    print(f"{g}├─ file: {w}{csv_file}")
    print(f"{g}├─ columns: {w}{len(columns)}")
    print(f"{g}└─ created: {w}{datetime.datetime.now().isoformat()}")

async def html_dumper():
    query = input(f"{g}Введите URL: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        response = requests.get(query, timeout=10)
        os.makedirs("html_dumps", exist_ok=True)
        filename = f"html_dumps/{query.replace('://', '_').replace('/', '_')}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"\n{g}=== HTML DUMPER ===")
        print(f"{g}├─ url: {w}{query}")
        print(f"{g}└─ saved_as: {w}{filename}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

class ReRendi:
    def __init__(self, file_name: str) -> None:
        self.file_name = file_name
        self.content = ""
        self.layers_removed = 0

    def _read_file(self, fname: str) -> str:
        try:
            with open(fname, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        except Exception as e:
            raise

    def _check_input_file(self, content: str = None) -> bool:
        try:
            check_content = content if content else self.content
            pattern = r"_=lambda __:__import__\('marshal'\)\.loads\(__import__\('gzip'\)\.decompress\(__import__\('lzma'\)\.decompress\(__import__\('zlib'\)\.decompress\(__import__\('base64'\)\.b64decode\(__\[::-1\]\)\)\)\)\)"
            match = re.search(pattern, check_content)
            return bool(match)
        except Exception as e:
            return False

    def _extract_encoded_data(self, content: str = None) -> str:
        try:
            check_content = content if content else self.content
            pattern = r"exec\(_\('(.+?)'\)\)"
            match = re.search(pattern, check_content)
            if not match:
                return None
            return match.group(1)
        except Exception as e:
            return None

    def _deobfuscate_single_layer(self, content: str) -> str:
        try:
            if not self._check_input_file(content):
                return None

            encoded_data = self._extract_encoded_data(content)
            if not encoded_data:
                return None

            reversed_data = encoded_data[::-1]
            try:
                decoded = base64.b64decode(reversed_data)
                decompressed_zlib = zlib.decompress(decoded)
                decompressed_lzma = lzma.decompress(decompressed_zlib)
                decompressed_gzip = gzip.decompress(decompressed_lzma)
                deobfuscated = marshal.loads(decompressed_gzip)

                if isinstance(deobfuscated, bytes):
                    try:
                        return deobfuscated.decode("utf-8")
                    except UnicodeDecodeError:
                        return deobfuscated.decode("cp1251")
                return str(deobfuscated)

            except Exception as e:
                return None

        except Exception:
            return None

    def deobfuscate(self):
        try:
            self.content = self._read_file(self.file_name)
            current_content = self.content
            self.layers_removed = 0

            while True:
                deobfuscated = self._deobfuscate_single_layer(current_content)
                if not deobfuscated:
                    break
                current_content = deobfuscated
                self.layers_removed += 1

            if self.layers_removed > 0:
                return current_content, self.layers_removed
            else:
                return None, 0

        except Exception as e:
            return None, 0

async def deobfuscator():
    file_name = input(f"{g}Введите путь к файлу: {w}").strip()
    if not os.path.exists(file_name): return
    
    show_loading_animation(4)
    
    deobfuscator = ReRendi(file_name=file_name)
    deobfuscated_code, layers = deobfuscator.deobfuscate()

    if deobfuscated_code:
        print(f"\n{g}=== DEOBFUSCATOR ===")
        print(f"{g}├─ file: {w}{file_name}")
        print(f"{g}├─ layers_removed: {w}{layers}")
        print(f"{g}└─ status: {w}Успешно")
        
        save = input(f"\n{g}Сохранить результат? (y/n): {w}").lower()
        if save == 'y':
            output = input(f"{g}Имя файла: {w}").strip()
            with open(output, "w", encoding="utf-8") as f:
                f.write(f"#Deobfuscated by Nihilist (Removed {layers} layers)\n" + deobfuscated_code)
            print(f"{g}Сохранено: {output}")
    else:
        print(f"{w}Не удалось деобфусцировать")

def zlb(in_):
    return zlib.compress(in_)
def b16(in_):
    return base64.b16encode(in_)
def b32(in_):
    return base64.b32encode(in_)
def b64(in_):
    return base64.b64encode(in_)
def mar(in_):
    return marshal.dumps(compile(in_, "<x>", "exec"))

async def obfuscator():
    file_name = input(f"{g}Введите путь к файлу: {w}").strip()
    if not os.path.exists(file_name): return
    
    show_loading_animation(3)
    
    with open(file_name, "r", encoding="utf-8") as f:
        data = f.read()
    
    print(f"\n{g}Выберите метод:")
    print(f"{w}1. Marshal\n2. Zlib\n3. Base64\n4. Base64 + Zlib\n5. Base64 + Marshal")
    choice = input(f"{g}Выбор: {w}").strip()
    
    if choice == '1':
        encoded = "exec((_)(%s))" % repr(mar(data.encode('utf8'))[::-1])
        header = "_ = lambda __ : __import__('marshal').loads(__[::-1]);"
    elif choice == '2':
        encoded = "exec((_)(%s))" % repr(zlb(data.encode('utf8'))[::-1])
        header = "_ = lambda __ : __import__('zlib').decompress(__[::-1]);"
    elif choice == '3':
        encoded = "exec((_)(%s))" % repr(b64(data.encode('utf8'))[::-1])
        header = "_ = lambda __ : __import__('base64').b64decode(__[::-1]);"
    elif choice == '4':
        encoded = "exec((_)(%s))" % repr(b64(zlb(data.encode('utf8')))[::-1])
        header = "_ = lambda __ : __import__('zlib').decompress(__import__('base64').b64decode(__[::-1]));"
    elif choice == '5':
        encoded = "exec((_)(%s))" % repr(b64(mar(data.encode('utf8')))[::-1])
        header = "_ = lambda __ : __import__('marshal').loads(__import__('base64').b64decode(__[::-1]));"
    else:
        print(f"{w}Неверный выбор")
        return
    
    output = file_name.replace(".py", "_obfuscated.py")
    with open(output, "w") as f:
        f.write(header + encoded)
    
    print(f"\n{g}=== OBFUSCATOR ===")
    print(f"{g}├─ original: {w}{file_name}")
    print(f"{g}├─ obfuscated: {w}{output}")
    print(f"{g}└─ method: {w}{choice}")

async def link_logger_check():
    query = input(f"{g}Введите URL для проверки: {w}").strip()
    if not query: return
    
    show_loading_animation(4)
    
    VIRUSTOTAL_API_KEY = "YOUR_API_KEY_HERE"
    
    try:
        url = f"https://www.virustotal.com/api/v3/urls"
        headers = {
            "x-apikey": VIRUSTOTAL_API_KEY,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"url": query}
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('data', {}).get('id')
            
            url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {}).get('attributes', {}).get('stats', {})
                
                print(f"\n{g}=== LINK LOGGER CHECK ===")
                print(f"{g}├─ url: {w}{query}")
                print(f"{g}├─ malicious: {w}{stats.get('malicious', 0)}")
                print(f"{g}├─ suspicious: {w}{stats.get('suspicious', 0)}")
                print(f"{g}├─ undetected: {w}{stats.get('undetected', 0)}")
                print(f"{g}└─ harmless: {w}{stats.get('harmless', 0)}")
            else:
                print(f"{w}Ошибка получения результатов")
        else:
            print(f"{w}Ошибка отправки URL")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def proxy_getter():
    show_loading_animation(4)
    
    try:
        url = "https://www.proxynova.com/api/proxy-list/"
        response = requests.get(url, timeout=10)
        data = response.json()
        proxies = []
        if 'data' in data:
            for proxy in data['data'][:10]:
                ip = proxy.get('ip', '')
                port = proxy.get('port', '')
                proxies.append(f"{ip}:{port}")
        
        print(f"\n{g}=== PROXY GETTER ===")
        print(f"{g}├─ source: {w}proxynova")
        for i, proxy in enumerate(proxies):
            print(f"{g}├─ proxy_{i+1}: {w}{proxy}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def ai_analysis_with_mistral():
    MISTRAL_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
    query = input(f"{g}Введите запрос для поиска в BigBase: {w}").strip()
    if not query: return
    
    show_loading_animation(8)
    
    bigbase_data = bigbase_search(query)
    
    if not bigbase_data:
        print(f"{w}Данные в BigBase не найдены")
        return
    
    data_for_ai = json.dumps(bigbase_data, ensure_ascii=False, indent=2)
    
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Проанализируй данные из BigBase и проведи глубокий OSINT анализ:

ДАННЫЕ ИЗ BIGBASE:
{data_for_ai}

ВОТ ЧТО НУЖНО СДЕЛАТЬ:

1. ИДЕНТИФИКАЦИЯ ЛИЧНОСТЕЙ:
- Определи, сколько уникальных личностей найдено в данных
- Раздели данные по разным людям, если номер/емейл используется несколькими лицами
- Сопоставь совпадающие данные для каждой личности

2. СОРТИРОВКА ДАННЫХ:
- Персональные данные (ФИО, дата рождения, документы)
- Контактные данные (телефоны, email)
- Социальные сети и мессенджеры
- Географические данные (адреса, локации)
- Финансовые данные (карты, счета)
- Транспортные данные (авто, VIN)
- Онлайн-активность (аккаунты, ники)
- Работа и образование

3. ОЦЕНКА ДОСТОВЕРНОСТИ:
- Определи надежность каждого источника данных
- Оцени вероятность совпадений/ошибок
- Выяви противоречия в данных

4. АНАЛИЗ РИСКОВ:
- Выяви потенциальные угрозы и уязвимости
- Оцени уровень приватности личности
- Определи возможные связи с мошенничеством

ФОРМАТ ВЫВОДА:

{g}[ИСТОЧНИКИ ДАННЫХ]
{w}Перечисли все найденные источники с оценкой достоверности

{g}[ЛИЧНОСТЬ 1] (если найдено несколько)
{w}Данные этой личности...

{g}[ЛИЧНОСТЬ 2]
{w}Данные второй личности...

{g}[КАТЕГОРИЗИРОВАННЫЕ ДАННЫХ]
{w}Структурированные данные по категориям

{g}[ПРОТИВОРЕЧИЯ И АНОМАЛИИ]
{w}Выявленные несоответствия

{g}[ОЦЕНКА ДОСТОВЕРНОСТИ]
{w}Общая оценка надежности данных

{g}[ВЫВОДЫ И РЕКОМЕНДАЦИИ]
{w}Ключевые выводы и дальнейшие шаги

Важно: Если данных недостаточно для каких-то разделов - пропусти их. Будь максимально точным и критичным к данным."""
    
    data = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 3000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=40)
        
        if response.status_code == 200:
            result = response.json()
            analysis_text = result["choices"][0]["message"]["content"]
            
            print(f"\n{g}=== AI АНАЛИЗ (MISTRAL) ===")
            
            lines = analysis_text.split('\n')
            for line in lines:
                if line.startswith('[') and ']' in line:
                    print(f"{g}{line}")
                elif line.startswith('- ') or line.startswith('• '):
                    print(f"{w}{line}")
                elif ':' in line and len(line.split(':')) > 1:
                    parts = line.split(':', 1)
                    print(f"{g}{parts[0]}:{w}{parts[1]}")
                else:
                    print(f"{w}{line}")
            
            save = input(f"\n{g}Сохранить анализ? (y/n): {w}").lower()
            if save == 'y':
                filename = f"ai_analysis_{int(time.time())}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"AI Analysis Report\n")
                    f.write(f"Время: {datetime.datetime.now()}\n")
                    f.write(f"Запрос: {query}\n\n")
                    f.write(analysis_text)
                print(f"{g}Анализ сохранен в {filename}")
                
        else:
            print(f"{w}Ошибка API: {response.status_code}")
            print(f"{w}Ответ: {response.text}")
            
    except Exception as e:
        print(f"{g}Ошибка: {e}")

def print_banner():
    banner = f"""{g}╔═════════════════════════════════════════════════════════════════════════════════════╗    ╔═══════════════════════════════════════════════|{w}ГЛОБАЛЬНЫЙ ПОИСК{g}|══════════════════════════════════════════════╗   
{g}║                                                                                     ║    ║                                                                                                               ║   
{g}║{w}      ███▄▄▄▄    ▄█     ▄█    █▄     ▄█   ▄█        ▄█  {g}   ▄████████ {w}    ███      {g}   ║    ║   [{w}01{g}] {w}Поиск по Номеру{g}             [{w}15{g}] {w}Поиск по MAC{g}                  [{w}29{g}] {w}Поиск по VIN Автомобиля{g}            ║   
{g}║{w}      ███▀▀▀██▄ ███    ███    ███   ███  ███       ███  {g}  ███    ███ {w}▀█████████▄  {g}   ║    ║   [{w}02{g}] {w}Поиск по Email{g}              [{w}16{g}] {w}Поиск по Github{g}               [{w}30{g}] {w}Поиск по Pikabu{g}                    ║   
{g}║{w}      ███   ███ ███▌   ███    ███   ███▌ ███       ███▌ {g}  ███    █▀  {w}   ▀███▀▀██  {g}   ║    ║   [{w}03{g}] {w}Поиск по никнейму{g}           [{w}17{g}] {w}Поиск по Wikipedia{g}            [{w}31{g}] {w}Поиск через Shodan{g}                 ║   
{g}║{w}      ███   ███ ███▌  ▄███▄▄▄▄███▄▄ ███▌ ███       ███▌ {g}  ███        {w}    ███   ▀  {g}   ║    ║   [{w}04{g}] {w}Поиск по Телеграмм{g}          [{w}18{g}] {w}Поиск по Steam{g}                [{w}32{g}] {w}Поиск по паролю{g}                    ║   
{g}║{w}      ███   ███ ███▌ ▀▀███▀▀▀▀███▀  ███▌ ███       ███▌ {g}▀███████████ {w}    ███      {g}   ║    ║   [{w}05{g}] {w}Поиск по ВК{g}                 [{w}19{g}] {w}Поиск по Компаниям{g}            [{w}33{g}] {w}Поиск по ИНН (Казахстан){g}           ║   
{g}║{w}      ███   ███ ███    ███    ███   ███  ███       ███  {g}         ███ {w}    ███      {g}   ║    ║   [{w}06{g}] {w}Поиск по Номеру Авто{g}        [{w}20{g}] {w}HLR Запрос{g}                    [{w}34{g}] {w}Поиск по Minecraft{g}                 ║   
{g}║{w}      ███   ███ ███    ███    ███   ███  ███▌    ▄ ███  {g}   ▄█    ███ {w}    ███      {g}   ║    ║   [{w}07{g}] {w}Поиск по ФИО{g}                [{w}21{g}] {w}Поиск по WhatsApp{g}             [{w}35{g}] {w}Парсинг Чатов{g}                      ║   
{g}║{w}       ▀█   █▀  █▀     ███    █▀    █▀   █████▄▄██ █▀   {g} ▄████████▀  {w}   ▄████▀    {g}   ║    ║   [{w}08{g}] {w}Поиск по ИНН{g}                [{w}22{g}] {w}Поиск по Домену{g}               [{w}36{g}] {w}Слежка{g}                             ║   
{g}║{w}                                    ▀                                              {g}  ║    ║   [{w}09{g}] {w}Поиск по Паспорту{g}           [{w}23{g}] {w}Поиск по Доркам{g}               [{w}37{g}] {w}Поиск по Перелётам{g}                 ║   
{g}║═════════════════════════════════════════════════════════════════════════════════════║    ║   [{w}10{g}] {w}Поиск по СНИЛС{g}              [{w}24{g}] {w}Сканнер Портов{g}                [{w}38{g}] {w}Информация о Самолёте{g}              ║   
{g}║                                                                                     ║    ║   [{w}11{g}] {w}Поиск по IP{g}                 [{w}25{g}] {w}Поиск по Координатам{g}          [{w}39{g}] {w}Создать Сессию{g}                     ║   
{g}║                      [{w}&{g}] {w}Telegram Channel: {g}@{w}none{g}                        ║    ║   [{w}12{g}] {w}Поиск по TikTok{g}             [{w}26{g}] {w}Поиск по Карте{g}                [{w}40{g}] {w}Управление Сессией{g}                 ║   
{g}║                      [{w}&{g}] {w}Authors: {g}@{w}netwith{g}                               ║    ║   [{w}13{g}] {w}Поиск по ОК{g}                 [{w}27{g}] {w}AI Analyze{g}                    [{w}41{g}] {w}Поиск по Viber{g}                     ║   
{g}║                      [{w}&{g}] {w}Version: Update {g}1.3                                        ║    ║   [{w}14{g}] {w}Поиск по Instagram{g}          [{w}28{g}] {w}SMTP Валидатор{g}                [{w}42{g}] {w}Поиск по Skype{g}                     ║   
{g}║                                                                                     ║    ║                                                                                                               ║   
{g}╚═════════════════════════════════════════════════════════════════════════════════════╝    ╚═══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝   

{g}╔════════════════════════|{w}ПРОЧЕЕ{g}|═══════════════════════╗
{g}║                                                       ║
{g}║    [{w}43{g}] {w}Мейлер{g}                                        ║
{g}║    [{w}44{g}] {w}Спам Кодами{g}                                   ║
{g}║    [{w}45{g}] {w}Бомбер{g}                                        ║
{g}║    [{w}46{g}] {w}Извлечь Метаданные{g}                            ║
{g}║    [{w}47{g}] {w}Очистка БД{g}                                    ║
{g}║    [{w}48{g}] {w}Веб Кравлер{g}                                   ║
{g}║    [{w}49{g}] {w}Создать свою БД{g}                               ║
{g}║    [{w}50{g}] {w}Выгрузка HTML{g}                                 ║
{g}║    [{w}51{g}] {w}Обфускация кода{g}                               ║
{g}║    [{w}52{g}] {w}Деобфускаторы{g}                                 ║
{g}║    [{w}53{g}] {w}Проверка ссылок на логгер{g}                     ║
{g}║    [{w}54{g}] {w}Получить прокси{g}                               ║
{g}║    [{w}55{g}] {w}Создать TXT Досье{g}                             ║
{g}║    [{w}56{g}] {w}Создать HTML Досье{g}                            ║
{g}║    [{w}57{g}] {w}Создать PDF Досье{g}                             ║
{g}║                                                       ║                                                      
{g}║    [{w}settings{g}] {w}— настройки{g}                             ║
{g}║                                                       ║
{g}║    [{w}0{g}] {w}Выход{g}                                          ║
{g}║                                                       ║
{g}╚═══════════════════════════════════════════════════════╝
"""
    print(banner)

async def show_changelog():
    changelog = f"""
{g}нигилист • обновление 1.3

{w}Новые функции:
• Поиск по VIN Автомобиля
• Поиск по Pikabu
• Поиск через Shodan
• Поиск по паролю
• Поиск по ИНН (Казахстан)
• Поиск по Minecraft
• Парсинг чатов (EMISSARY)
• Отслеживание аккаунта (Слежка)
• Поиск по Перелётам
• Информация о Самолёте
• Создать сессию (Telegram)
• Управление сессией
• Поиск по Viber
• Поиск по Skype

{w}Улучшения:
• Интегрирован Cryven API
• Интегрирован Depsearch API
• Поиск по нику через 4 источника
• Поиск по карте через BIN
• Новая система цветов в баннере
• Форматированный вывод
• Анимация поиска

{w}Дополнительно:
• Настройки: смена цвета баннера
• Создание досье (TXT, HTML, PDF)
• Улучшенный интерфейс
"""
    print(changelog)
    input(f"\n{g}Нажмите Enter для продолжения...")

async def settings_menu():
    global current_color_scheme
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""
{g}настройки

{w}1. смена цвета баннера
{w}2. changelog
{w}3. авторы
{w}4. выход в меню

""")
        
        choice = input(f"{g}выберите опцию: {w}").strip()
        
        if choice == '1':
            print(f"\n{g}доступные цветовые схемы:")
            print(f"{w}1. Зелёная (по умолчанию)")
            print(f"{w}2. Синяя")
            print(f"{w}3. Красная")
            print(f"{w}4. Фиолетовая")
            print(f"{w}5. Жёлтая")
            
            color_choice = input(f"\n{g}выберите цвет (1-5): {w}").strip()
            
            if color_choice == '1':
                update_color_scheme("default")
                print(f"{g}цвет изменён на зелёный")
            elif color_choice == '2':
                update_color_scheme("blue")
                print(f"{g}цвет изменён на синий")
            elif color_choice == '3':
                update_color_scheme("red")
                print(f"{g}цвет изменён на красный")
            elif color_choice == '4':
                update_color_scheme("purple")
                print(f"{g}цвет изменён на фиолетовый")
            elif color_choice == '5':
                update_color_scheme("yellow")
                print(f"{g}цвет изменён на жёлтый")
            else:
                print(f"{w}неверный выбор")
            
            input(f"\n{g}нажмите enter для продолжения...")
            
        elif choice == '2':
            await show_changelog()
        elif choice == '3':
            await show_authors()
        elif choice == '4':
            break
        else:
            print(f"{w}неверный выбор")
            input(f"{g}нажмите enter для продолжения...")

async def show_authors():
    authors = f"""
{g}авторы:

{w}TreeHugger - Главный разработчик
{w}@VkMard - Со-разработчик
{w}KanareykaXD - Автор EMISSARY

{g}контакты:
{w}Telegram канал: @NihilistSoftware
{w}Поддержка: @NihilistSupport
"""
    print(authors)
    input(f"\n{g}Нажмите Enter для продолжения...")

async def vin_search():
    query = input(f"{g}Введите VIN номер автомобиля: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    cryven_data = cryven_search(query, "auto")
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    else:
        print(f"{w}Данные не найдены")

async def pikabu_search():
    query = input(f"{g}Введите Pikabu username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    cryven_data = cryven_search(query, "pikabu")
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    else:
        print(f"{w}Данные не найдены")

async def shodan_search():
    query = input(f"{g}Введите IP/домен для Shodan: {w}").strip()
    if not query: return
    
    show_loading_animation(4)
    
    cryven_data = cryven_search(query, "shodan")
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    else:
        print(f"{w}Данные не найдены")

async def password_search():
    query = input(f"{g}Введите пароль для поиска: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    cryven_data = cryven_search(query, "password")
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    else:
        print(f"{w}Данные не найдены")

async def inn_kazakhstan_search():
    query = input(f"{g}Введите ИНН (Казахстан): {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    cryven_data = cryven_search(query, "inn")
    
    if cryven_data:
        print(f"\n{g}=== CRYVEN ===")
        print(format_nihilist_result(cryven_data))
    else:
        print(f"{w}Данные не найдены")

async def minecraft_search():
    query = input(f"{g}Введите никнейм Minecraft: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://api.mojang.com/users/profiles/minecraft/{query}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            uuid = data.get('id', '')
            name = data.get('name', '')
            
            skin_url = f"https://crafatar.com/renders/head/{uuid}"
            cape_url = f"https://crafatar.com/capes/{uuid}"
            
            print(f"\n{g}=== MINECRAFT ===")
            print(f"{g}├─ username: {w}{name}")
            print(f"{g}├─ uuid: {w}{uuid}")
            print(f"{g}├─ skin: {w}{skin_url}")
            print(f"{g}└─ cape: {w}{cape_url}")
        else:
            print(f"{w}Игрок не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def chat_parsing():
    print(f"{g}Запуск EMISSARY для парсинга чатов...")
    show_loading_animation(2)
    
    try:
        import subprocess
        subprocess.run([sys.executable, "EMISSARY.py"])
    except Exception as e:
        print(f"{g}Ошибка запуска EMISSARY: {e}")

async def account_tracking():
    print(f"{g}Запуск системы отслеживания аккаунтов...")
    show_loading_animation(2)
    
    try:
        import subprocess
        subprocess.run([sys.executable, "user_monitor.py"])
    except Exception as e:
        print(f"{g}Ошибка запуска user_monitor: {e}")

async def flights_search():
    query = input(f"{g}Введите номер рейса (например: SU123): {w}").strip()
    if not query: return
    
    show_loading_animation(4)
    
    try:
        url = f"https://api.aviationstack.com/v1/flights"
        params = {
            "access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "flight_iata": query
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{g}=== FLIGHTS SEARCH ===")
            print(format_nihilist_result(data))
        else:
            print(f"{w}Не удалось получить информацию")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def airplane_info():
    query = input(f"{g}Введите регистрационный номер самолёта (например: RA-12345): {w}").strip()
    if not query: return
    
    show_loading_animation(4)
    
    try:
        url = f"https://api.aviationstack.com/v1/airplanes"
        params = {
            "access_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
            "registration": query
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{g}=== AIRPLANE INFO ===")
            print(format_nihilist_result(data))
        else:
            print(f"{w}Не удалось получить информацию")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def create_session():
    print(f"{g}Создание Telegram сессии...")
    show_loading_animation(2)
    
    try:
        import subprocess
        subprocess.run([sys.executable, "EMISSARY.py"])
    except Exception as e:
        print(f"{g}Ошибка запуска: {e}")

async def manage_session():
    print(f"{g}Запуск управления сессиями...")
    show_loading_animation(2)
    
    try:
        import subprocess
        subprocess.run([sys.executable, "Telegram.py"])
    except Exception as e:
        print(f"{g}Ошибка запуска: {e}")

async def viber_search():
    phone = input(f"{g}Введите номер телефона: {w}").strip()
    if not phone: return
    
    show_loading_animation(2)
    
    try:
        url = f"viber://chat?number={phone}"
        print(f"\n{g}=== VIBER ===")
        print(f"{g}├─ phone: {w}{phone}")
        print(f"{g}└─ viber_url: {w}{url}")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def skype_search():
    query = input(f"{g}Введите Skype ID/username: {w}").strip()
    if not query: return
    
    show_loading_animation(3)
    
    try:
        url = f"https://api.skype.com/users/{query}/profile"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"\n{g}=== SKYPE ===")
            print(format_nihilist_result(data))
        else:
            print(f"{w}Пользователь не найден")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def create_txt_dossier():
    data = {}
    print(f"{g}Создание TXT досье...")
    
    data['name'] = input(f"{g}Имя: {w}").strip()
    data['surname'] = input(f"{g}Фамилия: {w}").strip()
    data['phone'] = input(f"{g}Телефон: {w}").strip()
    data['email'] = input(f"{g}Email: {w}").strip()
    data['address'] = input(f"{g}Адрес: {w}").strip()
    data['notes'] = input(f"{g}Заметки: {w}").strip()
    
    filename = input(f"{g}Имя файла (без .txt): {w}").strip()
    if not filename:
        filename = f"dossier_{int(time.time())}"
    
    with open(f"{filename}.txt", "w", encoding="utf-8") as f:
        f.write("ДОСЬЕ\n")
        f.write("=" * 50 + "\n")
        for key, value in data.items():
            if value:
                f.write(f"{key}: {value}\n")
    
    print(f"\n{g}=== TXT DOSSIER ===")
    print(f"{g}├─ filename: {w}{filename}.txt")
    print(f"{g}└─ status: {w}Сохранено успешно")

async def create_html_dossier():
    data = {}
    print(f"{g}Создание HTML досье...")
    
    data['name'] = input(f"{g}Имя: {w}").strip()
    data['surname'] = input(f"{g}Фамилия: {w}").strip()
    data['phone'] = input(f"{g}Телефон: {w}").strip()
    data['email'] = input(f"{g}Email: {w}").strip()
    data['address'] = input(f"{g}Адрес: {w}").strip()
    data['notes'] = input(f"{g}Заметки: {w}").strip()
    
    filename = input(f"{g}Имя файла (без .html): {w}").strip()
    if not filename:
        filename = f"dossier_{int(time.time())}"
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Досье - {data['name']} {data['surname']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        .info {{ margin: 20px 0; }}
        .label {{ font-weight: bold; color: #555; }}
        .value {{ color: #333; margin-left: 10px; }}
        .footer {{ margin-top: 30px; text-align: center; color: #777; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ДОСЬЕ</h1>
        <div class="info">
            <div><span class="label">Имя:</span> <span class="value">{data['name']}</span></div>
            <div><span class="label">Фамилия:</span> <span class="value">{data['surname']}</span></div>
            <div><span class="label">Телефон:</span> <span class="value">{data['phone']}</span></div>
            <div><span class="label">Email:</span> <span class="value">{data['email']}</span></div>
            <div><span class="label">Адрес:</span> <span class="value">{data['address']}</span></div>
            <div><span class="label">Заметки:</span> <span class="value">{data['notes']}</span></div>
        </div>
        <div class="footer">
            Создано с помощью Nihilist | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>"""
    
    with open(f"{filename}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n{g}=== HTML DOSSIER ===")
    print(f"{g}├─ filename: {w}{filename}.html")
    print(f"{g}└─ status: {w}Сохранено успешно")

async def create_pdf_dossier():
    print(f"{g}Создание PDF досье...")
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        
        data = {}
        data['name'] = input(f"{g}Имя: {w}").strip()
        data['surname'] = input(f"{g}Фамилия: {w}").strip()
        data['phone'] = input(f"{g}Телефон: {w}").strip()
        data['email'] = input(f"{g}Email: {w}").strip()
        data['address'] = input(f"{g}Адрес: {w}").strip()
        data['notes'] = input(f"{g}Заметки: {w}").strip()
        
        filename = input(f"{g}Имя файла (без .pdf): {w}").strip()
        if not filename:
            filename = f"dossier_{int(time.time())}"
        
        c = canvas.Canvas(f"{filename}.pdf", pagesize=letter)
        width, height = letter
        
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1*inch, height - 1*inch, "ДОСЬЕ")
        c.line(1*inch, height - 1.1*inch, 7.5*inch, height - 1.1*inch)
        
        c.setFont("Helvetica", 12)
        y = height - 1.5*inch
        
        for key, value in data.items():
            if value:
                c.drawString(1*inch, y, f"{key}: {value}")
                y -= 0.3*inch
        
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(1*inch, 0.5*inch, f"Создано с помощью Nihilist | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        c.save()
        
        print(f"\n{g}=== PDF DOSSIER ===")
        print(f"{g}├─ filename: {w}{filename}.pdf")
        print(f"{g}└─ status: {w}Сохранено успешно")
        
    except ImportError:
        print(f"{w}Требуется установить reportlab: pip install reportlab")
    except Exception as e:
        print(f"{g}Ошибка: {e}")

async def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        
        print(f"{w}Пользователь: {LOGGED_USER}")
        
        choice = input(f"{g}Выберите функцию: {w}").strip().lower()
        
        if choice == '0':
            print(f"{g}Выход...")
            break
        
        elif choice == 'settings':
            await settings_menu()
            continue
        
        elif choice == '1':
            await phone_search()
        elif choice == '2':
            await email_search()
        elif choice == '3':
            await nick_search()
        elif choice == '4':
            await telegram_search()
        elif choice == '5':
            await vk_search()
        elif choice == '6':
            await auto_search()
        elif choice == '7':
            await fio_search()
        elif choice == '8':
            await inn_search()
        elif choice == '9':
            await snils_search()
        elif choice == '10':
            await ip_search()
        elif choice == '11':
            await ip_search()
        elif choice == '12':
            await tiktok_search()
        elif choice == '13':
            await ok_search()
        elif choice == '14':
            await instagram_search()
        elif choice == '15':
            await mac_search()
        elif choice == '16':
            await github_search()
        elif choice == '17':
            await wikipedia_search_menu()
        elif choice == '18':
            await steam_search()
        elif choice == '19':
            await company_search()
        elif choice == '20':
            await hlr_search()
        elif choice == '21':
            await whatsapp_search()
        elif choice == '22':
            await domain_search()
        elif choice == '23':
            await dork_search()
        elif choice == '24':
            await port_scanner()
        elif choice == '25':
            await coordinates_search()
        elif choice == '26':
            await card_search()
        elif choice == '27':
            await ai_analysis_with_mistral()
        elif choice == '28':
            await smtp_validator_menu()
        elif choice == '29':
            await vin_search()
        elif choice == '30':
            await pikabu_search()
        elif choice == '31':
            await shodan_search()
        elif choice == '32':
            await password_search()
        elif choice == '33':
            await inn_kazakhstan_search()
        elif choice == '34':
            await minecraft_search()
        elif choice == '35':
            await chat_parsing()
        elif choice == '36':
            await account_tracking()
        elif choice == '37':
            await flights_search()
        elif choice == '38':
            await airplane_info()
        elif choice == '39':
            await create_session()
        elif choice == '40':
            await manage_session()
        elif choice == '41':
            await viber_search()
        elif choice == '42':
            await skype_search()
        elif choice == '43':
            await mailer()
        elif choice == '44':
            await spam_codes()
        elif choice == '45':
            await bomber()
        elif choice == '46':
            await exif_search()
        elif choice == '47':
            await db_cleaner()
        elif choice == '48':
            await web_crawler()
        elif choice == '49':
            await create_db()
        elif choice == '50':
            await html_dumper()
        elif choice == '51':
            await obfuscator()
        elif choice == '52':
            await deobfuscator()
        elif choice == '53':
            await link_logger_check()
        elif choice == '54':
            await proxy_getter()
        elif choice == '55':
            await create_txt_dossier()
        elif choice == '56':
            await create_html_dossier()
        elif choice == '57':
            await create_pdf_dossier()
        else:
            print(f"{w}Неверный выбор")
        
        input(f"\n{g}Нажмите Enter для продолжения...")

if __name__ == "__main__":
    asyncio.run(main())
