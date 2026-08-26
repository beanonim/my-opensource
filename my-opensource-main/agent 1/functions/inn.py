from localapi.colors import p, i
from functions.runner import execute_search

def search_inn():
    query = i("root:/ИНН $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "inn")

