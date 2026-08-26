from modules.imports import *
from modules.config import *
from modules.console import *
from modules.input import *
from modules.api import *

fake = Faker("ru_RU")

def upload_to_litterbox(filepath):
    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                'https://litterbox.catbox.moe/resources/internals/api.php',
                files={'fileToUpload': f},
                data={
                    'reqtype': 'fileupload',
                    'time': '24h'
                }
            )
        if response.status_code == 200:
            link = response.text.strip()
            if link.startswith('https://'):
                return link
            else:
                 console.print("[error]Ошибка API[/error]")
        else:
             console.print("[error]Ошибка источника[/error]")
        return None
    except Exception:
        console.print("[error]Ошибка загрузки[/error]")
        return None

def fake_db_generator():
    try:
        rows_input = v2i("Сколько строк сгенерировать", f'{USERNAME}@{UUID}')
        if not rows_input.isdigit():
            console.print("[error]Ошибка: Введите число.[/error]")
            return
        
        rows = int(rows_input)
        avg_line = 60
        size_mb = (rows * avg_line) / (1024 * 1024)
        console.print(f"\n[secondary]Примерный размер файла: ~{size_mb:.2f} MB[/secondary]")
        
        confirm = v2i("Сгенерировать и загрузить файл? (y/n) >>> ", f'{USERNAME}@{UUID}').strip().lower()
        if confirm not in ['y', 'yes', 'д', 'да']:
            console.print("[warning]Отмена генерации.[/warning]")
            return
        
        console.print("\n[success]Начинаю генерацию...[/success]")
        temp_file = tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False)
        temp_path = temp_file.name
        
        try:
            with temp_file as f:
                f.write("fio;birthday;phone;country\n")
                for i in range(rows):
                    fio = fake.name()
                    birthday = fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%d.%m.%Y")
                    if random.choice([True, False]): 
                        phone = "+380" + "".join(random.choice("0123456789") for _ in range(9))
                        country = "Украина"
                    else: 
                        phone = "+7" + "".join(random.choice("0123456789") for _ in range(10))
                        country = random.choice(["Россия", "Казахстан"])
                    f.write(f"{fio};{birthday};{phone};{country}\n")
            
            console.print(f"\n[success]Файл создан ({rows} строк)[/success]")
            console.print("[secondary]Загружаю на Litterbox...[/secondary]")
            link = upload_to_litterbox(temp_path)
            
            if link:
                console.print(f"\n[success]Готово! Ваша ссылка:\n{link}[/success]")
            else:
                console.print("\n[error]Ошибка загрузки файла[/error]")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    except KeyboardInterrupt:
        console.print("\n\n[warning]Программа остановлена пользователем.[/warning]")
    except Exception as e:
        console.print(f"\n[error]Произошла ошибка: {e}[/error]")
    