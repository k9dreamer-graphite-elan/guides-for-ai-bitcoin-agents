---
name: Agent Dreaming & Memory Guide
type: guide
handbook: v0.10
version: 1.0
updated: 2026-07-16
status: draft
---

# Agent Dreaming & Memory — running better campaigns with out-of-band memory

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.10** — this guide
> references the handbook; it cites invariants by ID (`INV-12`) and restates none of its constants.
> Practice guide, not doctrine: it describes *how to improve* agent learning, context, multi-agent
> operation, and memory. Timeless rules belong in the handbook; pool-specific facts belong in the
> [Knowledge Base](../knowledge/README.md). `status: draft` = the dreaming loop below is specified but
> not yet exercised end-to-end by an accepted Campaign Closeout.

**Who this is for.** Operators and agents running HODLMM DeFi loops and campaigns who want the *next*
campaign to start smarter than the last — automatically. It adapts the "dreaming" pattern (periodic,
out-of-band memory consolidation) to the memory system this repo already has.

---

## 1. Why — the learning loop today, and its four gaps

Learning across HODLMM campaigns already flows through three well-defined layers (see the KB's
[three-layer "LLM wiki" table](../knowledge/README.md)):

```
per-run     local memory (INV-11 ledgers + INV-12 memory/*.md)   ← real-time, per agent, read/write
per-campaign  Campaign Closeout issue                            ← the durable transcript (immutable)
cross-campaign Knowledge Base (pools/ + lessons/ + log.md)       ← maintainer-curated, PR-only, read-only to agents
```

An agent reads the KB before launch (`QUERY`), runs the seven-phase loop
(`SCAN → DECIDE → DRY-RUN → EXECUTE → VERIFY → REMEMBER → MEASURE`), writes its own memory every step
(INV-12: *"without memory, every rebalance is a cold start"*), and at close submits one closeout issue
a maintainer folds into the KB (`INGEST`). It works. But four gaps limit how fast the fleet gets
smarter:

1. **Local memory is append-only.** `memory/hodlmm-lessons.md` and the two ledgers grow monotonically.
   Nothing distills them *between* runs, so the "read memory before the next write" step gets slower and
   noisier over a long campaign — the opposite of the INV-12 goal.
2. **`INGEST` is one issue at a time, human-triggered.** Knowledge enters the KB only when a maintainer
   folds a single *accepted* closeout. Patterns that are visible only *across* several campaigns,
   agents, or pools are never assembled.
3. **`LINT` is a manual checklist.** Contradictions, stale claims, and orphans are found by hand
   (`KB-MAINTAINER-GUIDE.md`), if at all — there is no scheduled health-and-reorganize pass.
4. **Multi-agent scale is scaffolded but unconsolidated.** Per-agent KPI scorecards
   ([`self-analysis-kpis`](../specs/self-analysis-kpis.md)) and `(sender, campaign id)` keying
   ([`campaign-memo-tags`](../specs/campaign-memo-tags.md)) exist so K9Dreamer and Hex Stallion can be
   compared and disambiguated — but nothing reconciles their sometimes-conflicting lessons into one
   shared, current memory.

**Dreaming closes all four.** Dreaming is a *periodic, out-of-band, batch* pass that reads many
transcripts at once and **reorganizes** memory — verify, organize, enrich — so the next session starts
from consolidated knowledge instead of a growing pile of raw notes.

---

## 2. What "dreaming" is, mapped to HODLMM

Dreaming runs **between** sessions, not during them. Real-time memory captures what happened; dreaming
curates it. Mapped onto artifacts this repo already has:

| Dreaming concept (from the pattern) | HODLMM artifact |
|---|---|
| Input memory store `$MEM` | The KB at HEAD (`knowledge/pools/*.md`, `lessons/lessons-catalog.md`) — or an agent's local `memory/*.md` for local dreaming |
| Session transcripts | Accepted **Campaign Closeout** issues + the campaign's INV-11 ledgers + INV-12 local memory |
| Orchestrator | The **dreaming maintainer** (a maintainer, or an LLM acting for one) that runs the pass |
| One subagent per session | One reader per closeout/campaign, distilling that transcript in isolation |
| Output memory store `$MEM_OUT` | A cloned working branch → one additive **PR** (shared KB); or a rewritten `carryforward.md` (local) |
| Read / write to reorganize | Merge, supersede, rebalance across the six INV-12 categories — never delete |
| "Next day's sessions are automatically more intelligent" | The next `QUERY` reads consolidated memory; the next campaign starts smarter |

