import os
import re
import ast
import requests
from modules.console import console
from modules.input import v2i
from modules.config import USERNAME, UUID
from modules.modules.config import MODULES_DIR
from modules.modules.meta import get_meta
from modules.modules.display import print_table
from modules.modules.runner import list_modules, run_module
from modules.modules.docs import DOCS


_DANGEROUS_CALLS = {
    'exec', 'eval', 'compile', 'open', 'getattr', 'setattr', 'delattr',
    '__import__', 'breakpoint', 'exit', 'quit', 'globals', 'locals',
    'vars', 'dir', 'type', 'classmethod', 'staticmethod', 'super',
    'memoryview', 'bytearray', 'buffer', 'system', 'popen', 'spawn',
    'fork', 'kill', 'remove', 'rmdir', 'unlink', 'rename',
    'chown', 'chmod', 'chroot', 'symlink', 'link', 'mount', 'umount',
}
_DANGEROUS_NAMES = {
    '__import__', '__builtins__', '__globals__', '__locals__', '__code__',
    '__class__', '__bases__', '__subclasses__', '__mro__',
    '__import__', '__loader__', '__spec__', '__name__',
    '__qualname__', '__closure__', '__defaults__', '__annotations__',
    '__dict__', '__slots__', '__weakref__', '__module__',
    '__init_subclass__', '__set_name__', '__format__',
    '__reduce__', '__reduce_ex__', '__getstate__', '__setstate__',
    '__copy__', '__deepcopy__', '__sizeof__', '__repr__',
    '__str__', '__bytes__', '__hash__', '__bool__',
}
_DANGEROUS_MODULES = {
    'os', 'sys', 'subprocess', 'socket', 'shutil', 'pathlib',
    'ctypes', 'importlib', 'code', 'codeop', 'compileall',
    'py_compile', 'zipimport', 'pkgutil', 'runpy',
}


def _check_ast_node(node, errors):
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name.split('.')[0]
            if mod in _DANGEROUS_MODULES:
                errors.append(f'Импорт запрещённого модуля: {alias.name}')
    elif isinstance(node, ast.ImportFrom):
        if node.module:
            mod = node.module.split('.')[0]
            if mod in _DANGEROUS_MODULES:
                errors.append(f'Импорт из запрещённого модуля: {node.module}')
        for alias in node.names:
            if alias.name in _DANGEROUS_NAMES:
                errors.append(f'Импорт запрещённого имени: {alias.name}')
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name):
            if node.func.id in _DANGEROUS_CALLS:
                errors.append(f'Вызов запрещённой функции: {node.func.id}()')
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in _DANGEROUS_CALLS:
                errors.append(f'Вызов запрещённого метода: .{node.func.attr}()')
    elif isinstance(node, ast.Attribute):
        if node.attr in _DANGEROUS_NAMES:
            errors.append(f'Доступ к запрещённому атрибуту: .{node.attr}')
        if isinstance(node.value, ast.Name):
            if node.value.id in _DANGEROUS_NAMES:
                errors.append(f'Доступ к запрещённому атрибуту: {node.value.id}.{node.attr}')
    elif isinstance(node, ast.Subscript):
        if isinstance(node.value, ast.Attribute):
            if node.value.attr in ('__class__', '__bases__', '__mro__', '__subclasses__'):
                errors.append(f'Индексация запрещённого атрибута: .{node.value.attr}[...]')
        if isinstance(node.value, ast.Name):
            if node.value.id in _DANGEROUS_NAMES:
                errors.append(f'Индексация запрещённого имени: {node.value.id}[...]')
    elif isinstance(node, ast.Name):
        if node.id in _DANGEROUS_NAMES:
            errors.append(f'Использование запрещённого имени: {node.id}')
    for child in ast.iter_child_nodes(node):
        _check_ast_node(child, errors)


def _validate(content):
    if len(content) > 50_000:
        return 'Файл слишком большой (максимум 50 КБ)'
    meta = get_meta(content)
    if meta['name'] == '?':
        return 'Не является валидным .lw модулем (нет module_name)'
    code_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if re.match(r'^module_(name|developer|version|description|type)\s*=', stripped):
            continue
        if stripped:
            code_lines.append(line)
    code = '\n'.join(code_lines)
    if not code.strip():
        return None
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 'Синтаксическая ошибка в коде модуля'
    errors = []
    for node in ast.iter_child_nodes(tree):
        _check_ast_node(node, errors)
    if errors:
        return f'Запрещённая инструкция: {errors[0]}'
    return None


def _save(content, meta):
    safe_name = re.sub(r'[^\w\-]', '_', meta['name'].lower()) + '.lw'
    os.makedirs(MODULES_DIR, exist_ok=True)
    dest = os.path.join(MODULES_DIR, safe_name)
    if os.path.exists(dest):
        console.print(f'[warning]Модуль уже установлен: {safe_name}[/warning]')
        if v2i('Перезаписать? (y/n)', f'{USERNAME}@{UUID}').strip().lower() != 'y':
            return None
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)
    return safe_name


