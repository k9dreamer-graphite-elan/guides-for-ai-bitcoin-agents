# HODLMM Agent Handbook — Community Edition

> **Community Edition · v0.7.** A public, agent-first guide to trading and providing liquidity on Bitflow **HODLMM** (DLMM) concentrated-liquidity pools on Stacks, *safely*.
> **Not financial advice. Mainnet only — real funds are at risk.** Provided "as is", without warranty. **Verify every address, entrypoint, and limit on-chain before signing** — this is a guide, not an oracle.
> **Scope:** covers public contracts and APIs only. Bitflow internal infrastructure, operational endpoints, and incident runbooks are intentionally omitted.
> **Read Chapter 0 before any autonomous trade or LP action — it is the safety floor.**

This handbook is an agent-first operating manual: brakes first, then reference, then procedures, then recovery, then alpha. Every HODLMM skill and every autonomous run should *import* Chapter 0 rather than re-deriving its own assumptions. Chapter numbers follow priority: the safety floor (0–3) precedes strategy (4) and the supervision/accountability overlays (5–8).

---

## The Operating Loop (the frame)

All HODLMM agent activity runs inside one seven-phase loop. Phases are sequential. **No phase may be skipped.** The loop is the standard HODLMM liquidity-management discipline; the contract-level invariants underneath `EXECUTE` are this handbook's contribution.

```
read-only   :  SCAN  ->  DECIDE  ->  DRY-RUN
execute     :  EXECUTE  ->  VERIFY
learn       :  REMEMBER  ->  MEASURE
```

| Phase | Output | Chapter 0 gate that applies |
|---|---|---|
| SCAN | fresh wallet positions, active bin, drift, pool health | INV-7 (fresh scan), INV-8 (per-bin) |
| DECIDE | intent + chosen skill + approval-scope check | INV-1 (scope), INV-9 (pool not stale) |
| DRY-RUN | simulated range / quote, projected reads, post-conditions | INV-2..INV-6 (execution safety) |
| EXECUTE | signed, broadcast tx | all execution invariants enforced |
| VERIFY | on-chain confirmation + state re-scan | INV-10 (no assumed success) |
| REMEMBER | ledger write + memory update | INV-11 (ledgers), INV-12 (memory) |
| MEASURE | fee attribution, mark-to-market | INV-8 (DLP ≠ fees) |

---

## Chapter 0 — Invariants & Pre-Flight

These are non-negotiable. A run that violates any `INV` rule is a **defect**, regardless of whether it happened to make money.

### Hard invariants

**INV-1 — Act only inside an explicit Approval Scope.**
A scope defines: pool(s) + ID, duration (days), permissions (`manage-existing` / `add-new` / `withdraw` / `swap`), and constraints (what is prohibited). `MUST NOT` sign any transaction outside the active scope. Expired scope → execution permission reverts to **read-only**; scanning continues; request re-approval. Anything ambiguous → escalate to a human, do not infer authority.

**INV-2 — NEVER broadcast without the correct fund-protection for the operation type.**
Funds are protected by what you sign — and the right form depends on the operation. Using the wrong form, or none, discards the safety model. There are **two forms**:
- **Swaps →** sender-side Clarity post-conditions in `PostConditionMode.Deny`: `max-in` on the token sent, a real `min-out`/`min-dy` on the token received (**never `u1`**). The `POST /swap` endpoint (§1.4) generates these — use them, do not strip them.
- **LP add / move / withdraw →** HODLMM mints **and** burns DLP tokens in the same tx, which **cannot** be expressed as sender-side post-conditions. Protection moves into the contract-call arguments and runs in `PostConditionMode.Allow`: `min-dlp` (≥ ~95% of expected DLP shares back), `max-x-liquidity-fee` / `max-y-liquidity-fee` (cap the active-bin liquidity fee, ~5%), and an active-bin deviation tolerance that aborts if the active bin moved. A violated bound **reverts on-chain**.

`MUST NOT` broadcast a swap without Deny-mode post-conditions; `MUST NOT` broadcast an LP op without those contract-level bounds set. "I'm in Allow mode" is only acceptable for LP ops *with* the bounds, never for swaps.

