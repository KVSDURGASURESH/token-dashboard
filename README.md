# TOKEN DASHBOARD

> Local analytics for Claude Code token usage — see where your tokens burn, spot wasteful patterns, and optimize your workflow.

## What

A local dashboard that reads the JSONL transcripts Claude Code writes to `~/.claude/projects/` and surfaces:

- **Per-prompt cost breakdowns** — find your most expensive prompts
- **Tool & file heatmaps** — which tools eat the most tokens
- **Session drill-downs** — turn-by-turn token accounting
- **Project comparisons** — FIRE vs JARVIS vs ORION usage
- **Cache analytics** — are you getting cache hits or paying full price?
- **Tips engine** — rule-based suggestions to reduce token burn
- **Cost estimates** — API / Pro / Max / Max-20x pricing modes

## Stack

| Layer | Tech |
|---|---|
| Backend | Python 3 stdlib (no pip install) |
| Database | SQLite (`~/.claude/token-dashboard.db`) |
| Frontend | Vanilla JS + ECharts (vendored), no build step |
| Theme | Custom UPPERCASE + token-gold palette |
| Server | `http.server.ThreadingHTTPServer` + SSE live refresh |

**Port:** `8191`

## Quick Start

```bash
./run.sh                    # scan + serve → http://localhost:8191
./run.sh --no-browser       # don't auto-open browser
```

### CLI Commands

```bash
python3 cli.py scan         # populate / refresh the DB
python3 cli.py today        # today's token totals (terminal)
python3 cli.py stats        # all-time totals (terminal)
python3 cli.py tips         # actionable suggestions (terminal)
python3 cli.py dashboard    # scan + serve the UI
```

## Architecture

```
cli.py → token_dashboard/scanner.py → SQLite DB
         token_dashboard/server.py  → /api/* JSON + SSE + web/
```

Data flow:
1. Scanner reads `~/.claude/projects/<slug>/<session>.jsonl`
2. Dedupes streaming snapshots by `message.id`
3. Stores in SQLite with incremental mtime+offset tracking
4. Server exposes JSON APIs, SSE for live updates
5. Frontend renders via hash-router + ECharts

## Upstream

This is a customized fork of [`nateherkai/token-dashboard`](https://github.com/nateherkai/token-dashboard) (MIT).

```bash
git fetch upstream                  # check for new features
git log upstream/main --oneline -5  # see what's new
git cherry-pick <commit>            # selectively pull in changes
```

## Customizations from Upstream

- **UPPERCASE signature styling** — all UI text, headings, labels
- **Token-gold theme** — amber/gold accent palette (`#E8B038`)
- **Glassmorphism cards** — subtle glow borders, premium dark mode
- **Dot-grid background** — subtle gold dot pattern
- **Chart palette** — gold-primary instead of blue
- **Port 8191** — avoids conflicts with FIRE (8187), ORION (8189), etc.

## Privacy

100% local. No telemetry. No remote calls. All assets vendored.
The browser fetches JSON from `127.0.0.1` only.

## License

[MIT](LICENSE) — inherited from upstream.
