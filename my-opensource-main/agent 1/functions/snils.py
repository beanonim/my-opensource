from localapi.colors import p, i
from functions.runner import execute_search

def search_snils():
    query = i("root:/СНИЛС $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "snils")