**INV-3 — Use bounded swap entrypoints. This is the #1 footgun.**
Stacks blocks have a hard **~15,000 storage-read ceiling** (a network constant; budget under it, don't depend on the exact value). The classic unbounded entrypoints `swap-x-for-y-simple-multi` / `swap-y-for-x-simple-multi` `fold` over 319 steps (`MAX_STEPS = 319`); worst case `3 + 319×52 = 16,591` reads — **over the ceiling by design**. When exceeded, the tx pays its fee, **passes broadcast**, then fails only at mining time (`CostBalanceExceeded` → dropped per-miner) and can sit `pending` indefinitely.
- `MUST` call `swap-x-for-y-simple-range-multi` / `swap-y-for-x-simple-range-multi` on `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2` with `max-steps ≈ 230` → worst case `3 + 230×52 = 11,963` reads (~80% of ceiling, margin for variance).
- `MUST` set a meaningful `min-dy` (not `u1`) **or** read the `{in, out}` return and follow up on the residual against refreshed pool state. Ignoring the residual defeats the entrypoint's purpose.
- `MUST` recompute cost between legs of a multi-leg route.

**INV-4 — The cost estimator is a hint, not an admission oracle.**
The public fee/cost estimator reports directionally, not precisely (observed ~6% optimistic at the worst tail: ~14,070 reads reported for a tx that consumed 15,003). `MUST NOT` gate broadcast on "estimator < 100%." Gate on a conservative budget: **target estimated reads `< 12,000`**, and still treat the number as advisory. This budget is also why the exact block ceiling (≈15,000) is non-load-bearing — you stay under it regardless.

**INV-5 — Capping swap size is NOT a cost fix.**
Read cost is dominated by pool *shape* (how many active bins the fold traverses), not notional. On a wide pool the estimator returns similar reads for very different sizes. The lever is **traversal depth (`max-steps`)**, never order size. Do not "make it safe" by shrinking the order.

**INV-6 — Respect the stuck-nonce blast radius.**
Stacks enforces strict per-sender nonce order. One tx stuck behind INV-3 stalls **every** later tx from that signer. `MUST` serialize nonces (a cross-process nonce oracle / `nonce-manager`-class skill) to prevent mempool collisions. Canonical unstick for an already-stuck head nonce: a 1 µSTX self-transfer at that nonce with bumped fee (RBF). Custody that doesn't expose RBF ergonomically makes this harder — know your signer's RBF story *before* you broadcast. (Recovery procedure in Ch.3.)

**INV-7 — Fresh scan before every broadcast.**
Active bins move continuously. A plan valid 20 minutes ago may be stale at signing time. Before `EXECUTE`: re-scan positions + active bin, recompute drift, re-simulate the target range, and confirm the action is still warranted. A stale plan `MUST` be re-derived, not broadcast. Quotes can serve **stale data silently** when indexing lags — corroborate with the freshness/lag check (§1.4).

**INV-8 — Per-bin accounting; and DLP balance ≠ earned fees.**
LP positions are stored per `(user, bin_id)` — a 50-bin position is 50 map entries. `MUST NOT` write logic that assumes one position per `(user, pool)`; it will under-count. Provider + variable fees accrue *inside the bin* (auto-compounding into `x_balance`/`y_balance`); protocol fees are a separate, permissionless claim that dispatches to a contract-registered fee address, not to you. When reporting performance, `MUST` separate mark-to-market DLP value from attributed fee income — never conflate them.

**INV-9 — A stale pool is an exit candidate, not a rebalance candidate.**
Before automating a pool, confirm: meaningful 24h volume, fees actually generating, TVL sufficient for position size, active bin moving, token exposure acceptable. If a position has drifted out of range in a pool with no volume → recommend **exit**, not recenter. Recenter existing liquidity only; `MUST NOT` add new capital during a recenter unless the scope explicitly grants `add-new`.

**INV-10 — A confirmed transaction does not mean a correct outcome.**
After every broadcast: verify on-chain status, wait for confirmation (never assume success), re-scan the position, diff actual vs intended state, log anomalies. Treat partial fills (INV-3) as expected, not exceptional.

**INV-11 — Write both ledgers, every action.**
*Transaction Ledger*: timestamp, intent, approval scope, preflight state, txid, status, post-check state, lesson. *Performance Ledger*: token exposure, bin state, drift, pool APR, cumulative gas, mark-to-market, fee-attribution confidence. No silent actions.

**INV-12 — Persist memory across runs.**
Retain: stale-pool IDs, flaky API patterns, effective recenter targeting, failed-tx patterns, operator approvals/rejections, post-check lessons. Without memory, every rebalance is a cold start.

**INV-13 — Gate every write on the divergence & feed-safety tier.**
Before any write, classify the pool from the active-bin-vs-external divergence `d = (p − external)/external`
and feed health into one of three tiers:
- **aligned** (`|d| ≤ d_warn`, feed fresh, no peg break) → normal operation.
- **defensive** (`d_warn < |d| ≤ d_halt`, or feed stale below the halt age, or the lag case below) →
 force conservative params (max width, min size) and **mark inventory at the external price** — the
 active bin is the suspect quantity, not the fair one.
- **abnormal** (`|d| > d_halt`, any peg break, feed lost, or pool frozen) → **halt.** A broken-*market*
 halt (peg / `|d|`) withdraws to reserve but **holds inventory — never blind-swap into untrustworthy
 prices**; an *operational* halt (feed lost / pool frozen) withdraws and stops.

Load-bearing rules:
- **Ordering invariant `d_warn < d_halt` MUST always hold.** The *divergence* halt **scales** with
 volatility (`d_halt = max(halt_floor, k·σ)`) and `d_warn = k'·σ`; a vol spike can otherwise invert the
 bands and erase the defensive tier — clamp `d_warn` if so.
- The **peg band is a separate, FIXED, absolute threshold** — a depeg is a different event from
 pool/feed divergence and does not scale.
- **A cash- or wrapped-leg depeg cannot be detected from the volatile-asset/USD feed alone.** Independent
 references (cash-vs-USD, wrapped-vs-underlying) are required inputs, not optional.
- **Feed lag vs decoupling:** a large `|d|` with high `σ`, a stale feed, and a coherently advancing
 active bin is *feed lag* → **defensive**, not halt. A large `|d|` with a *fresh* feed, or an active
 bin sitting in a thin/empty region (it may have been walked across empty bins for gas — §1.3), is
 *decoupling/manipulation* → **halt**.
Procedure: `hodlmm-divergence-safety-runbook`.

### Ground-truth facts every HODLMM agent shares

- **Mainnet-only.** HODLMM has no testnet deployment. Do not branch on network.
- **No admin backdoors, no oracle dependency.** Contracts have no fund-admin key and no price oracle. Security comes from post-conditions / contract-level bounds + the 2-week core-migration cooldown + pool code-hash verification, not from a trusted operator.
- **Bins:** 1,001 per pool, indexed -500..+500, center 500. `bin_factor` is fixed at pool creation; only reserves move. Above active = Y only, below active = X only, at active = both (imbalanced adds taxed at swap rate).
- **Fee exemptions exist** per-address per-pool. If reconciling expected vs actual fees, check the `fee-exemptions` map first — it's policy, not a constant.
- **Live state is never cached here.** Pool list, TVL, active-bin-id → query on-chain or the public Bitflow API.

### Pre-flight checklist (the GATE before EXECUTE)

Run top to bottom. Any `NO` aborts the broadcast.

```
[ ] Active Approval Scope covers this pool + this action type?        (INV-1)
[ ] Fresh scan < this loop iteration; drift/range re-simulated?       (INV-7)
[ ] Pool passes liveness (volume/fees/TVL/active-bin moving)?         (INV-9)
[ ] Swap uses *-simple-range-multi with max-steps <= 230?             (INV-3)
[ ] Estimated reads < 12,000 (treated as advisory, not a gate)?       (INV-4)
[ ] Swap: Deny-mode post-conditions — max-in + real min-out (not u1)? (INV-2)
[ ] LP op: min-dlp + liquidity-fee caps + active-bin deviation set?   (INV-2)
[ ] Bounded/partial-fill residual handled?                           (INV-3)
[ ] Nonce serialized; signer RBF path known?                          (INV-6)
[ ] LP add: not adding new capital outside scope; active-bin tax ok?  (INV-9/2)
[ ] Ledger entry prepared; post-check + memory write planned?         (INV-10/11/12)
[ ] Divergence/feed tier = aligned (or defensive params applied); not abnormal (INV-13)
```

### Approved skill map (use these, by their registry names)

The approved skills published at **aibtc.com/skills**:

| Need | Skill |
|---|---|
| Scan / simulate / execute LP recenter | `hodlmm-move-liquidity` |
| Read-only LP guardrails | `hodlmm-bin-guardian` (read-only) |
| Token routing / aggregated swaps | `bitflow` |
| Cross-protocol position summary (HODLMM, Zest, ALEX, Styx) | `defi-portfolio-scanner` |
| Idle-sBTC yield routing (Zest vs HODLMM APR) | `sbtc-yield-maximizer` |
| Nonce safety (INV-6) | `nonce-manager` |
| Capital in/out | `bitflow-hodlmm-deposit` / `bitflow-hodlmm-withdraw` |
| Wallet / signing / balances | `wallet`, `signing`, `stx`, `sbtc`, `tokens`, `query` |
| Persistence | `memory`, `credentials` |

---

## Chapter 1 — Canonical Reference

The fleet's single source of record. Cite this; do not re-derive. Constants are point-in-time — re-verify on-chain before asserting in a tx (INV-4 discipline applies to facts too). Anything that moves (pool list, TVL, active bin, fees actually configured) is **not** recorded here — query it live.

### 1.1 Mainnet addresses (verified on-chain April 2026 — re-verify before signing)

**Two deployers** (a frequent source of confusion):

| Principal | Role |
|---|---|
| `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA` | DLMM **core** deployer |
| `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD` | DLMM **routers + pools** deployer |
| `SM1793C4R5PZ4NS4VQ4WMP7SKKYVH8JZEWSZ9HCCR` | XYK / Stableswap / Keeper deployer (legacy plane) |

Canonical HODLMM contracts:

| Contract | Full ID |
|---|---|
| Core | `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1` |
| Swap Router v1.2 (latest) | `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2` |
| Liquidity Router v1.2 (latest) | `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-liquidity-router-v-1-2` |
| Router v1.1 (superseded; some skills still call it) | `…dlmm-swap-router-v-1-1` / `…dlmm-liquidity-router-v-1-1` (under `SM1FKX…`) |

Per-pool contracts (`dlmm-pool-{pair}-…`) deploy under `SM1FKX…`; resolve a specific pool's contract from a live `GET /pools/{pool_id}` (the `pool-contract` field) rather than hardcoding. Confirm any contract on-chain via Hiro `GET /v2/contracts/interface/{principal}/{name}` before constructing a call. Protocol-fee claims dispatch to a contract-registered fee address — **not an agent concern** (Ch.5 §5.2).

### 1.2 Contract map — five types per pool

| Contract | Role | Agent touches it for |
|---|---|---|
| `dlmm-core-v-1-1` (`SP1PFR4V08…`) | Singleton. Swap logic, pool creation, fee exemptions, protocol-fee claims. | quoting truth, fee-exemption checks |
| `dlmm-pool-{pair}-v-1-1` (`SM1FKX…`) | Per-pool. Reserves, `balances-at-bin`, `user-balance-at-bin`, `active-bin-id`. SFT (SIP-013) + vault. | position reads (per-bin, INV-8) |
| `dlmm-swap-router-v-1-2` (`SM1FKX…`) | Bounded + classic multi-bin swap routing. | **all swaps — use bounded entrypoints (INV-3)** |
| `dlmm-liquidity-router` (v-1-2 latest; v-1-1 still in skill use) | Multi-bin add/withdraw, relative positioning + tolerance. | LP add / withdraw / recenter |
| `dlmm-staking-{pair}-v-1-1` | Per-pool staking, per-bin reward-per-block, 50 BPS early-unstake fee. | staking LP shares for reward yield |

Plus traits `dlmm-core-trait`, `dlmm-pool-trait`, `dlmm-staking-trait`. Only `dlmm-core-v-1-1` can move tokens across pools — this is what preserves post-condition atomicity.

### 1.3 Entrypoints an agent may call

**Swaps — bounded only (INV-3):**
- `swap-x-for-y-simple-range-multi` / `swap-y-for-x-simple-range-multi` on `dlmm-swap-router-v-1-2`, `max-steps ≈ 230`, meaningful `min-dy`, handle the `{in, out}` residual.
- Classic `*-simple-multi` exist but are `NEVER` to be used on pools that can drift wide (319-step fold, worst 16,591 reads > ceiling).

**Liquidity — `dlmm-liquidity-router` (v-1-2 latest; v-1-1 still used by current skills):** multi-bin add (`add-relative-liquidity-same-multi`; above active = Y only, below active = X only, at active = both & taxed at swap rate), withdraw, atomic recenter (`move-relative-liquidity-multi`), relative-offset positioning with tolerance checks.

**Staking — `dlmm-staking-{pair}-v-1-1`:** lock per-bin SFT shares, accrue per-block rewards, unstake (50 BPS fee if early-unstake enabled).

**Fees:** `claim-protocol-fees` on `dlmm-core-v-1-1` is **permissionless** but dispatches to a contract-registered fee address — calling it does not pay *you*. Provider + variable fees are not claimed; they auto-compound inside the bin (INV-8).

### 1.4 Quote → swap path (where post-conditions come from)

DLMM is the fast quote plane; the legacy plane (XYK/Stableswap/cross-DEX) is separate and **cannot compose atomically** with DLMM in one tx.

Base: the public Bitflow quotes API — `https://bff.bitflowapis.finance/api/quotes/v1/`

| Step | Call | Returns |
|---|---|---|
| Quote | `POST /quote` (best) / `POST /quote/multi` (all routes) | `amount_out`, `min_amount_out`, `slippage_tolerance`, `price_impact_bps`, `route_path`, `execution_path` |
| Build tx | `POST /swap` (feed the `execution_path`) | contract-call params, typed args, **post-conditions** (the INV-2 *swap* form) |
| Explore | `GET /pools`, `/pools/{id}`, `/bins/{pool}`, `/bins/{pool}/active`, `/bins/{pool}/{bin}`, `/pairs?input_token=`, `/tokens` | live pool/bin/token state |
| Positions | `GET /users/{address}/positions/{pool_id}/bins` | per-bin LP position (INV-8) |
| Freshness | the indexer-lag check | indexing vs canonical chain tip; lag ⇒ suspect stale |

Strategies the engine returns: `single_bin` (fits one bin, ~0 impact) · `multi_bin` (one-pool bin traversal) · `v1_split` (splits pools; may return max-available, not just requested). Empty `execution_path` ⇒ no DLMM pool for the pair; fall back to the legacy plane.

> Quotes can serve **stale data silently** when indexing lags — they do not error. This is why INV-7 (fresh scan) and the lag check exist. Do not assume the API rate-limits you — **self-throttle**.

### 1.5 Traversal & cost limits (distinct layers — do not conflate)

| Layer | Limit | Where |
|---|---|---|
| Quote engine bin traversal | 200 bins / direction (`max_bin_traversal`) | quote engine, off-chain |
| On-chain swap-router cap | ~350–384 bins / call (approximate, non-load-bearing) | dlmm contracts |
| Classic `*-simple-multi` fold | `MAX_STEPS = 319` (worst 16,591 reads) | dlmm-swap-router |
| Safe bounded budget | `max-steps = 230` (~11,963 reads) | your call site (INV-3) |
| Block read ceiling | ~15,000 reads (Stacks network constant) | Stacks VM (INV-3/4) |

> The absolute on-chain cap (≈350–384) and the exact block read ceiling (≈15,000) are **approximate and non-load-bearing** — your `max-steps ≤ 230` / `< 12,000`-read budget sits safely under all candidate values, so an agent never needs the precise figure. Size `max-steps` from INV-3, not from the quote engine's traversal count.

### 1.6 Fee model

Three fee types, configured **per-pool, per-direction** (X and Y independent):

| Fee | Destination | Claimed? |
|---|---|---|
| `protocol-fee` | Bitflow treasury (a contract-registered fee address) | permissionless `claim-protocol-fees` (dispatches there, not to you) |
| `provider-fee` | LP yield, accrues into the bin's reserves | no — auto-compounds (INV-8) |
| `variable-fee` | dynamic, `variable-fees-manager` (bin-change-count + cooldown; freezable) | no — auto-compounds |

Fee **exemptions** are per-address per-pool (`fee-exemptions` map on `dlmm-core-v-1-1`). Check before reconciling expected vs actual fees — it's policy, not a constant. Configured fee *rates* are mutable pool state — read them live, don't hardcode.

### 1.7 Hard boundaries

- **DLMM ↔ legacy do not compose atomically.** No single Clarity tx crosses the DLMM swap router and the XYK swap-helper. Plan each plane separately.
- **Keeper has no DLMM action.** Only `keeper-action-1/2/3` (XYK/Stableswap) exist; DLMM DCA/limit orders are unsupported and throw. Do not promise limit/DCA on HODLMM today.
- **Live state is never recorded in this handbook.** Pool list / TVL / active bin / configured fee rates → query the quotes API live.

> Source of truth: the on-chain DLMM contract source + the public Bitflow quotes API.

---

## Chapter 2 — Playbooks

Three procedures cover almost everything an agent does on HODLMM: **trade**, **provide LP**, and **manage a range**. Each is the same loop — `SCAN → DECIDE → DRY-RUN → EXECUTE → VERIFY → REMEMBER → MEASURE` — with Chapter 0 gates attached and a specific approved skill doing the on-chain work.

### 2.0 Conventions that apply to every playbook

- **Read-only stages never sign.** `doctor` / `scan` / `quote` / `status` / `plan` are safe to run with no write authority. Only the explicit-confirm step broadcasts.
- **Skills are dry-run by default.** Execution requires a deliberate confirm token — `--confirm` (move), `--confirm=DEPOSIT`, `--confirm=SWAP`. No token ⇒ you get a plan, not a tx.
- **Post-conditions have two forms — see INV-2.** Swaps → `PostConditionMode.Deny` + `min-out`. LP add/move/withdraw → `PostConditionMode.Allow` + contract-level bounds (`min-dlp`, `max-x/y-liquidity-fee`, active-bin deviation). Wrong form = unsafe.
- **Always:** serialize the nonce (INV-6), re-scan immediately before signing (INV-7), verify mined `success` after (INV-10), write both ledgers (INV-11).

### Playbook A — Trade safely (swap)

**Goal:** exchange one token for another without blowing the read ceiling or stripping slippage protection.
**Primary skill:** `bitflow` / `bitflow-swap-aggregator` (route-aware, handles post-conditions).
**Direct-DLMM path:** if you bypass the aggregator and call the pool directly, INV-3 is mandatory.

| Loop phase | Action | Gate |
|---|---|---|
| SCAN | `doctor --wallet <addr>`; `tokens --search <sym>` to resolve token IDs | INV-1 (scope includes `swap`) |
| DECIDE | `quote --token-in <id> --token-out <id> --amount-in <n>` → review route, `amount_out`, price impact | INV-7 (fresh quote), INV-4 (est. reads < 12k) |
| DRY-RUN | `plan --wallet <addr> …` → inspect contract/function, route, **post-conditions**, safety gates | INV-2 (Deny + min-out present) |
| EXECUTE | `run … --confirm=SWAP` | INV-3 (direct DLMM: `*-simple-range-multi`, `max-steps ≤ 230`, real `min-dy`), INV-6 (nonce) |
| VERIFY | skill waits for status; **blocks unless mined status = `success`** | INV-10 |
| REMEMBER / MEASURE | record txid, in/out, price impact, gas to the Transaction + Performance ledgers | INV-11 |

**Notes**
- The aggregator goes through Bitflow's SDK route surface and may pick DLMM or legacy — it does *not* make custom direct-pool DLMM calls. It abstracts INV-3 for you. If you build a direct DLMM swap, **you** own INV-3: bounded entrypoint, `max-steps ≤ 230`, meaningful `min-dy`, and follow up on the `{in, out}` residual (§1.3, §1.5).
- The aggregator requires the wallet to already hold the input asset.

### Playbook B — Provide LP & earn fees

**Goal:** place liquidity in productive bins and earn fees, then (optionally) stake for reward yield.
**Primary skill:** `bitflow-hodlmm-deposit` (proof path `add-relative-liquidity-same-multi`).
**Staking:** `dlmm-staking-{pair}-v-1-1` (§1.3) for reward-token yield on LP shares.

**Placement rules (non-negotiable, §1.2 / INV-8):**
- **Below** active bin → token **Y only**. **Above** active → token **X only**. **At** active → one- or two-sided, and the imbalanced portion is **taxed at the swap rate**.
- Position is **per-bin** — a range of N bins is N position entries (INV-8).

| Loop phase | Action | Gate |
|---|---|---|
| SCAN | `doctor --wallet <addr> --pool-id <id>` → router/token/balance/gas/pending checks | INV-1 (scope includes `add-new`), INV-9 (pool liveness: volume/fees/TVL/active-bin moving) |
| DECIDE | choose range via one selector: `--offsets -1,0,1` / `--range -2:2` / `--bin-ids` / `--plan-json`; default = active bin | INV-9 (don't fund a stale pool) |
| DRY-RUN | `status … --amount-x <n> --amount-y <n>` → preview bins, offsets, **min-dlp, fee bounds**, balance needs, active-bin tolerance | INV-2-LP (bounds set), INV-7 (active bin fresh) |
| EXECUTE | `run … --confirm=DEPOSIT` (re-checks live state, then broadcasts) | INV-6 (nonce), `--active-bin-max-deviation` (default 0 = exact match) |
| VERIFY | wait for inclusion; re-read positions `GET /users/{addr}/positions/{pool}/bins` | INV-10, INV-8 (per-bin) |
| REMEMBER / MEASURE | log deposited bins + DLP minted; track DLP value **separately** from earned fees | INV-8 (DLP ≠ fees), INV-11 |

**Width is a strategy choice (deepened in Ch.4):** narrower range = more fee share but faster drift out of range; wider = more durable but diluted. Start modest around the active bin; let Ch.4 tune it against flow toxicity / bin velocity.

**Earning & staking**
- Provider + variable fees **auto-compound inside the bin** — there is no claim step; your bin reserves grow (INV-8). Protocol fees are not yours.
- To stack reward-token yield, stake LP (SFT) shares into `dlmm-staking-{pair}-v-1-1`. Early unstake costs **50 BPS** if enabled. Staked shares are committed — factor that into exit planning.

### Playbook C — Manage / recenter a range

**Goal:** keep liquidity near the active bin so it keeps earning, or exit if the pool is dead.
**Primary skill:** `hodlmm-move-liquidity` — one **atomic** `move-relative-liquidity-multi` (withdraw old bins + deposit around active in a single tx; all-or-nothing, no partial-execution risk).

**Decision tree (per position):**
```
scan → compute drift (bins between active and your nearest bin)

drift ≥ threshold  AND pool active   AND scope valid     → DRY-RUN, then recenter
drift ≥ threshold  AND pool STALE (no volume)            → EXIT, do NOT recenter        (INV-9)
drift < threshold                                        → HOLD
scope expired                                            → read-only; request re-approval (INV-1)
```

| Loop phase | Action | Gate |
|---|---|---|
| SCAN | `scan --wallet <addr>` → per-pool in-range / bin range / active bin / drift | INV-7, INV-8 |
| DECIDE | apply the tree; pick `--spread` (±N around active, default 5, max 10) | INV-9, INV-1 (`manage-existing`) |
| DRY-RUN | `run --wallet <addr> --pool <id>` → preview plan (old_range → new_range, per-bin moves, gas) | INV-2-LP (min-dlp ≥95%, fee cap 5%) |
| EXECUTE | `run … --confirm` (signer unlocked via env, never argv) | INV-6 (nonce); **4-hour per-pool cooldown** enforced & persisted |
| VERIFY | re-`scan`; confirm mined `success` and new range straddles active | INV-10 |
| REMEMBER / MEASURE | log move, txid, new range; remember effective targeting + cooldown | INV-11, INV-12 |

**Constraints**
- **Recenter existing liquidity only.** Do **not** add new capital during a recenter unless the scope grants `add-new` (INV-9).
- **Cooldown:** 4 h per pool (skill-enforced). A move blocked by cooldown returns a `blocked` status with minutes remaining — that is expected, not an error.
- **Autonomous mode** (`auto`): monitors all pools on an interval (default 15 min, min 5) and moves when drift ≥ threshold (default 3 bins). Opt-in by the operator starting it; still bound by scope, cooldown, and all gates. Use `--once` for a single supervised cycle first.

### 2.x Failure branches (→ Chapter 3)

| Symptom | Immediate read | Handling |
|---|---|---|
| Swap broadcast but stuck `pending` | INV-3/INV-6 | Wrong entrypoint or blown read budget; unstick head nonce (RBF), migrate to `*-simple-range-multi`. |
| Swap returned partial fill | INV-3 | Expected with bounded swaps — follow up on the `{in, out}` residual vs refreshed state. |
| Move/deposit `blocked` (cooldown / confirmation) | Playbook C / 2.0 | Not an error. Wait out cooldown or re-run with the confirm token. |
| Active bin moved before broadcast | INV-7 | `--active-bin-max-deviation` aborted it; re-scan and re-plan. |
| Position shows old values after confirm | INV-10 | Indexing latency; re-read positions after lag clears, don't double-act. |

Full recovery procedures live in **Chapter 3 — Failure Modes & Recovery**.

---

## Chapter 3 — Failure Modes & Recovery

When a protection trips or the network misbehaves, recover **deterministically**, not by improvising. This chapter is agent-facing (what *you* do), distinct from the operator overlay in Ch.5. **A recovery action is still a broadcast** — the Chapter 0 pre-flight GATE applies to it too. Default posture on uncertainty: stop and escalate (§3.6), never double-broadcast.

### 3.1 Triage table

| # | Symptom | Likely cause | Recovery | Enforces |
|---|---|---|---|---|
| R1 | Swap fee-paid but stuck `pending` indefinitely | Unbounded `*-simple-multi` blew the ~15k read ceiling; dropped at mining time | §3.2 RBF unstick + re-issue as `*-simple-range-multi` (`max-steps ≤ 230`) | INV-3/6 |
| R2 | Every new tx from the signer stalls | Stuck **head** nonce; strict per-sender ordering | §3.2 unstick the head nonce first; serialize nonces | INV-6 |
| R3 | Swap returned a partial fill (`{in,out}` < requested) | Bounded entrypoint hit `max-steps`, or sparse bins | §3.3 follow up on residual vs refreshed state | INV-3/10 |
| R4 | Quote looks wrong / price off, multiple attempts | Quote served **stale** (indexing lag); never errors | §3.4 check freshness/lag; wait or refresh, do not act on stale | INV-7 |
| R5 | Position shows old values after a confirmed tx | Indexing/settlement latency (~15–30s+) | §3.4 re-read after lag clears; **do not re-submit** | INV-10 |
| R6 | Skill returns `blocked` (cooldown / confirmation) | Safe stop by design | §3.5 wait out cooldown or re-run with confirm token | INV-1 |
| R7 | Deposit/move aborted on active-bin deviation | Active bin moved between plan and broadcast | §3.5 re-scan, re-plan, re-broadcast | INV-7 |
| R8 | Repeated tx failures / suspected fund-risk / key exposure | Systemic or security issue | §3.6 STOP, page a human, do not retry blindly | INV-1 |

### 3.2 Stuck nonce (the big one)

A stuck head nonce is the highest-blast-radius failure: until it clears, nothing else from that signer mines.

1. **Confirm it's the read-ceiling pattern.** Tx is `pending`, fee was paid; public mempool may still show `pending` long after miners dropped it. Check the contract called — a `*-simple-multi` means assume R1.
2. **Unstick the head nonce with RBF.** Broadcast a **1 µSTX self-transfer at the stuck nonce** with a **bumped fee** (replace-by-fee). This is the canonical clear.
3. **Mind custody.** If the signer's custody doesn't expose RBF ergonomically, run the unstick out-of-band with the signing key, or wait for the mempool to age the tx out. Know this path *before* you trade.
4. **Re-issue correctly.** Rebuild the swap as `*-simple-range-multi` with `max-steps ≤ 230`, real `min-dy`, residual handling (INV-3).
5. **Serialize going forward.** Acquire/release every nonce through a nonce oracle so concurrent legs/processes never collide (INV-6).

### 3.3 Partial fills

Bounded swaps trade completeness for safety — a partial fill is **normal**, not a fault (INV-10).

1. Read the `{in, out}` return — that is what actually executed.
2. Recompute the **residual** (requested − filled) against **refreshed** pool state (re-quote; INV-7).
3. Decide: re-broadcast a second bounded leg for the residual, or accept the partial and stop (often correct if price moved against you).
4. Never paper over a partial by re-sending the original size — that risks double execution.

### 3.4 Stale data vs settlement latency (two different things)

- **Stale quote (R4):** quotes can **fail silently** when indexing lags. Before acting on a surprising quote, run the freshness/lag check. Materially behind ⇒ treat quotes as stale: wait for catch-up or refresh; do not size a trade off stale prices (INV-7).
- **Position latency (R5):** after a confirmed tx, the position view trails on-chain truth by the indexing delay (~15–30s+, longer for earnings). The tx *did* land — re-read after the lag clears. **Do not** re-submit because the endpoint hasn't caught up (INV-10).

### 3.5 Skill-level blocks are safe stops

`blocked` / confirmation-required / deviation-abort are the skill protecting you, not failures to route around:
- **Cooldown** (`hodlmm-move-liquidity`, 4h/pool): returns `blocked` with minutes remaining. Wait; do not force.
- **Confirmation required** (`--confirm`, `--confirm=DEPOSIT`, `--confirm=SWAP`): re-run with the token only after reviewing the plan.
- **Active-bin deviation** (`--active-bin-max-deviation`, default 0): re-scan, re-plan around the new active bin, re-broadcast (INV-7).

Log each block to the ledger (INV-11); a recurring block pattern is a memory signal (INV-12).

### 3.6 When to STOP and escalate

Escalate to a human (and stop acting) when:
- A tx-failure pattern **repeats** across retries (don't burn fees or risk funds looping).
- You suspect **fund risk**, a contract behaving against the invariants, or a **security/key exposure** — never act unilaterally.
- The required action falls **outside the active Approval Scope** or the scope is ambiguous (INV-1).
- A load-bearing fact you cannot confirm is required for the action.

Escalation is a valid terminal state of the loop. Record the diagnosis + where you stopped (INV-11). The operator-side decision matrix for these lives in **Chapter 5 — Operator & Escalation Overlay**.

### 3.7 Root-cause discrimination — the three stuck-tx causes (don't conflate)

A stuck, reverted, or partial transaction has distinct causes that need distinct fixes:

| Signal | Cause | Fix |
|---|---|---|
| Fee below market; simply not picked up | **Underpriced** | RBF, same nonce, higher fee (§3.2). |
| Unbounded `*-simple-multi` / wide pool; passed broadcast then hangs | **Oversized / read-ceiling** | **RBF will NOT help — the tx is too big, not underpriced.** Replace the payload with a bounded `*-simple-range-multi`, `max-steps ≤ 230` (INV-3, R1), same nonce; or cancel (1 µSTX self-transfer at the nonce) then re-issue bounded. |
| Reverted on a post-condition / min-out | **Adversarial reorder / sandwich** | Refresh, re-quote, retry once; if it persists, widen tolerance / chunk / route private / **escalate** (§3.6). Do not loop. |
| `(err u5001)` on a native move | **Illegal move geometry** | Withdraw→swap→redeposit; never blind-retry (recenter runbook addendum). |
| Bounded swap `{in,out}` < requested | **Partial fill (expected)** | Residual vs refreshed state (§3.3). |

**Doctrine:** *RBF only cures underpricing.* A transaction that exceeds the block read budget will never
mine regardless of fee — replace it, don't reprice it. Procedure: `hodlmm-stuck-transaction-runbook`.

---

## Chapter 4 — Strategy & Alpha

Alpha is deciding **where** to place liquidity, **how wide**, **how much**, and **when** — *within*
the safety envelope of Ch.0–3, never around it. Every signal below is **read-only input to the DECIDE
phase**; the chosen range/size is then handed to a Ch.2 playbook and runs the full gated loop. **No
strategy signal can relax an invariant** (max-steps, post-conditions, scope, cooldowns still bind).

### 4.1 The alpha inputs (read-only signal skills)

| Skill | Measures | Feeds the decision |
|---|---|---|
| `hodlmm-risk` | Volatility regime from bin spread (40%) + reserve imbalance (30%) + concentration (30%) → `calm`/`elevated`/`crisis` (0–100) | bin **width** + **max exposure** |
| `hodlmm-flow` | Direction bias, flow toxicity, bin velocity, whale concentration, liquidation pressure, bot ratio → LP-safety verdict + predicted range lifespan | go/no-go, **width**, **asymmetry** |
| `hodlmm-inventory-balancer` (`status`/`recommend`) | Price-weighted token-ratio vs target (default 50:50) | rebalance **trigger** |
| `hodlmm-signal-allocator` (`scan`) | Macro signal score + quantum readiness → risk-adjusted yield score | allocation **timing** |
| `sbtc-yield-maximizer` (`status`) | HODLMM APR vs Zest yield under TVL/volume/divergence gates | capital **routing** |

### 4.2 Range width vs adverse selection

The core LP tension: **narrow** = larger share of fees but shorter range lifespan and more exposure
to informed flow; **wide** = durable but diluted. Resolve it from two live readings, re-derived every
loop (INV-7):

- **Regime → width + exposure** (`hodlmm-risk` signals, as published):

  | Regime | Volatility | `recommendedBinWidth` | `maxExposurePct` |
  |---|---|---|---|
  | calm | 0–30 | 3 | 0.25 |
  | elevated | 31–60 | 7 | 0.10 |
  | crisis | 61–100 | 15 | **0.00** (do not add — pull) |

- **Flow → lifespan + safety** (`hodlmm-flow`): **bin velocity** predicts how long a ±N range stays
  in range (`rangeLifespanHours`); **flow toxicity > 0.6** means informed flow is adversely selecting
  LPs — widen or stand aside; an `lpSafety: avoid` verdict is a no-go regardless of APR.

> Synthesis: **width = f(regime, bin velocity)**, **exposure = f(regime, toxicity)**. High APR never
> overrides a `crisis` regime or an `avoid` flow verdict.

> Width also sets your **impermanent-loss exposure** (Ch.6 §6.6): narrower ranges realize divergence
> loss faster when price exits, so size width against *both* expected fee capture **and** expected IL —
> not fees alone. When a drifting position's IL is outrunning its fee accrual, the call is **exit**, not
> recenter (INV-9).

### 4.3 Asymmetric ranges under directional bias

`hodlmm-flow.directionBias` ∈ [-1, +1]. A strong, persistent bias means one side of a symmetric range
is being drained. Skew the range: weight more bins on the side price is trending toward (or position
to sell into the flow), fewer on the draining side. This is the placement-side complement to inventory
balancing (4.4) — use them together, not interchangeably.

### 4.4 Inventory balancing (symmetric exposure ≠ in-range)

**Inventory drift is not price drift.** A position can be perfectly *in range* yet pulled to 70/30 by
one-sided swap flow. `hodlmm-move-liquidity` fixes *price* drift; `hodlmm-inventory-balancer` fixes
*ratio* drift: it computes a **price-weighted** exposure ratio across all bins, compares to target
(default 50:50), and when deviation > `--min-drift-pct` (default 5%) runs a corrective swap +
redeploy. It respects the 4h per-pool move cooldown plus a 1h meta-cooldown (don't re-correct inside
one flow event). Managing symmetric exposure is what separates a market maker from a passive
directional position-taker.

> Note its post-condition shape is the **dual-pin Allow envelope** (sender `willSendLte(amount_in)` +
> pool `willSendGte(min_out)`) — consistent with INV-2's LP form, not a violation of it.

**Asymmetric inventory — volatile / cash pairs.** The symmetric target-ratio balancer above assumes both
legs carry risk. When the pair is a **volatile major (V) against a cash stablecoin (C)** and you measure
risk in USD, only V has drawdown — C is ~riskless at $1 and self-corrects. Manage it with a one-sided,
**V-only** cap: a **soft cap** (stop adding V; saturate skew to the V-selling side; widen; reduce size —
all passive and costless) and a **hard cap** (a deliberate, loss-accepting V→C swap, run **only when the
INV-13 tier is aligned/healthy** — otherwise halt-and-hold, never blind-swap). There is **no lower bound**
on V share: cash-heaviness is re-accumulated **passively on dips**, never by market-buying V (that chases
the move and forfeits the maker edge). Calibration (`f* < f_soft < f_hard`; `f_hard ≈ tolerance/stress`)
lives in the operating-guide **"Volatile major/cash pair"** profile.

### 4.5 Capital allocation & timing

- **When to enter** (`hodlmm-signal-allocator`): gate allocation on a risk-adjusted yield score ≥ 60,
  quantum readiness, price impact ≤ 1.5%, a spend cap, and a 6h cooldown. If the intelligence layer
  is silent/uncertain, **do nothing and say why** — don't allocate into unfavorable windows.
- **Where to route idle capital** (`sbtc-yield-maximizer`): compare HODLMM vs Zest on live yield,
  disqualifying pools under TVL/volume floors or above a price-divergence gate; route to the best
  *safe executable* path, else hold.

### 4.6 The strategy DECIDE pipeline

A reference ordering for the loop's DECIDE phase (all read-only; output feeds Ch.2 execution):

```
1. regime  = hodlmm-risk        → crisis? → HOLD/PULL (exposure 0). else carry width + maxExposure.
2. flow    = hodlmm-flow        → toxicity>0.6 or lpSafety=avoid? → stand aside or widen.
3. shape   = regime + velocity  → set width; directionBias → set asymmetry (4.3).
4. invent. = balancer status    → deviation>5%? → schedule corrective rebalance (4.4).
5. capital = signal-allocator + yield-maximizer → size + timing + venue.
6. hand the chosen {pool, range, size} to Ch.2 Playbook B (add) or C (recenter) — full gates run there.
```

### 4.7 Anti-patterns

- Ultra-narrow ranges chasing fee share in high-velocity / toxic flow (you get picked off).
- Adding liquidity in a `crisis` regime because APR looks high.
- Treating "in range" as "balanced" — ignoring inventory drift.
- Allocating on stale signals or outside favorable macro windows.
- Letting any alpha rationale relax a Ch.0 brake (max-steps, post-conditions/bounds, scope, cooldown).

> Source: `hodlmm-risk`, `hodlmm-flow`, `hodlmm-inventory-balancer`, `hodlmm-signal-allocator`, `sbtc-yield-maximizer`.

---

## Chapter 5 — Operator & Escalation Overlay

The boundary between what an agent does autonomously and what belongs to a human. This is the
supervision layer: the agent's **stop-and-hand-off contract** plus the operator's **controls over the
fleet**. It is the operator-side counterpart to INV-1 (scope) and Ch.3 §3.6 (escalation triggers). A
trading/LP agent is **not** an infra operator — most of this chapter is about knowing where your lane
ends.

### 5.1 Autonomy tiers (what the agent may do at all)

| Tier | Operations | Authority needed |
|---|---|---|
| **Read-only** | `scan` / `quote` / `status` / `assess-*` / position + lag reads | none — always allowed |
| **Scoped execution** | swap, LP add/withdraw, recenter — within an Approval Scope | active scope + Ch.0 GATE pass (INV-1) |
| **Operator / infra** | service restarts, repair scripts, deploys, datastore writes | the protocol team only — **never the trading agent** |

A HODLMM trading/LP agent lives in the first two tiers. The third tier is operated by the protocol team
and is out of scope for fleet agents — surfacing a problem there is an *escalation*, not an action.

### 5.2 Safe vs dangerous operations (agent lens)

| Operation | Class | Agent rule |
|---|---|---|
| Read-only scans / quotes / risk + flow reads | **SAFE** | always allowed, no scope |
| Scoped swap with INV-2/3 protections | **SAFE-in-scope** | only if the pre-flight GATE passes |
| Scoped LP add / withdraw | **SAFE-in-scope** | INV-2-LP bounds set; `add-new` granted for adds |
| Recenter via `move-liquidity` | **CAUTION** | atomic, but respect 4h cooldown; `manage-existing` only |
| Adding capital outside the scope | **FORBIDDEN** | needs explicit `add-new` (INV-1/9) |
| Claiming protocol fees | **REQUIRES AUTHORITY** | dispatches to the contract fee address — not yours to call for gain |
| Modifying contracts | **IMPOSSIBLE** | deployed on-chain, immutable |
| Infra / deploys / datastore writes | **OUT OF SCOPE** | never a trading agent; escalate instead |
| Key rotation / wallet ops / credential changes | **OWNER-APPROVAL** | never unilateral |

### 5.3 Escalation matrix (agent → human)

The agent's job in an incident is **detect → stop → page**, not fix infra.

| Situation | Agent action | Severity |
|---|---|---|
| Monitor blip, self-resolves < 2 min | log it, continue | low |
| Persistent stale/wrong quotes on a pool (INV-7) | stop trading that pool; page your operator | medium |
| Repeated tx failures across retries (Ch.3 §3.6) | stop; page operator with diagnosis | medium-high |
| Suspected **fund risk** | halt all writes immediately; page now | critical |
| **Security / key exposure** | halt; page your operator; **do not act unilaterally** | critical |
| Action outside / ambiguous scope (INV-1) | revert to read-only; request a scope grant | block, not incident |

### 5.4 The stop-and-hand-off contract

Escalation is a **valid terminal state of the loop**, not a failure. When a stop condition (Ch.3 §3.6)
fires, the agent `MUST`:

1. **Halt the relevant writes** — for fund-risk/security, halt *all* writes, not just the current one.
2. **Preserve state** — finish the ledger entry (INV-11): what was attempted, where it stopped, the
   diagnosis, and a suggested fix.
3. **Emit a structured escalation** — symptom, blast radius, the invariant involved, and what you
   need from the human (a scope, a key action, a decision).
4. **Revert to read-only** and **do not retry** the failing write until cleared.

### 5.5 Operator controls over the fleet

The human's levers over agents (the supervision surface):

- **Approval Scope** grant / revoke / expiry — the master control (expanded in Ch.7).
- **Dry-run-first** — skills default to dry-run; execution needs an explicit confirm token
  (`--confirm`, `--confirm=DEPOSIT`, `--confirm=SWAP`, `--confirm=BALANCE`, `--confirm=MAXIMIZE`).
- **Pause / kill** — stop `auto` loops; per-pool and meta cooldowns rate-limit churn.
- **Monitoring cadence** — read-only scans on an interval (e.g. 6h monitoring loop); `auto` rebalance
  interval default 15 min (min 5).
- **Spend caps & reserves** — per-skill: `--max-deploy-sats`, `--reserve-sats`, `--max-correction-sats`,
  STX gas reserve floors, spend caps (e.g. signal-allocator's 500 STX max).

### 5.6 Never-unilateral list

- Anything operator-tier: infra, deploys, datastore writes.
- Protocol-fee claims (authority belongs to the contract fee address).
- Acting on a security incident — page a human, do not improvise.
- Exceeding or *inferring* authority beyond the explicit scope (INV-1).
- Overriding a Ch.0 brake "because the situation seemed to call for it." Brakes do not have exceptions.

## Chapter 6 — Observability, Ledgers & Reporting

Accountability is an invariant, not a nicety. This chapter operationalizes INV-8 (DLP ≠ fees), INV-11
(both ledgers) and INV-12 (memory). No silent actions — every broadcast, escalation, and skill
`blocked` produces a record.

### 6.1 The two ledgers (operationalize INV-11)

Keep them **separate** — one answers "what did I do?", the other "how is it doing?".

**Transaction Ledger** — one row per broadcast *and* per escalation:

| Field | Note |
|---|---|
| `timestamp`, `intent` | what you set out to do |
| `approval_scope` | the scope authorizing it (Ch.7) |
| `preflight` | the GATE snapshot (active bin, est. reads, post-cond form) |
| `txid`, `status` | broadcast + mined result |
| `post_check` | actual-vs-intended diff (INV-10) |
| `lesson` | what to remember (feeds INV-12) |

**Performance Ledger** — one row per measurement cycle (the MEASURE phase):

| Field | Note |
|---|---|
| `token_exposure`, `ratio` | vs target (4.4) |
| `bin_state`, `drift` | range vs active bin |
| `pool_apr`, `cumulative_gas` | running cost basis |
| `mark_to_market` | DLP redemption value |
| `attributed_fees`, `fee_confidence` | see 6.2 |

### 6.2 Fee attribution: DLP value ≠ earned fees (INV-8)

- **DLP mark-to-market** = current redemption value of your bin shares (price-weighted across bins). It
  moves with **price and inventory**, not just earnings.
- **Earned fees** = provider + variable fees that **auto-compounded into your bins** since entry. There
  is no claim and **no FT-transfer event on the swap tx** — fees accrue inside bin balances and the
  `unclaimed-protocol-fees` map — so attribution is **derived, not observed**: estimate it from the
  growth in your share's reserves net of price moves, and record a **`fee_confidence`**. Never report
  compounded fees as realized cash.
- **Protocol fees are not yours** — they dispatch to a contract-registered fee address (§1.6).

### 6.3 What to measure each cycle

| Scope | Metrics | Read from |
|---|---|---|
| Position | range vs active, drift, in/out-of-range, token ratio, DLP m2m, attributed fees, IL estimate, APR | `GET /users/{addr}/positions/{pool}/bins`, `hodlmm-risk` (`impermanentLossEstimatePct`) |
| Pool | TVL, 24h volume, fee run-rate, regime, flow verdict | `GET /pools/{id}`, `hodlmm-risk`, `hodlmm-flow` |
| Wallet | gas reserve, free token balances, pending tx depth | `query` / wallet skills |
| Freshness | indexing lag (gate the above) | the indexer-lag check (INV-7) |

### 6.4 Your reporting surface

Maintain your **own** dashboard/report over the ledgers and public on-chain reads: transactions, TVL &
pools, volume & fees (unclaimed protocol fees are readable on-chain via
`get-unclaimed-protocol-fees-by-id`), per-position drift, and APR. Treat any third-party analytics view
as **convenience, not ground truth** — on any discrepancy, trust on-chain reads + the quote engine.

### 6.5 Telemetry hygiene

- **No silent actions** (INV-11): broadcast, escalation, and every skill `blocked` → a row.
- **Memory** (INV-12) is the cross-run distillation of the ledgers: stale pools, flaky APIs, effective
  targeting, failed-tx patterns.
- **Never write secrets** to ledgers, logs, or escalations (no wallet passwords, keys) — see Ch.7.

### 6.6 Impermanent loss (divergence loss) & net LP return

**Impermanent loss (IL)** is the difference between holding your LP position and simply holding the
same tokens. It exists because the pool rebalances your reserves as price moves, so your position
diverges from a plain hold. It is **a comparison, not a fee or a direct cost**, and it is *impermanent*
— unrealized until you withdraw, and it can grow or shrink as price moves.

IL is the third term in honest LP accounting and the counterweight to fees (extends INV-8 / §6.2):

```
net LP return  ≈  Fee PnL  +  IL-only PnL  −  gas
              =  earned fees  −  divergence loss  −  gas
```

where, valued in one numeraire at the **current** price:

```
IL-only PnL = V_position(excluding fees) − V_hold(original deposited amounts)
Fee PnL     = attributed earned fees (derived, with fee_confidence — see §6.2)
```

**Baseline formula (constant product).** For an `x·y=k` pool the closed form is `IL = 2√r/(1+r) − 1`,
where `r` = current price ÷ entry price. This applies directly to Bitflow's **XYK** pools and is the
right intuition for HODLMM (IL grows with the square-root of divergence and is symmetric in up/down
moves).

**HODLMM specifics (concentrated / bin model — this is what differs):**
- **No single closed form.** HODLMM is concentrated liquidity across **discrete bins**, so IL is
  **range-dependent**: compute IL-only PnL **empirically** — value your actual per-bin token amounts at
  the current price (`V_position excluding fees`) against the hold basis (`V_hold`). Don't use the
  Uniswap-V3 sqrt-price/tick equations; HODLMM is bin-based, not tick-based.
- **IL accelerates toward the range edges**, and is **realized when price exits your range**: your
  liquidity converts entirely to one side of the pair (per the bin rule in §1.3 — bins **above** the
  active bin hold only **Y**, bins **below** hold only **X**). Out of range, divergence loss stops being
  paper and becomes real until/unless price returns.
- **The `impermanentLossEstimatePct` figure from a risk skill is a rough linear proxy** (`driftScore ×
  0.08`, §6.3), useful for *monitoring*, **not** a true price-ratio IL. The definition above is
  canonical; the proxy is a shortcut.
- **Concentration is a two-edged lever (INV-9, Ch.4):** narrower bins earn more fees per dollar **and**
  realize IL faster on a move; wider bins are more durable but dilute fees. There is no protocol keeper
  for HODLMM (§1.7) — the agent controls realized IL via range width and **proactive recentering**
  (`hodlmm-move-liquidity`), or by **exiting** a position whose divergence is outrunning its fees.

> Reporting rule (with INV-8): always separate **IL-only PnL** from **Fee PnL** — never net them into a
> single number, and never report DLP balance as profit. No strategy eliminates IL; the goal is fees +
> incentives consistently exceeding divergence loss + gas.

## Chapter 7 — Approval Scopes, Authority & Custody

The contract between the human operator and the agent. Expands INV-1 (scope) and INV-6 (nonce/custody)
into the full authority + key-handling model. **Default-deny:** anything not explicitly granted is
forbidden, and authority is never *inferred* (INV-1).

### 7.1 The Approval Scope grammar

| Field | Values | Meaning |
|---|---|---|
| **pools** | pool ID(s) | which pools this scope covers |
| **duration** | days | when it auto-expires |
| **permissions** | `manage-existing` / `add-new` / `withdraw` / `swap` | the allowed action verbs |
| **constraints** | caps + prohibitions | spread/size caps, forbidden actions, target ratio |

**Lifecycle:** `granted → active → expired`. On expiry, execution reverts to **read-only** (scanning
continues); request re-approval. Revocable at any time. Example scope: *"`dlmm_1`, 7 days,
`manage-existing` only (no `add-new`), recenter spread ≤ 5, target ratio 50:50."*

### 7.2 Spend limits & reserves

The scope pins caps; the agent honors the **tighter** of (scope cap, skill default). Observed
skill-level controls to bind against:

| Control | Example source |
|---|---|
| Per-allocation spend cap | `signal-allocator` 500 STX max; `sbtc-yield-maximizer --max-deploy-sats` |
| Post-action reserve | `--reserve-sats`, ≥10 STX gas reserve |
| Per-correction cap | `inventory-balancer --max-correction-sats` |
| Price-impact ceiling | `signal-allocator` ≤ 1.5% |
| Cooldowns | move-liquidity 4h/pool; balancer 1h meta; allocator/maximizer per-skill |

**Always preserve a gas reserve** — a write that drains STX can leave you unable to fund the nonce
unstick (Ch.3 §3.2). Reserve enforcement is part of the scope, not an afterthought.

### 7.3 Key custody & signer handling (expand INV-6)

- **Never pass secrets as CLI arguments.** Use env vars (e.g. `WALLET_PASSWORD`, `AIBTC_WALLET_PASSWORD`).
  An argv secret is visible in `/proc/<pid>/cmdline` and `ps auxww` for the process lifetime. Prefer
  restored wallet sessions; a **locked wallet should return guidance, never an interactive prompt**.
- **Re-lock after the write path.**
- **Know your RBF story before trading.** Custody without ergonomic replace-by-fee turns a 30-second
  nonce unstick into a stuck queue (INV-6, Ch.3 §3.2).
- **Never persist secrets** to ledgers (Ch.6), logs, or escalation payloads.

### 7.4 What a scope can NEVER grant

A scope authorizes trade/LP **within caps**. It can never authorize:
- protocol-fee claims for gain, or any operator/infra action (Ch.5.6),
- contract changes (impossible — immutable on-chain),
- key rotation / credential changes,
- **overriding a Chapter 0 brake.** Brakes are not scope-grantable.

### 7.5 The trust handshake

```
grant scope → agent records it (Ch.6 ledger) → operate read-only until first confirm
→ execute within caps (Ch.2 gates) → report (Ch.6) → scope expires → revert to read-only
```

On any ambiguity, cap conflict, or out-of-scope need: **escalate** (Ch.5.3), do not infer authority.

## Chapter 8 — Skill Authoring & Conformance

A HODLMM skill is the executable unit that runs one playbook leg. It **MUST import this handbook's
invariants rather than re-deriving them** — that is the whole point of the handbook existing. This
chapter is the bridge: the import pattern, the AIBTC registry's structural contract, and the safety
bar mapped back to Chapter 0.

### 8.1 The import pattern — cite, don't copy

- **Reference, don't duplicate.** `AGENT.md` decision rules cite the invariants they depend on
  (e.g. "swaps obey INV-3 bounded entrypoints"; "LP writes use the INV-2 LP form"), they do not paste
  constants. When the handbook updates a number, the skill inherits it.
- **No hardcoded mutable state.** Addresses/limits live in Ch.1; live state (pool list, active bin,
  fee rates, TVL) is read at runtime, never baked in. A skill that hardcodes `max-steps` or a fee rate
  is non-conformant.
- **Pin a handbook version** (Appendix C / versioning) so conformance is checkable over time.

### 8.2 File structure & frontmatter (CI-enforced)

Directory: `skills/<name>/` containing `SKILL.md`, `AGENT.md`, `<name>.ts`.

`SKILL.md` frontmatter — the **nested `metadata:`** form; the validator rejects flat keys:

```yaml
metadata:
  author: "github-username"          # required
  author-agent: "Agent Name"
  user-invocable: "false"            # STRING, not boolean
  arguments: "doctor | status | run"
  entry: "<name>/<name>.ts"          # repo-root-relative, no skills/ prefix
  requires: "wallet, signing"        # comma-separated quoted string, not a YAML array
  tags: "defi, write, mainnet-only"  # comma-separated quoted string
```

`AGENT.md` **must** start with frontmatter `name` / `skill` / `description`, then behavior rules
(decision order, guardrails, on-error, on-success). Allowed tags only: `read-only`, `write`,
`mainnet-only`, `requires-funds`, `sensitive`, `infrastructure`, `defi`, `l1`, `l2`.

### 8.3 CLI & output contract

- **Commander.js** arg parsing. Conventional subcommands: `doctor` (+ optional `install-packs`),
  read verbs (`status` / `scan` / `quote` / `assess-*`), and a write verb (`run`).
- **Dry-run by default; explicit confirm token to write** (`--confirm` / `--confirm=WORD`). No token ⇒
  a plan, never a broadcast.
- **One JSON object to stdout.** Registry minimum is `{ "error": "message" }` on failure /
  `{ "result": ..., "details": {} }` on success. Recommended envelope:
  `{ "status": "success|error|blocked", "action": "...", "data": {}, "error": null }`. Use `blocked`
  for safe stops (cooldown, confirmation, gate) — never throw a raw stack trace.
- **Idempotent reruns; persist cooldown/state** to a state file.

### 8.4 Safety conformance maps to Chapter 0

| Registry judging criterion | Handbook obligation |
|---|---|
| **Reliability** (idempotent, safe defaults, explicit errors) | INV-10 verify; Ch.3 recovery; `blocked` for safe stops |
| **Security** (no secret leakage, warn on writes/fund moves) | Ch.7: secrets via env not argv, re-lock, no secrets in output; `write`/`requires-funds`/`sensitive` tags |
| **Structure** (valid frontmatter, AGENT.md rules, JSON contract) | §8.2 / §8.3 |
| **Proof** (on-chain tx / live output) | required — "no proof = not reviewed" |
| **HODLMM integration** | correct Ch.1 entrypoints + INV-2/3 forms |

**A write skill MUST implement the Chapter 0 pre-flight GATE before broadcast** — scope check,
post-condition *form* (swap Deny vs LP Allow+bounds), bounded swap + `max-steps` + residual, nonce
serialization, ledger write. A read-only skill is tagged `read-only` and never signs.

### 8.5 Validate & submit

```bash
bun run scripts/validate-frontmatter.ts      # must pass
bun run scripts/generate-manifest.ts
bun run skills/<name>/<name>.ts doctor        # smoke
```

Open a PR with the output pasted in and an **on-chain proof** (tx link or live JSON). Approved skills
are published to the AIBTC skills registry.

### 8.6 Conformance checklist (handbook-compliant skill)

```
[ ] AGENT.md cites the handbook invariants it relies on (does not copy constants)
[ ] No hardcoded mutable state — addresses/limits via Ch.1; live reads at runtime
[ ] Write path runs the Ch.0 pre-flight GATE before broadcast
[ ] Post-condition form correct per INV-2 (swap = Deny+min-out; LP = Allow+min-dlp/fee-cap/deviation)
[ ] If it swaps: bounded entrypoint + max-steps ≤ 230 + residual handling (INV-3)
[ ] Nonce serialized (INV-6); secrets via env + re-lock; no secrets in output (Ch.7)
[ ] Dry-run default + explicit confirm token; single JSON object; `blocked` for safe stops
[ ] Idempotent; cooldown/state persisted; explicit error payloads (no stack traces)
[ ] Both ledgers written (INV-11); on-chain proof attached; frontmatter passes the validator
```

> Source: the AIBTC skills registry conventions (`SKILL.md` / `AGENT.md` template); Ch.0–7 of this handbook.

---

## Appendices

### Appendix A — Glossary delta (handbook-specific)

| Term | Meaning |
|---|---|
| **The Operating Loop** | SCAN→DECIDE→DRY-RUN→EXECUTE→VERIFY→REMEMBER→MEASURE; every action runs inside it. |
| **Pre-flight GATE** | The Ch.0 checklist that must pass before any broadcast. |
| **Two post-condition forms** | Swap = Deny + min-out; LP = Allow + min-dlp / fee-cap / active-bin-deviation (INV-2). |
| **Bounded swap** | `*-simple-range-multi` with `max-steps` (INV-3); vs unbounded `*-simple-multi`. |
| **Residual** | The unfilled remainder (`{in,out}`) of a bounded/partial swap (INV-3, Ch.3). |
| **RBF unstick** | 1 µSTX self-transfer at a stuck nonce with bumped fee to clear it (INV-6, Ch.3 §3.2). |
| **DLP m2m vs earned fees** | Redemption value of bin shares vs auto-compounded fee income (INV-8, Ch.6). |
| **Inventory drift vs price drift** | Token-ratio imbalance vs range-out-of-position; different fixes (Ch.4 §4.4). |
| **Regime** | `hodlmm-risk` volatility class calm/elevated/crisis → width + exposure (Ch.4 §4.2). |
| **Flow toxicity / bin velocity** | `hodlmm-flow` metrics → adverse-selection risk + range lifespan (Ch.4). |
| **Approval Scope** | pools + duration + permissions + constraints; the authority envelope (INV-1, Ch.7). |

### Appendix B — Verification register

Contract IDs and constants verified point-in-time (April 2026); re-verify on-chain before relying on them.

| # | Claim | Status |
|---|---|---|
| V1 | `dlmm-core-v-1-1` → `SP1PFR4V08H1RAZXREBGFFQ59WB739XM8VVGTFSEA.dlmm-core-v-1-1` | verified (cross-confirmed across Bitflow's published config, app, and skills) |
| V2 | `dlmm-swap-router-v-1-2` → `SM1FKXGNZJWSTWDWXQZJNF7B5TV5ZB235JTCXYXKD.dlmm-swap-router-v-1-2` | verified (live Hiro `/v2/contracts/interface`; exports bounded `*-simple-range-multi`) |
| V3 | On-chain swap-router bin cap (≈350–384) | non-load-bearing — `MAX_STEPS = 319` fold confirmed; `max-steps ≤ 230` sits under it by design |
| V4 | Block read ceiling (≈15,000 reads) | non-load-bearing Stacks network constant — the `< 12,000`-read budget (INV-4) is the operative guard |
| V5 | Out-of-range conversion direction (above active bin → **Y only**; below → **X only**) | verified — matches §1.3 `add-relative-liquidity-same-multi` bin-side semantics (on-chain DLMM contract source); load-bearing for §6.6 IL realization |

### Appendix C — Change log & versioning

The handbook is **versioned**; skills pin the version they conform to (Ch.8 §8.1). Scheme: `v0.MINOR` during drafting; promote to `v1.0` once reviewed. Skills declare `handbook: v0.x` in `AGENT.md`; a constant change bumps the version and signals skills to re-verify.

| Version | Change |
|---|---|
| v0.6 | First public Community Edition: full Ch.0–8 + appendices; canonical contract IDs (two deployers); bounded-swap and two-form-post-condition invariants; strategy + recovery + supervision + conformance. |
| v0.6 *(additive)* | Added §6.6 impermanent-loss & net-LP-return doctrine, §4.2 width↔IL note, and verification V5 (out-of-range conversion direction). No constant changed — `handbook: v0.6` pins remain valid; no skill re-verification required. |
| v0.7 | Added INV-13 (divergence & feed-safety tiering); Ch.3 §3.7 (stuck-tx root-cause discrimination); Ch.4 §4.4 asymmetric-inventory extension. New runbooks: divergence-safety, stuck-transaction, volatile-pair-mm, adverse-selection, pair-calibration; shared peg-monitor. |

---

*This Community Edition is a public, agent-first distillation of how to operate on Bitflow HODLMM safely. It covers public contracts and APIs; protocol-internal infrastructure and operations are out of scope. Verify on-chain; trade at your own risk.*
