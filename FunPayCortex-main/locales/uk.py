# START OF FILE uk.py

# Глобальні
gl_next = "Далі ▶️"
gl_back = "Назад ◀️"
gl_yes = "Так ✅"
gl_yep = "Ага ✅"
gl_no = "Ні ❌"
gl_cancel = "Скасувати 🚫"
gl_error = "Помилка ⚠️"
gl_try_again = "Спробувати знову"
gl_error_try_again = f"{gl_error}. {gl_try_again}."
gl_refresh = "Оновити 🔄"
gl_delete = "Видалити 🗑️"
gl_edit = "Змінити ✏️"
gl_configure = "Налаштувати ⚙️"
gl_pcs = "шт."
gl_last_update = "Оновлено"
gl_refresh_and_try_again = "Оновіть список і спробуйте знову."
gl_close = "Закрити"
menu_closed = "Меню закрито."
help_not_found = "Довідку для цього розділу не знайдено."

# - Головне меню
mm_language = "🌍 Мова"
mm_global = "🔧 Загальні налаштування"
mm_notifications = "🔔 Сповіщення"
mm_autoresponse = "🤖 Автовідповідач"
mm_autodelivery = "📦 Автовидача"
mm_blacklist = "🚫 Чорний список"
mm_templates = "📝 Шаблони відповідей"
mm_greetings = "👋 Привітання"
mm_order_confirm = "👍 Відповідь на підтвердження"
mm_review_reply = "⭐ Відповідь на відгуки"
mm_new_msg_view = "💬 Вигляд сповіщень"
mm_plugins = "🧩 Плагіни"
mm_configs = "🔩 Конфігурації"
mm_authorized_users = "👤 Користувачі"
mm_proxy = "🌐 Проксі"
mm_manager_settings = "🔑 Налаштування менеджерів"
mm_manager_permissions = "⚙️ Права менеджерів"
mm_order_control = "{} 🛂 Контроль замовлень"
mp_can_control_orders = "{} 🛂 Контроль замовлень"

# Глобальні перемикачі
gs_autoraise = "{} Авто-буст лотів"
gs_autoresponse = "{} Автовідповідач"
gs_autodelivery = "{} Автовидача"
gs_nultidelivery = "{} Мульти-видача"
gs_autorestore = "{} Відновлення лотів"
gs_autodisable = "{} Деактивація лотів"
gs_old_msg_mode = "{} Застарілий режим повідомлень"
gs_keep_sent_messages_unread = "{} Не позначати прочитаним при відправці"

# Налаштування сповіщень
ns_new_msg = "{} Нове повідомлення"
ns_cmd = "{} Отримано команду"
ns_new_order = "{} Нове замовлення"
ns_order_confirmed = "{} Замовлення підтверджено"
ns_lot_activate = "{} Лот відновлено"
ns_lot_deactivate = "{} Лот деактивовано"
ns_delivery = "{} Товар видано"
ns_raise = "{} Лоти піднято"
ns_new_review = "{} Новий відгук"
ns_bot_start = "{} Бот запущено"
ns_other = "{} Інші (плагіни)"

# Налаштування автовідповідача
ar_edit_commands = "✏️ Редактор команд"
ar_add_command = "➕ Нова команда"
ar_to_ar = "🤖 До налаштувань автовідповідача"
ar_to_mm = "Меню 🏠"
ar_edit_response = "✏️ Текст відповіді"
ar_edit_notification = "✏️ Текст сповіщення"
ar_notification = "{} Сповіщення в Telegram"
ar_add_more = "➕ Ще"
ar_add_another = "➕ Іншу"
ar_no_valid_commands_entered = "Не введено жодної коректної команди."
ar_default_response_text = "Відповідь для цієї команди ще не налаштовано. Відредагуйте її."
ar_default_notification_text = "Користувач $username ввів команду: $message_text"
ar_command_deleted_successfully = "Команду/сет «{command_name}» успішно видалено."

# Налаштування авто-видачі
ad_edit_autodelivery = "🗳️ Редактор автовидачі"
ad_add_autodelivery = "➕ Прив'язати автовидачу"
ad_add_another_ad = "➕ Прив'язати інший"
ad_add_more_ad = "➕ Прив'язати ще"
ad_edit_goods_file = "📋 Файли товарів"
ad_upload_goods_file = "📤 Завантажити файл"
ad_create_goods_file = "➕ Створити файл"
ad_to_ad = "📦 До налаштувань автовидачі"
ad_to_mm = "Меню 🏠"
never_updated = "ніколи"
ad_default_response_text_new_lot = "Дякую за покупку, $username!\nОсь твій товар:\n$product"

# - Редагувати авто-видачу
ea_edit_delivery_text = "✏️ Текст видачі"
ea_link_goods_file = "🔗 Прив'язати файл товарів"
ea_delivery = "{} Автовидача"
ea_multidelivery = "{} Мультивидача"
ea_restore = "{} Відновлення"
ea_deactivate = "{} Деактивація"
ea_test = "🔑 Тестовий ключ"
ea_more_test = "🔑 Ще ключ"
ea_link_another_gf = "🔗 Інший файл"

# - Додати авто-видачу
fl_manual = "✍️ Ввести вручну"

# - Товарні файли
gf_add_goods = "➕ Додати товари"
gf_download = "📥 Завантажити"
gf_create_another = "➕ Створити інший"
gf_create_more = "➕ Створити ще"
gf_add_more = "➕ Додати ще"
gf_try_add_again = "➕ Повторити"
lot_info_header = "Інформація про лот"
text_not_set = "(текст не задано)"
gf_infinity = "нескінченно"
gf_count_error = "помилка підрахунку"
gf_file_not_found_short = "не знайдено"
gf_not_linked = "не прив'язаний"
gf_file_created_now = "створено"
gf_file_creation_error_short = "помилка створення"
no_lots_using_file = "Жоден лот не використовує цей файл."
gf_no_products_to_add = "Не було введено товарів для додавання."
gf_deleted_successfully = "Файл «{file_name}» успішно видалено."
gf_already_deleted = "Файл «{file_name}» вже був видалений."


# Налаштування чорного списку
bl_autodelivery = "{} Не видавати товар"
bl_autoresponse = "{} Не відповідати на команди"
bl_new_msg_notifications = "{} Без сповіщень про нові повідомлення"
bl_new_order_notifications = "{} Без сповіщень про нові замовлення"
bl_command_notifications = "{} Без сповіщень про команди"

# Шаблони відповідей
tmplt_add = "➕ Новий шаблон"
tmplt_add_more = "➕ Ще шаблон"
tmplt_add_another = "➕ Інший шаблон"
tmplt_editing_header = "📝 Редагування шаблону"
tmplt_err_empty_text = "❌ Текст шаблону не може бути порожнім. Будь ласка, введіть текст."
tmplt_deleted_successfully = "✅ Шаблон «{template_text}» успішно видалено."

# Налаштування привітання
gr_greetings = "{} Вітати нових"
gr_ignore_sys_msgs = "{} Ігнор системних повідомлень"
gr_edit_message = "✏️ Текст привітання"
gr_edit_cooldown = "⏱️ Кулдаун: {} дн."

# Налаштування відповіді на підтвердження замовлення
oc_watermark = "{} Водяний знак"
oc_send_reply = "{} Надсилати відповідь"
oc_edit_message = "✏️ Текст відповіді"

# Налаштування вигляду сповіщень про нові повідомлення
mv_incl_my_msg = "{} Мої повідомлення"
mv_incl_fp_msg = "{} Повідомлення FunPay"
mv_incl_bot_msg = "{} Повідомлення бота"
mv_only_my_msg = "{} Тільки мої"
mv_only_fp_msg = "{} Тільки від FunPay"
mv_only_bot_msg = "{} Тільки від бота"
mv_show_image_name = "{} Імена зображень"

