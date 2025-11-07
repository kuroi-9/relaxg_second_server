from dataclasses import dataclass

import torch
from sanic.log import logger

@dataclass(frozen=True)
class PyTorchSettings:
    use_cpu: bool
    use_fp16: bool
    gpu_index: int
    budget_limit: int
    force_cache_wipe: bool = False

    # PyTorch 2.0 does not support FP16 when using CPU
    def __post_init__(self):
        if self.use_cpu and self.use_fp16:
            object.__setattr__(self, "use_fp16", False)
            logger.info("Falling back to FP32 mode.")

    @property
    def device(self) -> torch.device:
        # CPU override
        if self.use_cpu:
            device = "cpu"
        # Check for Nvidia CUDA
        elif torch.cuda.is_available() and torch.cuda.device_count() > 0:
            device = f"cuda:{self.gpu_index}"
        # Check for Apple MPS
        elif (
            hasattr(torch, "backends")
            and hasattr(torch.backends, "mps")
            and torch.backends.mps.is_built()
            and torch.backends.mps.is_available()
        ):  # type: ignore -- older pytorch versions dont support this technically
            device = "mps"
        # Check for DirectML
        elif hasattr(torch, "dml") and torch.dml.is_available():  # type: ignore
            device = "dml"
        else:
            device = "cpu"

        return torch.device(device)


def get_settings() -> PyTorchSettings:
    # return PyTorchSettings(
    #     use_cpu=settings.get_bool("use_cpu", False),
    #     use_fp16=settings.get_bool("use_fp16", False),
    #     gpu_index=settings.get_int("gpu_index", 0, parse_str=True),
    #     budget_limit=settings.get_int("budget_limit", 0, parse_str=True),
    #     force_cache_wipe=settings.get_bool("force_cache_wipe", False),
    # )
    return PyTorchSettings(
        use_cpu=False,
        use_fp16=False,
        gpu_index=0,
        budget_limit=0,
        force_cache_wipe=False,
    )
