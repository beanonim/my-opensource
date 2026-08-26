# START OF FILE en.py

# Global
gl_next = "Next ▶️"
gl_back = "Back ◀️"
gl_yes = "Yes ✅"
gl_yep = "Yep ✅"
gl_no = "No ❌"
gl_cancel = "Cancel 🚫"
gl_error = "Error ⚠️"
gl_try_again = "Try again"
gl_error_try_again = f"{gl_error}. {gl_try_again}."
gl_refresh = "Refresh 🔄"
gl_delete = "Delete 🗑️"
gl_edit = "Edit ✏️"
gl_configure = "Configure ⚙️"
gl_pcs = "pcs."
gl_last_update = "Updated"
gl_refresh_and_try_again = "Refresh the list and try again."
gl_close = "Close"
menu_closed = "Menu closed."
help_not_found = "Help for this section was not found."

# - Main Menu
mm_language = "🌍 Language"
mm_global = "🔧 General Settings"
mm_notifications = "🔔 Notifications"
mm_autoresponse = "🤖 Auto-responder"
mm_autodelivery = "📦 Auto-delivery"
mm_blacklist = "🚫 Blacklist"
mm_templates = "📝 Response Templates"
mm_greetings = "👋 Greetings"
mm_order_confirm = "👍 Order Confirmation Reply"
mm_review_reply = "⭐ Review Reply"
mm_new_msg_view = "💬 Notification View"
mm_plugins = "🧩 Plugins"
mm_configs = "🔩 Configurations"
mm_authorized_users = "👤 Users"
mm_proxy = "🌐 Proxy"
mm_manager_settings = "🔑 Manager Settings"
mm_manager_permissions = "⚙️ Manager Permissions"
mm_order_control = "{} 🛂 Order control"
mp_can_control_orders = "{} 🛂 Order control"

# Global Switches
gs_autoraise = "{} Auto-boost listings"
gs_autoresponse = "{} Auto-responder"
gs_autodelivery = "{} Auto-delivery"
gs_nultidelivery = "{} Multi-delivery"
gs_autorestore = "{} Restore listings"
gs_autodisable = "{} Deactivate listings"
gs_old_msg_mode = "{} Legacy message mode"
gs_keep_sent_messages_unread = "{} Don't mark as read when sending"

# Notification Settings
ns_new_msg = "{} New message"
ns_cmd = "{} Command received"
ns_new_order = "{} New order"
ns_order_confirmed = "{} Order confirmed"
ns_lot_activate = "{} Listing restored"
ns_lot_deactivate = "{} Listing deactivated"
ns_delivery = "{} Item delivered"
ns_raise = "{} Listings boosted"
ns_new_review = "{} New review"
ns_bot_start = "{} Bot started"
ns_other = "{} Other (plugins)"

# Auto-responder Settings
ar_edit_commands = "✏️ Command Editor"
ar_add_command = "➕ New Command"
ar_to_ar = "🤖 To Auto-responder Settings"
ar_to_mm = "Menu 🏠"
ar_edit_response = "✏️ Response Text"
ar_edit_notification = "✏️ Notification Text"
ar_notification = "{} Notification in Telegram"
ar_add_more = "➕ More"
ar_add_another = "➕ Another"
ar_no_valid_commands_entered = "No valid commands were entered."
ar_default_response_text = "The response for this command has not been configured yet. Please edit it."
ar_default_notification_text = "User $username entered command: $message_text"
ar_command_deleted_successfully = "Command/set '{command_name}' successfully deleted."

# Auto-delivery Settings
ad_edit_autodelivery = "🗳️ Auto-delivery Editor"
ad_add_autodelivery = "➕ Link Auto-delivery"
ad_add_another_ad = "➕ Link Another"
ad_add_more_ad = "➕ Link More"
ad_edit_goods_file = "📋 Product Files"
ad_upload_goods_file = "📤 Upload File"
ad_create_goods_file = "➕ Create File"
ad_to_ad = "📦 To Auto-delivery Settings"
ad_to_mm = "menu 🏠"
never_updated = "never"
ad_default_response_text_new_lot = "Thank you for your purchase, $username!\nHere is your item:\n$product"

# - Edit Auto-delivery
ea_edit_delivery_text = "✏️ Delivery Text"
ea_link_goods_file = "🔗 Link Product File"
ea_delivery = "{} Auto-delivery"
ea_multidelivery = "{} Multi-delivery"
ea_restore = "{} Restoration"
ea_deactivate = "{} Deactivation"
ea_test = "🔑 Test Key"
ea_more_test = "🔑 Another Key"
ea_link_another_gf = "🔗 Another File"

# - Add Auto-delivery
fl_manual = "✍️ Enter manually"

# - Product Files
gf_add_goods = "➕ Add Products"
gf_download = "📥 Download"
gf_create_another = "➕ Create Another"
gf_create_more = "➕ Create More"
gf_add_more = "➕ Add More"
gf_try_add_again = "➕ Try Again"
lot_info_header = "Listing Information"
text_not_set = "(text not set)"
gf_infinity = "infinite"
gf_count_error = "counting error"
gf_file_not_found_short = "not found"
gf_not_linked = "not linked"
gf_file_created_now = "created now"
gf_file_creation_error_short = "creation error"
no_lots_using_file = "No listings are using this file."
gf_no_products_to_add = "No products were entered to be added."
gf_deleted_successfully = "File '{file_name}' successfully deleted."
gf_already_deleted = "File '{file_name}' was already deleted."


# Blacklist Settings
bl_autodelivery = "{} Do not deliver items"
bl_autoresponse = "{} Do not respond to commands"
bl_new_msg_notifications = "{} No notifications for new messages"
bl_new_order_notifications = "{} No notifications for new orders"
bl_command_notifications = "{} No notifications for commands"

# Response Templates
tmplt_add = "➕ New Template"
tmplt_add_more = "➕ More Templates"
tmplt_add_another = "➕ Another Template"
tmplt_editing_header = "📝 Editing Template"
tmplt_err_empty_text = "❌ Template text cannot be empty. Please enter text."
tmplt_deleted_successfully = "✅ Template '{template_text}' successfully deleted."

# Greeting Settings
gr_greetings = "{} Greet new users"
gr_ignore_sys_msgs = "{} Ignore system messages"
gr_edit_message = "✏️ Greeting Text"
gr_edit_cooldown = "⏱️ Cooldown: {} days"

# Order Confirmation Reply Settings
oc_watermark = "{} Watermark"
oc_send_reply = "{} Send reply"
oc_edit_message = "✏️ Reply Text"

# New Message Notification View Settings
mv_incl_my_msg = "{} My messages"
mv_incl_fp_msg = "{} FunPay messages"
mv_incl_bot_msg = "{} Bot messages"
mv_only_my_msg = "{} Only mine"
mv_only_fp_msg = "{} Only from FunPay"
mv_only_bot_msg = "{} Only from bot"
mv_show_image_name = "{} Image names"

