from modules.console import console
from modules.input import v2i
from modules.config import USERNAME, UUID
from modules.theme_manager import clear_theme_overrides, save_config, load_config
from modules.console_utils import update_console_theme
from modules.modules.runner import run_module
from modules.modules.registry import get_visual_modules, get_function_modules


def disable_active_visual_module():
    active = load_config(USERNAME).get('active_visual_module', '')
    clear_theme_overrides(USERNAME)
    save_config(USERNAME, 'custom_banner', '')
    save_config(USERNAME, 'banner_style', 'standard')
    save_config(USERNAME, 'banner_layout', 'down')
    save_config(USERNAME, 'style', 'standard')
    save_config(USERNAME, 'left_bracket', '[')
    save_config(USERNAME, 'right_bracket', ']')
    save_config(USERNAME, 'theme', 'standard')
    save_config(USERNAME, 'active_visual_module', '')
    update_console_theme(console, USERNAME)
    if active:
        console.print(f'\n[success]✓ Визуальный модуль "{active}" выключен[/success]')
        console.print('[dim]Оформление возвращено к стандартному.[/dim]')
    else:
        console.print('\n[success]✓ Оформление сброшено к стандартному[/success]')


def visual_modules_menu():
    console.print('\n[bold secondary]Визуальные модули (оформление)[/bold secondary]\n')
    active = load_config(USERNAME).get('active_visual_module', '')
    mods = get_visual_modules()
    if not mods:
        console.print('[dim]Нет установленных визуальных модулей[/dim]')
        console.print("[dim]Создай модуль с module_type = 'visual' или установи его по ссылке.[/dim]")
        console.print('[dim]Запуск такого модуля меняет темы, цвета и баннер софта.[/dim]\n')
        input('Нажмите Enter для возврата...')
        return

    for i, (fname, meta) in enumerate(mods, 1):
        mark = ' [success]✓ активен[/success]' if meta['name'] == active else ''
        console.print(f'[primary][{i}][/primary] {meta["name"]} [dim]{meta["version"]} by {meta["developer"]}[/dim]{mark}')
    if active:
        console.print(f'[dim]Сейчас включён: {active}[/dim]')
    console.print('[primary][9][/primary] Выключить активный визуальный модуль')
    console.print('[primary][0][/primary] Назад\n')

    choice = v2i('Выберите модуль', f'{USERNAME}@{UUID}').strip()

    if choice == '0':
        return
    if choice == '9':
        confirm = v2i('Выключить активный визуальный модуль? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
        if confirm == 'y':
            disable_active_visual_module()
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(mods):
            run_module(mods[idx][0])
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()
        else:
            console.print('[error]Неверный выбор[/error]')
    except ValueError:
        console.print('[error]Неверный выбор[/error]')


def my_functions_menu():
    console.print('\n[bold secondary]Мои функции (в главном меню)[/bold secondary]\n')
    fns = get_function_modules()
    if not fns:
        console.print('[dim]Нет установленных функциональных модулей[/dim]')
        console.print("[dim]Создай модуль с module_type = 'function' — он появится в главном меню.[/dim]\n")
        input('Нажмите Enter для возврата...')
        return

    console.print('[dim]Эти модули добавлены в главное меню:[/dim]\n')
    for code, fname, meta in fns:
        console.print(f'[primary][{code}][/primary] {meta["name"]} [dim]{meta["version"]} by {meta["developer"]}[/dim]')
    console.print('\n[dim]Запуск — просто введи код в главном меню.[/dim]\n')
    input('Нажмите Enter для возврата...')
