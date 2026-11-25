# Hype Index

**Weekly power rankings for AI skills, agents & MCP servers.** For AI enthusiasts: which tools are rising, falling, and worth your time — ranked per category.

**Live:** https://j2jun.github.io/hype-index/

## How it works
- `items.txt` — what's tracked (`category owner/repo`, one per line).
- `rank.py` — every Monday a GitHub Action pulls GitHub stats, scores each item, and commits a snapshot to `data/`. Stdlib Python, no dependencies.
- `index.html` — static page on GitHub Pages that renders `data/latest.json`.

**Score** = popularity (log stars) + 2 × momentum (log weekly star gain) + 2 × freshness (decays ~30 days after last push). Rank arrows compare to last week; `NEW` = first appearance.

## Add something
Open a PR adding a line to `items.txt`.

## Run locally
```
python3 test_rank.py
GITHUB_TOKEN=$(gh auth token) python3 rank.py
python3 -m http.server   # open http://localhost:8000
```

More ideas: [IDEAS.md](IDEAS.md).