# Plugins
pl_add = "➕ Add Plugin"
pl_activate = "🚀 Activate"
pl_deactivate = "💤 Deactivate"
pl_commands = "⌨️ Commands"
pl_settings = "⚙️ Settings"
pl_status_active = "Status: Active 🚀"
pl_status_inactive = "Status: Inactive 💤"
pl_no_commands = "This plugin has no registered commands."
pl_delete_handler_failed = "⚠️ Error executing delete handler for plugin '{plugin_name}'. The plugin has been removed from the list, but its data or files may remain. Check the logs."
pl_deleted_successfully = "✅ Plugin '{plugin_name}' successfully deleted. Restart FPCortex for the changes to take effect."
pl_file_delete_error = "⚠️ Failed to delete plugin file '{plugin_path}'. Check permissions and logs."
pl_safe_source = "Safe Plugins Source"
pl_channel_button = "FunPay Cortex Channel"

# Configs
cfg_download_main = "📥 Download Main"
cfg_download_ar = "📥 Download Auto-responder"
cfg_download_ad = "📥 Download Auto-delivery"
cfg_upload_main = "📤 Upload Main"
cfg_upload_ar = "📤 Upload Auto-responder"
cfg_upload_ad = "📤 Upload Auto-delivery"

# Authorized Users
tg_block_login = "{} Block password login"
role_admin = "👑 Administrator"
role_manager = "👤 Manager"
user_role = "Role"
promote_to_admin = "👑 Make Administrator"
demote_to_manager = "👤 Make Manager"
revoke_access = "🗑️ Revoke Access"
manager_settings_desc = "Here you can set a registration key for your managers. They will be able to use the bot with limited permissions.\n\n<b>Current key:</b> {}"
manager_key_not_set = "<i>(not set)</i>"
set_manager_key_btn = "🔑 Change Key"
enter_manager_key_prompt = "Enter a new registration key for managers. To delete the key, send <code>-</code>."
manager_key_changed_success = "✅ Manager registration key successfully changed."
user_access_revoked = "✅ Access for user {0} has been revoked."
user_role_changed_success = "✅ User {0}'s role has been changed to '{1}'."
demote_last_admin_error = "❌ You cannot demote the last administrator."
user_not_found = "User not found."
admin_only_command = "❌ This command is available only to the administrator."
manager_permission_denied = "❌ You do not have permission to execute this command."
role_change_already_admin = "You are already an administrator."
role_change_already_manager = "You are already a manager."
access_granted_role_changed = "Access updated! Your new role is: <b>{0}</b>. Open the menu with the /menu command."
manager_reg_admin_error = "❌ You are already an administrator. Logging in with a manager key is not possible."
manager_access_granted = "✅ Manager access granted! Open the menu with the /menu command."
au_exit_cp = "Exit Control Panel 🚪"

# Manager Permissions
mp_can_edit_ar = "{} Edit auto-responder"
mp_can_edit_ad = "{} Edit auto-delivery"
mp_can_edit_templates = "{} Edit templates"

# Proxy
prx_proxy_add = "➕ Add Proxy"
proxy_status_enabled = "Enabled"
proxy_status_disabled = "Disabled"
proxy_check_status_enabled = "Enabled"
proxy_check_status_disabled = "Disabled"
proxy_not_used_currently = "not currently in use"
proxy_not_selected = "not selected"
proxy_check_interval_info = "Auto-check interval: {interval} min."
proxy_global_status_header = "Global Proxy Module Status"
proxy_module_status_label = "Module state:"
proxy_health_check_label = "Auto-check proxy:"
proxy_current_in_use_label = "Current proxy in use:"
proxy_select_error_not_found = "⚠️ Error: this proxy no longer exists in the list."
proxy_select_error_invalid_format = "⚠️ Error: the selected proxy has an invalid format."
proxy_selected_and_applied = "✅ Proxy {proxy_str} has been selected and applied."
proxy_selected_not_applied = "ℹ️ Proxy {proxy_str} has been selected. Enable the proxy module in settings to start using it."
proxy_deleted_successfully = "✅ Proxy {proxy_str} has been successfully deleted from the list."
proxy_delete_error_not_found = "⚠️ Error: proxy to be deleted not found in the list."
proxy_undeletable = "❌ This proxy is in use and cannot be deleted."

# Announcements
an_an = "{} Announcements"
an_ad = "{} Advertisements"

# New Order
ord_refund = "💸 Refund"
ord_answer = "✉️ Reply"
ord_templates = "📝 Templates"

# New Message
msg_reply = "✉️ Reply"
msg_reply2 = "✉️ Again"
msg_templates = "📝 Templates"
msg_more = "🔎 More details"

# Message Texts
access_denied = """Hello, <b><i>{}</i></b>! 👋

Unfortunately, you do not have access. ⛔

🔑 Enter the <u><b>secret password</b></u> (for admin) or <u><b>registration key</b></u> (for manager) to log in.

✨ <b>FunPay Cortex</b> - your best assistant on FunPay!
📢 Learn more and join our community on the channel: <a href="https://t.me/FunPayCortex"><b>FunPay Cortex Channel</b></a>"""
access_granted = "Access granted! 🔓\n\n" \
                 "📢 Please note: notifications to <b><u>this chat</u></b> are not yet active.\n\n" \
                 "🔔 You can configure them in the menu.\n\n" \
                 "⚙️ Open <i>FPCortex</i> settings menu: /menu"
access_granted_notification = "<b>🚨 ATTENTION! 🚨\n\n\n</b>" * 3 + "\n\n\n🔐 User \"<a href=\"tg://user?id={1}\">{0}</a>\" " \
                                                                 "<b>(ID: {1}) has gained access to the Telegram control panel! 🔓</b>"
param_disabled = "❌ This setting is disabled globally and cannot be changed for this listing.\n\n" \
                 "🌍 Global settings are available here: " \
                 "/menu -> 🔧 General Settings."