# Плагіни
pl_add = "➕ Додати плагін"
pl_activate = "🚀 Активувати"
pl_deactivate = "💤 Деактивувати"
pl_commands = "⌨️ Команди"
pl_settings = "⚙️ Налаштування"
pl_status_active = "Статус: Активний 🚀"
pl_status_inactive = "Статус: Неактивний 💤"
pl_no_commands = "У цього плагіна немає зареєстрованих команд."
pl_delete_handler_failed = "⚠️ Помилка під час виконання обробника видалення плагіна «{plugin_name}». Плагін видалено зі списку, але його дані або файли могли залишитися. Перевірте логи."
pl_deleted_successfully = "✅ Плагін «{plugin_name}» успішно видалено. Перезапустіть FPCortex, щоб зміни набули чинності."
pl_file_delete_error = "⚠️ Не вдалося видалити файл плагіна «{plugin_path}». Перевірте права доступу та логи."
pl_safe_source = "Джерело безпечних плагінів"
pl_channel_button = "Канал FunPay Cortex"

# Конфіги
cfg_download_main = "📥 Завантажити Основний"
cfg_download_ar = "📥 Завантажити Автовідповідач"
cfg_download_ad = "📥 Завантажити Автовидачу"
cfg_upload_main = "📤 Завантажити Основний"
cfg_upload_ar = "📤 Завантажити Автовідповідач"
cfg_upload_ad = "📤 Завантажити Автовидачу"

# Авторизовані користувачі
tg_block_login = "{} Блокувати вхід за паролем"
role_admin = "👑 Адміністратор"
role_manager = "👤 Менеджер"
user_role = "Роль"
promote_to_admin = "👑 Зробити адміністратором"
demote_to_manager = "👤 Зробити менеджером"
revoke_access = "🗑️ Відкликати доступ"
manager_settings_desc = "Тут ви можете встановити ключ реєстрації для ваших менеджерів. Вони зможуть використовувати бота з обмеженими правами.\n\n<b>Поточний ключ:</b> {}"
manager_key_not_set = "<i>(не встановлено)</i>"
set_manager_key_btn = "🔑 Змінити ключ"
enter_manager_key_prompt = "Введіть новий ключ для реєстрації менеджерів. Щоб видалити ключ, надішліть <code>-</code>."
manager_key_changed_success = "✅ Ключ реєстрації менеджерів успішно змінено."
user_access_revoked = "✅ Доступ для користувача {0} відкликано."
user_role_changed_success = "✅ Роль користувача {0} змінено на «{1}»."
demote_last_admin_error = "❌ Не можна понизити в правах останнього адміністратора."
user_not_found = "Користувача не знайдено."
admin_only_command = "❌ Ця команда доступна лише адміністратору."
manager_permission_denied = "❌ У вас немає прав для виконання цієї команди."
role_change_already_admin = "Ви вже є адміністратором."
role_change_already_manager = "Ви вже є менеджером."
access_granted_role_changed = "Доступ оновлено! Ваша нова роль: <b>{0}</b>. Відкрийте меню командою /menu."
manager_reg_admin_error = "❌ Ви вже адміністратор. Вхід за ключем менеджера неможливий."
manager_access_granted = "✅ Доступ менеджера надано! Відкрийте меню командою /menu."
au_exit_cp = "Вийти з ПУ 🚪"

# Права менеджерів
mp_can_edit_ar = "{} Редагування автовідповідача"
mp_can_edit_ad = "{} Редагування автовидачі"
mp_can_edit_templates = "{} Редагування шаблонів"

# Проксі
prx_proxy_add = "➕ Додати проксі"
proxy_status_enabled = "Увімкнені"
proxy_status_disabled = "Вимкнені"
proxy_check_status_enabled = "Увімкнена"
proxy_check_status_disabled = "Вимкнена"
proxy_not_used_currently = "не використовується"
proxy_not_selected = "не вибраний"
proxy_check_interval_info = "Інтервал авто-перевірки: {interval} хв."
proxy_global_status_header = "Загальний статус проксі-модуля"
proxy_module_status_label = "Стан модуля:"
proxy_health_check_label = "Авто-перевірка проксі:"
proxy_current_in_use_label = "Поточний проксі в роботі:"
proxy_select_error_not_found = "⚠️ Помилка: цей проксі більше не існує у списку."
proxy_select_error_invalid_format = "⚠️ Помилка: вибраний проксі має невірний формат."
proxy_selected_and_applied = "✅ Проксі {proxy_str} вибрано та застосовано."
proxy_selected_not_applied = "ℹ️ Проксі {proxy_str} вибрано. Увімкніть модуль проксі в налаштуваннях, щоб він почав використовуватися."
proxy_deleted_successfully = "✅ Проксі {proxy_str} успішно видалено зі списку."
proxy_delete_error_not_found = "⚠️ Помилка: проксі для видалення не знайдено у списку."
proxy_undeletable = "❌ Цей проксі використовується і не може бути видалений."

# Оголошення
an_an = "{} Оголошення"
an_ad = "{} Реклама"

# Нове замовлення
ord_refund = "💸 Повернути кошти"
ord_answer = "✉️ Відповісти"
ord_templates = "📝 Шаблони"

# Нове повідомлення
msg_reply = "✉️ Відповісти"
msg_reply2 = "✉️ Ще раз"
msg_templates = "📝 Шаблони"
msg_more = "🔎 Детальніше"

# Тексти повідомлень
access_denied = """Привіт, <b><i>{}</i></b>! 👋

На жаль, у тебе немає доступу. ⛔

🔑 Введи <u><b>секретний пароль</b></u> (для адміна) або <u><b>ключ реєстрації</b></u> (для менеджера), щоб увійти.

✨ <b>FunPay Cortex</b> - твій найкращий помічник на FunPay!
📢 Дізнатися більше та приєднатися до нашої спільноти можна на каналі: <a href="https://t.me/FunPayCortex"><b>FunPay Cortex Channel</b></a>"""
access_granted = "Доступ відкрито! 🔓\n\n" \
                 "📢 Врахуй: сповіщення в <b><u>цей чат</u></b> поки що не надходять.\n\n" \
                 "🔔 Налаштувати їх можна в меню.\n\n" \
                 "⚙️ Відкрити меню налаштувань <i>FPCortex</i>: /menu"
access_granted_notification = "<b>🚨 УВАГА! 🚨\n\n\n</b>" * 3 + "\n\n\n🔐 Користувач \"<a href=\"tg://user?id={1}\">{0}</a>\" " \
                                                                 "<b>(ID: {1}) отримав доступ до панелі керування Telegram! 🔓</b>"
param_disabled = "❌ Це налаштування вимкнене глобально і не може бути змінене для цього лота.\n\n" \
                 "🌍 Глобальні налаштування доступні тут: " \
                 "/menu -> 🔧 Загальні налаштування."
