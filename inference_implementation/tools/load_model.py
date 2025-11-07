from __future__ import annotations

import os
from pathlib import Path

from sanic.log import logger
from spandrel import MAIN_REGISTRY, ModelDescriptor, ModelLoader
from spandrel_extra_arches import EXTRA_REGISTRY
from .utils import split_file_path

MAIN_REGISTRY.add(*EXTRA_REGISTRY)

def parse_ckpt_state_dict(checkpoint: dict):
    state_dict = {}
    for i, j in checkpoint.items():
        if "netG." in i:
            key = i.replace("netG.", "")
            state_dict[key] = j
        elif "module." in i:
            key = i.replace("module.", "")
            state_dict[key] = j
    return state_dict
