import asyncio
import os
import re
from pyrogram import Client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")

FARM_TARGET_BOT = "fustatifer_bot"
FARM_BATCH_SIZE = 10
NEXT_BUTTON_TEXTS = ["➡", "➡️", "▶", "▶️", "Next", "Далее"]


def ensure_sessions_dir():
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)


def get_session_files():
    ensure_sessions_dir()
    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".session")]
    return [os.path.splitext(f)[0] for f in files]


def extract_links(text, entities):
    links = []
    if text:
        links.extend(re.findall(r"https?://[^\s]+", text))
    if entities:
        for e in entities:
            if getattr(e, "url", None):
                links.append(e.url)
    return list(set(links))


async def ensure_joined(app, chat_target):
    try:
        await app.join_chat(chat_target)
    except Exception as e:
        if "USER_ALREADY_PARTICIPANT" not in str(e):
            print(f"[{app.name}] Ошибка входа {chat_target}: {e}")


async def process_pages(app, chat_item, message, all_links):
    current = message
    visited = set()

    while True:
        text = current.text or current.caption or ""
        links = extract_links(text, current.entities or current.caption_entities)
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
                btn_text = getattr(btn, "text", "")
                if btn_text in NEXT_BUTTON_TEXTS:
                    next_found = True
                    try:
                        await current.click(btn_text)
                        async for new_msg in app.get_chat_history(chat_item, limit=1):
                            current = new_msg
                            break
                    except Exception:
                        next_found = False
                    break
            if next_found:
                break
        if not next_found:
            break


async def send_batch(app, batch):
    text = "\n".join(batch)
    try:
        print(f"[{app.name}] Отправка {len(batch)} ссылок в @{FARM_TARGET_BOT}...")
        await app.send_message(FARM_TARGET_BOT, text)
    except Exception as e:
        print(f"[{app.name}] Ошибка отправки: {e}")


async def send_batches(app, links):
    buffer = []
    for link in links:
        buffer.append(link)
        if len(buffer) >= FARM_BATCH_SIZE:
            await send_batch(app, buffer)
            buffer = []
    if buffer:
        await send_batch(app, buffer)


async def run_farm(active_apps, source_chats):
    for app in active_apps:
        phone = getattr(app.me, "phone_number", app.name)
        print(f"\n--- Работает аккаунт +{phone} ---")
        all_links = []

        for chat in source_chats:
            print(f"[{app.name}] Обработка источника: {chat}")
            await ensure_joined(app, chat)

            try:
                async for msg in app.get_chat_history(chat, limit=5):
                    await process_pages(app, chat, msg, all_links)
            except Exception as e:
                print(f"[{app.name}] Ошибка чтения {chat}: {e}")

        unique_links = list(set(all_links))
        print(f"[{app.name}] Собрано уникальных ссылок: {len(unique_links)}")

        if unique_links:
            await send_batches(app, unique_links)
        else:
            print(f"[{app.name}] Нет ссылок для отправки")


async def main():
    session_names = get_session_files()
    if not session_names:
        print("Сессии не найдены в папке sessions/")
        return

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

    active_apps = []
    for s_name in session_names:
        session_path = os.path.join(SESSIONS_DIR, s_name)
        app = Client(session_path, no_updates=True)
        try:
            await app.start()
            me = await app.get_me()
            app.me = me
            active_apps.append(app)
        except Exception as e:
            print(f"Ошибка загрузки [{s_name}]: {e}")

    if active_apps:
        await run_farm(active_apps, source_chats)

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