old_mode_help = """<b>New message retrieval mode</b> 🚀
✅ <i>FPCortex</i> sees the entire chat history and all details of new messages.
✅ <i>FPCortex</i> can see images and forward them to <i>Telegram</i>.
✅ <i>FPCortex</i> accurately identifies the author: you, the other person, or arbitration.
❌ The chat becomes "read" (no longer highlighted in orange) as <i>FPCortex</i> reads the entire history.

<b>Legacy message retrieval mode</b> 🐢
✅ Chats you haven't read remain orange.
✅ Works slightly faster.
❌ <i>FPCortex</i> only sees the last message. If several messages arrive in a row, it will only see the last one.
❌ <i>FPCortex</i> cannot see images and cannot forward them.
❌ <i>FPCortex</i> does not always accurately identify the author. If the chat is unread, the message is from the other person; otherwise, it's from you. This logic can fail. Arbitration will also not be identified.

💡 If you press the <code>More details</code> button in a notification, <i>FPCortex</i> will "read" the chat, show the last 15 messages (including images), and can accurately identify the author."""
bot_started = """✅ Telegram bot started!
You can <b><u>configure configs</u></b> and <b><u>use all <i>Telegram</i> bot functions</u></b>.

⏳ <i>FPCortex</i> is <b><u>not yet initialized</u></b>, its functions are inactive.
When <i>FPCortex</i> starts, this message will change.

🕒 If initialization takes a long time, check the logs with the /logs command."""
fpc_init = """✅ <b><u>FPCortex initialized!</u></b>
ℹ️ <b><i>Version:</i></b> <code>{}</code>
👑 <b><i>Account:</i></b>  <code>{}</code> | <code>{}</code>
💰 <b><i>Balance:</i></b> <code>{}₽, {}$, {}€</code>
📊 <b><i>Active orders:</i></b>  <code>{}</code>

👨‍💻 <b><i>Author:</i></b> @beedge"""

create_test_ad_key = "Enter the listing name to test auto-delivery."
test_ad_key_created = """✅ A one-time key has been created for the listing '<code>{}</code>'.
Send the command below in the chat with the buyer to deliver the item:
<code>!autodelivery {}</code>"""
about = """<b>🧠 FPCortex 🧠 v{}</b>
<i>Author:</i> @beedge"""
sys_info = """<b>📊 System Summary</b>

<b>⚙️ CPU:</b>
{}
    Used by <i>FPCortex</i>: <code>{}%</code>

<b>💾 RAM:</b>
    Total:  <code>{} MB</code>
    Used:  <code>{} MB</code>
    Free:  <code>{} MB</code>
    Used by bot:  <code>{} MB</code>

<b>⏱️ Other:</b>
    Uptime:  <code>{}</code>
    Chat ID:  <code>{}</code>"""
act_blacklist = """Enter the user's nickname to add to the blacklist."""
already_blacklisted = "❌ User <code>{}</code> is already in the blacklist."
user_blacklisted = "✅ User <code>{}</code> has been added to the blacklist."
act_unban = "Enter the user's nickname to remove from the blacklist."
not_blacklisted = "❌ User <code>{}</code> is not in the blacklist."
user_unbanned = "✅ User <code>{}</code> has been removed from the blacklist."
blacklist_empty = "🚫 The blacklist is empty."
act_proxy = "Enter proxy in the format <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_already_exists = "❌ Proxy <code>{}</code> already exists."
proxy_added = "✅ Proxy <u>{}</u> successfully added."
proxy_format = "❌ Incorrect proxy format. Required: <u>login:password@ip:port</u> or <u>ip:port</u>."
proxy_adding_error = "⚠️ Error adding proxy."
proxy_undeletable = "❌ This proxy is in use and cannot be deleted."
act_edit_watermark = "Enter the new watermark text. Examples:\n{}\n<code>𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙</code>\n" \
                     "<code>FPCortex</code>\n<code>[FunPay / Cortex]</code>\n<code>𝑭𝑷𝑪𝒙</code>\n" \
                     "<code>FPCx</code>\n<code>🤖</code>\n<code>🧠</code>\n\n" \
                     "Examples can be copied and edited.\nNote that on FunPay, the 🧠 emoji " \
                     "may look different.\n\nTo remove the watermark, send <code>-</code>."
v_edit_watermark_current = "Current"
watermark_changed = "✅ Watermark changed."
watermark_deleted = "✅ Watermark deleted."
watermark_error = "⚠️ Invalid watermark."
logfile_not_found = "❌ Log file not found."
logfile_sending = "Sending log file (this may take some time)... ⏳"
logfile_error = "⚠️ Failed to send log file."
logfile_deleted = "🗑️ Deleted {} log file(s)."
update_no_tags = "❌ Failed to get the list of versions from GitHub. Please try again later."
update_lasted = "✅ You have the latest version of FPCortex {} installed."
update_get_error = "❌ Failed to get information about the new version from GitHub. Please try again later."
update_available = "✨ <b>A new version of FPCortex is available!</b> ✨\n\n{}"
update_update = "To update, enter the command /update"
update_backup = "✅ A backup has been created (configs, storage, plugins): <code>backup.zip</code>.\n\n" \
                "🔒 <b>IMPORTANT:</b> DO NOT SEND this archive to ANYONE. It contains all bot data and settings (including golden_key and products)."
update_backup_error = "⚠️ Failed to create backup."
update_backup_not_found = "❌ Backup not found."
update_downloaded = "✅ Update {} downloaded. Skipped {} items (if they were old releases). Installing..."
update_download_error = "⚠️ Error downloading update archive."
update_done = "✅ Update installed! Restart <i>FPCortex</i> with the /restart command."
update_done_exe = "✅ Update installed! The new <code>FPCortex.exe</code> is in the <code>update</code> folder. " \
                  "Turn off <i>FPCortex</i>, replace the old <code>FPCortex.exe</code> with the new one, " \
                  "and run <code>Start.bat</code>."
update_install_error = "⚠️ Error installing update."

restarting = "Restarting... 🚀"
power_off_0 = """<b>Are you sure you want to turn me off?</b> 🤔
You <b><u>won't be able to</u></b> turn me back on via <i>Telegram</i>!"""
power_off_1 = "Just in case... <b><u>Are you absolutely sure you want to turn me off?</u></b> 😟"
power_off_2 = """Just so you know:
you'll have to go to the server/computer and start me manually! 💻"""
power_off_3 = """I'm not insisting, but if you need to apply changes to the main config,
you can just restart me with the /restart command. 😉"""
power_off_4 = "Are you even reading my messages? 😉 Let's check: yes = no, no = yes. " \
              "I bet you're not even reading, and here I am, writing important information."
