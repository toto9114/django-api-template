from PIL import Image
from io import BytesIO
import numpy as np


def to_webp(
    pil_image: Image.Image,
    lossless: bool = True,
    quality: int = 80,
    method: int = 4,
    max_side: int = 3000,
    resample=Image.BILINEAR,
) -> BytesIO:
    input_size = pil_image.size

    def alpha_composite(src, dst):
        """
        Return the alpha composite of src and dst.

        Parameters:
        src -- PIL RGBA Image object
        dst -- PIL RGBA Image object

        The algorithm comes from http://en.wikipedia.org/wiki/Alpha_compositing
        """
        # http://stackoverflow.com/a/3375291/190597
        # http://stackoverflow.com/a/9166671/190597
        src = np.asarray(src)
        dst = np.asarray(dst)
        out = np.empty(src.shape, dtype="float")
        alpha = np.index_exp[:, :, 3:]
        rgb = np.index_exp[:, :, :3]
        src_a = src[alpha] / 255.0
        dst_a = dst[alpha] / 255.0
        out[alpha] = src_a + dst_a * (1 - src_a)
        old_setting = np.seterr(invalid="ignore")
        out[rgb] = (src[rgb] * src_a + dst[rgb] * dst_a * (1 - src_a)) / out[alpha]
        np.seterr(**old_setting)
        out[alpha] *= 255
        np.clip(out, 0, 255)
        # astype('uint8') maps np.nan (and np.inf) to 0
        out = out.astype("uint8")
        out = Image.fromarray(out, "RGBA")
        return out

    # Scale down large images
    scale: float = max_side / max(input_size)
    if scale < 1:
        output_size = tuple([int(s * scale) for s in input_size])
        pil_image = pil_image.resize(output_size, resample)

    # Convert to RGB colorspace if necessary
    if pil_image.mode != "RGB":
        if pil_image.mode == "RGBA":
            white_background = Image.new("RGBA", pil_image.size, (255, 255, 255, 255))
            pil_image = alpha_composite(pil_image, white_background).convert("RGB")
        else:
            pil_image = pil_image.convert("RGB")

    temp = BytesIO()
    # Store the image in WebP format
    pil_image.save(
        temp, lossless=lossless, quality=quality, method=method, format="webp"
    )
    return temp
