import os
import re
from rich.theme import Theme
from modules.config import *

DEFAULT_THEMES = {
    'standard': {
        'primary': 'blue',
        'secondary': 'cyan',
        'success': 'green',
        'warning': 'yellow',
        'error': 'red',
        'text': 'white',
        'highlight': 'magenta',
        'dim': 'dim white',
        'banner': 'bold blue'
    },
    'dark': {
        'primary': '#444444',
        'secondary': '#666666',
        'success': '#228822',
        'warning': '#888822',
        'error': '#882222',
        'text': '#cccccc',
        'highlight': '#ffffff',
        'dim': 'dim #666666',
        'banner': 'bold #888888'
    },
    'hacker': {
        'primary': '#22ff22',
        'secondary': '#008800',
        'success': 'bold #00ff00',
        'warning': '#ffff00',
        'error': '#ff0000',
        'text': '#00ff00',
        'highlight': '#ffffff',
        'dim': 'dim #00ff00',
        'banner': 'bold #22ff22'
    },
    'neon': {
        'primary': '#ff00ff',
        'secondary': '#00ffff',
        'success': 'bold #00ff00',
        'warning': 'bold #ffff00',
        'error': 'bold #ff0000',
        'text': '#ffffff',
        'highlight': 'bold #ff00ff',
        'dim': 'dim #ff00ff',
        'banner': 'bold #00ffff'
    },
    'ocean': {
        'primary': '#0077ff',
        'secondary': '#00ccff',
        'success': '#00ffaa',
        'warning': '#ffff00',
        'error': '#ff4444',
        'text': '#eeeeee',
        'highlight': '#00aaff',
        'dim': 'dim #00ccff',
        'banner': 'bold #0077ff'
    },
    'sunset': {
        'primary': '#ff4400',
        'secondary': '#ff8800',
        'success': '#ffaa00',
        'warning': 'bold #ff4400',
        'error': 'bold #ffcc00',
        'text': '#ffffff',
        'highlight': '#ffaa00',
        'dim': 'dim #ff4400',
        'banner': 'bold #ff8800'
    },
    'forest': {
        'primary': '#228b22',
        'secondary': '#32cd32',
        'success': '#90ee90',
        'warning': '#ffff00',
        'error': '#ff4444',
        'text': '#e0ffe0',
        'highlight': '#ffff00',
        'dim': 'dim #228b22',
        'banner': 'bold #32cd32'
    },
    'dracula': {
        'primary': '#bd93f9',
        'secondary': '#8be9fd',
        'success': '#50fa7b',
        'warning': '#f1fa8c',
        'error': '#ff5555',
        'text': '#f8f8f2',
        'highlight': '#ff79c6',
        'dim': 'dim #6272a4',
        'banner': 'bold #bd93f9'
    },
    'monokai': {
        'primary': '#a6e22e',
        'secondary': '#66d9ef',
        'success': '#a6e22e',
        'warning': '#fd971f',
        'error': '#f92672',
        'text': '#f8f8f2',
        'highlight': '#ae81ff',
        'dim': 'dim #75715e',
        'banner': 'bold #f92672'
    },
    'cyberpunk': {
        'primary': '#fdf500',
        'secondary': '#ff00ff',
        'success': '#00ff00',
        'warning': '#fdf500',
        'error': '#ff0000',
        'text': '#ffffff',
        'highlight': '#00ffff',
        'dim': 'dim #ff00ff',
        'banner': 'bold #fdf500'
    },
    'nord': {
        'primary': '#81a1c1',
        'secondary': '#88c0d0',
        'success': '#a3be8c',
        'warning': '#ebcb8b',
        'error': '#bf616a',
        'text': '#eceff4',
        'highlight': '#d8dee9',
        'dim': 'dim #4c566a',
        'banner': 'bold #81a1c1'
    },
    'gruvbox': {
        'primary': '#fe8019',
        'secondary': '#fabd2f',
        'success': '#b8bb26',
        'warning': '#fabd2f',
        'error': '#fb4934',
        'text': '#ebdbb2',
        'highlight': '#d3869b',
        'dim': 'dim #928374',
        'banner': 'bold #fe8019'
    },
    'pastel': {
        'primary': '#ffb7b2',
        'secondary': '#b2e2f2',
        'success': '#b2f2bb',
        'warning': '#f2f2b2',
        'error': '#f2b2b2',
        'text': '#ffffff',
        'highlight': '#e2b2f2',
        'dim': 'dim #ffffff',
        'banner': 'bold #ffb7b2'
    },
    'gold': {
        'primary': '#ffd700',
        'secondary': '#ffcc00',
        'success': '#ffcc00',
        'warning': '#ffffff',
        'error': '#ff4444',
        'text': '#fffdf0',
        'highlight': '#ffffff',
        'dim': 'dim #ffd700',
        'banner': 'bold #ffd700'
    },
    'cherry': {
        'primary': '#ff007f',
        'secondary': '#ff66b2',
        'success': '#00ff00',
        'warning': '#ffff00',
        'error': '#ff0000',
        'text': '#fff0f5',
        'highlight': '#ffffff',
        'dim': 'dim #ff007f',
        'banner': 'bold #ff007f'
    },
    'midnight': {
        'primary': '#00008b',
        'secondary': '#191970',
        'success': '#00ff7f',
        'warning': '#ffd700',
        'error': '#ff4500',
        'text': '#f0f8ff',
        'highlight': '#ffffff',
        'dim': 'dim #00008b',
        'banner': 'bold #191970'
    },
    'matrix': {
        'primary': '#00ff41',
        'secondary': '#003b00',
        'success': '#00ff41',
        'warning': '#008f11',
        'error': '#ff0000',
        'text': '#00ff41',
        'highlight': 'bold #00ff41',
        'dim': 'dim #003b00',
        'banner': 'bold #00ff41'
    },
    'toxic': {
        'primary': '#adff2f',
        'secondary': '#a020f0',
        'success': '#32cd32',
        'warning': '#ffff00',
        'error': '#ff0000',
        'text': '#ffffff',
        'highlight': '#bf00ff',
        'dim': 'dim #a020f0',
        'banner': 'bold #bf00ff'
    },
    'cotton_candy': {
        'primary': '#ffbcd9',
        'secondary': '#b2ffff',
        'success': '#b2f2bb',
        'warning': '#f2f2b2',
        'error': '#f2b2b2',
        'text': '#ffffff',
        'highlight': '#ff00ff',
        'dim': 'dim #ffffff',
        'banner': 'bold #ffbcd9'
    },
    'volcano': {
        'primary': '#ff4500',
        'secondary': '#8b0000',
        'success': '#00ff00',
        'warning': '#ffff00',
        'error': '#ff0000',
        'text': '#fff5ee',
        'highlight': '#ffffff',
        'dim': 'dim #ff4500',
        'banner': 'bold #ff4500'
    }
}