power_off_5 = "So, your final answer is... yes? 😏"
power_off_6 = "Alright, alright, shutting down... 💤"
power_off_cancelled = "Shutdown cancelled. Continuing to work! 👍"
power_off_error = "❌ This button is no longer relevant. Call the shutdown menu again."
enter_msg_text = "Enter the message text:"
msg_sent = "✅ Message sent to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sent_short = "✅ Message sent."
msg_sending_error = "⚠️ Failed to send message to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>."
msg_sending_error_short = "⚠️ Failed to send message."
send_img = "Send me an image 🖼️"
greeting_changed = "✅ Greeting text changed."
greeting_cooldown_changed = "✅ Greeting cooldown changed: {} days."
order_confirm_changed = "✅ Order confirmation reply text changed!"
review_reply_changed = "✅ Reply text for {}⭐ review changed!"
review_reply_empty = "⚠️ Reply for {}⭐ review is not set."
review_reply_text = "Reply for {}⭐ review:\n<code>{}</code>"
get_chat_error = "⚠️ Failed to get chat data."
viewing = "Viewing"
you = "You"
support = "tech support"
photo = "Photo"
refund_attempt = "⚠️ Failed to refund order <code>#{}</code>. Attempts left: <code>{}</code>."
refund_error = "❌ Failed to refund order <code>#{}</code>."
refund_complete = "✅ Funds for order <code>#{}</code> have been refunded."
updating_profile = "Updating account statistics... 📊"
profile_updating_error = "⚠️ Failed to update statistics."
acc_balance_available = "available"
act_change_golden_key = "🔑 Enter your golden_key:"
cookie_changed = "✅ golden_key successfully changed{}.\n"
cookie_changed2 = "Restart the bot with the /restart command to apply changes."
cookie_incorrect_format = "❌ Incorrect golden_key format. Please try again."
cookie_error = "⚠️ Failed to authorize. Perhaps an incorrect golden_key was entered?"
ad_lot_not_found_err = "⚠️ Listing with index <code>{}</code> not found."
ad_already_ad_err = "⚠️ Listing <code>{}</code> already has auto-delivery configured."
ad_lot_already_exists = "⚠️ Auto-delivery is already linked to listing <code>{}</code>."
ad_lot_linked = "✅ Auto-delivery linked to listing <code>{}</code>."
ad_link_gf = "Enter the name of the product file.\nTo unlink the file, send <code>-</code>\n\n" \
             "If the file does not exist, it will be created automatically."
ad_gf_unlinked = "✅ Product file unlinked from listing <code>{}</code>."
ad_gf_linked = "✅ File <code>storage/products/{}</code> linked to listing <code>{}</code>."
ad_gf_created_and_linked = "✅ File <code>storage/products/{}</code> has been <b><u>created</u></b> and linked to listing <code>{}</code>."
ad_creating_gf = "⏳ Creating file <code>storage/products/{}</code>..."
ad_product_var_err = "⚠️ A product file is linked to listing <code>{}</code>, but the delivery text does not contain the <code>$product</code> variable."
ad_product_var_err2 = "⚠️ Cannot link file: the delivery text does not contain the <code>$product</code> variable."
ad_text_changed = "✅ Delivery text for listing <code>{}</code> changed to:\n<code>{}</code>"
ad_updating_lots_list = "Updating listings and categories data... ⏳"
ad_lots_list_updating_err = "⚠️ Failed to update listings and categories data."
gf_not_found_err = "⚠️ Product file with index <code>{}</code> not found."
copy_lot_name = "Send the exact name of the listing (as on FunPay)."
act_create_gf = "Enter a name for the new product file (e.g., 'steam_keys')."
gf_name_invalid = "🚫 Invalid file name.\n\n" \
                  "Only <b><u>English</u></b> " \
                  "and <b><u>Russian</u></b> letters, numbers, and the symbols <code>_</code>, <code>-</code>, and <code>space</code> are allowed."
gf_already_exists_err = "⚠️ File <code>{}</code> already exists."
gf_creation_err = "⚠️ Error creating file <code>{}</code>."
gf_created = "✅ File <code>storage/products/{}</code> created."
gf_amount = "Products in file"
gf_uses = "Used in listings"
gf_send_new_goods = "Send the products to add. Each product on a new line (<code>Shift+Enter</code>)."
gf_add_goods_err = "⚠️ Failed to add products to the file."
gf_new_goods = "✅ Added <code>{}</code> product(s) to file <code>storage/products/{}</code>."
gf_empty_error = "📂 File storage/products/{} is empty."
gf_linked_err = "⚠️ File <code>storage/products/{}</code> is linked to one or more listings.\n" \
                "First, unlink it from all listings, then delete it."
gf_deleting_err = "⚠️ Failed to delete file <code>storage/products/{}</code>."
ar_cmd_not_found_err = "⚠️ Command with index <code>{}</code> not found."
ar_subcmd_duplicate_err = "⚠️ Command <code>{}</code> is duplicated in the set."
ar_cmd_already_exists_err = "⚠️ Command <code>{}</code> already exists."
ar_enter_new_cmd = "Enter a new command (or several, separated by <code>|</code>)."
ar_cmd_added = "✅ New command <code>{}</code> added."
ar_response_text = "Response text"
ar_notification_text = "Notification text"
ar_response_text_changed = "✅ Response text for command <code>{}</code> changed to:\n<code>{}</code>"
ar_notification_text_changed = "✅ Notification text for command <code>{}</code> changed to:\n<code>{}</code>"
cfg_main = "Main config. 🔒 IMPORTANT: DO NOT SEND this file to ANYONE."
cfg_ar = "Auto-responder config."
cfg_ad = "Auto-delivery config."
cfg_not_found_err = "⚠️ Config {} not found."
cfg_empty_err = "📂 Config {} is empty."
tmplt_not_found_err = "⚠️ Template with index <code>{}</code> not found."
tmplt_already_exists_err = "⚠️ This template already exists."
tmplt_added = "✅ Template added."
tmplt_msg_sent = "✅ Message from template sent to chat <a href=\"https://funpay.com/chat/?node={}\">{}</a>:\n\n<code>{}</code>"
pl_not_found_err = "⚠️ Plugin with UUID <code>{}</code> not found."
pl_file_not_found_err = "⚠️ File <code>{}</code> not found.\nRestart <i>FPCortex</i> with the /restart command."
pl_commands_list = "Commands for plugin <b><i>{}</i></b>:"
pl_author = "Author"
pl_new = "Send me the plugin file (.py).\n\n<b>☢️ WARNING!</b> Loading plugins from unverified sources can be dangerous."
au_user_settings = "Settings for user {}"
adv_fpc = "😎 FPCortex - your best assistant for FunPay!"
adv_description = """🧠 FPCortex v{} 🚀

🤖 Auto-delivery of goods
📈 Auto-boost listings
💬 Smart auto-responder
♻️ Auto-restore listings
📦 Auto-deactivation (if products run out)
🔝 Always online
📲 Telegram notifications
🕹️ Full control via Telegram
🧩 Plugin support
🌟 And much more!

👨‍💻 Author: @beedge"""
exit_from_cp_warning = "Are you sure you want to exit the control panel? This action will revoke your access."
exit_from_cp_success = "You have successfully exited the control panel. Your access has been revoked."
exit_from_cp_success_alert = "Access revoked."

