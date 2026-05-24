# Example: v3 Minimal Vault — Current Reference

This example implements **SPEC v3.1 — Agentic Atomic Markdown Memory** as a small, portable vault. It keeps the v2 idea of human-readable Markdown, but separates human prose from agent-facing records and gives cooperative agents a safe proposal/apply workflow:

- `memory/facts/` — atomic semantic facts, one tuple per file.
- `memory/events/` — append-only episodic records.
- `memory/_views/` — generated materialized views committed for auditability in this example.
- `memory/_inbox/` — cooperative agent operation staging area.
- `memory/_claims/` — advisory claim files for cooperative agents.
- `memory/_ops/` — applied operation receipts.
- `tools/` — portable validation, query, reflection, and compaction scripts that travel with the vault.

The original `examples/minimal-vault/` remains the legacy v2 reference. This directory is the current v3.1 reference and should be the starting point for new vaults.

## Quick start

Recommended local setup for bash/zsh:

```bash
cd examples/v3-minimal-vault
chmod +x tools/*.sh tools/pre-commit
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./tools/rebuild-views.sh
.venv/bin/python tools/lint.py
./tools/query.sh facts --entity elena-voss
./tools/query.sh id fact-elena-voss-role
./tools/query.sh events --since 2026-03-01
```

For fish, use an explicit `./` prefix or activate fish's venv script:

```fish
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python tools/lint.py
# or:
source .venv/bin/activate.fish
```

The scripts require Python 3.11+ and PyYAML. The shell wrappers prefer `.venv/bin/python` when it exists, then fall back to `python3`.

For a one-shot setup, run `bash setup.sh`. After executable bits are restored, `./setup.sh` also works.

## Rules implemented here

### Version marker

`memory/schema/version.yaml` declares the frozen on-disk schema baseline:

```yaml
spec_version: "3.0"
schema_status: stable
```

`tools/lint.py` fails if the marker is missing or incompatible. v3.1 is additive over this stable v3.0 schema baseline, so the marker remains `3.0` while operation envelopes, claims, IDs, and receipts define the current agentic protocol.

### Facts and filenames

The canonical active fact path is:

```text
memory/facts/{entity}/{predicate}.md
```

Historical or superseded facts may use a suffix:

```text
memory/facts/{entity}/{predicate}--{slug}.md
```

The frontmatter `entity` and `predicate` are authoritative, but the path must match them. A suffix is allowed only after `--`. Predicates are controlled by `memory/schema/predicates.yaml`.

Facts may also carry stable `id:` values. v3.1 tools use those IDs for operation envelopes and applied receipts so paths can stay readable without being the only durable identity.

Canonical fact frontmatter includes the required fields first, then confidence and local sources:

```yaml
---
type: fact
entity: elena-voss
predicate: base
value: "Berlin, Germany"
recorded_at: 2026-05-10T22:14:00Z
confidence: high
sources: []
valid_from: null
valid_to: null
---
```

### Temporal semantics

- `valid_from` and `valid_to` are inclusive dates.
- `valid_to: null` means open-ended.
- `valid_from: null` means unknown start.
- `recorded_at` is required and means when the fact was written down; it is not replaced by `valid_from`.
- Overlapping facts for the same `(entity, predicate)` with different values are contradictions unless one points at the other via `superseded_by`.

### Entity policy

Every referenced entity must appear in `memory/entities.md`. This is strict because typos in entity IDs silently split memory.

### Common mistakes lint will catch

A short field guide to first-contact errors and how to fix them:

- **`source does not exist: https://...`** — `sources:` entries are local filesystem paths relative to the vault root, not URLs. To cite an external URL, put it in the note body or save a local source file under `sources/articles/` and cite that path.
- **`missing required field 'recorded_at'`** — every `fact` needs an ISO-8601 timestamp for when the fact was recorded. `valid_from` is separate and optional.

  ```yaml
  type: fact
  entity: elena-voss
  predicate: role
  value: "Art conservator"
  recorded_at: 2026-05-13T18:51:00Z
  valid_from: 2026-05-13
  valid_to: null
  confidence: high
  sources: []
  ```

