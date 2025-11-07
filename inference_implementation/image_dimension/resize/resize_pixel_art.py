from __future__ import annotations
from enum import Enum
import numpy as np
from chainner_ext import pixel_art_upscale


class ResizeAlgorithm(Enum):
    ADV_MANE_2X = "adv_mame2x"
    ADV_MANE_3X = "adv_mame3x"
    ADV_MANE_4X = "adv_mame4x"
    EAGLE_2X = "eagle2x"
    EAGLE_3X = "eagle3x"
    SUPER_EAGLE_2X = "super_eagle2x"
    SAI_2X = "sai2x"
    SUPER_SAI_2X = "super_sai2x"
    HQ2X = "hqx2x"
    HQ3X = "hqx3x"
    HQ4X = "hqx4x"

    @property
    def algorithm(self) -> str:
        return self.value[:-2]

    @property
    def scale(self) -> int:
        if self in (ResizeAlgorithm.ADV_MANE_4X, ResizeAlgorithm.HQ4X):
            return 4
        if self in (
            ResizeAlgorithm.ADV_MANE_3X,
            ResizeAlgorithm.EAGLE_3X,
            ResizeAlgorithm.HQ3X,
        ):
            return 3
        return 2


ALGORITHM_LABEL: dict[ResizeAlgorithm, str] = {
    ResizeAlgorithm.ADV_MANE_2X: "EXP/AdvMAME 2x",
    ResizeAlgorithm.ADV_MANE_3X: "EXP/AdvMAME 3x",
    ResizeAlgorithm.ADV_MANE_4X: "EXP/AdvMAME 4x",
    ResizeAlgorithm.EAGLE_2X: "Eagle 2x",
    ResizeAlgorithm.EAGLE_3X: "Eagle 3x",
    ResizeAlgorithm.SUPER_EAGLE_2X: "Super Eagle 2x",
    ResizeAlgorithm.SAI_2X: "SaI 2x",
    ResizeAlgorithm.SUPER_SAI_2X: "Super SaI 2x",
    ResizeAlgorithm.HQ2X: "HQ 2x",
    ResizeAlgorithm.HQ3X: "HQ 3x",
    ResizeAlgorithm.HQ4X: "HQ 4x",
}


def resize_pixel_art_node(
    img: np.ndarray,
    algorithm: ResizeAlgorithm,
) -> np.ndarray:
    return pixel_art_upscale(img, algorithm.algorithm, algorithm.scale)
