---
name: Cross-Campaign Dreaming Report — 2026-07-10 → 2026-07-17
type: guide
handbook: v0.10
version: 1.0
updated: 2026-07-17
status: published
---

# Cross-Campaign Dreaming Report — `2026-07-10 → 2026-07-17`

> First filled instance of the [report template](./cross-campaign-dreaming-report-template.md),
> produced by the **first end-to-end `DREAM` pass** per the
> [Agent Dreaming & Memory Guide](./agent-dreaming-guide.md) (Tracks A + C). Read/report-only — no
> on-chain writes. Publication operator-approved (the pass and its deliverables were
> operator-scheduled 2026-07-16, `INV-1`). Handbook cited by ID; every PnL figure carries its
> confidence label (`INV-8`).

## Scope of this pass

| Field | Value |
|---|---|
| Period | `2026-07-10 → 2026-07-17` |
| Closeouts dreamed (source issues) | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) (`HODLMM-DLMM1-20260710-004`), [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) (`HODLMM-DLMM3-20260710-005`) — the first concurrent two-campaign run |
| Agents / models covered | `agent:k9dreamer/claude-fable-5` (supervised decisions, this pass); `script:hodlmm-campaign-monitor.sh` (all unattended repairs + both exits); `operator` (charter approvals, supervised-repair "go"s) |
| Pools covered | `dlmm_1` (sBTC/USDCx), `dlmm_3` (STX/USDCx) |
| KB state before → after | `6267049` → this PR |
| Run by (attribution §F) | planned_by `operator` (scheduled 2026-07-16) / decided_by + executed_by `agent:k9dreamer/claude-fable-5` / reviewed_by `operator` (PR review) |

**Pass shape.** Both exits chain-verified read-only first (004 `0x417f6be6…` block 8570534, 005
`0x4a3bccfb…` block 8570749, both `success`, DLP 0). Then two isolated per-transcript readers
(closeout issue + INV-11 ledgers + INV-12 local memory each), then consolidation:
verify → organize → enrich, additive only.

## 1. Reconciliation across agents

Partitioned by `(watched principal, campaign id)` — both campaigns here share one principal
(`SP1AK5ZK…7MKR`), which is exactly what made the verify step decisive. The raw issue wins on
conflict; where the *chain* contradicted an issue, the correction was posted **on the issue** so
the issue-plus-comments remains the authoritative transcript.

