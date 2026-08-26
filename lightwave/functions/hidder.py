from modules.console import console
from functions.misc.data_hiding import is_protected, get_protection_info

_LABELS = {
    'phone': 'номер', 'email': 'email', 'username': 'никнейм',
    'vk_id': 'ID ВКонтакте', 'ip': 'IP-адрес', 'snils': 'СНИЛС',
    'telegram': 'Telegram', 'vin': 'VIN', 'fio': 'ФИО',
    'imei': 'IMEI', 'domain': 'домен',
}

def block(value, category):
    if not value or not value.strip():
        return False
    if not is_protected(value, category):
        return False
    info = get_protection_info(value, category)
    label = _LABELS.get(category, category)
    if info and info.get('show_nick'):
        console.print(f'\n[warning]Поиск по данному {label} защищен пользователем {info["protector"]}![/warning]')
    else:
        console.print(f'\n[warning]Поиск по данному {label} защищен![/warning]')
    console.print('[dim]Нажмите Enter для продолжения...[/dim]')
    input()
    return True
