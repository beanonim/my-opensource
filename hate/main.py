from rich.console import Console
from rich.table import Table
from rich.text import Text

from localapi.colors import p, i
from localapi.help import cls
import localapi.gradients

from pushokguard.user_info import username, uuid, sub
from api import APIS

from functions.phone import search_phone
from functions.email import search_email
from functions.fio import search_fio
from functions.nickname import search_nickname
from functions.password import search_password
from functions.car import search_car
from functions.telegram import search_telegram
from functions.facebook import search_facebook
from functions.instagram import search_instagram
from functions.ip import search_ip
from functions.card import search_card
from functions.passport import search_passport
from functions.ok import search_ok
from functions.inn import search_inn
from functions.snils import search_snils
from functions.vk import search_vk

def build_banner(page):
    pages = [
        [
            ["[1] Поиск по номеру", "[3] Поиск по ФИО", "[5] Поиск по паролю"],
            ["[2] Поиск по почте", "[4] Поиск по никнейму", "[6] Поиск по авто"],
            ["[b] Назад", "[n] Следующая страница", ""]
        ],
        [
            ["[7] Поиск по Telegram", "[9] Поиск по Instagram", "[11] Поиск по карте"],
            ["[8] Поиск по Facebook", "[10] Поиск по IP", "[12] Поиск по паспорту"],
            ["[b] Назад", "[n] Следующая страница", ""]
        ],
        [
            ["[13] Поиск по Одноклассникам", "[15] Поиск по СНИЛС", "[0] Информация о софте"],
            ["[14] Поиск по ИНН", "[16] Поиск по ВКонтакте", "[b] Назад"],
            ["[b] Назад", "[n] Следующая страница", ""]
        ],
    ]
    page_items = pages[page]
    header = f"""
██  ██    ███    ██████  ██████  Пользователь: {username} | {uuid}
██  ██  ██   ██    ██    ██      Подписка: {sub}
██████  ███████    ██    ██████
██  ██  ██   ██    ██    ██
██  ██  ██   ██    ██    ██████
"""
    table = Table(show_header=False, box=None, pad_edge=False, padding=(0, 0), expand=False)
    table.add_column(justify="left", width=30, no_wrap=True)
    table.add_column(justify="left", width=30, no_wrap=True)
    table.add_column(justify="left", width=30, no_wrap=True)
    for idx, row in enumerate(page_items):
        if idx == len(page_items) - 1:
            continue
        table.add_row(*[Text(item) if item else "" for item in row])
    console = Console(force_terminal=False, width=120, color_system=None, no_color=True)
    with console.capture() as capture:
        console.print(header)
        console.print(table)
        console.print(Text("[b] Назад     [n] Следующая страница"))
    return capture.get()


def main():
    cls()
    page = 0
    while True:
        cls()
        p(build_banner(page))
        choice = i(f"root:/{username} $ ").strip().lower()

        actions = {
            "1": search_phone,
            "2": search_email,
            "3": search_fio,
            "4": search_nickname,
            "5": search_password,
            "6": search_car,
            "7": search_telegram,
            "8": search_facebook,
            "9": search_instagram,
            "10": search_ip,
            "11": search_card,
            "12": search_passport,
            "13": search_ok,
            "14": search_inn,
            "15": search_snils,
            "16": search_vk,
        }

        if choice in actions:
            actions[choice]()
            break
        elif choice == "0":
            p("  ─── APIs ───")
            for api_id, api in APIS.items():
                p(f"  {api['name']} - {api_id}")
                p(f"  bases : {api['bases']} TB")
                p("  ──────")
            p(f"""Сделано с любовью от @netwith
Баннер, база софта сделана: @netwith
Софт под защитой: @netwith

Информация и пользователе:
- Ник: {username}
- UUID: {uuid}
- Подписка: {sub}""")
            break
        elif choice == "n":
            page = min(page + 1, 2)
            continue
        elif choice == "b":
            page = max(page - 1, 0)
            continue
        else:
            p("  Неверный выбор")
            continue

if __name__ == "__main__":
    main()

