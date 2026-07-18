"""Render data/contributions.json into a 53x7 GitHub-style contribution
heatmap SVG, with squares revealing diagonally (SMIL, freezes after
playing once).
"""
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 11
GAP = 3
PAD = 20
COLS = 53
ROWS = 7
STEP_DELAY = 0.015
REVEAL_DURATION = 0.3


def load_weeks(json_path: str) -> list[list[int]]:
    days = json.loads(Path(json_path).read_text())
    by_date = {d["date"]: d["level"] for d in days}
    dates = sorted(by_date)
    if not dates:
        raise RuntimeError("contributions.json is empty")

    # Bucket into ISO weeks (Sun-Sat, matching GitHub's calendar) x 7
    first = datetime.strptime(dates[0], "%Y-%m-%d")
    start_offset = (first.weekday() + 1) % 7  # days since preceding Sunday
    grid = defaultdict(lambda: [0] * ROWS)
    for date_str in dates:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        day_index = (d - first).days + start_offset
        week = day_index // 7
        weekday = day_index % 7
        grid[week][weekday] = by_date[date_str]

    max_week = max(grid) if grid else 0
    weeks = [grid[w] for w in range(max_week + 1)]
    return weeks[-COLS:] if len(weeks) > COLS else weeks


def build_svg(weeks: list[list[int]]) -> str:
    width = PAD * 2 + len(weeks) * (CELL + GAP)
    height = PAD * 2 + ROWS * (CELL + GAP)

    cells = []
    for col, week in enumerate(weeks):
        for row, level in enumerate(week):
            x = PAD + col * (CELL + GAP)
            y = PAD + row * (CELL + GAP)
            color = PALETTE[min(level, len(PALETTE) - 1)]
            begin = (col + row) * STEP_DELAY
            cells.append(
                f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.3f}s" dur="{REVEAL_DURATION}s" fill="freeze"/>'
                f"</rect>"
            )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#0d1117"/>
{chr(10).join(cells)}
</svg>
"""


def main(src_path: str, dst_path: str) -> None:
    weeks = load_weeks(src_path)
    svg = build_svg(weeks)
    Path(dst_path).write_text(svg)
    print(f"Wrote {dst_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "../data/contributions.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "../contrib-heatmap.svg"
    main(src, dst)
