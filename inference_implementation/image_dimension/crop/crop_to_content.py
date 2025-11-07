from __future__ import annotations

import numpy as np
from ...tools.utils import get_h_w_c

def crop_to_content_node(img: np.ndarray, thresh_val: float) -> np.ndarray:
    c = get_h_w_c(img)[2]
    if c < 4:
        return img

    # Threshold value 100 guarantees an empty image, so make sure the max
    # is just below that.
    thresh_val = min(thresh_val / 100, 0.99999)

    # Valid alpha is greater than threshold, else impossible to crop 0 alpha only
    alpha = img[:, :, 3]
    r = np.any(alpha > thresh_val, 1)
    if r.any():
        h, w, _ = get_h_w_c(img)
        c = np.any(alpha > thresh_val, 0)
        imgout = np.copy(img)[
            r.argmax() : h - r[::-1].argmax(), c.argmax() : w - c[::-1].argmax()
        ]
    else:
        raise RuntimeError("Crop results in empty image.")

    return imgout
