from rich.color import Color
from rich.markup import escape

class Gradient:
    def __init__(self, colors):
        self.colors = colors

def _color_to_rgb(color_str):
    try:
        return Color.parse(color_str).get_truecolor()
    except Exception:
        return (255, 255, 255)

def theme_gradient(theme_dict):
    colors = []
    for key in ('primary', 'secondary', 'highlight', 'primary'):
        col = theme_dict.get(key, 'white')
        colors.append(_color_to_rgb(col))
    return Gradient(colors)

def _apply_gradient(text_obj, gradient):
    colors = gradient.colors
    plain = text_obj.plain
    if not plain or len(colors) < 2:
        return
    lines = plain.split('\n')
    max_lines = max(len(lines) - 1, 1)
    offset = 0
    for row, line in enumerate(lines):
        for col in range(len(line)):
            ratio = (row / max_lines + col / max(len(line) - 1, 1)) / 2
            idx = min(int(ratio * (len(colors) - 1)), len(colors) - 2)
            t = ratio * (len(colors) - 1) - idx
            c1, c2 = colors[idx], colors[idx + 1]
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            text_obj.stylize(f"#{r:02x}{g:02x}{b:02x}", offset + col, offset + col + 1)
        offset += len(line) + 1

def _gradient_markup(text, gradient):
    colors = gradient.colors
    if not text or len(colors) < 2:
        return text
    lines = text.split('\n')
    max_lines = max(len(lines) - 1, 1)
    out = []
    for row, line in enumerate(lines):
        if not line:
            out.append('')
            continue
        chars = []
        for col in range(len(line)):
            ratio = (row / max_lines + col / max(len(line) - 1, 1)) / 2
            idx = min(int(ratio * (len(colors) - 1)), len(colors) - 2)
            t = ratio * (len(colors) - 1) - idx
            c1, c2 = colors[idx], colors[idx + 1]
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            chars.append(f"[#{r:02x}{g:02x}{b:02x}]{escape(line[col])}[/]")
        out.append(''.join(chars))
    return '\n'.join(out)
