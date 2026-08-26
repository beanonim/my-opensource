import ast
import asyncio
import inspect
import itertools
import os
import re
import sqlite3
import string
import sys

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, FloodWait, UsernameInvalid, UsernameOccupied
from pyrogram.raw.functions.messages import Report
from pyrogram.raw.functions.account import ResetAuthorization, GetAuthorizations, CheckUsername
from pyrogram.raw.types import (
    InputReportReasonSpam,
    InputReportReasonViolence,
    InputReportReasonPornography,
    InputReportReasonChildAbuse,
    InputReportReasonOther,
    XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX,
    InputReportReasonIllegalDrugs,
)

from telethon import TelegramClient
from telethon.sessions import MemorySession
from telethon.crypto import AuthKey
from telethon.tl import functions, types

DEFAULT_API_ID = 2040000
DEFAULT_API_HASH = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

DC_IP_MAP = {
    1: ("149.154.175.53", 443),
    2: ("149.154.167.51", 443),
    3: ("149.154.175.100", 443),
    4: ("149.154.167.91", 443),
    5: ("91.108.56.130", 443),
}

REPORT_REASONS = {
    "1": ("Спам", InputReportReasonSpam()),
    "2": ("Другое", InputReportReasonOther()),
    "3": ("Насилие", InputReportReasonViolence()),
    "4": ("Порнография", InputReportReasonPornography()),
    "5": ("Личные данные", XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX()),
    "6": ("Запрещенные вещества", InputReportReasonIllegalDrugs()),
    "7": ("Жестокое обращение с детьми", InputReportReasonChildAbuse()),
    "8": ("Своя причина", InputReportReasonOther()),
}

FARM_TARGET_BOT = "fustatifer_bot"
FARM_BATCH_SIZE = 10
NEXT_BUTTON_TEXTS = ["➡", "➡️", "▶", "▶️", "Next", "Далее"]

FARM_STOP = False
FARM_PAUSED = False
FARM_SENDING = False

VOWELS = list("aeiouy")
CONSONANTS = list("bcdfghjklmnpqrstvwxz")
DIGITS = list(string.digits)
ANY_CHAR = list(string.ascii_lowercase + string.digits + "_")

TELEGRAM_USERNAME_REGEX = r"^[a-zA-Z](?!.*__)[a-zA-Z0-9_]{3,30}[a-zA-Z0-9]$"


def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def get_session_files():
    ensure_sessions_dir()
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    return [os.path.splitext(f)[0] for f in files]


def is_valid_username_format(username: str) -> bool:
    return bool(re.match(TELEGRAM_USERNAME_REGEX, username))


def parse_post_link(link):
    pattern = r"t\.me\/(?:c\/)?([a-zA-Z0-9_]+|\d+)\/(\d+)"
    match = re.search(pattern, link)
    if not match:
        return None, None
    channel, msg_id = match.group(1), int(match.group(2))
    if str(channel).isdigit():
        channel_str = str(channel)
        if not channel_str.startswith("-100"):
            channel = int(f"-100{channel_str}")
        else:
            channel = int(channel_str)
    return channel, msg_id


def extract_links_from_text_and_entities(text, entities):
    links = []
    if text:
        links.extend(re.findall(r"https?://[^\s]+", text))
    if entities:
        for e in entities:
            if getattr(e, "url", None):
                links.append(e.url)
    return list(set(links))


def generate_usernames_by_pattern(pattern):
    pattern = pattern.strip().lower()
    pools = []
    for char in pattern:
        if char == "+":
            pools.append(VOWELS)
        elif char == "-":
            pools.append(CONSONANTS)
        elif char == "#":
            pools.append(DIGITS)
        elif char == "*":
            pools.append(ANY_CHAR)
        else:
            pools.append([char])

    raw_combinations = ["".join(comb) for comb in itertools.product(*pools)]
    return [u for u in raw_combinations if is_valid_username_format(u)]