def browse_marketplace():
    console.print()
    mods = list_modules()
    print_table(mods)
    if not mods:
        return
    console.print('[primary][0][/primary] Назад\n')
    sel = v2i('Выберите модуль', f'{USERNAME}@{UUID}').strip()
    if sel == '0':
        return
    try:
        idx = int(sel) - 1
        if 0 <= idx < len(mods):
            run_module(mods[idx])
            console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
            input()
        else:
            console.print('[error]Неверный выбор[/error]')
    except ValueError:
        console.print('[error]Неверный выбор[/error]')


def install_by_url():
    console.print('\n[bold secondary]Установка по ссылке[/bold secondary]\n')
    console.print('[dim]1. Зайдите на[/dim] [primary]https://catbox.moe[/primary]')
    console.print('[dim]2. Нажмите «Select or drop files», выберите .lw файл, нажмите «Upload»[/dim]')
    console.print('[dim]3. Скопируйте ссылку и вставьте ниже[/dim]\n')

    url = v2i('Ссылка на .lw файл', f'{USERNAME}@{UUID}').strip()
    if not url:
        console.print('[error]Ссылка не введена[/error]')
        return
    if not (url.startswith('http://') or url.startswith('https://')):
        console.print('[error]Ссылка должна начинаться с http(s)://[/error]')
        return
    if not url.endswith('.lw'):
        console.print('[error]Ссылка должна вести на .lw файл[/error]')
        return

    console.print('\n[dim]Загружаю...[/dim]')
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/plain, */*',
        }
        resp = requests.get(url, timeout=15, headers=headers)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        console.print('[error]Превышено время ожидания[/error]')
        return
    except requests.exceptions.RequestException:
        console.print('[error]Ошибка загрузки[/error]')
        return

    content = resp.text
    err = _validate(content)
    if err:
        console.print(f'[error]{err}[/error]')
        return

    meta = get_meta(content)
    result = _save(content, meta)
    if result:
        type_labels = {'script': 'скрипт', 'visual': 'визуальный', 'function': 'функция'}
        type_label = type_labels.get(meta.get('type', 'script'), 'скрипт')
        console.print(f'\n[success]Модуль "{meta["name"]}" установлен![/success]')
        console.print(f'[dim]{meta["version"]} by {meta["developer"]} • тип: {type_label}[/dim]')
        if meta.get('type') == 'visual':
            console.print('[dim]Запустите модуль в «Визуальные модули», чтобы применить оформление.[/dim]')
        elif meta.get('type') == 'function':
            console.print('[dim]Модуль появится в главном меню как функция.[/dim]')


def _module_template(mod_type):
    common = (
        "module_name = 'Мой модуль'\n"
        "module_developer = 't.me/username'\n"
        "module_version = 'v1.0'\n"
        "module_description = 'Короткое описание'\n"
    )
    if mod_type == 'visual':
        return (
            common + "module_type = 'visual'\n\n"
            "set_theme('hacker')\n"
            "set_color(primary, '#00ffaa')\n"
            "set_banner_style('square')\n"
            "print(success, 'Тема применена!')\n"
        )
    if mod_type == 'function':
        return (
            common + "module_type = 'function'\n\n"
            "print(info, 'Привет! Это функция из главного меню.')\n"
            "name = ask('Как тебя зовут? ')\n"
            "print(success, format('Привет, {name}!', name))\n"
        )
    return (
        common +
        "name = ask('Как тебя зовут? ')\n"
        "print('Привет, ' + name + '!')\n"
    )


def create_module_guide():
    console.print(DOCS)
    console.print()
    console.print('[bold secondary]Создание модуля[/bold secondary]\n')
    console.print('[primary][1][/primary] Скрипт (запускается из «Установленные модули»)')
    console.print('[primary][2][/primary] Визуальный (темы, цвета, баннер)')
    console.print('[primary][3][/primary] Функция (появляется в главном меню)')
    console.print('[primary][0][/primary] Назад')
    t = v2i('Выберите тип модуля', f'{USERNAME}@{UUID}').strip()
    type_map = {'1': 'script', '2': 'visual', '3': 'function'}
    if t not in type_map:
        return
    mod_type = type_map[t]
    template = _module_template(mod_type)
    console.print(f'\n[bold secondary]Шаблон {mod_type}:[/bold secondary]\n')
    console.print(template)
    if v2i('Сохранить шаблон в модули? (y/n)', f'{USERNAME}@{UUID}').strip().lower() != 'y':
        console.print('[dim]Шаблон скопирован выше — вставьте его в файл и поделитесь через «Установить по ссылке»[/dim]')
        return
    content = template.replace("module_name = 'Мой модуль'", "module_name = 'Мой новый модуль'")
    meta = get_meta(content)
    result = _save(content, meta)
    if result:
        if mod_type == 'function':
            console.print('[success]Модуль создан![/success]')
            console.print('[dim]Он появится в главном меню (страницы функций).[/dim]')
        elif mod_type == 'visual':
            console.print('[success]Модуль создан![/success]')
            console.print('[dim]Запустите его через «Визуальные модули».[/dim]')
        else:
            console.print('[success]Модуль создан![/success]')
            console.print('[dim]Запустите его через «Установленные модули».[/dim]')