old_mode_help = """<b>Новий режим отримання повідомлень</b> 🚀
✅ <i>FPCortex</i> бачить всю історію чату та всі деталі нових повідомлень.
✅ <i>FPCortex</i> може бачити зображення та пересилати їх у <i>Telegram</i>.
✅ <i>FPCortex</i> точно визначає автора: ти, співрозмовник або арбітраж.
❌ Чат стає "прочитаним" (не горить помаранчевим), оскільки <i>FPCortex</i> читає всю історію.

<b>Застарілий режим отримання повідомлень</b> 🐢
✅ Непрочитані тобою чати залишаються помаранчевими.
✅ Працює трохи швидше.
❌ <i>FPCortex</i> бачить тільки останнє повідомлення. Якщо надійде кілька повідомлень поспіль – побачить тільки останнє.
❌ <i>FPCortex</i> не бачить зображення і не може їх переслати.
❌ <i>FPCortex</i> не завжди точно визначає автора. Якщо чат не прочитаний – повідомлення від співрозмовника, інакше – від тебе. Ця логіка може давати збої. Арбітраж також не буде визначено.

💡 Якщо натиснути кнопку <code>Детальніше</code> у сповіщенні, <i>FPCortex</i> "прочитає" чат, покаже останні 15 повідомлень (включаючи картинки) і зможе точно визначити автора."""
bot_started = """✅ Telegram-бот запущено!
Ти можеш <b><u>налаштовувати конфіги</u></b> і <b><u>використовувати всі функції <i>Telegram</i>-бота</u></b>.

⏳ <i>FPCortex</i> <b><u>поки не ініціалізований</u></b>, його функції неактивні.
Коли <i>FPCortex</i> запуститься, це повідомлення зміниться.

🕒 Якщо ініціалізація займає багато часу, перевір логи командою /logs."""
fpc_init = """✅ <b><u>FPCortex ініціалізовано!</u></b>
ℹ️ <b><i>Версія:</i></b> <code>{}</code>
👑 <b><i>Акаунт:</i></b>  <code>{}</code> | <code>{}</code>
💰 <b><i>Баланс:</i></b> <code>{}₽, {}$, {}€</code>
📊 <b><i>Активні замовлення:</i></b>  <code>{}</code>

👨‍💻 <b><i>Автор:</i></b> @beedge"""

create_test_ad_key = "Введи назву лота для тесту автовидачі."
test_ad_key_created = """✅ Створено одноразовий ключ для видачі лота «<code>{}</code>».
Надішли команду нижче в чат з покупцем, щоб видати товар:
<code>!автовидача {}</code>"""
about = """<b>🧠 FPCortex 🧠 v{}</b>
<i>Автор:</i> @beedge"""
sys_info = """<b>📊 Системне зведення</b>

<b>⚙️ CPU:</b>
{}
    Використовується <i>FPCortex</i>: <code>{}%</code>

<b>💾 RAM:</b>
    Всього:  <code>{} MB</code>
    Використано:  <code>{} MB</code>
    Вільно:  <code>{} MB</code>
    Використовується ботом:  <code>{} MB</code>

<b>⏱️ Інше:</b>
    Аптайм:  <code>{}</code>
    ID чату:  <code>{}</code>"""
act_blacklist = """Введи нікнейм користувача для додавання в чорний список."""
already_blacklisted = "❌ Користувач <code>{}</code> вже в чорному списку."
user_blacklisted = "✅ Користувач <code>{}</code> доданий в чорний список."
act_unban = "Введи нікнейм користувача для видалення з чорного списку."
not_blacklisted = "❌ Користувача <code>{}</code> немає в чорному списку."
user_unbanned = "✅ Користувач <code>{}</code> видалений з чорного списку."
blacklist_empty = "🚫 Чорний список порожній."
act_proxy = "Введи проксі у форматі <u>login:password@ip:port</u> або <u>ip:port</u>."
proxy_already_exists = "❌ Проксі <code>{}</code> вже додано."
proxy_added = "✅ Проксі <u>{}</u> успішно додано."
proxy_format = "❌ Неправильний формат проксі. Потрібен: <u>login:password@ip:port</u> або <u>ip:port</u>."
proxy_adding_error = "⚠️ Помилка при додаванні проксі."
proxy_undeletable = "❌ Цей проксі використовується і не може бути видалений."
act_edit_watermark = "Введи новий текст водяного знака. Приклади:\n{}\n<code>𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙</code>\n" \
                     "<code>FPCortex</code>\n<code>[FunPay / Cortex]</code>\n<code>𝑭𝑷𝑪𝒙</code>\n" \
                     "<code>FPCx</code>\n<code>🤖</code>\n<code>🧠</code>\n\n" \
                     "Приклади можна скопіювати і відредагувати.\nВрахуй, що на FunPay емодзі " \
                     "🧠 може виглядати інакше.\n\nЩоб видалити водяний знак, надішли <code>-</code>."
v_edit_watermark_current = "Поточний"
watermark_changed = "✅ Водяний знак змінено."
watermark_deleted = "✅ Водяний знак видалено."
watermark_error = "⚠️ Некоректний водяний знак."
logfile_not_found = "❌ Лог-файл не знайдено."
logfile_sending = "Надсилаю лог-файл (це може зайняти час)... ⏳"
logfile_error = "⚠️ Не вдалося надіслати лог-файл."
logfile_deleted = "🗑️ Видалено {} лог-файлів."
update_no_tags = "❌ Не вдалося отримати список версій з GitHub. Спробуйте пізніше."
update_lasted = "✅ У вас встановлена остання версія FPCortex {}."
update_get_error = "❌ Не вдалося отримати інформацію про нову версію з GitHub. Спробуйте пізніше."
update_available = "✨ <b>Доступна нова версія FPCortex!</b> ✨\n\n{}"
update_update = "Щоб оновитися, введіть команду /update"
update_backup = "✅ Створено резервну копію (конфіги, сховище, плагіни): <code>backup.zip</code>.\n\n" \
                "🔒 <b>ВАЖЛИВО:</b> НЕ НАДСИЛАЙТЕ цей архів НІКОМУ. Він містить усі дані та налаштування бота (включаючи golden_key та товари)."
update_backup_error = "⚠️ Не вдалося створити резервну копію."
update_backup_not_found = "❌ Резервну копію не знайдено."
update_downloaded = "✅ Завантажено оновлення {}. Пропущено {} елементів (якщо це були старі релізи). Встановлюю..."
update_download_error = "⚠️ Помилка під час завантаження архіву оновлення."
update_done = "✅ Оновлення встановлено! Перезапустіть <i>FPCortex</i> командою /restart"
update_done_exe = "✅ Оновлення встановлено! Новий <code>FPCortex.exe</code> знаходиться в папці <code>update</code>. " \
                  "Вимкніть <i>FPCortex</i>, замініть старий <code>FPCortex.exe</code> новим " \
                  "і запустіть <code>Start.bat</code>."
update_install_error = "⚠️ Помилка під час встановлення оновлення."

restarting = "Перезапускаюся... 🚀"
power_off_0 = """<b>Ви впевнені, що хочете мене вимкнути?</b> 🤔
Увімкнути назад через <i>Telegram</i> <b><u>не вийде!</u></b>"""
power_off_1 = "Ще раз, про всяк випадок... <b><u>Точно вимикаємо?</u></b> 😟"
power_off_2 = """Просто щоб ти знав:
доведеться заходити на сервер/комп'ютер і запускати мене вручну! 💻"""
power_off_3 = """Не наполягаю, але якщо потрібно застосувати зміни основного конфігу,
можна просто перезапустити мене командою /restart. 😉"""
power_off_4 = "Ти взагалі читаєш мої повідомлення? 😉 Давай перевіримо: так = ні, ні = так. " \
              "Впевнений, ти навіть не читаєш, а я тут важливу інформацію пишу."
