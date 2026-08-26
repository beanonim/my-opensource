# функции принт \ инпут с градиентоммм

from rich.console import Console
from rich.text import Text
from typing import Optional
from .gradients import GRAY_WHITE, gray_white_gradient_custom, Gradient


console = Console()


def _apply_gradient(text_obj: Text, gradient: Gradient) -> None:
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


def p(text: str, gradient: Optional[Gradient] = None) -> None:
    # принт с градиентом
    if gradient is None:
        gradient = GRAY_WHITE

    rich_text = Text(text)
    _apply_gradient(rich_text, gradient)
    console.print(rich_text)


def i(prompt: str, gradient: Optional[Gradient] = None) -> str:
    # инпут с градиентом
    if gradient is None:
        gradient = GRAY_WHITE

    rich_text = Text(prompt)
    _apply_gradient(rich_text, gradient)
    console.print(rich_text, end="")

    return input()
