from __future__ import annotations

from enum import Enum
import numpy as np
from ...tools.resize import ResizeFilter, resize
from ...tools.utils import get_h_w_c, round_half_up

class SideSelection(Enum):
    WIDTH = "width"
    HEIGHT = "height"
    SHORTER_SIDE = "shorter side"
    LONGER_SIDE = "longer side"


class ResizeCondition(Enum):
    BOTH = "both"
    UPSCALE = "upscale"
    DOWNSCALE = "downscale"


def resize_to_side_conditional(
    w: int, h: int, target: int, side: SideSelection, condition: ResizeCondition
) -> tuple[int, int]:
    def compare_conditions(b: int) -> bool:
        if condition == ResizeCondition.BOTH:
            return False
        if condition == ResizeCondition.DOWNSCALE:
            return target > b
        elif condition == ResizeCondition.UPSCALE:
            return target < b
        else:
            raise RuntimeError(f"Unknown condition {condition}")

    if side == SideSelection.WIDTH:
        if compare_conditions(w):
            w_new = w
            h_new = h
        else:
            w_new = target
            h_new = max(round_half_up((target / w) * h), 1)

    elif side == SideSelection.HEIGHT:
        if compare_conditions(h):
            w_new = w
            h_new = h
        else:
            w_new = max(round_half_up((target / h) * w), 1)
            h_new = target

    elif side == SideSelection.SHORTER_SIDE:
        if compare_conditions(min(h, w)):
            w_new = w
            h_new = h
        else:
            w_new = max(round_half_up((target / min(h, w)) * w), 1)
            h_new = max(round_half_up((target / min(h, w)) * h), 1)

    elif side == SideSelection.LONGER_SIDE:
        if compare_conditions(max(h, w)):
            w_new = w
            h_new = h
        else:
            w_new = max(round_half_up((target / max(h, w)) * w), 1)
            h_new = max(round_half_up((target / max(h, w)) * h), 1)

    else:
        raise RuntimeError(f"Unknown side selection {side}")

    return w_new, h_new

def resize_to_side_node(
    img: np.ndarray,
    target: int,
    side: SideSelection,
    condition: ResizeCondition,
    filter: ResizeFilter,
) -> np.ndarray:
    h, w, _ = get_h_w_c(img)
    out_dims = resize_to_side_conditional(w, h, target, side, condition)

    return resize(img, out_dims, filter)
