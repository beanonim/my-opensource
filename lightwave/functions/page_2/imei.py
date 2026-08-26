from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.filter import clean_record
from functions.page_1.ai_chat import get_ai_answer
from functions.hidder import block
from functions.misc.utils import print_record


# rbi - страна/регулятор по первым двум цифрам imei
# источник: itu-t e.118 / gsma ts.06
RBI_MAP = {
    '00': 'США (FCC)',       '01': 'США (FCC)',       '02': 'США (FCC)',
    '10': 'Финляндия',       '20': 'Германия',        '30': 'Норвегия',
    '35': 'Великобритания',  '44': 'Австрия',         '45': 'Южная Корея',
    '49': 'Германия',
    '50': 'Китай',           '51': 'Китай',           '52': 'Китай',
    '53': 'Австралия',       '54': 'Австралия',       '55': 'Австралия',
    '60': 'Франция',         '65': 'Бельгия',         '70': 'Нидерланды',
    '74': 'Швеция',          '75': 'Италия',          '76': 'Испания',
    '78': 'Дания',           '80': 'Таиланд',         '86': 'Китай (CMIIT)',
    '87': 'Китай (CMIIT)',   '88': 'Китай (CMIIT)',   '89': 'Китай (CMIIT)',
    '91': 'Индия',           '92': 'Индия',           '93': 'Индия',
    '94': 'Индия',           '95': 'Индия',
    '98': 'Япония',          '99': 'Япония',
}


def _validate_imei(imei: str) -> bool:
    # алхоритм луууунаааа
    if not re.fullmatch(r'\d{15}', imei):
        return False
    total = 0
    for i, d in enumerate(reversed(imei)):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _decode_rbi(imei: str) -> dict:
    tac = imei[:8]
    rbi = imei[:2]
    return {
        'TAC (Type Allocation Code)': tac,
        'SNR (серийный номер)':       imei[8:14],
        'CD (контрольная цифра)':     imei[14],
        'RBI (орган сертификации)':   rbi,
        'Страна сертификации':        RBI_MAP.get(rbi, f'Неизвестен (RBI={rbi})'),
        'Производитель / Модель':     'Требуется платная GSMA TAC-база',
    }


# норм апишки которые реально отвечают

def _query_apple_check(imei: str) -> dict | None:
    try:
        r = requests.get(
            'https://api.apple-check.com/api/check',
            params={'imei': imei, 'token': 'free'},
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and data.get('brand', '').lower() == 'apple':
                result = {}
                for k in ('brand', 'name', 'model', 'country', 'carrier', 'status'):
                    if data.get(k):
                        result[k] = str(data[k])
                return result if result else None
    except Exception:
        pass
    return None


def _query_imeicheck_api(imei: str) -> dict | None:
    try:
        r = requests.post(
            'https://api.imeicheck.net/v1/checks',
            json={'deviceId': imei, 'serviceId': 12},   # serviceId 12 = free basic
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0',
            },
            timeout=12
        )
        if r.status_code in (200, 201):
            data = r.json()
            props = data.get('properties', data.get('result', data))
            if isinstance(props, dict):
                result = {}
                for k, v in props.items():
                    if v is not None and not isinstance(v, (dict, list)) and str(v).strip():
                        result[str(k)] = str(v)
                return result if result else None
    except Exception:
        pass
    return None


def _query_gsmarena(imei: str) -> dict | None:
    try:
        tac = imei[:8]
        r = requests.get(
            f'https://www.gsmarena.com/search.php3?sQuickSearch={tac}',
            headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
                'Accept-Language': 'ru-RU,ru;q=0.9',
                'Referer': 'https://www.gsmarena.com/',
            },
            timeout=12
        )
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, 'html.parser')
        devices = []
        for item in soup.select('.makers ul li')[:5]:
            a = item.find('a')
            if a:
                name = a.get_text(strip=True).replace('\n', ' ')
                href = a.get('href', '')
                if name:
                    devices.append(name)
        if devices:
            return {'Возможные совпадения (GSMArena)': ', '.join(devices)}
    except Exception:
        pass
    return None


def _query_freemobile(tac: str) -> dict | None:
    endpoints = [
        f'https://freemobileapi.com/devices/tac/{tac}',
        f'https://freemobileapi.com/v2/tac/{tac}',
        f'https://freemobileapi.com/api/tac?code={tac}',
    ]
    for url in endpoints:
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0',
                                            'Accept': 'application/json'},
                              timeout=8)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict) and data:
                    result = {}
                    for k, v in data.items():
                        if v and not isinstance(v, (dict, list)):
                            result[str(k)] = str(v)
                    if result:
                        return result
        except Exception:
            continue
    return None


