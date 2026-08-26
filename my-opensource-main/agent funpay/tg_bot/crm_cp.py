# tg_bot/crm_cp.py
from __future__ import annotations
from typing import TYPE_CHECKING
import os
import json
import time
import logging
from threading import Thread

from FunPayAPI.common.enums import OrderStatuses
from FunPayAPI.updater.events import NewOrderEvent, InitialChatEvent, OrderStatusChangedEvent

from locales.localizer import Localizer

if TYPE_CHECKING:
    from cortex import Cortex

logger = logging.getLogger("FPC.crm_cp")
localizer = Localizer()
_ = localizer.translate

CRM_FILE_PATH = "storage/cache/crm_data.json"

def load_crm_data(cortex: Cortex):
    """Загружает данные CRM из файла."""
    if os.path.exists(CRM_FILE_PATH):
        try:
            with open(CRM_FILE_PATH, "r", encoding="utf-8") as f:
                cortex.crm_data = {int(k): v for k, v in json.load(f).items()}
        except (json.JSONDecodeError, IOError, ValueError) as e:
            logger.error(f"Ошибка загрузки данных CRM: {e}")
            cortex.crm_data = {}
    else:
        cortex.crm_data = {}

def save_crm_data(cortex: Cortex):
    """Сохраняет данные CRM в файл."""
    try:
        with open(CRM_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(cortex.crm_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"Ошибка сохранения данных CRM: {e}")

def get_or_create_customer(cortex: Cortex, user_id: int, username: str | None) -> dict:
    """Получает или создает профиль клиента в CRM."""
    if user_id not in cortex.crm_data:
        cortex.crm_data[user_id] = {
            "username": username,
            "first_contact_ts": int(time.time()),
            "last_contact_ts": int(time.time()),
            "purchases": [],
            "refunds": [],
            "pending": [],
            "notes": ""
        }
        logger.debug(f"Создан новый профиль в CRM для {username} ({user_id})")
    elif username and cortex.crm_data[user_id].get("username") != username:
        cortex.crm_data[user_id]["username"] = username # Обновляем ник, если изменился
    
    cortex.crm_data[user_id]["last_contact_ts"] = int(time.time())
    return cortex.crm_data[user_id]

def update_order_in_crm(cortex: Cortex, order_id: str, buyer_id: int, buyer_username: str, status: OrderStatuses):
    """Обновляет или добавляет информацию о заказе в CRM-профиле клиента."""
    customer = get_or_create_customer(cortex, buyer_id, buyer_username)
    
    # Удаляем заказ из всех списков, чтобы избежать дублирования
    for status_list in ['purchases', 'refunds', 'pending']:
        if order_id in customer.get(status_list, []):
            customer[status_list].remove(order_id)
            
    # Добавляем в нужный список в зависимости от статуса
    if status == OrderStatuses.CLOSED:
        if order_id not in customer.get('purchases', []): customer.setdefault('purchases', []).append(order_id)
    elif status == OrderStatuses.REFUNDED:
        if order_id not in customer.get('refunds', []): customer.setdefault('refunds', []).append(order_id)
    elif status == OrderStatuses.PAID:
        if order_id not in customer.get('pending', []): customer.setdefault('pending', []).append(order_id)

    save_crm_data(cortex)

def crm_initial_scan(cortex: Cortex):
    """Выполняет первичное сканирование всей истории продаж для заполнения CRM."""
    if cortex.crm_data:
        logger.info("CRM данные уже существуют, первичное сканирование пропущено.")
        return

    logger.info("CRM-база пуста. Начинаю первичное сканирование истории продаж...")
    if cortex.telegram and list(cortex.telegram.authorized_users.keys()):
        try:
            cortex.telegram.bot.send_message(list(cortex.telegram.authorized_users.keys())[0],
                                             "📊 Начинаю первичное сканирование истории продаж для CRM. Это может занять некоторое время...")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление о начале сканирования CRM: {e}")

    next_order_id, batch, locale, subcs = cortex.account.get_sales()
    total_processed = 0
    while True:
        if not batch:
            break
        for sale in batch:
            update_order_in_crm(cortex, sale.id, sale.buyer_id, sale.buyer_username, sale.status)
            total_processed += 1
        if not next_order_id:
            break
        time.sleep(1)
        next_order_id, batch, _, _ = cortex.account.get_sales(start_from=next_order_id, locale=locale, sudcategories=subcs)

    save_crm_data(cortex)
    logger.info(f"Первичное сканирование CRM завершено. Обработано {total_processed} заказов.")
    if cortex.telegram and list(cortex.telegram.authorized_users.keys()):
        try:
            cortex.telegram.bot.send_message(list(cortex.telegram.authorized_users.keys())[0],
                                             f"✅ Сканирование CRM завершено. Загружена информация о {total_processed} заказах.")
        except Exception as e:
            logger.warning(f"Не удалось отправить уведомление о завершении сканирования CRM: {e}")

def crm_initial_chat_hook(cortex: Cortex, event: InitialChatEvent):
    """Хук для создания профиля клиента при первом обнаружении чата."""
    interlocutor_id = cortex.account.interlocutor_ids.get(event.chat.id)
    if interlocutor_id:
        get_or_create_customer(cortex, interlocutor_id, event.chat.name)

def crm_new_order_hook(cortex: Cortex, event: NewOrderEvent):
    """Хук для добавления нового заказа в CRM."""
    update_order_in_crm(cortex, event.order.id, event.order.buyer_id, event.order.buyer_username, event.order.status)

def crm_order_status_hook(cortex: Cortex, event: OrderStatusChangedEvent):
    """Хук для отслеживания изменения статуса заказов."""
    update_order_in_crm(cortex, event.order.id, event.order.buyer_id, event.order.buyer_username, event.order.status)

def init_crm_cp(cortex: Cortex, *args):
    """Инициализация модуля CRM."""
    load_crm_data(cortex)
    # Запускаем первичное сканирование в отдельном потоке, чтобы не блокировать запуск
    Thread(target=crm_initial_scan, args=(cortex,), daemon=True).start()
    
    # Регистрация обработчиков Telegram (если они есть)
    # В текущей реализации вся логика работает через хуки, но здесь можно добавить команды, например, /customer_info <username>
    pass

BIND_TO_POST_INIT = [init_crm_cp]
BIND_TO_NEW_ORDER = [crm_new_order_hook]
BIND_TO_INIT_MESSAGE = [crm_initial_chat_hook]
BIND_TO_ORDER_STATUS_CHANGED = [crm_order_status_hook]