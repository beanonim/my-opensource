import re
import shutil
from rich.markup import escape
from rich.layout import Layout
from rich.panel import Panel
from rich.console import RenderableType
from rich.align import Align
from rich.text import Text
from modules.config import *
from modules.theme_manager import *
from modules.banner.templates import *
from modules.banner.gradient import theme_gradient, _gradient_markup
from functions.misc.settings import *
from modules.modules.registry import get_function_pages, get_total_pages, STATIC_PAGES

def get_tw():
    return shutil.get_terminal_size().columns

def _v_len(s):
    s = re.sub(r'\[/?(?:[a-z_]+|#[0-9a-fA-F]{3,6})\]', '', s)
    s = s.replace('\\[', '[')
    return len(s)

def _center_block(text, width=None):
    if width is None:
        width = get_tw()
    lines = text.strip('\n').split('\n')
    max_l = max(_v_len(line) for line in lines) if lines else 0
    margin = max(0, (width - max_l) // 2)
    return '\n'.join((' ' * margin) + line for line in lines)


def create_banner(page=1, show_coffee=False, layout='down'):
    lb, rb = get_banner_brackets(USERNAME)
    
    config_data = load_config(USERNAME)
    show_user_info = config_data.get('show_user_info', 'false') == 'true'
    user_info_pos = config_data.get('user_info_pos', '1')

    banner_color_mode = config_data.get('banner_color_mode', 'solid')
    gradient_mode = banner_color_mode == 'gradient'
    gradient = theme_gradient(DEFAULT_THEMES.get(config_data.get('theme', 'standard'), DEFAULT_THEMES['standard'])) if gradient_mode else None

    def _style_art_line(line):
        if gradient_mode and line:
            return f"[bold]{_gradient_markup(line, gradient)}[/bold]"
        return f"[bold][banner]{escape(line)}[/banner][/bold]" if line else ""

    ascii_art = HEADER_ASCII.strip('\n')
    custom_banner = config_data.get('custom_banner', '')
    if custom_banner:
        ascii_art = custom_banner.replace('\\n', '\n')
    
    
    info_vars = {'data': escape(DATABASE_SIZE), 'version': escape(VERSION), 'username': escape(USERNAME), 'uuid': escape(UUID), 'subscription': escape(SUBSCRIPTION)}
    
    if show_user_info:
        info_lines = [line.format(**info_vars) for line in INFO_SIDE_TEMPLATE]
    else:
        info_lines = [
            f"[banner]\\[/][/banner] Баз данных: [primary]{info_vars['data']}[/primary]",
            f"[banner]\\[&][/banner] Разработчик: [primary]t.me/hatedfame[/primary]",
            f"[banner]\\[@][/banner] Версия: [primary]{info_vars['version']}[/primary]"
        ]

    banner_lines = [line.rstrip() for line in ascii_art.split('\n')]
    max_logo_w = max(_v_len(l) for l in banner_lines) if banner_lines else 0
    tw = get_tw()
    
    if user_info_pos == '1' and max_logo_w + 20 < tw:
        max_h = max(len(banner_lines), len(info_lines))
        header_lines = []
        offset = (max_h - len(info_lines)) // 2
        
        for i in range(max_h):
            l_raw = banner_lines[i] if i < len(banner_lines) else ""
            l_styled = _style_art_line(l_raw)
            l_v = _v_len(l_raw)
            
            s_idx = i - offset
            s_styled = info_lines[s_idx] if 0 <= s_idx < len(info_lines) else ""
            
            show_sep = config_data.get('show_banner_separator', 'true') == 'true'
            sep = " │ " if show_sep else "  "
            pad = " " * (max_logo_w - l_v + 2)
            header_lines.append(f"{l_styled}{pad}{sep}{s_styled}".rstrip())
        header = "\n".join(header_lines)
    else:
        logo_block = "\n".join([_style_art_line(l) for l in banner_lines])
        stats_block = "\n".join(info_lines)
        header = f"{logo_block}\n\n{stats_block}"


    items = []
    total_pages = get_total_pages()
    nav_label = get_navigation_label(page, total_pages)
    items.append(f'[primary]{lb}99{rb}[/primary] {nav_label}')
        
    if show_coffee:
        items.append(f'[primary]{lb}88{rb}[/primary] Купите мне кофе')
        
    items.append(f'[primary]{lb}77{rb}[/primary] Настройки')
    items.append(f'[primary]{lb}55{rb}[/primary] Модули')
    items.append(f'[primary]{lb}66{rb}[/primary] Полезные ссылки')

    while len(items) < 5:
        items.append("")
    
    fn_pages = get_function_pages()
    if page <= STATIC_PAGES:
        raw_opts = PAGE_OPTIONS.get(page) or []
        page_fn_mods = []
    else:
        raw_opts = PAGE_OPTIONS.get(STATIC_PAGES + 1) if page == STATIC_PAGES + 1 else []
        fn_idx = page - STATIC_PAGES - 1
        page_fn_mods = fn_pages[fn_idx] if fn_idx < len(fn_pages) else []

    opts = []
    for code, label in raw_opts:
        if code:
            opts.append(f'[primary]{lb}{code}{rb}[/primary] {label}')

    for code, fname, meta in page_fn_mods:
        opts.append(f'[primary]{lb}{code}{rb}[/primary] [success]{meta["name"]}[/success]')

    def p(text, width):
        return text + (" " * max(0, width - _v_len(text)))

    show_layout_sep = config_data.get('show_layout_separator', 'true') == 'true'
    side_sep = " │ " if show_layout_sep else "   "
    
    if layout == 'side':
        rows = []
        rows_n = max(5, (len(opts) + 1) // 2)
        for i in range(rows_n):
            left = opts[2 * i] if 2 * i < len(opts) else ''
            right = opts[2 * i + 1] if 2 * i + 1 < len(opts) else ''
            it = items[i] if i < len(items) else ''
            rows.append(f'{p(left, 28)} {p(right, 26)}{side_sep}{it}')
        menu_content = '\n'.join(rows)
    else:
        option_rows = []
        if page <= STATIC_PAGES:
            padded = opts + [''] * (8 - len(opts))
            for i in range(0, len(padded), 2):
                left = padded[i]
                right = padded[i + 1] if i + 1 < len(padded) else ''
                option_rows.append(f'{p(left, 28)} {p(right, 26)}')
        else:
            rows = (len(opts) + 1) // 2
            for r in range(rows):
                left = opts[r] if r < len(opts) else ''
                right = opts[r + rows] if r + rows < len(opts) else ''
                option_rows.append(f'{p(left, 28)} {p(right, 26)}')
        menu_content = '\n'.join(option_rows) + f'''

{p(items[0], 28)} {p(items[2], 26)}
{p(items[1], 28)} {p(items[3], 26)}
{p(items[4], 28)}'''

    banner_style = config_data.get('banner_style', 'standard')

    if banner_style == 'classic_cli':
        art = HEADER_ASCII.strip('\n')
        sep = '  ' + '-' * 60
        stats_text = f"  \u25cf DB {info_vars['data']}    \u25cf VER {info_vars['version']}    \u25cf DEV t.me/hatedfame"
        cli_lines = [('  ' + _style_art_line(line)) for line in art.split('\n')]
        cli_block = '\n'.join(cli_lines) + f'\n\n{sep}\n{stats_text}\n{sep}'

        raw_opts = (PAGE_OPTIONS.get(STATIC_PAGES + 1) if page == STATIC_PAGES + 1 else []) if page > STATIC_PAGES else (PAGE_OPTIONS.get(page) or [])
        cli_menu_lines = []
        col_w = 32
        for row_idx in range(0, len(raw_opts), 2):
            left = raw_opts[row_idx]
            right = raw_opts[row_idx + 1] if row_idx + 1 < len(raw_opts) else (None, None)
            line = '  '
            if left[0]:
                line += f'{left[0]:>2} \u25b8 {left[1]}'
                visual = 2 + len(left[0]) + 1 + 1 + len(left[1])
                if visual < col_w:
                    line += ' ' * (col_w - visual)
            else:
                line += ' ' * col_w
            line += ' \u2502 '
            if right and right[0]:
                line += f'{right[0]:>2} \u25b8 {right[1]}'
            cli_menu_lines.append(line)

        nav_label = get_navigation_label(page, total_pages)
        cli_menu_lines.append(f'  99 \u25b8 {nav_label}')
        cli_menu_lines.append(f'  77 \u25b8 Настройки')
        cli_menu_lines.append(f'  55 \u25b8 Модули')
        cli_menu_lines.append(f'   8 \u25b8 Выход')
        for code, fname, meta in page_fn_mods:
            cli_menu_lines.append(f'{code:>3} \u25b8 {meta["name"]}')

        cli_menu = '\n'.join(cli_menu_lines)
        full_block = f'{cli_block}\n{cli_menu}'
        full_block = '\n'.join(("          " + line if line else "") for line in full_block.split('\n'))
        return full_block + '\n'

    if banner_style in ['square', 'square2']:
        frame_width = 85
        if banner_style == 'square':
            tl, tr, bl, br, h, v, sl, sr = "╔", "╗", "╚", "╝", "═", "║", "╠", "╣"
        else:
            tl, tr, bl, br, h, v, sl, sr = "┏", "┓", "┗", "┛", "━", "┃", "┣", "┫"
        c_start = "[bold][banner]"
        c_end = "[/banner][/bold]"
        top_border = f"{c_start}{tl}{h * frame_width}{tr}{c_end}"
        bottom_border = f"{c_start}{bl}{h * frame_width}{br}{c_end}"
        sep_border = f"{c_start}{sl}{h * frame_width}{sr}{c_end}"
        framed_lines = [top_border]
        header_lines_split = header.strip('\n').split('\n')
        max_header_len = max(_v_len(line) for line in header_lines_split) if header_lines_split else 0
        header_left_pad = max(0, frame_width - max_header_len) // 2
        for line in header_lines_split:
            line_len = _v_len(line)
            left_spaces = " " * header_left_pad
            right_spaces = " " * max(0, frame_width - header_left_pad - line_len)
            framed_lines.append(f"{c_start}{v}{c_end}{left_spaces}{line}{right_spaces}{c_start}{v}{c_end}")
        framed_lines.append(sep_border)
        framed_lines.append(f"{c_start}{v}{c_end}{' ' * frame_width}{c_start}{v}{c_end}")
        menu_lines = menu_content.strip('\n').split('\n')
        max_menu_len = max(_v_len(line) for line in menu_lines) if menu_lines else 0
        menu_left_pad = max(0, frame_width - max_menu_len) // 2
        for line in menu_lines:
            line_len = _v_len(line)
            left_spaces = " " * menu_left_pad
            right_spaces = " " * max(0, frame_width - menu_left_pad - line_len)
            framed_lines.append(f"{c_start}{v}{c_end}{left_spaces}{line}{right_spaces}{c_start}{v}{c_end}")
        framed_lines.append(f"{c_start}{v}{c_end}{' ' * frame_width}{c_start}{v}{c_end}")
        framed_lines.append(bottom_border)
        full_block = '\n'.join(framed_lines)
    else:
        full_block = f'{header}\n{menu_content}'
    full_block = '\n'.join(("          " + line if line else "") for line in full_block.split('\n'))
    return full_block + '\n'