power_off_5 = "Отже, твоя остаточна відповідь... так? 😏"
power_off_6 = "Добре, добре, вимикаюся... 💤"
power_off_cancelled = "Вимкнення скасовано. Продовжуємо роботу! 👍"
power_off_error = "❌ Ця кнопка більше неактуальна. Виклич меню вимкнення знову."
enter_msg_text = "Введи текст повідомлення:"
msg_sent = "✅ Повідомлення надіслано в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sent_short = "✅ Повідомлення надіслано."
msg_sending_error = "⚠️ Не вдалося надіслати повідомлення в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sending_error_short = "⚠️ Не вдалося надіслати повідомлення."
send_img = "Надішли мені зображення 🖼️"
greeting_changed = "✅ Текст привітання змінено."
greeting_cooldown_changed = "✅ Кулдаун привітання змінено: {} дн."
order_confirm_changed = "✅ Текст відповіді на підтвердження замовлення змінено!"
review_reply_changed = "✅ Текст відповіді на {}⭐ відгук змінено!"
review_reply_empty = "⚠️ Відповідь на {}⭐ відгук не задано."
review_reply_text = "Відповідь на {}⭐ відгук:\n<code>{}</code>"
get_chat_error = "⚠️ Не вдалося отримати дані чату."
viewing = "Дивиться"
you = "Ти"
support = "тех. підтримка"
photo = "Фото"
refund_attempt = "⚠️ Не вдалося повернути кошти за замовленням <code>#{}</code>. Залишилося спроб: <code>{}</code>."
refund_error = "❌ Не вдалося повернути кошти за замовленням <code>#{}</code>."
refund_complete = "✅ Кошти за замовленням <code>#{}</code> повернуто."
updating_profile = "Оновлюю статистику акаунта... 📊"
profile_updating_error = "⚠️ Не вдалося оновити статистику."
acc_balance_available = "доступно"
act_change_golden_key = "🔑 Введи свій golden_key:"
cookie_changed = "✅ golden_key успішно змінено{}.\n"
cookie_changed2 = "Перезапусти бота командою /restart, щоб застосувати зміни."
cookie_incorrect_format = "❌ Неправильний формат golden_key. Спробуй ще раз."
cookie_error = "⚠️ Не вдалося авторизуватися. Можливо, введено невірний golden_key?"
ad_lot_not_found_err = "⚠️ Лот з індексом <code>{}</code> не знайдено."
ad_already_ad_err = "⚠️ У лота <code>{}</code> вже налаштована автовидача."
ad_lot_already_exists = "⚠️ До лота <code>{}</code> вже прив'язана автовидача."
ad_lot_linked = "✅ Автовидачу прив'язано до лота <code>{}</code>."
ad_link_gf = "Введи назву файлу з товарами.\nЩоб відв'язати файл, надішли <code>-</code>\n\n" \
             "Якщо файлу немає, він буде створений автоматично."
ad_gf_unlinked = "✅ Файл товарів відв'язаний від лота <code>{}</code>."
ad_gf_linked = "✅ Файл <code>storage/products/{}</code> прив'язаний до лота <code>{}</code>."
ad_gf_created_and_linked = "✅ Файл <code>storage/products/{}</code> <b><u>створено</u></b> і прив'язано до лота <code>{}</code>."
ad_creating_gf = "⏳ Створюю файл <code>storage/products/{}</code>..."
ad_product_var_err = "⚠️ До лота <code>{}</code> прив'язаний файл товарів, але в тексті видачі немає змінної <code>$product</code>."
ad_product_var_err2 = "⚠️ Не можна прив'язати файл: у тексті видачі немає змінної <code>$product</code>."
ad_text_changed = "✅ Текст видачі для лота <code>{}</code> змінено на:\n<code>{}</code>"
ad_updating_lots_list = "Оновлюю дані про лоти та категорії... ⏳"
ad_lots_list_updating_err = "⚠️ Не вдалося оновити дані про лоти та категорії."
gf_not_found_err = "⚠️ Файл товарів з індексом <code>{}</code> не знайдено."
copy_lot_name = "Надішли точну назву лота (як на FunPay)."
act_create_gf = "Введи назву для нового файлу товарів (наприклад, 'ключі_стім')."
gf_name_invalid = "🚫 Неприпустиме ім'я файлу.\n\n" \
                  "Дозволені лише <b><u>англійські</u></b> " \
                  "і <b><u>російські</u></b> літери, цифри, а також символи <code>_</code>, <code>-</code> та <code>пробіл</code>."
gf_already_exists_err = "⚠️ Файл <code>{}</code> вже існує."
gf_creation_err = "⚠️ Помилка при створенні файлу <code>{}</code>."
gf_created = "✅ Файл <code>storage/products/{}</code> створено."
gf_amount = "Товарів у файлі"
gf_uses = "Використовується в лотах"
gf_send_new_goods = "Надішли товари для додавання. Кожен товар з нового рядка (<code>Shift+Enter</code>)."
gf_add_goods_err = "⚠️ Не вдалося додати товари у файл."
gf_new_goods = "✅ Додано <code>{}</code> товар(а/ів) у файл <code>storage/products/{}</code>."
gf_empty_error = "📂 Файл storage/products/{} порожній."
gf_linked_err = "⚠️ Файл <code>storage/products/{}</code> прив'язаний до одного або кількох лотів.\n" \
                "Спочатку відв'яжи його від усіх лотів, потім видаляй."
gf_deleting_err = "⚠️ Не вдалося видалити файл <code>storage/products/{}</code>."
ar_cmd_not_found_err = "⚠️ Команду з індексом <code>{}</code> не знайдено."
ar_subcmd_duplicate_err = "⚠️ Команда <code>{}</code> дублюється в наборі."
ar_cmd_already_exists_err = "⚠️ Команда <code>{}</code> вже існує."
ar_enter_new_cmd = "Введи нову команду (або кілька, розділяючи їх символом <code>|</code>)."
ar_cmd_added = "✅ Нову команду <code>{}</code> додано."
ar_response_text = "Текст відповіді"
ar_notification_text = "Текст сповіщення"
ar_response_text_changed = "✅ Текст відповіді для команди <code>{}</code> змінено на:\n<code>{}</code>"
ar_notification_text_changed = "✅ Текст сповіщення для команди <code>{}</code> змінено на:\n<code>{}</code>"
cfg_main = "Основний конфіг. 🔒 ВАЖЛИВО: НЕ НАДСИЛАЙ цей файл НІКОМУ."
cfg_ar = "Конфіг автовідповідача."
cfg_ad = "Конфіг автовидачі."
cfg_not_found_err = "⚠️ Конфіг {} не знайдено."
cfg_empty_err = "📂 Конфіг {} порожній."
tmplt_not_found_err = "⚠️ Шаблон з індексом <code>{}</code> не знайдено."
tmplt_already_exists_err = "⚠️ Такий шаблон вже існує."
tmplt_added = "✅ Шаблон додано."
tmplt_msg_sent = "✅ Повідомлення за шаблоном надіслано в чат <a href=\"https://funpay.com/chat/?node={}\">{}</a>:\n\n<code>{}</code>"
pl_not_found_err = "⚠️ Плагін з UUID <code>{}</code> не знайдено."
pl_file_not_found_err = "⚠️ Файл <code>{}</code> не знайдено.\nПерезапусти <i>FPCortex</i> командою /restart."
pl_commands_list = "Команди плагіна <b><i>{}</i></b>:"
pl_author = "Автор"
pl_new = "Надішли мені файл плагіна (.py).\n\n<b>☢️ УВАГА!</b> Завантаження плагінів з неперевірених джерел може бути небезпечним."
au_user_settings = "Налаштування для користувача {}"
adv_fpc = "😎 FPCortex - твій найкращий асистент для FunPay!"
adv_description = """🧠 FPCortex v{} 🚀

🤖 Автовидача товарів
📈 Авто-буст лотів
💬 Розумний автовідповідач
♻️ Автовідновлення лотів
📦 Автодеактивація (якщо товари закінчилися)
🔝 Завжди онлайн
📲 Telegram-сповіщення
🕹️ Повний контроль через Telegram
🧩 Підтримка плагінів
🌟 І багато іншого!

👨‍💻 Автор: @beedge"""
exit_from_cp_warning = "Ви впевнені, що хочете вийти з панелі керування? Ця дія відкличе ваш доступ."
exit_from_cp_success = "Ви успішно вийшли з панелі керування. Ваш доступ відкликано."
exit_from_cp_success_alert = "Доступ відкликано."

