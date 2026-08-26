from localapi.colors import p, i
from functions.runner import execute_search

def search_passport():
    query = i("root:/паспорт $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "passport")

