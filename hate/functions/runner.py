import asyncio
import json
from datetime import datetime
from api import search_target, ai_analyze, APIS
from localapi.colors import p


def log_error(api_id, query, search_type, data):
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {api_id} | query={query} | type={search_type}\n")
        f.write(f"{json.dumps(data, ensure_ascii=False, indent=2)}\n")
        f.write("-" * 80 + "\n")

def print_tree(obj, indent="", is_last=True):
    if isinstance(obj, dict):
        items = list(obj.items())
        for idx, (key, val) in enumerate(items):
            last_item = (idx == len(items) - 1)
            item_branch = "└── " if last_item else "├── "
            if isinstance(val, (dict, list)):
                p(f"{indent}{item_branch}{key}")
                print_tree(val, indent + ("    " if last_item else "│   "), last_item)
            else:
                if val is not None and str(val).strip():
                    p(f"{indent}{item_branch}{key}: {val}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            last_item = (idx == len(obj) - 1)
            item_branch = "└── " if last_item else "├── "
            if isinstance(item, (dict, list)):
                p(f"{indent}{item_branch}[{idx}]")
                print_tree(item, indent + ("    " if last_item else "│   "), last_item)
            else:
                if item is not None and str(item).strip():
                    p(f"{indent}{item_branch}{item}")

def execute_search(query, search_type):
    p(f"Запуск поиска [{search_type}] по всем доступным шлюзам...")
    p("└── Выполняю запрос через доступные источники")
    results = asyncio.run(search_target(query, search_type))
    all_data = {}
    for api_id, data in results.items():
        if api_id not in APIS:
            continue
        p("")
        p(f"└── {api_id}")
        if isinstance(data, dict) and "error_code" in data:
            p("    └── временно недоступен")
            log_error(api_id, query, search_type, data)
            continue
        if isinstance(data, dict) and data.get("ok") is False:
            p("    └── без результатов")
            log_error(api_id, query, search_type, data)
            continue
        if isinstance(data, dict) and "error" in data:
            p("    └── ошибка ответа")
            log_error(api_id, query, search_type, data)
            continue
        if isinstance(data, dict) and isinstance(data.get("message"), str):
            msg = data.get("message", "").lower()
            if "error" in msg or "ошибка" in msg or "token" in msg or "автор" in msg:
                p("    └── ошибка ответа")
                log_error(api_id, query, search_type, data)
                continue
        print_tree(data, indent="    ", is_last=True)
        all_data[api_id] = data
    if not all_data:
        p("\nДанные во всех шлюзах отсутствуют.")
        return
    p("")
    p("└── Начинаю перекрестный AI анализ собранной информации...")
    p("    └── Ожидание ответа от Нейросети...")
    report = asyncio.run(ai_analyze(all_data))
    p("")
    for line in report.split('\n'):
        p(f"    {line}")