# - Menu Descriptions
desc_main = "Hello! Choose what to configure 👇"
desc_lang = "Choose the interface language:"
desc_gs = "Here you can enable or disable the main functions of <i>FPCortex</i>."
desc_ns = """Configure notifications for this chat.
Each chat is configured separately!

This chat's ID: <code>{}</code>"""
desc_bl = "Set restrictions for users on the blacklist."
desc_ar = "Add commands for the auto-responder or edit existing ones."
desc_ar_list = "Choose a command or command set to edit:"
desc_ad = "Auto-delivery settings: linking to listings, managing product files, etc."
desc_ad_list = "List of listings with configured auto-delivery. Choose a listing to edit:"
desc_ad_fp_lot_list = "List of listings from your FunPay profile. Choose a listing to configure auto-delivery.\n" \
                      "If the desired listing is not here, press <code>🔄 Refresh</code>.\n\n" \
                      "Last scan: {}"
desc_gf = "Choose a product file to manage:"
desc_mv = "Configure how new message notifications will look."
desc_gr = "Configure welcome messages for new dialogues.\n\n<b>Current greeting text:</b>\n<code>{}</code>"
desc_oc = "Configure the message that will be sent upon order confirmation.\n\n<b>Current message text:</b>\n<code>{}</code>"
desc_or = "Configure automatic responses to reviews."
desc_an = "Announcement notification settings."
desc_cfg = "Here you can download or upload configuration files."
desc_tmplt = "Manage quick response templates."
desc_pl = "Plugin information and settings.\n\n" \
          "⚠️ <b>IMPORTANT:</b> After activating, deactivating, adding, or deleting a plugin, " \
          "you <b><u>must restart the bot</u></b> with the /restart command!"
desc_au = "User authorization settings in the Telegram control panel."
desc_proxy = "Manage proxy servers for the bot's operation."
desc_mp = "Here you can configure which sections and commands will be available to managers."
unknown_action = "Unknown action or the button is outdated."

# - Help
help_manager_permissions = "This section allows you to configure detailed permissions for users with the 'Manager' role. You can allow or deny them access to specific bot functions, such as viewing the balance, editing the auto-responder and auto-delivery, and managing response templates."
help_new_message_view = "Here you can configure which messages from FunPay chats will be displayed in Telegram notifications. You can enable/disable the display of your messages, FunPay system messages, and messages sent by the bot. You can also set up notifications to receive only messages from a specific type of sender."

# - Command Descriptions
cmd_menu = "open the main menu"
cmd_language = "change interface language"
cmd_profile = "view account statistics"
cmd_golden_key = "change golden_key (access token)"
cmd_test_lot = "create a test auto-delivery key"
cmd_upload_chat_img = "(chat) upload an image to FunPay"
cmd_upload_offer_img = "(listing) upload an image to FunPay"
cmd_upload_plugin = "upload a new plugin"
cmd_ban = "add a user to the blacklist"
cmd_unban = "remove a user from the blacklist"
cmd_black_list = "show the blacklist"
cmd_watermark = "change the message watermark"
cmd_note = "add/edit a customer note"
cmd_logs = "download the current log file"
cmd_del_logs = "delete old log files"
cmd_about = "information about the bot"
cmd_check_updates = "check for updates"
cmd_update = "update the bot"
cmd_sys = "system information and load"
cmd_create_backup = "create a backup"
cmd_get_backup = "download a backup"
cmd_restart = "restart FPCortex"
cmd_power_off = "turn off FPCortex"

# - Variable Descriptions
v_edit_greeting_text = "Enter the greeting message text:"
v_edit_greeting_cooldown = "Enter the greeting cooldown (in days, e.g., 0.5 for 12 hours):"
v_edit_order_confirm_text = "Enter the order confirmation reply text:"
v_edit_review_reply_text = "Enter the reply text for a review with {}⭐:"
v_edit_delivery_text = "Enter the new text for auto-delivery of the item:"
v_edit_response_text = "Enter the new response text for the command:"
v_edit_notification_text = "Enter the new text for the Telegram notification:"
V_new_template = "Enter the text of the new response template:"
v_list = "Available variables:"
v_date = "<code>$date</code> - date (DD.MM.YYYY)"
v_date_text = "<code>$date_text</code> - date (January 1)"
v_full_date_text = "<code>$full_date_text</code> - date (January 1, 2001)"
v_time = "<code>$time</code> - time (HH:MM)"
v_full_time = "<code>$full_time</code> - time (HH:MM:SS)"
v_photo = "<code>$photo=[PHOTO_ID]</code> - picture (ID via /upload_chat_img)"
v_sleep = "<code>$sleep=[SECONDS]</code> - delay before sending (e.g., $sleep=2)"
v_order_id = "<code>$order_id</code> - order ID (without #)"
v_order_link = "<code>$order_link</code> - link to the order"
v_order_title = "<code>$order_title</code> - order title"
v_order_params = "<code>$order_params</code> - order parameters"
v_order_desc_and_params = "<code>$order_desc_and_params</code> - title and/or parameters of the order"
v_order_desc_or_params = "<code>$order_desc_or_params</code> - title or parameters of the order"
v_game = "<code>$game</code> - game name"
v_category = "<code>$category</code> - subcategory name"
v_category_fullname = "<code>$category_fullname</code> - full name (subcategory + game)"
v_product = "<code>$product</code> - item from the file (if not linked, will not be replaced)"
v_chat_id = "<code>$chat_id</code> - chat ID"
v_chat_name = "<code>$chat_name</code> - chat name"
v_message_text = "<code>$message_text</code> - text of the other person's message"
v_username = "<code>$username</code> - nickname of the other person"
v_cpu_core = "Core"

# Exception Texts
exc_param_not_found = "Parameter '{}' not found."
exc_param_cant_be_empty = "The value of parameter '{}' cannot be empty."
exc_param_value_invalid = "Invalid value for '{}'. Allowed: {}. Current: '{}'."
exc_goods_file_not_found = "Product file '{}' not found."
exc_goods_file_is_empty = "File '{}' is empty."
exc_not_enough_items = "Not enough items in file '{}'. Needed: {}, available: {}."
exc_no_product_var = "'productsFileName' is specified, but the 'response' parameter does not contain the $product variable."
exc_no_section = "Section is missing."
exc_section_duplicate = "Duplicate section detected."
exc_cmd_duplicate = "Command or sub-command '{}' already exists."
exc_cfg_parse_err = "Error in config {}, section [{}]: {}"
exc_plugin_field_not_found = "Failed to load plugin '{}': missing required field '{}'."

