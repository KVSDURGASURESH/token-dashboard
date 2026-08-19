#!/usr/bin/env bash
# TOKEN-DASHBOARD — unified launcher
# Port : 8191  (HTTP + SSE server)
# Usage: ./run.sh [--no-browser]
#
# Scans ~/.claude/projects/ and serves the token analytics UI.
# Python stdlib only — no pip, no node, no build step.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8191

B="\033[1m"; R="\033[0m"; GR="\033[32m"; YL="\033[33m"; CY="\033[36m"; DM="\033[2m"; RD="\033[31m"; GL="\033[38;5;220m"
ok()   { echo -e "  ${GR}✓${R}  $*"; }
info() { echo -e "  ${CY}→${R}  $*"; }
warn() { echo -e "  ${YL}⚠${R}  $*"; }
err()  { echo -e "  ${RD}✗${R}  $*"; }
dim()  { echo -e "  ${DM}$*${R}"; }

echo ""
echo -e "${B}${GL}  ◆  TOKEN DASHBOARD${R}  ${DM}→  http://localhost:${PORT}${R}"
echo ""

# Parse flags
NO_BROWSER=0
for arg in "$@"; do
    [[ "$arg" == "--no-browser" ]] && NO_BROWSER=1
done

# ── Clear port (loop until OS confirms it's free) ─────────────────────────────
clear_port() {
    local port="$1" i=0
    while true; do
        local pids
        pids=$(lsof -ti :"$port" 2>/dev/null || true)
        [[ -z "$pids" ]] && break
        echo "$pids" | xargs kill -9 2>/dev/null || true
        i=$((i+1))
        if [[ $i -ge 20 ]]; then
            warn "Port $port still in use after ${i} attempts — proceeding anyway"
            break
        fi
        sleep 0.3
    done
}
if lsof -ti :"$PORT" &>/dev/null; then
    dim "clearing port $PORT…"
    clear_port "$PORT"
    dim "port $PORT free"
fi

# ── Start dashboard ───────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"
info "Scanning sessions & starting server…"
PORT=$PORT python3 cli.py dashboard --no-open &
GW_PID=$!
dim "PID=$GW_PID"

# ── Wait for ready ─────────────────────────────────────────────────────────────
for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${PORT}/api/plan" -o /dev/null 2>/dev/null; then
        ok "Dashboard is up"
        break
    fi
    sleep 0.5
    if [[ $i -eq 30 ]]; then
        err "Dashboard did not respond after 15s — check logs"
        kill "$GW_PID" 2>/dev/null
        exit 1
    fi
done

# ── Open browser ───────────────────────────────────────────────────────────────
if [[ $NO_BROWSER -eq 0 ]] && command -v open &>/dev/null; then
    open "http://localhost:${PORT}"
fi

echo ""
echo -e "${B}${GL}  ◆  http://localhost:${PORT}${R}   ·   Ctrl+C to stop"
echo ""

# ── Trap and wait ──────────────────────────────────────────────────────────────
cleanup() {
    echo ""
    kill "$GW_PID" 2>/dev/null
    dim "TOKEN DASHBOARD stopped"
    exit 0
}
trap cleanup INT TERM

wait "$GW_PID"
