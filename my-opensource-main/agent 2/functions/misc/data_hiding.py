import json, os, time, threading
import requests
from rich.table import Table
from modules.config import USERNAME
from modules.console import console
from modules.input import v2i

KVDB_BUCKET = "331LsFpVfgG53nVPyLW2CS"
KVDB_KEY = "global_protected"
KVDB_URL = f"https://kvdb.io/{KVDB_BUCKET}/{KVDB_KEY}"

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
CACHE_FILE = os.path.join(CACHE_DIR, 'protected_data.json')

_protected_data = None
_data_lock = threading.Lock()
_last_sync = 0
_SYNC_INTERVAL = 60

def _make_key(query, category):
    if category == 'phone':
        return f'phone:{_clean_phone(query)}'
    return f'{category}:{query.strip().lower()}'

def _clean_phone(phone):
    return ''.join(c for c in phone if c.isdigit())

def _fetch_remote():
    try:
        r = requests.get(KVDB_URL, timeout=5)
        if r.status_code == 200 and r.text.strip():
            return json.loads(r.text)
    except Exception:
        pass
    return None

def _push_remote(data):
    try:
        requests.post(KVDB_URL, data=json.dumps(data), timeout=5)
    except Exception:
        pass

def _load_local():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None

def _save_local(data):
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_protected():
    global _protected_data, _last_sync
    with _data_lock:
        if _protected_data is None:
            _protected_data = _load_local() or {}
        now = time.time()
        if now - _last_sync > _SYNC_INTERVAL:
            _last_sync = now
            remote = _fetch_remote()
            if remote is not None:
                _protected_data = remote
                _save_local(_protected_data)
        return _protected_data

def is_protected(query, category='phone'):
    data = load_protected()
    return _make_key(query, category) in data

def get_protection_info(query, category='phone'):
    data = load_protected()
    return data.get(_make_key(query, category))

_CATEGORY_LABELS = {
    'phone': 'номер', 'email': 'email', 'username': 'никнейм',
    'vk_id': 'ID ВКонтакте', 'ip': 'IP-адрес', 'snils': 'СНИЛС',
    'telegram': 'Telegram', 'vin': 'VIN', 'fio': 'ФИО',
    'imei': 'IMEI', 'domain': 'домен',
}

def check_protected(query, category):
    if not is_protected(query, category):
        return False
    info = get_protection_info(query, category)
    label = _CATEGORY_LABELS.get(category, category)
    if info and info.get('show_nick'):
        console.print(f'\n[warning]Поиск по данному {label} защищен пользователем {info["protector"]}![/warning]')
    else:
        console.print(f'\n[warning]Поиск по данному {label} защищен![/warning]')
    console.print('[dim]Нажмите Enter для продолжения...[/dim]')
    input()
    return True

def add_protection(query, category='phone', show_nick=True):
    data = load_protected()
    key = _make_key(query, category)

    if key in data:
        return False, 'Эти данные уже защищены'

    user_items = [v for v in data.values() if v.get('protector') == USERNAME]
    if len(user_items) >= 5:
        return False, 'Лимит защищённых записей: 5'

    data[key] = {
        'protector': USERNAME,
        'show_nick': show_nick,
        'category': category,
        'query': query,
        'timestamp': time.time()
    }

    with _data_lock:
        _protected_data = data
    _save_local(data)
    _push_remote(data)
    return True, 'Данные успешно защищены'

def remove_protection(key):
    data = load_protected()
    if key not in data:
        return False, 'Запись не найдена'
    entry = data[key]
    if entry.get('protector') != USERNAME:
        return False, 'Вы не можете удалить чужую защиту'

    del data[key]
    with _data_lock:
        _protected_data = data
    _save_local(data)
    _push_remote(data)
    return True, 'Защита успешно снята'

def get_user_protected():
    data = load_protected()
    return {k: v for k, v in data.items() if v.get('protector') == USERNAME}

