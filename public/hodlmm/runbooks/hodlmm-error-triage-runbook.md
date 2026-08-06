---
name: HODLMM Error-Triage Runbook
type: runbook
handbook: v0.10
enforces: [INV-1, INV-3, INV-11]
skills: [query, bitflow]
status: draft
---

# HODLMM Error-Triage Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.10**.
> Enforces: INV-1, INV-3, INV-11.
> Source: [#89](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/89)
> (K9Dreamer, built from deployed contract source 2026-08-05; **draft until a live abort exercises
> the full path**).

## Purpose

Turn any failed DLMM v2 transaction — a broadcast rejection or an on-chain abort — into a named
root cause and the correct next action, in one lookup, without guessing.

## When to run / when NOT to run

- **Run when:** any DLMM v2 `contract_call` you signed returns an error, aborts on-chain
  (`abort_by_response` / `abort_by_post_condition`), or is dropped from the mempool; and as the
  **first step of every unattended-executor tick** (§4).
- **Do NOT run for:** stuck-`pending` transactions — that is nonce/fee territory; use the
  [Stuck-Transaction Runbook](hodlmm-stuck-transaction-runbook.md).

## 1. The contract map — which layer failed

The DLMM v2 suite splits one logical pool across four contracts. The error-code **prefix**
identifies the failing layer instantly:

| Prefix | Layer | Contract (mainnet) |
|---|---|---|
| `u1xxx` | **Core** — swap/add/withdraw/move logic | `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1` |
| `u2xxx` | **Swap router** | `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2` |
| `u3xxx` (+ `u1`–`u4`) | **Pool** — SIP-013 token + bin state (one per pool) | e.g. `SM1FKX….dlmm-pool-stx-usdcx-v-2-bps-10` |
| `u5xxx` | **Liquidity router** | `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-1` |

For any pool you have not worked before, discover its exact surface first (INV-3 — never assume
cached structure):

```
GET /v2/contracts/interface/{deployer}/{pool-contract}
GET /v2/contracts/source/{deployer}/{contract}?proof=0     # error constants live in the source
```

## 2. Decoder tables — code → constant → action

**Swap router (`u2xxx`)** — swap failures:

| Code | Constant | Action |
|---|---|---|
| u2001 | ERR_NO_RESULT_DATA | re-quote |
| u2002 | ERR_BIN_SLIPPAGE | re-quote with a fresh bin walk |
| u2003 | ERR_MINIMUM_RECEIVED | min-received too tight — recheck the pool's REAL fee (query `get-pool-for-swap`; pool names can understate it) and re-quote |
| u2004/u2005 | ERR_MINIMUM_X/Y_AMOUNT | min params wrong |
| u2006 | ERR_NO_ACTIVE_BIN_DATA | re-read pool state |
| u2007–u2011 | list/bin/step parameter errors | fix call construction |
| u2012 | ERR_DEADLINE_PASSED | retry with fresh deadline |

**Liquidity router (`u5xxx`)** — add-liquidity failures:

| Code | Constant | Action |
|---|---|---|
| u5001 | ERR_NO_RESULT_DATA | re-quote |
| u5002/u5003 | ERR_MINIMUM_X/Y_AMOUNT | min params wrong |
| u5004 | ERR_NO_ACTIVE_BIN_DATA | re-read pool state |
| u5005–u5007 | list/bin parameter errors | fix call construction |
| u5008 | ERR_ACTIVE_BIN_TOLERANCE | active bin moved between quote and mine — re-anchor offsets to the current active bin and retry |

**Core (`u1xxx`)** — the subset an LP agent can actually hit:

| Code | Constant | Action |
|---|---|---|
| u1001 | ERR_NOT_AUTHORIZED | wrong caller path |
| u1002 | ERR_INVALID_AMOUNT | fix amounts |
| u1010 | ERR_POOL_DISABLED | pool state changed — stop and re-screen liveness |
| u1016 | ERR_INVALID_TOKEN_DIRECTION | x/y swapped in the call |
| u1020/u1021 | ERR_INVALID_X/Y_AMOUNT | fix amounts |
| u1022/u1023 | ERR_MINIMUM_X/Y_AMOUNT | withdraw mins — this layer is why zero mins are rejected; use small nonzero mins |
| u1024 | ERR_MINIMUM_LP_AMOUNT | min-dlp too high for the fill |
| u1025/u1026 | ERR_MAXIMUM_X/Y_AMOUNT | max bounds breached |
| u1027 | ERR_INVALID_MIN_DLP_AMOUNT | fix min-dlp param |
| u1047 | ERR_NOT_ACTIVE_BIN | state changed — re-read |
| u1048 | ERR_NO_BIN_SHARES | bin already empty — rescan positions before retrying |

Codes u1004–u1015 and u1029–u1062 are pool-creation/admin/fee-management — if you hit one as an
LP agent, your call construction is wrong at a structural level; read the source.

**Pool (`u3xxx` + SIP-013 `u1`–`u4`)**: u1 INSUFFICIENT_BALANCE · u2 MATCHING_PRINCIPALS ·
u3 INVALID_AMOUNT · u4 NOT_AUTHORIZED · u3001–u3006 pool-level auth/amount/principal/token checks.

## 3. The two non-`uNNN` outcomes

- **`abort_by_post_condition`** — this is **your own deny-mode post-condition firing**, not a
  contract error. The contract logic may be fine (a probe that aborts here but simulates clean
  proves it). Fix the PC set, not the call: every asset leg needs a covering PC, including the
  **pool's own send** back to you.
- **`dropped_*`** — never mined; safe to rebuild and retry (mind the nonce).

## 4. The pendingTx guard — a returned txid is NOT success

An unattended executor that advances its state machine at broadcast time has a silent failure
mode: the tx aborts on-chain minutes later and every subsequent tick runs on a false premise —
no alert, no retry, wedged (see LSN-0032). Procedure, first thing every tick:

1. **At broadcast:** persist `pendingTx {txid, leg}` in the executor's state file.
2. **Next tick, before any new action, resolve it** (indexer `GET /extended/v1/tx/{txid}`):
   - `success` → clear `pendingTx`, proceed.
   - `pending`/indexer error → **hold: no new broadcasts this tick** (duplicate-broadcast guard —
     the same bins/funds must not be acted on twice while a tx is in flight).
   - `abort_by_response` → extract `(err uNNN)` from `tx_result.repr`, decode via §2, **revert the
     state machine to the failed leg's precondition**, refund any consumed budget counters
     (daily-cycle caps etc.), ledger the abort, alert with the decoded constant + action.
   - `abort_by_post_condition` → as above, but flag as own-PC bug (§3) — do not blind-retry.
   - `dropped_*` → revert phase; safe to retry.
3. **Alert with the decoded name and action hint, never the bare code** (INV-11: alerts must be
   actionable).

## Verification

- After any recovery action, re-read pool + wallet state fresh (INV-3) before the next attempt.
- A triaged abort must appear in the campaign ledger with its decoded cause; closeouts book its
  gas per the [PnL Runbook](hodlmm-pnl-runbook.md).

## Failure modes of this runbook

- Decoder tables go stale if Bitflow deploys new router/core versions — on any unmapped code or
  unfamiliar contract name, re-fetch the source (§1) rather than trusting these tables (INV-1:
  the chain is the authority).
- The `query` skill (or raw Hiro calls) is required for tx resolution; the `bitflow` skill's
  call construction is where most `u1016`/`u1020`-class errors originate — fix there.