THEME_ALIASES = {str(i): name for i, name in enumerate(DEFAULT_THEMES.keys(), 1)}
CONFIGS_DIR = os.path.join(os.path.dirname(__file__), 'banner', 'configs')

def get_theme_config_path(username):
    os.makedirs(CONFIGS_DIR, exist_ok=True)
    safe_name = re.sub(r'[^\w\-]', '_', str(username).strip())[:64] or '_default'
    return os.path.join(CONFIGS_DIR, f'{safe_name}.cfg')

def load_config(username):
    config_path = get_theme_config_path(username)
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        except Exception:
            pass
    return config

def save_config(username, key, value):
    current_config = load_config(username)
    current_config[key] = value
    config_path = get_theme_config_path(username)
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            for k, v in current_config.items():
                f.write(f'{k}={v}\n')
        return True
    except Exception:
        return False

def load_user_theme_name(username):
    config = load_config(username)
    return config.get('theme', 'standard')

def save_user_theme(username, theme_name):
    return save_config(username, 'theme', theme_name)

def load_theme_overrides(username):
    config = load_config(username)
    overrides = {}
    for role in DEFAULT_THEMES['standard']:
        key = 'color_' + role
        if config.get(key):
            overrides[role] = config[key]
    return overrides

def clear_theme_overrides(username):
    config = load_config(username)
    changed = False
    for key in list(config.keys()):
        if key.startswith('color_'):
            config.pop(key)
            changed = True
    if changed:
        path = get_theme_config_path(username)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for k, v in config.items():
                    f.write(f'{k}={v}\n')
        except Exception:
            return False
    return True

def get_theme(username=None):
    theme_name = 'standard'
    if username:
        theme_name = load_user_theme_name(username)
    if theme_name not in DEFAULT_THEMES:
        theme_name = 'standard'
    theme_styles = dict(DEFAULT_THEMES[theme_name])
    if username:
        theme_styles.update(load_theme_overrides(username))
    return Theme(theme_styles)

def is_first_run(username):
    config = load_config(username)
    return config.get('first_run', 'true') == 'true'