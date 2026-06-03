---
name: HODLMM Active LP Management Runbook
type: runbook
handbook: v0.6
enforces: [INV-1, INV-2, INV-7, INV-9, INV-10, INV-11, INV-12]
skills: [hodlmm-move-liquidity, hodlmm-bin-guardian, bitflow-hodlmm-deposit, bitflow-hodlmm-withdraw, bitflow-swap-aggregator, memory, cron]
status: active
---

# HODLMM Liquidity Management — Agent Operational Runbook

> **Purpose:** Instructions for an AI agent managing concentrated liquidity positions on Bitflow HODLMM (DLMM) pools via the Stacks blockchain.
>
> **Conforms to:** [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) v0.6 — enforces INV-1/2/7/9/10/11/12.
>
> **Author:** @k9dreamer_btc
>
> **Last updated:** 2026-05-29
>
> **Status:** Active — live run in progress

---

## Resources

| Resource | URL | Purpose |
|---|---|---|
| Skills Registry | https://www.bff.army/skills | Browse and deploy agent skills |
| Agent Dashboard | https://www.bff.army/agent-dashboard | Track on-chain agent activity |
| Build Course | https://www.bff.army/courses/build-your-first-bitcoin-ai-agent-in-10-Minutes | Launch a Bitcoin AI agent in 10 minutes |
| AIBTC Network Guide | https://aibtc.com/guide | Onboarding to the AIBTC agent network |
| Bitflow HODLMM App | https://app.bitflow.finance | Pool interface and position management |

---

## Core Concept

HODLMM liquidity is allocated to discrete **bins**. Each bin represents a narrow price range. The **active bin** is the bin currently processing swaps.

- If the active bin moves away from a position's bins, that position becomes **out of range**.
- Out-of-range liquidity is **idle** — tokens are held but not competing for trading flow or earning fees.
- The primary objective is: **keep useful liquidity near the active bin.**

---

## Control Loop

All liquidity management follows this loop. Execute steps in order. Do not skip steps.

```
SCAN → DECIDE → DRY-RUN → EXECUTE → VERIFY → REMEMBER → MEASURE
```

### Phase 1 — Read-Only (no signing, no broadcast)

| Step | Action | Output |
|---|---|---|
| **SCAN** | Fetch wallet positions, active bin, pool state | Position report with drift calculation |
| **DECIDE** | Compare drift to thresholds, evaluate pool health | Recommendation: hold / recenter / exit |
| **DRY-RUN** | Simulate the proposed move without broadcasting | Preflight report: target bins, token amounts, expected state |

### Phase 2 — Execution (requires approval)

| Step | Action | Output |
|---|---|---|
| **EXECUTE** | Broadcast the approved transaction | txid |
| **VERIFY** | Wait for confirmation, rescan position, confirm intended state achieved | Post-check report |

### Phase 3 — Learning

| Step | Action | Output |
|---|---|---|
| **REMEMBER** | Log the transaction, outcome, and any lessons to memory | Updated transaction ledger |
| **MEASURE** | Update performance ledger with exposure, fees, gas, mark-to-market | Updated performance ledger |

---

## Required Skills

| Skill | Function | Phase |
|---|---|---|
| `hodlmm-move-liquidity` | Scan positions, dry-run moves, execute recenters | Read-only + Execution |
| `hodlmm-bin-guardian` | Read-only guardrails and drift alerts | Read-only |
| `bitflow-hodlmm-deposit` | Add new liquidity to a pool | Execution |
| `bitflow-hodlmm-withdraw` | Remove liquidity / exit a pool | Execution |
| `bitflow-swap-aggregator` | Route and execute token swaps | Execution |
| `memory` | Persist decisions, outcomes, lessons across sessions | Learning |
| `cron` | Schedule recurring scans (default: every 6 hours) | Read-only |

---

## Rule: Fresh Scan Before Every Transaction

**This rule is mandatory. No exceptions.**

Active bins move continuously. A plan that was valid 20 minutes ago may be stale at broadcast time.

Before any transaction:

1. Scan wallet positions
2. Read current active bin
3. Calculate drift (active bin − nearest user bin)
4. Dry-run the target range
5. Only then decide whether to proceed

If the scan reveals the position is already in range, **do not transact.**

---

## Pool Selection Criteria

Before automating any pool, evaluate:

| Factor | Check | Action if failed |
|---|---|---|
| 24h volume | > 0 and meaningful relative to TVL | Do not automate — likely exit candidate |
| 24h fees | Fees being generated | Do not automate |
| TVL | Sufficient for position size | Evaluate slippage risk |
| Active bin movement | Bin is moving (pool is traded) | Do not automate if static |
| Existing wallet bins | Agent already has a position | Manage existing before adding new |
| Token exposure | Acceptable to the operator | Flag if outside tolerance |

**A stale pool with no volume is not a rebalance candidate. It is an exit candidate.**

---

## Approval Boundaries

The agent operates within an explicitly defined scope. Everything outside requires fresh human approval.

### Scope Definition Format

```
Pool:         [pool name and ID]
Duration:     [number of days]
Permissions:  [manage existing / add new / withdraw / swap]
Constraints:  [what is NOT allowed]
```

