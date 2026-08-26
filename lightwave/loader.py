import sys
import random
import time

sys.dont_write_bytecode = True
from modules.config import *
from modules.console import *
from modules.input import *
from modules.banner.engine import *
from functions.misc.settings import *
from functions.misc.coffee import *
from functions.misc.connections import run_connections
from functions.page_1.ai_chat import *
from functions.page_1.ip import *
from functions.page_1.nickname import *
from functions.page_1.phone import *
from functions.page_1.snils import *
from functions.page_1.tg_search import *
from functions.page_1.vk import *
from functions.page_2.builder import *
from functions.page_2.discord import *
from functions.page_2.email import *
from functions.page_2.fake_db import *
from functions.page_2.fio import *
from functions.page_2.image import *
from functions.page_2.of_data import *
from functions.page_2.telegram import *
from functions.page_2.vin import *
from functions.page_2.imei import imei_search
from functions.page_3.temp_mail import *
from functions.page_3.temp_phone import *
from functions.page_3.bomber.engine import *
from functions.page_3.proxy import *
from functions.page_3.cf_resolver import *
from functions.page_3.endpoint_finder import *
from functions.page_3.dos import *
from functions.page_3.temp_phone import *
from functions.page_3.getcontact import *
from functions.page_4.whois_lookup import whois_lookup
from functions.page_4.github_search import github_search
from functions.page_4.email_mx import email_mx_check
from modules.modules import modules_menu
from modules.modules.runner import run_module
from modules.modules.registry import get_function_map, get_total_pages
from modules.logger_tg import log_search

def cycle(show_coffee):
    current_page = 1
    
    while True:
        cls()
        config = load_config(USERNAME)
        layout = config.get('banner_layout', 'down')
        displayed_banner = create_banner(current_page, show_coffee, layout)
        console.print(displayed_banner)

        choice = v2i('Выберите действие', f'{USERNAME}@{UUID}').strip()

        user_functions = get_function_map()

        if choice == '88':
            if show_coffee:
                buy_me_a_coffee()
            else:
                console.print('\n[error]Эта опция сейчас недоступна![/error]')

        elif choice == '99':
            current_page = (current_page % get_total_pages()) + 1
            continue

        elif choice == '1':
            phone = v2i('Введите номер', f'{USERNAME}@{UUID}')
            log_search('phone_search', phone)
            phone_search(phone)

        elif choice == '2':
            nickname = v2i('Введите имя пользователя', f'{USERNAME}@{UUID}')
            nickname_search(nickname)

        elif choice == '3':
            vk = v2i('Введите ID ВКонтакте', f'{USERNAME}@{UUID}')
            log_search('vk_search', vk)
            vk_search(vk)

        elif choice == '4':
            ip = v2i('Введите IP-адрес для поиска', f'{USERNAME}@{UUID}')
            log_search('ip_search', ip)
            ip_search(ip)

        elif choice == '5':
            snils = v2i('Введите номер СНИЛС (только цифры)', f'{USERNAME}@{UUID}')
            snils_search(snils)

        elif choice == '6':
            query = v2i('Введите ID или username пользователя Telegram', f'{USERNAME}@{UUID}')
            log_search('tgsearch', query)
            tgsearch(query)

        elif choice == '7':
            console.print('[dim]Ctrl+C для выхода из чата[/dim]')
            try:
                select_ai_model()
                while True:
                    prompt = v2i('Вопрос нейросети', f'{USERNAME}@{UUID}')
                    if not prompt.strip():
                        continue
                    ai_chat(prompt)
            except KeyboardInterrupt:
                console.print('\n[dim]Выход из чата[/dim]')
                reset_ai_model()

        elif choice == '8':
            console.print('\n[success]До свидания![/success]')
            break

        elif choice == '9':
            vin = v2i('Введите VIN-номер', f'{USERNAME}@{UUID}')
            vin_search(vin)

        elif choice == '10':
            of_data_search()

        elif choice == '11':
            telegram_username_checker()

        elif choice == '12':
            discord_tool()

        elif choice == '13':
            stealer_builder()

        elif choice == '14':
            email = v2i('Введите email', f'{USERNAME}@{UUID}')
            log_search('email_search', email)
            email_search(email)

        elif choice == '15':
            fullname = v2i('Введите ФИО (пример: Козлов Дмитрий Сергеевич)', f'{USERNAME}@{UUID}')
            log_search('fio_search', fullname)
            fio_search(fullname)

        elif choice == '16':
            fake_db_generator()

        elif choice == '23':
            imei = v2i('Введите IMEI-номер (15 цифр)', f'{USERNAME}@{UUID}').strip()
            if imei:
                log_search('imei_search', imei)
                imei_search(imei)

        elif choice == '17':
            sms_bomber()

        elif choice == '18':
            proxy_scraper()

        elif choice == '19':
            domain = v2i('Введите домен (например, example.com)', f'{USERNAME}@{UUID}').strip()
            if domain:
                cf_resolver(domain)

        elif choice == '20':
            url = v2i('Введите URL (например, example.com)', f'{USERNAME}@{UUID}').strip()
            if url:
                endpoint_finder(url)

        elif choice == '21':
            dos()

        elif choice == '22':
            temp_mail_tool()


        elif choice == '24':
            phone = v2i('Введите номер', f'{USERNAME}@{UUID}')
            log_search('getcontact_search', phone)
            getcontact_search(phone)

        elif choice == '25':
            domain = v2i('Введите домен (например, example.com)', f'{USERNAME}@{UUID}').strip()
            if domain:
                whois_lookup(domain)

        elif choice == '26':
            email = v2i('Введите email', f'{USERNAME}@{UUID}').strip()
            if email:
                email_mx_check(email)

        elif choice == '28':
            gh_user = v2i('Введите username GitHub', f'{USERNAME}@{UUID}').strip()
            if gh_user:
                github_search(gh_user)

        elif choice == '77':
            settings_menu()

        elif choice == '55':
            modules_menu()

        elif choice == '66':
            console.print('\n[bold secondary]Полезные ссылки:[/bold secondary]')
            console.print('Канал lightwave: [primary]t.me/l1ghtwave[/primary]')
            console.print('Разработчик lightwave: [primary]t.me/hatedfame[/primary]')

        elif choice in user_functions:
            fname, meta = user_functions[choice]
            run_module(fname)

        else:
            console.print('\n[error]Неверный выбор[/error]')

        console.print('\n[dim]Нажмите Enter для продолжения...[/dim]')
        input()

def start():
    config = load_config(USERNAME)
    first_run = config.get('first_run', 'True') != 'False'

    show_coffee = random.random() < 0.5
    greeting_key = config.get('greeting', '1')
    from functions.misc.settings import GREETINGS
    greeting_text = GREETINGS.get(greeting_key, GREETINGS['1'])
    console.print(f'\n[success]{greeting_text}[/success]\n')
    time.sleep(0.8)

    if first_run:
        console.print('[warning]Похоже, ты запустил софт первый раз[/warning]')
        choice = v2i('Хочешь открыть настройки? (y/n)', f'{USERNAME}@{UUID}').strip().lower()
        if choice == 'y':
            settings_menu()
        config['first_run'] = False
        save_config(USERNAME, 'first_run', False)

    cycle(show_coffee)