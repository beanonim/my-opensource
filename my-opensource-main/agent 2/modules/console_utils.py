from modules.theme_manager import *

def update_console_theme(console, username):
    new_theme = get_theme(username)
    try:
        console._theme = new_theme
    except AttributeError:
        pass