import aiohttp
import asyncio
import json
import re


def normalize_search_type(search_type: str) -> str:
    mapping = {
        "phone": "phone",
        "email": "email",
        "fio": "name",
        "name": "name",
        "nickname": "username",
        "username": "username",
        "instagram": "username",
        "telegram": "username",
        "vk": "username",
        "facebook": "username",
        "ok": "username",
        "car": "vehicle",
        "vehicle": "vehicle",
        "card": "card",
        "passport": "passport",
        "ip": "ip",
        "inn": "inn",
        "snils": "snils",
        "password": "password"
    }
    return mapping.get(search_type, search_type)


def normalize_query(query: str, search_type: str) -> str:
    query = (query or "").strip()
    if search_type == "phone":
        return re.sub(r"\D", "", query)
    return query


def build_bigbase_headers(token: str):
    return [
        {"Authorization": token},
        {"Authorization": f"Bearer {token}"},
        {"X-API-Key": token},
    ]


APIS = {
    "HateAPI #1": {
        "name": "DarkSearch",
        "url": "https://deepscan.cc/api/v1/search",
        "token": "deepscan_8293763126:mNBVpROy",
        "bases": 12
    },
    "HateAPI #2": {
        "name": "Infinity",
        "url": "https://infinity-search.fun/",
        "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "bases": 2
    },
    "HateAPI #3": {
        "name": "Snusbase",
        "url": "https://api.snusbase.com/data/search",
        "token": "sbmeovhou6ecsn9fd9wcwnwwvsvwnc",
        "bases": 1
    },
    "HateAPI #4": {
        "name": "Seon",
        "url": "https://api.seon.io/SeonRestService/phone-api/v2",
        "token": "758f5f54-befb-4125-bd17-931689af6633",
        "bases": 1
    },
    "HateAPI #5": {
        "name": "LeakOsint",
        "url": "https://leakosintapi.com/",
        "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "bases": 5
    },
    "HateAPI #6": {
        "name": "Infernal BigBase",
        "url": "https://bigbase.top/api/search",
        "token": "mAC3RghEqL-BDdVKMeq2D5mi8e5mSGch",
        "bases": 25
    },
    "HateAPI #7": {
        "name": "DepSearch",
        "url": "https://api.depsearch.sbs/v1/search",
        "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        "bases": 5
    }
}

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_KEY = "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

SYS_PROMPT = (
    "Ты — опытный OSINT-аналитик. Я передаю тебе собранные разрозненные данные по объект в формате JSON. "
    "Твоя задача — проанализировать их, сопоставить факты, найти наиболее вероятные правдивые "
    "значения (ФИО, дата рождения/возраст, соцсети, почты, адреса, работа) и выдать структурированное итоговое досье. "
    "Пиши обычным текстом, БЕЗ использования Markdown (без звездочек, решеток и жирного шрифта). "
    "Не пиши ничего лишнего, только итоговый отчет. Отсеивай явные ошибки или противоречивый мусор."
)

async def _fetch_leakosint_token():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://pastebin.com/raw/pqTvg2Wa", timeout=5) as r:
                text = await r.text()
                match = re.search(r'[A-Za-z0-9_-]{16,}', text)
                if match:
                    return match.group(0).strip()
    except Exception:
        pass
    return APIS["HateAPI #5"]["token"]

async def _req_deepscan(session, query, search_type):
    async with session.post(
        APIS["HateAPI #1"]["url"],
        json={"token": APIS["HateAPI #1"]["token"], "search": query, "type": search_type},
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

async def _req_infinity(session, query, search_type):
    async with session.get(
        APIS["HateAPI #2"]["url"],
        params={"query": query, "type": search_type, "token": APIS["HateAPI #2"]["token"]},
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

async def _req_snusbase(session, query, search_type):
    async with session.post(
        APIS["HateAPI #3"]["url"],
        headers={"Content-Type": "application/json", "Auth": APIS["HateAPI #3"]["token"]},
        json={"terms": [query], "types": [search_type]},
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

async def _req_seon(session, query, search_type):
    if search_type != "phone":
        return {"ok": False, "message": "Unsupported type"}
    async with session.post(
        APIS["HateAPI #4"]["url"],
        headers={"X-API-KEY": APIS["HateAPI #4"]["token"]},
        json={
            "phone": query,
            "config": {
                "timeout": 5000,
                "priority_timeout": 5000,
                "priority_sites": "",
                "include": "cnam_lookup",
                "flags_timeframe_days": 365
            }
        },
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

async def _req_leakosint(session, query, search_type):
    token = await _fetch_leakosint_token()
    async with session.post(
        APIS["HateAPI #5"]["url"],
        json={
            "token": token,
            "request": query,
            "limit": 100,
            "lang": "en",
            "type": "json"
        },
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

async def _req_infernal(session, query, search_type):
    token = APIS["HateAPI #6"]["token"]
    headers_list = build_bigbase_headers(token)
    last_error = None
    for headers in headers_list:
        try:
            async with session.post(
                APIS["HateAPI #6"]["url"],
                headers=headers,
                json={
                    "search": query,
                    "page": 0
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as r:
                payload = await r.json()
                if isinstance(payload, dict) and payload.get("error") and "автор" in str(payload.get("error")).lower():
                    last_error = payload
                    continue
                return payload
        except Exception as e:
            last_error = {"error": str(e)}
    if last_error is not None:
        return last_error
    return {"error": "Ошибка авторизации!"}

async def _req_depsearch(session, query, search_type):
    async with session.post(
        APIS["HateAPI #7"]["url"],
        json={"token": APIS["HateAPI #7"]["token"], "request": query, "type": search_type},
        timeout=aiohttp.ClientTimeout(total=30)
    ) as r:
        return await r.json()

ERROR_MAP = {
    "HateAPI #1": _req_deepscan,
    "HateAPI #2": _req_infinity,
    "HateAPI #3": _req_snusbase,
    "HateAPI #4": _req_seon,
    "HateAPI #5": _req_leakosint,
    "HateAPI #6": _req_infernal,
    "HateAPI #7": _req_depsearch,
}

async def _safe_call(api_id, session, query, search_type):
    try:
        normalized_type = normalize_search_type(search_type)
        normalized_query = normalize_query(query, normalized_type)
        return api_id, await ERROR_MAP[api_id](session, normalized_query, normalized_type)
    except aiohttp.ClientResponseError as e:
        return api_id, {"error_code": e.status, "reason": "API временно недоступен"}
    except asyncio.TimeoutError:
        return api_id, {"error_code": 408, "reason": "Превышено время ожидания"}
    except Exception:
        return api_id, {"error_code": 0, "reason": "Неизвестная ошибка"}

async def search_target(query: str, search_type: str) -> dict:
    async with aiohttp.ClientSession() as session:
        tasks = [_safe_call(aid, session, query, search_type) for aid in ERROR_MAP]
        done = await asyncio.gather(*tasks)
    return dict(done)

async def ai_analyze(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                    "messages": [
                        {"role": "system", "content": SYS_PROMPT},
                        {"role": "user", "content": payload}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 4096
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as r:
                resp = await r.json()
                return resp["choices"][0]["message"]["content"]
    except Exception:
        return "Ошибка AI-анализа"

