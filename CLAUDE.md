# Claude Project Guide — TOKEN DASHBOARD

## Project

TOKEN DASHBOARD is a local-first analytics dashboard for Claude Code token usage.
Reads JSONL transcripts from `~/.claude/projects/`, turns them into cost analytics,
tool/file heatmaps, session drill-downs, and a rule-based tips engine.

**Stack:** Python 3 stdlib (no pip) + SQLite + Vanilla JS/ECharts (port **8191**)
**Run:** `./run.sh` from this directory
**Upstream:** `git remote upstream` → `nateherkai/token-dashboard` (MIT)

## Key files

| Path | Purpose |
|---|---|
| `cli.py` | CLI entrypoint — scan, stats, today, tips, dashboard |
| `token_dashboard/scanner.py` | JSONL parser → SQLite |
| `token_dashboard/server.py` | HTTP server: JSON API + SSE + static UI |
| `token_dashboard/db.py` | All SQLite queries |
| `token_dashboard/tips.py` | Rule-based token-saving suggestions |
| `token_dashboard/pricing.py` | Cost calculation from pricing.json |
| `web/style.css` | Custom UPPERCASE + token-gold theme (our fork) |
| `web/app.js` | Router, state, fetch helpers |
| `web/charts.js` | ECharts wrappers (token-gold palette) |
| `web/routes/*.js` | Per-tab UI routes (7 tabs) |
| `pricing.json` | Model pricing rates — edit directly |

## Conventions

- **Stdlib only.** No `pip install`. Zero external dependencies.
- **Read-only on session data.** Only writes to its own SQLite cache `~/.claude/token-dashboard.db`.
- **UPPERCASE UI.** All user-facing text uses uppercase letter-spacing styling.
- **Token-gold palette.** Primary accent `#E8B038`, charts use amber/gold lead color.
- **Upstream tracking.** `git fetch upstream` to check for new features. Cherry-pick selectively.

## Gotchas

- Only tracks Claude Code sessions — not Antigravity (Gemini). Phase 2 roadmap item.
- Cowork (server-side) sessions don't write local JSONL — invisible to scanner.
- Dedupes streaming snapshots by `message.id` — numbers match API billing.
- Single instance only — two dashboards fight over SQLite.

## Subagents
Use `haiku` (`claude-haiku-4-5-20251001`) for exploration subagents — file searches, codebase scans, grep tasks. Use Sonnet for subagents that write code, debug, or reason.