# - Описи меню
desc_main = "Привіт! Вибери, що налаштуємо 👇"
desc_lang = "Вибери мову інтерфейсу:"
desc_gs = "Тут можна вмикати та вимикати основні функції <i>FPCortex</i>."
desc_ns = """Налаштуй сповіщення для цього чату.
Кожен чат налаштовується окремо!

ID цього чату: <code>{}</code>"""
desc_bl = "Встанови обмеження для користувачів із чорного списку."
desc_ar = "Додай команди для автовідповідача або відредагуй існуючі."
desc_ar_list = "Вибери команду або набір команд для редагування:"
desc_ad = "Налаштування автовидачі: прив'язка до лотів, керування файлами товарів і т.д."
desc_ad_list = "Список лотів з налаштованою автовидачею. Вибери лот для редагування:"
desc_ad_fp_lot_list = "Список лотів з твого профілю FunPay. Вибери лот, щоб налаштувати автовидачу.\n" \
                      "Якщо потрібного лота немає, натисни <code>🔄 Оновити</code>.\n\n" \
                      "Останнє сканування: {}"
desc_gf = "Вибери файл товарів для керування:"
desc_mv = "Налаштуй, як будуть виглядати сповіщення про нові повідомлення."
desc_gr = "Налаштуй привітальні повідомлення для нових діалогів.\n\n<b>Поточний текст привітання:</b>\n<code>{}</code>"
desc_oc = "Налаштуй повідомлення, яке буде надсилатися при підтвердженні замовлення.\n\n<b>Поточний текст повідомлення:</b>\n<code>{}</code>"
desc_or = "Налаштуй автоматичні відповіді на відгуки."
desc_an = "Налаштування сповіщень про оголошення."
desc_cfg = "Тут можна завантажити або вивантажити файли конфігурації."
desc_tmplt = "Керуй шаблонами швидких відповідей."
desc_pl = "Інформація та налаштування плагінів.\n\n" \
          "⚠️ <b>ВАЖЛИВО:</b> Після активації, деактивації, додавання або видалення плагіна, " \
          "<b><u>необхідно перезапустити бота</u></b> командою /restart!"
desc_au = "Налаштування авторизації користувачів у панелі керування Telegram."
desc_proxy = "Керування проксі-серверами для роботи бота."
desc_mp = "Тут ви можете налаштувати, які розділи та команди будуть доступні менеджерам."
unknown_action = "Невідома дія або кнопка застаріла."

# - Довідка
help_manager_permissions = "Цей розділ дозволяє вам детально налаштувати права для користувачів з роллю 'Менеджер'. Ви можете дозволити або заборонити їм доступ до певних функцій бота, таких як перегляд балансу, редагування автовідповідача та автовидачі, а також керування шаблонами відповідей."
help_new_message_view = "Тут налаштовується, які повідомлення з чатів FunPay будуть відображатися у сповіщеннях Telegram. Ви можете вмикати/вимикати показ ваших повідомлень, системних повідомлень FunPay та повідомлень, надісланих ботом. Також можна налаштувати отримання сповіщень тільки про повідомлення від певного типу відправника."

# - Опис команд
cmd_menu = "відкрити головне меню"
cmd_language = "змінити мову інтерфейсу"
cmd_profile = "подивитися статистику акаунта"
cmd_golden_key = "змінити golden_key (токен доступу)"
cmd_test_lot = "створити тестовий ключ автовидачі"
cmd_upload_chat_img = "(чат) завантажити картинку на FunPay"
cmd_upload_offer_img = "(лот) завантажити картинку на FunPay"
cmd_upload_plugin = "завантажити новий плагін"
cmd_ban = "додати користувача в ЧС"
cmd_unban = "видалити користувача з ЧС"
cmd_black_list = "показати чорний список"
cmd_watermark = "змінити водяний знак повідомлень"
cmd_note = "додати/змінити примітку про клієнта"
cmd_logs = "завантажити поточний лог-файл"
cmd_del_logs = "видалити старі лог-файли"
cmd_about = "інформація про бота"
cmd_check_updates = "перевірити оновлення"
cmd_update = "оновити бота"
cmd_sys = "системна інформація та навантаження"
cmd_create_backup = "створити резервну копію"
cmd_get_backup = "завантажити резервну копію"
cmd_restart = "перезапустити FPCortex"
cmd_power_off = "вимкнути FPCortex"

# - Опис змінних
v_edit_greeting_text = "Введи текст привітального повідомлення:"
v_edit_greeting_cooldown = "Введи кулдаун для привітання (у днях, наприклад, 0.5 для 12 годин):"
v_edit_order_confirm_text = "Введи текст відповіді на підтвердження замовлення:"
v_edit_review_reply_text = "Введи текст відповіді на відгук з {}⭐:"
v_edit_delivery_text = "Введи новий текст для автовидачі товару:"
v_edit_response_text = "Введи новий текст відповіді для команди:"
v_edit_notification_text = "Введи новий текст для Telegram-сповіщення:"
V_new_template = "Введи текст нового шаблону відповіді:"
v_list = "Доступні змінні:"
v_date = "<code>$date</code> - дата (ДД.ММ.РРРР)"
v_date_text = "<code>$date_text</code> - дата (1 січня)"
v_full_date_text = "<code>$full_date_text</code> - дата (1 січня 2001 року)"
v_time = "<code>$time</code> - час (ГГ:ХХ)"
v_full_time = "<code>$full_time</code> - час (ГГ:ХХ:СС)"
v_photo = "<code>$photo=[ID_ФОТО]</code> - картинка (ID через /upload_chat_img)"
v_sleep = "<code>$sleep=[СЕКУНДИ]</code> - затримка перед відправкою (наприклад, $sleep=2)"
v_order_id = "<code>$order_id</code> - ID замовлення (без #)"
v_order_link = "<code>$order_link</code> - посилання на замовлення"
v_order_title = "<code>$order_title</code> - назва замовлення"
v_order_params = "<code>$order_params</code> - параметри замовлення"
v_order_desc_and_params = "<code>$order_desc_and_params</code> - назва та/або параметри замовлення"
v_order_desc_or_params = "<code>$order_desc_or_params</code> - назва або параметри замовлення"
v_game = "<code>$game</code> - назва гри"
v_category = "<code>$category</code> - назва підкатегорії"
v_category_fullname = "<code>$category_fullname</code> - повна назва (підкатегорія + гра)"
v_product = "<code>$product</code> - товар з файлу (якщо не прив'язаний, не заміниться)"
v_chat_id = "<code>$chat_id</code> - ID чату"
v_chat_name = "<code>$chat_name</code> - назва чату"
v_message_text = "<code>$message_text</code> - текст повідомлення співрозмовника"
v_username = "<code>$username</code> - нікнейм співрозмовника"
v_cpu_core = "Ядро"

# Тексти винятків
exc_param_not_found = "Параметр «{}» не знайдено."
exc_param_cant_be_empty = "Значення параметра «{}» не може бути порожнім."
exc_param_value_invalid = "Неприпустиме значення для «{}». Дозволено: {}. Поточне: «{}»."
exc_goods_file_not_found = "Файл товарів «{}» не знайдено."
exc_goods_file_is_empty = "Файл «{}» порожній."
exc_not_enough_items = "У файлі «{}» не вистачає товарів. Потрібно: {}, доступно: {}."
exc_no_product_var = "Вказано «productsFileName», але в параметрі «response» немає змінної $product."
exc_no_section = "Секція відсутня."
exc_section_duplicate = "Виявлено дублікат секції."
exc_cmd_duplicate = "Команда або суб-команда «{}» вже існує."
exc_cfg_parse_err = "Помилка в конфігу {}, секція [{}]: {}"
exc_plugin_field_not_found = "Не вдалося завантажити плагін «{}»: відсутнє обов'язкове поле «{}»."

