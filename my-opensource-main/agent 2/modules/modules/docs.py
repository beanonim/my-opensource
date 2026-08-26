DOCS = """
[bold secondary]═══ Документация LightWave Script (.lw) ═══[/bold secondary]

[primary]── Заголовок ──[/primary]
  module_name        = 'Название'
  module_developer   = 't.me/username'
  module_version     = 'v1.0'
  module_description = 'Описание до 100 символов'
  module_type        = 'script'    # script | visual | function

[primary]── Типы модулей ──[/primary]
  script   — обычный модуль, запускается из «Установленные модули»
  visual   — меняет внешний вид софта (темы, цвета, баннер, скобки)
  function — регистрируется как пункт в главном меню (код выдается автоматически)

[primary]── Переменные ──[/primary]
  x = 'строка'
  x = 42
  x = True / False
  x = y + 5
  x = y * 2
  x = y / 3
  x = y // 3
  x = y % 2
  x = y ** 2
  x = not flag
  x = a and b
  x = a or b
  y = ask('Вопрос')
  y = ask_hidden('Пароль')
  y = input('Вопрос')

[primary]── Системные переменные ──[/primary]
  name = lightwave.user(username)       # ник пользователя
  id = lightwave.user(uuid)             # UUID пользователя
  sub = lightwave.user(subscription)    # подписка пользователя

[primary]── Операции ──[/primary]
  x = 1 + 2
  x = 10 - 3
  x = 2 * 5
  x = 9 / 2
  x = 9 // 2
  x = 2 ** 3
  x = 'Hello' + ' ' + 'world'
  x = len(name) + 2

[primary]── Строки ──[/primary]
  z = format('Привет {name}!', name)
  z = upper(x)
  z = lower(x)
  z = trim(x)
  z = len(x)
  z = replace(x, 'а', 'б')
  z = contains(x, 'текст')
  z = split(x, ',')
  z = join(', ', mylist)
  z = starts_with(x, 'префикс')
  z = ends_with(x, 'суффикс')
  z = slice(x, 2)
  z = slice(x, 2, 5)

[primary]── Числа ──[/primary]
  x = int('42')
  x = float('3.14')
  x = str(42)
  x = bool(1)
  x = abs(-5)
  x = min(3, 1, 7)
  x = max(3, 1, 7)
  x = round(3.14)
  x = round(3.14159, 2)
  x = random(100)
  x = random(1, 10)

[primary]── Словарь (для API) ──[/primary]
  data = dict(token='abc', request=phone, limit=100)

[primary]── Вывод ──[/primary]
  print('текст')
  print(success, 'текст')
  print(error,   'текст')
  print(warning, 'текст')
  print(primary, 'текст')
  print(info,    'текст')

[primary]── Условия ──[/primary]
  if x is 'значение':
      print('да')
  elif x == 'другое':
      print('другой')
  else:
      print('нет')

  if x == 42
  if x != 'abc'
  if x > 10
  if not x
  if x is not 'abc'
  if contains(x, 'abc')

[primary]── Циклы ──[/primary]
  while x < 5:
      print(x)
      x = x + 1

  for i in range(10):
      print(i)

  for i in range(1, 10):
      print(i)

  for i in range(0, 100, 5):
      print(i)

  forever:
      print('крутится вечно')

  forever:
      x = ask('Введите exit для выхода')
      if x is 'exit':
          break

[primary]── Списки ──[/primary]
  mylist = list()
  mylist = list(1, 2, 3)
  list.append(mylist, 4)
  x = list.get(mylist, 0)
  list.set(mylist, 0, 99)
  list.remove(mylist, 0)
  list.sort(mylist)
  list.reverse(mylist)
  flag = list.contains(mylist, 5)
  print(len(mylist))

[primary]── Проверки ──[/primary]
  flag = is_number(x)
  flag = is_empty(x)
  t = type(x)

[primary]── Ввод ──[/primary]
  y = ask('Вопрос')
  y = ask_hidden('Пароль')
  y = input('Вопрос')

[primary]── Оформление (только для module_type = 'visual') ──[/primary]
  set_theme('hacker')                     # цветовая тема (standard, hacker, neon...)
  set_color(primary, '#ff0000')            # переопределить один цвет
  set_color(secondary, '#00ff00')          # роли: primary secondary success warning error
  set_color(banner, 'bold #00ffff')        #       text highlight dim banner
  set_banner_style('square')               # standard | square | square2 | classic_cli
  set_banner_layout('down')                # down | side
  set_brackets('«', '»')                   # скобки в меню
  set_input_style('2')                     # стиль ввода: 1-5
  set_banner('мой баннер\\nв две строки')   # свой баннер (\\n = новая строка)
  set_config('greeting', '2')              # сохранить любую настройку

  [dim]Пример визуального модуля:[/dim]
    module_name = 'Неон для lw'
    module_type = 'visual'
    module_developer = 't.me/username'
    module_version = 'v1.0'
    set_theme('neon')
    set_color(primary, '#00ffaa')
    set_banner_style('square')
    print(success, 'Готово! Тема применена')

[primary]── Модуль-функция (module_type = 'function') ──[/primary]
  [dim]Такой модуль появляется в главном меню и вызывается оттуда.[/dim]
  [dim]Мета-данные обязательны, ниже — обычный код .lw.[/dim]
  [dim]Код назначается автоматически, конфликты с встроенными не бывают.[/dim]

[primary]── Прочее ──[/primary]
  clear()
  sleep(1.5)

[primary]── HTTP запросы ──[/primary]
  result = request.send(write_answer, 'https://...')
  data   = dict(token='abc', q=phone)
  result = request.post_json(write_answer, 'https://...', data)
  result = request.get_json(write_answer, 'https://...', data) # data как параметры в URL (GET)

  result = http.get('https://api.example.com/data')
  result = http.post('https://api.example.com/data', data)
  code   = http.status('https://example.com')
  hdrs   = http.headers('https://example.com')

[primary]── JSON ──[/primary]
  name  = json.get(result, 'name')
  phone = json.get(result, 'data.phone')
  first = json.get(result, 'items.0.name')
  raw   = json.raw(result)
  new   = json.set(result, 'name', 'Иван')
  new   = json.set(result, 'items.0.name', 'Иван')

[primary]── Полный пример: меню поиска ──[/primary]
  phone  = ask('Введите номер')
  data   = dict(token='TOKEN', request=phone, limit=100, lang='ru')
  result = request.post_json(write_answer, 'https://leakosintapi.com/', data)
  count  = json.get(result, 'NumResults')
  if count is '':
      count = '0'
  print(primary, '══════════ РЕЗУЛЬТАТ ══════════')
  print(info, format('Номер:   {phone}', phone))
  print(info, format('Найдено: {count}', count))
  raw = json.raw(result)
  print(raw)
"""