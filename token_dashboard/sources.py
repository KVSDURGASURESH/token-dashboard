"""Which agents' session logs get scanned.

Claude Code (~/.claude/projects) is always a source. Others come from, in
order: a JSON config file, then repeatable ``--source name=kind:path`` flags.
Kinds: ``claude``, ``codex``, ``hermes``, ``generic`` (see scanner.KINDS).
A config entry may add ``"model_alias": {"ojas-qwen": "qwen3.5"}`` (hermes) to rename gateway aliases.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Optional

from .scanner import KINDS

CODEX_DEFAULT = "~/.codex/sessions"


def default_config_path() -> Path:
    return Path(os.environ.get("TOKEN_DASHBOARD_SOURCES") or Path.home() / ".claude" / "token-dashboard-sources.json")


def parse_source_arg(spec: str) -> dict:
    """``name=kind:path`` (or ``name=path`` when name is itself a kind)."""
    name, sep, rest = spec.partition("=")
    if not sep or not name or not rest:
        raise ValueError(f"bad --source {spec!r}; expected name=kind:path, e.g. codex=codex:~/.codex/sessions")
    kind, sep, path = rest.partition(":")
    # "kind:path" vs a bare path (which may itself contain ':' on Windows)
    if not sep or kind not in KINDS:
        kind, path = (name, rest)
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r} in --source {spec!r}; expected one of {sorted(KINDS)}")
    return {"name": name, "kind": kind, "path": path}


def load_config(path: Optional[Path] = None) -> List[dict]:
    path = Path(path) if path else default_config_path()
    if not path.is_file():
        return []
    out = []
    for e in json.loads(path.read_text(encoding="utf-8")):
        if e.get("kind") not in KINDS or not e.get("name") or not e.get("path"):
            raise ValueError(f"{path}: each entry needs name, kind ({sorted(KINDS)}), path; got {e!r}")
        out.append({"name": e["name"], "kind": e["kind"], "path": e["path"],
                    **({"options": {"model_alias": e["model_alias"]}} if e.get("model_alias") else {})})
    return out


def resolve_sources(claude_dir: str, use_config: bool = True, extra: Optional[List[str]] = None,
                    config_path: Optional[Path] = None) -> List[dict]:
    """Claude Code first, then config-file sources, then --source flags.

    A later entry with the same name replaces an earlier one. Callers pass
    use_config=False when the user pinned --projects-dir, so an explicit
    directory means exactly that directory.
    """
    by_name = {"claude": {"name": "claude", "kind": "claude", "path": claude_dir}}
    if use_config:
        for s in load_config(config_path):
            by_name[s["name"]] = s
    for spec in extra or []:
        s = parse_source_arg(spec)
        by_name[s["name"]] = s
    return list(by_name.values())
