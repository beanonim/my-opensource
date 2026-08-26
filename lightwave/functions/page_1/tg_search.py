from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from funstat_api import AsyncFunstatClient
from funstat_api.exceptions import ApiError, FunstatError
from modules.api import FUNSTAT_TOKEN, API_CONFIG
from modules.filter import clean_record
from functions.page_1.tg_parser import tg_parser_search
from functions.page_1.phone import _normalize_deepscan
from functions.hidder import block
from functions.misc.utils import jitler_fetch, whitesearch_fetch, nyx_fetch, sanitize_error, whitesearch_fetch, nyx_fetch, whitesearch_records


def tgsearch(query):
    if block(query, 'telegram'): return
    try:
        if not query:
            query = v2i('Введите запрос (ID, @username, ссылка, текст)', f'{USERNAME}@{UUID}').strip()
            if block(query, 'telegram'): return
            
        if not query:
            console.print('[error]Запрос не указан[/error]')
            return

        # режим поиска: api / parser / оба
        tg_mode = load_config(USERNAME).get('tg_search_mode', 'api')

        if tg_mode == 'parser':
            tg_parser_search(query)
            return

        if tg_mode == 'both':
            console.print('\n[secondary]Режим: API + Парсер[/secondary]')

        async def main_async():
            console.print('\n[secondary]Выберите направление поиска:[/secondary]')
            console.print('[1] Полная статистика пользователя (ID/@username/ссылка)')
            console.print('[2] Минимальная статистика пользователя (ID/@username/ссылка)')
            console.print('[3] Участники группы/канала (ID/@username/ссылка)')
            console.print('[4] Информация о группе/канале (ID/@username/ссылка)')
            console.print('[5] История имен пользователя (ID/@username/ссылка)')
            console.print('[6] Общие группы пользователя (ID/@username/ссылка)')
            console.print('[7] Использование юзернейма (Только юзернейм)')
            console.print('[8] Поиск сообщений пользователя (ID/@username/ссылка)')
            console.print('[9] Поиск по тексту сообщений (Текст)')
            console.print('[10] Поиск использования имени (Имя)')

            choice = v2i('Введите номер варианта', f'{USERNAME}@{UUID}').strip()

            console.print(f'\n[secondary]Подключение к API...[/secondary]')
            
            async with AsyncFunstatClient(FUNSTAT_TOKEN) as fs:
                try:
                    if choice == '1' or choice == '2':
                        if choice == '1':
                            res = await fs.stats(query)
                        else:
                            res = await fs.stats_min(query)
                            
                        labels = {
                            'id': 'ID', 'first_name': 'Имя', 'last_name': 'Фамилия', 'username': 'Юзернейм',
                            'is_bot': 'Бот', 'is_active': 'Активен', 'first_msg_date': 'Первое сообщение',
                            'last_msg_date': 'Последнее сообщение', 'total_msg_count': 'Всего сообщений',
                            'msg_in_groups_count': 'Сообщений в группах', 'adm_in_groups': 'Админ в группах',
                            'usernames_count': 'Смена юзернеймов', 'names_count': 'Смена имен',
                            'total_groups': 'Всего групп', 'is_cyrillic_primary': 'Пишет на кириллице',
                            'lang_code': 'Язык', 'unique_percent': 'Уникальность текста (%)',
                            'circle_count': 'Кружков', 'voice_count': 'Голосовых',
                            'reply_percent': 'Ответов (%)', 'media_percent': 'Медиа (%)',
                            'link_percent': 'Ссылок (%)', 'favorite_chat': 'Любимый чат',
                            'media_usage': 'Использование медиа', 'stars_val': 'Звезд',
                            'personal_channel_id': 'ID личного канала', 'gift_count': 'Подарков',
                            'stars_level': 'Уровень звезд', 'birth_day': 'День рождения',
                            'birth_month': 'Месяц рождения', 'birth_year': 'Год рождения',
                            'about': 'О себе', 'bio': 'О себе'
                        }
                        
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        for k, v in res.data.__dict__.items():
                            if v is not None and v != '':
                                label = labels.get(k, k.replace('_', ' ').capitalize())
                                if k == 'favorite_chat' and hasattr(v, 'title'):
                                    v = f"{v.title} ({getattr(v, 'id', '')})"
                                elif isinstance(v, bool):
                                    v = 'Да' if v else 'Нет'
                                console.print(f"[primary]{label}:[/primary] [white]{v}[/white]")

                    elif choice == '3':
                        res = await fs.get_group_members(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        total_count = getattr(res.data, 'total', len(data_arr)) if not isinstance(res.data, list) else len(data_arr)
                        console.print(f"[primary]Найдено участников:[/primary] [white]{total_count}[/white]")
                        for m in data_arr[:20]:
                            username = getattr(m, 'username', None)
                            uname = f"@{username}" if username else "Нет юзернейма"
                            console.print(f"[white]{getattr(m, 'id', '')}[/white] | [secondary]{getattr(m, 'first_name', '')}[/secondary] | {uname}")
                        if total_count > 20: console.print(f"[secondary]... и еще {total_count - 20}[/secondary]")

                    elif choice == '4':
                        res = await fs.get_group_info(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        console.print(f"[primary]Название:[/primary] [white]{getattr(res.data, 'title', '')}[/white]")
                        username = getattr(res.data, 'username', None)
                        if username: console.print(f"[primary]Юзернейм:[/primary] [white]@{username}[/white]")
                        console.print(f"[primary]ID:[/primary] [white]{getattr(res.data, 'id', '')}[/white]")
                        description = getattr(res.data, 'description', None)
                        if description: console.print(f"[primary]Описание:[/primary] [white]{description}[/white]")
                        console.print(f"[primary]Тип:[/primary] [white]{getattr(res.data, 'type', '')}[/white]")

                    elif choice == '5':
                        res = await fs.get_names(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        total_count = getattr(res.data, 'total', len(data_arr)) if not isinstance(res.data, list) else len(data_arr)
                        console.print(f"[primary]Найдено имен:[/primary] [white]{total_count}[/white]")
                        for n in data_arr:
                            console.print(f"[white]{getattr(n, 'name', '')}[/white] [secondary](Первое появление: {getattr(n, 'first_seen', '')})[/secondary]")

                    elif choice == '6':
                        res = await fs.common_groups(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        total_count = getattr(res.data, 'total', len(data_arr)) if not isinstance(res.data, list) else len(data_arr)
                        console.print(f"[primary]Найдено общих групп:[/primary] [white]{total_count}[/white]")
                        for g in data_arr[:20]:
                            console.print(f"[white]{getattr(g, 'title', '')}[/white] [secondary]({getattr(g, 'id', '')})[/secondary]")

                    elif choice == '7':
                        query_clean = query.replace('@', '').replace('https://t.me/', '')
                        res = await fs.username_usage(query_clean)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        past_users = getattr(res.data, 'usage_by_users_in_the_past', []) or []
                        actual_users = getattr(res.data, 'actual_users', []) or []
                        data_arr = past_users + actual_users
                        console.print(f"[primary]Пользователей с этим юзернеймом:[/primary] [white]{len(data_arr)}[/white]")
                        for u in data_arr:
                            console.print(f"[white]{getattr(u, 'id', '')}[/white] | [secondary]{getattr(u, 'name', '')}[/secondary] (с {getattr(u, 'first_seen', '')} по {getattr(u, 'last_seen', '')})")

                    elif choice == '8':
                        res = await fs.get_messages(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        limit = min(len(data_arr), 10)
                        console.print(f"[primary]Последние сообщения (показано {limit}):[/primary]")
                        for msg in data_arr[:10]:
                            date_str = getattr(msg, 'date', 'Неизвестно')
                            console.print(f"[secondary][{date_str}] Группа {getattr(msg, 'chat_id', '')}:[/secondary] [white]{getattr(msg, 'text', '')}[/white]")

                    elif choice == '9':
                        res = await fs.search_text(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        total_count = getattr(res.data, 'total', len(data_arr)) if not isinstance(res.data, list) else len(data_arr)
                        console.print(f"[primary]Найдено сообщений (всего):[/primary] [white]{total_count}[/white]")
                        for msg in data_arr[:10]:
                            date_str = getattr(msg, 'date', 'Неизвестно')
                            console.print(f"[secondary][{date_str}] Юзер {getattr(msg, 'user_id', '')} в группе {getattr(msg, 'chat_id', '')}:[/secondary] [white]{getattr(msg, 'text', '')}[/white]")

                    elif choice == '10':
                        res = await fs.name_usage(query)
                        console.print('\n[success]━━━ РЕЗУЛЬТАТ ━━━[/success]')
                        data_arr = res.data if isinstance(res.data, list) else getattr(res.data, 'data', [])
                        total_count = getattr(res.data, 'total', len(data_arr)) if not isinstance(res.data, list) else len(data_arr)
                        console.print(f"[primary]Пользователей с таким именем:[/primary] [white]{total_count}[/white]")
                        for u in data_arr[:20]:
                            username = getattr(u, 'username', None)
                            uname = f"@{username}" if username else "Нет"
                            console.print(f"[white]{getattr(u, 'id', '')}[/white] | [secondary]{getattr(u, 'name', '')}[/secondary] (Юзернейм: {uname})")

                    else:
                        console.print('[error]Неверный номер варианта[/error]')

                except Exception:
                    console.print('[error]Ошибка API[/error]')

        asyncio.run(main_async())

        # Если режим оба тада запускаем парсер тоже
        if tg_mode == 'both':
            console.print('\n[secondary]━━━ Запуск парсера ━━━[/secondary]')
            tg_parser_search(query)

        try:
            ds_cfg = API_CONFIG[38]
            ds_payload = ds_cfg['payload'].copy()
            ds_payload['search'] = query
            ds_resp = requests.post(ds_cfg['url'], json=ds_payload, headers=ds_cfg['headers'], timeout=15)
            if ds_resp.status_code == 200:
                ds_data = ds_resp.json()
                ds_record = _normalize_deepscan(ds_data)
                if ds_record:
                    ds_record = clean_record(ds_record)
                    if ds_record:
                        console.print('\n[success]━━━ API 38 ━━━[/success]')
                        for k, v in ds_record.items():
                            if isinstance(v, list):
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                            else:
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
        except Exception as e:
            console.print(f'[error]API 38 ошибка: {sanitize_error(e)}[/error]')

        try:
            ws_cfg = API_CONFIG[42]
            ws_data, ws_err = whitesearch_fetch(ws_cfg, '/search/telegram', {'id': query})
            if ws_data:
                for rec in whitesearch_records(ws_data):
                    rec = clean_record(rec)
                    if rec:
                        console.print('\n[success]━━━ API 42 ━━━[/success]')
                        for k, v in rec.items():
                            if isinstance(v, list):
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                            else:
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
        except Exception as e:
            console.print(f'[error]API 42 ошибка: {sanitize_error(e)}[/error]')

        try:
            nx_cfg = API_CONFIG[43]
            nx_data, nx_err = nyx_fetch(nx_cfg, query)
            if nx_data:
                text = nx_data.get('text') if isinstance(nx_data, dict) else str(nx_data)
                if text:
                    console.print('\n[success]━━━ API 43 ━━━[/success]')
                    console.print(text)
        except Exception as e:
            console.print(f'[error]API 43 ошибка: {sanitize_error(e)}[/error]')

        try:
            jit_cfg = API_CONFIG[40]
            jit_data, jit_err = jitler_fetch(jit_cfg, query, search_type='sherlock')
            if jit_data:
                console.print('\n[success]━━━ Результат ━━━[/success]')
                items = jit_data if isinstance(jit_data, list) else [jit_data]
                for item in items[:15]:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, list):
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {", ".join(str(x) for x in v)}')
                            else:
                                console.print(f'  [success]•[/success] [secondary]{k}[/secondary]: {v}')
                    else:
                        console.print(f'  [success]•[/success] [secondary]{item}[/secondary]')
        except Exception:
            pass

        console.print(
            '\n[success]Готово[/success]',
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

    except KeyboardInterrupt:
        console.print('\n[warning]Операция прервана пользователем[/warning]')
    except Exception as e:
        console.print(f'\n[error]Критическая ошибка: {sanitize_error(e)}[/error]')