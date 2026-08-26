import os
import time
import json

try:
    import requests
except ImportError:
    requests = None

try:
    import wikifind
except ImportError:
    wikifind = None

from pushokguard.user_info import username, uuid, sub

runned = False


class Console:
    BANNER = r""" 
║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗                   ║
║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                   ║
║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                      ║
║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                      ║
║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                      ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                      ║
    """

    CLEAR_CMD = "cls" if os.name == "nt" else "clear"

    @staticmethod
    def clear():
        os.system(Console.CLEAR_CMD)

    @staticmethod
    def banner():
        print(Console.BANNER)

    @staticmethod
    def input(msg):
        return input(f" [$] {msg}: ")

    @staticmethod
    def print(msg):
        print(f" [!] {msg}")


class Searching:
    BIGBASE_URL = "https://bigbase.top/api/"
    BIGBASE_TOKEN = "g-eg8muf-20sQ_ygoovh_jTWacp43rTh"

    HEADERS = {
        "Authorization": f"Bearer {BIGBASE_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    @staticmethod
    def wiki_search(query):
        if wikifind is None:
            return None
        return wikifind.process(query)

    @staticmethod
    def bigbase_search(query):
        if requests is None:
            return None
        data = {"search": query, "page": 0}
        resp = requests.post(
            Searching.BIGBASE_URL + "search",
            json=data,
            headers=Searching.HEADERS,
            timeout=30,
        )
        if resp.status_code == 200:
            return resp.json()
        return None


class Menu:
    functions = [
        {"text": "Поиск по Номеру телефона", "function": Searching.bigbase_search},
        {"text": "Поиск по Википедии", "function": Searching.wiki_search},
    ]

    @staticmethod
    def start():
        Console.clear()
        Console.banner()
        Console.print("Пользователь: " + username + " | UUID: " + uuid)
        Console.print("Подписка: " + sub)
        print()

        print(" [0] Назад")
        for count, function in enumerate(Menu.functions, start=1):
            print(f" [$] {count}. {function['text']}")
        print()

        data = Console.input("Номер функции")
        if data == "0":
            return False

        query = Console.input("Введите данные")

        try:
            data = int(data)
            if data > len(Menu.functions) or data < 1:
                Console.print("Неверный выбор")
            else:
                resp = Menu.functions[data - 1]["function"](query)
                if resp:
                    text = json.dumps(resp, indent=2, ensure_ascii=False)
                    for line in text.split("\n"):
                        print(f" {line}")
                else:
                    Console.print("Ничего не найдено")
        except Exception as e:
            print(e)
            Console.print("Неверный выбор")

        Console.input("Нажмите ENTER чтобы продолжить")
        return True


def main():
    global runned

    while True:
        Console.clear()
        Console.banner()
        Console.print("Developer: t.me/wawelrate")
        Console.print("Channel (News/Updates): t.me/VersusPort")
        Console.print("Protected by t.me/pushokguard")

        if not runned:
            time.sleep(1.5)

        runned = True
        if Menu.start() is False:
            break


if __name__ == "__main__":
    main()
