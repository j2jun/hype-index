# Ideas

## Categories
- Claude Code skills / plugins
- Agents & agent frameworks
- MCP servers
- Models (open + closed)
- Dev tools / IDEs / CLIs
- Prompts & workflows

## Signals (free sources)
- GitHub: stars, star velocity, forks, commits, issue activity
- Hacker News (Algolia API): mentions, points
- Reddit (r/LocalLLaMA, r/ClaudeAI): mentions, upvotes
- Hugging Face: downloads, likes
- npm / PyPI: weekly downloads
- Awesome-lists and plugin/skill marketplaces: inclusion

## Score
- Popularity (absolute size), Momentum (week-over-week change), Relevance (recency + activity)
- Weighted per category; show rank delta (▲3 / ▼2 / NEW)

## Delivery
- GitHub Actions cron → fetch → JSON snapshot committed to repo → static site on GitHub Pages
- Zero cost, no server, history = git log
