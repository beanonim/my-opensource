from localapi.colors import p, i
from functions.runner import execute_search

def search_car():
    query = i("root:/авто $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "car")

