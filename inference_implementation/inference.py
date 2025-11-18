from __future__ import annotations
import numpy as np
import torch
from PIL import Image
from .pytorch import auto_split
from .tools import resize, save_image
from .upscale.tiler import MaxTileSize
from spandrel import ImageModelDescriptor, ModelLoader
from .image_dimension.resize import resize_to_side
from .api.lazy import Lazy
from pathlib import Path
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class InferenceImplementation:
    def __init__(self):
        pass

    def process_image(self, input_file: str, model_file: str, output_file: str):
        """
        Process an image using the specified model and save the output.

        Args:
            input_file (str): Path to the input image file.
            model_file (str): Path to the model file.
            output_file (str): Path to save the output image.
        """

        # loading GPU
        device_gpu = torch.device("cuda:0")

        # loads a model from disk
        model = ModelLoader().load_from_file(model_file)
        # making sure it's an image-to-image model before preparing it for inference
        assert isinstance(model, ImageModelDescriptor)
        _ = model.cuda().eval()

        # set tile size to maximum possible (low VRAM usage is the default)
        tiler = MaxTileSize()
        # open image and convert to grayscale
        img_pil = Image.open(input_file).convert("L")
        img_np = np.array(img_pil, dtype=np.float32) / 255.0

        # resize image to a standard size keeping aspect ratio (the 2nd argument is the longest side of the screen)
        img_rts = resize_to_side.resize_to_side_node(
            img_np,
            2420,
            resize_to_side.SideSelection.LONGER_SIDE,
            resize_to_side.ResizeCondition.DOWNSCALE,
            resize.ResizeFilter.LANCZOS,
        )

        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                'process_group',
                {
                    'type': 'process.message',
                    'message': 'Inference | Image resized, processing...'
                }
            )

        # process image
        img_out = auto_split.pytorch_auto_split(img_rts, model, device_gpu, False, tiler)

        # computing output image after upscaling
        output_img = img_out * 255.0
        output_np_uint8 = np.clip(output_img, 0, 255).astype(np.uint8)
        output_np_2d = output_np_uint8.squeeze()

        # saving image
        save_image.save_image_node(
            Lazy.ready(output_np_2d),
            Path(model_file).parent,
            None,
            output_file,
            save_image.ImageFormat.JPG,
            save_image.PngColorDepth.U16,
            True,
            71,
            save_image.JpegSubsampling.FACTOR_444,
            False,
            save_image.TiffColorDepth.F32,
            save_image.TiffCompression.NONE,
            "R8_UNORM",  # texture compression format
            save_image.BC7Compression.BEST_QUALITY,  # BC7 compression speed/quality
            save_image.DDSErrorMetric.UNIFORM,  # error metric optimized for human eye
            True,  # enable dithering to reduce banding
            10,  # number of mipmap levels to generate
            False,  # do not separate alpha channel
            save_image.AvifSubsampling.FACTOR_444,  # color subsampling (maximum quality)
            False,  # ignore if output file already exists
        )


    # if __name__ == "__main__":
    #     import argparse

    #     parser = argparse.ArgumentParser(
    #         description="Process an image using a specified model."
    #     )
    #     parser.add_argument("input_file", type=str, help="Path to the input image file.")
    #     parser.add_argument("model_file", type=str, help="Path to the model file.")
    #     parser.add_argument("output_file", type=str, help="Path to save the output image.")

    #     args = parser.parse_args()
    #     process_image(args.input_file, args.model_file, args.output_file)
