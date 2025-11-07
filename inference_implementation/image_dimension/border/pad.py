from __future__ import annotations

from enum import Enum
from typing import Any

import numpy as np
from numpy import ndarray, dtype

from ...color.color import Color
from ...tools.image_utils import BorderType, create_border
from ...tools.utils import Padding, get_h_w_c

class BorderMode(Enum):
    BORDER = 0
    EDGES = 1
    OFFSETS = 2

def pad_node(
    img: np.ndarray,
    border_type: BorderType,
    color: Color,
    border_mode: BorderMode,
    amount: int,
    left: int,
    top: int,
    right: int,
    bottom: int,
    width: int,
    height: int,
) -> None | ndarray | ndarray[tuple[int, ...], dtype[Any] | Any]:
    if border_mode == BorderMode.BORDER:
        return create_border(img, border_type, Padding.all(amount), color=color)
    elif border_mode == BorderMode.EDGES:
        return create_border(
            img, border_type, Padding(top, right, bottom, left), color=color
        )
    elif border_mode == BorderMode.OFFSETS:
        h, w, _ = get_h_w_c(img)
        r = width - left - w
        b = height - top - h
        padded = create_border(
            img, border_type, Padding(top, max(0, r), max(0, b), left), color=color
        )
        if r < 0 or b < 0:
            # copy, so we don't keep a reference to the underlying array
            padded = padded[:height, :width, ...].copy()
        return padded
