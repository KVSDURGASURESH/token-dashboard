# Inspiration: code-simplifier agent (anthropics/claude-plugins-official)

Source: https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md

## What it is

An official Claude Code plugin subagent definition (`model: opus`) whose job
is to simplify recently-modified code for clarity and consistency while
preserving exact functionality.

## Best practices it documents

- **Behavior preservation is non-negotiable**: never change what code does,
  only how it does it.
- **Clarity over brevity**: explicit code beats dense/clever code. No nested
  ternaries — prefer `if`/`elif` or early returns.
- **Don't over-simplify**: avoid collapsing distinct concerns into one
  function, removing helpful abstractions, or optimizing for fewer lines at
  the expense of readability or debuggability.
- **Respect project conventions**: apply the target project's own
  CLAUDE.md/style conventions rather than generic opinions.
- **Scope discipline**: by default, only touch code that was actually
  recently modified — don't wander into unrelated files.

## How we used it

Ran the `code-simplifier:code-simplifier` subagent over this codebase after
landing the Builder Profile feature (see
`docs/superpowers/specs/2026-08-19-builder-profile-design.md`), scoped to the
whole project rather than just the new diff, per an explicit one-off request.