def remove_function_from_self():
    script_path = os.path.abspath(__file__)
    try:
        with open(script_path, "r", encoding="utf-8") as f:
            code = f.read()

        parsed = ast.parse(code)
        funcs = [node for node in parsed.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]

        protected = ["main", "ensure_sessions_dir", "get_session_files", "remove_function_from_self", "select_accounts"]
        removable = [f for f in funcs if f.name not in protected]

        if not removable:
            print("Нет доступных функций для удаления.")
            return

        print("\n=== МОДУЛЬ СЕБЕУДАЛЕНИЯ ФУНКЦИЙ ===")
        for idx, fn in enumerate(removable, 1):
            print(f" {idx}. {fn.name}")

        choice = input("Выберите номер функции для физического вырезания из файла: ").strip()
        if not choice.isdigit() or not (1 <= int(choice) <= len(removable)):
            print("Отмена.")
            return

        target_fn = removable[int(choice) - 1]
        lines = code.splitlines(keepends=True)

        start_line = target_fn.lineno - 1
        end_line = target_fn.end_lineno

        new_lines = lines[:start_line] + lines[end_line:]
        new_code = "".join(new_lines)

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_code)

        print(f"✅ Функция `{target_fn.name}` успешно вырезана из исходного кода файла!")
        print("Перезапустите скрипт, чтобы обновить структуры в памяти.")
    except Exception as e:
        print(f"Ошибка при модификации файла: {e}")


async def select_accounts(active_apps):
    if not active_apps:
        print("Нет активных аккаунтов.")
        return []

    print("\n=== ВЫБОР ЦЕЛЕВЫХ АККАУНТОВ ===")
    print(" 0. Использовать ВСЕ аккаунты")
    for idx, app in enumerate(active_apps, 1):
        phone = getattr(app.me, "phone_number", "Неизвестно")
        name = getattr(app.me, "first_name", "Неизвестно")
        print(f" [{idx}] {name} (+{phone})")

    choice = input("Укажите номера через запятую (например: 1,3) или '0' для всех: ").strip()
    if choice == "0" or not choice:
        return active_apps

    selected = []
    for part in choice.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part)
            if 1 <= idx <= len(active_apps):
                selected.append(active_apps[idx - 1])
    return selected


async def wait_if_farm_paused():
    global FARM_PAUSED, FARM_STOP
    while FARM_PAUSED and not FARM_STOP:
        await asyncio.sleep(1)


async def ensure_joined_pyrogram(app, chat_target):
    try:
        if isinstance(chat_target, str) and ("t.me/+" in chat_target or "joinchat/" in chat_target):
            await app.join_chat(chat_target)
            print(f"[{app.name}] Успешный вход по инвайту: {chat_target}")
        else:
            await app.join_chat(chat_target)
            print(f"[{app.name}] Успешный вход в чат: {chat_target}")
    except Exception as e:
        if "USER_ALREADY_PARTICIPANT" not in str(e):
            print(f"[{app.name}] Ошибка входа в {chat_target}: {e}")


async def process_pyrogram_pages(app, chat_item, message, all_links):
    global FARM_STOP
    current = message
    visited = set()

    while True:
        await wait_if_farm_paused()
        if FARM_STOP:
            return

        text = current.text or current.caption or ""
        links = extract_links_from_text_and_entities(text, current.entities or current.caption_entities)
        all_links.extend(links)

        if not current.reply_markup or not getattr(current.reply_markup, "inline_keyboard", None):
            break

        page_hash = hash(text)
        if page_hash in visited:
            break
        visited.add(page_hash)

        next_found = False
        for row in current.reply_markup.inline_keyboard:
            for btn in row:
                if FARM_STOP:
                    return
                btn_text = getattr(btn, "text", "")
                if btn_text in NEXT_BUTTON_TEXTS:
                    next_found = True
                    try:
                        await current.click(btn_text)
                        async for new_msg in app.get_chat_history(chat_item, limit=1):
                            current = new_msg
                            break
                    except Exception as e:
                        print(f"[{app.name}] Ошибка клика кнопки: {e}")
                        next_found = False
                    break
            if next_found:
                break
        if not next_found:
            break


