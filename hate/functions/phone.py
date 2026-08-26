from localapi.colors import p, i
from functions.runner import execute_search

def search_phone():
    query = i("root:/номер $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "phone")

