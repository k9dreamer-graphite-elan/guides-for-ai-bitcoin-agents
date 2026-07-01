# KB Maintainer Guide — Maintaining the HODLMM Knowledge Base

> Standing instructions for any **maintainer** (or LLM acting for one) that updates the HODLMM
> Knowledge Base under `public/hodlmm/knowledge/`. Sibling to the
> [`AGENT-AUTHORING-GUIDE`](../runbooks/AGENT-AUTHORING-GUIDE.md) — that one governs runbooks; this one
> governs the KB. **Agents do not use this guide to edit the KB** — agents submit closeout *issues* and
> read the KB; only maintainers write it.

## The golden rules (import, don't copy)

1. **Raw issues are authoritative.** The KB *distills and links*; it never replaces the issue. On any
   conflict, the issue wins. Every claim carries a `sources:` link back to the issue it came from.
2. **Cite, never restate.** Cite the handbook by invariant ID (`INV-8`) or section (`§4.2`), and cite
   runbooks by name. Never copy a handbook constant (contract IDs, bin counts, step/read limits) into
   the KB — those live in the handbook and move with it.
3. **No secrets, no live state.** Only on-chain-public or operator-approved data. No keys/seeds. No
   cached pool lists, TVL, APR, or active-bin values — those are queried live.
4. **Honest PnL (INV-8).** Never present a DLP balance or protocol "display earnings" as realized
   profit. Carry the issue's confidence labels verbatim in spirit (`realized | reported | low`).
5. **Empirical, not doctrinal.** The KB holds *time-stamped, pool-specific, empirical* knowledge. If a
   lesson should become a timeless rule, that's a **handbook/runbook PR**, not a KB edit.

## The three operations

### INGEST — fold an accepted closeout into the KB *(maintainer-side, PR-based)*

Trigger: a Campaign Closeout issue is labeled **`accepted`**.

1. **Read the accepted issue only.** Not the comment thread as authority (comments are discussion, not
   control — `INV-1`).
2. **Gate before ingest:** no secrets; PnL is framed net-vs-hold after gas with display marks labeled
   context-only (`INV-8`); closure proof present (wallet DLP zero + chain-confirmed exit, `INV-10`);
   status is `accepted`.
3. **Pick 1–3 target pages.** The pool's `pools/<pool>.md` (create it from
   [`_TEMPLATE-pool.md`](./pools/_TEMPLATE-pool.md) if new) and/or `lessons/lessons-catalog.md`. Don't
   spray edits across many pages.
4. **Distill, don't copy.** Summarize the tactic/failure/lesson in your own words; add the issue URL to
   the page `sources:` and to each claim's Evidence; carry the confidence label.
5. **Cross-link both ways.** Pool page ↔ lesson entry. Reuse an existing `LSN-` id when the pattern
   already exists (extend its Evidence/Pools); **supersede, don't delete** (`Status: superseded-by
   LSN-####`). `LSN-` ids are stable and never reused.
6. **Append one row to [`log.md`](./log.md).**
7. **Bump touched pages'** `version` / `updated` / `last_ingested`, and add a line to `CHANGELOG.md`
   `[Unreleased]`.
8. **Open an additive PR.** Agents never do this step.

### QUERY — read the KB before acting *(agent- or maintainer-run, read-only)*

`README` → `pools/<pool>.md` (status, what worked, what failed, recenter targeting) → skim
`lessons-catalog.md` by `INV-12` category → for anything load-bearing, follow `sources` to the raw
issue. The KB is a fast index; the issue is the source of truth. Agents QUERY freely and never edit.

### LINT — health-check the KB *(maintainer-run; manual checklist in v1)*

- **Contradictions:** two `active` claims that conflict with no `superseded-by` link between them.
- **Stale claims:** a page `last_ingested` older than a newer accepted closeout for that pool; or a KB
  pool `status: active` while a closeout flagged it stale/exit-only (`INV-9` mismatch).
- **Orphans:** a page with zero inbound links or an empty `sources:`.
- **Broken refs:** dead relative links; one-directional pool↔lesson links; `superseded-by` pointing at a
  missing `LSN-`.
- **Provenance integrity:** every claim traces to a `sources:` URL; every `log.md` row maps to a real
  page diff.
- **Import discipline (hard fail):** a restated handbook constant inside `knowledge/`.
- **PnL honesty (hard fail):** a KB PnL figure with no confidence label, or a display/DLP mark presented
  as realized profit.

## Frontmatter & conventions

Content pages carry: `type` (`kb-pool` | `kb-lessons`), `handbook: v0.6`, `version`, `updated`,
`last_ingested`, `status`, and `sources:` (issue URLs). Index READMEs stay unversioned (the repo
Release covers them). Per-claim `confidence` uses the closeout vocabulary: `realized | reported | low`.
Filenames are lowercase; pool pages mirror the pool id (`dlmm_6.md`).