- **`unknown predicate 'X'`** — predicates are controlled by `memory/schema/predicates.yaml`. Declare the predicate before writing facts or operation payloads that use it.

  ```yaml
  predicates:
    - id: spec-version
      description: Declared spec version of a memory vault or schema.
  ```

- **`source:` vs `sources:`** — the schema field is the plural array `sources: []`, not the singular `source:`.

### Narrative note schemas

The example also includes lightweight schemas for optional human-facing narrative notes:

- `memory/schema/person.schema.yaml` for `memory/people/`
- `memory/schema/project.schema.yaml` for `memory/projects/`
- `memory/schema/context.schema.yaml` for `memory/context/`

These keep prose pages lintable when you add typed frontmatter, while preserving the v3 split: structured facts remain in `memory/facts/`, and narrative pages remain optimized for humans.

### Generated views

Generated files under `memory/_views/` are committed in this example so diffs show derived-state changes. In a private vault, you may ignore `_views/` and regenerate them locally.

For deterministic stale calculations, scripts use `MEMORY_TODAY` when set:

```bash
MEMORY_TODAY=2026-05-11 tools/rebuild-views.sh
```

### Wikilink subset

The linter supports these wikilink forms:

- `[[memory/facts/elena-voss/timezone]]`
- `[[memory/projects/concordance|Concordance]]`
- `[[concordance]]` when the basename is unique
- `[[memory/projects/concordance#Current status]]`

Ambiguous basenames are reported as errors.

## v3.1 agentic operation flow

Agents should avoid writing canonical memory directly. Instead, create operation envelopes in `_inbox/`:

```bash
tools/ops.py create-fact \
  --agent agent-copilot-1234abcd \
  --entity elena-voss \
  --predicate language \
  --value Spanish \
  --source sources/README.md \
  --reason "Capture a durable language preference."
```

Then review and apply:

```bash
tools/compact.sh
```

The compactor validates the operation, checks `precondition_hash` when present, applies the change, rebuilds views, and stores an applied receipt under `memory/_ops/applied/`.

For cooperative work, agents may create advisory claims:

```bash
tools/ops.py claim \
  --agent agent-copilot-1234abcd \
  --target-id fact-elena-voss-language \
  --operation-id op-20260512t180000z-1234abcd
```

Claims are not database locks. They are local coordination files with TTLs, useful for avoiding obvious collisions and for diagnosing conflicts.

## Anthropic Memory Tool mapping

The v3 `memory/` folder maps cleanly to Anthropic's `/memories` directory:

| v3 path | Memory Tool meaning |
|---------|---------------------|
| `memory/facts/` | Canonical semantic memories |
| `memory/events/` | Append-only episodic memories |
| `memory/decisions/` | Durable decisions with rationale |
| `memory/insights/` | Reflections and learned patterns |
| `memory/_views/` | Generated read models; do not edit as source |
| `memory/_inbox/` | Proposed writes from agents; compact before treating as canonical |
| `memory/_claims/` | Advisory cooperative claims, not locks |
| `memory/_ops/` | Applied operation receipts |
| `memory/_archive/` | Expired historical facts |

If a tool points directly at `memory/`, configure it to treat `_views/`, `_inbox/`, and `_archive/` as special-purpose folders rather than primary sources.

## Reflection ritual

`tools/reflect.py` is intentionally conservative. It does not call an LLM and does not merge into canonical memory. It accepts a short session summary and writes a proposed `add_event` operation into `memory/_inbox/{agent-id}/ops/`:

```bash
tools/reflect.py --agent copilot --summary "Reviewed SPEC v3 and agreed to controlled predicates."
tools/compact.sh
```

Run `tools/compact.sh` to review inbox entries and move safe records into canonical memory.
