import os
from modules.console import console
from modules.config import USERNAME
from modules.modules.config import MODULES_DIR
from modules.modules.meta import get_meta
from modules.modules.interpreter import LWInterpreter, ModuleError
from modules.console_utils import update_console_theme
from modules.theme_manager import save_config


def list_modules():
    os.makedirs(MODULES_DIR, exist_ok=True)
    return [f for f in sorted(os.listdir(MODULES_DIR)) if f.endswith('.lw')]


def run_module(filename):
    path = os.path.join(MODULES_DIR, filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        console.print(f'[error]Не удалось загрузить модуль: {e}[/error]')
        return
    meta = get_meta(source)
    console.print(f'\n[primary]{meta["name"]}[/primary] [dim]{meta["version"]} by {meta["developer"]}[/dim]\n')
    try:
        LWInterpreter(source).run()
    except ModuleError:
        console.print('[error]Ошибка модуля[/error]')
    except Exception:
        console.print('[error]Внутренняя ошибка[/error]')
    _after_run(meta)


def run_code(source):
    meta = get_meta(source)
    console.print(f'\n[primary]{meta["name"]}[/primary] [dim]{meta["version"]} by {meta["developer"]}[/dim]\n')
    try:
        LWInterpreter(source).run()
    except ModuleError:
        console.print('[error]Ошибка модуля[/error]')
    except Exception:
        console.print('[error]Внутренняя ошибка[/error]')
    _after_run(meta)


def _after_run(meta):
    if meta.get('type') == 'visual':
        update_console_theme(console, USERNAME)
        save_config(USERNAME, 'active_visual_module', meta['name'])
        console.print('\n[success]✓ Визуальные изменения применены![/success]')
    elif meta.get('type') == 'function':
        console.print('\n[info]Модуль зарегистрирован в главном меню.[/info]')