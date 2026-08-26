from localapi.colors import p, i
from functions.runner import execute_search

def search_nickname():
    query = i("root:/никнейм $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "nickname")

