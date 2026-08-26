from localapi.colors import p, i
from functions.runner import execute_search

def search_facebook():
    query = i("root:/facebook $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "facebook")

