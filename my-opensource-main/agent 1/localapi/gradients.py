# функции для цветов

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Gradient:
    colors: List[Tuple[int, int, int]]


def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def gray_white_gradient() -> Gradient:
    # градиент от серого к белому
    return Gradient(colors=[_hex_to_rgb("#808080"), _hex_to_rgb("#FFFFFF")])


def gray_white_gradient_custom(start: str = "#808080", end: str = "#FFFFFF") -> Gradient:
    # кастом градиент
    return Gradient(colors=[_hex_to_rgb(start), _hex_to_rgb(end)])


GRAY_WHITE = gray_white_gradient()