### Example

```
Pool:         STX / sBTC DLMM Bin Step 15 (dlmm_6)
URL:          https://app.bitflow.finance/pools/dlmm/dlmm_6
Duration:     4 days
Permissions:  Manage existing liquidity only
Constraints:  No new liquidity. No swaps. No other pools.
```

### Rules

- The agent **can** act within the defined scope without asking.
- The agent **must** request approval for anything outside the scope.
- If the scope expires (duration elapsed), all execution permissions revert. Read-only scanning continues.

---

## Ledgers

Maintain two separate ledgers. They answer different questions.

### Transaction Ledger — "What did we do?"

Record for every transaction:

| Field | Description |
|---|---|
| `timestamp` | When the action was taken |
| `intent` | What the agent was trying to achieve |
| `approval_scope` | The active approval scope at time of execution |
| `preflight` | Position state before the transaction |
| `txid` | On-chain transaction identifier |
| `status` | confirmed / failed / pending |
| `post_check` | Position state after confirmation |
| `lesson` | What was learned (especially on failure) |

### Performance Ledger — "Is this working?"

Track over time:

| Metric | Description |
|---|---|
| `token_exposure` | Current token balances in the position |
| `dlp_bin_state` | Which bins hold DLP tokens and their amounts |
| `active_bin_drift` | Distance between active bin and nearest user bin |
| `pool_apr` | Current pool APR and fee rate |
| `gas_paid` | Cumulative gas spent on rebalances |
| `mark_to_market` | Current USD value of the position |
| `fee_attribution` | Confidence level that observed gains are from fees vs price movement |

**DLP balance is not the same as earned fees. Do not conflate them. Do not report fake PnL.**

---

## Default Monitoring Loop

Runs on cron. **Read-only. No signing. No broadcast.**

**Frequency:** Every 6 hours

**Steps:**

1. Scan all HODLMM positions in the wallet
2. For each position:
   - Read active bin
   - Calculate drift
   - Flag if out of range
3. If any position is out of range:
   - Prepare a dry-run move plan
   - Alert the operator
4. If all positions are in range:
   - Log the scan result
   - No alert needed

**This loop never executes transactions.** It only observes and alerts.

---

## Recenter Decision Logic

When a position is flagged as out of range:

```
IF drift > threshold AND pool is active AND approval scope is valid:
    → dry-run recenter
    → present plan to operator (or auto-execute if within scope)

IF drift > threshold AND pool is NOT active (no recent volume):
    → recommend EXIT, not recenter

IF drift <= threshold:
    → hold, do nothing

IF approval scope is expired:
    → alert operator, request new scope
```

### Recenter Constraints

- **Recenter existing liquidity only.** Do not add new capital during a recenter unless explicitly approved.
- **Respect cooldowns.** Do not recenter the same pool within the cooldown window unless the operator overrides.
- **Managing existing capital is not the same as increasing exposure.** These are separate decisions requiring separate approvals.

---

## Post-Transaction Verification

**Mandatory after every broadcast. No exceptions.**

1. Verify tx status on-chain (confirmed / failed)
2. Wait for confirmation (do not assume success from broadcast)
3. Rescan the position
4. Compare actual state to intended state
5. Log the result to the transaction ledger

**A successful transaction does not guarantee the strategy outcome is correct.** The post-check is where you confirm that.

If actual state ≠ intended state → log as anomaly, alert operator.

---

## Cooldown Policy

| Scope | Default Cooldown | Override |
|---|---|---|
| Same-pool recenter | 6 hours minimum | Operator can override with explicit approval |
| Cross-pool moves | No default cooldown | Subject to approval scope |
| Emergency exit | No cooldown | Always allowed |

Frequent rebalancing incurs gas costs and potential churn. **The goal is not maximum activity. The goal is profitable, controlled activity.**

---

## Memory Requirements

The agent must persist the following across sessions:

| Memory Item | Why |
|---|---|
| Which pools were stale | Avoid rebalancing dead pools |
| Which API calls were flaky | Retry logic, fallback behavior |
| Which moves reduced drift effectively | Improve future recenter targeting |
| Which transactions failed | Avoid repeating known-bad patterns |
| What the operator approved | Stay within scope |
| What the operator rejected | Do not re-propose without new information |
| Lessons from post-checks | Improve verification accuracy |

**Without memory, every rebalance is a cold start.** Memory is what turns a script into an operating system.

---

## Summary

HODLMM management is not a single DeFi action. It is an **operating system for liquidity.**

| Layer | Function |
|---|---|
| **Skills** | Execute on-chain actions |
| **Memory** | Preserve judgment across sessions |
| **Ledgers** | Maintain audit trail and performance tracking |
| **Approval scopes** | Bound agent authority |
| **Monitoring loop** | Continuous read-only observation |
| **Post-checks** | Verify outcomes match intent |

**The agent advantage is not magic. It is continuous attention.**

---

*Built on [Bitflow HODLMM](https://app.bitflow.finance) · Stacks · sBTC*

*Maintained by [@k9dreamer_btc](https://x.com/k9dreamer_btc)*