async def send_farm_batch(app, batch):
    global FARM_STOP
    await wait_if_farm_paused()
    if FARM_STOP:
        return
    text = "\n".join(batch)
    try:
        print(f"[{app.name}] Отправка {len(batch)} ссылок в @{FARM_TARGET_BOT}...")
        await app.send_message(FARM_TARGET_BOT, text)
    except Exception as e:
        print(f"[{app.name}] Ошибка отправки: {e}")


async def send_farm_batches(app, links):
    global FARM_STOP
    buffer = []
    for link in links:
        await wait_if_farm_paused()
        if FARM_STOP:
            return
        buffer.append(link)
        if len(buffer) >= FARM_BATCH_SIZE:
            await send_farm_batch(app, buffer)
            buffer = []
    if buffer and not FARM_STOP:
        await send_farm_batch(app, buffer)


async def run_farm_task(target_apps, source_chats):
    global FARM_STOP, FARM_SENDING, FARM_PAUSED
    FARM_STOP = False
    FARM_PAUSED = False
    FARM_SENDING = True

    print("\nЗапуск фарма Фанстата...")

    try:
        for app in target_apps:
            if FARM_STOP:
                break

            phone = getattr(app.me, "phone_number", app.name)
            print(f"\n--- Работает аккаунт +{phone} ---")
            all_links = []

            for chat in source_chats:
                if FARM_STOP:
                    break
                print(f"[{app.name}] Обработка источника: {chat}")
                await ensure_joined_pyrogram(app, chat)

                try:
                    async for msg in app.get_chat_history(chat, limit=5):
                        if FARM_STOP:
                            break
                        await process_pyrogram_pages(app, chat, msg, all_links)
                except Exception as e:
                    print(f"[{app.name}] Ошибка чтения {chat}: {e}")

            unique_links = list(set(all_links))
            print(f"[{app.name}] Собрано уникальных ссылок: {len(unique_links)}")

            if unique_links and not FARM_STOP:
                await send_farm_batches(app, unique_links)
                print(f"[{app.name}] Фарм завершен")
            else:
                print(f"[{app.name}] Нет ссылок для отправки")

    except Exception as e:
        print(f"Критическая ошибка фарма: {e}")
    finally:
        FARM_SENDING = False
        print("\nФарм процесс полностью завершен.")


