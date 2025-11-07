from __future__ import annotations

import weakref

import numpy as np
import psutil
import torch
from sanic.log import logger
from spandrel import ImageModelDescriptor, ModelTiling

from ..pytorch.auto_split import pytorch_auto_split
from ..upscale.auto_split_tiles import (
    NO_TILING,
    TileSize,
    estimate_tile_size,
    parse_tile_size_input,
)
from ..upscale.tiler import MaxTileSize
from .settings import PyTorchSettings

MODEL_BYTES_CACHE = weakref.WeakKeyDictionary()


def upscale(
    img: np.ndarray,
    model: ImageModelDescriptor,
    tile_size: TileSize,
    options: PyTorchSettings,
):
    with torch.no_grad():
        # Borrowed from iNNfer
        logger.debug("Upscaling image")

        # TODO: use bfloat16 if RTX
        use_fp16 = options.use_fp16 and model.supports_half
        device = options.device

        if model.tiling == ModelTiling.INTERNAL:
            # disable tiling if the model already does it internally
            tile_size = NO_TILING

        def estimate():
            model_bytes = MODEL_BYTES_CACHE.get(model)
            if model_bytes is None:
                model_bytes = sum(p.numel() * 4 for p in model.model.parameters())
                MODEL_BYTES_CACHE[model] = model_bytes

            if "cuda" in device.type:
                if options.use_fp16:
                    model_bytes = model_bytes // 2
                mem_info: tuple[int, int] = torch.cuda.mem_get_info(device)  # type: ignore
                _free, total = mem_info
                # only use 75% of the total memory
                total = int(total * 0.75)
                if options.budget_limit > 0:
                    total = min(options.budget_limit * 1024**3, total)
                # Estimate using 80% of the value to be more conservative
                budget = int(total * 0.8)

                return MaxTileSize(
                    estimate_tile_size(
                        budget,
                        model_bytes,
                        img,
                        2 if use_fp16 else 4,
                    )
                )
            elif device.type == "cpu":
                free = psutil.virtual_memory().available
                if options.budget_limit > 0:
                    free = min(options.budget_limit * 1024**3, free)
                budget = int(free * 0.8)
                return MaxTileSize(
                    estimate_tile_size(
                        budget,
                        model_bytes,
                        img,
                        4,
                    )
                )
            return MaxTileSize()

        img_out = pytorch_auto_split(
            img,
            model=model,
            device=device,
            use_fp16=use_fp16,
            tiler=parse_tile_size_input(tile_size, estimate),
            # progress=progress,
        )
        logger.debug("Done upscaling")

        return img_out
