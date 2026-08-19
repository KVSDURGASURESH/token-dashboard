# TOKEN DASHBOARD — Implementation Log
> Chronological record of all major changes, decisions, and roadmap.

---

## 2026-04-28 — v1.0: Initial Setup (PHASE 1)

### What was done
- **Cloned upstream** `nateherkai/token-dashboard` (MIT) as baseline
- **Renamed remote** `origin` → `upstream` for tracking upstream changes
- **Custom theme applied:**
  - UPPERCASE signature styling on ALL user-facing text (headings, labels, descriptions, buttons, badges)
  - Token-gold accent palette (`#E8B038` primary, amber/gold spectrum)
  - Glassmorphism cards with subtle glow borders and top-edge gradient reveal on hover
  - Dot-grid background pattern (gold-tinted)
  - Custom scrollbar and selection colors
  - Premium dark mode (`#06080C` base)
  - Token-pulse animation on brand diamond icon
- **Chart theme updated:**
  - Gold-primary palette instead of upstream blue
  - Consistent dark theme colors across all chart types
  - Tooltip and legend colors matched to new theme
- **App.js customized:**
  - Brand text: "TOKEN DASHBOARD" (uppercase)
  - Nav links: uppercase with letter-spacing
  - First-run modal: uppercase text
  - Plan pill: uppercase
- **All 7 route files touched:**
  - Overview: all headings, descriptions, chart titles, empty states → UPPERCASE
  - Settings: plan, pricing, privacy headings → UPPERCASE
  - (Prompts, Sessions, Projects, Skills, Tips inherit from CSS `text-transform` on card h2/h3)
- **Port set to 8191** — avoids conflicts with all existing services
- **Project docs created:**
  - `CLAUDE.md` — lean AI context file
  - `README.md` — full project documentation
  - `IMPLEMENTATION_LOG.md` — this file
  - `run.sh` — launcher matching workspace conventions

### Architecture decisions
- **Fork approach (not symlink):** Clone + rename remote to `upstream`. This gives full ownership of the codebase while preserving ability to `git fetch upstream` and cherry-pick selectively. A symlink approach was considered but rejected — it doesn't allow UI customization and creates fragile path dependencies.
- **Python backend untouched:** The scanner, DB, server, tips engine, and pricing modules are used as-is from upstream. All customization is in the frontend layer (`web/`). This makes upstream merges trivial — Python changes can be cherry-picked cleanly.
- **Stdlib-only rule preserved:** No pip dependencies added. Consistent with upstream philosophy and workspace conventions.

### What NOT to do
- ❌ Do NOT run two dashboard instances simultaneously — SQLite locking
- ❌ Do NOT modify JSONL files in `~/.claude/projects/` — read-only
- ❌ Do NOT delete `~/.claude/token-dashboard.db` while dashboard is running

---

## ROADMAP

### Phase 2 — Antigravity (Gemini) Integration
- [ ] Add scanner for Antigravity conversation logs (`~/.gemini/antigravity/brain/`)
- [ ] Unified token tracking across Claude Code + Antigravity
- [ ] Model pricing for Gemini models in `pricing.json`
- [ ] Combined "AI spend" view in Overview tab
- **Status:** Planned. Antigravity logs at `~/.gemini/antigravity/brain/<conversation-id>/.system_generated/logs/`

### Phase 3 — ALBATROSS Integration
- [ ] Register TOKEN-DASHBOARD in `ALBATROSS/albatross.yaml` port registry
- [ ] Add to `launch.sh` service list
- [ ] SSE bridge to ALBATROSS dashboard for unified monitoring
- **Status:** Planned.

### Phase 4 — Advanced Analytics
- [ ] Token budget alerts (daily/weekly caps)
- [ ] Historical trend analysis (week-over-week)
- [ ] Per-project cost allocation
- [ ] Export reports (CSV/JSON)
- [ ] Auto-tips based on ML pattern detection
- **Status:** Backlog.

---
