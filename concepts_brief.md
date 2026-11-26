# Hype Index v2: Rankings for Claude Code and Codex Add-ons

* **Author:** j2jun
* **Date:** 2026-11-25
* **Status:** Brainstorm, after two rounds of independent review (7 reviewers each)

## Overview

Hype Index is a free weekly power ranking of the add-ons people install into **Claude Code** and **Codex**:

- MCP servers
- plugins, with the skills and subagents they bundle listed under them

It is for technical AI enthusiasts who want to know what is worth installing this week.

v1 is live at https://j2jun.github.io/hype-index/. It ranks 20 hand-picked MCP servers on GitHub stars and recent pushes.

v2 makes four changes:

- The bot finds candidates on its own from curated lists, with no human approval step.
- Items are ranked on evidence from at least two independent free sources.
- Every number, every status, and the reason for it are public.
- The page gets its own visual identity.

The success measure is trust. A reader should be able to check why any item is where it is, and why an item is missing.

## Analysis

### A. Failed fetches must never look like ranking changes (round 1, all reviewers)

Today, a timeout crashes the run, and a rate-limit error drops the item. The next week the item comes back labelled NEW, and its history is gone.

**Fix:**

- **Never treat a missing value as zero.** Carry the last good value forward and mark it "stale".
- **Publish gate.** Refuse to publish when more than 15% of fetches fail: keep the last good board and fail the job, so GitHub emails the owner.
- **Stale banner.** Show a banner on the page when the board is more than 8 days old. This also catches a cron that GitHub has silently disabled.

### B. Keep the bot's memory separate from the page (round 1)

- **Separate files.** `data/state.json` holds first-seen dates, last good values, compatibility, and star-check results. The page never reads it. `data/latest.json` is derived from it for the page.
- **Version fields.**
  - `schema_version`: a file without it is treated as v1.
  - `score_version`: when the formula changes, the page shows "rescored" instead of fake rank arrows.
- **Rollback.** Revert the code and restore `data/latest.json` from a known-good dated snapshot.

### C. The unit of ranking: rank only what can be measured on its own (round 2, all reviewers)

GitHub stars, pushes, and Hacker News links belong to a **repo**, not to a plugin inside it.

Most plugins sit in shared marketplace repos (`source: ./plugins/foo`). If each plugin were ranked, every plugin in a big repo would show the same stars and the same gain, and their order would be meaningless. The same problem already affects `modelcontextprotocol/servers` and `awslabs/mcp` in v1.

**Proposed rule:**

- **Item ID** = lowercased `owner/repo`, plus an optional subpath. The 20 existing histories map onto this without a lookup table.
- **The ranked row is the repo.**
  - A repo with one add-on gets its own ranked row.
  - A repo with several plugins or servers becomes one **collection** row, with its contents listed underneath and labelled "collection".
- **Collections are kept apart from single add-ons.** They either sit in their own lane or are visibly labelled, so a giant collection doesn't crowd out single add-ons.
- **Skills and subagents** are listed under their parent plugin. Each gets its own ID now, so promoting standalone skills later doesn't split their history.
- **One project, one category.** A project found both as an MCP server (MCP Registry) and as a plugin (marketplace) is ranked once:
  - a repo whose main job is an MCP server goes to `mcp-servers`
  - everything else goes to `plugins`
  - `recat` is the manual fix

### D. The two-source rule, stated per category (rounds 1–2)

The sources cause each other: a Hacker News front page causes star growth. Sources therefore count only when they are linked through links the project itself declares. Items are compared by percentile within their category.

- **mcp-servers:** ranked when the item is in the top 50% of its category on GitHub star growth **and** has a declared package with real downloads:
  - npm `repository` field, or PyPI `project_urls`
  - downloads in the top 50% of the category
  
  This rule is strong, because downloads are a separate signal from stars.

- **plugins (proposal):** GitHub star growth plus **public adoption**. Neither tool publishes install counts, but people commit their config files to public repos:
  - `.claude/settings.json` with `enabledPlugins` entries
  - `.mcp.json` files
  - Codex `config.toml` `[mcp_servers]` blocks
  
  The adoption signal is the number of **distinct repo owners** whose public config names the item. It is real usage and it is independent of stars.

  **Limits of the adoption signal:**
  - GitHub code search allows about 10 requests per minute and gives approximate counts.
  - It sees only default branches, so it undercounts private use.
  - It probably needs a free personal access token stored as a repo secret, because the Actions token may not be allowed to search all of GitHub. This is unverified.

  **Rejected as a second source:** "how many marketplaces list it". A marketplace is a file anyone can create for free, so three self-made marketplaces would pass the rule.
  
  Marketplace listings count only as discovery, and a listing counts only when the marketplace owner is different from the plugin owner.

