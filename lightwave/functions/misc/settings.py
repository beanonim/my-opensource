from rich.table import Table
from modules.config import *
from modules.theme_manager import *
from modules.console import *
from modules.input import *
from modules.console_utils import *
from functions.misc.data_hiding import data_hiding_menu
from modules.limits import DAILY_SEARCH_LIMIT, get_search_count

def load_banner_theme(username):
    config = load_config(username)
    return {
        'style': config.get('style', 'standard'),
        'left_bracket': config.get('left_bracket', '['),
        'right_bracket': config.get('right_bracket', ']')
    }

def save_banner_theme(username, theme_dict):
    success = True
    for key, value in theme_dict.items():
        if not save_config(username, key, value):
            success = False
    return success

def get_banner_brackets(username):
    theme = load_banner_theme(username)
    style = theme.get('style', 'standard')
    
    if style == 'none':
        return '', ''
    elif style == 'custom':
        return theme.get('left_bracket', ''), theme.get('right_bracket', '')
    else:
        return '[', ']'

def theme_settings_menu():
    console.print('[bold secondary]Настройка темы интерфейса[/bold secondary]\n')
    console.print('[primary]Выберите тему:[/primary]')
    
    sorted_aliases = sorted(THEME_ALIASES.items(), key=lambda x: int(x[0]))
    
    table = Table(show_header=False, box=None, padding=(0, 4))
    table.add_column("Col1", justify="left")
    table.add_column("Col2", justify="left")
    
    total_themes = len(sorted_aliases)
    mid_point = (total_themes + 1) // 2
    
    for i in range(mid_point):
        key1, name1 = sorted_aliases[i]
        theme_data1 = DEFAULT_THEMES.get(name1, {})
        color1 = theme_data1.get('primary', 'white')
        display_name1 = name1.capitalize().replace('_', ' ')
        item1 = f'[primary][{key1}][/primary] [{color1}]{display_name1}[/{color1}]'
        
        item2 = ""
        if i + mid_point < total_themes:
            key2, name2 = sorted_aliases[i + mid_point]
            theme_data2 = DEFAULT_THEMES.get(name2, {})
            color2 = theme_data2.get('primary', 'white')
            display_name2 = name2.capitalize().replace('_', ' ')
            item2 = f'[primary][{key2}][/primary] [{color2}]{display_name2}[/{color2}]'
            
        table.add_row(item1, item2)
    
    console.print(table)
    console.print('\n[primary][0][/primary] Отмена\n')
    
    choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()
    
    if choice == '0':
        return
        
    if choice in THEME_ALIASES:
        theme_name = THEME_ALIASES[choice]
        if save_user_theme(USERNAME, theme_name):
            update_console_theme(console, USERNAME)
            console.print(f'\n[success]Тема "{theme_name}" успешно установлена![/success]')
            console.print(f'Перезапустите софт, для  применения изменений.')
        else:
            console.print('\n[error]Ошибка сохранения темы[/error]')
    else:
        console.print('\n[error]Неверный выбор[/error]')
    

def banner_brackets_settings():
    current_theme = load_banner_theme(USERNAME)
    left, right = get_banner_brackets(USERNAME)
    
    if current_theme.get('style') == 'none':
        example = '1 Пример пункта меню'
    else:
        example = f'{left}1{right} Пример пункта меню'
    
    console.print(f'[dim]Текущая тема: {example}[/dim]\n')
    console.print('[primary]Выберите стиль:[/primary]')
    console.print('[primary][1][/primary] Стандартные скобки [dim]([test])[/dim]')
    console.print('[primary][2][/primary] Без скобок [dim](test)[/dim]')
    console.print('[primary][3][/primary] Кастомные скобки')
    console.print('[primary][0][/primary] Отмена\n')
    
    choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()
    new_theme = {}
    
    if choice == '1':
        new_theme = {
            'style': 'standard',
            'left_bracket': '[',
            'right_bracket': ']'
        }
        console.print('\n[success]✓ Установлены стандартные скобки[/success]')
    elif choice == '2':
        new_theme = {
            'style': 'none',
            'left_bracket': '',
            'right_bracket': ''
        }
        console.print('\n[success]✓ Скобки отключены[/success]')
    elif choice == '3':
        left_char = v2i('Введите левый символ (или Enter для пропуска)', f'{USERNAME}@{UUID}')
        right_char = v2i('Введите правый символ', f'{USERNAME}@{UUID}')
        new_theme = {
            'style': 'custom',
            'left_bracket': left_char,
            'right_bracket': right_char
        }
        preview = f'{left_char}1{right_char}'
        console.print(f'\n[success]✓ Установлены символы: "{preview}"[/success]')
    elif choice == '0':
        return
    else:
        console.print('\n[error]Неверный выбор[/error]')
        return
    
    if save_banner_theme(USERNAME, new_theme):
        console.print('[success]Настройки сохранены! Изменения вступят в силу после возврата в меню.[/success]')
    else:
        console.print('[error]Ошибка сохранения настроек[/error]')
    