async def farm_fanstat_menu(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    print("\n=== НАСТРОЙКА И ФАРМ ФАНСТАТА ===")
    chats_raw = input("Введите чаты/каналы через запятую: ").strip()
    if not chats_raw:
        return

    source_chats = []
    for item in chats_raw.split(","):
        item = item.strip()
        if item.startswith("-") and item[1:].isdigit():
            source_chats.append(int(item))
        elif item.isdigit():
            source_chats.append(int(item))
        elif item:
            source_chats.append(item)

    if not source_chats:
        print("Не распознано ни одного чата.")
        return

    asyncio.create_task(run_farm_task(target_apps, source_chats))

    while True:
        print("\nУправление фармом:")
        print("1. Пауза / Возобновить")
        print("2. Остановить фарм")
        print("3. Проверить статус")
        print("0. Назад в главное меню")

        cmd = input("> ").strip()
        if cmd == "1":
            FARM_PAUSED = not FARM_PAUSED
            print(f"Пауза: {FARM_PAUSED}")
        elif cmd == "2":
            FARM_STOP = True
            print("Сигнал остановки отправлен...")
        elif cmd == "3":
            print(f"Активен: {FARM_SENDING} | Пауза: {FARM_PAUSED} | Стоп: {FARM_STOP}")
        elif cmd == "0":
            break


async def check_username_availability(app, username: str):
    clean_username = username.strip().lstrip("@")

    if not is_valid_username_format(clean_username):
        return False, "Неверный формат (буквы, 5-32 симв., без '_' в конце)"

    try:
        if not app.is_connected:
            await app.connect()

        is_available = await app.invoke(CheckUsername(username=clean_username))
        if is_available:
            return True, "СВОБОДЕН (можно поставить)"
        return False, "Занят или недоступен"
    except UsernameOccupied:
        return False, "Занят другим пользователем"
    except UsernameInvalid:
        return False, "Недопустимый юзернейм / зарезервирован"
    except FloodWait as e:
        return False, f"Флудвейт: подождите {e.value} сек."
    except RPCError as e:
        err_msg = str(e)
        if "PURCHASE_AVAILABLE" in err_msg or "FRAGMENT" in err_msg:
            return False, "Продается на Fragment / TON NFT"
        return False, f"Ошибка API: {err_msg}"
    except BaseException as e:
        return False, f"Сбой соединения/системы: {e}"


async def username_checker_menu(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    app = target_apps[0]
    print(f"\n=== ПОДБОР И ПРОВЕРКА ЮЗЕРНЕЙМОВ ===")
    print(f"Проверку выполняет сессия: {getattr(app.me, 'first_name', app.name)}")
    print("1. Ввести юзернеймы вручную")
    print("2. Загрузить из файла (usernames.txt)")
    print("3. Сгенерировать по маске (+ гласные, - согласные, # цифры, * любые)")

    mode = input("> ").strip()
    usernames = []

    if mode == "1":
        raw_input = input("Введите юзернеймы через запятую или пробел: ").strip()
        usernames = [u.strip() for u in re.split(r"[\s,]+", raw_input) if u.strip()]
    elif mode == "2":
        file_path = input("Путь к файлу (Enter для usernames.txt): ").strip() or "usernames.txt"
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                usernames = [line.strip() for line in f if line.strip()]
        else:
            print(f"Файл {file_path} не найден.")
            return
    elif mode == "3":
        pattern = input("Введите маску (напр. ZXC+-, test_##, user*#): ").strip()
        if not pattern:
            print("Маска не введена.")
            return
        usernames = generate_usernames_by_pattern(pattern)
        print(f"Сгенерировано подходящих комбинаций: {len(usernames)}")
        if len(usernames) > 500:
            confirm = input("Комбинаций больше 500. Продолжить? (y/n): ").strip().lower()
            if confirm != "y":
                return

    if not usernames:
        print("Список юзернеймов пуст или варианты отсеяны правилами Telegram.")
        return

    auto_set = input("Устанавливать первый найденный свободный юзернейм на выбранные аккаунты? (y/n): ").strip().lower() == "y"

    available_list = []
    print(f"\n--- Проверка {len(usernames)} юзернеймов ---")

    for username in usernames:
        clean_name = username.strip().lstrip("@")
        print(f"Проверка @{clean_name}... ", end="", flush=True)

        is_free, status = await check_username_availability(app, clean_name)

        if is_free:
            print(f"✅ {status}")
            available_list.append(clean_name)

            if auto_set:
                for target_app in target_apps:
                    try:
                        await target_app.set_username(clean_name)
                        print(f"🎉 Успешно установлен @{clean_name} на аккаунт (+{getattr(target_app.me, 'phone_number', '')})!")
                        break
                    except Exception as e:
                        print(f"❌ Ошибка установки на {target_app.name}: {e}")
                break
        else:
            print(f"❌ {status}")

        await asyncio.sleep(1.5)

    print("\n=== ИТОГИ ПРОВЕРКИ ===")
    if available_list:
        print(f"Свободных юзернеймов ({len(available_list)}):")
        for u in available_list:
            print(f" - @{u}")
        with open("free_usernames.txt", "a", encoding="utf-8") as f:
            for u in available_list:
                f.write(f"{u}\n")
        print("Результаты сохранены в free_usernames.txt")
    else:
        print("Свободных юзернеймов не найдено.")


async def create_new_session():
    ensure_sessions_dir()
    session_name = input("Имя файла сессии (например: acc1): ").strip()
    if not session_name:
        return None

    api_id_input = input(f"Введите API ID (Enter для {DEFAULT_API_ID}): ").strip()
    api_id = int(api_id_input) if api_id_input.isdigit() else DEFAULT_API_ID

    api_hash = input("Введите API Hash (Enter по умолчанию): ").strip() or DEFAULT_API_HASH

    session_path = os.path.join(SESSIONS_DIR, session_name)
    app = Client(session_path, api_id=api_id, api_hash=api_hash, no_updates=True)

    try:
        await app.start()
        me = await app.get_me()
        app.me = me
        app.session_file_path = session_path + ".session"
        print(f"УСПЕШНО: {me.first_name} (+{me.phone_number})")
        return app
    except Exception as e:
        print(f"ОШИБКА: {e}")
        return None


async def mass_report_menu(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    link = input("Ссылка на пост для жалобы: ").strip()
    channel, msg_id = parse_post_link(link)
    if not channel or not msg_id:
        print("Неверная ссылка на пост.")
        return

    print("\nПричины жалобы:")
    for k, v in REPORT_REASONS.items():
        print(f" [{k}] {v[0]}")

    reason_choice = input("Выберите причину (1-8): ").strip() or "1"
    _, reason_obj = REPORT_REASONS.get(reason_choice, REPORT_REASONS["1"])
    comment = input("Комментарий к жалобе: ").strip() or "Violation"

    for idx, app in enumerate(target_apps, 1):
        try:
            chat = await app.get_chat(channel)
            peer = await app.resolve_peer(chat.id)
            await app.invoke(Report(peer=peer, id=[msg_id], reason=reason_obj, message=comment))
            print(f"[{idx}] Жалоба отправлена с аккаунта +{getattr(app.me, 'phone_number', app.name)}")
        except Exception as e:
            print(f"[{idx}] Ошибка на аккаунте {app.name}: {e}")


async def send_message_to_target(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    target = input("Кому отправить (@юзернейм, ID или номер): ").strip()
    text = input("Текст сообщения: ").strip()
    if not target or not text:
        print("Заполните все поля.")
        return

    for idx, app in enumerate(target_apps, 1):
        try:
            await app.send_message(chat_id=target, text=text)
            print(f"[{idx}] Сообщение отправлено с аккаунта +{getattr(app.me, 'phone_number', app.name)}")
        except Exception as e:
            print(f"[{idx}] Ошибка на аккаунте {app.name}: {e}")


async def join_ref_link(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    ref_link = input("Ссылка (реферальная, бот или чат): ").strip()
    if not ref_link:
        return

    for idx, app in enumerate(target_apps, 1):
        try:
            if "start=" in ref_link or "startgroup=" in ref_link:
                bot_username = ref_link.split("t.me/")[1].split("?")[0]
                param = ref_link.split("start=")[-1] if "start=" in ref_link else ref_link.split("startgroup=")[-1]
                await app.start_bot(bot_username, param)
                print(f"[{idx}] Бот запущен ({bot_username}) на аккаунте +{getattr(app.me, 'phone_number', app.name)}")
            elif "/+" in ref_link or "joinchat/" in ref_link:
                await app.join_chat(ref_link)
                print(f"[{idx}] Успешный вход в приватный чат (+{getattr(app.me, 'phone_number', app.name)})")
            else:
                target = ref_link.replace("https://t.me/", "")
                await app.join_chat(target)
                print(f"[{idx}] Вход в чат ({target}) выполнен (+{getattr(app.me, 'phone_number', app.name)})")
        except Exception as e:
            print(f"[{idx}] Ошибка на аккаунте {app.name}: {e}")


async def update_profile(app, first_name=None, last_name=None, username=None, avatar_path=None):
    try:
        if first_name is not None or last_name is not None:
            await app.update_profile(first_name=first_name, last_name=last_name)
            print("  Имя и фамилия обновлены")

        if username is not None:
            await app.set_username(username)
            print(f"  Юзернейм изменен: @{username}")

        if avatar_path and os.path.exists(avatar_path):
            await app.set_profile_photo(photo=avatar_path)
            print("  Аватар обновлен")
    except Exception as e:
        print(f"  Ошибка обновления: {e}")


async def edit_profile_menu(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    first_name = input("Новое Имя (Enter - пропустить): ").strip() or None
    last_name = input("Новая Фамилия (Enter - пропустить): ").strip() or None

    username = None
    if len(target_apps) == 1:
        username = input("Новый юзернейм без @ (Enter - пропустить): ").strip() or None

    avatar_path = input("Путь к фото для аватара (Enter - пропустить): ").strip() or None

    for idx, app in enumerate(target_apps, 1):
        phone = getattr(app.me, "phone_number", "N/A")
        print(f"[{idx}] Обновление аккаунта (+{phone})...")
        await update_profile(app, first_name, last_name, username, avatar_path)


async def terminate_other_sessions(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    for idx, app in enumerate(target_apps, 1):
        try:
            authorizations = await app.invoke(GetAuthorizations())
            killed = 0
            for auth in authorizations.authorizations:
                if not auth.current:
                    try:
                        await app.invoke(ResetAuthorization(hash=auth.hash))
                        killed += 1
                    except Exception:
                        pass
            print(f"[{idx}] Аккаунт +{getattr(app.me, 'phone_number', app.name)}: Завершено чужих сеансов: {killed}")
        except Exception as e:
            print(f"[{idx}] Ошибка на аккаунте {app.name}: {e}")


def create_telethon_session_from_pyrogram(session_file_path):
    conn = sqlite3.connect(session_file_path)
    cur = conn.cursor()
    cur.execute("SELECT dc_id, auth_key FROM sessions LIMIT 1")
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError("Не удалось прочитать авторизационные данные из файла сессии.")

    dc_id, auth_key_bytes = row
    ip, port = DC_IP_MAP.get(dc_id, ("149.154.167.51", 443))

    session = MemorySession()
    session.set_dc(dc_id, ip, port)
    session.auth_key = AuthKey(auth_key_bytes)
    return session


async def send_telegram_gift_menu(active_apps):
    target_apps = await select_accounts(active_apps)
    if not target_apps:
        return

    print("\n=== КАТАЛОГ ПОДАРКОВ ===")
    print("📋 Доступные подарки:")
    print("  ❤️ 15⭐️ 5170145012310081615")
    print("  🧸 15⭐️ 5170233102089322756")
    print("  🎁 25⭐️ 5170250947678437525")
    print("  🌹 25⭐️ 5168103777563050263")
    print("  🎂 50⭐️ 5170144170496491616")
    print("  💐 50⭐️ 5170314324215857265")
    print("  🚀 50⭐️ 5170564780938756245")
    print("  🍾 50⭐️ 6028601630662853006")
    print("  кубок 100⭐️ 5168043875654172773")
    print("  💍 100⭐️ 5170690322832818290")
    print("  алмаз 100⭐️ 5170521118301225164\n")

    gift_id_str = input("Введи ID подарка из списка: ").strip()
    if not gift_id_str.isdigit():
        print("Ошибка: ID подарка должен быть числом.")
        return
    gift_id = int(gift_id_str)

    message_text = input("Введи подпись к подарку (или Enter чтобы пропустить): ").strip()
    recipient = input("Введи ID или @username получателя: ").strip()
    if not recipient:
        print("Ошибка: получатель не указан.")
        return

    for app in target_apps:
        api_id = getattr(app, "api_id", DEFAULT_API_ID) or DEFAULT_API_ID
        api_hash = getattr(app, "api_hash", DEFAULT_API_HASH) or DEFAULT_API_HASH

        try:
            session = create_telethon_session_from_pyrogram(app.session_file_path)
        except Exception as e:
            print(f"Ошибка считывания сессии {app.name}: {e}")
            continue

        print(f"Подключаем Telethon для аккаунта +{getattr(app.me, 'phone_number', app.name)}...")
        tele_client = TelegramClient(session, api_id, api_hash)

        try:
            await tele_client.connect()
            if not await tele_client.is_user_authorized():
                print(f"Ошибка: Сессия {app.name} не авторизована!")
                continue

            user = await tele_client.get_entity(int(recipient) if recipient.lstrip("-").isdigit() else recipient)
            peer = await tele_client.get_input_entity(user)
            print(f"Получатель найден: {getattr(user, 'first_name', recipient)} (id={user.id})")

            msg = types.TextWithEntities(text=message_text, entities=[]) if message_text else None
            invoice = types.InputInvoiceStarGift(peer=peer, gift_id=gift_id, message=msg)

            form = await tele_client(functions.payments.GetPaymentFormRequest(invoice=invoice))
            await tele_client(functions.payments.SendStarsFormRequest(form_id=form.form_id, invoice=invoice))
            print(f"ПОДАРОК УСПЕШНО ОТПРАВЛЕН С АККАУНТА +{getattr(app.me, 'phone_number', app.name)}!")
        except Exception as e:
            print(f"Ошибка при отправке подарка с {app.name}: {e}")
        finally:
            await tele_client.disconnect()


async def main():
    ensure_sessions_dir()
    session_names = get_session_files()
    active_apps = []

    if session_names:
        print(f"Загрузка сессий ({len(session_names)})...")
        for s_name in session_names:
            session_path = os.path.join(SESSIONS_DIR, s_name)
            app = Client(session_path, api_id=DEFAULT_API_ID, api_hash=DEFAULT_API_HASH, no_updates=True)
            try:
                await app.start()
                me = await app.get_me()
                app.me = me
                app.session_file_path = session_path + ".session"
                print(f"УСПЕХ | [{s_name}] | +{me.phone_number}")
                active_apps.append(app)
            except Exception as e:
                print(f"ОШИБКА | [{s_name}] | {e}")
    else:
        print("В папке sessions нет файлов сессий.")

    while True:
        print("\n=== ГЛАВНОЕ МЕНЮ (ВЫБОР ДЕЙСТВИЯ) ===")
        print(f"Активных аккаунтов в системе: {len(active_apps)}")
        print("1. Жалоба на пост (Массово / Точечно)")
        print("2. Отправка сообщения (Массово / Точечно)")
        print("3. Переход по реф. ссылкам / Запуск ботов")
        print("4. Изменение профилей (Имя, Фамилия, Аватар)")
        print("5. Завершение чужих сессий")
        print("6. Фарм Фанстата (Авто-сбор и отправка)")
        print("7. Отправка подарков Telegram (Stars)")
        print("8. Подбор и проверка юзернеймов (API)")
        print("9. Вырезать / удалить функцию из скрипта")
        print("10. Добавить / Авторизовать новый аккаунт")
        print("0. Выход")

        choice = input("> ").strip()

        if choice == "1":
            await mass_report_menu(active_apps)
        elif choice == "2":
            await send_message_to_target(active_apps)
        elif choice == "3":
            await join_ref_link(active_apps)
        elif choice == "4":
            await edit_profile_menu(active_apps)
        elif choice == "5":
            await terminate_other_sessions(active_apps)
        elif choice == "6":
            await farm_fanstat_menu(active_apps)
        elif choice == "7":
            await send_telegram_gift_menu(active_apps)
        elif choice == "8":
            await username_checker_menu(active_apps)
        elif choice == "9":
            remove_function_from_self()
        elif choice == "10":
            new_app = await create_new_session()
            if new_app:
                active_apps.append(new_app)
        elif choice == "0":
            print("Выход из программы...")
            break

    for app in active_apps:
        try:
            await app.stop()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