- **Every category header** shows its rule in one sentence.
- **Every row** shows which sources counted: "GitHub ✓ npm ✓ adoption –".

### E. Discovery: a small stated starting list (round 2)

There is no central registry of plugin marketplaces. The bot needs a short **hand-made seed list**: the official marketplaces plus a few known aggregators, kept in `overrides.txt`. The page states this openly as a human choice.

The list grows on its own:

- A marketplace that is mentioned by an existing marketplace, or appears in public settings files, is added.
- One capped code search per week sweeps for new marketplaces. It is a backup, not the main discovery path.

**Fetching:**

- **No API quota.** Manifests come from `raw.githubusercontent.com`.
- **MCP candidates** come from the official MCP Registry.
- **Hard call budget.** When it runs out, values are carried forward as "stale".
- **Size caps.** At most about 50 ranked items plus 20 on probation per category. Items are retired after 8 weeks without gain.

**Codex gap:** none of these sources finds Codex-only add-ons. Either a Codex discovery source is named, or the page says that Codex coverage only reflects items found through the other sources.

### F. Compatibility with Claude Code and Codex (round 2)

Compatibility comes from **declared metadata only**, never from reading README text:

- **MCP servers:** MCP is a shared protocol, so a server works in both tools through MCP. The table shows "✓ via MCP" for both, based on the transport (stdio or HTTP) declared in the MCP Registry's `server.json`. A short, maintained table lists which transports each tool supports.
- **Plugins:**
  - Claude Code: a `.claude-plugin/` folder, or a marketplace entry that defines the plugin.
  - Codex: a `.codex-plugin/` folder. The EGM plugin ships one, but **check this against the Codex documentation before building on it**.
  - Skills: a `SKILL.md` file. Both tools read this format.
- **Symbols:**
  - **✓** = declared support.
  - **–** = not declared by the project; it may still work. This legend sits next to the columns, not in a footnote.
  - **✗** = known not to work. Only a manual override can set it: `incompat <id> <tool> # reason`.
- **Evidence.** The decisions log stores the evidence for each ✓ (file path or registry field). Detection results are cached by commit, so they aren't fetched again every week.
- **Layout.** Compatibility appears as **two narrow columns in the main ranking table**, plus a "Works with: All / Claude Code / Codex" filter. A separate grid beside the table would repeat every row and wouldn't fit on phones. The grid can be an optional view.

### G. Hashtags for describing what an item does (author's idea)

**Category vs. hashtags:**

- **Category** (one per item) decides which board the item is on.
- **Hashtags** (several per item) describe what it does: `#browser #database #testing #docs #security`. Readers click them to filter.

**Where tags come from:**

- **Sources.** GitHub `topics` (already in the API response v1 fetches) and plugin `keywords` in `plugin.json`, at no extra cost.
- **Fixed vocabulary.** There is a fixed list of about 15–20 tags, and raw topics are mapped onto it. For example, `playwright`, `puppeteer`, and `browser-automation` all become `#browser`. Generic tags (`#ai #llm #claude #mcp`) are dropped because they would match everything.
- **No effect on rank.** Tags are for filtering only, so tag spam gives no advantage.
- **No per-tag rankings.** There are no lists like "#1 in #database", because small lists are noisy and easy to game.
- **Manual fix:** `tag <id> #browser`.

### H. The bought-star check: a note only (round 2)

**What it does:**

- **The query.** One GraphQL query returns the newest 100 stargazers of a repo, with when each starred it and when each account was created.

**When it runs:**

- when an item is first seen (new items are where bought bursts are most likely)
- when weekly gain is above 3 times its 4-week median and above 200 stars
- again after 4 weeks

**What the page shows:**

- **A comparison.** The note always shows the category baseline: "41% of the newest 100 stargazers have accounts under 30 days old (category median: 7%). Checked 2026-12-07." Many people create GitHub accounts just to use AI tools, so a bare percentage would mislead.
- **Neutral wording.** The note links to the method and does not accuse anyone.
- **The check's status:** checked and clean, checked with a note, not checked, skipped (budget), or failed.
- **No effect on rank.** The note does not change rank.

