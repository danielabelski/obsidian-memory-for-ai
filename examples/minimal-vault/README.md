# Example: Minimal Vault — Legacy v2

> **v2 reference:** This example demonstrates the prose-first compiled wiki pattern from the main guide. For the v3 atomic-facts implementation, see [`../v3-minimal-vault/`](../v3-minimal-vault/).

This is a complete, working example of the legacy compiled-wiki system described in the [v2 guide](../../guide.md). New implementations should start from [`../v3-minimal-vault/`](../v3-minimal-vault/).

**The persona is fictional.** Elena Voss is an invented art conservator. The vault demonstrates real structure and conventions using a domain (pigment research, museum conservation) that's different enough from software engineering to show the system works for anyone, not just developers.

## What's here

```
minimal-vault/
├── CLAUDE.md                          ← Tier 0 context / router
├── TASKS.md                           ← Time-horizoned task list
└── memory/
    ├── ContextSummary.md              ← What to load first vs. on demand
    ├── working-context.md             ← Mutable state snapshot (updated each session)
    ├── recent-sessions.md             ← Rolling log of last ~10 sessions
    ├── glossary.md                    ← Acronyms, internal terms, nicknames
    ├── context/
    │   ├── professional.md            ← Role, lab, tools, team
    │   └── personality.md             ← Work style and AI interaction preferences
    ├── people/
    │   ├── marta-delvaux.md           ← Research collaborator
    │   └── tobias-ackermann.md        ← Lab colleague
    ├── projects/
    │   ├── concordance.md             ← Primary research project
    │   └── gallery-work.md            ← Current museum assignment
    └── decisions/
        ├── ContextSummary.md          ← When to create decisions and log
        └── DEC-001 - Concordance...   ← Example decision with full rationale
```

## How to use it

1. **Read through the files** to see how the conventions from the guide look in practice
2. **Copy the structure** to your own vault and replace the content with yours
3. Start with just `CLAUDE.md`, `TASKS.md`, and `memory/glossary.md` — add the rest as you need it

## Things to notice

- **CLAUDE.md is under 80 lines.** Dense, scannable, no filler. It's a router, not a warehouse. Everything else lives in `memory/`.
- **The glossary resolves ambiguity.** "The manuscript" means the Strasbourg MS. "GG" means the museum. The AI won't have to guess.
- **People profiles include what matters for AI context**, not a full biography. Marta's communication preferences and data format expectations are there because they affect collaboration.
- **The decision record captures *why*, not just *what*.** DEC-001 explains why Markdown+CSV was chosen over SQLite — so a future session won't suggest the same rejected alternatives.
- **`working-context.md` is a mutable snapshot.** It captures what matters *right now* — active threads, pending items, recent decisions — so the AI has temporal context without loading full project files. The AI rewrites it at session end.
- **`recent-sessions.md` is a recency buffer.** One line per session, capped at ~10 entries. It gives the AI a sense of momentum and sequence without full conversation replay.
- **Wikilinks with relationship verbs** (`supports:`, `applies:`, `related:`) connect files into a navigable graph.
- **Frontmatter is minimal but consistent.** Type, relevance, last_reviewed on every memory file — and `last_reviewed` means semantic review, not "a bot touched this file during an audit."
