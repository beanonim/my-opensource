from localapi.colors import p, i
from functions.runner import execute_search

def search_vk():
    query = i("root:/ВКонтакте $ ").strip()
    if not query: return p("Пустой запрос")
    execute_search(query, "vk")