**What is stored:** only the summary, never the sampled accounts, which would publish other people's account data.

### I. Reader reports: an issue form, not a pull request (round 2, all reviewers)

A link can't open a pre-filled pull request that adds one line to an existing file. Instead:

- **Issue form.** Each row has a "Report" link that opens a GitHub **issue form**, pre-filled with the item ID. It has a reason dropdown, and each reason maps to one override line:
  - spam or abuse → `block`
  - bought stars → `flag`
  - wrong compatibility → `incompat`
  - wrong category → `recat`
  - wrong tag → `tag`
  - other
- **Owner turns reports into overrides.** The owner writes the override line, citing the issue number in its reason. The issue stays as the public record.
- **Named exception.** This is the one human step in an otherwise hands-off design. It is needed only when someone reports something.

### J. One override file

The file is `overrides.txt`. Humans edit it; the bot never writes to it. Each line uses one verb, and every line needs a `# reason`:

- `seed-marketplace <repo>`
- `pin <category> <id>`
- `recat <category> <id>`
- `block <id>`
- `allow <id>`
- `flag <id>`
- `incompat <id> <tool>`
- `tag <id> #tag`

An unknown verb fails the run, instead of the line being silently skipped. `items.txt` becomes `pin` lines for the 20 existing items.

### K. Timing, probation, and rollout (rounds 1–2)

**Timing and score:**

- **Gains** are measured against the dated snapshot closest to 7 days ago, and converted to a 7-day rate.
- **Probation** is counted from `first_seen` dates, not from runs. An item graduates after passing its category rule two weeks in a row, and returns to probation after failing twice.
- **Rising lane.** Probation items appear there with their numbers but no rank number.
- **The freshness term** gives every current item about the same bonus, and daily pushes can game it.
  - **Fix:** replace it with releases in the last 30 days.

**Rollout:**

- **Shadow mode for both categories.** New rules are computed and shown, but nothing is demoted, for **4 weekly snapshots**.
  - A single `shadow` flag controls it, and switching the flag back is the rollback.
  - The 20 existing items keep `data/2026-11-25.json` as their first-seen date.

**Workflow fixes:**

- add a `concurrency:` group
- run `git pull --rebase` before pushing
- treat a failed push as a failure, not as "no changes"
- add a keepalive step in case GitHub's 60-day auto-disable applies. It is unverified whether the bot's own commits count as activity.

### L. Visible run health (round 2)

- **Run summary.** Each run writes one to the GitHub job summary and to `data/<date>.decisions.json`. It records:
  - calls made and failed per source
  - API quota left
  - items marked stale
  - unreadable marketplace entries
  - why each candidate passed or failed
- **Page footer:** "Last run 2026-12-07 · sources OK 4/4 · 3 items stale".
- **Gate failures** name the source and the failure rate that caused them.

## Goals vs. Non-Goals

**In-scope goals:**

- Rank Claude Code and Codex add-ons: MCP servers and plugins, with bundled skills and subagents listed under them.
- Ranks come out the same no matter when or how often the job runs.
- A failed fetch never changes a rank, and a failed run never replaces a good board.
- Every row shows its status, its per-source numbers, the category rule, compatibility, hashtags, and any star-check note.
- The bot discovers candidates without approval, starting from a stated seed list.
- Zero cost: GitHub Actions, GitHub Pages, and free public APIs. A free personal token as a secret is acceptable.
- A themed visual design on real table markup, with evidence still reachable on phones.

**Out-of-scope non-goals:**

- Other AI tools and ecosystems: Cursor, Windsurf, models, agent frameworks.
- Paid APIs, X/Twitter, and Reddit scraping.
- Sentiment analysis.
- Rankings inside a hashtag, or across categories.
- User accounts, voting, or comments.

## Alternatives Weighed

