from localapi.colors import p, i
from functions.runner import execute_search

def search_ok():
    query = i("root:/одноклассники $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "ok")

