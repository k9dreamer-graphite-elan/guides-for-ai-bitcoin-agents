---
name: Cross-Campaign Dreaming Report — 2026-07-17 → 2026-07-29
type: guide
handbook: v0.10
version: 1.0
updated: 2026-07-29
status: published
---

# Cross-Campaign Dreaming Report — `2026-07-17 → 2026-07-29`

> Second end-to-end `DREAM` pass per the
> [Agent Dreaming & Memory Guide](./agent-dreaming-guide.md), over three closed campaigns and two
> watched principals. Read/report-only: no wallet or on-chain write was used. Publication and PR
> creation were operator-directed on 2026-07-28 (`INV-1`); every PnL figure carries its confidence
> label (`INV-8`).

## Scope of this pass

| Field | Value |
|---|---|
| Period | `2026-07-17 → 2026-07-29` |
| Closeouts dreamed | [#67](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/67) (`HODLMM-DLMM3-20260717-006`), [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) (`HODLMM-DLMMV2-20260722-007`), [#71](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/71) (`HODLMM-DLMM1-20260720-004`) |
| Agents / models covered | `agent:k9dreamer/claude-fable-5`; `script:hodlmm-campaign-monitor.sh`; Hex Stallion (model not recorded in #71); this pass `agent:k9dreamer/gpt-5` |
| Pools covered | `dlmm_3` STX/USDCx v1, `dlmm_14` STX/USDCx v2, `dlmm_1` sBTC/USDCx |
| KB state before → after | `d640f03` → this PR |
| Run by | planned_by + decided_by `operator`; executed_by `agent:k9dreamer/gpt-5`; reviewed_by `operator` (PR review) |

**Verification shape.** One isolated reader per campaign read the closeout transcript and local
artifacts. The orchestrator independently swept each sender's full campaign nonce range, included
failed transactions in gas, and paginated `/extended/v1/tx/events` through the terminal empty page.
All three published figures reconciled exactly; no correction comment was required.

## 1. Reconciliation across agents

| Claim | Agents/campaigns | Resolution | Evidence |
|---|---|---|---|
| Direct-read withdrawal arithmetic is required | Hex 004 + K9 007 | **LSN-0025 promoted active.** Hex supplied the paid indexed-reserve failure; 007 supplied the independent successful v2 execution using fresh per-bin direct reads and nonzero expected-side minimums. | [#71 review](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/71#issuecomment-5100023455), [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) |
| Repair audit history and failed-cycle budget are separate | Hex 004 + K9 007 | **Kept draft.** 007 made no repair attempt, so it did not exercise LSN-0026's failed-then-resolved promotion condition. | [#71](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/71), [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) |
| Alert-prescribed remedies require a fresh read | 006 + Hex 004 + 007 | **Two recurrences in this three-closeout corpus, one clean conformance.** 006 exposed a stale operator premise; Hex cancelled a retry after fresh reads; 007's fill alert correctly resulted in no action and no divergence. Across the full catalog LSN-0018 has three exercised campaign sources (#60/#67/#71), plus 007 conformance. | [#67](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/67), [#71](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/71), [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) |
| v1 was dead; screen the successor pool | 006 + 007 | **LSN-0023 promoted active.** The screen's first live use rejected the structurally drained v1 venue, checked router/live-flow evidence, and selected v2; 007 exited net +31.350775 STX realized-withdrawal. This confirms the screen, not a guarantee that every successor is profitable. | [#67](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/67), [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73) |

## 2. Fleet KPI roll-up

| KPI | Section | This period | Prior | Δ |
|---|---|---|---|---|
| Recurrence rate (target 0) | A | No repeated paid failure class across the three; LSN-0018 recurred as decision-quality evidence twice, without tuition | First DREAM: 2 paid recurrences | improved |
| Tuition cost per failure class | A | Hex indexed-reserve withdrawal abort: 0.05 STX; already captured by LSN-0025 | 0.35 STX in first DREAM period | lower |
| Incident → defense time | A | LSN-0025 direct-read builder existed before 007 and cleared its first independent live execution; cadence-race and alert-delivery defenses remain candidates | first period established gates after incidents | mixed |
| Unattended hours between interventions | B | 006: ~4d to operator early exit; 007: full 7d, zero interventions; Hex 004: one staged repair sequence | prior DREAM measured 27–111h stretches | 007 extends zero-touch evidence |
| Clean-exit rate | C | 3/3, DLP/direct position zero, chain-proven | 2/2 in first DREAM | held 100% |
| Novel-situation first-contact success **by model** | D | K9 007 static event-capture ladder: correct no-repair scope and clean exit; Hex model unrecorded, so no cross-model score is manufactured | K9 baseline 1/1 | K9 evidence +1; Hex n/a |
| Net vs hold after gas | E | 006 **+3.49 STX / +0.17%** realized-withdrawal; 007 **+31.350775 STX / +5.225%** realized-withdrawal; Hex 004 **+$0.11999420 / +0.4866%** high-confidence aggregate | first DREAM ≈ +$13.90 combined | all three positive; currencies not summed |

## 3. Memory deltas produced

| Delta | Type | Pages touched | Source issue(s) |
|---|---|---|---|
| LSN-0023 promoted — successor-pool screen first live use | enrich / promote | lessons, `dlmm_3`, `dlmm_14` | #67, #73 |
| LSN-0025 promoted — direct-read withdrawal arithmetic first independent successful execution | enrich / promote | lessons, `dlmm_1`, `dlmm_14` | #71, #73 |
| LSN-0027 created — terminal verifiers must cover scheduler cadence | new draft | lessons, `dlmm_14` | #73 |
| LSN-0028 created — sparse-pop ladder scaling is demand-limited and event-conditional | new draft | lessons, `dlmm_14` | #73 |
| `dlmm_14.md` created | new / ingest | pool page | #73 |
| LSN-0018/-0019 confirmations and LSN-0026 non-confirmation recorded | enrich | lessons, report | #67, #71, #73 |

## 4. New cross-campaign insights

- **Regime and posture are separate axes.** `whipsaw / trend / dead` remains the market-regime
  taxonomy. A static out-of-range ladder is an **event-capture posture**, not a fourth regime:
  007 spent long intervals out of range by design, then monetized sparse pop-through-and-return
  events. Calling every intentional OOR ladder a new regime would mix market behavior with strategy.
- **The successor-pool clause earned its first confirmation.** 006 identified v1 structural
  deadlock and required checking the newer venue; 007 selected the routed, live v2 successor and
  realized +5.225% after gas. LSN-0023 therefore graduates from a proposed screen to an exercised one.
- **Capital scaling is demand-limited, not gas-limited.** The 007 mid-campaign central estimate
  (+29.75 STX at 600) landed 5.1% below the realized +31.350775 STX, correctly identifying roughly
  two pop events and the sweep/churn mechanism. That is field support at **1× only** for LSN-0028;
  larger-size claims remain draft because no scaled campaign exercised them. The local simulation
  is neither cited nor reproduced.

## 5. Doctrine candidates (out of scope)

- Terminal closeout checkers should poll across a scheduler interval or run only after
  `planned_end + scheduler_period + margin` before declaring exit failure → closeout and unattended
  automation runbooks.
- Alert delivery needs a tested retry/queue path, and daily checkpoints need missed-run detection →
  unattended automation runbook.
- Promote the Agent Dreaming & Memory Guide `draft → active` in a **separate PR**. This second
  end-to-end pass is the requested promotion evidence.

## Confirmations

- [x] No secrets; only on-chain-public or operator-approved data; no wallet operation.
- [x] Every PnL figure carries a confidence label; display/DLP marks are not realized profit.
- [x] Every memory delta traces to a source issue; the `log.md` row matches the page diff.
- [x] The maintainer PR is left unmerged for operator review.