- **Five broad categories** (models, agent frameworks, AI coding tools, and others): rejected by the author. Closed tools could never meet the two-source rule, and the scope was too large. Narrowed to Claude Code and Codex add-ons.
- **Human approval for every new entry:** rejected by the author, who wants the project hands-off. The issue form is the only human step, and only for reports.
- **Ranking each plugin inside a shared repo:** rejected. They would all share one repo's stars, so their order would be meaningless. The repo or collection is the unit.
- **Marketplace listing count as a second source:** rejected. Anyone can create marketplaces for free. Public adoption in config files is proposed instead.
- **Reading README text for compatibility:** rejected. It is fuzzy text matching, and it would mark working MCP servers "–". Declared metadata is used instead.
- **A separate compatibility grid beside the rankings:** replaced by columns in the main table plus a filter. A separate grid repeats every row and doesn't fit phones. It is kept as an optional view.
- **Pre-filled pull request for reports:** GitHub links can't create one for an existing file. An issue form is used instead.
- **Bought-star check that demotes items:** rejected by the author. Shown as a side note only.
- **Bought-star check only on gain jumps:** extended to also run when an item is first seen, because new items have no previous week to "jump" from.
- **Fuzzy name matching between sources:** rejected because it causes false matches and lets spam claim popular names. Only links the project declares count.
- **Broad GitHub search as the main discovery path:** rejected because it returns mostly junk and uses up quota. It is kept only as a capped weekly sweep for new marketplaces.

## Key Decisions & Staging for Next Steps

**Decided by the author:**

1. **Audience:** technical AI enthusiasts.
2. **Scope:** Claude Code and Codex add-ons. Launch with MCP servers and plugins.
3. **Hands-off:** no approval step, except owner-handled reader reports.
4. **Zero cost:** Actions, Pages, and stdlib Python.
5. **Bought-star check:** kept, shown as a side note only.
6. **Compatibility:** shown for both tools, ✓ / – / ✗.
7. **Reader reports:** yes.
8. **Visual design:** distinctive themed design.

**Decided after round 2 (these replace any conflicting detail in sections C–H):**

9. **Unit of ranking = the repo.**
   - One row per repo.
   - A repo with several add-ons gets a "collection" badge and an expandable list of its contents.
   - Collections stay on the same board, with no separate lane.
10. **Works-with label:** one badge per row, `Claude Code`, `Codex`, or `Both`. It replaces the two ✓ columns.
    - Labels are set from the folders the project ships: `.claude-plugin/` means Claude Code, `.codex-plugin/` means Codex, both means Both.
    - MCP servers are labelled `Both`.
    - A wrong label is fixed with one line in `overrides.txt`.
    - Codex-only add-ons are in scope and are found by the same weekly sweep, which also searches for `.codex-plugin/plugin.json`.
11. **Second source for plugins:** public adoption, counted as distinct repo owners whose committed config enables the item.
    - It is built **last**.
    - Until then, plugins rank on GitHub alone, with a visible "1 source" label.
    - The marketplace-count signal is dropped completely.
12. **Hashtags:** filter only, never ranked.
    - The first vocabulary is 10 tags: `#browser #database #git #docs #testing #design #security #devops #data #memory`.
13. **Bought-star note:** checked when an item is first seen, then every 4 weeks.
    - The "gain jump" trigger is dropped.
    - The note is shown beside the item with the category median.
14. **Cut for now:**
    - a separate collection lane
    - the two ✓ compatibility columns
    - the marketplace-count signal
    - the gain-jump trigger
    - retiring items after 8 weeks

**Verified on 2026-11-25 with GitHub code search, using a personal token; counts are approximate:**

- about 29,000 public `settings.json` files contain `enabledPlugins`
- about 12,900 public `config.toml` files contain `[mcp_servers`
- about 7,900 repos ship `.codex-plugin/plugin.json`, for example `google/elephant-goldfish-model`

So `.codex-plugin/` is a real convention, and adoption data exists for both tools.

**Still to verify:**

- whether the Actions `GITHUB_TOKEN` can run code search, or a free personal token secret is needed
- whether bot commits count as activity for GitHub's 60-day cron auto-disable

**Build order (each phase ships on its own):**

1. **Reliability.** On the existing MCP board:
   - `state.json`
   - carry-forward for failed fetches
   - publish gate
   - 7-day comparisons
   - `overrides.txt`
   - decisions log
   - workflow fixes
2. **Discovery and plugins:**
   - MCP Registry
   - marketplace seed list
   - `.codex-plugin` sweep
   - collection rows
   - works-with labels
   - shadow mode
3. **The page:**
   - themed design
   - hashtags
   - report issue form
   - source labels on each row
4. **Signals:** public adoption counting, then the bought-star note.

**Engineering foundation:**

- an `owner/repo[/subpath]` ID
- a `state.json` separate from `latest.json`
- carry-forward for failed fetches, with a publish gate
- dated 7-day comparisons
- a decisions log with a run summary
- `schema_version` and `score_version` fields
- `overrides.txt` with a strict parser
- shadow mode for 4 weeks
- workflow fixes: concurrency group, rebase before push, keepalive
