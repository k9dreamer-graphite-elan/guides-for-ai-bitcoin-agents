# Agent Authoring Guide — Maintaining the HODLMM Runbooks

> Standing instructions for any agent (or human) that **updates an existing runbook or writes a new
> one** in this repo. It is both the agent's operating prompt and the contributor spec. Read it before
> touching anything in `public/hodlmm/runbooks/`.

## 1. The repo's document model

Three layers, by purpose. Never blur them:

- **Handbook (doctrine)** — [`../handbook/HODLMM-Agent-Handbook.md`](../handbook/HODLMM-Agent-Handbook.md).
  The canonical source of truth: invariants (`INV-1`…`INV-12`), terminology, contract IDs, fee
  mechanics, the pre-flight GATE. Currently **v0.6**. You do NOT restate its contents elsewhere — you
  cite it.
- **Operating guide (field manual)** — [`../operating-guide/hodlmm-operating-guide.md`](../operating-guide/hodlmm-operating-guide.md).
  Daily practice + **strategy selection** (which runbook to run when). References the handbook.
- **Runbooks (procedures)** — this folder. One executable operation per file. This is what you write.

```
public/hodlmm/
├── handbook/            # doctrine (don't edit unless fixing doctrine)
├── operating-guide/     # daily practice + strategy profiles
├── knowledge/           # distilled campaign memory (see KB-MAINTAINER-GUIDE.md, not this file)
└── runbooks/
    ├── _TEMPLATE-runbook.md
    ├── AGENT-AUTHORING-GUIDE.md   # this file
    └── hodlmm-<operation>-runbook.md
```

> The **Knowledge Base** (`../knowledge/`) is a separate practice surface — distilled, pool-specific
> campaign memory built from accepted closeout issues. Its maintenance is governed by
> [`../knowledge/KB-MAINTAINER-GUIDE.md`](../knowledge/KB-MAINTAINER-GUIDE.md), **not** this runbook
> authoring flow. Same "import, don't copy" discipline applies.

## 2. Golden rules (non-negotiable)

1. **Import, don't copy.** Cite handbook invariants by ID (e.g. "bounded swap per INV-3"). NEVER paste
   or re-derive the handbook's constants (`max-steps`, read ceiling, fee rates, addresses). If the
   handbook changes a number, runbooks must inherit it — so don't duplicate it.
2. **One operation per file.** A runbook does one repeatable thing, end to end.
3. **Executable.** A runbook must be followable step-by-step: inputs → required scope → gates →
   procedure (skills/commands) → expected outputs → failure handling.
4. **No mutable live state in any doc.** Pool lists, TVL, APR, active bin, fee rates are queried live,
   never hardcoded.
5. **Never invent contract addresses or limits.** Use the handbook §1.1/§1.2. If something is
   unverified, say so — don't assert it.
6. **Filenames: `hodlmm-<operation>-runbook.md`, lowercase, HYPHEN-separated.** Keep every dash. (Past
   uploads silently dropped hyphens and broke links — always verify the committed filename matches the
   hyphenated name.)

## 3. The runbook contract

Every runbook starts with this frontmatter, then follows
[`_TEMPLATE-runbook.md`](./_TEMPLATE-runbook.md)'s sections:

```yaml
---
name: HODLMM <Operation> Runbook
type: runbook
handbook: v0.6                 # the doctrine version this conforms to
enforces: [INV-1, INV-2, ...]  # the invariants this runbook guarantees
skills: [hodlmm-..., ...]      # approved skills it calls (from aibtc.com/skills)
status: draft|active|deprecated
---
```

Required sections (from the template): Purpose · When to run / NOT to run · Inputs · Required Approval
Scope (INV-1) · Gates (the Ch.0 pre-flight subset that applies) · Procedure (SCAN→…→REMEMBER, dry-run
before any broadcast) · Expected outputs · Failure handling (map each to Handbook **Ch.3 §3.x**) ·
Idempotency/cooldown.

## 4. When UPDATING an existing runbook

1. Keep the frontmatter. Bump `handbook:` if you're aligning it to a newer doctrine version, and
   re-check that `enforces:` still lists every invariant the procedure actually guarantees.
2. Make sure nothing in the body contradicts the handbook (e.g. swap path = `*-simple-range-multi`,
   `max-steps ≤ 230`; LP protection = `min-dlp`/fee-cap/active-bin bounds). If the runbook is stricter
   than the handbook (e.g. a longer cooldown), that's fine — stricter is allowed, contradiction is not.
3. Don't import handbook prose. Replace any restated constant with a citation.
4. Preserve author attribution and voice. Don't rewrite a human-authored runbook's content unless
   asked — you add structure (frontmatter, conformance line), you don't editorialize.

## 5. When CREATING a new runbook

1. Copy [`_TEMPLATE-runbook.md`](./_TEMPLATE-runbook.md) → `hodlmm-<operation>-runbook.md`.
2. Fill every section. The Procedure steps must be concrete skill/command calls with expected outputs.
3. Set `enforces:` to exactly the invariants your steps guarantee. Set `skills:` to the approved skills
   you call.
4. Map every failure mode to a Handbook Ch.3 row — don't write new recovery logic that the handbook
   already owns.
5. Add the new runbook to the catalog table in [`../README.md`](../README.md) (flip `planned` → `active`).
6. If it introduces or changes a *strategy choice*, update the strategy-profiles table in the operating
   guide — strategy *selection* lives there; strategy *execution* lives in the runbook.

Planned runbooks to build (copy the template): `hodlmm-campaign-entry-runbook.md`,
`hodlmm-recenter-runbook.md`, `hodlmm-inventory-balancing-runbook.md`, `hodlmm-exit-runbook.md`,
`hodlmm-pnl-runbook.md`. Cross-protocol ones (e.g. sBTC yield routing) go in `public/shared/`.

## 6. Pre-commit conformance check

Before committing any runbook, confirm:

```
[ ] Frontmatter: name/type/handbook/enforces/skills/status present
[ ] Cites handbook invariants by ID; restates NO handbook constants
[ ] Required Approval Scope + Gates sections reflect the actual operation (INV-1, pre-flight)
[ ] Swaps: bounded entrypoint + max-steps <= 230 + residual handling (INV-3)
[ ] Fund-protection form correct (swap = Deny PCs; LP = Allow + bounds) (INV-2)
[ ] Every failure mode maps to Handbook Ch.3
[ ] No hardcoded mutable state; no invented addresses/limits
[ ] Filename is hodlmm-<operation>-runbook.md WITH hyphens
[ ] Catalog (hodlmm/README.md) updated; operating guide updated if strategy changed
```

## 7. Hard don'ts

- Don't duplicate or contradict the handbook.
- Don't hardcode pool lists, TVL, APR, fee rates, or contract addresses.
- Don't strip hyphens from filenames.
- Don't add a write step without the pre-flight GATE in front of it.
- Don't claim a fact you can't verify on-chain — flag it instead.
