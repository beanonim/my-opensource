from localapi.colors import p, i
from functions.runner import execute_search

def search_email():
    query = i("root:/почта $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "email")