def banner_layout_settings():
    while True:
        cls()
        config = load_config(USERNAME)
        current_layout = config.get('banner_layout', 'down')
        show_sep = config.get('show_layout_separator', 'true') == 'true'
        
        layout_name = 'Сайдбар' if current_layout == 'side' else 'Давнбар (Стандарт)'
        sep_status = '[success]ВКЛ[/success]' if show_sep else '[error]ВЫКЛ[/error]'
        
        console.print(f'[dim]Текущее расположение: {layout_name}[/dim]\n')
        console.print('[primary]Настройка расположения меню:[/primary]')
        console.print('[primary][1][/primary] Давнбар [dim](Выбор снизу, 2x2)[/dim]')
        console.print('[primary][2][/primary] Сайдбар [dim](Выбор сбоку, в столбик)[/dim]')
        console.print(f'[primary][3][/primary] Разделители меню: {sep_status}')
        console.print('[primary][0][/primary] Назад\n')
        
        choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()
        
        if choice == '1':
            if save_config(USERNAME, 'banner_layout', 'down'):
                console.print('\n[success]✓ Установлено стандартное расположение (Давнбар)[/success]')
        elif choice == '2':
            if save_config(USERNAME, 'banner_layout', 'side'):
                console.print('\n[success]✓ Установлено расположение сбоку (Сайдбар)[/success]')
        elif choice == '3':
            new_val = 'false' if show_sep else 'true'
            save_config(USERNAME, 'show_layout_separator', new_val)
            console.print(f'\n[success]Отображение разделителей меню изменено![/success]')
        elif choice == '0':
            break
        else:
            console.print('\n[error]Неверный выбор[/error]')
    

def banner_style_settings():
    config = load_config(USERNAME)
    current_style = config.get('banner_style', 'standard')
    current_color_mode = config.get('banner_color_mode', 'solid')

    style_names = {
        'square': 'Квадратный', 'square2': 'Квадратный 2',
        'classic_cli': 'Classic CLI',
    }
    style_name = style_names.get(current_style, 'Стандартный')
    color_mode_name = 'Градиент' if current_color_mode == 'gradient' else 'Базовый (цвет темы)'

    console.print(f'[dim]Текущий стиль баннера: {style_name}[/dim]')
    console.print(f'[dim]Текущий цвет баннера: {color_mode_name}[/dim]\n')
    console.print('[primary]Выберите стиль баннера:[/primary]')
    console.print('[primary][1][/primary] Стандартный')
    console.print('[primary][2][/primary] Квадратный [dim](В рамке)[/dim]')
    console.print('[primary][3][/primary] Квадратный 2 [dim](Другая рамка)[/dim]')
    console.print('[primary][4][/primary] Classic CLI')
    console.print('[primary]Цвет баннера:[/primary]')
    console.print('[primary][5][/primary] Базовый [dim](цвет из темы)[/dim]')
    console.print('[primary][6][/primary] Градиент [dim](по цветам темы)[/dim]')
    console.print('[primary][0][/primary] Отмена\n')

    choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()

    style_map = {
        '1': ('standard', 'Стандартный'),
        '2': ('square', 'Квадратный'),
        '3': ('square2', 'Квадратный 2'),
        '4': ('classic_cli', 'Classic CLI'),
    }
    if choice in style_map:
        key, label = style_map[choice]
        if save_config(USERNAME, 'banner_style', key):
            console.print(f'\n[success]✓ Установлен стиль: {label}[/success]')
    elif choice in ('5', '6'):
        mode = 'solid' if choice == '5' else 'gradient'
        if save_config(USERNAME, 'banner_color_mode', mode):
            label = 'Базовый' if mode == 'solid' else 'Градиент'
            console.print(f'\n[success]✓ Установлен цвет баннера: {label}[/success]')
            input('Нажмите Enter для возврата...')
    elif choice == '0':
        return
    else:
        console.print('\n[error]Неверный выбор[/error]')
        return
    

