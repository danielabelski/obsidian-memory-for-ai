# Automating Memory Maintenance

> **Status:** Optional v3.1 integration guide. The required protocol remains the Markdown/YAML contract in [`SPEC-v3.md`](SPEC-v3.md) plus the portable tools in [`examples/v3-minimal-vault/`](examples/v3-minimal-vault/).

Automation should make the v3 workflow easier; it should not create a second source of truth. A script or agent may propose facts, events, reviews, and archives, but canonical changes should still pass through validation and view rebuilds.

## Recommended v3 automation boundary

| Task | Safe automation pattern |
|---|---|
| Add a durable fact | Create an operation envelope with `tools/ops.py create-fact`, then run `tools/compact.sh` |
| Record a session | Use `tools/reflect.py` to propose an event, then compact |
| Audit stale facts | Read `_views/stale.md` or run `tools/lint.py`; propose review operations |
| Rebuild read models | Run `tools/rebuild-views.sh` |
| Check consistency | Run `tools/lint.py` and regression tests |

Avoid direct writes to canonical `memory/facts/` from unattended agents unless the agent is trusted, local, and immediately runs validation.

## Minimal post-session workflow

From a v3 vault root:

```bash
tools/reflect.py \
  --agent agent-local-1234abcd \
  --summary "Reviewed Concordance status and agreed to backfill current collaborator facts."

tools/compact.sh
.venv/bin/python tools/lint.py
tools/rebuild-views.sh
```

This records the session as a proposed operation, applies it through the compactor, validates source truth, and refreshes generated views.

## Building a standalone maintenance agent

A maintenance agent should operate in three phases:

1. **Read:** load `CLAUDE.md` or `AGENTS.md`, `memory/schema/version.yaml`, `memory/schema/predicates.yaml`, relevant `_views/`, and any referenced source files.
2. **Propose:** write operation envelopes under `memory/_inbox/{agent-id}/ops/` rather than mutating canonical files directly.
3. **Validate:** run `tools/compact.sh`, `tools/lint.py`, and `tools/rebuild-views.sh`; leave unresolved conflicts visible in `_views/conflicts.md`.

The prompt for such an agent can be short:

```text
You maintain a v3.1 Obsidian Memory vault.

Rules:
- Human prose lives in memory/people, memory/projects, memory/context, memory/decisions, and memory/insights.
- Canonical agent facts live in memory/facts/{entity}/{predicate}.md.
- Session records are append-only events under memory/events/YYYY-MM-DD/.
- Prefer tools/ops.py and tools/reflect.py for proposed writes.
- Apply proposed writes only through tools/compact.sh.
- Run tools/lint.py and tools/rebuild-views.sh before reporting success.
- Do not edit memory/_views directly.
- Do not bulk-refresh last_reviewed; it means semantic validation.
```

## Scheduled maintenance

A local cron or launchd job can run read-only checks:

```bash
cd ~/path/to/vault
.venv/bin/python tools/lint.py
MEMORY_TODAY="$(date +%F)" tools/rebuild-views.sh
git diff -- memory/_views
```

Use this as an alerting loop, not as an unattended mutator. If generated views change, review the diff and decide whether to commit it.

## Human review checkpoints

Require human review before applying operations that:

- lower confidence or archive a fact
- resolve contradictions
- introduce new predicates
- alter `memory/schema/`
- change `CLAUDE.md`, `AGENTS.md`, or other procedural instructions
- touch private/person-sensitive narrative pages

## Legacy note

Older automation examples for v2 used `memory/ContextSummary.md`, `memory/recent-sessions.md`, `memory/log.md`, and broad updates to prose pages. Those remain valid for legacy compiled-wiki vaults, but they are not the recommended v3 workflow. For v3, use facts, events, generated views, and operation envelopes.
