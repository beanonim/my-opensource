from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *

CATBOX_HOST = "files.catbox.moe"
TMP_DIR = "/tmp/lightwave_catbox"
MAX_SIZE = 10 * 1024 * 1024
ALLOWED_EXT = ("png", "jpeg", "jpg", "webp", "bmp")

def download_image_with_retry(url, max_retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive"
    }       
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(url, stream=True, timeout=10, headers=headers)
            r.raise_for_status()
            return r, None
        except Exception as exc:
            if attempt == max_retries:
                return None, str(exc)
    return None, "unknown error"

def analyze_image_text(image_url=None):
    try:
        from model import TextAnalysisModel
    except ImportError:
        console.print('\n[error]Ошибка: модуль model.py не найден.[/error]')
        return

    os.makedirs(TMP_DIR, exist_ok=True)
    if not image_url:
        image_url = v2i('Вставьте ссылку на изображение (catbox.moe)', f'{USERNAME}@{UUID}').strip()

    if not image_url:
        console.print('\n[error]Ошибка: ссылка не введена[/error]')
        return

    try:
        parsed = urlparse(image_url)
        if parsed.scheme != "https" or parsed.hostname != CATBOX_HOST:
             console.print('\n[error]Ошибка: разрешены только https-ссылки files.catbox.moe[/error]')
             return
    except Exception:
        console.print('\n[error]Ошибка: некорректный URL[/error]')
        return

    console.print('\n[secondary]Загрузка изображения...[/secondary]')
    r, err = download_image_with_retry(image_url)
    if err:
        console.print('\n[error]Ошибка запроса[/error]')
        return

    ctype = r.headers.get("Content-Type", "")
    size = int(r.headers.get("Content-Length", 0))
    if size > MAX_SIZE:
        console.print('\n[error]Ошибка: файл слишком большой (макс. 10 MB)[/error]')
        return

    ext = ctype.split("/")[1].split(";")[0] if "/" in ctype else "jpg"
    tmp_path = os.path.join(TMP_DIR, f"{uuid.uuid4().hex}.{ext}")
    try:
        with open(tmp_path, "wb") as tmp_file:
            for chunk in r.iter_content(8192):
                tmp_file.write(chunk)
    except Exception:
        console.print('\n[error]Ошибка записи файла[/error]')
        return

    try:
        console.print('\n[secondary]Инициализация модели...[/secondary]')
        model = TextAnalysisModel(model_name="lightwave.gguf", use_ocr=True)
        console.print('[secondary]Обработка изображения...[/secondary]')
        result = model.process_image(tmp_path)
    except Exception:
        console.print('\n[error]Критическая ошибка[/error]')
        return
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if "error" in result:
        console.print('\n[error]Ошибка обработки[/error]')
        return

    info_table = Table(show_header=True, header_style="primary")
    info_table.add_column('Параметр', style='secondary', width=25)
    info_table.add_column('Значение', style='text')
    info_table.add_row('Файл изображения', result.get('image', 'N/A'))
    info_table.add_row('Метод OCR', result.get('ocr', {}).get('method', 'N/A'))
    ocr_confidence = result.get('ocr', {}).get('confidence', 0)
    info_table.add_row('Уверенность OCR', f"{ocr_confidence * 100:.1f}%")
    console.print('[warning]Информация об изображении:[/warning]')
    console.print(info_table)

    ocr_text = result.get('ocr', {}).get('text', '')
    console.print('\n[warning]Извлеченный текст:[/warning]')
    if ocr_text:
        console.print(f'[text]{ocr_text[:500]}{"..." if len(ocr_text) > 500 else ""}[/text]')
    else:
        console.print('[dim]Текст не распознан[/dim]')

    analysis = result.get('analysis', {})
    console.print('\n[warning]Статистика текста:[/warning]')
    stats_table = Table(show_header=True, header_style="primary")
    stats_table.add_column('Метрика', style='secondary', width=25)
    stats_table.add_column('Значение', style='text')
    stats_table.add_row('Всего символов', str(analysis.get('length', 0)))
    stats_table.add_row('Всего слов', str(analysis.get('words', 0)))
    stats_table.add_row('Всего предложений', str(analysis.get('sentences', 0)))
    console.print(stats_table)

    console.print('\n[warning]Анализ текста:[/warning]')
    analysis_table = Table(show_header=True, header_style="primary")
    analysis_table.add_column('Характеристика', style='secondary', width=25)
    analysis_table.add_column('Результат', style='text')
    language = analysis.get('analysis', {}).get('language', 'Unknown')
    analysis_table.add_row('Язык', f'[success]{language}[/success]')
    console.print(analysis_table)
    console.print('\n[success]Анализ завершен успешно[/success]')
