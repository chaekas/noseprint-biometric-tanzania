from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError


def load_rgb_image(raw: bytes) -> Image.Image:
    try:
        image = Image.open(BytesIO(raw))
        image = ImageOps.exif_transpose(image).convert("RGB")
        image.load()
        return image
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Uploaded file is not a valid image.") from exc