# Логи
log_tg_initialized = "$MAGENTATelegram бот ініціалізовано."
log_tg_started = "$CYANTelegram бот $YELLOW@{}CYAN запущено."
log_tg_handler_error = "Сталася помилка при виконанні хендлера Telegram бота."
log_tg_update_error = "Сталася помилка ({}) при отриманні оновлень Telegram (введено некоректний токен?)."
log_tg_notification_error = "Сталася помилка при надсиланні сповіщення в чат $YELLOW{}$RESET."
log_access_attempt = "$MAGENTA@{} (ID: {})$RESET спробував отримати доступ до ПУ. Стримую його як можу!"
log_manager_access_granted = "$YELLOW[MANAGER]$RESET $MAGENTA@{} (ID: {})$RESET отримав доступ до ПУ."
log_click_attempt = "$MAGENTA@{} (ID: {})$RESET натискає кнопки ПУ в чаті $MAGENTA@{} (ID: {})$RESET. У нього нічого не вийде!"
log_access_granted = "$MAGENTA@{} (ID: {})$RESET отримав доступ до ПУ."
log_new_ad_key = "$MAGENTA@{} (ID: {})$RESET створив ключ для видачі $YELLOW{}$RESET: $CYAN{}$RESET."
log_user_blacklisted = "$MAGENTA@{} (ID: {})$RESET додав $YELLOW{}$RESET в ЧС."
log_user_unbanned = "$MAGENTA@{} (ID: {})$RESET видалив $YELLOW{}$RESET з ЧС."
log_watermark_changed = "$MAGENTA@{} (ID: {})$RESET змінив водяний знак повідомлень на $YELLOW{}$RESET."
log_watermark_deleted = "$MAGENTA@{} (ID: {})$RESET видалив водяний знак повідомлень."
log_greeting_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст привітання на $YELLOW{}$RESET."
log_greeting_cooldown_changed = "$MAGENTA@{} (ID: {})$RESET змінив кулдаун привітального повідомлення на $YELLOW{}$RESET дн."
log_order_confirm_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст відповіді на підтвердження замовлення на $YELLOW{}$RESET."
log_review_reply_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст відповіді на відгук з {} зір. на $YELLOW{}$RESET."
log_param_changed = "$MAGENTA@{} (ID: {})$RESET змінив параметр $CYAN{}$RESET секції $YELLOW[{}]$RESET на $YELLOW{}$RESET."
log_notification_switched = "$MAGENTA@{} (ID: {})$RESET перемкнув сповіщення $YELLOW{}$RESET для чату $YELLOW{}$RESET на $CYAN{}$RESET."
log_ad_linked = "$MAGENTA@{} (ID: {})$RESET прив'язав авто-видачу до лота $YELLOW{}$RESET."
log_ad_text_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст видачі лота $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ad_deleted = "$MAGENTA@{} (ID: {})$RESET видалив авто-видачу лота $YELLOW{}$RESET."
log_gf_created = "$MAGENTA@{} (ID: {})$RESET створив товарний файл $YELLOWstorage/products/{}$RESET."
log_gf_unlinked = "$MAGENTA@{} (ID: {})$RESET відв'язав товарний файл від лота $YELLOW{}$RESET."
log_gf_linked = "$MAGENTA@{} (ID: {})$RESET прив'язав товарний файл $YELLOWstorage/products/{}$RESET до лота $YELLOW{}$RESET."
log_gf_created_and_linked = "$MAGENTA@{} (ID: {})$RESET створив і прив'язав товарний файл $YELLOWstorage/products/{}$RESET до лота $YELLOW{}$RESET."
log_gf_new_goods = "$MAGENTA@{} (ID: {})$RESET додав $CYAN{}$RESET товар(-а, -ів) у файл $YELLOWstorage/products/{}$RESET."
log_gf_downloaded = "$MAGENTA@{} (ID: {})$RESET запросив товарний файл $YELLOWstorage/products/{}$RESET."
log_gf_deleted = "$MAGENTA@{} (ID: {})$RESET видалив товарний файл $YELLOWstorage/products/{}$RESET."
log_ar_added = "$MAGENTA@{} (ID: {})$RESET додав нову команду $YELLOW{}$RESET."
log_ar_response_text_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст відповіді команди $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ar_notification_text_changed = "$MAGENTA@{} (ID: {})$RESET змінив текст сповіщення команди $YELLOW{}$RESET на $YELLOW\"{}\"$RESET."
log_ar_cmd_deleted = "$MAGENTA@{} (ID: {})$RESET видалив команду $YELLOW{}$RESET."
log_cfg_downloaded = "$MAGENTA@{} (ID: {})$RESET запросив конфіг $YELLOW{}$RESET."
log_tmplt_added = "$MAGENTA@{} (ID: {})$RESET додав заготовку відповіді $YELLOW\"{}\"$RESET."
log_tmplt_deleted = "$MAGENTA@{} (ID: {})$RESET видалив заготовку відповіді $YELLOW\"{}\"$RESET."
log_pl_activated = "$MAGENTA@{} (ID: {})$RESET активував плагін $YELLOW\"{}\"$RESET."
log_pl_deactivated = "$MAGENTA@{} (ID: {})$RESET деактивував плагін $YELLOW\"{}\"$RESET."
log_pl_deleted = "$MAGENTA@{} (ID: {})$RESET видалив плагін $YELLOW\"{}\"$RESET."
log_pl_delete_handler_err = "Сталася помилка при виконанні хендлера видалення плагіна $YELLOW\"{}\"$RESET."
log_user_revoked = "$MAGENTA@{} (ID: {})$RESET відкликав доступ у користувача $YELLOW{} (ID: {})$RESET."
log_user_role_changed = "$MAGENTA@{} (ID: {})$RESET змінив роль користувача $YELLOW{} (ID: {})$RESET на $CYAN{}$RESET."
log_manager_key_changed = "$MAGENTA@{} (ID: {})$RESET змінив ключ реєстрації менеджерів на $YELLOW{}$RESET."

# Логи хендлерів
log_new_msg = "$MAGENTA┌──$RESET Нове повідомлення в листуванні з користувачем $YELLOW{} (CID: {}):"
log_sending_greetings = "Користувач $YELLOW{} (CID: {})$RESET написав уперше! Надсилаю привітальне повідомлення..."
log_new_cmd = "Отримано команду $YELLOW{}$RESET у чаті з користувачем $YELLOW{} (CID: {})$RESET."
ntfc_new_order_price_details = "<code>{seller_price} {currency}</code> (покупець заплатив <code>{buyer_price} {currency}</code>)"
ntfc_new_order_no_link = "💰 <b>Нове замовлення:</b> <code>{}</code>\n\n<b><i>🙍‍♂️ Покупець:</i></b>  <code>{}</code>\n<b><i>💵 Сума:</i></b>  {}\n<b><i>📇 ID:</i></b> <code>#{}</code>\n\n<i>{}</i>"
ntfc_new_order_not_in_cfg = "ℹ️ Товар не буде видано, оскільки до лота не прив'язана авто-видача."
ntfc_new_order_ad_disabled = "ℹ️ Товар не буде видано, оскільки авто-видача вимкнена в глобальних перемикачах."
ntfc_new_order_ad_disabled_for_lot = "ℹ️ Товар не буде видано, оскільки авто-видача вимкнена для цього лота."
ntfc_new_order_user_blocked = "ℹ️ Товар не буде видано, оскільки користувач знаходиться в ЧС і ввімкнено блокування авто-видачі."
ntfc_new_order_will_be_delivered = "ℹ️ Товар буде видано найближчим часом."
ntfc_new_review = "🔮 Ви отримали {} за замовлення <code>{}</code>!\n\n💬<b>Відгук:</b>\n<code>{}</code>{}"
ntfc_review_reply_text = "\n\n🗨️<b>Відповідь:</b> \n<code>{}</code>"

