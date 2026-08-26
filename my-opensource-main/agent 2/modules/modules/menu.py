import os
from modules.console import console
from modules.input import v2i
from modules.config import USERNAME, UUID
from modules.modules.config import MODULES_DIR
from modules.modules.marketplace import browse_marketplace, install_by_url, create_module_guide
from modules.modules.global_market import browse_global_market
from modules.modules.ai_builder import ai_module_builder
from modules.modules.manage import visual_modules_menu, my_functions_menu

def modules_menu():
    os.makedirs(MODULES_DIR, exist_ok=True)
    while True:
        console.print('\n[bold secondary]Меню модулей[/bold secondary]\n')
        console.print('[primary][1][/primary] Установленные модули')
        console.print('[primary][2][/primary] Глобальный Маркетплейс')
        console.print('[primary][3][/primary] Установить по ссылке')
        console.print('[primary][4][/primary] Создать свой модуль')
        console.print('[primary][5][/primary] Написать модуль с помощью ИИ')
        console.print('[primary][6][/primary] Визуальные модули [dim](оформление)[/dim]')
        console.print('[primary][7][/primary] Мои функции [dim](в главном меню)[/dim]')
        console.print('[primary][0][/primary] Назад\n')

        choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()

        if choice == '0':
            break
        elif choice == '1':
            browse_marketplace()
        elif choice == '2':
            browse_global_market()
        elif choice == '3':
            install_by_url()
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()
        elif choice == '4':
            create_module_guide()
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()
        elif choice == '5':
            ai_module_builder()
        elif choice == '6':
            visual_modules_menu()
        elif choice == '7':
            my_functions_menu()
        else:
            console.print('[error]Неверный выбор[/error]')