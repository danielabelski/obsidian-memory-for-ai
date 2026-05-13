# Repository instructions for Copilot

## Commands

The repository is documentation-first; validation is centered on the v3 example vault.

```bash
# Install the only runtime dependency used by the example tools
python3 -m pip install PyYAML

# Validate the v3 reference vault
cd examples/v3-minimal-vault
python3 tools/lint.py

# Rebuild generated v3 views
tools/rebuild-views.sh

# Match the GitHub Actions check for deterministic generated views
MEMORY_TODAY=2026-05-11 tools/rebuild-views.sh
git diff --exit-code -- memory/_views

# Query one slice of memory data
tools/query.sh facts --entity elena-voss
tools/query.sh facts --entity elena-voss --predicate role
tools/query.sh events --since 2026-03-01
```

The CI workflow in `.github/workflows/v3-memory.yml` runs Python 3.11, installs `PyYAML`, lints `examples/v3-minimal-vault`, rebuilds `_views`, and fails if generated view files differ.

## Architecture

This repo documents and demonstrates an Obsidian-backed AI memory system. The root Markdown files are guides/specs, not an application runtime. `README.md` is the entry point, `guide.md` documents the v2 "compiled wiki" pattern, and `SPEC-v3.md` defines the v3 "Atomic Markdown Memory" design.

There are two example vaults:

- `examples/minimal-vault/` is the v2 reference: human-readable `memory/` wiki pages, `TASKS.md`, and a `CLAUDE.md` orientation file.
- `examples/v3-minimal-vault/` is the current v3 reference: typed atomic facts, append-only events, schemas, generated views, and portable Python/Bash tooling.

The v3 vault separates audiences:

- Human prose lives in `memory/people/`, `memory/projects/`, and `memory/context/`.
- Agent-readable semantic records live in `memory/facts/`, one tuple per file.
- Episodic records live in `memory/events/YYYY-MM-DD/` and are append-only.
- Generated read models live in `memory/_views/`; they are derived from source files and should be regenerated, not edited by hand.
- Multi-agent proposed writes go through `memory/_inbox/{agent-id}/` and are merged by `tools/compact.sh`.

## Key conventions

- For v3 facts, the canonical path is `memory/facts/{entity}/{predicate}.md`. The frontmatter `entity` and `predicate` are authoritative, but the path must match; historical variants may use `predicate--suffix.md`.
- Every v3 `entity` must be declared in `memory/entities.md`; every fact `predicate` must be declared in `memory/schema/predicates.yaml`.
- v3 schemas live in `memory/schema/*.schema.yaml`; `tools/lint.py` validates typed frontmatter, date semantics, entity/predicate references, source paths, wikilinks, and overlapping contradictory facts.
- `valid_from`/`valid_to` represent when a fact is true in the world; `recorded_at` is when it was written down. `last_reviewed` is a semantic validation date, not a mechanical audit timestamp.
- Use `MEMORY_TODAY` when commands need deterministic date-dependent output, especially stale-fact views and CI-equivalent rebuilds.
- Supported wikilink forms include full paths, aliases, unique basenames, and headings, e.g. `[[memory/projects/concordance|Concordance]]`; ambiguous basenames are lint errors.
- Treat files under `sources/` as immutable raw inputs in example vaults. Agents may read them as provenance, but should not rewrite them during memory updates.
- The `CLAUDE.md` files inside example vaults describe fictional example users and vault behavior. Incorporate their protocol conventions when editing examples, but do not treat their personal profile content as repository maintainer instructions.
