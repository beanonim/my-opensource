HEADER_ASCII = r'''
    █████╗  ██████╗ ███████╗███╗   ██╗████████╗                   
   ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝                   
   ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║                      
   ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║                      
   ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║                      
   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝                           
'''

INFO_SIDE_TEMPLATE = [
    "[banner]\\[&][/banner] Пользователь: [primary]{username}[/primary]",
    "[banner]\\[#][/banner] UUID: [primary]{uuid}[/primary]",
    "[banner]\\[*][/banner] Подписка: [primary]{subscription}[/primary]",
    "[banner]\\[/][/banner] Баз данных: [primary]{data}[/primary]",
    "[banner]\\[&][/banner] Разработчик: [primary]t.me/hatedfame[/primary]",
    "[banner]\\[@][/banner] Версия: [primary]{version}[/primary]"
]

STATIC_PAGES = 3

PAGE_OPTIONS = {
    1: [
        ('1', 'Поиск по номеру'), ('5', 'Поиск по снилсу'),
        ('2', 'Поиск по нику'), ('6', 'Поиск по телеграму'),
        ('3', 'Поиск по вк'), ('7', 'Чат с нейросетью'),
        ('4', 'Поиск по ip'), ('8', 'Выход')
    ],
    2: [
        ('9', 'Поиск по vin'), ('13', 'Билдер стиллера'),
        ('10', 'Поиск компаний'), ('14', 'Поиск по почте'),
        ('11', 'Поиск юзеров в тг'), ('15', 'Поиск по ФИО'),
        ('12', 'Дискорд инстр-ы'), ('16', 'Генератор БД')
    ],
    3: [
        ('17', 'SMS Бомбер'), ('21', 'DoS'),
        ('18', 'Прокси скрейпер'), ('22', 'Временная почта'),
        ('19', 'Cloudflare резольвер'), ('23', 'Поиск по IMEI'),
        ('20', 'Поиск эндпоинтов'), ('24', 'Getcontact')
    ],
    4: [
        ('25', 'Whois + DNS домена'), ('26', 'Email MX проверка'),
        ('28', 'GitHub OSINT'), ('', '')
    ]
}

def get_navigation_label(page, total_pages=None):
    if total_pages is None:
        total_pages = STATIC_PAGES
    if page >= total_pages:
        return 'Первая страница'
    nxt = page + 1
    if nxt <= STATIC_PAGES:
        ordinal = {2: 'Вторая', 3: 'Третья'}.get(nxt, 'Следующая')
        return f'{ordinal} страница'
    return f'Страница функций {nxt - STATIC_PAGES}'
