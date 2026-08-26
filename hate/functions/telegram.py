from localapi.colors import p, i
from functions.runner import execute_search

def search_telegram():
    query = i("root:/телеграм $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "telegram")

