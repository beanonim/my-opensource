# Файл: FunPayCortex-main/tg_bot/keyboards.py

"""
Функции генерации клавиатур для суб-панелей управления.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from cortex import Cortex
    from FunPayAPI.types import MyLotShortcut, Category, SubCategory

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B

from tg_bot import CBT, MENU_CFG, utils
from tg_bot.utils import NotificationTypes, bool_to_text, add_navigation_buttons

import Utils.cortex_tools
from FunPayAPI.common.enums import SubCategoryTypes
from locales.localizer import Localizer

import logging
import random
import os
import math

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate


def power_off(instance_id: int, state: int) -> K:
    """
    Генерирует клавиатуру выключения бота (CBT.SHUT_DOWN:<state>:<instance_id>).

    :param instance_id: ID запуска бота.
    :param state: текущей этап клавиатуры.

    :return: объект клавиатуры выключения бота.
    """
    kb = K()
    if state == 0:
        kb.row(B(_("gl_yes"), callback_data=f"{CBT.SHUT_DOWN}:1:{instance_id}"),
               B(_("gl_no"), callback_data=CBT.CANCEL_SHUTTING_DOWN))
    elif state == 1:
        kb.row(B(_("gl_no"), callback_data=CBT.CANCEL_SHUTTING_DOWN),
               B(_("gl_yes"), callback_data=f"{CBT.SHUT_DOWN}:2:{instance_id}"))
    elif state == 2:
        yes_button_num = random.randint(1, 10)
        yes_button = B(_("gl_yes"), callback_data=f"{CBT.SHUT_DOWN}:3:{instance_id}")
        no_button = B(_("gl_no"), callback_data=CBT.CANCEL_SHUTTING_DOWN)
        buttons = [*[no_button] * (yes_button_num - 1), yes_button, *[no_button] * (10 - yes_button_num)]
        kb.add(*buttons, row_width=2)
    elif state == 3:
        yes_button_num = random.randint(1, 30)
        yes_button = B(_("gl_yes"), callback_data=f"{CBT.SHUT_DOWN}:4:{instance_id}")
        no_button = B(_("gl_no"), callback_data=CBT.CANCEL_SHUTTING_DOWN)
        buttons = [*[no_button] * (yes_button_num - 1), yes_button, *[no_button] * (30 - yes_button_num)]
        kb.add(*buttons, row_width=5)
    elif state == 4:
        yes_button_num = random.randint(1, 40)
        yes_button = B(_("gl_no"), callback_data=f"{CBT.SHUT_DOWN}:5:{instance_id}")
        no_button = B(_("gl_yes"), callback_data=CBT.CANCEL_SHUTTING_DOWN)
        buttons = [*[yes_button] * (yes_button_num - 1), no_button, *[yes_button] * (40 - yes_button_num)]
        kb.add(*buttons, row_width=7)
    elif state == 5:
        kb.add(B(_("gl_yep"), callback_data=f"{CBT.SHUT_DOWN}:6:{instance_id}"))
    return kb


def language_settings(c: Cortex) -> K:
    """
    Генерирует клавиатуру настроек языка (CBT.CATEGORY:lang).

    :param c: объект Cortex.
    :return: объект клавиатуры настроек языка.
    """
    lang = c.MAIN_CFG["Other"]["language"]
    langs = {
        "uk": "🇺🇦 Українська",
        "en": "🇺🇸 English",
        "ru": "🇷🇺 Русский"
    }

    kb = K()
    lang_buttons = []

    for i in langs:
        cb = f"{CBT.LANG}:{i}" if lang != i else CBT.EMPTY
        text = f"✅ {langs[i]}" if lang == i else langs[i]
        lang_buttons.append(B(text, callback_data=cb))
    kb.row(*lang_buttons)
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb


def main_settings(c: Cortex) -> K:
    """
    Генерирует клавиатуру основных переключателей (CBT.CATEGORY:main).

    :param c: объект Cortex.
    :return: объект клавиатуры основных переключателей.
    """
    p = f"{CBT.SWITCH}:FunPay"

    def l(s):
        return '🟢' if c.MAIN_CFG["FunPay"].getboolean(s) else '🔴'

    kb = K() \
        .row(B(_("gs_autoraise", l('autoRaise')), callback_data=f"{p}:autoRaise"),
             B(_("gs_autoresponse", l('autoResponse')), callback_data=f"{p}:autoResponse")) \
        .row(B(_("gs_autodelivery", l('autoDelivery')), callback_data=f"{p}:autoDelivery"),
             B(_("gs_nultidelivery", l('multiDelivery')), callback_data=f"{p}:multiDelivery")) \
        .row(B(_("gs_autorestore", l('autoRestore')), callback_data=f"{p}:autoRestore"),
             B(_("gs_autodisable", l('autoDisable')), callback_data=f"{p}:autoDisable")) \
        .row(B(_("gs_old_msg_mode", l('oldMsgGetMode')), callback_data=f"{p}:oldMsgGetMode"),
             B(f"❓", callback_data=f"{CBT.SEND_HELP}:old_mode_help")) \
        .add(B(_("gs_keep_sent_messages_unread", l('keepSentMessagesUnread')), callback_data=f"{p}:keepSentMessagesUnread")) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb


def new_message_view_settings(c: Cortex) -> K:
    """
    Генерирует клавиатуру настроек вида уведомлений о новых сообщениях (CBT.CATEGORY:newMessageView).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек вида уведомлений о новых сообщениях.
    """
    p = f"{CBT.SWITCH}:NewMessageView"

    def l(s):
        return '🟢' if c.MAIN_CFG["NewMessageView"].getboolean(s) else '🔴'

    kb = K() \
        .add(B(_("mv_incl_my_msg", l("includeMyMessages")), callback_data=f"{p}:includeMyMessages")) \
        .add(B(_("mv_incl_fp_msg", l("includeFPMessages")), callback_data=f"{p}:includeFPMessages")) \
        .add(B(_("mv_incl_bot_msg", l("includeBotMessages")), callback_data=f"{p}:includeBotMessages")) \
        .add(B(_("mv_only_my_msg", l("notifyOnlyMyMessages")), callback_data=f"{p}:notifyOnlyMyMessages")) \
        .add(B(_("mv_only_fp_msg", l("notifyOnlyFPMessages")), callback_data=f"{p}:notifyOnlyFPMessages")) \
        .add(B(_("mv_only_bot_msg", l("notifyOnlyBotMessages")), callback_data=f"{p}:notifyOnlyBotMessages")) \
        .add(B(_("mv_show_image_name", l("showImageName")), callback_data=f"{p}:showImageName")) \
        .row(B("❓", callback_data=f"{CBT.SEND_HELP}:help_new_message_view"), B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def greeting_settings(c: Cortex):
    """
    Генерирует клавиатуру настроек приветственного сообщения (CBT.CATEGORY:greetings).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек приветственного сообщения.
    """
    p = f"{CBT.SWITCH}:Greetings"

    def l(s):
        return '🟢' if c.MAIN_CFG["Greetings"].getboolean(s) else '🔴'

    cd = float(c.MAIN_CFG["Greetings"]["greetingsCooldown"])
    cd = int(cd) if int(cd) == cd else cd
    kb = K() \
        .add(B(_("gr_greetings", l("sendGreetings")), callback_data=f"{p}:sendGreetings")) \
        .add(B(_("gr_ignore_sys_msgs", l("ignoreSystemMessages")), callback_data=f"{p}:ignoreSystemMessages")) \
        .add(B(_("gr_edit_message"), callback_data=CBT.EDIT_GREETINGS_TEXT)) \
        .add(B(_("gr_edit_cooldown").format(cd), callback_data=CBT.EDIT_GREETINGS_COOLDOWN)) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def order_confirm_reply_settings(c: Cortex):
    """
    Генерирует клавиатуру настроек ответа на подтверждение заказа (CBT.CATEGORY:orderConfirm).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек ответа на подтверждение заказа.
    """
    kb = K() \
        .add(B(_("oc_send_reply", bool_to_text(int(c.MAIN_CFG['OrderConfirm']['sendReply']))),
               callback_data=f"{CBT.SWITCH}:OrderConfirm:sendReply")) \
        .add(B(_("oc_watermark", bool_to_text(int(c.MAIN_CFG['OrderConfirm']['watermark']))),
               callback_data=f"{CBT.SWITCH}:OrderConfirm:watermark")) \
        .add(B(_("oc_edit_message"), callback_data=CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT)) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def authorized_users(c: Cortex, offset: int, current_user_id: int):
    """
    Генерирует клавиатуру со списком авторизованных пользователей (CBT.AUTHORIZED_USERS:<offset>).
    :param c: объект Cortex.
    :param offset: смещение списка пользователей.
    :param current_user_id: ID пользователя, вызвавшего меню.
    :return: объект клавиатуры со списком пользователей.
    """
    kb = K()
    p = f"{CBT.SWITCH}:Telegram"
    user_role = utils.get_user_role(c.telegram.authorized_users, current_user_id)

    def l(s):
        return '🟢' if c.MAIN_CFG["Telegram"].getboolean(s) else '🔴'

    if user_role == "admin":
        kb.add(B(_("tg_block_login", l("blockLogin")), callback_data=f"{p}:blockLogin:{offset}"))

    users_dict = c.telegram.authorized_users
    sorted_users = sorted(users_dict.items(), key=lambda item: (item[1].get('role', 'z'), item[1].get('username', str(item[0])).lower()))
    
    users_on_page = sorted_users[offset: offset + MENU_CFG.AUTHORIZED_USERS_BTNS_AMOUNT]

    for user_id, user_info in users_on_page:
        username = user_info.get("username", f"ID: {user_id}")
        role = user_info.get("role")
        role_emoji = "👑" if role == 'admin' else '👤' if role == 'manager' else '❓'
        display_name = f"{role_emoji} {username}"
        kb.row(B(display_name, callback_data=f"{CBT.AUTHORIZED_USER_SETTINGS}:{user_id}:{offset}"))

    kb = add_navigation_buttons(kb, offset, MENU_CFG.AUTHORIZED_USERS_BTNS_AMOUNT, len(users_on_page),
                                len(sorted_users), CBT.AUTHORIZED_USERS)
    
    if user_role == "admin":
        kb.row(B(_("mm_manager_settings"), callback_data=CBT.MANAGER_SETTINGS),
               B(_("mm_manager_permissions"), callback_data=f"{CBT.CATEGORY}:mp"))

    kb.add(B(_("au_exit_cp"), callback_data=f"{CBT.EXIT_FROM_CP}:{current_user_id}:{offset}"))
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def authorized_user_settings(c: Cortex, user_id: int, offset: int, user_link: bool, current_user_id: int):
    """
    Генерирует клавиатуру с настройками пользователя (CBT.AUTHORIZED_USER_SETTINGS:<offset>).
    """
    kb = K()
    user_info = c.telegram.authorized_users.get(user_id, {})
    username = user_info.get("username", str(user_id))
    user_role = user_info.get("role")
    current_user_role = utils.get_user_role(c.telegram.authorized_users, current_user_id)

    if user_link:
        kb.add(B(f"👤 {username}", url=f"tg:user?id={user_id}"))
    else:
        kb.add(B(f"👤 {username}", callback_data=CBT.EMPTY))
    
    if current_user_role == 'admin' and current_user_id != user_id:
        if user_role == 'manager':
            kb.add(B(_("promote_to_admin"), callback_data=f"{CBT.CHANGE_USER_ROLE}:{user_id}:{offset}:admin"))
        elif user_role == 'admin':
            admins = [uid for uid, uinfo in c.telegram.authorized_users.items() if uinfo.get("role") == "admin"]
            if len(admins) > 1: # Нельзя понизить последнего админа
                kb.add(B(_("demote_to_manager"), callback_data=f"{CBT.CHANGE_USER_ROLE}:{user_id}:{offset}:manager"))
        
        kb.add(B(_("revoke_access"), callback_data=f"{CBT.REVOKE_USER_ACCESS}:{user_id}:{offset}"))

    kb.add(B(_("gl_back"), callback_data=f"{CBT.AUTHORIZED_USERS}:{offset}"))
    return kb


def proxy(c: Cortex, offset: int, proxies: dict[str, bool]):
    """
    Генерирует клавиатуру со списком прокси (CBT.PROXY:<offset>).
    :param c: объект Cortex.
    :param offset: смещение списка прокси.
    :param proxies: {прокси: валидность прокси}.
    :return: объект клавиатуры со списком прокси.
    """
    kb = K()
    ps = list(c.proxy_dict.items())[offset: offset + MENU_CFG.PROXY_BTNS_AMOUNT]
    ip, port = c.MAIN_CFG["Proxy"]["ip"], c.MAIN_CFG["Proxy"]["port"]
    login, password = c.MAIN_CFG["Proxy"]["login"], c.MAIN_CFG["Proxy"]["password"]
    current_proxy_str = f"{f'{login}:{password}@' if login and password else ''}{ip}:{port}"
    
    kb.row(
        B(f"🌐 Прокси: {bool_to_text(c.MAIN_CFG['Proxy'].getboolean('enable'))}", callback_data=f"{CBT.SWITCH}:Proxy:enable:{offset}"),
        B(f"🚦 Проверка: {bool_to_text(c.MAIN_CFG['Proxy'].getboolean('check'))}", callback_data=f"{CBT.SWITCH}:Proxy:check:{offset}")
    )
    kb.row(B("─" * 15, callback_data=CBT.EMPTY))

    for proxy_internal_id, proxy_string_value in ps:
        status_emoji = "🟢" if proxies.get(proxy_string_value) else "🟡" if proxies.get(proxy_string_value) is None else "🔴"
        is_current = proxy_string_value == current_proxy_str and c.MAIN_CFG["Proxy"].getboolean("enable")
        
        display_text = f"{status_emoji} {proxy_string_value}"
        if is_current:
            display_text = f"✅ {display_text}"
            action_button_cb = CBT.EMPTY
        else:
            action_button_cb = f"{CBT.CHOOSE_PROXY}:{offset}:{proxy_internal_id}"
        
        kb.row(
            B(display_text, callback_data=action_button_cb),
            B("🗑️", callback_data=f"{CBT.DELETE_PROXY}:{offset}:{proxy_internal_id}")
        )

    kb = add_navigation_buttons(kb, offset, MENU_CFG.PROXY_BTNS_AMOUNT, len(ps),
                                len(c.proxy_dict.items()), CBT.PROXY)
    kb.row(B(_("prx_proxy_add"), callback_data=f"{CBT.ADD_PROXY}:{offset}"))
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def review_reply_settings(c: Cortex):
    """
    Генерирует клавиатуру настроек ответа на отзыв (CBT.CATEGORY:reviewReply).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек ответа на отзыв.
    """
    kb = K()
    kb.add(B("📝 Редактировать ответы на отзывы", callback_data=CBT.EMPTY))
    for i in range(1, 6):
        stars_text = '⭐' * i
        reply_enabled_text = bool_to_text(int(c.MAIN_CFG['ReviewReply'][f'star{i}Reply']))
        reply_set_icon = "✏️" if c.MAIN_CFG['ReviewReply'][f'star{i}ReplyText'] else "➕"

        kb.row(
            B(f"{stars_text} Ответ: {reply_enabled_text}", callback_data=f"{CBT.SWITCH}:ReviewReply:star{i}Reply"),
            B(f"{reply_set_icon} Текст", callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{i}")
        )
        current_reply = c.MAIN_CFG['ReviewReply'][f'star{i}ReplyText']
        if current_reply:
            kb.add(B(f"↳ «{current_reply[:20]}...»", callback_data=f"{CBT.SEND_REVIEW_REPLY_TEXT}:{i}"))
        else:
            kb.add(B("↳ (Ответ не задан)", callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{i}"))

    kb.add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def notifications_settings(c: Cortex, chat_id: int) -> K:
    """
    Генерирует клавиатуру настроек уведомлений (CBT.CATEGORY:telegram).
    :param c: объект Cortex.
    :param chat_id: ID чата, в котором вызвана клавиатура.
    :return: объект клавиатуры настроек уведомлений.
    """
    p = f"{CBT.SWITCH_TG_NOTIFICATIONS}:{chat_id}"
    n = NotificationTypes

    def l(nt):
        return '🔔' if c.telegram.is_notification_enabled(chat_id, nt) else '🔕'

    kb = K() \
        .row(B(_("ns_new_msg", l(n.new_message)), callback_data=f"{p}:{n.new_message}"),
             B(_("ns_cmd", l(n.command)), callback_data=f"{p}:{n.command}")) \
        .row(B(_("ns_new_order", l(n.new_order)), callback_data=f"{p}:{n.new_order}"),
             B(_("ns_order_confirmed", l(n.order_confirmed)), callback_data=f"{p}:{n.order_confirmed}")) \
        .row(B(_("ns_lot_activate", l(n.lots_restore)), callback_data=f"{p}:{n.lots_restore}"),
             B(_("ns_lot_deactivate", l(n.lots_deactivate)), callback_data=f"{p}:{n.lots_deactivate}")) \
        .row(B(_("ns_delivery", l(n.delivery)), callback_data=f"{p}:{n.delivery}"),
             B(_("ns_raise", l(n.lots_raise)), callback_data=f"{p}:{n.lots_raise}")) \
        .add(B(_("ns_new_review", l(n.review)), callback_data=f"{p}:{n.review}")) \
        .add(B(_("ns_bot_start", l(n.bot_start)), callback_data=f"{p}:{n.bot_start}")) \
        .add(B(_("ns_other", l(n.other)), callback_data=f"{p}:{n.other}")) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb


def announcements_settings(c: Cortex, chat_id: int):
    """
    Генерирует клавиатуру настроек уведомлений объявлений.
    :param c: объект Cortex.
    :param chat_id: ID чата, в котором вызвана клавиатура.
    :return: объект клавиатуры настроек уведомлений объявлений.
    """
    p = f"{CBT.SWITCH_TG_NOTIFICATIONS}:{chat_id}"
    n = NotificationTypes

    def l(nt):
        return '🔔' if c.telegram.is_notification_enabled(chat_id, nt) else '🔕'

    kb = K() \
        .add(B(_("an_an", l(n.announcement)), callback_data=f"{p}:{n.announcement}")) \
        .add(B(_("an_ad", l(n.ad)), callback_data=f"{p}:{n.ad}"))
    return kb


def blacklist_settings(c: Cortex) -> K:
    """
    Генерирует клавиатуру настроек черного списка (CBT.CATEGORY:blockList).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек черного списка.
    """
    p = f"{CBT.SWITCH}:BlockList"

    def l(s):
        return '🟢' if c.MAIN_CFG["BlockList"].getboolean(s) else '🔴'

    kb = K() \
        .add(B(_("bl_autodelivery", l("blockDelivery")), callback_data=f"{p}:blockDelivery")) \
        .add(B(_("bl_autoresponse", l("blockResponse")), callback_data=f"{p}:blockResponse")) \
        .add(B(_("bl_new_msg_notifications", l("blockNewMessageNotification")), callback_data=f"{p}:blockNewMessageNotification")) \
        .add(B(_("bl_new_order_notifications", l("blockNewOrderNotification")), callback_data=f"{p}:blockNewOrderNotification")) \
        .add(B(_("bl_command_notifications", l("blockCommandNotification")), callback_data=f"{p}:blockCommandNotification")) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb

def manager_permissions_settings(c: Cortex) -> K:
    """
    Генерирует клавиатуру настроек прав менеджеров (CBT.CATEGORY:mp).
    :param c: объект Cortex.
    :return: объект клавиатуры настроек прав менеджеров.
    """
    p = f"{CBT.SWITCH}:ManagerPermissions"
    
    def l(s):
        return '🟢' if c.MAIN_CFG["ManagerPermissions"].getboolean(s, fallback=False) else '🔴'

    kb = K() \
        .add(B(_("mp_can_view_stats", l("can_view_stats")), callback_data=f"{p}:can_view_stats")) \
        .add(B(_("mp_can_edit_ar", l("can_edit_ar")), callback_data=f"{p}:can_edit_ar")) \
        .add(B(_("mp_can_edit_ad", l("can_edit_ad")), callback_data=f"{p}:can_edit_ad")) \
        .add(B(_("mp_can_edit_templates", l("can_edit_templates")), callback_data=f"{p}:can_edit_templates")) \
        .add(B(_("mp_can_control_orders", l("can_control_orders")), callback_data=f"{p}:can_control_orders")) \
        .row(B("❓", callback_data=f"{CBT.SEND_HELP}:help_manager_permissions"), B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb


def commands_list(c: Cortex, offset: int) -> K:
    """
    Генерирует клавиатуру со списком команд (CBT.CMD_LIST:<offset>).
    :param c: объект Cortex.
    :param offset: смещение списка команд.
    :return: объект клавиатуры со списком команд.
    """
    kb = K()
    commands = c.RAW_AR_CFG.sections()[offset: offset + MENU_CFG.AR_BTNS_AMOUNT]
    if not commands and offset != 0:
        offset = 0
        commands = c.RAW_AR_CFG.sections()[offset: offset + MENU_CFG.AR_BTNS_AMOUNT]

    if not commands and offset == 0:
        kb.add(B("🤖 Пока нет ни одной команды", callback_data=CBT.EMPTY))
    else:
        for index, cmd_raw_text in enumerate(commands):
            cmd_display = cmd_raw_text.split("|")[0].strip()
            if "|" in cmd_raw_text:
                cmd_display += " | ..."
            kb.add(B(f"💬 {cmd_display}", callback_data=f"{CBT.EDIT_CMD}:{offset + index}:{offset}"))

    kb = add_navigation_buttons(kb, offset, MENU_CFG.AR_BTNS_AMOUNT, len(commands), len(c.RAW_AR_CFG.sections()),
                                CBT.CMD_LIST)

    kb.add(B(_("ar_to_ar"), callback_data=f"{CBT.CATEGORY}:ar"))
    kb.add(B(_("ar_to_mm"), callback_data=CBT.MAIN))
    return kb


def edit_command(c: Cortex, command_index: int, offset: int) -> K:
    """
    Генерирует клавиатуру изменения параметров команды (CBT.EDIT_CMD:<command_num>:<offset>).
    :param c: объект Cortex.
    :param command_index: номер команды.
    :param offset: смещение списка команд.
    :return объект клавиатуры изменения параметров команды.
    """
    command_raw_text = c.RAW_AR_CFG.sections()[command_index]
    command_obj = c.RAW_AR_CFG[command_raw_text]
    notif_status = bool_to_text(command_obj.get('telegramNotification'), '🔔', '🔕')

    kb = K() \
        .add(B(_("ar_edit_response"), callback_data=f"{CBT.EDIT_CMD_RESPONSE_TEXT}:{command_index}:{offset}")) \
        .add(B(_("ar_edit_notification"), callback_data=f"{CBT.EDIT_CMD_NOTIFICATION_TEXT}:{command_index}:{offset}")) \
        .add(B(_("ar_notification", notif_status),
               callback_data=f"{CBT.SWITCH_CMD_NOTIFICATION}:{command_index}:{offset}")) \
        .add(B(_("gl_delete"), callback_data=f"{CBT.DEL_CMD}:{command_index}:{offset}")) \
        .row(B(_("gl_back"), callback_data=f"{CBT.CMD_LIST}:{offset}"),
             B(_("gl_refresh"), callback_data=f"{CBT.EDIT_CMD}:{command_index}:{offset}"))
    return kb


def products_files_list(offset: int) -> K:
    """
    Генерирует клавиатуру со списком товарных файлов (CBT.PRODUCTS_FILES_LIST:<offset>).
    :param offset: смещение списка товарных файлов.
    :return: объект клавиатуры со списком товарных файлов.
    """
    keyboard = K()
    products_dir = "storage/products"
    if not os.path.exists(products_dir):
        os.makedirs(products_dir)
        
    all_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")])
    
    files_on_page = all_files[offset:offset + MENU_CFG.PF_BTNS_AMOUNT]
    if not files_on_page and offset != 0:
        offset = 0
        files_on_page = all_files[offset:offset + MENU_CFG.PF_BTNS_AMOUNT]

    if not files_on_page and offset == 0:
        keyboard.add(B("📂 Пока нет файлов с товарами", callback_data=CBT.EMPTY))
    else:
        for index, name in enumerate(files_on_page):
            try:
                amount = Utils.cortex_tools.count_products(os.path.join(products_dir, name))
            except Exception:
                amount = "⚠️" 
            keyboard.add(B(f"📄 {name} ({amount} {_('gl_pcs')})", callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{all_files.index(name)}:{offset}"))

    keyboard = add_navigation_buttons(keyboard, offset, MENU_CFG.PF_BTNS_AMOUNT, len(files_on_page),
                                      len(all_files), CBT.PRODUCTS_FILES_LIST)

    keyboard.add(B(_("ad_to_ad"), callback_data=f"{CBT.CATEGORY}:ad"))
    keyboard.add(B(_("ad_to_mm"), callback_data=CBT.MAIN))
    return keyboard


def products_file_edit(file_number: int, offset: int, confirmation: bool = False) \
        -> K:
    """
    Генерирует клавиатуру изменения товарного файла (CBT.EDIT_PRODUCTS_FILE:<file_index>:<offset>).
    :param file_number: порядковый номер файла в отсортированном списке.
    :param offset: смещение списка товарных файлов.
    :param confirmation: включить ли в клавиатуру подтверждение удаления файла.
    :return: объект клавиатуры изменения товарного файла.
    """
    keyboard = K() \
        .add(B(_("gf_add_goods"), callback_data=f"{CBT.ADD_PRODUCTS_TO_FILE}:{file_number}:{file_number}:{offset}:0")) \
        .add(B(_("gf_download"), callback_data=f"download_products_file:{file_number}:{offset}"))
    if not confirmation:
        keyboard.add(B(_("gl_delete"), callback_data=f"del_products_file:{file_number}:{offset}"))
    else:
        keyboard.row(B(_("gl_yes") + " " + _("gl_delete"), callback_data=f"confirm_del_products_file:{file_number}:{offset}"),
                     B(_("gl_no") + " " + _("ord_dont_refund"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_number}:{offset}"))
    keyboard.row(B(_("gl_back"), callback_data=f"{CBT.PRODUCTS_FILES_LIST}:{offset}"),
                 B(_("gl_refresh"), callback_data=f"{CBT.EDIT_PRODUCTS_FILE}:{file_number}:{offset}"))
    return keyboard


def lots_list(cortex_instance: Cortex, offset: int) -> K:
    """
    Создает клавиатуру со списком лотов с автовыдачей. (lots:<offset>).
    :param cortex_instance: объект Cortex.
    :param offset: смещение списка лотов.
    :return: объект клавиатуры со списком лотов с автовыдачей.
    """
    keyboard = K()
    all_lots = cortex_instance.AD_CFG.sections()
    lots_on_page = all_lots[offset: offset + MENU_CFG.AD_BTNS_AMOUNT]
    if not lots_on_page and offset != 0:
        offset = 0
        lots_on_page = all_lots[offset: offset + MENU_CFG.AD_BTNS_AMOUNT]

    if not lots_on_page and offset == 0:
        keyboard.add(B("🧾 Пока нет лотов с автовыдачей", callback_data=CBT.EMPTY))
    else:
        for index, lot_name in enumerate(lots_on_page):
            keyboard.add(B(f"📦 {lot_name}", callback_data=f"{CBT.EDIT_AD_LOT}:{all_lots.index(lot_name)}:{offset}"))

    keyboard = add_navigation_buttons(keyboard, offset, MENU_CFG.AD_BTNS_AMOUNT, len(lots_on_page),
                                      len(all_lots), CBT.AD_LOTS_LIST)

    keyboard.add(B(_("ad_to_ad"), callback_data=f"{CBT.CATEGORY}:ad"))
    keyboard.add(B(_("ad_to_mm"), callback_data=CBT.MAIN))
    return keyboard


def edit_lot(c: Cortex, lot_number: int, offset: int) -> K:
    """
    Генерирует клавиатуру изменения лота (CBT.EDIT_AD_LOT:<lot_num>:<offset>).
    :param c: экземпляр Cortex.
    :param lot_number: номер лота в списке AD_CFG.sections().
    :param offset: смещение списка слотов для кнопки "Назад".
    :return: объект клавиатуры изменения лота.
    """
    all_ad_lots = c.AD_CFG.sections()
    if lot_number >= len(all_ad_lots):
        return lots_list(c, offset)
        
    lot_name = all_ad_lots[lot_number]
    lot_obj = c.AD_CFG[lot_name]
    file_name = lot_obj.get("productsFileName")
    kb = K() \
        .add(B(_("ea_edit_delivery_text"), callback_data=f"{CBT.EDIT_LOT_DELIVERY_TEXT}:{lot_number}:{offset}"))
    
    products_dir = "storage/products"
    link_file_text = _("ea_link_goods_file")
    add_goods_text = _("gf_add_goods")

    if not file_name:
        kb.add(B(link_file_text, callback_data=f"{CBT.BIND_PRODUCTS_FILE}:{lot_number}:{offset}"))
    else:
        all_storage_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")]) if os.path.exists(products_dir) else []
        file_exists_in_storage = file_name in all_storage_files
        
        if not file_exists_in_storage:
            if not os.path.exists(products_dir): os.makedirs(products_dir)
            with open(os.path.join(products_dir, file_name), "w", encoding="utf-8"): pass
            all_storage_files = sorted([f for f in os.listdir(products_dir) if f.endswith(".txt")])
            
        file_index_in_storage = all_storage_files.index(file_name) if file_name in all_storage_files else -1

        if file_index_in_storage != -1:
            kb.row(B(f"{link_file_text} («{file_name}»)", callback_data=f"{CBT.BIND_PRODUCTS_FILE}:{lot_number}:{offset}"),
                   B(add_goods_text, callback_data=f"{CBT.ADD_PRODUCTS_TO_FILE}:{file_index_in_storage}:{lot_number}:{offset}:1"))
        else:
            kb.add(B(f"{link_file_text} (⚠️ {file_name} - не найден!)", callback_data=f"{CBT.BIND_PRODUCTS_FILE}:{lot_number}:{offset}"))

    p = {
        "ad": (c.MAIN_CFG["FunPay"].getboolean("autoDelivery"), "disable"),
        "md": (c.MAIN_CFG["FunPay"].getboolean("multiDelivery"), "disableMultiDelivery"),
        "ares": (c.MAIN_CFG["FunPay"].getboolean("autoRestore"), "disableAutoRestore"),
        "adis": (c.MAIN_CFG["FunPay"].getboolean("autoDisable"), "disableAutoDisable"),
    }
    info_cb_part, switch_lot_cb_prefix, param_disabled_cb = f"{lot_number}:{offset}", "switch_lot", CBT.PARAM_DISABLED

    def get_status_emoji(setting_key_short: str):
        global_enabled, local_option_name = p[setting_key_short]
        if not global_enabled: return '⚪'
        return '🔴' if lot_obj.getboolean(local_option_name, False) else '🟢'

    kb.row(B(_("ea_delivery", get_status_emoji("ad")), callback_data=f"{f'{switch_lot_cb_prefix}:disable:{info_cb_part}' if p['ad'][0] else param_disabled_cb}"),
           B(_("ea_multidelivery", get_status_emoji("md")), callback_data=f"{f'{switch_lot_cb_prefix}:disableMultiDelivery:{info_cb_part}' if p['md'][0] else param_disabled_cb}")) \
        .row(B(_("ea_restore", get_status_emoji("ares")), callback_data=f"{f'{switch_lot_cb_prefix}:disableAutoRestore:{info_cb_part}' if p['ares'][0] else param_disabled_cb}"),
             B(_("ea_deactivate", get_status_emoji("adis")), callback_data=f"{f'{switch_lot_cb_prefix}:disableAutoDisable:{info_cb_part}' if p['adis'][0] else param_disabled_cb}")) \
        .row(B(_("ea_test"), callback_data=f"test_auto_delivery:{info_cb_part}"),
             B(_("gl_delete"), callback_data=f"{CBT.DEL_AD_LOT}:{info_cb_part}")) \
        .row(B(_("gl_back"), callback_data=f"{CBT.AD_LOTS_LIST}:{offset}"),
             B(_("gl_refresh"), callback_data=f"{CBT.EDIT_AD_LOT}:{info_cb_part}"))
    return kb


def new_order(order_id: str, username: str, node_id: int,
              confirmation: bool = False, no_refund: bool = False, cortex: Cortex | None = None) -> K:
    """
    Генерирует клавиатуру для сообщения о новом заказе.
    :param order_id: ID заказа (без #).
    :param username: никнейм покупателя.
    :param node_id: ID чата с покупателем.
    :param confirmation: заменить ли кнопку "Вернуть деньги" на подтверждение "Да" / "Нет"?
    :param no_refund: убрать ли кнопки, связанные с возвратом денег?
    :param cortex: экземпляр Cortex для проверки статуса подтверждения.
    :return: объект клавиатуры для сообщения о новом заказе.
    """
    kb = K()

    if cortex and cortex.MAIN_CFG["OrderControl"].getboolean("notify_pending_confirmation", False):
        if not cortex.order_confirmations.get(order_id, {}).get("confirmed_ts"):
            kb.add(B("✅ " + _("oc_mark_as_delivered_btn"), callback_data=f"{CBT.MARK_ORDER_DELIVERED}:{order_id}"))

    if not no_refund:
        if confirmation:
            kb.row(B(_("gl_yes") + " " + _("ord_refund"), callback_data=f"{CBT.REFUND_CONFIRMED}:{order_id}:{node_id}:{username}"),
                   B(_("gl_no") + " " + _("ord_dont_refund"), callback_data=f"{CBT.REFUND_CANCELLED}:{order_id}:{node_id}:{username}"))
        else:
            kb.add(B(_("ord_refund"), callback_data=f"{CBT.REQUEST_REFUND}:{order_id}:{node_id}:{username}"))

    kb.row(B(_("ord_answer"), callback_data=f"{CBT.SEND_FP_MESSAGE}:{node_id}:{username}"),
           B(_("ord_templates"), callback_data=
             f"{CBT.TMPLT_LIST_ANS_MODE}:0:{node_id}:{username}:2:{order_id}:{1 if no_refund else 0}"))
    return kb


def reply(node_id: int, username: str, again: bool = False, extend: bool = False) -> K:
    """
    Генерирует клавиатуру для отправки сообщения в чат FunPay.
    :param node_id: ID переписки, в которую нужно отправить сообщение.
    :param username: никнейм пользователя, с которым ведется переписка.
    :param again: заменить текст "Отправить" на "Отправить еще"?
    :param extend: добавить ли кнопку "Расширить"?
    :return: объект клавиатуры для отправки сообщения в чат FunPay.
    """
    buttons = [
        B(_("msg_reply2") if again else _("msg_reply"), callback_data=f"{CBT.SEND_FP_MESSAGE}:{node_id}:{username}"),
        B(_("msg_templates"), callback_data=f"{CBT.TMPLT_LIST_ANS_MODE}:0:{node_id}:{username}:{int(again)}:{int(extend)}")
    ]
    if extend:
        buttons.append(B(_("msg_more"), callback_data=f"{CBT.EXTEND_CHAT}:{node_id}:{username}"))
    
    buttons.append(B(f"💬 FunPay: {username}", url=f"https://funpay.com/chat/?node={node_id}"))
    
    kb = K(row_width=2)
    kb.add(*buttons)
    return kb


def templates_list(c: Cortex, offset: int) -> K:
    """
    Генерирует клавиатуру со списком шаблонов ответов. (CBT.TMPLT_LIST:<offset>).
    :param c: экземпляр Cortex.
    :param offset: смещение списка шаблонов.
    :return: объект клавиатуры со списком шаблонов ответов.
    """
    kb = K()
    all_templates = c.telegram.answer_templates
    templates_on_page = all_templates[offset: offset + MENU_CFG.TMPLT_BTNS_AMOUNT]
    if not templates_on_page and offset != 0:
        offset = 0
        templates_on_page = all_templates[offset: offset + MENU_CFG.TMPLT_BTNS_AMOUNT]

    if not templates_on_page and offset == 0:
        kb.add(B("📝 Пока нет ни одного шаблона", callback_data=CBT.EMPTY))
    else:
        for index, tmplt_text in enumerate(templates_on_page):
            display_text = tmplt_text[:30] + "..." if len(tmplt_text) > 30 else tmplt_text
            kb.add(B(f"📄 {display_text}", callback_data=f"{CBT.EDIT_TMPLT}:{all_templates.index(tmplt_text)}:{offset}"))

    kb = add_navigation_buttons(kb, offset, MENU_CFG.TMPLT_BTNS_AMOUNT, len(templates_on_page),
                                len(all_templates), CBT.TMPLT_LIST)
    kb.add(B(_("tmplt_add"), callback_data=f"{CBT.ADD_TMPLT}:{offset}"))
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb


def edit_template(c: Cortex, template_index: int, offset: int) -> K:
    """
    Генерирует клавиатуру изменения шаблона ответа (CBT.EDIT_TMPLT:<template_index>:<offset>).
    :param c: экземпляр Cortex.
    :param template_index: числовой индекс шаблона ответа.
    :param offset: смещение списка шаблонов ответа.
    :return: объект клавиатуры изменения шаблона ответа.
    """
    kb = K() \
        .add(B(_("gl_delete"), callback_data=f"{CBT.DEL_TMPLT}:{template_index}:{offset}")) \
        .add(B(_("gl_back"), callback_data=f"{CBT.TMPLT_LIST}:{offset}"))
    return kb


def templates_list_ans_mode(c: Cortex, offset: int, node_id: int, username: str, prev_page: int,
                            extra: list | None = None):
    """
    Генерирует клавиатуру со списком шаблонов ответов для быстрого ответа.
    (CBT.TMPLT_LIST_ANS_MODE:{offset}:{node_id}:{username}:{prev_page}:{extra}).
    :param c: объект Cortex.
    :param offset: смещение списка шаблонов ответа.
    :param node_id: ID чата, в который нужно отправить шаблон.
    :param username: никнейм пользователя, с которым ведется переписка.
    :param prev_page: предыдущая страница (для кнопки "Назад").
    :param extra: доп данные для пред. страницы.
    :return: объект клавиатуры со списком шаблонов ответов.
    """
    kb = K()
    all_templates = c.telegram.answer_templates
    templates_on_page = all_templates[offset: offset + MENU_CFG.TMPLT_BTNS_AMOUNT]
    extra_str = (":" + ":".join(str(i) for i in extra)) if extra else ""

    if not templates_on_page and offset != 0:
        offset = 0
        templates_on_page = all_templates[offset: offset + MENU_CFG.TMPLT_BTNS_AMOUNT]

    if not templates_on_page and offset == 0:
        kb.add(B("📝 Шаблонов для ответа нет", callback_data=CBT.EMPTY))
    else:
        for index, tmplt_text in enumerate(templates_on_page):
            display_text = tmplt_text.replace("$username", username)
            display_text = display_text[:30] + "..." if len(display_text) > 30 else display_text
            kb.add(B(f"💬 {display_text}",
                     callback_data=f"{CBT.SEND_TMPLT}:{all_templates.index(tmplt_text)}:{node_id}:{username}:{prev_page}{extra_str}"))

    extra_list_for_nav = [node_id, username, prev_page]
    if extra:
        extra_list_for_nav.extend(extra)
    kb = add_navigation_buttons(kb, offset, MENU_CFG.TMPLT_BTNS_AMOUNT, len(templates_on_page),
                                len(all_templates), CBT.TMPLT_LIST_ANS_MODE,
                                extra_list_for_nav)

    back_cb_data = f"{CBT.BACK_TO_REPLY_KB}:{node_id}:{username}:0{extra_str}"
    if prev_page == 1:
        back_cb_data = f"{CBT.BACK_TO_REPLY_KB}:{node_id}:{username}:1{extra_str}"
    elif prev_page == 2:
        back_cb_data = f"{CBT.BACK_TO_ORDER_KB}:{node_id}:{username}{extra_str}"
    kb.add(B(_("gl_back"), callback_data=back_cb_data))
    return kb


def plugins_list(c: Cortex, offset: int):
    """
    Генерирует клавиатуру со списком плагинов (CBT.PLUGINS_LIST:<offset>).
    :param c: объект Cortex.
    :param offset: смещение списка плагинов.
    :return: объект клавиатуры со списком плагинов.
    """
    kb = K()
    sorted_plugin_uuids = sorted(c.plugins.keys(), key=lambda x_uuid: c.plugins[x_uuid].name.lower())
    
    plugins_on_page = sorted_plugin_uuids[offset: offset + MENU_CFG.PLUGINS_BTNS_AMOUNT]
    if not plugins_on_page and offset != 0:
        offset = 0
        plugins_on_page = sorted_plugin_uuids[offset: offset + MENU_CFG.PLUGINS_BTNS_AMOUNT]

    if not plugins_on_page and offset == 0:
        kb.add(B("🧩 Плагинов пока нет", callback_data=CBT.EMPTY))
    else:
        for uuid in plugins_on_page:
            plugin_obj = c.plugins[uuid]
            status_emoji = '🚀' if plugin_obj.enabled else '💤'
            kb.add(B(f"{status_emoji} {plugin_obj.name} v{plugin_obj.version}",
                     callback_data=f"{CBT.EDIT_PLUGIN}:{uuid}:{offset}"))

    kb = add_navigation_buttons(kb, offset, MENU_CFG.PLUGINS_BTNS_AMOUNT, len(plugins_on_page),
                                len(sorted_plugin_uuids), CBT.PLUGINS_LIST)

    kb.add(B(_("pl_add"), callback_data=f"{CBT.UPLOAD_PLUGIN}:{offset}"))
    kb.add(B(_("gl_back"), callback_data=CBT.MAIN))
    return kb


def edit_plugin(c: Cortex, uuid: str, offset: int, ask_to_delete: bool = False):
    """
    Генерирует клавиатуру управления плагином.
    :param c: объект Cortex.
    :param uuid: UUID плагина.
    :param offset: смещение списка плагинов.
    :param ask_to_delete: вставить ли подтверждение удаления плагина?
    :return: объект клавиатуры управления плагином.
    """
    plugin_obj = c.plugins[uuid]
    kb = K()
    active_text = _("pl_deactivate") if plugin_obj.enabled else _("pl_activate")
    kb.add(B(active_text, callback_data=f"{CBT.TOGGLE_PLUGIN}:{uuid}:{offset}"))

    if plugin_obj.commands:
        kb.add(B(_("pl_commands"), callback_data=f"{CBT.PLUGIN_COMMANDS}:{uuid}:{offset}"))
    if plugin_obj.settings_page:
        kb.add(B(_("pl_settings"), callback_data=f"{CBT.PLUGIN_SETTINGS}:{uuid}:{offset}"))

    if not ask_to_delete:
        kb.add(B(_("gl_delete"), callback_data=f"{CBT.DELETE_PLUGIN}:{uuid}:{offset}"))
    else:
        kb.row(B(_("gl_yes") + " " + _("gl_delete"), callback_data=f"{CBT.CONFIRM_DELETE_PLUGIN}:{uuid}:{offset}"),
               B(_("gl_no") + " " + _("ord_dont_refund"), callback_data=f"{CBT.CANCEL_DELETE_PLUGIN}:{uuid}:{offset}"))
    kb.add(B(_("gl_back"), callback_data=f"{CBT.PLUGINS_LIST}:{offset}"))
    return kb


def LINKS_KB(language: None | str = None) -> K:
    return K()
    
    
def statistics_menu(c: Cortex) -> K:
    """
    Генерирует клавиатуру для меню статистики.
    """
    kb = K(row_width=2)
    buttons = [
        B("За день", callback_data=f"{CBT.STATS_MENU}:day"),
        B("За неделю", callback_data=f"{CBT.STATS_MENU}:week"),
        B("За месяц", callback_data=f"{CBT.STATS_MENU}:month"),
        B("За все время", callback_data=f"{CBT.STATS_MENU}:all")
    ]
    kb.add(*buttons)
    kb.row(
        B(_("gl_back"), callback_data=CBT.MAIN),
        B(_("gl_configure"), callback_data=f"{CBT.STATS_CONFIG_MENU}:main"),
        B(_("gl_refresh"), callback_data=f"{CBT.STATS_MENU}:main")
    )
    return kb

def statistics_config_menu(c: Cortex) -> K:
    """
    Генерирует клавиатуру для настроек статистики.
    """
    kb = K()
    report_interval = c.MAIN_CFG["Statistics"].getint("report_interval", 0)
    analysis_period = c.MAIN_CFG["Statistics"].getint("analysis_period", 30)

    report_text = f"Авто-отчет: {'🟢' if report_interval > 0 else '🔴'} ({report_interval} ч.)"
    kb.add(B(report_text, callback_data=f"{CBT.STATS_CONFIG_MENU}:set_interval"))

    period_text = f"Период анализа: {analysis_period} дн."
    kb.add(B(period_text, callback_data=f"{CBT.STATS_CONFIG_MENU}:set_period"))

    kb.add(B(_("gl_back"), callback_data=f"{CBT.STATS_MENU}:main"))
    return kb

def order_control_settings(c: Cortex):
    """
    Генерирует клавиатуру настроек "Контролёра заказов".
    """
    p = f"{CBT.SWITCH}:OrderControl"

    def l(s):
        return '🟢' if c.MAIN_CFG["OrderControl"].getboolean(s, fallback=False) else '🔴'

    exec_threshold = c.MAIN_CFG["OrderControl"].getint("pending_execution_threshold_m")
    confirm_threshold = c.MAIN_CFG["OrderControl"].getint("pending_confirmation_threshold_h")

    kb = K() \
        .add(B(_("oc_notify_pending_execution", l("notify_pending_execution")), callback_data=f"{p}:notify_pending_execution")) \
        .add(B(_("oc_pending_execution_threshold", exec_threshold), callback_data=f"{CBT.OC_SET_EXEC_THRESHOLD}")) \
        .add(B("─" * 20, callback_data=CBT.EMPTY)) \
        .add(B(_("oc_notify_pending_confirmation", l("notify_pending_confirmation")), callback_data=f"{p}:notify_pending_confirmation")) \
        .add(B(_("oc_pending_confirmation_threshold", confirm_threshold), callback_data=f"{CBT.OC_SET_CONFIRM_THRESHOLD}")) \
        .add(B(_("gl_back"), callback_data=CBT.MAIN2))
    return kb

# НОВЫЕ ФУНКЦИИ ДЛЯ ПОШАГОВОГО ВЫБОРА
def ad_categories_list(c: Cortex, offset: int) -> K:
    """
    Генерирует клавиатуру со списком категорий (игр), где у пользователя есть лоты.
    """
    kb = K()
    # Данные берем из tg_profile, который обновляется по кнопке "Обновить"
    if not c.tg_profile:
        kb.add(B(_("gl_error_try_again"), callback_data=f"update_funpay_lots:{offset}"))
        return kb
        
    all_lots = c.tg_profile.get_common_lots()
    
    unique_categories = {}
    for lot in all_lots:
        if lot.subcategory and lot.subcategory.category:
            cat = lot.subcategory.category
            if cat.id not in unique_categories:
                unique_categories[cat.id] = cat
                
    sorted_categories = sorted(unique_categories.values(), key=lambda category: category.name)
    
    cats_on_page = sorted_categories[offset: offset + MENU_CFG.AD_BTNS_AMOUNT]
    
    if not cats_on_page and offset == 0:
        kb.add(B("🤷‍♂️ Не найдено игр с активными лотами", callback_data=CBT.EMPTY))
    else:
        for category in cats_on_page:
            kb.add(B(f"🎮 {category.name}", callback_data=f"{CBT.AD_CHOOSE_SUBCATEGORY_LIST}:{category.id}:0"))

    kb = add_navigation_buttons(kb, offset, MENU_CFG.AD_BTNS_AMOUNT, len(cats_on_page),
                                len(sorted_categories), CBT.AD_CHOOSE_CATEGORY_LIST)
    
    kb.row(B(_("gl_refresh"), callback_data=f"update_funpay_lots:{offset}"),
           B(_("fl_manual"), callback_data=f"{CBT.ADD_AD_TO_LOT_MANUALLY}:{offset}"))
    kb.add(B(_("ad_to_ad"), callback_data=f"{CBT.CATEGORY}:ad"))
    return kb


def ad_subcategories_list(c: Cortex, category_id: int, offset: int) -> K:
    """
    Генерирует клавиатуру со списком подкатегорий в выбранной игре.
    """
    kb = K()
    if not c.tg_profile:
        kb.add(B(_("gl_error_try_again"), callback_data=f"{CBT.AD_CHOOSE_CATEGORY_LIST}:0"))
        return kb
        
    all_lots = c.tg_profile.get_common_lots()

    unique_subcategories = {}
    for lot in all_lots:
        if lot.subcategory and lot.subcategory.category.id == category_id:
            subcat = lot.subcategory
            if subcat.id not in unique_subcategories:
                unique_subcategories[subcat.id] = subcat

    sorted_subcategories = sorted(unique_subcategories.values(), key=lambda subcat: subcat.name)

    subcats_on_page = sorted_subcategories[offset: offset + MENU_CFG.AD_BTNS_AMOUNT]

    if not subcats_on_page and offset == 0:
        kb.add(B("🤷‍♂️ Не найдено разделов с лотами в этой игре", callback_data=CBT.EMPTY))
    else:
        for subcat in subcats_on_page:
            kb.add(B(f"📁 {subcat.name}", callback_data=f"{CBT.AD_CHOOSE_LOT_LIST}:{category_id}:{subcat.id}:0"))

    extra_nav = [category_id]
    kb = add_navigation_buttons(kb, offset, MENU_CFG.AD_BTNS_AMOUNT, len(subcats_on_page),
                                len(sorted_subcategories), CBT.AD_CHOOSE_SUBCATEGORY_LIST, extra_nav)

    kb.add(B(_("gl_back"), callback_data=f"{CBT.AD_CHOOSE_CATEGORY_LIST}:0"))
    return kb


def ad_lots_from_subcategory_list(c: Cortex, lots: List[MyLotShortcut], category_id: int, subcategory_id: int, offset: int) -> K:
    """
    Генерирует клавиатуру со списком лотов из выбранной подкатегории.
    """
    kb = K()
    lots_on_page = lots[offset: offset + MENU_CFG.AD_BTNS_AMOUNT]

    if not lots_on_page and offset == 0:
        kb.add(B("🤷‍♂️ Не найдено лотов в этом разделе.", callback_data=CBT.EMPTY))
    else:
        for index, lot_obj in enumerate(lots_on_page):
            # В `get_my_subcategory_lots` нет информации о названии лота, используем описание
            lot_title = lot_obj.description or f"Лот ID {lot_obj.id}"
            is_ad_configured = lot_title in c.AD_CFG.sections()
            prefix = "✅ " if is_ad_configured else "➕ "
            display_title = lot_title[:40] + "..." if len(lot_title) > 40 else lot_title
            # Передаем индекс на странице, а не абсолютный
            callback_data = f"{CBT.ADD_AD_TO_LOT}:{index}:{subcategory_id}:{category_id}:{offset}"
            kb.add(B(f"{prefix}{display_title}", callback_data=callback_data))

    extra_nav = [category_id, subcategory_id]
    kb = add_navigation_buttons(kb, offset, MENU_CFG.AD_BTNS_AMOUNT, len(lots_on_page),
                                len(lots), CBT.AD_CHOOSE_LOT_LIST, extra_nav)
                                
    kb.add(B(_("gl_back"), callback_data=f"{CBT.AD_CHOOSE_SUBCATEGORY_LIST}:{category_id}:0"))
    return kb