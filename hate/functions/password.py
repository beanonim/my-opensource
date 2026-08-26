from localapi.colors import p, i
from functions.runner import execute_search

def search_password():
    query = i("root:/пароль $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "password")

