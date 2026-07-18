"""Scrape a GitHub user's public contribution calendar (no token needed —
this is the same HTML fragment that renders the graph on the profile page)
and write it to data/contributions.json for render_heatmap_svg.py.
"""
import json
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Bhavyashah20"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch(username: str) -> list[dict]:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, td[data-date]"):
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        if level is None:
            # older markup: level encoded in a numbered CSS class
            classes = cell.get("class", [])
            level = next((c.split("-")[-1] for c in classes if c.startswith("contrib-")), "0")
        days.append({"date": date, "level": int(level)})

    return days


def main(username: str, dst_path: str) -> None:
    days = fetch(username)
    if not days:
        raise RuntimeError(
            "No contribution cells found — GitHub may have changed its markup, "
            "or the profile has no public activity."
        )
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
    Path(dst_path).write_text(json.dumps(days, indent=2))
    print(f"Wrote {len(days)} days to {dst_path}")


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    dst = sys.argv[2] if len(sys.argv) > 2 else "../data/contributions.json"
    main(username, dst)