| Claim | Agents/campaigns | Resolution | Evidence |
|---|---|---|---|
| "Chain-summed gas beats the running counter; state.json drifted (2.05 vs 0.95)" (#59) | k9dreamer · 004 | **superseded-by [LSN-0019](../knowledge/lessons/lessons-catalog.md#lsn-0019)** — a full nonce-range sweep shows the closeout roster omitted 11 unattended auto-moves; the running counter (2.05 STX) was correct and the "chain-sum" was incomplete. The finding as stated was inverted. | [#59 correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054) |
| "Gas 0.80 STX chain-summed over 5 txs" (#60) | k9dreamer · 005 | **superseded-by [LSN-0019](../knowledge/lessons/lessons-catalog.md#lsn-0019)** — 2 auto-moves omitted; true 1.00 STX / 7 txs. | [#60 correction](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60#issuecomment-5003288187) |
| "Swap-back repair was the right recovery" (004) vs "zero-swap moves; swap-backs are exit-adjacent" (005) | k9dreamer · 004 vs 005 | **merged** into [LSN-0020](../knowledge/lessons/lessons-catalog.md#lsn-0020) as a same-week A/B, kept honestly regime-confounded (n=1 per arm) rather than declaring a winner. | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59), [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) |
| "Fully unattended campaign" framing (005) vs decision ledger (2 supervised moves, operator "go"s) | k9dreamer · 005 | **kept-both** — the *exit* was genuinely zero-touch; mid-campaign had 3 human touches. The KB pool page states the unattended stretches instead of the headline adjective. | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60), [pools/dlmm_3.md](../knowledge/pools/dlmm_3.md) |

## 2. Fleet KPI roll-up

Per [`self-analysis-kpis`](../specs/self-analysis-kpis.md) §A–E. **Results (§E) reported last.**
"Prior" = campaigns 002/003 (pre-spec; most KPIs were not yet tracked — `n/a (pre-spec)` where so).

| KPI | Section | This period | Prior | Δ |
|---|---|---|---|---|
| Recurrence rate (target 0) | A | **2 paid recurrences** of documented classes: `u5001` wide-gap move on dlmm_1 (LSN-0001, 0.10 STX) and first-mint postcondition abort on dlmm_3 (LSN-0003, 0.25 STX) | ≥1 (LSN-0003 class at 002/003 era) | not improving yet; both classes now have deployed gates |
| Tuition cost per failure class | A | 0.35 STX ≈ $0.06 total (u5001 0.10; LSN-0003 0.25); zero repeat payments after gating | n/a (pre-spec) | — |
| Incident → defense time | A | u5001 paid abort → pre-broadcast geometry gate: **≈ 2.4 days**; floor-pinning first hit → guardian PINNED posture: **≈ 3 days** | n/a (pre-spec) | — |
| Unattended hours between interventions | B | 004: ~111h, then ~58h (1 mid-campaign touch). 005: ~83h / ~58h / ~27h (3 touches). Both exits zero-touch | 003: scheduled exit unattended; hours untracked | first period with measured stretches |
| Clean-exit rate | C | **2/2** scheduled unattended exits on time, DLP 0, chain-proven (fleet lifetime: 5/5 K9Dreamer campaigns) | 3/3 | held at 100% |
| Novel-situation first-contact success **by model** | D | `agent:k9dreamer/claude-fable-5`: HOLD-NO-REPAIR override vs alert prescription — **graded CORRECT at closeout (1/1)**, first §D data point. Memo-tag spec first live use: worked, surfaced the v1.1 tag-sink erratum on first contact. Pre-2026-07-15 actions: model unrecorded (pre-convention) | n/a (spec adopted 2026-07-15) | baseline established |
| Net vs hold after gas (realized) | E | 004: **≈ +$0.81 / +0.9%** (reported — USD mark on realized inventory, chain-swept gas). 005: **+79.44 STX ≈ +$13.09 / ~+13.2%** (realized in STX terms). Combined ≈ +$13.90 on ~$187 deployed, ~+7.4%/7d | 003: ≈ +$9 / +18% (realized-withdrawal); 002: +$6.31 / +13% (realized) | positive, below 003's regime-assisted peak |

## 3. Memory deltas produced

Supersede-not-delete; every delta traces to a source issue.

| Delta | Type | Pages touched | Source issue(s) |
|---|---|---|---|
| **LSN-0018** created — alert-prescribed remedies are snapshots; fresh-read before executing; grade overrides at closeout | new | `lessons/lessons-catalog.md`, `pools/dlmm_3.md` | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) |
| **LSN-0019** created — closeout tx rosters from a chain nonce-range sweep, never hand-maintained ledgers | new (cross-campaign enrichment — produced by this dream, stated by neither closeout) | `lessons/lessons-catalog.md`, both pool pages | [#59 corr.](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59#issuecomment-5003288054), [#60 corr.](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60#issuecomment-5003288187) |
| **LSN-0020** created — zero-swap moves vs swap round-trips at small notional (same-week A/B, regime-confounded) | new (cross-campaign enrichment) | `lessons/lessons-catalog.md`, both pool pages | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59), [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) |
| **LSN-0001** extended — first paid recurrence on dlmm_1; geometry-gate defense recorded | enrich | `lessons/lessons-catalog.md`, `pools/dlmm_1.md` | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) |
| **LSN-0003** extended — third confirmation (dlmm_3, empty-bin first mint) | enrich | `lessons/lessons-catalog.md`, `pools/dlmm_3.md` | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) |
| `pools/dlmm_1.md` v0.2 → v0.3 — 004 ingested; trend-regime failure mode; corrected PnL | enrich | `pools/dlmm_1.md` | [#59](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/59) |
| `pools/dlmm_3.md` v0.1 → v0.2 — 005 ingested; **off-floor open question ANSWERED**; floor-pinning regime documented | enrich (question answered in place, superseding question recorded) | `pools/dlmm_3.md` | [#60](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/60) |
| `log.md` DREAM row (this pass) | provenance | `knowledge/log.md` | — |

## 4. New cross-campaign insights (enrichment)

- **Closeout self-audit fails the same way fleet-wide** — both concurrent campaigns under-counted
  their own unattended txs at closeout (11 and 2 omissions), because monitor auto-events bypassed
  the role ledger the closeout reads. Visible only when one sweep reconciled the shared wallet's
  full nonce range. Evidence: #59 + #60 corrections; became **LSN-0019**; category: post-check
  lessons.
- **Regime dominates strategy shape at this scale** — one week, one wallet, two pools: whipsaw
  ladder ~+13.2% realized vs trending band ≈ +0.9% reported; and both prior ladder wins (002, 005)
  were whipsaw weeks. Floor proximity, previously the suspected driver, is not required. Evidence:
  #59 + #60 (+#21 context); folded into both pool pages' open questions; the trend-regime cell is
  the fleet's next experiment.
- **Zero-swap relocation preserves edge that swap round-trips consume** (same-week A/B) — became
  **LSN-0020**; category: effective recenter targeting.

**Verification addendum (owed item closed):** the 3 self-flagged skills-audit risks
([#53](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/53)) were
checked against the actual exit behavior and recorded on #53 (2026-07-17 comment): the unprotected
direct-swap path was never exercised by automation; the `min-dlp=1` repair path never fired on exit;
router `v-1-1` handled both exits cleanly with amounts verified against direct reads.

## 5. Doctrine candidates (out of scope for the dream itself)

Handbook/runbook PRs for a maintainer to decide — **not** encoded by this dream:

- **Correct the gas-reconciliation wording merged via PR #61** — the pnl/closeout runbooks now say
  chain-summed `fee_rate` *overrides running counters*; #59's correction shows that rule is unsafe
  without roster completeness. Target: `hodlmm-pnl-runbook` + `hodlmm-closeout-runbook` (align with
  LSN-0019: "sweep the nonce range, then sum").
- **Unattended monitors must write every broadcast tx into the campaign role ledger** (the LSN-0019
  root cause). Target: `hodlmm-unattended-automation-runbook`.
- **Promote [`agent-dreaming-guide.md`](./agent-dreaming-guide.md) `status: draft → active`** —
  this pass is the guide's first end-to-end exercise and its promotion evidence (per the repo's
  own draft→active discipline). Target: separate follow-up PR.

## Confirmations

- [x] No secrets; only on-chain-public or operator-approved data.
- [x] Every PnL figure carries a confidence label; no display/DLP mark presented as realized (`INV-8`).
- [x] Every memory delta traces to a source issue; the `log.md` DREAM row matches the page diffs.
- [x] PR opened under explicit operator direction (pass + deliverables operator-scheduled
  2026-07-16, `INV-1`); the operator reviews and merges — the agent does not merge.
