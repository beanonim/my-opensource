from rich.console import Console
from rich import style as rich_style
from modules.config import *
from modules.theme_manager import *

console = Console(width=120, force_terminal=True, theme=get_theme(USERNAME))

PL = {
    'bg1': rich_style.Style(bgcolor='grey23', color='bright_white'),
    'bg2': rich_style.Style(bgcolor='grey30', color='bright_white'),
    'bg3': rich_style.Style(bgcolor='grey23', color='bright_white'),
}

def cls():
    console.clear()