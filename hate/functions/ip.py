from localapi.colors import p, i
from functions.runner import execute_search

def search_ip():
    query = i("root:/IP $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "ip")

