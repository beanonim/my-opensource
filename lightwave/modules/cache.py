import os
import json
import re

CACHE_DIR = "cache"

def normalize_query(query, category):
    """
    Нормализует поисковый запрос в зависимости от категории.
    Для телефонов: оставляет только цифры.
    Для остального: убирает пробелы и приводит к нижнему регистру.
    """
    if not query:
        return "empty"
    
    if category == "phone":
        normalized = re.sub(r'\D', '', str(query))
        return normalized if normalized else "invalid_phone"
    
    return str(query).strip().lower()

def get_cache_path(category, query, api_id):
    """
    Возвращает путь к файлу кэша для конкретного запроса и API.
    """
    safe_category = re.sub(r'[^\w\-]', '_', str(category).strip().lower())[:32] or '_default'
    norm_query = normalize_query(query, category)
    
    folder_path = os.path.join(CACHE_DIR, safe_category, norm_query)
    
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path, exist_ok=True)
        except Exception:
            pass
            
    safe_api_id = re.sub(r'[^\w\-]', '_', str(api_id))
    return os.path.join(folder_path, f"{safe_api_id}.json")

def save_cache(category, query, api_id, data):
    """
    Сохраняет данные в кэш.
    """
    if not data:
        return False
        
    try:
        path = get_cache_path(category, query, api_id)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception:
        return False

def load_cache(category, query, api_id):
    """
    Загружает данные из кэша.
    """
    try:
        path = get_cache_path(category, query, api_id)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None