# Логи кортекса
crd_proxy_detected = "Виявлено проксі."
crd_checking_proxy = "Виконую перевірку проксі..."
crd_proxy_err = "Не вдалося підключитися до проксі. Переконайтеся, що дані введено вірно."
crd_proxy_success = "Проксі успішно перевірено! IP-адреса: $YELLOW{}$RESET."
crd_acc_get_timeout_err = "Не вдалося завантажити дані про акаунт: перевищено тайм-аут очікування."
crd_acc_get_unexpected_err = "Сталася непередбачена помилка при отриманні даних акаунта."
crd_try_again_in_n_secs = "Повторю спробу через {} секунд(-у/-и)..."
crd_getting_profile_data = "Отримую дані про лоти та категорії..."
crd_profile_get_timeout_err = "Не вдалося завантажити дані про лоти акаунта: перевищено тайм-аут очікування."
crd_profile_get_unexpected_err = "Сталася непередбачена помилка при отриманні даних про лоти та категорії."
crd_profile_get_too_many_attempts_err = "Сталася помилка при отриманні даних про лоти та категорії: перевищено кількість спроб ({})."
crd_profile_updated = "Оновив інформацію про лоти $YELLOW({})$RESET та категорії $YELLOW({})$RESET профілю."
crd_tg_profile_updated = "Оновив інформацію про лоти $YELLOW({})$RESET та категорії $YELLOW({})$RESET профілю (TG ПУ)."
crd_raise_time_err = 'Не вдалося підняти лоти категорії $CYAN\"{}\"$RESET. FunPay каже: "{}". Наступна спроба через {}.'
crd_raise_unexpected_err = "Сталася непередбачена помилка при спробі підняти лоти категорії $CYAN\"{}\"$RESET. Пауза на 10 секунд..."
crd_raise_status_code_err = "Помилка {} при піднятті лотів категорії $CYAN\"{}\"$RESET. Пауза на 1 хв..."
crd_lots_raised = "Всі лоти категорії $CYAN\"{}\"$RESET піднято!"
crd_raise_wait_3600 = "Наступна спроба через {}."
crd_msg_send_err = "Сталася помилка при надсиланні повідомлення в чат $YELLOW{}$RESET."
crd_msg_attempts_left = "Залишилося спроб: $YELLOW{}$RESET."
crd_msg_no_more_attempts_err = "Не вдалося надіслати повідомлення в чат $YELLOW{}$RESET: перевищено кількість спроб."
crd_msg_sent = "Надіслав повідомлення в чат $YELLOW{}."
crd_session_timeout_err = "Не вдалося оновити сесію: перевищено тайм-аут очікування."
crd_session_unexpected_err = "Сталася непередбачена помилка при оновленні сесії."
crd_session_no_more_attempts_err = "Не вдалося оновити сесію: перевищено кількість спроб."
crd_session_updated = "Сесію оновлено."
crd_raise_loop_started = "$CYANЦикл автопідняття лотів запущено (це не означає, що автопідняття лотів увімкнено)."
crd_raise_loop_not_started = "$CYANЦикл автопідняття не було запущено, оскільки на акаунті не виявлено лотів."
crd_session_loop_started = "$CYANЦикл оновлення сесії запущено."
crd_no_plugins_folder = "Папку з плагінами не виявлено."
crd_no_plugins = "Плагіни не виявлено."
crd_plugin_load_err = "Не вдалося завантажити плагін {}."
crd_invalid_uuid = "Не вдалося завантажити плагін {}: невалідний UUID."
crd_uuid_already_registered = "UUID {} ({}) вже зареєстровано."
crd_handlers_registered = "Хендлери з $YELLOW{}.py$RESET зареєстровано."
crd_handler_err = "Сталася помилка при виконанні хендлера."
crd_tg_au_err = "Не вдалося змінити повідомлення з інформацією про користувача: {}. Спробую без посилання."

acc_balance_available = "доступно"
gf_infinity = "нескінченно"
gf_count_error = "помилка підрахунку"
gf_file_not_found_short = "не знайдено"
gf_not_linked = "не прив'язаний"
gf_file_created_now = "створено"
gf_file_creation_error_short = "помилка створення"
no_lots_using_file = "Жоден лот не використовує цей файл."
gf_no_products_to_add = "Не було введено товарів для додавання."
gf_deleted_successfully = "Файл «{file_name}» успішно видалено."
gf_already_deleted = "Файл «{file_name}» вже був видалений."
ar_no_valid_commands_entered = "Не введено жодної коректної команди."
ar_default_response_text = "Відповідь для цієї команди ще не налаштовано. Відредагуйте її."
ar_default_notification_text = "Користувач $username ввів команду: $message_text"
ar_command_deleted_successfully = "Команду/сет «{command_name}» успішно видалено."
file_err_not_detected = "❌ Файл не знайдено в повідомленні."
file_err_must_be_text = "❌ Файл має бути текстовим (наприклад, .txt, .cfg, .py, .json, .ini, .log)."
file_err_wrong_format = "❌ Неправильний формат файлу: <b><u>.{actual_ext}</u></b> (очікувався <b><u>.{expected_ext}</u></b>)."
file_err_too_large = "❌ Розмір файлу не повинен перевищувати 20МБ."
file_info_downloading = "⏬ Завантажую файл з серверів Telegram..."
file_err_download_failed = "❌ Сталася помилка під час завантаження файлу на сервер бота."
file_info_checking_validity = "🤔 Перевіряю вміст файлу..."
file_err_processing_generic = "⚠️ Сталася помилка при обробці файлу: <code>{error_message}</code>"
file_err_utf8_decode = "Сталася помилка при читанні файлу (UTF-8). Переконайтеся, що кодування файлу — UTF-8, а формат кінця рядків — LF."
file_info_main_cfg_loaded = "✅ Основний конфіг успішно завантажено.\n\n⚠️ <b>Необхідно перезапустити бота (/restart)</b>, щоб зміни набули чинності.\n\nБудь-які зміни основного конфігу через перемикачі в панелі керування до перезапуску скасують завантажені налаштування."
file_info_ar_cfg_applied = "✅ Конфіг автовідповідача успішно завантажено та застосовано."
file_info_ad_cfg_applied = "✅ Конфіг автовидачі успішно завантажено та застосовано."
plugin_uploaded_success = "✅ Плагін <code>{filename}</code> успішно завантажено.\n\n⚠️Щоб плагін запрацював, <b><u>перезавантажте FPCortex!</u></b> (/restart)"
image_upload_unsupported_format = "❌ Непідтримуваний формат зображення. Доступні: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>."
image_upload_error_generic = "⚠️ Не вдалося вивантажити зображення на FunPay. Подробиці дивіться в лог-файлі (<code>logs/log.log</code>)."
image_upload_chat_success_info = "Використовуйте цей ID в текстах автовидачі або автовідповіді зі змінною <code>$photo</code>.\n\nНаприклад: <code>$photo={image_id}</code>"
image_upload_offer_success_info = "Використовуйте цей ID для додавання зображень до ваших лотів на FunPay."
image_upload_success_header = "✅ Зображення успішно вивантажено на сервер FunPay.\n\n<b>ID зображення:</b> <code>{image_id}</code>\n\n"
products_file_provide_prompt = "📎 Надішліть мені файл з товарами (.txt):"
products_file_upload_success = "✅ Файл з товарами <code>{filepath}</code> успішно завантажено. Товарів у файлі: <code>{count}</code>."
products_file_count_error = "⚠️ Сталася помилка при підрахунку товарів у завантаженому файлі."
main_config_provide_prompt = "⚙️ Надішліть мені файл основного конфігу (<code>_main.cfg</code>):"
ar_config_provide_prompt = "🤖 Надішліть мені файл конфігу автовідповідача (<code>auto_response.cfg</code>):"
ad_config_provide_prompt = "📦 Надішліть мені файл конфігу автовидачі (<code>auto_delivery.cfg</code>):"
pl_status_active = "Статус: Активний 🚀"
pl_status_inactive = "Статус: Неактивний 💤"
pl_no_commands = "У цього плагіна немає зареєстрованих команд."
pl_delete_handler_failed = "⚠️ Помилка під час виконання обробника видалення плагіна «{plugin_name}». Плагін видалено зі списку, але його дані або файли могли залишитися. Перевірте логи."
pl_deleted_successfully = "✅ Плагін «{plugin_name}» успішно видалено. Перезапустіть FPCortex, щоб зміни набули чинності."
pl_file_delete_error = "⚠️ Не вдалося видалити файл плагіна «{plugin_path}». Перевірте права доступу та логи."
proxy_status_enabled = "Увімкнені"
proxy_status_disabled = "Вимкнені"
proxy_check_status_enabled = "Увімкнена"
proxy_check_status_disabled = "Вимкнена"
proxy_not_used_currently = "не використовується"
proxy_not_selected = "не вибраний"
proxy_check_interval_info = "Інтервал авто-перевірки: {interval} хв."
proxy_global_status_header = "Загальний статус проксі-модуля"
proxy_module_status_label = "Стан модуля:"
proxy_health_check_label = "Авто-перевірка проксі:"
proxy_current_in_use_label = "Поточний проксі в роботі:"
proxy_select_error_not_found = "⚠️ Помилка: цей проксі більше не існує у списку."
proxy_select_error_invalid_format = "⚠️ Помилка: вибраний проксі має невірний формат."
proxy_selected_and_applied = "✅ Проксі {proxy_str} вибрано та застосовано."
proxy_selected_not_applied = "ℹ️ Проксі {proxy_str} вибрано. Увімкніть модуль проксі в налаштуваннях, щоб він почав використовуватися."
proxy_deleted_successfully = "✅ Проксі {proxy_str} успішно видалено зі списку."
proxy_delete_error_not_found = "⚠️ Помилка: проксі для видалення не знайдено у списку."
tmplt_editing_header = "📝 Редагування шаблону"
tmplt_err_empty_text = "❌ Текст шаблону не може бути порожнім. Будь ласка, введіть текст."
tmplt_deleted_successfully = "✅ Шаблон «{template_text}» успішно видалено."
no_messages_to_display = "Немає повідомлень для відображення"

