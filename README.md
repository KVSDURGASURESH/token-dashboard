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

## Tracking other agents (Codex, anything else)

Claude Code is always scanned. Add more agents and they land in the same DB, tagged by `source`;
the top bar gets an agent picker and Overview gets a BY AGENT table.

```
./run.sh --codex                                    # shorthand for the line below
python3 cli.py dashboard --source codex=codex:~/.codex/sessions
python3 cli.py scan --source mybot=generic:~/logs/mybot.jsonl
```

Or make it permanent in `~/.claude/token-dashboard-sources.json` (honoured unless `--projects-dir` is pinned):

```json
[{"name": "codex", "kind": "codex", "path": "~/.codex/sessions"}]
```

Hermes (SQLite at `~/.hermes/state.db` plus one per profile) is a kind too, with an optional alias for gateway model names:

```json
{"name": "hermes", "kind": "hermes", "path": "~/.hermes", "model_alias": {"ojas-qwen": "qwen3.5"}}
```

Hermes records per-session token totals only, so each session's totals are split evenly over its assistant turns:
session and agent totals are exact, per-turn and per-day figures are an approximation. Databases are opened read-only.
`pricing.json` prices `qwen3.5` at $0 (local model); change it if yours isn't local.

Every skill, tool, model, project, session, prompt and tip carries an agent badge (colour per agent, with that agent's
count), tool and skill charts are stacked by agent, and Profile scores each agent separately.

Kinds: `claude`, `codex` (OpenAI Codex CLI/desktop rollouts), `hermes`, `generic` (one JSON object per API call:
`session_id`, `timestamp`, `model`, `input_tokens` (uncached), `output_tokens`, optional
`cache_read_tokens`, `cwd`, `prompt`, `tools`). Any agent that can write that line is trackable;
a new native format is one parser in `scanner.py` plus an entry in `KINDS`.

Costs: models missing from `pricing.json` (all non-Claude models, until you add rates) show as `—`, not `$0`.
Add `"gpt-x": {"input": .., "output": .., "cache_read": ..}` under `models` to price them.
Codex subagents are grouped under their parent session and flagged as sidechains.

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

## The 8 tabs

- **Overview** — all-time input/output/cache tokens, sessions, turns, estimated cost on your chosen plan, daily work and cache-read charts, tokens-by-project, token share by model, top tools by call count, and recent sessions. This is the landing tab.
- **Prompts** — your most expensive user prompts ranked by tokens. Click any row to see the assistant response, tool calls made, and the size of each tool result.
- **Sessions** — turn-by-turn view of any single session, with per-turn tokens and tool calls.
- **Projects** — per-project comparison: tokens, session counts, and which files were touched most.
- **Profile** — four rule-based 0-100 scores (Steering, Execution, Engineering, Planning) plus an archetype label, computed from your own local session history — not a comparison to other users, since there's no population to compare against locally.
- **Skills** — which skills you invoke most often, and (where we can measure them) their token cost. See [limitations](docs/KNOWN_LIMITATIONS.md#skills-token-counts-are-partial).
- **Tips** — rule-based suggestions for reducing token usage (repeated file reads, oversized tool results, low cache-hit rate, etc.).
- **Settings** — switch pricing between API / Pro / Max / Max-20x so cost figures everywhere else reflect your actual plan.

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
