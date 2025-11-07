from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
import pillow_avif  # type: ignore # noqa: F401
from ..api.lazy import Lazy
from PIL import Image
from sanic.log import logger
from ..dds.format import (
    BC7_FORMATS,
    BC123_FORMATS,
    LEGACY_TO_DXGI,
    PREFER_DX9,
    WITH_ALPHA,
    DDSFormat,
    to_dxgi,
)
from ..dds.texconv import save_as_dds
from ..tools.image_utils import cv_save_image, to_uint8, to_uint16
from ..tools.utils import get_h_w_c

class ImageFormat(Enum):
    PNG = "png"
    JPG = "jpg"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    WEBP = "webp"
    TGA = "tga"
    DDS = "dds"
    AVIF = "avif"

    @property
    def extension(self) -> str:
        return self.value


IMAGE_FORMAT_LABELS: dict[ImageFormat, str] = {
    ImageFormat.PNG: "PNG",
    ImageFormat.JPG: "JPG",
    ImageFormat.GIF: "GIF",
    ImageFormat.BMP: "BMP",
    ImageFormat.TIFF: "TIFF",
    ImageFormat.WEBP: "WEBP",
    ImageFormat.TGA: "TGA",
    ImageFormat.DDS: "DDS",
    ImageFormat.AVIF: "AVIF",
}


class JpegSubsampling(Enum):
    FACTOR_444 = int(cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444)
    FACTOR_440 = int(cv2.IMWRITE_JPEG_SAMPLING_FACTOR_440)
    FACTOR_422 = int(cv2.IMWRITE_JPEG_SAMPLING_FACTOR_422)
    FACTOR_420 = int(cv2.IMWRITE_JPEG_SAMPLING_FACTOR_420)


class AvifSubsampling(Enum):
    FACTOR_444 = "4:4:4"
    FACTOR_422 = "4:2:2"
    FACTOR_420 = "4:2:0"
    FACTOR_400 = "4:0:0"


class PngColorDepth(Enum):
    U8 = "u8"
    U16 = "u16"


class TiffColorDepth(Enum):
    U8 = "u8"
    U16 = "u16"
    F32 = "f32"


class TiffCompression(Enum):
    NONE = 1
    LZW = 5
    ZIP = 8

    @property
    def cv2_code(self) -> int:
        # OpenCV is a beautiful piece of software, so surely they won't forget to define the TIFF compression constants, right?
        return self.value


SUPPORTED_DDS_FORMATS: list[tuple[DDSFormat, str]] = [
    ("BC1_UNORM_SRGB", "BC1 (4bpp, sRGB, 1-bit Alpha)"),
    ("BC1_UNORM", "BC1 (4bpp, Linear, 1-bit Alpha)"),
    ("BC3_UNORM_SRGB", "BC3 (8bpp, sRGB, 8-bit Alpha)"),
    ("BC3_UNORM", "BC3 (8bpp, Linear, 8-bit Alpha)"),
    ("BC4_UNORM", "BC4 (4bpp, Grayscale)"),
    ("BC5_UNORM", "BC5 (8bpp, Unsigned, 2-channel normal)"),
    ("BC5_SNORM", "BC5 (8bpp, Signed, 2-channel normal)"),
    ("BC7_UNORM_SRGB", "BC7 (8bpp, sRGB, 8-bit Alpha)"),
    ("BC7_UNORM", "BC7 (8bpp, Linear, 8-bit Alpha)"),
    ("DXT1", "DXT1 (4bpp, Linear, 1-bit Alpha)"),
    ("DXT3", "DXT3 (8bpp, Linear, 4-bit Alpha)"),
    ("DXT5", "DXT5 (8bpp, Linear, 8-bit Alpha)"),
    ("R8G8B8A8_UNORM_SRGB", "RGBA (32bpp, sRGB, 8-bit Alpha)"),
    ("R8G8B8A8_UNORM", "RGBA (32bpp, Linear, 8-bit Alpha)"),
    ("B8G8R8A8_UNORM_SRGB", "BGRA (32bpp, sRGB, 8-bit Alpha)"),
    ("B8G8R8A8_UNORM", "BGRA (32bpp, Linear, 8-bit Alpha)"),
    ("B5G5R5A1_UNORM", "BGRA (16bpp, Linear, 1-bit Alpha)"),
    ("B5G6R5_UNORM", "BGR (16bpp, Linear)"),
    ("B8G8R8X8_UNORM_SRGB", "BGRX (32bpp, sRGB)"),
    ("B8G8R8X8_UNORM", "BGRX (32bpp, Linear)"),
    ("R8G8_UNORM", "RG (16bpp, Linear)"),
    ("R8_UNORM", "R (8bpp, Linear)"),
]

SUPPORTED_FORMATS = {f for f, _ in SUPPORTED_DDS_FORMATS}
SUPPORTED_BC7_FORMATS = list(SUPPORTED_FORMATS.intersection(BC7_FORMATS))
SUPPORTED_BC123_FORMATS = list(SUPPORTED_FORMATS.intersection(BC123_FORMATS))
SUPPORTED_WITH_ALPHA = list(SUPPORTED_FORMATS.intersection(WITH_ALPHA))