# Logs
log_tg_initialized = "$MAGENTATelegram bot initialized."
log_tg_started = "$CYANTelegram bot $YELLOW@{}CYAN started."
log_tg_handler_error = "An error occurred while executing the Telegram bot handler."
log_tg_update_error = "An error ({}) occurred while getting Telegram updates (invalid token entered?)."
log_tg_notification_error = "An error occurred while sending a notification to chat $YELLOW{}$RESET."
log_access_attempt = "$MAGENTA@{} (ID: {})$RESET tried to access the control panel. I'm holding them back as best I can!"
log_manager_access_granted = "$YELLOW[MANAGER]$RESET $MAGENTA@{} (ID: {})$RESET gained access to the control panel."
log_click_attempt = "$MAGENTA@{} (ID: {})$RESET is clicking control panel buttons in chat $MAGENTA@{} (ID: {})$RESET. They will not succeed!"
log_access_granted = "$MAGENTA@{} (ID: {})$RESET gained access to the control panel."
log_new_ad_key = "$MAGENTA@{} (ID: {})$RESET created a delivery key for $YELLOW{}$RESET: $CYAN{}$RESET."
log_user_blacklisted = "$MAGENTA@{} (ID: {})$RESET added $YELLOW{}$RESET to the blacklist."
log_user_unbanned = "$MAGENTA@{} (ID: {})$RESET removed $YELLOW{}$RESET from the blacklist."
log_watermark_changed = "$MAGENTA@{} (ID: {})$RESET changed the message watermark to $YELLOW{}$RESET."
log_watermark_deleted = "$MAGENTA@{} (ID: {})$RESET deleted the message watermark."
log_greeting_changed = "$MAGENTA@{} (ID: {})$RESET changed the greeting text to $YELLOW{}$RESET."
log_greeting_cooldown_changed = "$MAGENTA@{} (ID: {})$RESET changed the greeting message cooldown to $YELLOW{}$RESET days."
log_order_confirm_changed = "$MAGENTA@{} (ID: {})$RESET changed the order confirmation reply text to $YELLOW{}$RESET."
log_review_reply_changed = "$MAGENTA@{} (ID: {})$RESET changed the reply text for a {} star review to $YELLOW{}$RESET."
log_param_changed = "$MAGENTA@{} (ID: {})$RESET changed parameter $CYAN{}$RESET of section $YELLOW[{}]$RESET to $YELLOW{}$RESET."
log_notification_switched = "$MAGENTA@{} (ID: {})$RESET switched $YELLOW{}$RESET notifications for chat $YELLOW{}$RESET to $CYAN{}$RESET."
log_ad_linked = "$MAGENTA@{} (ID: {})$RESET linked auto-delivery to listing $YELLOW{}$RESET."
log_ad_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the delivery text for listing $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ad_deleted = "$MAGENTA@{} (ID: {})$RESET deleted auto-delivery for listing $YELLOW{}$RESET."
log_gf_created = "$MAGENTA@{} (ID: {})$RESET created product file $YELLOWstorage/products/{}$RESET."
log_gf_unlinked = "$MAGENTA@{} (ID: {})$RESET unlinked the product file from listing $YELLOW{}$RESET."
log_gf_linked = "$MAGENTA@{} (ID: {})$RESET linked product file $YELLOWstorage/products/{}$RESET to listing $YELLOW{}$RESET."
log_gf_created_and_linked = "$MAGENTA@{} (ID: {})$RESET created and linked product file $YELLOWstorage/products/{}$RESET to listing $YELLOW{}$RESET."
log_gf_new_goods = "$MAGENTA@{} (ID: {})$RESET added $CYAN{}$RESET product(s) to file $YELLOWstorage/products/{}$RESET."
log_gf_downloaded = "$MAGENTA@{} (ID: {})$RESET requested product file $YELLOWstorage/products/{}$RESET."
log_gf_deleted = "$MAGENTA@{} (ID: {})$RESET deleted product file $YELLOWstorage/products/{}$RESET."
log_ar_added = "$MAGENTA@{} (ID: {})$RESET added a new command $YELLOW{}$RESET."
log_ar_response_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the response text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_notification_text_changed = "$MAGENTA@{} (ID: {})$RESET changed the notification text for command $YELLOW{}$RESET to $YELLOW\"{}\"$RESET."
log_ar_cmd_deleted = "$MAGENTA@{} (ID: {})$RESET deleted command $YELLOW{}$RESET."
log_cfg_downloaded = "$MAGENTA@{} (ID: {})$RESET requested config $YELLOW{}$RESET."
log_tmplt_added = "$MAGENTA@{} (ID: {})$RESET added response template $YELLOW\"{}\"$RESET."
log_tmplt_deleted = "$MAGENTA@{} (ID: {})$RESET deleted response template $YELLOW\"{}\"$RESET."
log_pl_activated = "$MAGENTA@{} (ID: {})$RESET activated plugin $YELLOW\"{}\"$RESET."
log_pl_deactivated = "$MAGENTA@{} (ID: {})$RESET deactivated plugin $YELLOW\"{}\"$RESET."
log_pl_deleted = "$MAGENTA@{} (ID: {})$RESET deleted plugin $YELLOW\"{}\"$RESET."
log_pl_delete_handler_err = "An error occurred while executing the delete handler for plugin $YELLOW\"{}\"$RESET."
log_user_revoked = "$MAGENTA@{} (ID: {})$RESET revoked access for user $YELLOW{} (ID: {})$RESET."
log_user_role_changed = "$MAGENTA@{} (ID: {})$RESET changed the role of user $YELLOW{} (ID: {})$RESET to $CYAN{}$RESET."
log_manager_key_changed = "$MAGENTA@{} (ID: {})$RESET changed the manager registration key to $YELLOW{}$RESET."

# Handler Logs
log_new_msg = "$MAGENTA┌──$RESET New message in chat with user $YELLOW{} (CID: {}):"
log_sending_greetings = "User $YELLOW{} (CID: {})$RESET wrote for the first time! Sending a welcome message..."
log_new_cmd = "Received command $YELLOW{}$RESET in chat with user $YELLOW{} (CID: {})$RESET."
ntfc_new_order_price_details = "<code>{seller_price} {currency}</code> (buyer paid <code>{buyer_price} {currency}</code>)"
ntfc_new_order_no_link = "💰 <b>New order:</b> <code>{}</code>\n\n<b><i>🙍‍♂️ Buyer:</i></b>  <code>{}</code>\n<b><i>💵 Amount:</i></b>  {}\n<b><i>📇 ID:</i></b> <code>#{}</code>\n\n<i>{}</i>"
ntfc_new_order_not_in_cfg = "ℹ️ The item will not be delivered because auto-delivery is not linked to the listing."
ntfc_new_order_ad_disabled = "ℹ️ The item will not be delivered because auto-delivery is disabled in the global switches."
ntfc_new_order_ad_disabled_for_lot = "ℹ️ The item will not be delivered because auto-delivery is disabled for this listing."
ntfc_new_order_user_blocked = "ℹ️ The item will not be delivered because the user is on the blacklist and auto-delivery block is enabled."
ntfc_new_order_will_be_delivered = "ℹ️ The item will be delivered shortly."
ntfc_new_review = "🔮 You received {} for order <code>{}</code>!\n\n💬<b>Review:</b>\n<code>{}</code>{}"
ntfc_review_reply_text = "\n\n🗨️<b>Reply:</b> \n<code>{}</code>"

