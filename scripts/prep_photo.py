"""Clean up a source photo for ASCII conversion: remove background,
boost local contrast, and composite onto a plain white canvas so the
character-density mapping in make_ascii_svg.py has a clean signal.
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


def prep_photo(src_path: str, dst_path: str, size: int = 512) -> None:
    src = Image.open(src_path).convert("RGBA")

    # 1. Remove background
    no_bg = remove(src)

    # 2. Composite onto white
    white_bg = Image.new("RGBA", no_bg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, no_bg).convert("RGB")

    # 3. Square crop + resize
    w, h = composited.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    composited = composited.crop((left, top, left + side, top + side))
    composited = composited.resize((size, size), Image.LANCZOS)

    # 4. Adaptive contrast enhancement (CLAHE) on luminance channel
    arr = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(arr)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    arr = cv2.merge((l, a, b))
    result = cv2.cvtColor(arr, cv2.COLOR_LAB2RGB)

    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(dst_path)
    print(f"Wrote {dst_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source_photo.png"
    dst = sys.argv[2] if len(sys.argv) > 2 else "prepped_photo.png"
    prep_photo(src, dst)
