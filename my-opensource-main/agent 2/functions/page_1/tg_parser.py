import re
import sys
from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from telethon.tl.functions.messages import StartBotRequest

TG_PARSER_API_ID   = 21826549
TG_PARSER_API_HASH = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
BOT_USERNAME       = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
BOT_STARTPARAM     = 'zzaEuOxd0Fw8'
DAILY_BONUS_BTN    = '🎁 Забрать ежедневный бонус'

TOTAL_STEPS = 7


def _step(n):
    sys.stdout.write(f'\r\033[KПарсим [{n}/{TOTAL_STEPS}]')
    sys.stdout.flush()


def _step_done():
    sys.stdout.write('\n')
    sys.stdout.flush()


def _strip_tg_formatting(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)      # **bold**
    text = re.sub(r'__(.+?)__', r'\1', text)            # __italic__
    text = re.sub(r'`{1,3}(.+?)`{1,3}', r'\1', text, flags=re.DOTALL)  # `code`
    text = re.sub(r'\[(.+?)\]\(https?://\S+?\)', r'\1', text)  # [text](url)
    text = re.sub(r'~~(.+?)~~', r'\1', text)            # ~~strike~~
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'\1', text) # _italic_
    return text


async def _click_button_by_text(client, bot_entity, text_fragment, timeout=20):
    for _ in range(timeout):
        await asyncio.sleep(1)
        msgs = await client.get_messages(bot_entity, limit=5)
        for msg in msgs:
            if not msg.buttons:
                continue
            for row in msg.buttons:
                for btn in row:
                    if text_fragment in (btn.text or ''):
                        try:
                            await btn.click()
                            return True
                        except Exception:
                            pass
    return False


async def _run_parser(query: str) -> str:
    phone = v2i(
        'Введите ваш номер телефона (с кодом страны, например +79123456789)',
        f'{USERNAME}@{UUID}'
    ).strip()

    session_name = 'session_tgparser_' + ''.join(c for c in phone if c.isdigit())
    client = TelegramClient(session_name, TG_PARSER_API_ID, TG_PARSER_API_HASH)
    await client.connect()

    _step(1)
    if not await client.is_user_authorized():
        _step_done()
        await client.send_code_request(phone)
        code = v2i('Введите код из Telegram', f'{USERNAME}@{UUID}').strip()
        try:
            await client.sign_in(phone=phone, code=code)
        except errors.SessionPasswordNeededError:
            password = v2i('Введите 2FA пароль', f'{USERNAME}@{UUID}').strip()
            await client.sign_in(password=password)

    _step(2)
    bot_entity = await client.get_entity(BOT_USERNAME)
    await client(StartBotRequest(bot=bot_entity, peer=bot_entity, start_param=BOT_STARTPARAM))
    await asyncio.sleep(1)

    _step(3)
    captcha_clicked = False
    for _ in range(10):
        await asyncio.sleep(1)
        msgs = await client.get_messages(bot_entity, limit=5)
        for msg in msgs:
            if msg.out or not msg.buttons:
                continue
            for row in msg.buttons:
                for btn in row:
                    if btn.text and '✅' in btn.text:
                        try:
                            await btn.click()
                            captcha_clicked = True
                        except Exception:
                            pass
                        break
                if captcha_clicked:
                    break
            if captcha_clicked:
                break
        if captcha_clicked:
            break

    if captcha_clicked:
        await asyncio.sleep(1)

    _step(4)
    await _click_button_by_text(client, bot_entity, DAILY_BONUS_BTN, timeout=20)
    await asyncio.sleep(1)

    _step(5)
    sent = await client.send_message(bot_entity, query)
    sent_id = sent.id

    _step(6)
    collected_ids = set()
    all_texts = []
    last_new = asyncio.get_event_loop().time()

    for _ in range(40):
        await asyncio.sleep(1)
        msgs = await client.get_messages(bot_entity, limit=10)
        got_new = False
        for msg in msgs:
            if msg.out or msg.id <= sent_id or msg.id in collected_ids:
                continue
            text = (msg.text or msg.message or '').strip()
            if text:
                collected_ids.add(msg.id)
                all_texts.append(text)
                got_new = True
        if got_new:
            last_new = asyncio.get_event_loop().time()
        if all_texts and (asyncio.get_event_loop().time() - last_new) >= 3:
            break

    _step(7)
    await asyncio.sleep(1)
    await client.disconnect()
    _step_done()

    if not all_texts:
        return '[Парсер] Бот не ответил'

    JUNK_FRAGMENTS = [
        'void.help', 'Вы находитесь в главном меню',
        'Актуальная рабочая ссылка', 'Сохраните ссылку',
        'нажмите кнопку ниже', 'Подтвердите, что вы человек',
    ]

    def is_junk(line: str) -> bool:
        return any(j.lower() in line.lower() for j in JUNK_FRAGMENTS)

    clean_parts = []
    for text in all_texts:
        text = _strip_tg_formatting(text)
        lines = [l for l in text.splitlines() if not is_junk(l)]
        cleaned = '\n'.join(lines).strip()
        cleaned = cleaned.replace('void', '').replace('Void', '').replace('VOID', '').strip()
        if cleaned:
            clean_parts.append(cleaned)

    sep = '\n' + '─' * 40 + '\n'
    return sep.join(clean_parts)


def tg_parser_search(query: str):
    try:
        result = asyncio.run(_run_parser(query))
        console.print('\n[success]━━━ РЕЗУЛЬТАТ ПАРСЕРА ━━━[/success]')
        console.print(result)
    except KeyboardInterrupt:
        console.print('\n[warning]Прервано пользователем.[/warning]')
    except Exception:
        console.print('\n[error]Ошибка парсера[/error]')