class DDSErrorMetric(Enum):
    PERCEPTUAL = 0
    UNIFORM = 1


class BC7Compression(Enum):
    BEST_SPEED = 1
    DEFAULT = 0
    BEST_QUALITY = 2

def save_image_node(
    lazy_image: Lazy[np.ndarray],
    base_directory: Path,
    relative_path: str | None,
    filename: str,
    image_format: ImageFormat,
    png_color_depth: PngColorDepth,
    webp_lossless: bool,
    quality: int,
    jpeg_chroma_subsampling: JpegSubsampling,
    jpeg_progressive: bool,
    tiff_color_depth: TiffColorDepth,
    tiff_compression: TiffCompression,
    dds_format: DDSFormat,
    dds_bc7_compression: BC7Compression,
    dds_error_metric: DDSErrorMetric,
    dds_dithering: bool,
    dds_mipmap_levels: int,
    dds_separate_alpha: bool,
    avif_chroma_subsampling: AvifSubsampling,
    skip_existing_files: bool,
) -> None:
    full_path = get_full_path(base_directory, relative_path, filename, image_format)

    if full_path.exists():
        if skip_existing_files:
            logger.debug(f"Skipping existing file: {full_path}")
            return
    else:
        # Create directory if it doesn't exist
        full_path.parent.mkdir(parents=True, exist_ok=True)

    logger.debug(f"Writing image to path: {full_path}")
    img = lazy_image.value

    # DDS files are handled separately
    if image_format == ImageFormat.DDS:
        # we only support 8bits of precision for DDS
        img = to_uint8(img, normalized=True)

        # remap legacy DX9 formats
        legacy_dds = dds_format in LEGACY_TO_DXGI or dds_format in PREFER_DX9

        save_as_dds(
            full_path,
            img,
            to_dxgi(dds_format),
            mipmap_levels=dds_mipmap_levels,
            dithering=dds_dithering,
            uniform_weighting=dds_error_metric == DDSErrorMetric.UNIFORM,
            minimal_compression=dds_bc7_compression == BC7Compression.BEST_SPEED,
            maximum_compression=dds_bc7_compression == BC7Compression.BEST_QUALITY,
            dx9=legacy_dds,
            separate_alpha=dds_separate_alpha,
        )
        return

    # Some formats are handled by PIL
    if image_format in (ImageFormat.GIF, ImageFormat.TGA, ImageFormat.AVIF):
        # we only support 8bits of precision for those formats
        img = to_uint8(img, normalized=True)
        args = {}

        if image_format == ImageFormat.AVIF:
            args["quality"] = quality
            args["subsampling"] = avif_chroma_subsampling.value

        channels = get_h_w_c(img)[2]
        if channels == 1:
            # PIL supports grayscale images just fine, so we don't need to do any conversion
            pass
        elif channels == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif channels == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
        else:
            raise RuntimeError(
                f"Unsupported number of channels. Saving .{image_format.extension} images is only supported for "
                f"grayscale, RGB, and RGBA images."
            )

        with Image.fromarray(img) as image:
            image.save(full_path, **args)

    else:
        params: list[int]
        if image_format == ImageFormat.JPG:
            params = [
                cv2.IMWRITE_JPEG_QUALITY,
                quality,
                cv2.IMWRITE_JPEG_SAMPLING_FACTOR,
                jpeg_chroma_subsampling.value,
                cv2.IMWRITE_JPEG_PROGRESSIVE,
                int(jpeg_progressive),
            ]
        elif image_format == ImageFormat.WEBP:
            params = [cv2.IMWRITE_WEBP_QUALITY, 101 if webp_lossless else quality]
        elif (
            image_format == ImageFormat.TIFF and tiff_color_depth != TiffColorDepth.F32
        ):
            params = [cv2.IMWRITE_TIFF_COMPRESSION, tiff_compression.cv2_code]
        else:
            params = []

        # the bit depth depends on the image format and settings
        precision: Literal["u8", "u16", "f32"] = "u8"
        if image_format == ImageFormat.PNG:
            if png_color_depth == PngColorDepth.U16:
                precision = "u16"
        elif image_format == ImageFormat.TIFF:
            if tiff_color_depth == TiffColorDepth.U16:
                precision = "u16"
            elif tiff_color_depth == TiffColorDepth.F32:
                precision = "f32"

        if precision == "u8":
            img = to_uint8(img, normalized=True)
        elif precision == "u16":
            img = to_uint16(img, normalized=True)
        elif precision == "f32":
            # chainner images are always f32
            pass

        cv_save_image(full_path, img, params)


def get_full_path(
    base_directory: Path,
    relative_path: str | None,
    filename: str,
    image_format: ImageFormat,
) -> Path:
    file = f"{filename}.{image_format.extension}"
    if relative_path and relative_path != ".":
        base_directory = base_directory / relative_path
    full_path = base_directory / file
    return full_path.resolve()
