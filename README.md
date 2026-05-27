> **Before you clone**
>
> What you see here is an artifact: the concrete shape my problem took. It almost certainly doesn't fit your personal scenario perfectly, and that's fine. The interesting part isn't the code, it's the pattern of how I thought about the problem — that's what transfers. Read it, steal the idea, write your own. If any of this was useful to you, after clicking on the star, drop by [impermanente.es](https://impermanente.es) — there are posts and photos you might like.
>
> Context: [Seguimos compartiendo el producto, no la idea](https://impermanente.es/2026/05/25/seguimos-compartiendo-el-producto-no.html)

---

# Obsidian Memory for AI

**Persistent AI memory in plain Markdown, designed for Obsidian and usable by any assistant that can read files.**

> **Current stable version: v3.1 — Agentic Atomic Markdown Memory.**
> The reference implementation lives in [`examples/v3-minimal-vault/`](examples/v3-minimal-vault/) and the compatibility contract lives in [`SPEC-v3.md`](SPEC-v3.md).

The project is intentionally boring infrastructure: no database, daemon, vector store, server, embeddings, or binary source of truth. A memory vault is a folder of Markdown and YAML files you can read, edit, diff, sync, copy, and move between tools.

## Start here

| If you want to... | Read |
|---|---|
| Understand the current protocol | [`SPEC-v3.md`](SPEC-v3.md) |
| Copy a working v3 vault | [`examples/v3-minimal-vault/`](examples/v3-minimal-vault/) |
| Migrate an older compiled-wiki vault | [`migration-v3.md`](migration-v3.md) |
| See the full documentation map | [`docs/README.md`](docs/README.md) |
| Understand the older v2 pattern | [`guide.md`](guide.md) |

## What v3.1 is

v3 keeps the original promise of this repository — owned, transparent, portable AI memory — but stops mixing human notes and agent facts in the same file.

The core split is:

| Layer | Path | Purpose |
|---|---|---|
| Human narrative | `memory/people/`, `memory/projects/`, `memory/context/`, `memory/decisions/`, `memory/insights/` | Notes you can read naturally in Obsidian |
| Agent facts | `memory/facts/{entity}/{predicate}.md` | One durable typed fact per file |
| Events | `memory/events/YYYY-MM-DD/{slug}.md` | Append-only episodic records |
| Schemas | `memory/schema/` | YAML schemas and controlled predicates |
| Generated views | `memory/_views/` | Derived read models; regenerate, do not hand-edit |
| Agent inbox | `memory/_inbox/{agent-id}/ops/` | Proposed writes from assistants |
| Operations | `memory/_ops/applied/` | Receipts for applied changes |
| Claims | `memory/_claims/` | Advisory cooperative claims, not locks |

The important design move is **one fact, one file**. The path is a readable primary key, frontmatter is the schema, `tools/lint.py` is the constraint engine, and generated `_views/` are the materialized read models.

## Quick start

```bash
cd examples/v3-minimal-vault
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./tools/rebuild-views.sh
.venv/bin/python tools/lint.py
./tools/query.sh facts --entity elena-voss
```

The example vault includes:

- atomic facts in `memory/facts/`
- append-only events in `memory/events/`
- controlled predicates in `memory/schema/predicates.yaml`
- generated views in `memory/_views/`
- operation envelopes, advisory claims, compaction, receipts, and reflection tooling
- repository regression coverage under `tests/`

## When to use this

Use this repository when you want:

- personal or project memory that survives across AI tools
- plain-text ownership and `git diff` auditability
- human-readable notes and agent-readable facts in the same vault
- a small portable toolkit that travels with the vault
- cooperative few-agent writes with human-reviewable proposals

Do **not** use it as a replacement for a database-backed enterprise memory system. If your problem needs large-scale graph traversal, ranked retrieval over tens of thousands of records, multi-user OLTP concurrency, or managed personalization for many end users, use SQLite/Kuzu, Mem0, Zep/Graphiti, Letta, Cloudflare Agent Memory, or a RAG platform.

## Repository layout

```text
.
├── README.md                         # Landing page and current orientation
├── docs/README.md                    # Documentation map
├── SPEC-v3.md                        # Stable v3.1 protocol contract
├── migration-v3.md                   # v2 -> v3 migration checklist
├── automation-guide.md               # Optional v3 automation patterns
├── plugin-guide.md                   # Optional host-agent plugin pattern
├── obsidian-cli.md                   # Optional Obsidian CLI maintenance recipes
├── photo-ingest-guide.md             # Optional photography ingest workflow
├── optional-ideas.md                 # Experimental ideas, not protocol
├── guide.md                          # Legacy v2 compiled-wiki guide
├── examples/
│   ├── v3-minimal-vault/             # Current reference implementation
│   └── minimal-vault/                # Legacy v2 reference
└── tests/                            # Regression tests for v3 tooling
```

## Version guide

| Version | Status | Meaning |
|---|---|---|
| v3.1 | Current stable | v3 protocol plus agentic operation envelopes, claims, receipts, IDs, generated operational views, and reflection tooling |
| v3.0 | Frozen schema baseline | Atomic facts, events, schemas, linting, views, inbox compaction |
| v2.1 / v2.0 | Legacy | Prose-first compiled wiki pattern, still useful for small single-agent vaults |

v3.1 is additive over the frozen v3.0 schema baseline. The example vault still declares `spec_version: "3.0"` in `memory/schema/version.yaml` because the on-disk schema remains compatible.

## Core commands

From `examples/v3-minimal-vault/`:

```bash
# Validate source truth
.venv/bin/python tools/lint.py

# Regenerate derived views
MEMORY_TODAY=2026-05-11 tools/rebuild-views.sh

# Query facts and events
tools/query.sh facts --entity elena-voss
tools/query.sh facts --entity elena-voss --predicate role
tools/query.sh events --since 2026-03-01

# Propose and compact a new fact
tools/ops.py create-fact \
  --agent agent-local-1234abcd \
  --entity elena-voss \
  --predicate role \
  --value "Art conservator" \
  --reason "Capture a durable role fact."
tools/compact.sh
```

CI mirrors the same posture: install PyYAML, lint the v3 example vault, rebuild generated views with a deterministic date, and fail if generated views drift.

## How this differs from v2

v2 treated `memory/people/elena-voss.md` as both a human page and an agent source of truth. That worked, but it made schema enforcement, querying, concurrency, and drift detection fuzzy.

v3 keeps the human page, but moves the durable fact into files like:

```text
memory/facts/elena-voss/role.md
memory/facts/elena-voss/base.md
memory/facts/elena-voss/employer.md
```

The human note stays readable. The agent fact becomes typed, lintable, queryable with filesystem tools, and safe to propose through `_inbox/`.

## Compatibility with AI tools

| Tool | Recommended integration |
|---|---|
| Claude Code / Copilot CLI / Cursor-like agents | Read the vault from disk; follow `CLAUDE.md`, `AGENTS.md`, or local instructions |
| Claude Desktop / Cowork-style tools | Package the protocol as commands or a skill; see [`plugin-guide.md`](plugin-guide.md) |
| Anthropic Memory Tool | Map `memory/` to `/memories`; treat `_views/`, `_inbox/`, `_claims/`, and `_ops/` as special folders |
| Standalone scripts | Use the portable tools in the vault; see [`automation-guide.md`](automation-guide.md) |
| Obsidian local maintenance | Use Obsidian CLI for native link/property audits; see [`obsidian-cli.md`](obsidian-cli.md) |

## Acknowledgments

This project draws on the plain-file knowledge-base pattern described by Andrej Karpathy, the tiered memory ideas popularized by MemGPT/Letta, typed memory concepts from Chetna, cooperative agent memory patterns from the 2026 memory-tooling ecosystem, and Obsidian's own Markdown-first conventions.

The v3 design keeps the parts that fit a personal, owner-controlled memory layer and deliberately leaves managed infrastructure problems to systems built for that scale.