def input_settings_menu():
    while True:
        cls()
        config = load_config(USERNAME)
        current_style = config.get('input_style', '1')
        
        styles = {
            '1': 'Стандартный (Блочный)',
            '2': 'Linux (user@uuid)',
            '3': 'Cyber (⚡ lightwave)',
            '4': 'Minimal (❯ title)',
            '5': 'Lambda (λ user)'
        }
        
        style_name = styles.get(current_style, 'Стандартный')
        
        console.print(f'[bold secondary]Настройка стиля ввода[/bold secondary]\n')
        console.print(f'[dim]Текущий стиль: {style_name}[/dim]\n')
        
        console.print('[primary][1][/primary] Стандартный [dim](Блочный заголовок)[/dim]')
        console.print('[primary][2][/primary] Linux [dim](user@uuid $ title > )[/dim]')
        console.print('[primary][3][/primary] Cyber [dim](⚡ lightwave • title ❯)[/dim]')
        console.print('[primary][4][/primary] Minimal [dim](❯ title »)[/dim]')
        console.print('[primary][5][/primary] Lambda [dim](λ user)[/dim]')
        console.print('[primary][0][/primary] Назад\n')
        
        choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()
        
        if choice in ['1', '2', '3', '4', '5']:
            if save_config(USERNAME, 'input_style', choice):
                console.print(f'\n[success]✓ Установлен стиль: {styles[choice]}[/success]')
            else:
                console.print('\n[error]Ошибка сохранения[/error]')
        elif choice == '0':
            break
        else:
            console.print('\n[error]Неверный выбор[/error]')

def phone_settings_menu():
    while True:
        cls()
        config = load_config(USERNAME)
        instant_output = config.get('instant_output', 'false') == 'true'
        use_ai = config.get('use_ai', 'true') == 'true'
        
        status_text = '[success]ВКЛ[/success]' if instant_output else '[error]ВЫКЛ[/error]'
        ai_status = '[success]ВКЛ[/success]' if use_ai else '[error]ВЫКЛ[/error]'
        
        console.print('[bold secondary]Настройки поиска по номеру[/bold secondary]\n')
        console.print(f'[primary][1][/primary] Моментальный вывод информации: {status_text}')
        console.print(f'[primary][2][/primary] ИИ-анализ (Досье): {ai_status}')
        console.print('[primary][0][/primary] Назад\n')
        
        choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()

        if choice == '1':
            new_value = 'false' if instant_output else 'true'
            save_config(USERNAME, 'instant_output', new_value)
        elif choice == '2':
            new_value = 'false' if use_ai else 'true'
            save_config(USERNAME, 'use_ai', new_value)
        elif choice == '0':
            break


GREETINGS = {
    '1': f'Приветствуем, {USERNAME}!',
    '2': f'Добро пожаловать, {USERNAME}.',
    '3': f'С возвращением, {USERNAME}.',
}

