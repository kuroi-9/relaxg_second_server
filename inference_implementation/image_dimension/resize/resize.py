from __future__ import annotations

from enum import Enum
import numpy as np
from ...tools.resize import ResizeFilter, resize
from ...tools.utils import get_h_w_c, round_half_up


class ImageResizeMode(Enum):
    PERCENTAGE = 0
    ABSOLUTE = 1

def resize_node(
    img: np.ndarray,
    mode: ImageResizeMode,
    scale: float,
    width: int,
    height: int,
    filter: ResizeFilter,
    separate_alpha: bool,
) -> np.ndarray:
    h, w, _ = get_h_w_c(img)

    out_dims: tuple[int, int]
    if mode == ImageResizeMode.PERCENTAGE:
        out_dims = (
            max(round_half_up(w * (scale / 100)), 1),
            max(round_half_up(h * (scale / 100)), 1),
        )
    else:
        out_dims = (width, height)

    return resize(
        img,
        out_dims,
        filter,
        separate_alpha=separate_alpha,
        gamma_correction=False,
    )