def data_hiding_menu():
    while True:
        data = load_protected()
        user_items = {k: v for k, v in data.items() if v.get('protector') == USERNAME}
        count = len(user_items)

        console.print('[bold secondary]Скрытие данных[/bold secondary]\n')
        console.print(f'[dim]Защищено записей: {count}/5[/dim]\n')
        console.print('[primary][1][/primary] Скрыть данные')
        console.print('[primary][2][/primary] Мои скрытые данные')
        console.print('[primary][3][/primary] Убрать скрытие')
        console.print('[primary][0][/primary] Назад\n')

        choice = v2i('Выберите действие', f'{USERNAME}').strip()

        if choice == '1':
            _hide_data_menu()
        elif choice == '2':
            _list_protected(user_items)
        elif choice == '3':
            _unhide_data_menu(user_items)
        elif choice == '0':
            break
        else:
            console.print('\n[error]Неверный выбор[/error]')

        if choice != '2':
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()

def _hide_data_menu():
    console.print('\n[bold secondary]Выберите категорию:[/bold secondary]')
    console.print('[primary][1][/primary] Номер телефона')
    console.print('[primary][2][/primary] Email')
    console.print('[primary][3][/primary] Username / Никнейм')
    console.print('[primary][0][/primary] Отмена\n')

    cat_choice = v2i('Выберите категорию', f'{USERNAME}').strip()
    cat_map = {'1': 'phone', '2': 'email', '3': 'username'}
    if cat_choice not in cat_map:
        return

    category = cat_map[cat_choice]
    cat_labels = {'phone': 'номер', 'email': 'email', 'username': 'никнейм'}
    value = v2i(f'Введите {cat_labels[category]} для защиты', f'{USERNAME}')

    if not value.strip():
        console.print('\n[error]Значение не может быть пустым[/error]')
        return

    show_nick_choice = v2i('Показывать ваш ник в предупреждении? (y/n)', f'{USERNAME}').strip().lower()
    show_nick = show_nick_choice == 'y'

    success, msg = add_protection(value.strip(), category, show_nick)
    if success:
        console.print(f'\n[success]✓ {msg}[/success]')
    else:
        console.print(f'\n[error]{msg}[/error]')

def _list_protected(user_items):
    if not user_items:
        console.print('\n[dim]У вас пока нет защищённых записей[/dim]')
        console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
        input()
        return

    table = Table(show_header=True, box=None, padding=(0, 2))
    table.add_column('#', style='primary', width=3)
    table.add_column('Категория', style='secondary', width=12)
    table.add_column('Значение', style='text', width=30)
    table.add_column('Показывать ник', style='dim', width=16)

    for i, (key, info) in enumerate(user_items.items(), 1):
        cat_label = {'phone': 'Телефон', 'email': 'Email', 'username': 'Username'}.get(info.get('category', ''), info.get('category', ''))
        nick_status = '[success]Да[/success]' if info.get('show_nick') else '[error]Нет[/error]'
        table.add_row(str(i), cat_label, info.get('query', ''), nick_status)

    console.print()
    console.print(table)
    console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
    input()

def _unhide_data_menu(user_items):
    if not user_items:
        console.print('\n[dim]Нет записей для удаления[/dim]')
        return

    items_list = list(user_items.items())
    console.print('\n[bold secondary]Выберите запись для снятия защиты:[/bold secondary]\n')
    for i, (key, info) in enumerate(items_list, 1):
        cat_label = {'phone': 'Телефон', 'email': 'Email', 'username': 'Username'}.get(info.get('category', ''), info.get('category', ''))
        console.print(f'[primary][{i}][/primary] {cat_label}: {info.get("query", "")}')

    console.print('[primary][0][/primary] Отмена\n')

    choice = v2i('Выберите запись', f'{USERNAME}').strip()
    if choice == '0' or not choice.isdigit():
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(items_list):
        console.print('\n[error]Неверный выбор[/error]')
        return

    key = items_list[idx][0]
    confirm = v2i(f'Снять защиту? (y/n)', f'{USERNAME}').strip().lower()
    if confirm != 'y':
        return

    success, msg = remove_protection(key)
    if success:
        console.print(f'\n[success]✓ {msg}[/success]')
    else:
        console.print(f'\n[error]{msg}[/error]')
