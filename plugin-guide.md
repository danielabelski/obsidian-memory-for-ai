# Packaging the Memory Protocol as Commands or a Skill

> **Status:** Optional v3.1 integration guide. This document describes how to expose the protocol to host agents such as Claude Desktop/Cowork-style tools. It is not part of the v3 compatibility contract.

The goal is to package a v3 vault's loading and update rules so an assistant can follow them consistently without stuffing every instruction into `CLAUDE.md`.

## What to package

Create a small command/skill bundle with:

| Component | Purpose |
|---|---|
| `/memory-load` | Load the right v3 views and narrative pages for a topic |
| `/memory-propose` | Propose facts or events into `_inbox/` |
| `/memory-compact` | Apply reviewed operations and rebuild views |
| `/memory-audit` | Report stale facts, conflicts, unresolved links, and schema issues |
| Skill/reference docs | Teach the assistant the v3 folder semantics |

The host tool decides the exact packaging format. The protocol content should stay the same.

## Skill body template

```yaml
---
name: memory-system
description: >
  Use when the user mentions memory, vault, Obsidian context, facts, events,
  _views, _inbox, agents, remembered preferences, or asks to load/update/audit
  an Obsidian-backed AI memory system.
version: 0.1.0
---
```

Recommended body:

```text
You are operating on a v3.1 Obsidian Memory vault.

Load order:
1. Read CLAUDE.md, AGENTS.md, or equivalent procedural instructions.
2. Read memory/schema/version.yaml and memory/schema/predicates.yaml.
3. Prefer generated context from memory/_views/.
4. Load human narrative pages only when relevant to the user's topic.

Write rules:
- Do not edit memory/_views directly.
- Prefer operation envelopes under memory/_inbox/{agent-id}/ops/.
- Use tools/ops.py for fact proposals and tools/reflect.py for session reflections.
- Apply changes with tools/compact.sh.
- Run tools/lint.py and tools/rebuild-views.sh before considering changes done.
- Treat memory/_claims as advisory, not transactional locks.
- Treat last_reviewed as semantic validation, not a mechanical audit timestamp.
```

Keep tool-specific details in reference files so the main skill remains short.

## Command templates

### `/memory-load`

```yaml
---
description: Load relevant context from a v3 Obsidian Memory vault
allowed-tools: Read, Glob, Grep
argument-hint: [topic/person/project]
---
```

Instructions:

1. Read procedural instructions and `memory/schema/version.yaml`.
2. Read relevant generated views, starting with `_views/by-id.md`, `_views/by-predicate.md`, `_views/timeline.md`, or `_views/by-entity/{entity}.md` when the topic maps to an entity.
3. Load narrative pages from `people/`, `projects/`, `context/`, `decisions/`, or `insights/` only when they add human context.
4. Summarize what was loaded and what remains uncertain.

### `/memory-propose`

```yaml
---
description: Propose a v3 memory change without directly mutating canon
allowed-tools: Read, Write, Bash
argument-hint: [fact/event/review/archive description]
---
```

Instructions:

1. Resolve entity and predicate names against `memory/entities.md` and `memory/schema/predicates.yaml`.
2. Prefer `tools/ops.py create-fact` for durable semantic facts.
3. Prefer `tools/reflect.py` for session-level event proposals.
4. Leave the result in `_inbox/` unless the user explicitly asks to compact.

### `/memory-compact`

```yaml
---
description: Review and apply proposed v3 memory operations
allowed-tools: Read, Write, Bash
---
```

Instructions:

1. Run `tools/compact.sh`.
2. Run `tools/lint.py`.
3. Run `tools/rebuild-views.sh`.
4. Report applied operations and unresolved conflicts.

### `/memory-audit`

```yaml
---
description: Audit a v3 Obsidian Memory vault
allowed-tools: Read, Glob, Grep, Bash
argument-hint: [quick|monthly|schema|conflicts]
---
```

Instructions:

1. Run `tools/lint.py`.
2. Inspect `_views/stale.md`, `_views/contradictions.md`, `_views/conflicts.md`, `_views/inbox.md`, and `_views/operations.md`.
3. Report findings by severity.
4. Do not bulk-refresh `last_reviewed`.
5. Do not apply changes unless the user asks for a separate compact/apply step.

## Adapting to host tools

| Host | Adaptation |
|---|---|
| Claude Desktop / Cowork | Package the templates as slash commands and a skill |
| Claude Code / Copilot CLI | Put the core rules in `CLAUDE.md`, `AGENTS.md`, or repo instructions |
| Cursor-like tools | Use command docs plus workspace rules |
| Anthropic Memory Tool | Point the runtime at `memory/`, but mark `_views`, `_inbox`, `_claims`, `_ops`, and `_archive` as special-purpose folders |

## Legacy note

Older plugin recipes targeted v2 compiled-wiki vaults and used files such as `ContextSummary.md`, `recent-sessions.md`, `Timeline.md`, and broad prose-page edits. Those patterns remain useful for legacy v2 vaults, but new plugin packaging should default to v3 views, facts, events, and operation envelopes.
