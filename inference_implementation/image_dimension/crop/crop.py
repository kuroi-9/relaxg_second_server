from __future__ import annotations

from enum import Enum
from typing import Any

import numpy as np
from numpy import ndarray, dtype

from ...tools.utils import get_h_w_c


class CropMode(Enum):
    BORDER = 0
    EDGES = 1
    OFFSETS = 2


def crop_node(
    img: np.ndarray,
    mode: CropMode,
    amount: int,
    left: int,
    top: int,
    right: int,
    bottom: int,
    width: int,
    height: int,
) -> None | ndarray | ndarray[tuple[int, ...], dtype[Any] | Any]:
    h, w, _ = get_h_w_c(img)

    if mode == CropMode.BORDER:
        if amount == 0:
            return img

        assert 2 * amount < h, "Cropped area would result in an image with no height"
        assert 2 * amount < w, "Cropped area would result in an image with no width"

        return img[amount : h - amount, amount : w - amount]
    elif mode == CropMode.EDGES:
        if top == bottom == left == right == 0:
            return img

        assert top + bottom < h, "Cropped area would result in an image with no height"
        assert left + right < w, "Cropped area would result in an image with no width"

        return img[top : h - bottom, left : w - right]
    elif mode == CropMode.OFFSETS:
        assert top < h, "Cropped area would result in an image with no height"
        assert left < w, "Cropped area would result in an image with no width"

        return img[top : top + height, left : left + width]
