"""Hand-authored neofetch-style info card SVG: colored key/value rows
that fade in one at a time (SMIL, staggered begin times, freezes after
playing). Edit FIELDS below to change what's displayed.
"""
from pathlib import Path

USER = "bhavyashah20@"
HOST = "github"
FIELDS = [
    ("Role", "Research Assistant @ Georgia Tech FSIL"),
    ("Edu", "B.Tech CS, SPIT Mumbai"),
    ("Stack", "Python, PyTorch, LangChain, React, SQL"),
    ("Focus", "Financial NLP, LLM agents, time-series forecasting"),
    ("Papers", "3 (ICCCMLA'25, ICMI'26, SEGAN under review)"),
]

FONT_SIZE = 13
LINE_H = FONT_SIZE * 1.8
PAD_X = 16
PAD_TOP = 30
ROW_DELAY = 0.25
ROW_DURATION = 0.5
KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"

CHAR_W = FONT_SIZE * 0.62
_longest_line = max(
    [f"{USER}{HOST}"] + [f"{key}: {val}" for key, val in FIELDS],
    key=len,
)
WIDTH = int(PAD_X * 2 + len(_longest_line) * CHAR_W) + 10
HEIGHT = PAD_TOP + LINE_H * (len(FIELDS) + 1) + 20


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    lines = []

    header = f"{USER}{HOST}"
    lines.append(
        f'  <text x="{PAD_X}" y="{PAD_TOP}" font-weight="bold" fill="{KEY_COLOR}" '
        f'font-size="{FONT_SIZE + 2}" opacity="0">{escape(header)}'
        f'<animate attributeName="opacity" from="0" to="1" begin="0s" dur="{ROW_DURATION}s" fill="freeze"/>'
        f"</text>"
    )
    sep_y = PAD_TOP + 10
    lines.append(
        f'  <line x1="{PAD_X}" y1="{sep_y}" x2="{WIDTH - PAD_X}" y2="{sep_y}" '
        f'stroke="{BORDER_COLOR}" opacity="0">'
        f'<animate attributeName="opacity" from="0" to="1" begin="0.1s" dur="{ROW_DURATION}s" fill="freeze"/>'
        f"</line>"
    )

    for i, (key, val) in enumerate(FIELDS):
        y = PAD_TOP + LINE_H * (i + 1)
        begin = 0.3 + i * ROW_DELAY
        lines.append(
            f'  <text x="{PAD_X}" y="{y:.1f}" font-size="{FONT_SIZE}" opacity="0">'
            f'<tspan fill="{KEY_COLOR}" font-weight="bold">{escape(key)}: </tspan>'
            f'<tspan fill="{VAL_COLOR}">{escape(val)}</tspan>'
            f'<animate attributeName="opacity" from="0" to="1" begin="{begin:.2f}s" dur="{ROW_DURATION}s" fill="freeze"/>'
            f"</text>"
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT:.0f}" font-family="monospace">
  <rect width="100%" height="100%" rx="6" fill="{BG_COLOR}" stroke="{BORDER_COLOR}"/>
{chr(10).join(lines)}
</svg>
"""


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "info-card.svg"
    out.write_text(build_svg())
    print(f"Wrote {out}")