# Cortex Logs
crd_proxy_detected = "Proxy detected."
crd_checking_proxy = "Performing proxy check..."
crd_proxy_err = "Failed to connect to proxy. Make sure the data is entered correctly."
crd_proxy_success = "Proxy checked successfully! IP address: $YELLOW{}$RESET."
crd_acc_get_timeout_err = "Failed to load account data: request timed out."
crd_acc_get_unexpected_err = "An unexpected error occurred while getting account data."
crd_try_again_in_n_secs = "Retrying in {} second(s)..."
crd_getting_profile_data = "Getting listing and category data..."
crd_profile_get_timeout_err = "Failed to load account listing data: request timed out."
crd_profile_get_unexpected_err = "An unexpected error occurred while getting listing and category data."
crd_profile_get_too_many_attempts_err = "An error occurred while getting listing and category data: exceeded number of attempts ({})."
crd_profile_updated = "Updated information about profile listings $YELLOW({})$RESET and categories $YELLOW({})$RESET."
crd_tg_profile_updated = "Updated information about profile listings $YELLOW({})$RESET and categories $YELLOW({})$RESET (TG CP)."
crd_raise_time_err = 'Failed to boost listings in category $CYAN\"{}\"$RESET. FunPay says: "{}". Next attempt in {}.'
crd_raise_unexpected_err = "An unexpected error occurred while trying to boost listings in category $CYAN\"{}\"$RESET. Pausing for 10 seconds..."
crd_raise_status_code_err = "Error {} when boosting listings in category $CYAN\"{}\"$RESET. Pausing for 1 min..."
crd_lots_raised = "All listings in category $CYAN\"{}\"$RESET have been boosted!"
crd_raise_wait_3600 = "Next attempt in {}."
crd_msg_send_err = "An error occurred while sending a message to chat $YELLOW{}$RESET."
crd_msg_attempts_left = "Attempts left: $YELLOW{}$RESET."
crd_msg_no_more_attempts_err = "Failed to send message to chat $YELLOW{}$RESET: exceeded number of attempts."
crd_msg_sent = "Sent a message to chat $YELLOW{}."
crd_session_timeout_err = "Failed to update session: request timed out."
crd_session_unexpected_err = "An unexpected error occurred while updating the session."
crd_session_no_more_attempts_err = "Failed to update session: exceeded number of attempts."
crd_session_updated = "Session updated."
crd_raise_loop_started = "$CYANAuto-boost loop for listings has started (this does not mean that auto-boosting is enabled)."
crd_raise_loop_not_started = "$CYANAuto-boost loop was not started as no listings were found on the account."
crd_session_loop_started = "$CYANSession update loop started."
crd_no_plugins_folder = "Plugins folder not found."
crd_no_plugins = "No plugins found."
crd_plugin_load_err = "Failed to load plugin {}."
crd_invalid_uuid = "Failed to load plugin {}: invalid UUID."
crd_uuid_already_registered = "UUID {} ({}) is already registered."
crd_handlers_registered = "Handlers from $YELLOW{}.py$RESET registered."
crd_handler_err = "An error occurred while executing the handler."
crd_tg_au_err = "Failed to change the message with user information: {}. Trying without the link."

acc_balance_available = "available"
gf_infinity = "infinite"
gf_count_error = "counting error"
gf_file_not_found_short = "not found"
gf_not_linked = "not linked"
gf_file_created_now = "created now"
gf_file_creation_error_short = "creation error"
no_lots_using_file = "No listings are using this file."
gf_no_products_to_add = "No products were entered to be added."
gf_deleted_successfully = "File '{file_name}' successfully deleted."
gf_already_deleted = "File '{file_name}' was already deleted."
ar_no_valid_commands_entered = "No valid commands were entered."
ar_default_response_text = "The response for this command has not been configured yet. Please edit it."
ar_default_notification_text = "User $username entered command: $message_text"
ar_command_deleted_successfully = "Command/set '{command_name}' successfully deleted."
file_err_not_detected = "❌ File not detected in the message."
file_err_must_be_text = "❌ The file must be a text file (e.g., .txt, .cfg, .py, .json, .ini, .log)."
file_err_wrong_format = "❌ Incorrect file format: <b><u>.{actual_ext}</u></b> (expected <b><u>.{expected_ext}</u></b>)."
file_err_too_large = "❌ File size must not exceed 20MB."
file_info_downloading = "⏬ Downloading file from Telegram servers..."
file_err_download_failed = "❌ An error occurred while downloading the file to the bot's server."
file_info_checking_validity = "🤔 Checking file contents..."
file_err_processing_generic = "⚠️ An error occurred while processing the file: <code>{error_message}</code>"
file_err_utf8_decode = "An error occurred while reading the file (UTF-8). Ensure the file encoding is UTF-8 and the line endings are LF."
file_info_main_cfg_loaded = "✅ Main config successfully loaded.\n\n⚠️ <b>You must restart the bot (/restart)</b> for the changes to take effect.\n\nAny changes to the main config via the control panel switches before restarting will undo the loaded settings."
file_info_ar_cfg_applied = "✅ Auto-responder config successfully loaded and applied."
file_info_ad_cfg_applied = "✅ Auto-delivery config successfully loaded and applied."
plugin_uploaded_success = "✅ Plugin <code>{filename}</code> successfully uploaded.\n\n⚠️For the plugin to work, <b><u>restart FPCortex!</u></b> (/restart)"
image_upload_unsupported_format = "❌ Unsupported image format. Available: <code>.png</code>, <code>.jpg</code>, <code>.jpeg</code>, <code>.gif</code>."
image_upload_error_generic = "⚠️ Failed to upload image to FunPay. See the log file (<code>logs/log.log</code>) for details."
image_upload_chat_success_info = "Use this ID in auto-delivery or auto-responder texts with the <code>$photo</code> variable.\n\nFor example: <code>$photo={image_id}</code>"
image_upload_offer_success_info = "Use this ID to add images to your listings on FunPay."
image_upload_success_header = "✅ Image successfully uploaded to FunPay server.\n\n<b>Image ID:</b> <code>{image_id}</code>\n\n"
products_file_provide_prompt = "📎 Send me a file with products (.txt):"
products_file_upload_success = "✅ Product file <code>{filepath}</code> successfully uploaded. Products in file: <code>{count}</code>."
products_file_count_error = "⚠️ An error occurred while counting products in the uploaded file."
main_config_provide_prompt = "⚙️ Send me the main config file (<code>_main.cfg</code>):"
ar_config_provide_prompt = "🤖 Send me the auto-responder config file (<code>auto_response.cfg</code>):"
ad_config_provide_prompt = "📦 Send me the auto-delivery config file (<code>auto_delivery.cfg</code>):"
pl_status_active = "Status: Active 🚀"
pl_status_inactive = "Status: Inactive 💤"
pl_no_commands = "This plugin has no registered commands."
pl_delete_handler_failed = "⚠️ Error executing delete handler for plugin '{plugin_name}'. The plugin has been removed from the list, but its data or files may remain. Check the logs."
pl_deleted_successfully = "✅ Plugin '{plugin_name}' successfully deleted. Restart FPCortex for the changes to take effect."
pl_file_delete_error = "⚠️ Failed to delete plugin file '{plugin_path}'. Check permissions and logs."
proxy_status_enabled = "Enabled"
proxy_status_disabled = "Disabled"
proxy_check_status_enabled = "Enabled"
proxy_check_status_disabled = "Disabled"
proxy_not_used_currently = "not currently in use"
proxy_not_selected = "not selected"
proxy_check_interval_info = "Auto-check interval: {interval} min."
proxy_global_status_header = "Global Proxy Module Status"
proxy_module_status_label = "Module state:"
proxy_health_check_label = "Auto-check proxy:"
proxy_current_in_use_label = "Current proxy in use:"
proxy_select_error_not_found = "⚠️ Error: this proxy no longer exists in the list."
proxy_select_error_invalid_format = "⚠️ Error: the selected proxy has an invalid format."
proxy_selected_and_applied = "✅ Proxy {proxy_str} has been selected and applied."
proxy_selected_not_applied = "ℹ️ Proxy {proxy_str} has been selected. Enable the proxy module in settings to start using it."
proxy_deleted_successfully = "✅ Proxy {proxy_str} has been successfully deleted from the list."
proxy_delete_error_not_found = "⚠️ Error: proxy to be deleted not found in the list."
tmplt_editing_header = "📝 Editing Template"
tmplt_err_empty_text = "❌ Template text cannot be empty. Please enter text."
tmplt_deleted_successfully = "✅ Template '{template_text}' successfully deleted."
no_messages_to_display = "No messages to display"

