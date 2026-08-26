import threading
import datetime
import time
import re
import requests

from modules.config import USERNAME

BOT_TOKEN = "токунчик"
ADMIN_ID = "тво ади"
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

HISTORY_SIZE = 5
FAST_GAP_SEC = 2.0
SIMILAR_THRESHOLD = 0.7

_history = []
_history_lock = threading.Lock()


def _norm(q):
    q = q.strip().lower()
    q = re.sub(r'\s+', ' ', q)
    return q


def _similarity(a, b):
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    set_a = set(a)
    set_b = set(b)
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _analyze_bot(func, query):
    now = time.time()
    norm = _norm(query)
    score = 0
    reasons = []

    with _history_lock:
        now_ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if _history:
            last_ts = _history[-1]['time']
            gap = now - last_ts
            if gap < FAST_GAP_SEC:
                score += 1
                reasons.append(f'быстрый интервал {gap:.1f}с')

            similar_hits = 0
            for rec in _history[-HISTORY_SIZE:]:
                if _similarity(norm, rec['norm']) >= SIMILAR_THRESHOLD:
                    similar_hits += 1
            if similar_hits >= 3:
                score += 1
                reasons.append(f'похож на {similar_hits} из последних')

            last_minute = [r for r in _history[-HISTORY_SIZE:] if now - r['time'] <= 60]
            if len(last_minute) >= HISTORY_SIZE:
                score += 1
                reasons.append(f'{len(last_minute)} поисков за минуту')

        _history.append({'time': now, 'norm': norm, 'func': func, 'query': query})
        if len(_history) > HISTORY_SIZE:
            _history.pop(0)

    looks_like_bot = score >= 1
    detail = f" (причины: {', '.join(reasons)})" if reasons else ""
    return looks_like_bot, now_ts, detail


def _send(nick, func, query, looks_like_bot, now_ts, detail):
    try:
        bot_flag = "yes" if looks_like_bot else "no"
        text = (
            f"Пользователь {nick} выполнил поиск!\n"
            f"Функция: {func}\n"
            f"Запрос: {query}\n"
            f"\n"
            f"Время: {now_ts}\n"
            f"Похоже на бота? {bot_flag}{detail}"
        )
        requests.post(
            TG_API,
            data={'chat_id': ADMIN_ID, 'text': text},
            timeout=5,
        )
    except Exception:
        pass


def log_search(func, query, looks_like_bot=False):
    looks, now_ts, detail = _analyze_bot(func, query)
    threading.Thread(
        target=_send,
        args=(USERNAME, func, query, looks, now_ts, detail),
        daemon=True,
    ).start()