def greeting_settings_menu():
    config = load_config(USERNAME)
    current = config.get('greeting', '1')
    current_text = GREETINGS.get(current, GREETINGS['1'])

    console.print('[bold secondary]Настройка приветствия[/bold secondary]\n')
    console.print(f'[dim]Текущее: {current_text}[/dim]\n')
    console.print(f'[primary][1][/primary] Приветствуем, {USERNAME}!')
    console.print(f'[primary][2][/primary] Добро пожаловать, {USERNAME}.')
    console.print(f'[primary][3][/primary] С возвращением, {USERNAME}.')
    console.print('[primary][0][/primary] Отмена\n')

    choice = v2i('Выберите вариант', f'{USERNAME}@{UUID}').strip()

    if choice in GREETINGS:
        save_config(USERNAME, 'greeting', choice)
        console.print(f'\n[success]✓ Установлено: {GREETINGS[choice]}[/success]')
    elif choice == '0':
        return
    else:
        console.print('\n[error]Неверный выбор[/error]')


def connections_settings_menu():
    console.print('[bold secondary]Настройки: Связи[/bold secondary]\n')
    console.print('[warning]⚠ Функция "Связи" временно недоступна.[/warning]')
    console.print('[dim]Эта функция автоматически строит цепочку:[/dim]')
    console.print('[dim]Телефон → ФИО → ВКонтакте → Email → ...[/dim]')
    console.print('[dim]Включение и изменение параметров в данный момент невозможно.[/dim]\n')
    input('Нажмите Enter для возврата...')

def user_info_settings():
    while True:
        cls()
        config = load_config(USERNAME)
        show_info = config.get('show_user_info', 'false') == 'true'
        pos = config.get('user_info_pos', '1')
        show_sep = config.get('show_banner_separator', 'true') == 'true'
        
        status_text = '[success]ВКЛ[/success]' if show_info else '[error]ВЫКЛ[/error]'
        pos_text = 'Справа от баннера' if pos == '1' else 'Под баннером'
        sep_status = '[success]ВКЛ[/success]' if show_sep else '[error]ВЫКЛ[/error]'
        
        console.print('[bold secondary]Настройка данных пользователя на баннере[/bold secondary]\n')
        console.print(f'[primary][1][/primary] Отображение данных: {status_text}')
        console.print(f'[primary][2][/primary] Расположение: [secondary]{pos_text}[/secondary]')
        console.print(f'[primary][3][/primary] Разделитель (|): {sep_status}')
        console.print('[primary][0][/primary] Назад\n')
        
        choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()

        if choice == '1':
            new_val = 'false' if show_info else 'true'
            save_config(USERNAME, 'show_user_info', new_val)
            console.print(f'\n[success]Настройка отображения обновлена![/success]')
        elif choice == '2':
            new_pos = '2' if pos == '1' else '1'
            save_config(USERNAME, 'user_info_pos', new_pos)
            console.print(f'\n[success]Расположение изменено на: {"Под баннером" if new_pos == "2" else "Справа"}[/success]')
        elif choice == '3':
            new_val = 'false' if show_sep else 'true'
            save_config(USERNAME, 'show_banner_separator', new_val)
            console.print(f'\n[success]Отображение разделителя изменено![/success]')
        elif choice == '0':
            break


def tg_search_settings_menu():
    while True:
        cls()
        config = load_config(USERNAME)
        mode = config.get('tg_search_mode', 'api')

        mode_labels = {
            'api':    '[success]API[/success] [dim](Funstat)[/dim]',
            'parser': '[success]Парсер[/success] [dim](бот-парсер)[/dim]',
            'both':   '[success]API + Парсер[/success]',
        }
        current_label = mode_labels.get(mode, mode)

        console.print('[bold secondary]Настройка поиска по Telegram[/bold secondary]\n')
        console.print(f'[dim]Текущий режим: {current_label}[/dim]\n')
        console.print('[primary][1][/primary] API [dim](только API)[/dim]')
        console.print('[primary][2][/primary] Парсер [dim](только бот-парсер, нужен Telegram аккаунт)[/dim]')
        console.print('[primary][3][/primary] API + Парсер [dim](оба сразу)[/dim]')
        console.print('[primary][0][/primary] Назад\n')

        choice = v2i('Выберите режим', f'{USERNAME}@{UUID}').strip()

        mode_map = {'1': 'api', '2': 'parser', '3': 'both'}
        if choice in mode_map:
            new_mode = mode_map[choice]
            save_config(USERNAME, 'tg_search_mode', new_mode)
            console.print(f'\n[success]✓ Режим установлен: {mode_labels[new_mode]}[/success]')
        elif choice == '0':
            break
        else:
            console.print('\n[error]Неверный выбор[/error]')


