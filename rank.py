#!/usr/bin/env python3
"""Fetch GitHub stats for items.txt, score + rank per category, write data/<date>.json and data/latest.json."""
import json
import math
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"


def fetch(repo, token):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "hype-index"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}", headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def score(stars, gain, days_since_push):
    # ponytail: hand-tuned weights; retune once a few weeks of history exist
    popularity = math.log10(stars + 1)               # size, ~0-5
    momentum = math.log10(gain + 1) if gain > 0 else 0  # weekly star gain, log so giants don't always win
    freshness = math.exp(-days_since_push / 30)       # 1.0 = pushed today, fades over ~a month
    return round(popularity + 2 * momentum + 2 * freshness, 3)


def rank(items, prev):
    """items: dicts with category, repo, stars, days_since_push. prev: {repo: last week's item}."""
    for it in items:
        p = prev.get(it["repo"])
        it["gain"] = it["stars"] - p["stars"] if p else None
        it["score"] = score(it["stars"], it["gain"] or 0, it["days_since_push"])
    cats = {}
    for it in sorted(items, key=lambda x: -x["score"]):
        cats.setdefault(it["category"], []).append(it)
    for members in cats.values():
        for i, it in enumerate(members, 1):
            it["rank"] = i
            p = prev.get(it["repo"])
            it["delta"] = p["rank"] - i if p else None  # None = NEW
    return cats


def main():
    token = os.environ.get("GITHUB_TOKEN")
    now = datetime.now(timezone.utc)
    latest = DATA / "latest.json"
    # ponytail: "previous" = last run, so run weekly; running twice in a week shrinks the deltas
    prev = {}
    if latest.exists():
        for members in json.loads(latest.read_text())["categories"].values():
            prev.update({it["repo"]: it for it in members})

    items = []
    for line in (ROOT / "items.txt").read_text().splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        category, repo = line.split()
        try:
            r = fetch(repo, token)
        except urllib.error.HTTPError as e:
            print(f"skip {repo}: HTTP {e.code}", file=sys.stderr)
            continue
        pushed = datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))
        items.append({
            "category": category,
            "repo": r["full_name"],
            "url": r["html_url"],
            "description": r["description"] or "",
            "stars": r["stargazers_count"],
            "days_since_push": (now - pushed).days,
        })

    out = json.dumps({"generated": now.isoformat(timespec="seconds"), "categories": rank(items, prev)}, indent=1)
    DATA.mkdir(exist_ok=True)
    (DATA / f"{now:%Y-%m-%d}.json").write_text(out)
    latest.write_text(out)
    print(f"ranked {len(items)} items")


if __name__ == "__main__":
    main()
