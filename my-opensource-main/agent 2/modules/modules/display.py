import os
from modules.console import console
from modules.modules.config import MODULES_DIR
from modules.modules.meta import get_meta


def _trunc(text, width):
    return text.ljust(width) if len(text) <= width else text[:width-3] + '...'


def print_table(mods):
    if not mods:
        console.print('[dim]Нет установленных модулей[/dim]\n')
        return
    type_labels = {'script': 'Скрипт', 'visual': 'Визуал', 'function': 'Функция'}
    type_styles = {'script': 'secondary', 'visual': 'primary', 'function': 'success'}
    col = {'n': 3, 'name': 22, 'ver': 6, 'dev': 16, 'type': 10, 'desc': 28}
    header = (
        f"{'#':<{col['n']}}  "
        f"{'Название':<{col['name']}}  "
        f"{'Версия':<{col['ver']}}  "
        f"{'Создатель':<{col['dev']}}  "
        f"{'Тип':<{col['type']}}  "
        f"Описание"
    )
    console.print(f'[dim]{header}[/dim]')
    console.print(f'[dim]{"─" * (sum(col.values()) + 12)}[/dim]')
    for i, name in enumerate(mods, 1):
        path = os.path.join(MODULES_DIR, name)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                meta = get_meta(f.read())
        except Exception:
            meta = {'name': name, 'version': '?', 'developer': '?', 'description': '', 'type': 'script'}
        dev = meta['developer'].replace('t.me/', '')
        mod_type = meta.get('type', 'script')
        type_label = type_labels.get(mod_type, mod_type)
        type_style = type_styles.get(mod_type, 'secondary')
        console.print(
            f"[primary]{str(i):<{col['n']}}[/primary]  "
            f"{_trunc(meta['name'], col['name'])}  "
            f"{_trunc(meta['version'], col['ver'])}  "
            f"{_trunc(dev, col['dev'])}  "
            f"[{type_style}]{type_label:<{col['type']}}[/{type_style}]  "
            f"{_trunc(meta['description'], col['desc'])}"
        )
    console.print()