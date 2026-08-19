# Inspiration: Paxel (paxel.ycombinator.com)

Source: https://paxel.ycombinator.com

## What it does

A Y Combinator experiment that reads local AI-coding-tool session transcripts
(Claude Code, Codex, Cursor, opencode, Gemini CLI, Copilot, Antigravity) and
produces a "Builder Profile": an archetype label plus scores across five
dimensions (steering, execution, engineering, product instinct, planning),
delivered by email.

## How it works

- Sign in with a YC account, then run `curl -fsSL https://paxel.ycombinator.com/upload.sh | bash`
- Analysis runs locally inside a Docker container (`ghcr.io/yc-software/paxel-client`)
- Transcript excerpts are sent to Claude/GPT (via `paxel-llm.ycombinator.com`) for
  summarization; scored results, session metadata (file paths, bash commands),
  and git line-count stats are uploaded to YC
- Results arrive by email 15-30 minutes later
- Working tree contents and `.env` files stay local; only redacted/scored
  summaries leave the machine

## Why this is not a duplicate of TOKEN DASHBOARD

Paxel does not track token usage, cost, or cache-hit rates, and has no local
dashboard — it's a remote behavioral-analytics service that requires Docker,
a YC account, and off-device uploads. TOKEN DASHBOARD is a 100%-local,
zero-upload token/cost dashboard. Different purpose, different privacy model.

## What we borrowed (not copied)

The idea of a session-derived "builder archetype" — but reimplemented as
`token_dashboard/profile.py`'s **Builder Profile** feature: fully local,
zero-upload, rule-based scoring over data already in this project's SQLite
cache. No Docker, no remote LLM calls, no account, no email. See
`docs/superpowers/specs/2026-08-19-builder-profile-design.md` for the design.