def imei_search(imei: str):
    if block(imei, 'imei'): return
    imei = re.sub(r'\D', '', imei.strip())

    console.print(f'\n[secondary]Поиск по IMEI:[/secondary] {imei}\n')

    if len(imei) != 15:
        console.print(
            f'[error]Неверный формат: нужно 15 цифр, введено {len(imei)}[/error]'
        )
        return

    # алгоритм луна
    if _validate_imei(imei):
        console.print('[success]✔ IMEI прошёл проверку алгоритма Луна[/success]\n')
    else:
        console.print(
            '[warning]⚠ IMEI не прошёл алгоритм Луна — возможна опечатка '
            'или нестандартный аппарат[/warning]\n'
        )

    all_data = []
    tac = imei[:8]

    rbi_data = _decode_rbi(imei)
    rbi_data = clean_record(rbi_data)
    if rbi_data:
        print_record(rbi_data, title='Структура IMEI (стандарт ITU-T E.118)')
        all_data.append({'source': 'ITU-T', 'data': rbi_data})

    console.print('[secondary]Запрос freemobileapi.com...[/secondary]')
    fm = _query_freemobile(tac)
    if fm:
        fm = clean_record(fm)
        if fm:
            print_record(fm, title='freemobileapi.com')
            all_data.append({'source': 'freemobileapi.com', 'data': fm})
    else:
        console.print('[warning]freemobileapi.com: нет данных[/warning]')

    console.print('[secondary]Запрос imeicheck.net...[/secondary]')
    ic = _query_imeicheck_api(imei)
    if ic:
        ic = clean_record(ic)
        if ic:
            print_record(ic, title='imeicheck.net')
            all_data.append({'source': 'imeicheck.net', 'data': ic})
    else:
        console.print('[warning]imeicheck.net: нет данных[/warning]')

    console.print('[secondary]Запрос GSMArena...[/secondary]')
    ga = _query_gsmarena(imei)
    if ga:
        ga = clean_record(ga)
        if ga:
            print_record(ga, title='GSMArena (поиск по TAC)')
            all_data.append({'source': 'GSMArena', 'data': ga})
    else:
        console.print('[warning]GSMArena: устройство не найдено[/warning]')

    # блок 5: apple coverage check
    console.print('[secondary]Запрос Apple Coverage Check...[/secondary]')
    ac = _query_apple_check(imei)
    if ac:
        print_record(ac, title='Apple Coverage Check')
        all_data.append({'source': 'Apple', 'data': ac})
    else:
        console.print('[secondary]Apple Coverage Check: не Apple-устройство[/secondary]')

    # ии анализ (только по честным данным)
    console.print('\n[secondary]ИИ анализ...[/secondary]')
    known_facts = [d for d in all_data if d['source'] != 'ITU-T']
    
    if known_facts:
        data_str = '\n'.join(f"{d['source']}: {d['data']}" for d in all_data)
        prompt = (
            f"Ниже — всё что известно об IMEI {imei} из реальных источников:\n\n"
            f"{data_str}\n\n"
            "Опиши устройство строго по этим данным. "
            "Если производитель или модель не найдены — так и напиши, не угадывай. "
            "Не добавляй ничего от себя. Коротко, на русском, без Markdown."
        )
    else:
        # Только RBI данные — говорим ИИ быть честным
        prompt = (
            f"По IMEI {imei} удалось определить только:\n"
            f"- Страна сертификации: {rbi_data.get('Страна сертификации', 'неизвестна')}\n"
            f"- TAC: {tac}\n\n"
            "Объясни пользователю, что точный производитель и модель "
            "по TAC можно определить только через платную GSMA-базу, "
            "и что бесплатные источники в данном случае не дали результата. "
            "Будь честен, не угадывай. Коротко, на русском, без Markdown."
        )

    for model in ['groq', 'mistral', 'chatgpt']:
        try:
            ai_response = get_ai_answer(prompt, model_name=model)
            console.print('\n[success]ИИ анализ:[/]\n')
            console.print(ai_response.replace('*', '').replace('#', '').strip())
            console.print()
            break
        except Exception:
            pass
