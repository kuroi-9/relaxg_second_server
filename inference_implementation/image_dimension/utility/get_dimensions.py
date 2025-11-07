from __future__ import annotations

import numpy as np
from ...tools.utils import get_h_w_c

def get_dimensions_node(
    img: np.ndarray,
) -> tuple[int, int, int]:
    h, w, c = get_h_w_c(img)
    return w, h, c