autotp_command_desc = "auto-ticket creation settings for support"
autotp_settings_header = "⚙️ <b>AutoTP Settings</b>\n\n{}"
autotp_status_line = "Status: <b>{}</b>\nNext check in: <b>~{} min.</b>"
autotp_status_enabled = "🟢 Enabled"
autotp_status_disabled = "🔴 Disabled"
autotp_trigger_button = "🚀 Create tickets now"
autotp_toggle_button = "{} Auto-create tickets"
autotp_interval_button = "⏳ Interval: {} min."
autotp_threshold_button = "⏰ Threshold: {} h."
autotp_exclusions_button = "🚫 Exclusions"
autotp_template_button = "📝 Ticket Template"
autotp_alert_enabled = "✅ Auto-ticket creation enabled"
autotp_alert_disabled = "❌ Auto-ticket creation disabled"
autotp_prompt_interval = "Enter the new check interval in minutes (e.g., 30):"
autotp_err_interval_too_small = "❌ The interval cannot be less than 5 minutes."
autotp_success_interval_changed = "✅ Check interval changed to {} minutes."
autotp_prompt_threshold = "Enter the new time threshold for ticket creation in hours (e.g., 24):"
autotp_err_threshold_too_small = "❌ The time threshold cannot be less than 1 hour."
autotp_success_threshold_changed = "✅ Time threshold for ticket creation changed to {} hours."
autotp_prompt_template = "Current template:\n{}\n\nSend a new one. Use `{orders}` for the list of orders."
autotp_err_template_no_placeholder = "❌ The template must contain `{orders}` to substitute the list of orders."
autotp_success_template_changed = "✅ Ticket template successfully updated."
autotp_exclusions_header = "🚫 <b>Manage Category Exclusions</b>\n\nSelect categories for which tickets should <b>not</b> be created."
autotp_no_active_categories = "🤷‍♂️ No active categories found on the account."
autotp_trigger_started = "🚀 Starting order check and ticket creation..."
autotp_notify_success = "✅ AutoTP: Created a ticket for orders:\n{}"
autotp_notify_fail = "❌ AutoTP: Failed to create a ticket for orders:\n{}"
autotp_notify_no_orders = "✅ AutoTP: Check complete. No orders found for ticket creation."
autotp_exclusions_legend = "✅ - Tickets for this category will be created.\n🚫 - Tickets for this category will not be created."

# Statistics
stat_adv_stats_button = "📈 Statistics"
stat_settings_desc = "⚙️ <b>Statistics Settings</b>\n\nHere you can configure periodic reports and sales analysis depth."
stat_notifications_button = "{} Periodic Reports"
stat_notif_for_chat_button = "{} Notifications in this chat"
stat_interval_button = "⏳ Interval: {} hrs."
stat_period_button = "🗓️ Analysis period: {} days"
stat_prompt_interval = "Enter new interval for periodic reports (in hours):"
stat_prompt_period = "Enter new period for sales analysis (in days):"
mp_can_view_stats = "{} View statistics"

# CRM
cmd_note = "add/edit a note about a customer"
crm_prompt_add_note = "Send a note in the format: `Nickname Note`\nFor example: `SLLMK prefers delivery at night`"
crm_err_note_format = "❌ Incorrect format. Use: `Nickname Note`."
crm_err_customer_not_found = "❌ Customer with nickname `{username}` not found in the database."
crm_success_note_added = "✅ Note for customer `{username}` successfully added/updated."

# Order Control
mm_order_control = "🛂 Order Control"
oc_menu_desc = "Here you can configure notifications for 'stuck' orders."
oc_notify_pending_execution = "{} 🔔 Notify about orders pending execution"
oc_notify_pending_confirmation = "{} 🔔 Notify about orders pending confirmation"
oc_pending_execution_threshold = "⏳ Execution threshold: {} min."
oc_pending_confirmation_threshold = "⏳ Confirmation threshold: {} h."
oc_prompt_exec_threshold = "Enter the time in minutes, after which an order will be considered 'stuck' and requiring execution."
oc_prompt_confirm_threshold = "Enter the time in hours, after which to remind about an unconfirmed order (after you mark it as delivered)."
oc_err_threshold_format = "❌ Invalid value. Please enter a positive integer."
oc_success_threshold_changed = "✅ Threshold successfully changed to {}."
oc_notify_pending_execution_msg = "⚠️ Order <code>#{order_id}</code> from <code>{username}</code> has been pending your attention for over {minutes} minutes!"
oc_notify_pending_confirmation_msg = "🔔 Buyer <code>{username}</code> has not confirmed order <code>#{order_id}</code> for over {hours} hours. It might be worth reminding them."
oc_mark_as_delivered_btn = "Mark as Delivered"
oc_alert_marked_as_delivered = "✅ Order marked as delivered. The timer for a confirmation reminder has started."
ord_dont_refund = "Don't Refund"