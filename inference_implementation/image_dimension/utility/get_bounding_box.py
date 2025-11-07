from __future__ import annotations

import numpy as np
from ...tools.utils import get_h_w_c


def get_bounding_box_node(
    img: np.ndarray,
    thresh_val: float,
) -> tuple[int, int, int, int]:
    # Threshold value 100 guarantees an empty image, so make sure the max
    # is just below that.
    thresh = min(thresh_val / 100, 0.99999)
    h, w, _ = get_h_w_c(img)

    r = np.any(img > thresh, 1)
    c = np.any(img > thresh, 0)
    if not r.any():
        raise RuntimeError("Resulting bounding box is empty.")

    x, y = c.argmax(), r.argmax()
    return int(x), int(y), int(w - x - c[::-1].argmax()), int(h - y - r[::-1].argmax())