autotp_command_desc = "налаштування авто-створення тікетів у ТП"
autotp_settings_header = "⚙️ <b>Налаштування AutoTP</b>\n\n{}"
autotp_status_line = "Статус: <b>{}</b>\nНаступна перевірка через: <b>~{} хв.</b>"
autotp_status_enabled = "🟢 Увімкнено"
autotp_status_disabled = "🔴 Вимкнено"
autotp_trigger_button = "🚀 Створити тікети зараз"
autotp_toggle_button = "{} Авто-створення тікетів"
autotp_interval_button = "⏳ Інтервал: {} хв."
autotp_threshold_button = "⏰ Поріг: {} год."
autotp_exclusions_button = "🚫 Винятки"
autotp_template_button = "📝 Шаблон тікета"
autotp_alert_enabled = "✅ Авто-створення тікетів увімкнено"
autotp_alert_disabled = "❌ Авто-створення тікетів вимкнено"
autotp_prompt_interval = "Введіть новий інтервал перевірки в хвилинах (наприклад, 30):"
autotp_err_interval_too_small = "❌ Інтервал не може бути меншим за 5 хвилин."
autotp_success_interval_changed = "✅ Інтервал перевірки змінено на {} хвилин."
autotp_prompt_threshold = "Введіть новий поріг часу для створення тікета в годинах (наприклад, 24):"
autotp_err_threshold_too_small = "❌ Поріг часу не може бути меншим за 1 годину."
autotp_success_threshold_changed = "✅ Поріг часу для створення тікета змінено на {} годин."
autotp_prompt_template = "Поточний шаблон:\n{}\n\nНадішліть новий. Використовуйте `{orders}` для списку замовлень."
autotp_err_template_no_placeholder = "❌ Шаблон повинен містити `{orders}` для підстановки списку замовлень."
autotp_success_template_changed = "✅ Шаблон тікета успішно оновлено."
autotp_exclusions_header = "🚫 <b>Керування винятками категорій</b>\n\nВиберіть категорії, для яких <b>не потрібно</b> створювати тікети."
autotp_no_active_categories = "🤷‍♂️ Не знайдено активних категорій на акаунті."
autotp_trigger_started = "🚀 Запускаю перевірку замовлень та створення тікетів..."
autotp_notify_success = "✅ AutoTP: Створено тікет для замовлень:\n{}"
autotp_notify_fail = "❌ AutoTP: Не вдалося створити тікет для замовлень:\n{}"
autotp_notify_no_orders = "✅ AutoTP: Перевірку завершено. Замовлень для створення тікета не знайдено."
autotp_exclusions_legend = "✅ - тікети для цієї категорії будуть створюватися.\n🚫 - тікети для цієї категорії створюватися не будуть."

# Статистика
stat_adv_stats_button = "📈 Статистика"
stat_settings_desc = "⚙️ <b>Налаштування статистики</b>\n\nТут можна налаштувати періодичні звіти та глибину аналізу продажів."
stat_notifications_button = "{} Періодичні звіти"
stat_notif_for_chat_button = "{} Сповіщення в цьому чаті"
stat_interval_button = "⏳ Інтервал: {} год."
stat_period_button = "🗓️ Період аналізу: {} дн."
stat_prompt_interval = "Введіть новий інтервал для періодичних звітів (у годинах):"
stat_prompt_period = "Введіть новий період для аналізу продажів (у днях):"
mp_can_view_stats = "{} Перегляд статистики"

# CRM
cmd_note = "додати/змінити нотатку про клієнта"
crm_prompt_add_note = "Надішліть нотатку у форматі: `Нікнейм Нотатка`\nНаприклад: `SLLMK віддає перевагу доставці вночі`"
crm_err_note_format = "❌ Неправильний формат. Використовуйте: `Нікнейм Нотатка`."
crm_err_customer_not_found = "❌ Клієнта з ніком `{username}` не знайдено в базі."
crm_success_note_added = "✅ Нотатку для клієнта `{username}` успішно додано/оновлено."

# Order Control
mm_order_control = "🛂 Контроль замовлень"
oc_menu_desc = "Тут налаштовуються сповіщення про 'завислі' замовлення."
oc_notify_pending_execution = "{} 🔔 Повідомляти про замовлення, що очікують виконання"
oc_notify_pending_confirmation = "{} 🔔 Повідомляти про замовлення, що очікують підтвердження"
oc_pending_execution_threshold = "⏳ Поріг для виконання: {} хв."
oc_pending_confirmation_threshold = "⏳ Поріг для підтвердження: {} год."
oc_prompt_exec_threshold = "Введіть час у хвилинах, після якого замовлення буде вважатися 'завислим' і потребує виконання."
oc_prompt_confirm_threshold = "Введіть час у годинах, після якого потрібно нагадати про непідтверджене замовлення (після того, як ви позначите його виконаним)."
oc_err_threshold_format = "❌ Неправильне значення. Введіть ціле додатне число."
oc_success_threshold_changed = "✅ Поріг успішно змінено на {}."
oc_notify_pending_execution_msg = "⚠️ Замовлення <code>#{order_id}</code> від <code>{username}</code> очікує на вашу увагу вже понад {minutes} хвилин!"
oc_notify_pending_confirmation_msg = "🔔 Покупець <code>{username}</code> не підтверджує замовлення <code>#{order_id}</code> вже понад {hours} годин. Можливо, варто йому нагадати."
oc_mark_as_delivered_btn = "Товар видано"
oc_alert_marked_as_delivered = "✅ Замовлення позначено як виконане. Таймер для нагадування про підтвердження запущено."
ord_dont_refund = "Не повертати"