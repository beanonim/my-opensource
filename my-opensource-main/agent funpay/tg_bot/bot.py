"""
В данном модуле написан Telegram бот.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from FunPayAPI import Account
from tg_bot.utils import NotificationTypes

if TYPE_CHECKING:
    from cortex import Cortex

import os
import sys
import time
import random
import string
import psutil
import telebot
from telebot.apihelper import ApiTelegramException
import logging
import requests

from telebot.types import InlineKeyboardMarkup as K, InlineKeyboardButton as B, Message, CallbackQuery, BotCommand, \
    InputFile
from tg_bot import utils, static_keyboards as skb, keyboards as kb, CBT, crm_cp
from Utils import cortex_tools, updater
from locales.localizer import Localizer

logger = logging.getLogger("TGBot")
localizer = Localizer()
_ = localizer.translate
telebot.apihelper.ENABLE_MIDDLEWARE = True


def strip_html_comments(html_string: str) -> str:
    """Удаляет HTML-комментарии из строки."""
    if not isinstance(html_string, str):
        return str(html_string)
    return re.sub(r"<!--(.*?)-->", "", html_string, flags=re.DOTALL)

class TGBot:
    def __init__(self, cortex_instance: Cortex):
        self.cortex: Cortex = cortex_instance
        self.bot = telebot.TeleBot(self.cortex.MAIN_CFG["Telegram"]["token"], parse_mode="HTML",
                                   allow_sending_without_reply=True, num_threads=5)

        self.file_handlers = {}
        self.attempts = {}
        self.init_messages = []

        self.user_states = {}
        self.notification_settings = utils.load_notification_settings()
        self.answer_templates = utils.load_answer_templates()
        self.authorized_users = utils.load_authorized_users()
        self._initialized = False

        self.commands = {
            "menu": "cmd_menu",
            "profile": "stat_adv_stats_button",
            "restart": "cmd_restart",
            "check_updates": "cmd_check_updates",
            "update": "cmd_update",
            "golden_key": "cmd_golden_key",
            "ban": "cmd_ban",
            "unban": "cmd_unban",
            "black_list": "cmd_black_list",
            "upload_chat_img": "cmd_upload_chat_img",
            "upload_offer_img": "cmd_upload_offer_img",
            "upload_plugin": "cmd_upload_plugin",
            "test_lot": "cmd_test_lot",
            "logs": "cmd_logs",
            "about": "cmd_about",
            "sys": "cmd_sys",
            "get_backup": "cmd_get_backup",
            "create_backup": "cmd_create_backup",
            "del_logs": "cmd_del_logs",
            "power_off": "cmd_power_off",
            "watermark": "cmd_watermark",
            "note": "cmd_note",
        }
        self.__default_notification_settings = {
            utils.NotificationTypes.ad: 1,
            utils.NotificationTypes.announcement: 1,
            utils.NotificationTypes.critical: 1
        }

    def get_state(self, chat_id: int, user_id: int) -> dict | None:
        try:
            return self.user_states[chat_id][user_id]
        except KeyError:
            return None

    def set_state(self, chat_id: int, message_id: int, user_id: int, state: str, data: dict | None = None):
        if chat_id not in self.user_states:
            self.user_states[chat_id] = {}
        self.user_states[chat_id][user_id] = {"state": state, "mid": message_id, "data": data or {}}

    def clear_state(self, chat_id: int, user_id: int, del_msg: bool = False) -> int | None:
        try:
            state = self.user_states[chat_id][user_id]
        except KeyError:
            return None
        msg_id = state.get("mid")
        if user_id in self.user_states.get(chat_id, {}):
            del self.user_states[chat_id][user_id]
        if del_msg:
            try:
                self.bot.delete_message(chat_id, msg_id)
            except ApiTelegramException:
                pass
            except Exception as e:
                logger.warning(f"Не удалось удалить сообщение {msg_id} при очистке состояния: {e}")
        return msg_id

    def check_state(self, chat_id: int, user_id: int, state: str) -> bool:
        try:
            return self.user_states[chat_id][user_id]["state"] == state
        except KeyError:
            return False

    def is_notification_enabled(self, chat_id: int | str, notification_type: str) -> bool:
        try:
            return bool(self.notification_settings[str(chat_id)][notification_type])
        except KeyError:
            return False

    def toggle_notification(self, chat_id: int, notification_type: str) -> bool:
        chat_id_str = str(chat_id)
        if chat_id_str not in self.notification_settings:
            self.notification_settings[chat_id_str] = {}

        current_status = self.notification_settings[chat_id_str].get(notification_type, False)
        self.notification_settings[chat_id_str][notification_type] = not current_status
        utils.save_notification_settings(self.notification_settings)
        return self.notification_settings[chat_id_str][notification_type]


    def file_handler(self, state, handler):
        self.file_handlers[state] = handler

    def run_file_handlers(self, m: Message):
        if (state := self.get_state(m.chat.id, m.from_user.id)) is None \
                or state["state"] not in self.file_handlers:
            return
        try:
            self.file_handlers[state["state"]](self, m)
        except Exception as e:
            logger.error(_("log_tg_handler_error") + f" (File Handler: {state['state']})")
            logger.debug(f"Error details: {e}", exc_info=True)


    def msg_handler(self, handler, **kwargs):
        bot_instance = self.bot
        @bot_instance.message_handler(**kwargs)
        def run_handler(message: Message):
            try:
                handler(message)
            except Exception as e:
                logger.error(_("log_tg_handler_error") + f" (Message Handler: {handler.__name__})")
                logger.debug(f"Error details: {e}", exc_info=True)

    def cbq_handler(self, handler, func, **kwargs):
        bot_instance = self.bot
        @bot_instance.callback_query_handler(func, **kwargs)
        def run_handler(call: CallbackQuery):
            try:
                handler(call)
            except Exception as e:
                logger.error(_("log_tg_handler_error") + f" (Callback Handler: {handler.__name__}, data: {call.data[:50]})")
                logger.debug(f"Error details: {e}", exc_info=True)

    def mdw_handler(self, handler, **kwargs):
        bot_instance = self.bot
        @bot_instance.middleware_handler(**kwargs)
        def run_handler(bot_mdw, update):
            try:
                handler(bot_mdw, update)
            except Exception as e:
                logger.error(_("log_tg_handler_error") + f" (Middleware Handler: {handler.__name__})")
                logger.debug(f"Error details: {e}", exc_info=True)


    def setup_chat_notifications(self, bot_instance_mdw: telebot.TeleBot, m: Message):
        chat_id_str = str(m.chat.id)
        user_id = m.from_user.id

        if chat_id_str not in self.notification_settings:
            self.notification_settings[chat_id_str] = self.__default_notification_settings.copy()
            self.notification_settings[chat_id_str][NotificationTypes.critical] = 1 if user_id in self.authorized_users else 0
            utils.save_notification_settings(self.notification_settings)
        elif user_id in self.authorized_users and \
             not self.notification_settings[chat_id_str].get(NotificationTypes.critical, False):
            self.notification_settings[chat_id_str][NotificationTypes.critical] = 1
            utils.save_notification_settings(self.notification_settings)


    def handle_unauthorized_message(self, m: Message):
        """
        Обрабатывает все текстовые сообщения от неавторизованных пользователей.
        Пытается авторизовать. Если не получается - отправляет сообщение об отказе в доступе.
        """
        lang = m.from_user.language_code
        if m.chat.type != "private" or m.text is None:
            return

        user_input = m.text.strip()
        user_id = m.from_user.id
        username = m.from_user.username or str(user_id)
        
        # Попытка входа по паролю администратора
        is_admin_password = not self.cortex.block_tg_login and cortex_tools.check_password(user_input, self.cortex.MAIN_CFG["Telegram"]["secretKeyHash"])
        
        # Попытка входа по ключу менеджера
        manager_key = self.cortex.MAIN_CFG["Manager"].get("registration_key", "").strip()
        is_manager_key = manager_key and user_input == manager_key

        # Если это пароль админа
        if is_admin_password:
            self.authorized_users[user_id] = {"username": username, "role": "admin"}
            utils.save_authorized_users(self.authorized_users)
            self.setup_chat_notifications(self.bot, m)
            logger.warning(_("log_access_granted", username, user_id))
            self.send_notification(text=_("access_granted_notification", username, user_id),
                                   notification_type=NotificationTypes.critical, pin=True, exclude_chat_id=m.chat.id)
            self.bot.send_message(m.chat.id, _("access_granted", language=lang))
            return

        # Если это ключ менеджера
        if is_manager_key:
            self.authorized_users[user_id] = {"username": username, "role": "manager"}
            utils.save_authorized_users(self.authorized_users)
            self.setup_chat_notifications(self.bot, m)
            logger.warning(_("log_manager_access_granted", username, user_id))
            self.bot.send_message(m.chat.id, _("manager_access_granted", language=lang))
            return
            
        # Если это не пароль и не ключ - отказ в доступе
        if self.attempts.get(m.from_user.id, 0) >= 5: return
        self.attempts[user_id] = self.attempts.get(user_id, 0) + 1
        self.bot.send_message(m.chat.id, _("access_denied", m.from_user.username or user_id, language=lang))
        logger.warning(_("log_access_attempt", username, user_id))


    def ignore_unauthorized_users(self, c: CallbackQuery):
        logger.warning(_("log_click_attempt", c.from_user.username, c.from_user.id, c.message.chat.username,
                         c.message.chat.id))
        self.attempts[c.from_user.id] = self.attempts.get(c.from_user.id, 0) + 1
        if self.attempts[c.from_user.id] <= 5:
            self.bot.answer_callback_query(c.id, _("adv_fpc", language=c.from_user.language_code), show_alert=True)
        else:
            self.bot.answer_callback_query(c.id)


    def send_settings_menu(self, m: Message):
        start_message = f"""👋 <b>{_('desc_main', language=m.from_user.language_code)}</b>

        🧠 <b>FunPay Cortex v{self.cortex.VERSION}</b>
        🚀 {_('adv_fpc', language=m.from_user.language_code)}

        🔗 <a href="https://t.me/FunPayCortex"><b>Канал FPCortex в Telegram</b></a> - обновления, плагины, общение!

        👇 {_('cmd_menu').capitalize()}:
        """
        self.bot.send_message(m.chat.id, start_message, reply_markup=skb.SETTINGS_SECTIONS(self.cortex, m.from_user.id), disable_web_page_preview=True)

    def send_profile(self, m_or_c: Message | CallbackQuery):
        chat_id = m_or_c.chat.id if isinstance(m_or_c, Message) else m_or_c.message.chat.id

        user_role = utils.get_user_role(self.authorized_users, m_or_c.from_user.id)
        if user_role == "manager" and not self.cortex.MAIN_CFG["ManagerPermissions"].getboolean("can_view_stats", fallback=False):
            self.bot.send_message(chat_id, _("manager_permission_denied"))
            return

        # Принудительно обновляем сессию для получения актуальных данных
        try:
            self.cortex.update_session()
        except Exception as e:
            logger.error(f"Не удалось обновить сессию для /profile: {e}")
            self.bot.send_message(chat_id, _("profile_updating_error"))
            if isinstance(m_or_c, CallbackQuery):
                self.bot.answer_callback_query(m_or_c.id)
            return

        text = utils.generate_profile_text(self.cortex)
        kb = skb.REFRESH_BTN()

        if isinstance(m_or_c, Message):
            self.bot.send_message(chat_id, text, reply_markup=kb)
        else:  # CallbackQuery
            try:
                self.bot.edit_message_text(text, chat_id, m_or_c.message.id, reply_markup=kb)
            except telebot.apihelper.ApiTelegramException as e:
                if "message is not modified" not in e.description:
                    raise
            self.bot.answer_callback_query(m_or_c.id)


    def send_statistics_menu(self, m: Message):
        user_role = utils.get_user_role(self.authorized_users, m.from_user.id)
        if user_role == 'manager' and not self.cortex.MAIN_CFG["ManagerPermissions"].getboolean("can_view_stats"):
            self.bot.send_message(m.chat.id, _("manager_permission_denied"))
            return
        
        try:
            self.cortex.balance = self.cortex.get_balance()
        except Exception as e:
            logger.error(f"Не удалось обновить баланс для меню статистики: {e}")
            self.bot.send_message(m.chat.id, _("gl_error_try_again"))
            return

        self.bot.send_message(m.chat.id, "📊 " + _("stat_adv_stats_button"),
                              reply_markup=kb.statistics_menu(self.cortex))

    def send_advanced_profile_stats(self, c: CallbackQuery):
        """Отправляет расширенную статистику по аккаунту."""
        user_role = utils.get_user_role(self.authorized_users, c.from_user.id)
        if user_role == "manager" and not self.cortex.MAIN_CFG["ManagerPermissions"].getboolean("can_view_stats", fallback=False):
            self.bot.answer_callback_query(c.id, _("manager_permission_denied"), show_alert=True)
            return
            
        progress_msg = self.bot.send_message(c.message.chat.id, _("updating_profile"))
        try:
            stats_data = self.cortex.generate_advanced_stats()
            stats_text = utils.generate_advanced_stats_text(self.cortex, stats_data)
            self.bot.edit_message_text(stats_text, progress_msg.chat.id, progress_msg.id,
                                       reply_markup=skb.ADV_PROFILE_STATS_BTN())
        except Exception as e:
            self.bot.edit_message_text(_("profile_updating_error") + f"\nError: {str(e)[:100]}",
                                       progress_msg.chat.id, progress_msg.id)
            logger.error(f"Ошибка при формировании расширенной статистики: {e}", exc_info=True)
        finally:
            self.bot.answer_callback_query(c.id)

    def act_change_cookie(self, m: Message):
        user_role = utils.get_user_role(self.authorized_users, m.from_user.id)
        if user_role != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        result = self.bot.send_message(m.chat.id, _("act_change_golden_key"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.CHANGE_GOLDEN_KEY)

    def change_cookie(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        golden_key = m.text.strip()
        if len(golden_key) != 32 or golden_key != golden_key.lower() or len(golden_key.split()) != 1:
            self.bot.send_message(m.chat.id, _("cookie_incorrect_format"))
            return
        self.bot.delete_message(m.chat.id, m.id)
        new_account = Account(golden_key, self.cortex.account.user_agent, proxy=self.cortex.proxy,
                              locale=self.cortex.account.locale)
        try:
            new_account.get()
        except Exception as e:
            logger.warning(_("cookie_error") + f": {e}")
            logger.debug("TRACEBACK", exc_info=True)
            self.bot.send_message(m.chat.id, _("cookie_error"))
            return

        one_acc = False
        if new_account.id == self.cortex.account.id or self.cortex.account.id is None:
            one_acc = True
            self.cortex.account.golden_key = golden_key
            try:
                self.cortex.account.get()
            except Exception as e:
                logger.warning(_("cookie_error") + f": {e}")
                logger.debug("TRACEBACK", exc_info=True)
                self.bot.send_message(m.chat.id, _("cookie_error"))
                return
            accs = f" (<a href='https://funpay.com/users/{new_account.id}/'>{utils.escape(new_account.username)}</a>)"
        else:
            accs = f" (<a href='https://funpay.com/users/{self.cortex.account.id}/'>" \
                   f"{utils.escape(self.cortex.account.username)}</a> ➔ <a href='https://funpay.com/users/{new_account.id}/'>" \
                   f"{utils.escape(new_account.username)}</a>)"

        self.cortex.MAIN_CFG.set("FunPay", "golden_key", golden_key)
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        self.bot.send_message(m.chat.id, f'{_("cookie_changed", accs)}{_("cookie_changed2") if not one_acc else ""}',
                              disable_web_page_preview=True)

    def update_profile(self, c: CallbackQuery):
        new_msg = self.bot.send_message(c.message.chat.id, _("updating_profile"))
        try:
            self.cortex.account.get()
            self.cortex.balance = self.cortex.get_balance()
            self.bot.delete_message(new_msg.chat.id, new_msg.id)
            try:
                self.bot.edit_message_text(utils.generate_profile_text(self.cortex), c.message.chat.id,
                                       c.message.id, reply_markup=skb.REFRESH_BTN())
            except ApiTelegramException as e:
                if "message is not modified" not in e.description:
                    raise
        except Exception as e:
            self.bot.edit_message_text(_("profile_updating_error") + f"\nError: {str(e)[:100]}", new_msg.chat.id, new_msg.id)
            logger.error(f"Ошибка при обновлении профиля через TG: {e}")
            logger.debug("TRACEBACK", exc_info=True)
        finally:
            self.bot.answer_callback_query(c.id)


    def act_manual_delivery_test(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("create_test_ad_key"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.MANUAL_AD_TEST)

    def manual_delivery_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        lot_name = m.text.strip()
        key = "".join(random.sample(string.ascii_letters + string.digits, 50))
        self.cortex.delivery_tests[key] = lot_name
        logger.info(_("log_new_ad_key", m.from_user.username, m.from_user.id, lot_name, key))
        self.bot.send_message(m.chat.id, _("test_ad_key_created", utils.escape(lot_name), key))

    def act_ban(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("act_blacklist"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.BAN)

    def ban(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        nickname = m.text.strip()
        if nickname in self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("already_blacklisted", utils.escape(nickname)))
            return
        self.cortex.blacklist.append(nickname)
        cortex_tools.cache_blacklist(self.cortex.blacklist)
        logger.info(_("log_user_blacklisted", m.from_user.username, m.from_user.id, nickname))
        self.bot.send_message(m.chat.id, _("user_blacklisted", utils.escape(nickname)))

    def act_unban(self, m: Message):
        result = self.bot.send_message(m.chat.id, _("act_unban"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.UNBAN)

    def unban(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        nickname = m.text.strip()
        if nickname not in self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("not_blacklisted", utils.escape(nickname)))
            return
        self.cortex.blacklist.remove(nickname)
        cortex_tools.cache_blacklist(self.cortex.blacklist)
        logger.info(_("log_user_unbanned", m.from_user.username, m.from_user.id, nickname))
        self.bot.send_message(m.chat.id, _("user_unbanned", utils.escape(nickname)))

    def send_ban_list(self, m: Message):
        if not self.cortex.blacklist:
            self.bot.send_message(m.chat.id, _("blacklist_empty"))
            return
        blacklist_str = "\n".join(f"🚫 <code>{utils.escape(i)}</code>" for i in sorted(self.cortex.blacklist, key=lambda x: x.lower()))
        self.bot.send_message(m.chat.id, f"<b>{_('mm_blacklist')}:</b>\n{blacklist_str}" if blacklist_str else _("blacklist_empty"))


    def act_edit_watermark(self, m: Message):
        watermark = self.cortex.MAIN_CFG["Other"]["watermark"]
        watermark_display = f"\n\n{_('crd_msg_sent', '').split(' в чат')[0]} {_('v_edit_watermark_current')}: <code>{utils.escape(watermark)}</code>" if watermark else ""
        result = self.bot.send_message(m.chat.id, _("act_edit_watermark").format(watermark_display),
                                       reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, CBT.EDIT_WATERMARK)

    def edit_watermark(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        watermark_text = m.text.strip() if m.text.strip() != "-" else ""
        if re.fullmatch(r"\[[a-zA-Z]+]", watermark_text):
            self.bot.reply_to(m, _("watermark_error"))
            return
        preview_html = f"<a href=\"https://sfunpay.com/s/chat/zb/wl/zbwl4vwc8cc1wsftqnx5.jpg\">⁠</a>"
        if any(i.lower() in watermark_text.lower() for i in ("🧠", "fpcx", "cortex", "кортекс")):
            preview_html = f"<a href=\"https://sfunpay.com/s/chat/kd/8i/kd8isyquw660kcueck3g.jpg\">⁠</a>"
        self.cortex.MAIN_CFG["Other"]["watermark"] = watermark_text
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        if watermark_text:
            logger.info(_("log_watermark_changed", m.from_user.username, m.from_user.id, watermark_text))
            self.bot.reply_to(m, preview_html + _("watermark_changed", utils.escape(watermark_text)))
        else:
            logger.info(_("log_watermark_deleted", m.from_user.username, m.from_user.id))
            self.bot.reply_to(m, preview_html + _("watermark_deleted"))

    def send_logs(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        if not os.path.exists("logs/log.log"):
            self.bot.send_message(m.chat.id, _("logfile_not_found"))
        else:
            progress_msg = self.bot.send_message(m.chat.id, _("logfile_sending"))
            try:
                with open("logs/log.log", "rb") as f:
                    mode_info = _("gs_old_msg_mode").replace("{} ", "") if self.cortex.old_mode_enabled else _("old_mode_help").split('\n')[0].replace("<b>","").replace("</b>","").replace("🚀","").strip()
                    self.bot.send_document(m.chat.id, f,
                                           caption=f"📄 Лог-файл FPCortex\nРежим сообщений: <i>{mode_info}</i>")
                self.bot.delete_message(progress_msg.chat.id, progress_msg.id)
            except Exception as e:
                self.bot.edit_message_text(_("logfile_error") + f"\nError: {str(e)[:100]}", progress_msg.chat.id, progress_msg.id)
                logger.error(f"Ошибка при отправке логов: {e}")
                logger.debug("TRACEBACK", exc_info=True)


    def del_logs(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        logger.info(
            f"[IMPORTANT] Удаляю старые логи по запросу пользователя $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET.")
        deleted_count = 0
        logs_dir = "logs"
        if not os.path.isdir(logs_dir):
            self.bot.send_message(m.chat.id, _("logfile_deleted", 0))
            return

        for file_name in os.listdir(logs_dir):
            if file_name == "log.log":
                continue
            try:
                full_path = os.path.join(logs_dir, file_name)
                if os.path.isfile(full_path):
                    os.remove(full_path)
                    deleted_count += 1
            except OSError as e:
                logger.warning(f"Не удалось удалить файл {file_name}: {e}")
                continue
            except Exception as e:
                logger.error(f"Непредвиденная ошибка при удалении файла {file_name}: {e}")
                logger.debug("TRACEBACK", exc_info=True)
        self.bot.send_message(m.chat.id, _("logfile_deleted", deleted_count))

    def about(self, m: Message):
        self.bot.send_message(m.chat.id, _("about", self.cortex.VERSION))

    def check_updates(self, m: Message):
        curr_tag = f"v{self.cortex.VERSION}"
        releases = updater.get_new_releases(curr_tag)
        if isinstance(releases, int):
            errors = {
                1: ["update_no_tags", ()],
                2: ["update_lasted", (curr_tag,)],
                3: ["update_get_error", ()],
            }
            self.bot.send_message(m.chat.id, _(errors[releases][0], *errors[releases][1]))
            return
        for release in releases:
            cleaned_description = strip_html_comments(release.description)
            self.bot.send_message(m.chat.id, _("update_available", f"{release.name}\n\n{cleaned_description}"))
            time.sleep(1)
        self.bot.send_message(m.chat.id, _("update_update"))

    def get_backup(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        logger.info(
            f"[IMPORTANT] Запрос резервной копии от $MAGENTA@{m.from_user.username} (id: {m.from_user.id})$RESET.")
        backup_path = "backup.zip"
        if os.path.exists(backup_path):
            progress_msg = self.bot.send_message(m.chat.id, _("logfile_sending"))
            try:
                with open(backup_path, 'rb') as file_to_send:
                    modification_timestamp = os.path.getmtime(backup_path)
                    formatted_time = time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(modification_timestamp))
                    self.bot.send_document(chat_id=m.chat.id, document=InputFile(file_to_send),
                                           caption=f'{_("update_backup")}\n\n🗓️ {_("v_date_text").replace(" ($date_text)", "")}: {formatted_time}')
                self.bot.delete_message(progress_msg.chat.id, progress_msg.id)
            except Exception as e:
                self.bot.edit_message_text(_("logfile_error") + f"\nError: {str(e)[:100]}", progress_msg.chat.id, progress_msg.id)
                logger.error(f"Ошибка при отправке бэкапа: {e}")
                logger.debug("TRACEBACK", exc_info=True)
        else:
            self.bot.send_message(m.chat.id, _("update_backup_not_found"))

    def create_backup(self, m: Message):
        if updater.create_backup() != 0:
            self.bot.send_message(m.chat.id, _("update_backup_error"))
            return False
        self.get_backup(m)
        return True

    def update(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        curr_tag = f"v{self.cortex.VERSION}"
        releases = updater.get_new_releases(curr_tag)
        if isinstance(releases, int):
            errors = {
                1: ["update_no_tags", ()],
                2: ["update_lasted", (curr_tag,)],
                3: ["update_get_error", ()],
            }
            self.bot.send_message(m.chat.id, _(errors[releases][0], *errors[releases][1]))
            return
        if not self.create_backup(m):
            return

        release = releases[-1]
        if updater.download_zip(release.sources_link) != 0 \
                or (release_folder := updater.extract_update_archive()) == 1:
            self.bot.send_message(m.chat.id, _("update_download_error"))
            return
        self.bot.send_message(m.chat.id, _("update_downloaded", release.name, str(len(releases) - 1)))

        if updater.install_release(release_folder) != 0:
            self.bot.send_message(m.chat.id, _("update_install_error"))
            return

        if getattr(sys, 'frozen', False):
            self.bot.send_message(m.chat.id, _("update_done_exe"))
        else:
            self.bot.send_message(m.chat.id, _("update_done"))

    def send_system_info(self, m: Message):
        current_timestamp = int(time.time())
        uptime_seconds = current_timestamp - self.cortex.start_time
        ram_info = psutil.virtual_memory()
        cpu_usage_per_core_list = psutil.cpu_percent(percpu=True)
        cpu_usage_per_core_str = "\n".join(
            f"    {_('v_cpu_core')} {i+1}:  <code>{usage}%</code>" for i, usage in enumerate(cpu_usage_per_core_list))
        self.bot.send_message(m.chat.id, _("sys_info", cpu_usage_per_core_str, psutil.Process().cpu_percent(),
                                           ram_info.total // 1048576, ram_info.used // 1048576, ram_info.free // 1048576,
                                           psutil.Process().memory_info().rss // 1048576,
                                           cortex_tools.time_to_str(uptime_seconds), m.chat.id))


    def restart_cortex(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        self.bot.send_message(m.chat.id, _("restarting"))
        cortex_tools.restart_program()

    def ask_power_off(self, m: Message):
        if utils.get_user_role(self.authorized_users, m.from_user.id) != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        self.bot.send_message(m.chat.id, _("power_off_0"), reply_markup=kb.power_off(self.cortex.instance_id, 0))

    def cancel_power_off(self, c: CallbackQuery):
        try:
            self.bot.edit_message_text(_("power_off_cancelled"), c.message.chat.id, c.message.id)
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(c.id)

    def power_off(self, c: CallbackQuery):
        split_data = c.data.split(":")
        current_stage = int(split_data[1])
        instance_id_from_cb = int(split_data[2])
        if instance_id_from_cb != self.cortex.instance_id:
            try:
                self.bot.edit_message_text(_("power_off_error"), c.message.chat.id, c.message.id)
            except ApiTelegramException as e:
                if "message is not modified" not in e.description:
                    raise
            self.bot.answer_callback_query(c.id)
            return
        if current_stage == 6:
            try:
                self.bot.edit_message_text(_("power_off_6"), c.message.chat.id, c.message.id)
            except ApiTelegramException as e:
                if "message is not modified" not in e.description:
                    raise
            self.bot.answer_callback_query(c.id)
            cortex_tools.shut_down()
            return
        try:
            self.bot.edit_message_text(_(f"power_off_{current_stage}"), c.message.chat.id, c.message.id,
                                       reply_markup=kb.power_off(instance_id_from_cb, current_stage))
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(c.id)

    def act_send_funpay_message(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id = int(split_data[1])
        username = split_data[2] if len(split_data) > 2 else None
        result_msg = self.bot.send_message(c.message.chat.id, _("enter_msg_text"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id,
                       CBT.SEND_FP_MESSAGE, {"node_id": node_id, "username": username})
        self.bot.answer_callback_query(c.id)

    def send_funpay_message(self, message: Message):
        state_data = self.get_state(message.chat.id, message.from_user.id)["data"]
        node_id, username = state_data["node_id"], state_data["username"]
        self.clear_state(message.chat.id, message.from_user.id, True)
        response_text_to_send = message.text.strip()
        send_success = self.cortex.send_message(node_id, response_text_to_send, username, watermark=False)
        reply_kb = kb.reply(node_id, username, again=True, extend=True)
        if send_success:
            self.bot.reply_to(message, _("msg_sent", node_id, utils.escape(username or "Пользователь")), reply_markup=reply_kb)
        else:
            self.bot.reply_to(message, _("msg_sending_error", node_id, utils.escape(username or "Пользователь")), reply_markup=reply_kb)

    def act_upload_image(self, m: Message):
        user_role = utils.get_user_role(self.authorized_users, m.from_user.id)
        if user_role != "admin":
            self.bot.send_message(m.chat.id, _("admin_only_command"))
            return
        cbt_state = CBT.UPLOAD_CHAT_IMAGE if m.text.startswith("/upload_chat_img") else CBT.UPLOAD_OFFER_IMAGE
        result_msg = self.bot.send_message(m.chat.id, _("send_img"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result_msg.id, m.from_user.id, cbt_state)

    def act_edit_greetings_text(self, c: CallbackQuery):
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_message_text", "v_chat_id", "v_chat_name", "v_photo", "v_sleep"]
        text_to_send = f"{_('v_edit_greeting_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_GREETINGS_TEXT)
        self.bot.answer_callback_query(c.id)

    def edit_greetings_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_greeting_text = m.text.strip()
        self.cortex.MAIN_CFG["Greetings"]["greetingsText"] = new_greeting_text
        logger.info(_("log_greeting_changed", m.from_user.username, m.from_user.id, new_greeting_text))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:gr"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_GREETINGS_TEXT))
        self.bot.reply_to(m, _("greeting_changed"), reply_markup=reply_keyboard)

    def act_edit_greetings_cooldown(self, c: CallbackQuery):
        text_to_send = _('v_edit_greeting_cooldown')
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_GREETINGS_COOLDOWN)
        self.bot.answer_callback_query(c.id)

    def edit_greetings_cooldown(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        try:
            cooldown_days = float(m.text.replace(",", "."))
            if cooldown_days < 0: raise ValueError("Cooldown не может быть отрицательным")
        except ValueError:
            self.bot.reply_to(m, _("gl_error_try_again") + " (введите число, например, 0.5 или 1)")
            return
        self.cortex.MAIN_CFG["Greetings"]["greetingsCooldown"] = str(cooldown_days)
        logger.info(_("log_greeting_cooldown_changed", m.from_user.username, m.from_user.id, str(cooldown_days)))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:gr"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_GREETINGS_COOLDOWN))
        self.bot.reply_to(m, _("greeting_cooldown_changed", str(cooldown_days)), reply_markup=reply_keyboard)

    def act_edit_order_confirm_reply_text(self, c: CallbackQuery):
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_order_id", "v_order_link", "v_order_title", "v_game", "v_category", "v_category_fullname",
                     "v_photo", "v_sleep"]
        text_to_send = f"{_('v_edit_order_confirm_text')}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT)
        self.bot.answer_callback_query(c.id)

    def edit_order_confirm_reply_text(self, m: Message):
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_reply_text = m.text.strip()
        self.cortex.MAIN_CFG["OrderConfirm"]["replyText"] = new_reply_text
        logger.info(_("log_order_confirm_changed", m.from_user.username, m.from_user.id, new_reply_text))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:oc"),
                 B(_("gl_edit"), callback_data=CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT))
        self.bot.reply_to(m, _("order_confirm_changed"), reply_markup=reply_keyboard)

    def act_edit_review_reply_text(self, c: CallbackQuery):
        stars_count = int(c.data.split(":")[1])
        variables = ["v_date", "v_date_text", "v_full_date_text", "v_time", "v_full_time", "v_username",
                     "v_order_id", "v_order_link", "v_order_title", "v_order_params",
                     "v_order_desc_and_params", "v_order_desc_or_params", "v_game", "v_category", "v_category_fullname"]
        text_to_send = f"{_('v_edit_review_reply_text', '⭐' * stars_count)}\n\n{_('v_list')}:\n" + "\n".join(_(var) for var in variables)
        result_msg = self.bot.send_message(c.message.chat.id, text_to_send, reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(c.message.chat.id, result_msg.id, c.from_user.id, CBT.EDIT_REVIEW_REPLY_TEXT, {"stars": stars_count})
        self.bot.answer_callback_query(c.id)

    def edit_review_reply_text(self, m: Message):
        state_data = self.get_state(m.chat.id, m.from_user.id)
        if not state_data or "data" not in state_data or "stars" not in state_data["data"]:
            logger.warning(f"Некорректное состояние для edit_review_reply_text, user: {m.from_user.id}")
            self.clear_state(m.chat.id, m.from_user.id, True)
            self.bot.reply_to(m, _("gl_error_try_again"))
            return
        stars_count = state_data["data"]["stars"]
        self.clear_state(m.chat.id, m.from_user.id, True)
        new_review_reply = m.text.strip()
        self.cortex.MAIN_CFG["ReviewReply"][f"star{stars_count}ReplyText"] = new_review_reply
        logger.info(_("log_review_reply_changed", m.from_user.username, m.from_user.id, stars_count, new_review_reply))
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        reply_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:rr"),
                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{stars_count}"))
        self.bot.reply_to(m, _("review_reply_changed", '⭐' * stars_count), reply_markup=reply_keyboard)

    def open_reply_menu(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id, username = int(split_data[1]), split_data[2]
        is_again_reply = int(split_data[3])
        should_extend = True if len(split_data) > 4 and int(split_data[4]) else False
        try:
            self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=kb.reply(node_id, username, bool(is_again_reply), should_extend))
        except ApiTelegramException as e:
            if e.error_code == 400 and "message is not modified" in e.description.lower():
                pass
            else:
                raise e
        self.bot.answer_callback_query(c.id)


    def extend_new_message_notification(self, c: CallbackQuery):
        chat_id_str, username = c.data.split(":")[1:]
        try:
            chat_obj = self.cortex.account.get_chat(int(chat_id_str))
        except Exception as e:
            logger.warning(f"Не удалось получить чат {chat_id_str} для расширения: {e}")
            logger.debug("TRACEBACK", exc_info=True)
            self.bot.answer_callback_query(c.id, _("get_chat_error"), show_alert=True)
            return

        text_to_send = ""
        if chat_obj.looking_link:
            text_to_send += f"<b>{_('viewing')}:</b> <a href=\"{chat_obj.looking_link}\">{utils.escape(chat_obj.looking_text)}</a>\n\n"

        chat_messages = chat_obj.messages[-10:]
        last_author_id = -1
        last_by_bot_flag = False
        last_author_badge = None
        last_by_fpcortex = False

        for msg_item in chat_messages:
            author_prefix = ""
            if msg_item.author_id == last_author_id and \
               msg_item.by_bot == last_by_bot_flag and \
               msg_item.badge == last_author_badge and \
               last_by_fpcortex == (msg_item.by_bot and msg_item.author_id == self.cortex.account.id):
                pass
            elif msg_item.author_id == self.cortex.account.id:
                author_prefix = f"<i><b>🤖 {_('you')} (<i>FPCortex</i>):</b></i> " if msg_item.by_bot else f"<i><b>🫵 {_('you')}:</b></i> "
                if msg_item.is_autoreply:
                    author_prefix = f"<i><b>📦 {_('you')} ({utils.escape(msg_item.badge or '')}):</b></i> "
            elif msg_item.author_id == 0:
                author_prefix = f"<i><b>🔵 {utils.escape(msg_item.author or 'FunPay')}: </b></i>"
            elif msg_item.is_employee:
                author_prefix = f"<i><b>🆘 {utils.escape(msg_item.author or 'Support')} ({utils.escape(msg_item.badge or '')}): </b></i>"
            elif msg_item.author == msg_item.chat_name:
                author_prefix = f"<i><b>👤 {utils.escape(msg_item.author or 'User')}: </b></i>"
                if msg_item.is_autoreply:
                    author_prefix = f"<i><b>🛍️ {utils.escape(msg_item.author or 'User')} ({utils.escape(msg_item.badge or '')}):</b></i> "
                elif msg_item.author and msg_item.author in self.cortex.blacklist:
                    author_prefix = f"<i><b>🚷 {utils.escape(msg_item.author)}: </b></i>"
                elif msg_item.by_bot and msg_item.author_id != self.cortex.account.id :
                     author_prefix = f"<i><b>👾 {utils.escape(msg_item.author or 'Bot')}: </b></i>"
            else:
                author_prefix = f"<i><b>⚖️ {utils.escape(msg_item.author or 'Arbiter')} ({_('support')}): </b></i>"

            message_content_text = msg_item.text
            if msg_item.image_link:
                 message_content_text = f"<a href=\"{msg_item.image_link}\">" \
                                     f"{utils.escape(msg_item.image_name) if self.cortex.MAIN_CFG['NewMessageView'].getboolean('showImageName') and not (msg_item.author_id == self.cortex.account.id and msg_item.by_bot) else _('photo')}</a>"

            text_to_send += f"{author_prefix}{utils.escape(message_content_text or '')}\n\n"

            last_author_id = msg_item.author_id
            last_by_bot_flag = msg_item.by_bot
            last_author_badge = msg_item.badge
            last_by_fpcortex = msg_item.by_bot and msg_item.author_id == self.cortex.account.id

        text_to_send = text_to_send.strip()
        if not text_to_send: text_to_send = f"<i>({_('no_messages_to_display')})</i>"

        try:
            self.bot.edit_message_text(text_to_send, c.message.chat.id, c.message.id,
                                   reply_markup=kb.reply(int(chat_id_str), username, False, False))
        except ApiTelegramException as e:
            if e.error_code == 400 and "message is not modified" in e.description.lower():
                pass
            else:
                logger.error(f"Ошибка при расширении уведомления: {e}")
                logger.debug("TRACEBACK", exc_info=True)
        self.bot.answer_callback_query(c.id)


    def ask_confirm_refund(self, call: CallbackQuery):
        split_data = call.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        refund_confirm_keyboard = kb.new_order(order_id, username, node_id, confirmation=True)
        try:
            self.bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=refund_confirm_keyboard)
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(call.id)

    def cancel_refund(self, call: CallbackQuery):
        split_data = call.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        order_keyboard = kb.new_order(order_id, username, node_id)
        try:
            self.bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=order_keyboard)
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(call.id)

    def refund(self, c: CallbackQuery):
        split_data = c.data.split(":")
        order_id, node_id, username = split_data[1], int(split_data[2]), split_data[3]
        progress_message = None
        attempts_left = 3
        refund_successful = False
        while attempts_left > 0:
            try:
                self.cortex.account.refund(order_id)
                refund_successful = True
                break
            except Exception as e:
                logger.error(f"Ошибка возврата заказа #{order_id}, попытка {4 - attempts_left}: {e}")
                logger.debug("TRACEBACK", exc_info=True)
                attempt_message_text = _("refund_attempt", order_id, attempts_left -1)
                try:
                    if not progress_message:
                        progress_message = self.bot.send_message(c.message.chat.id, attempt_message_text)
                    else:
                        self.bot.edit_message_text(attempt_message_text, progress_message.chat.id, progress_message.id)
                except ApiTelegramException as tg_api_err:
                     logger.warning(f"Не удалось обновить сообщение о прогрессе возврата: {tg_api_err}")
                attempts_left -= 1
                if attempts_left > 0: time.sleep(1)
        final_message_text = _("refund_complete", order_id) if refund_successful else _("refund_error", order_id)
        try:
            if not progress_message:
                self.bot.send_message(c.message.chat.id, final_message_text)
            else:
                self.bot.edit_message_text(final_message_text, progress_message.chat.id, progress_message.id)
        except ApiTelegramException as tg_api_err_final:
             logger.warning(f"Не удалось отправить/изменить финальное сообщение о возврате: {tg_api_err_final}")

        order_keyboard_after_refund = kb.new_order(order_id, username, node_id, no_refund=refund_successful)
        try:
            self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=order_keyboard_after_refund)
        except ApiTelegramException as tg_api_err_kb:
            if tg_api_err_kb.error_code == 400 and "message to edit not found" in tg_api_err_kb.description.lower():
                logger.warning(f"Не удалось обновить клавиатуру для заказа {order_id}: исходное сообщение не найдено.")
            elif "message is not modified" not in tg_api_err_kb.description:
                logger.warning(f"Не удалось обновить клавиатуру для заказа {order_id}: {tg_api_err_kb}")
        self.bot.answer_callback_query(c.id)

    def open_order_menu(self, c: CallbackQuery):
        split_data = c.data.split(":")
        node_id, username, order_id = int(split_data[1]), split_data[2], split_data[3]
        no_refund_flag = bool(int(split_data[4]))
        try:
            self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=kb.new_order(order_id, username, node_id, no_refund=no_refund_flag))
        except ApiTelegramException as e:
            if e.error_code == 400 and "message is not modified" in e.description.lower(): pass
            else: raise e
        self.bot.answer_callback_query(c.id)


    def open_cp(self, c: CallbackQuery):
        desc_text = _("desc_main")
        try:
            if c.message.content_type == 'text':
                self.bot.edit_message_text(desc_text, c.message.chat.id, c.message.id,
                                       reply_markup=skb.SETTINGS_SECTIONS(self.cortex, c.from_user.id))
            else:
                try: self.bot.delete_message(c.message.chat.id, c.message.id)
                except: pass
                self.bot.send_message(c.message.chat.id, desc_text, reply_markup=skb.SETTINGS_SECTIONS(self.cortex, c.from_user.id))
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(c.id)

    def open_cp2(self, c: CallbackQuery):
        desc_text = _("desc_main")
        try:
            if c.message.content_type == 'text':
                self.bot.edit_message_text(desc_text, c.message.chat.id, c.message.id,
                                       reply_markup=skb.SETTINGS_SECTIONS_2(self.cortex, c.from_user.id))
            else:
                try: self.bot.delete_message(c.message.chat.id, c.message.id)
                except: pass
                self.bot.send_message(c.message.chat.id, desc_text, reply_markup=skb.SETTINGS_SECTIONS_2(self.cortex, c.from_user.id))
        except ApiTelegramException as e:
            if "message is not modified" not in e.description:
                raise
        self.bot.answer_callback_query(c.id)


    def switch_param(self, c: CallbackQuery):
        split_data = c.data.split(":")
        section_name, option_name = split_data[1], split_data[2]
        if section_name == "FunPay" and option_name == "oldMsgGetMode":
            self.cortex.switch_msg_get_mode()
        else:
            current_value_str = self.cortex.MAIN_CFG[section_name].get(option_name, "0")
            new_value = str(int(not int(current_value_str)))
            self.cortex.MAIN_CFG[section_name][option_name] = new_value
            self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")

        section_keyboards_map = {
            "FunPay": kb.main_settings, "BlockList": kb.blacklist_settings,
            "NewMessageView": kb.new_message_view_settings, "Greetings": kb.greeting_settings,
            "OrderConfirm": kb.order_confirm_reply_settings, "ReviewReply": kb.review_reply_settings,
            "Proxy": lambda ctx, offset_kb: kb.proxy(ctx, offset_kb, getattr(ctx.telegram, 'pr_dict', {})),
            "ManagerPermissions": kb.manager_permissions_settings,
            "Statistics": lambda ctx: kb.statistics_settings(ctx, c.message.chat.id),
            "OrderControl": kb.order_control_settings,
        }
        reply_markup_to_send = None
        if section_name == "Telegram":
             offset_val = int(split_data[3]) if len(split_data) > 3 else 0
             reply_markup_to_send = kb.authorized_users(self.cortex, offset_val, c.from_user.id)
        elif section_name == "Proxy":
             offset_val = int(split_data[3]) if len(split_data) > 3 else 0
             pr_dict_for_kb = getattr(self.cortex.telegram, 'pr_dict', {})
             reply_markup_to_send = kb.proxy(self.cortex, offset_val, pr_dict_for_kb)
        elif section_name in section_keyboards_map:
            kb_gen = section_keyboards_map[section_name]
            reply_markup_to_send = kb_gen(self.cortex)

        if reply_markup_to_send:
            try:
                self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id, reply_markup=reply_markup_to_send)
            except ApiTelegramException as e:
                if e.error_code == 400 and "message is not modified" in e.description.lower(): pass
                else: raise e
        else:
            self.bot.answer_callback_query(c.id, "✅")

        logger.info(_("log_param_changed", c.from_user.username, c.from_user.id, option_name, section_name,
                      self.cortex.MAIN_CFG[section_name][option_name]))
        if not reply_markup_to_send: self.bot.answer_callback_query(c.id)


    def switch_chat_notification(self, c: CallbackQuery):
        split_data = c.data.split(":")
        chat_id_for_notif_str, notification_type_str = split_data[1], split_data[2]
        chat_id_for_notif = int(chat_id_for_notif_str)

        toggle_result = self.toggle_notification(chat_id_for_notif, notification_type_str)
        logger.info(_("log_notification_switched", c.from_user.username, c.from_user.id,
                      notification_type_str, c.message.chat.id, toggle_result))
        reply_kb_generator = kb.notifications_settings
        if notification_type_str in [NotificationTypes.announcement, NotificationTypes.ad]:
            reply_kb_generator = kb.announcements_settings

        try:
            self.bot.edit_message_reply_markup(c.message.chat.id, c.message.id,
                                           reply_markup=reply_kb_generator(self.cortex, c.message.chat.id))
        except ApiTelegramException as e:
            if e.error_code == 400 and "message is not modified" in e.description.lower(): pass
            else: raise e
        self.bot.answer_callback_query(c.id)


    def open_settings_section(self, c: CallbackQuery):
        section_key = c.data.split(":")[1]
        user_id = c.from_user.id
        
        user_role = utils.get_user_role(self.authorized_users, user_id)
        admin_only_sections = ["main", "bl", "au", "proxy", "mp"]
        
        if section_key in admin_only_sections and user_role != "admin":
            self.bot.answer_callback_query(c.id, _("admin_only_command"), show_alert=True)
            return
        
        manager_only_sections = ["orc"]
        if section_key in manager_only_sections and user_role == "manager" and not self.cortex.MAIN_CFG["ManagerPermissions"].getboolean("can_control_orders", False):
            self.bot.answer_callback_query(c.id, _("manager_permission_denied"), show_alert=True)
            return

        sections_map = {
            "lang": (_("desc_lang"), kb.language_settings, [self.cortex]),
            "main": (_("desc_gs"), kb.main_settings, [self.cortex]),
            "tg": (_("desc_ns", c.message.chat.id), kb.notifications_settings, [self.cortex, c.message.chat.id]),
            "bl": (_("desc_bl"), kb.blacklist_settings, [self.cortex]),
            "ar": (_("desc_ar"), skb.AR_SETTINGS, []),
            "ad": (_("desc_ad"), skb.AD_SETTINGS, []),
            "mv": (_("desc_mv"), kb.new_message_view_settings, [self.cortex]),
            "rr": (_("desc_or"), kb.review_reply_settings, [self.cortex]),
            "gr": (_("desc_gr", utils.escape(self.cortex.MAIN_CFG['Greetings']['greetingsText'])),
                   kb.greeting_settings, [self.cortex]),
            "oc": (_("desc_oc", utils.escape(self.cortex.MAIN_CFG['OrderConfirm']['replyText'])),
                   kb.order_confirm_reply_settings, [self.cortex]),
            "orc": (_("oc_menu_desc"), kb.order_control_settings, [self.cortex]),
            "au": (_("desc_au"), lambda c_instance, o: kb.authorized_users(c_instance, o, user_id), [self.cortex, 0]),
            "mp": (_("desc_mp"), kb.manager_permissions_settings, [self.cortex])
        }
        current_section_data = sections_map.get(section_key)
        if current_section_data:
            desc_text, kb_generator, kb_args = current_section_data
            try:
                if c.message.content_type == 'text':
                    self.bot.edit_message_text(desc_text, c.message.chat.id, c.message.id, reply_markup=kb_generator(*kb_args))
                else:
                    try: self.bot.delete_message(c.message.chat.id, c.message.id)
                    except: pass
                    self.bot.send_message(c.message.chat.id, desc_text, reply_markup=kb_generator(*kb_args))
            except ApiTelegramException as e:
                if "message is not modified" not in e.description:
                    raise
        else:
            self.bot.answer_callback_query(c.id, _("unknown_action"), show_alert=True)
            return
        self.bot.answer_callback_query(c.id)

    def cancel_action(self, call: CallbackQuery):
        clear_result = self.clear_state(call.message.chat.id, call.from_user.id, True)
        self.bot.answer_callback_query(call.id)


    def param_disabled(self, c: CallbackQuery):
        self.bot.answer_callback_query(c.id, _("param_disabled"), show_alert=True)

    def send_announcements_kb(self, m: Message):
        self.bot.send_message(m.chat.id, _("desc_an"), reply_markup=kb.announcements_settings(self.cortex, m.chat.id))

    def send_review_reply_text(self, c: CallbackQuery):
        stars_count = int(c.data.split(":")[1])
        reply_text = self.cortex.MAIN_CFG["ReviewReply"][f"star{stars_count}ReplyText"]
        edit_keyboard = K() \
            .row(B(_("gl_back"), callback_data=f"{CBT.CATEGORY}:rr"),
                 B(_("gl_edit"), callback_data=f"{CBT.EDIT_REVIEW_REPLY_TEXT}:{stars_count}"))
        if not reply_text:
            self.bot.send_message(c.message.chat.id, _("review_reply_empty", "⭐" * stars_count), reply_markup=edit_keyboard)
        else:
            self.bot.send_message(c.message.chat.id, _("review_reply_text", "⭐" * stars_count,
                                                       utils.escape(reply_text)),
                                  reply_markup=edit_keyboard)
        self.bot.answer_callback_query(c.id)

    def send_old_mode_help_text(self, c: CallbackQuery):
        self.bot.answer_callback_query(c.id)
        self.bot.send_message(c.message.chat.id, _("old_mode_help"))

    def empty_callback(self, c: CallbackQuery):
        self.bot.answer_callback_query(c.id, "👍")

    def switch_lang(self, c: CallbackQuery):
        selected_lang = c.data.split(":")[1]
        Localizer(selected_lang)
        self.cortex.MAIN_CFG["Other"]["language"] = selected_lang
        self.cortex.save_config(self.cortex.MAIN_CFG, "configs/_main.cfg")
        self.setup_commands()
        alert_message = None
        if selected_lang == "en":
            alert_message = "The translation may be incomplete and contain errors.\n\n" \
                            "If you find errors, please let @beedge know.\n\nThank you :)"
        elif selected_lang == "uk":
            alert_message = "Переклад може бути неповним та містити помилки.\n\n" \
                            "Повідомте @beedge, якщо знайдете неточності."
        if alert_message:
            self.bot.answer_callback_query(c.id, alert_message, show_alert=True)
        else:
            self.bot.answer_callback_query(c.id)
        c.data = f"{CBT.CATEGORY}:lang"
        self.open_settings_section(c)

    def close_menu(self, c: CallbackQuery):
        try:
            self.bot.delete_message(c.message.chat.id, c.message.id)
            self.bot.answer_callback_query(c.id)
        except ApiTelegramException:
            self.bot.answer_callback_query(c.id, _("menu_closed"), show_alert=True)

    def send_help_text(self, c: CallbackQuery):
        help_key = c.data.split(":")[1]
        help_text = _(help_key)
        if help_text == help_key:
            help_text = _("help_not_found")
        
        try:
            self.bot.send_message(c.message.chat.id, help_text, reply_markup=K().add(B(_('gl_close'), callback_data=CBT.DELETE_MESSAGE)))
            self.bot.answer_callback_query(c.id)
        except ApiTelegramException as e:
            logger.error(f"Ошибка при отправке справки: {e}")
            self.bot.answer_callback_query(c.id, _("gl_error"), show_alert=True)

    def delete_message_cb(self, c: CallbackQuery):
        try:
            self.bot.delete_message(c.message.chat.id, c.message.id)
            self.bot.answer_callback_query(c.id)
        except ApiTelegramException:
            self.bot.answer_callback_query(c.id)

    # ==================== CRM ====================
    def act_add_note(self, m: Message):
        """Активирует режим добавления заметки к клиенту."""
        result = self.bot.send_message(m.chat.id, _("crm_prompt_add_note"), reply_markup=skb.CLEAR_STATE_BTN())
        self.set_state(m.chat.id, result.id, m.from_user.id, "add_note")

    def add_note(self, m: Message):
        """Добавляет заметку к клиенту."""
        self.clear_state(m.chat.id, m.from_user.id, True)
        parts = m.text.split(maxsplit=1)
        if len(parts) < 2:
            self.bot.reply_to(m, _("crm_err_note_format"))
            return
        
        username, note_text = parts
        customer_id = None
        for uid, data in self.cortex.crm_data.items():
            if data.get("username") == username:
                customer_id = uid
                break
        
        if customer_id is None:
            self.bot.reply_to(m, _("crm_err_customer_not_found", username=utils.escape(username)))
            return

        self.cortex.crm_data[customer_id]["notes"] = note_text
        crm_cp.save_crm_data(self.cortex)
        self.bot.reply_to(m, _("crm_success_note_added", username=utils.escape(username)))


    def __register_handlers(self):
        self.mdw_handler(self.setup_chat_notifications, update_types=['message'])

        # Обработка любых текстовых сообщений от неавторизованных пользователей
        self.msg_handler(self.handle_unauthorized_message,
                         func=lambda m: m.text is not None and m.from_user.id not in self.authorized_users,
                         content_types=['text'])
        
        # Блокировка всех кнопок для неавторизованных
        self.cbq_handler(self.ignore_unauthorized_users, lambda c: c.from_user.id not in self.authorized_users)
        
        # Общие колбэки для всех
        self.cbq_handler(self.param_disabled, lambda c: c.data.startswith(CBT.PARAM_DISABLED))

        # Обработчики для авторизованных пользователей
        auth_filter = lambda msg: msg.from_user.id in self.authorized_users
        auth_cb_filter = lambda call: call.from_user.id in self.authorized_users

        self.msg_handler(self.run_file_handlers, content_types=["photo", "document"], func=lambda m: self.is_file_handler(m) and auth_filter(m))
        self.msg_handler(self.send_settings_menu, commands=["menu", "start"], func=auth_filter)
        self.msg_handler(self.send_statistics_menu, commands=["profile"], func=auth_filter)
        self.msg_handler(self.act_change_cookie, commands=["change_cookie", "golden_key"], func=auth_filter)
        self.msg_handler(self.change_cookie, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.CHANGE_GOLDEN_KEY) and auth_filter(m))
        self.cbq_handler(self.update_profile, lambda c: c.data == CBT.UPDATE_PROFILE and auth_cb_filter(c))
        self.msg_handler(self.act_manual_delivery_test, commands=["test_lot"], func=auth_filter)
        self.msg_handler(self.act_upload_image, commands=["upload_chat_img", "upload_offer_img"], func=auth_filter)
        self.cbq_handler(self.act_edit_greetings_text, lambda c: c.data == CBT.EDIT_GREETINGS_TEXT and auth_cb_filter(c))
        self.msg_handler(self.edit_greetings_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_GREETINGS_TEXT) and auth_filter(m))
        self.cbq_handler(self.act_edit_greetings_cooldown, lambda c: c.data == CBT.EDIT_GREETINGS_COOLDOWN and auth_cb_filter(c))
        self.msg_handler(self.edit_greetings_cooldown, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_GREETINGS_COOLDOWN) and auth_filter(m))
        self.cbq_handler(self.act_edit_order_confirm_reply_text, lambda c: c.data == CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT and auth_cb_filter(c))
        self.msg_handler(self.edit_order_confirm_reply_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_ORDER_CONFIRM_REPLY_TEXT) and auth_filter(m))
        self.cbq_handler(self.act_edit_review_reply_text, lambda c: c.data.startswith(f"{CBT.EDIT_REVIEW_REPLY_TEXT}:") and auth_cb_filter(c))
        self.msg_handler(self.edit_review_reply_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_REVIEW_REPLY_TEXT) and auth_filter(m))
        self.msg_handler(self.manual_delivery_text, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.MANUAL_AD_TEST) and auth_filter(m))
        self.msg_handler(self.act_ban, commands=["ban"], func=auth_filter)
        self.msg_handler(self.ban, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.BAN) and auth_filter(m))
        self.msg_handler(self.act_unban, commands=["unban"], func=auth_filter)
        self.msg_handler(self.unban, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.UNBAN) and auth_filter(m))
        self.msg_handler(self.send_ban_list, commands=["black_list"], func=auth_filter)
        self.msg_handler(self.act_edit_watermark, commands=["watermark"], func=auth_filter)
        self.msg_handler(self.edit_watermark, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.EDIT_WATERMARK) and auth_filter(m))
        self.msg_handler(self.send_logs, commands=["logs"], func=auth_filter)
        self.msg_handler(self.del_logs, commands=["del_logs"], func=auth_filter)
        self.msg_handler(self.about, commands=["about"], func=auth_filter)
        self.msg_handler(self.check_updates, commands=["check_updates"], func=auth_filter)
        self.msg_handler(self.update, commands=["update"], func=auth_filter)
        self.msg_handler(self.get_backup, commands=["get_backup"], func=auth_filter)
        self.msg_handler(self.create_backup, commands=["create_backup"], func=auth_filter)
        self.msg_handler(self.send_system_info, commands=["sys"], func=auth_filter)
        self.msg_handler(self.restart_cortex, commands=["restart"], func=auth_filter)
        self.msg_handler(self.ask_power_off, commands=["power_off"], func=auth_filter)
        self.msg_handler(self.send_announcements_kb, commands=["announcements"], func=auth_filter)
        self.msg_handler(self.act_add_note, commands=["note"], func=auth_filter)
        self.msg_handler(self.add_note, func=lambda m: self.check_state(m.chat.id, m.from_user.id, "add_note") and auth_filter(m))

        self.cbq_handler(self.send_review_reply_text, lambda c: c.data.startswith(f"{CBT.SEND_REVIEW_REPLY_TEXT}:") and auth_cb_filter(c))
        self.cbq_handler(self.act_send_funpay_message, lambda c: c.data.startswith(f"{CBT.SEND_FP_MESSAGE}:") and auth_cb_filter(c))
        self.cbq_handler(self.open_reply_menu, lambda c: c.data.startswith(f"{CBT.BACK_TO_REPLY_KB}:") and auth_cb_filter(c))
        self.cbq_handler(self.extend_new_message_notification, lambda c: c.data.startswith(f"{CBT.EXTEND_CHAT}:") and auth_cb_filter(c))
        self.msg_handler(self.send_funpay_message, func=lambda m: self.check_state(m.chat.id, m.from_user.id, CBT.SEND_FP_MESSAGE) and auth_filter(m))
        self.cbq_handler(self.ask_confirm_refund, lambda c: c.data.startswith(f"{CBT.REQUEST_REFUND}:") and auth_cb_filter(c))
        self.cbq_handler(self.cancel_refund, lambda c: c.data.startswith(f"{CBT.REFUND_CANCELLED}:") and auth_cb_filter(c))
        self.cbq_handler(self.refund, lambda c: c.data.startswith(f"{CBT.REFUND_CONFIRMED}:") and auth_cb_filter(c))
        self.cbq_handler(self.open_order_menu, lambda c: c.data.startswith(f"{CBT.BACK_TO_ORDER_KB}:") and auth_cb_filter(c))
        self.cbq_handler(self.open_cp, lambda c: c.data == CBT.MAIN and auth_cb_filter(c))
        self.cbq_handler(self.open_cp2, lambda c: c.data == CBT.MAIN2 and auth_cb_filter(c))
        self.cbq_handler(self.open_settings_section, lambda c: c.data.startswith(f"{CBT.CATEGORY}:") and auth_cb_filter(c))
        self.cbq_handler(self.switch_param, lambda c: c.data.startswith(f"{CBT.SWITCH}:") and auth_cb_filter(c))
        self.cbq_handler(self.switch_chat_notification, lambda c: c.data.startswith(f"{CBT.SWITCH_TG_NOTIFICATIONS}:") and auth_cb_filter(c))
        self.cbq_handler(self.power_off, lambda c: c.data.startswith(f"{CBT.SHUT_DOWN}:") and auth_cb_filter(c))
        self.cbq_handler(self.cancel_power_off, lambda c: c.data == CBT.CANCEL_SHUTTING_DOWN and auth_cb_filter(c))
        self.cbq_handler(self.cancel_action, lambda c: c.data == CBT.CLEAR_STATE and auth_cb_filter(c))
        self.cbq_handler(self.send_old_mode_help_text, lambda c: c.data == CBT.OLD_MOD_HELP and auth_cb_filter(c))
        self.cbq_handler(self.empty_callback, lambda c: c.data == CBT.EMPTY and auth_cb_filter(c))
        self.cbq_handler(self.switch_lang, lambda c: c.data.startswith(f"{CBT.LANG}:") and auth_cb_filter(c))
        self.cbq_handler(self.close_menu, lambda c: c.data == CBT.CLOSE_MENU and auth_cb_filter(c))
        self.cbq_handler(self.send_help_text, lambda c: c.data.startswith(f"{CBT.SEND_HELP}:") and auth_cb_filter(c))
        self.cbq_handler(self.delete_message_cb, lambda c: c.data == CBT.DELETE_MESSAGE and auth_cb_filter(c))
        self.cbq_handler(self.send_advanced_profile_stats, lambda c: c.data == CBT.ADV_PROFILE_STATS and auth_cb_filter(c))
        self.cbq_handler(lambda c: self.send_profile(c), func=lambda c: c.data == "profile_view" and auth_cb_filter(c))


    def send_notification(self, text: str | None, keyboard: K | None = None,
                          notification_type: str = utils.NotificationTypes.other, photo: bytes | None = None,
                          pin: bool = False, exclude_chat_id: int | None = None, chat_id: int | None = None):
        kwargs = {}
        if keyboard is not None:
            kwargs["reply_markup"] = keyboard
        to_delete_chats = []

        if chat_id:
            chats_to_notify = {str(chat_id): self.notification_settings.get(str(chat_id), {})}
        else:
            chats_to_notify = self.notification_settings.copy()

        for chat_id_str, settings in chats_to_notify.items():
            if exclude_chat_id and str(exclude_chat_id) == chat_id_str:
                continue

            if notification_type not in [NotificationTypes.critical, NotificationTypes.important_announcement] and \
               not settings.get(notification_type, False):
                continue
            if notification_type == NotificationTypes.critical:
                is_admin_primary_chat = False
                try:
                    user_id = int(chat_id_str)
                    if user_id in self.authorized_users and self.authorized_users[user_id].get("role") == "admin":
                        is_admin_primary_chat = True
                except ValueError:
                    pass

                if not is_admin_primary_chat :
                    continue

            if notification_type == NotificationTypes.important_announcement and not settings.get(NotificationTypes.announcement, False):
                continue


            try:
                if photo:
                    msg = self.bot.send_photo(chat_id_str, photo, caption=text, **kwargs)
                else:
                    msg = self.bot.send_message(chat_id_str, text, **kwargs)

                if notification_type == utils.NotificationTypes.bot_start:
                    self.init_messages.append((msg.chat.id, msg.id))
                if pin:
                    try:
                        self.bot.pin_chat_message(msg.chat.id, msg.id, disable_notification=True)
                    except ApiTelegramException as pin_e:
                        logger.warning(f"Не удалось закрепить сообщение в чате {msg.chat.id}: {pin_e.description}")
                    except Exception as e_pin_generic:
                        logger.error(f"Непредвиденная ошибка при закреплении сообщения в чате {msg.chat.id}: {e_pin_generic}")

            except requests.exceptions.ConnectionError as e_conn:
                logger.error(f"Ошибка соединения при отправке уведомления в чат {chat_id_str}: {e_conn}")
                time.sleep(10)
                continue
            except ApiTelegramException as e:
                logger.error(_("log_tg_notification_error", chat_id_str) + f" (API Error: {e.error_code} - {e.description})")
                logger.debug("TRACEBACK", exc_info=True)
                if e.error_code in [400, 403] and \
                   ("chat not found" in e.description.lower() or \
                    "bot was blocked by the user" in e.description.lower() or \
                    "user is deactivated" in e.description.lower() or \
                    "bot was kicked from the group chat" in e.description.lower() or \
                    "group chat was upgraded to a supergroup chat" in e.description.lower()):
                    to_delete_chats.append(chat_id_str)
            except Exception as e_generic:
                logger.error(_("log_tg_notification_error", chat_id_str) + f" (Generic Error: {e_generic})")
                logger.debug("TRACEBACK", exc_info=True)
                continue

        if to_delete_chats:
            for chat_id_del in to_delete_chats:
                if chat_id_del in self.notification_settings:
                    del self.notification_settings[chat_id_del]
                    logger.info(f"Настройки уведомлений для чата {chat_id_del} удалены, т.к. бот был заблокирован или удален из чата.")
            if to_delete_chats:
                utils.save_notification_settings(self.notification_settings)


    def add_command_to_menu(self, command: str, help_text_key: str) -> None:
        self.commands[command] = help_text_key

    def setup_commands(self):
        for lang_code in [None] + list(localizer.languages.keys()):
            try:
                bot_commands = [BotCommand(f"/{cmd_key}", _(help_text_key, language=lang_code))
                                for cmd_key, help_text_key in self.commands.items()]
                self.bot.set_my_commands(bot_commands, language_code=lang_code)
                if lang_code is None : logger.info("Команды Telegram бота (по умолчанию) установлены.")
                else: logger.info(f"Команды Telegram бота для языка '{lang_code}' установлены.")
            except ApiTelegramException as e:
                logger.error(f"Не удалось установить команды для языка '{lang_code or 'default'}': {e.description}")
            except Exception as e_gen:
                 logger.error(f"Непредвиденная ошибка при установке команд для языка '{lang_code or 'default'}': {e_gen}")


    def edit_bot(self):
        for lang_code in [None] + list(localizer.languages.keys()):
            if lang_code is None:
                try:
                    bot_me = self.bot.get_me()
                    current_name = bot_me.full_name
                    new_bot_name = "FPCortex"
                    name_suffix_options = [" 🚀", " | FunPay Bot", " ✨"]
                    if len(new_bot_name) < 30:
                        for suffix in name_suffix_options:
                            if len(new_bot_name) + len(suffix) <= 32:
                                new_bot_name += suffix
                                break
                    if new_bot_name != current_name:
                         self.bot.set_my_name(new_bot_name)
                         logger.info(f"Имя бота изменено на: {new_bot_name}")
                except ApiTelegramException as e:
                    logger.error(f"Не удалось изменить имя бота: {e.description}")
                except Exception as e_name_gen:
                    logger.error(f"Непредвиденная ошибка при изменении имени бота: {e_name_gen}")


            new_short_description = _("adv_fpc", language=lang_code)
            try:
                current_short_desc_obj = self.bot.get_my_short_description(language_code=lang_code)
                if current_short_desc_obj.short_description != new_short_description:
                    self.bot.set_my_short_description(new_short_description, language_code=lang_code)
                    logger.info(f"Короткое описание бота для языка '{lang_code or 'default'}' изменено.")
            except ApiTelegramException as e:
                logger.error(f"Не удалось изменить короткое описание бота для языка '{lang_code or 'default'}': {e.description}")
            except Exception as e_short_desc_gen:
                logger.error(f"Непредвиденная ошибка при изменении короткого описания для языка '{lang_code or 'default'}': {e_short_desc_gen}")

            new_full_description = _("adv_description", self.cortex.VERSION, language=lang_code)
            try:
                current_full_desc_obj = self.bot.get_my_description(language_code=lang_code)
                if current_full_desc_obj.description != new_full_description:
                    self.bot.set_my_description(new_full_description, language_code=lang_code)
                    logger.info(f"Полное описание бота для языка '{lang_code or 'default'}' изменено.")
            except ApiTelegramException as e:
                logger.error(f"Не удалось изменить полное описание бота для языка '{lang_code or 'default'}': {e.description}")
            except Exception as e_full_desc_gen:
                logger.error(f"Непредвиденная ошибка при изменении полного описания для языка '{lang_code or 'default'}': {e_full_desc_gen}")


    def init(self):
        if self._initialized:
            return
        self.__register_handlers()
        self.setup_commands()
        self.edit_bot()
        self._initialized = True
        logger.info(_("log_tg_initialized"))

    def run(self):
        self.send_notification(_("bot_started"), notification_type=utils.NotificationTypes.bot_start)
        k_err_count = 0
        while True:
            try:
                bot_username = self.bot.get_me().username
                logger.info(_("log_tg_started", bot_username))
                self.bot.infinity_polling(logger_level=logging.WARNING, timeout=60, long_polling_timeout=30)
            except requests.exceptions.ConnectionError as e_conn:
                k_err_count += 1
                logger.error(_("log_tg_update_error", k_err_count) + f" (Connection Error: {e_conn})")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(60)
            except ApiTelegramException as e_api:
                k_err_count += 1
                logger.error(_("log_tg_update_error", k_err_count) + f" (API Error: {e_api.error_code} - {e_api.description})")
                logger.debug("TRACEBACK", exc_info=True)
                if e_api.error_code == 401:
                    logger.critical("Критическая ошибка: токен Telegram бота недействителен. Проверьте токен в _main.cfg. Бот остановлен.")
                    cortex_tools.shut_down()
                    break
                elif e_api.error_code == 409:
                     logger.critical("Критическая ошибка: обнаружен конфликт (409). Возможно, запущена другая копия бота с этим же токеном. Бот остановлен.")
                     cortex_tools.shut_down()
                     break
                time.sleep(30)
            except Exception as e:
                k_err_count += 1
                logger.error(_("log_tg_update_error", k_err_count) + f" (General Error: {e})")
                logger.debug("TRACEBACK", exc_info=True)
                time.sleep(15)

    def is_file_handler(self, m: Message) -> bool:
        state = self.get_state(m.chat.id, m.from_user.id)
        return state is not None and state["state"] in self.file_handlers