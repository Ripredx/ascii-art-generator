from PIL import Image, ImageOps
import pyfiglet
from typing import Optional
from utils.constants import CHAR_SETS


class AsciiEngine:
    @staticmethod
    def image_to_ascii(
        img: Image.Image,
        charset_name: str,
        width: int = 120,
        contrast: float = 1.0,
        brightness: float = 1.0,
        invert: bool = False,
    ) -> str:
        chars = CHAR_SETS.get(charset_name, CHAR_SETS["Standard"])

        aspect_ratio = img.height / img.width
        new_height = int(width * aspect_ratio * 0.55)
        new_height = max(1, new_height)

        try:
            resample_filter = Image.Resampling.LANCZOS
        except AttributeError:
            resample_filter = Image.LANCZOS  # type: ignore[attr-defined]

        img_resized = img.resize((width, new_height), resample_filter)
        img_l = img_resized.convert("L")

        # Apply contrast / brightness via pixel mapping
        if contrast != 1.0 or brightness != 1.0:
            from PIL import ImageEnhance

            img_l = ImageEnhance.Contrast(img_l).enhance(contrast)
            img_l = ImageEnhance.Brightness(img_l).enhance(brightness)

        if invert:
            img_l = ImageOps.invert(img_l)

        pixels = list(img_l.getdata())
        char_count = len(chars) - 1

        rows = []
        for row_start in range(0, len(pixels), width):
            row_pixels = pixels[row_start : row_start + width]
            row = "".join(
                chars[min(int(p / 256 * len(chars)), char_count)] for p in row_pixels
            )
            rows.append(row)

        return "\n".join(rows)

    @staticmethod
    def text_to_ascii(text: str, font: str = "standard") -> Optional[str]:
        if not text:
            return None
        try:
            return pyfiglet.figlet_format(text, font=font)
        except Exception:
            # Fall back to standard if the chosen font fails
            try:
                return pyfiglet.figlet_format(text, font="standard")
            except Exception:
                return None
