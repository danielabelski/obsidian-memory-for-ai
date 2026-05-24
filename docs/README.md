# Documentation map

This repository is documentation-first. The current protocol is **v3.1 Agentic Atomic Markdown Memory**; older v2 material is retained as legacy reference.

## Canonical reading paths

| Audience | Start with | Then read |
|---|---|---|
| New user copying a vault | [`../README.md`](../README.md) | [`../examples/v3-minimal-vault/`](../examples/v3-minimal-vault/), then [`../SPEC-v3.md`](../SPEC-v3.md) as needed |
| Implementer building tools | [`../SPEC-v3.md`](../SPEC-v3.md) | [`../examples/v3-minimal-vault/tools/`](../examples/v3-minimal-vault/tools/), [`../tests/`](../tests/) |
| Existing v2 user | [`../migration-v3.md`](../migration-v3.md) | [`../examples/v3-minimal-vault/`](../examples/v3-minimal-vault/) |
| Agent/plugin author | [`../plugin-guide.md`](../plugin-guide.md) | [`../automation-guide.md`](../automation-guide.md), [`../obsidian-cli.md`](../obsidian-cli.md) |
| Historian of the original pattern | [`../guide.md`](../guide.md) | [`../examples/minimal-vault/`](../examples/minimal-vault/) |

## Document status

| Document | Status | Role |
|---|---|---|
| [`../README.md`](../README.md) | Current | Landing page and short orientation |
| [`../SPEC-v3.md`](../SPEC-v3.md) | Current, normative | Stable v3.1 compatibility contract |
| [`../examples/v3-minimal-vault/README.md`](../examples/v3-minimal-vault/README.md) | Current | Working v3.1 reference implementation |
| [`../migration-v3.md`](../migration-v3.md) | Current | Manual v2-to-v3 migration checklist |
| [`../automation-guide.md`](../automation-guide.md) | Current, optional | v3-compatible automation patterns |
| [`../plugin-guide.md`](../plugin-guide.md) | Current, optional | Host-agent command/skill packaging pattern |
| [`../obsidian-cli.md`](../obsidian-cli.md) | Optional integration | Local Obsidian CLI recipes |
| [`../photo-ingest-guide.md`](../photo-ingest-guide.md) | Optional integration | Domain-specific ingest workflow |
| [`../optional-ideas.md`](../optional-ideas.md) | Experimental | Non-protocol ideas |
| [`../guide.md`](../guide.md) | Legacy v2 | Original compiled-wiki guide |
| [`../examples/minimal-vault/README.md`](../examples/minimal-vault/README.md) | Legacy v2 | Original compiled-wiki example |

## Maintenance rules

1. Keep `README.md` short and navigational; move deep explanations to focused docs.
2. Treat `SPEC-v3.md` as the source of truth for v3 behavior.
3. Mark v2 content as legacy wherever it appears.
4. Avoid adding new top-level guides unless they are broadly useful. Prefer this `docs/README.md` map plus focused existing guides.
5. When a guide describes optional tooling, state whether it is required for v3 compatibility. Most integrations are optional.
6. Do not bulk-refresh date examples unless the semantic guidance changes.