def reset_config():
    console.print('\n[warning]Вы уверены, что хотите сбросить все настройки?[/warning]')
    console.print('[dim]Это действие нельзя отменить![/dim]\n')
    console.print('[primary][1][/primary] Да, сбросить')
    console.print('[primary][0][/primary] Отмена\n')
    
    choice = v2i('Подтвердите действие', f'{USERNAME}@{UUID}').strip()
    
    if choice == '1':
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'modules', 'banner', 'configs', f'{USERNAME}.cfg')
            if os.path.exists(config_path):
                os.remove(config_path)
                console.print('\n[success]✓ Конфигурация успешно сброшена![/success]')
                console.print('[dim]Перезапустите софт для применения изменений.[/dim]')
            else:
                console.print('\n[error]Файл конфигурации не найден[/error]')
        except Exception:
            console.print('\n[error]Ошибка при сбросе конфига[/error]')
    elif choice == '0':
        console.print('\n[dim]Действие отменено[/dim]')
    else:
        console.print('\n[error]Неверный выбор[/error]')
    

def settings_menu():
    while True:
        cls()
        cfg = load_config(USERNAME)
        conn_enabled = cfg.get('connections_enabled', 'false') == 'true'
        conn_status  = '[success]ВКЛ[/success]' if conn_enabled else '[error]ВЫКЛ[/error]'
        tg_mode      = cfg.get('tg_search_mode', 'api')
        tg_mode_short = {'api': 'API', 'parser': 'Парсер', 'both': 'API+Парсер'}.get(tg_mode, tg_mode)

        console.print('[bold secondary]Настройки[/bold secondary]\n')
        console.print('[primary][1][/primary] Настройка баннера (скобки)')
        console.print('[primary][2][/primary] Настройка темы (цвета)')
        console.print('[primary][3][/primary] Настройка расположения меню')
        console.print('[primary][4][/primary] Настройки поиска по номеру')
        console.print('[primary][5][/primary] Настройка стиля баннера')
        console.print('[primary][6][/primary] Настройка стиля ввода')
        console.print('[primary][7][/primary] Данные пользователя на баннере')
        console.print(f'[primary][8][/primary] Связи (цепочка OSINT): {conn_status}')
        console.print(f'[primary][9][/primary] Поиск по Telegram: [secondary]{tg_mode_short}[/secondary]')
        console.print('[primary][10][/primary] Приветствие при входе')
        console.print('[primary][11][/primary] Скрытие данных')
        console.print('[primary][12][/primary] Сбросить конфигурацию')
        console.print('[primary][0][/primary] Назад\n')

        used = get_search_count()
        left = max(0, DAILY_SEARCH_LIMIT - used)
        console.print(f'[dim]Дневной лимит поисков: {used}/{DAILY_SEARCH_LIMIT} (осталось {left})[/dim]')

        choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()

        if choice == '1':
            banner_brackets_settings()
        elif choice == '2':
            theme_settings_menu()
        elif choice == '3':
            banner_layout_settings()
        elif choice == '4':
            phone_settings_menu()
        elif choice == '5':
            banner_style_settings()
        elif choice == '6':
            input_settings_menu()
        elif choice == '7':
            user_info_settings()
        elif choice == '8':
            connections_settings_menu()
        elif choice == '9':
            tg_search_settings_menu()
        elif choice == '10':
            greeting_settings_menu()
        elif choice == '11':
            data_hiding_menu()
        elif choice == '12':
            reset_config()
        elif choice == '0':
            break
        else:
            console.print('\n[error]Неверный выбор[/error]')