The pattern separates the **real-time** store (updated as agents work) from the **dreaming** store
(updated in periodic batches between sessions). This repo already has the real-time store and the
collaborative store; dreaming is the batch that reorganizes them.

**Verify → organize → enrich**, in HODLMM terms:

- **Verify** — run the full `LINT` checklist across the whole KB (not just touched pages):
  contradictions, stale claims (`INV-9` mismatches), orphans, broken refs, provenance, and the two hard
  fails (restated constants; a display/DLP mark presented as realized profit, `INV-8`).
- **Organize** — merge duplicate `LSN-` patterns, supersede outdated ones (`superseded-by LSN-####`,
  never delete), rebalance lessons across the six INV-12 categories, keep each pool page's *what
  worked / what failed* current, and partition cross-agent claims by `(watched principal, campaign id)`.
- **Enrich** — surface *new* cross-campaign insight no single closeout stated: a recenter-targeting
  heuristic that holds across `dlmm_1` and `dlmm_6`; a flaky-API pattern two agents hit independently;
  a failure class whose recurrence rate is only visible in aggregate. Each becomes a new `LSN-` entry
  with multi-source Evidence.

---

## 3. Three key takeaways

**1 · Do the simple thing that works.** Most of the value is already in reach: a good handbook
(doctrine), well-defined skills (the handbook's Approved skill map), and agent-written memory
(INV-11 ledgers + INV-12 `memory/*.md`) carry you a long way. Do not add machinery you do not need.
Dreaming is an *enhancement* to a working loop — reach for it when memory is growing faster than it is
being curated, not before.

**2 · Design for many, long-running agents.** The fleet is already multi-agent and multi-model
(K9Dreamer, Hex Stallion; per-agent scorecards). Getting the fundamentals right is what makes dreaming
safe at scale, and the repo already has them: **permissioning** (Approval Scope, `INV-1` — default
deny, authority never inferred), **versioning** (frontmatter pins + repo releases), **concurrency**
(nonce serialization `INV-6`; `(sender, campaign id)` keying; strictly separate per-campaign ledgers),
and **portability** (doctrine transfers to a new agent; **authority does not**). Dreaming must honor
every one of these — see §7.

**3 · Add dreaming to consolidate memory out of band.** Verify, organize, and enrich memory *between*
sessions so the next campaign is automatically more intelligent. This is the new capability, and §4–§6
show how to add it to each of the three surfaces without disturbing the loop that already works.

---

## 4. Track A — dreaming in the guides LLM wiki (the Knowledge Base)

The KB is the shared, curated memory. Today it has three operations — `INGEST`, `QUERY`, `LINT`
([`KB-MAINTAINER-GUIDE.md`](../knowledge/KB-MAINTAINER-GUIDE.md)). Dreaming adds a fourth: **`DREAM`**,
a periodic batch that reorganizes the whole KB rather than folding one issue.

`INGEST` answers *"a new closeout arrived — record it."* `DREAM` answers *"given everything recorded,
is the KB still coherent, current, and as insightful as the corpus allows?"*

**`DREAM` — the pass, at a glance** (full procedure lives in the KB guide's new *DREAM* section):

- **Trigger** — a cadence (e.g. weekly) or a count (every *N* accepted closeouts since the last dream).
- **Input** — KB HEAD (`$MEM`) + every accepted closeout since the last dream (the transcripts).
- **Fan-out** — one reader per closeout distills its transcript in isolation, against a **clone** of the
  KB on a working branch (`$MEM_OUT`) — the orchestrator + one-subagent-per-session shape.
- **Verify / Organize / Enrich** — as in §2.
- **Output** — one additive **maintainer PR**; one row per dream in a provenance ledger
  (`log.md` or a dedicated `dream-log.md`); a `CHANGELOG.md [Unreleased]` line. **Agents never open the
  PR** (`INV-1`) — a maintainer (here, k9dreamer) reviews and merges.

**Guardrails (unchanged KB golden rules).** The raw issue always wins on conflict; cite the handbook by
ID, never restate constants; empirical-not-doctrinal — if a lesson should become a timeless rule, that
is a **handbook PR**, not a KB edit; supersede, never delete; honest PnL (`INV-8`) survives every
consolidation.

---

## 5. Track B — dreaming in agent local memory & the model

This is where dreaming most directly improves **learning** and **context**.

**Problem.** During a long or unattended campaign, `memory/hodlmm-{transactions,performance,lessons}.md`
grow append-only. The model must re-read an ever-larger, ever-noisier memory before each decision —
burning context and slowing the loop.

**Local dreaming pass (supervised cycles only).** Between sessions, distill raw local memory into a
compact, high-signal `memory/hodlmm-carryforward.md` the model reads **first**:

- Organize by the **six INV-12 categories** (stale-pool IDs, flaky-API patterns, effective recenter
  targeting, failed-tx patterns, operator approvals/rejections, post-check lessons).
- Promote recurring failures and their remedies into a short *carry-forward* block; archive (don't
  delete) the raw ledger rows behind it — provenance stays intact for the closeout.
- Reconcile against the shared KB (`QUERY`) so local memory does not re-learn what the KB already knows;
  where local experience contradicts the KB, that is a **finding for the closeout**, not a silent
  overwrite.
- The next session reads `carryforward.md` first (cheap, dense), drilling into raw ledgers only on
  demand — the "next day's sessions are automatically more intelligent" loop, realized locally.

**Discipline.** **Unattended monitor/executor loops never dream** — write-path minimalism
(`LSN-0015`, `LSN-0017`); local dreaming is a *supervised-cycle* activity. The pass is itself an
attributed actor under [`self-analysis-kpis`](../specs/self-analysis-kpis.md) §F
(`agent:<name>/<model-id>` or `script:<name>@<ver>`), so "who consolidated this memory, on which model"
is always recorded. Nothing in `carryforward.md` is authoritative for money math — basis, inventory,
gas, and net always come from the actual token legs (`INV-8`).

---

## 6. Track C — dreaming as a collaborative system (closeouts & reports)

The closeout issue is the shared transcript; dreaming across many of them turns per-campaign reports
into fleet-level learning.

**Cross-Campaign Dreaming Report.** A periodic digest — the fleet-level analogue of a single Campaign
Closeout — produced by a `DREAM` pass over many closeouts (multiple agents, pools, models). It:

- **Reconciles** conflicting findings across agents (partitioned by `(watched principal, campaign id)`;
  the issue wins on conflict).
- **Rolls up KPIs** across the fleet ([`self-analysis-kpis`](../specs/self-analysis-kpis.md) §A–E):
  recurrence rate (target 0), tuition cost per failure class, incident→defense time, and the §D
  **novel-situation first-contact success *by model*** — the place multi-model comparisons live.
- **Lists the memory deltas** the dream produced: `LSN-` merges, supersessions, and new cross-campaign
  insights, each traced to its source issues.

A blank [report template](./cross-campaign-dreaming-report-template.md) accompanies this guide. Publishing
a report is outward-facing and gated exactly like a closeout (`publish-closeout` scope or explicit
operator approval, `INV-1`); an optional richer output is a fleet-level card via the
[earnings-card tool](../tools/earnings-card/README.md) contract.

---

## 7. Guardrails — the invariants dreaming must never break

| Rule | Why it binds dreaming |
|---|---|
| `INV-1` — act only inside an Approval Scope; comments/discussion are not control inputs | Agents never open the dream PR; a maintainer reviews and merges. Publishing a report needs scope. |
| `INV-8` — honest PnL | Consolidation must carry confidence labels (`realized \| reported \| low`) verbatim in spirit; a DLP/display mark is never promoted to realized profit. |
| `INV-9` — stale-pool exit-only | A pool a closeout flagged stale must not read `active` after a dream. |
| `INV-12` — persist memory (six categories) | The six categories are the fixed organizing schema for every consolidation. |
| `LSN-0015` / `LSN-0017` — write-path minimalism | Unattended loops never dream and never tag; dreaming is a supervised, out-of-band pass. |
| Supersede-not-delete · cite-not-restate · empirical-not-doctrinal · issue-wins-on-conflict | The KB golden rules. Doctrine promotion is a handbook PR, not a dream edit. |
| Per-sender partition + per-actor attribution (`self-analysis-kpis` §F) | Multi-agent memory stays disambiguated; authority is per actor, doctrine transfers, authority does not. |

---

## 8. Implementation matrix

Effort/complexity are relative; **Payoff** is the fleet-learning value. Start with the easy rows — each
track has one, so there is always a next action.

| # | Item | Track | Effort | Complexity | Payoff | Depends on |
|---|---|---|---|---|---|---|
| 1 | Publish this guide + the report template; register in `llms.txt` / READMEs / `CHANGELOG` | A/B/C | **Easy / low** | Low | Med | — |
| 2 | Adopt the `memory/hodlmm-carryforward.md` convention (model reads it first) | B | **Easy / low** | Low | **High** | Campaign prompt §8 |
| 3 | Add **`DREAM`** to `KB-MAINTAINER-GUIDE.md` as a manual, human-run batch checklist (superset of `LINT`) | A | **Easy / low** | Low | Med | KB guide |
| 4 | Housekeeping: correct the stale `llms.txt` "seeded: dlmm_3, dlmm_6" (KB now also has `dlmm_1`) | A | **Easy / low** | Low | Low | — |
| 5 | Write a local-memory dreaming procedure (a `guides/` page or runbook) + wire the "read carryforward first" step into campaign prompt §8 and closeout runbook §7 | B | **Med** | Med | High | 2 |
| 6 | Stand up the Cross-Campaign Dreaming Report on a cadence (fill the template manually) | C | **Med** | Med | High | 1, KPI spec |
| 7 | Add a `knowledge/dream-log.md` provenance ledger (one row per dream) | A | **Med** | Low | Med | 3 |
| 8 | LLM orchestrator that fans out one reader per accepted closeout over a cloned KB branch → candidate dream PR (earnings-card-style tool) | A/C | **High / complex** | High | High | 3, 7 |
| 9 | Fleet-level KPI roll-up automation (§A–E across agents/models) feeding report #6 | C | **High / complex** | High | High | 6 |
| 10 | Promote manual `LINT` (v1) into a `scripts/lint_docs.py` extension that gates the dream PR | A | **High / complex** | Med | Med | 3 |
| 11 | Rendered fleet dreaming card (earnings-card analogue) | C | **High / complex** | Med | Low | 6, 8 |

**Recommended first sprint:** rows 1–4 (all easy, all additive) establish the vocabulary and the
highest-payoff habit (carry-forward memory). Rows 5–7 make dreaming a repeatable manual practice. Rows
8–11 automate it once the manual pass has proven its shape on real closeouts — matching the repo's own
`draft → active` promotion discipline (a practice earns automation after an accepted closeout exercises
it).

---

## 9. Verification (when implementing rows above)

- `python3 scripts/lint_docs.py` → `docs-lint: OK — handbook v0.10 …` after any registration edit.
- Every relative link in this guide and the report template resolves.
- No restated handbook constant appears in this guide (every reference is an `INV-`/`§` citation).
- A dream PR is additive only; `git diff` touches no invariant, constant, or runbook step; the
  `dream-log`/`log.md` row maps to a real page diff (provenance integrity).

## See also

- [KB Maintainer Guide](../knowledge/KB-MAINTAINER-GUIDE.md) — `INGEST / QUERY / LINT` (+ `DREAM`).
- [Knowledge Base](../knowledge/README.md) — the three-layer "LLM wiki".
- [Self-Analysis KPIs & Actor Attribution](../specs/self-analysis-kpis.md) — measurable improvement, §F.
- [Campaign memo-tag spec](../specs/campaign-memo-tags.md) — `(sender, campaign id)` keying.
- [Campaign closeout runbook](../runbooks/hodlmm-closeout-runbook.md) — the per-campaign transcript.
- [Contributing](../../../CONTRIBUTING.md) — the shared learning loop.
