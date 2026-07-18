"""Convert a prepped portrait photo into an animated ASCII-art SVG.
Downsamples the image to a character grid, maps per-cell brightness to
a density ramp, and animates the rows typing in left-to-right (SMIL,
freezes after playing once so it doesn't loop forever on the profile page).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
COLS = 100
ROWS = 55
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.0
ROW_DELAY = 0.05
ROW_DURATION = 0.6


def brightness_to_char(v: float) -> str:
    idx = int(v / 255 * (len(RAMP) - 1))
    return RAMP[idx]


def image_to_grid(path: str) -> list[str]:
    img = Image.open(path).convert("L").resize((COLS, ROWS), Image.LANCZOS)
    arr = np.array(img)
    return ["".join(brightness_to_char(v) for v in row) for row in arr]


def escape(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def build_svg(grid: list[str]) -> str:
    width = COLS * CHAR_W
    height = ROWS * CHAR_H

    rows_svg = []
    for i, row in enumerate(grid):
        y = (i + 1) * CHAR_H
        begin = i * ROW_DELAY
        text = "".join(escape(c) for c in row)
        rows_svg.append(
            f'  <text x="0" y="{y:.1f}" class="row" opacity="0">'
            f'{text}'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{begin:.2f}s" dur="{ROW_DURATION:.2f}s" fill="freeze"/>'
            f"</text>"
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" font-family="monospace">
  <style>
    .row {{ font-size: {FONT_SIZE}px; fill: #39d353; white-space: pre; }}
    svg {{ background: #0d1117; }}
  </style>
  <rect width="100%" height="100%" fill="#0d1117"/>
{chr(10).join(rows_svg)}
</svg>
"""


def main(src_path: str, dst_path: str) -> None:
    grid = image_to_grid(src_path)
    svg = build_svg(grid)
    Path(dst_path).write_text(svg)
    print(f"Wrote {dst_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "prepped_photo.png"
    dst = sys.argv[2] if len(sys.argv) > 2 else "../bhavya-ascii.svg"
    main(src, dst)
