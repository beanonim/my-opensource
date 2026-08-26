import requests
import json
import re
from modules.console import console
from modules.input import v2i
from modules.config import USERNAME, UUID
from modules.modules.meta import get_meta
from modules.modules.marketplace import _save, _validate

KVDB_BUCKET = "331LsFpVfgG53nVPyLW2CS"
KVDB_URL = f"https://kvdb.io/{KVDB_BUCKET}/"


def _fetch_modules():
    try:
        r = requests.get(f"{KVDB_URL}?format=json&values=true", timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception:
        console.print('[error]Ошибка подключения к Маркетплейсу[/error]')
        return None

    if not data:
        console.print('[warning]Маркетплейс пока пуст.[/warning]')
        return None

    modules_list = []
    for key, value in data:
        try:
            if isinstance(value, str):
                mod_data = json.loads(value)
            else:
                mod_data = value
            mod_data['_key'] = key
            modules_list.append(mod_data)
        except:
            pass

    if not modules_list:
        console.print('[warning]Нет доступных модулей.[/warning]')
        return None

    return modules_list


def _trunc(text, width):
    return text.ljust(width) if len(text) <= width else text[:width - 3] + '...'


def _print_market_table(modules_list):
    col = {'n': 3, 'name': 22, 'ver': 8, 'dev': 16, 'status': 10}
    header = (
        f"{'#':<{col['n']}}  "
        f"{'Название':<{col['name']}}  "
        f"{'Версия':<{col['ver']}}  "
        f"{'Создатель':<{col['dev']}}  "
        f"{'Статус':<{col['status']}}"
    )
    console.print(f'[dim]{header}[/dim]')
    console.print(f'[dim]{"─" * (sum(col.values()) + 8)}[/dim]')
    for i, mod in enumerate(modules_list, 1):
        status = '🔒 скрыт' if mod.get('hide_source') else 'открыт'
        console.print(
            f"[primary]{str(i):<{col['n']}}[/primary]  "
            f"{_trunc(mod.get('name', '?'), col['name'])}  "
            f"{_trunc(mod.get('version', '?'), col['ver'])}  "
            f"{_trunc(mod.get('developer', '?'), col['dev'])}  "
            f"{_trunc(status, col['status'])}"
        )
    console.print()


def publish_to_global_market(code):
    console.print('\n[secondary]Публикация в Глобальный Маркетплейс[/secondary]')

    err = _validate(code)
    if err:
        console.print(f'[error]Код невалиден: {err}[/error]')
        return

    meta = get_meta(code)
    mod_name = meta['name']
    if mod_name == '?':
        console.print('[error]У модуля нет имени![/error]')
        return

    safe_name = re.sub(r'[^\w\-]', '_', mod_name.lower())
    module_key = f"{safe_name}_{UUID[:8]}"

    hide_src = v2i('Запретить скачивание исходного кода? (y/n)', f'{USERNAME}@{UUID}').strip().lower() == 'y'

    payload = {
        "uuid": UUID,
        "developer": USERNAME,
        "name": mod_name,
        "description": meta.get('description', 'Без описания'),
        "version": meta.get('version', 'v1.0'),
        "code": code,
        "hide_source": hide_src
    }

    console.print('[dim]Публикация...[/dim]')
    try:
        r = requests.put(f"{KVDB_URL}{module_key}", json=payload, timeout=15)
        r.raise_for_status()
        console.print(f'[success]Модуль "{mod_name}" успешно опубликован в Глобальном Маркетплейсе![/success]')
    except Exception:
        console.print('[error]Ошибка при публикации[/error]')


def browse_global_market():
    console.print('\n[bold secondary]Глобальный Маркетплейс[/bold secondary]')
    console.print('[dim]Загрузка списка модулей...[/dim]')

    modules_list = _fetch_modules()
    if not modules_list:
        return

    _print_market_table(modules_list)
    console.print('[primary][0][/primary] Назад\n')
    
    sel = v2i('Выберите модуль', f'{USERNAME}@{UUID}').strip()
    if sel == '0':
        return
        
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(modules_list):
            mod = modules_list[idx]
            _interact_with_global_module(mod)
        else:
            console.print('[error]Неверный выбор[/error]')
    except ValueError:
        console.print('[error]Неверный выбор[/error]')


def _interact_with_global_module(mod):
    while True:
        console.print(f'\n[bold secondary]Модуль: {mod.get("name")}[/bold secondary]')
        console.print(f'[dim]Описание: {mod.get("description")}[/dim]')
        console.print(f'[dim]Разработчик: {mod.get("developer")}[/dim]')

        is_owner = (mod.get("uuid") == UUID)

        console.print('\n[primary][1][/primary] Скачать и установить')

        if not mod.get("hide_source") or is_owner:
            console.print('[primary][2][/primary] Посмотреть исходный код')

        if is_owner:
            console.print('[error][9][/error] Удалить модуль из Маркетплейса')

        console.print('[primary][0][/primary] Назад\n')

        sel = v2i('Действие', f'{USERNAME}@{UUID}').strip()

        if sel == '0':
            return
        elif sel == '1':
            if not mod.get("hide_source") or is_owner:
                from modules.modules.marketplace import _validate
                code = mod.get("code", "")
                err = _validate(code)
                if err:
                    console.print(f'[error]{err}[/error]')
                    return
                meta = get_meta(code)
                fname = _save(code, meta)
                if fname:
                    console.print(f'\n[success]Установлено как {fname}[/success]')
                return
            else:
                console.print('[error]Исходный код скрыт — скачивание невозможно[/error]')
        elif sel == '2' and (not mod.get("hide_source") or is_owner):
            console.print('\n[secondary]Исходный код:[/secondary]')
            console.print(mod.get("code"))
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()
        elif sel == '9' and is_owner:
            conf = v2i('Вы уверены? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
            if conf == 'y':
                try:
                    requests.delete(f"{KVDB_URL}{mod.get('_key')}", timeout=10)
                    console.print('[success]Модуль удален![/success]')
                    return
                except Exception:
                    console.print('[error]Ошибка при удалении[/error]')
        else:
            console.print('[error]Неверный выбор или нет прав[/error]')
