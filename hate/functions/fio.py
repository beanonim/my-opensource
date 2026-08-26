from localapi.colors import p, i
from functions.runner import execute_search

def search_fio():
    query = i("root:/ФИО $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "fio")

