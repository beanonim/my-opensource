import datetime
from modules.theme_manager import load_config, save_config
from modules.config import USERNAME

DAILY_SEARCH_LIMIT = 10

def _today():
    return datetime.date.today().isoformat()

def get_search_count():
    config = load_config(USERNAME)
    today = _today()
    if config.get('search_date') != today:
        return 0
    try:
        return int(config.get('search_count', '0'))
    except ValueError:
        return 0

def searches_left():
    return max(0, DAILY_SEARCH_LIMIT - get_search_count())

def register_search():
    config = load_config(USERNAME)
    today = _today()
    if config.get('search_date') != today:
        count = 1
        save_config(USERNAME, 'search_date', today)
    else:
        try:
            count = int(config.get('search_count', '0')) + 1
        except ValueError:
            count = 1
    save_config(USERNAME, 'search_count', str(count))

def is_limit_reached():
    return get_search_count() >= DAILY_SEARCH_LIMIT
