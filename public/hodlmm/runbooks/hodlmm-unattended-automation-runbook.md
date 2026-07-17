---
name: HODLMM Unattended Automation Runbook
type: runbook
handbook: v0.9
enforces: [INV-1, INV-6, INV-7, INV-10, INV-11, INV-12, INV-13]
skills: [nonce-manager]
status: active
---

# HODLMM Unattended Automation Runbook

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.9**.
> Enforces: INV-1, INV-6, INV-7, INV-10, INV-11, INV-12, INV-13.

## Purpose

Arm and operate an **unattended monitor/executor loop** for one HODLMM campaign — scheduled reads,
gated writes, and alerting that stay safe with no human and no LLM in the loop — from day-0
validation through disarm at campaign close.

This runbook governs the *harness around* operations, not the operations themselves: the loop's
write branches execute other runbooks (recenter, exit) via their approved skills. Every field rule
here was earned by an incident in an accepted Campaign Closeout — sources are cited inline so the
evidence chain stays auditable.

## When to run / when NOT to run

- **Run when:** a campaign charter includes scheduled monitoring and/or operator-approved automated
  writes (recenter, auto-exit at planned end) and you are about to arm the schedules.
- **Do NOT run when:** there is no explicit approval scope for *automation* (attended approval to
  trade ≠ approval to sign unattended — INV-1); or the write branches' underlying runbooks are not
  themselves ready to execute; or you cannot deliver alerts to the operator (an unattended loop that
  cannot page a human on failure is not armed, it is abandoned).
- Decision reference: Handbook Ch.5 (Operator & Escalation Overlay) for what may run unattended
  versus what must escalate.

## Inputs

| Param | Meaning | Default |
|---|---|---|
| `campaign-state` | path to the campaign's persisted state file (counters, clocks, gate flags) | — |
| `monitor-cadence` | read-only scan interval | 2h |
| `executor-cadence` | write-eligible tick interval; offset from monitor so each tick sees ≥1 fresh scan | 4h |
| `confirm-scans` | consecutive scans that must agree before a write branch arms | 2 |
| `failure-gate` | consecutive failed writes that halt the loop | 1 |
| `alert-channel` | operator paging path (must be test-fired at arm time) | — |
| `rehearsal-lead` | how far before a terminal trigger to dry-run the exit branch in the real scheduler env | 24h |

## Required Approval Scope (INV-1)

- Permissions needed: explicit operator approval for **each automated write branch** (e.g.
  "recenter under conditions X", "exit at planned end") — enumerated, not implied. Read-only
  monitoring needs no write scope.
- Caps this runbook respects: the campaign charter's gas budget, per-write fee cap, write-count
  caps, cooldowns, and untouchable assets. Counters persist in `campaign-state` (INV-12) and every
  tick checks them before acting.
- Resuming after any halt requires **fresh operator approval** — the loop never un-halts itself.
- If scope is missing/expired → monitor-only; alert instead of act. Do not infer authority.

## Gates — run BEFORE arming (day-0), and the per-tick subset before every write

**Arm-time gates (day-0 environment parity):**

```
[ ] Every script sets its own environment: explicit PATH (and any env the signer needs) exported
    in-script — never inherited from the scheduler. Scheduler default PATH lacks user tool dirs;
    this killed an operator-approved exit on its first scheduled invocation (closeout #21).
[ ] EVERY action branch — especially the rare ones (exit) — dry-run under a scheduler-minimal
    environment: env -i HOME=$HOME PATH=/usr/bin:/bin. Interactive validation proves nothing
    about the scheduled environment; the rare branch can stay unexercised all campaign and fail
    exactly when it matters (closeout #21: "first-use-in-cron" failure class).
[ ] CLI flags verified against the INSTALLED skill's --help — never inherited from a prior
    campaign's scripts (a wrong flag = silent exit, no tx, no error surfaced; closeout #21).
[ ] Signer unlock path verified WITHOUT secrets in argv or inherited env (process lists leak argv).
[ ] Alert channel test-fired end-to-end; failure-alert enabled on every schedule (after 1 error).
[ ] Watchdog armed: a process OUTSIDE the loop pages the operator when the monitor misses a tick.
    The loop cannot detect its own death; silent monitor outages are the most-hit failure class
    (3 incidents, 3 distinct root causes, one 14h gap — closeouts #21, #11–#13 and dlmm_1 field log).
[ ] Ledger + state files initialized (INV-11/12).
```

**Per-tick gates (before any write branch):**

```
[ ] Kill-switch clear: no operator touch-file present (global or per-campaign) — see
    "Operator kill-switch" below; if present, freeze all writes, alert once, exit clean
[ ] Fresh scan this tick; plan recomputed from it (INV-7) — never execute a plan from a prior tick
[ ] Feed-health / divergence verdict permits writes (INV-13); independent sources agree —
    on ANY degraded or disagreeing read: ABORT the branch and alert, never sign blind
[ ] Condition confirmed on `confirm-scans` consecutive scans (kills transient read jitter)
[ ] Charter caps: gas budget, write count, cooldown clock, untouchable list — all green
[ ] Failure gate closed (no unresolved prior failure)
[ ] Nonce serialized via `nonce-manager` — one in-flight tx per signer, globally across everything that signs (INV-6)
[ ] Ledger entry prepared (INV-11)
```

## Procedure

1. **SPLIT** — build the loop as two scheduled units: a read-only **monitor** (scan, evaluate,
   alert) and a write-eligible **executor** (gates → plan → sign). The planner that computes
   expected outputs is read-only; **write targets come from the maintained skill, never from a
   local planner** (a local plan script carried a strategy bug the maintained skill got right —
   deterministic ≠ correct; closeout #11–#13 addendum, dlmm_1 field log).
2. **VALIDATE (day-0)** — run every arm-time gate above. All stderr from every branch goes to the
   log (`2>>$LOG`), plus a stdout snippet on failure — discarded stderr masked a root cause for
   4 days (closeout #21).
3. **ARM** — install the schedules (`monitor-cadence`, `executor-cadence` offset so the executor
   always sees fresh scans), enable failure alerts, start the watchdog. Record the arm event and
   the approved branch list in the ledger (INV-1/11).
4. **OPERATE (each executor tick)** — per-tick gates → if no branch triggers, write `action=none`
   and exit. If a branch triggers: dry-run first, then execute per the *operation's own runbook*
   (recenter/exit), with explicit fee (never auto-fee), output minimums from direct on-chain reads,
   and serialized nonce (INV-2/3/6 enforced by that runbook's procedure).
5. **VERIFY** — after any broadcast, prove the **actuator chain end-to-end**: mined `success` AND
   re-scanned position matches intent (INV-10). A green tick is not a completed action; a confirmed
   tx is not a correct outcome (LSN-0011). If the signer process hangs or times out after emitting
   a txid, resolve by re-scanning the chain — the chain is truth, not the child process.
6. **REMEMBER** — write both ledgers and update `campaign-state` counters/clocks every tick,
   including no-ops (INV-11/12). A monitor that only logs when something happens cannot prove it
   was alive (LSN-0008: freshness ≠ completeness).
7. **REHEARSE** — at `rehearsal-lead` before any terminal trigger (planned end, goal threshold),
   dry-run the exit branch **in the real scheduler environment**. The exit that fires must be one
   that has already been exercised there.
8. **HALT / RECOVER** — on `failure-gate` consecutive failed writes: freeze all write branches,
   alert, keep monitoring. Position intact + nothing broadcast is the designed safe state (held in
   both live incidents — closeout #21). Resume only per Required Approval Scope. If planned end
   passes with the position nonzero, alert on every tick until resolved (this alert is what
   recovered the failed auto-exit in closeout #21; see also LSN-0007).
9. **DISARM** — at campaign close: disable all schedules and the watchdog, confirm closed state
   per the exit runbook's closure proof, write the final ledger entry, and mark `campaign-state`
   closed. Leftover live schedules against a closed campaign are an incident, not litter.
   Disarm is **host-level, and it is a proof, not an intent**: enumerate *generic/shared* residents
   too, not only campaign-specific ones — a signer-enabled service still bound to the ended campaign
   by an **implicit default** is the dangerous case (field-seen: no tx submitted, but stale
   `rebalance,exit` authority survived closure). Verify (a) no signer-enabled process still
   references the campaign, (b) no in-flight tx remains, (c) repository ↔ installed ↔ loaded
   scheduler config reconcile to a dormant, signer-disabled, campaign-unbound template, and (d) the
   runtime **fails closed** — a closure-proven campaign state is rejected before any heartbeat/loop
   can start (require an explicit campaign-state binding; never an implicit campaign default). See
   [LSN-0017](../knowledge/lessons/lessons-catalog.md#lsn-0017) and the closeout runbook's
   host-disarm checklist. (LSN-0015 covers the write-path lifecycle gate; this covers the host.)

## Expected outputs

- Per tick: a ledger/log line — timestamp, scan source(s) + agreement verdict, gate results,
  `action=none|<branch>`, and for writes: txid + verified outcome diff.
- Watchdog: silence (its output is the *absence* of "monitor missed a tick" pages).
- A `blocked`/halted status is **expected**, not an error: it means a gate did its job.

## Failure handling

Map each failure to **Handbook Chapter 3** (don't restate the recovery):

| Symptom | Handbook |
|---|---|
| Scheduled branch dies on missing tool/env (works interactively) | Ch.3 §3.5-class safe stop → fix env per arm-time gates, re-run day-0 parity before re-arming |
| Stuck `pending` / nonce stalled | Ch.3 §3.2 (RBF unstick) |
| Partial fill on a write branch | Ch.3 §3.3 (residual) |
| Stale/degraded/disagreeing reads | Ch.3 §3.4 + INV-13 gate (branch ABORTs, alerts) |
| Executor `blocked` (cooldown / confirm / gate) | Ch.3 §3.5 — safe stop, not an error |
| Repeated write failures / fund risk / key exposure | Ch.3 §3.6 → STOP + escalate (failure gate enforces the stop) |
| Tx confirmed but re-scan ≠ intent | Ch.3 §3.7 root-cause discrimination; do not fire the next action off an unproven repair (LSN-0011) |
| Monitor silent (watchdog page) | Treat as incident: no writes trusted until the loop is proven live again (LSN-0008) |

## Idempotency / cooldown

- Monitor: safe to re-run any time (read-only). Executor: idempotent by construction — every tick
  recomputes from a fresh scan (INV-7) and consults persisted counters/clocks (INV-12); a re-run
  tick that finds no armed condition writes `action=none`.
- Cooldown: charter's per-pool write cooldown, tracked in `campaign-state`, checked in the per-tick
  gates. Never re-send an original-size action to "fix" a partial — risks double execution.
- Halt state survives restarts: the failure gate lives in `campaign-state`, not in process memory.

## Operator kill-switch (touch-file)

Every unattended loop must be stoppable **without a restart, an edit, or a deploy**. The
mechanism is a touch-file, checked at the top of every tick, before every other gate:

- Convention: a well-known path per host (global) and one per campaign directory
  (per-campaign), e.g. `.KILL-SWITCH`.
- If present: log it, alert the operator once (not every tick), take no actions, exit 0.
- `touch .KILL-SWITCH` halts the loop within one tick; `rm .KILL-SWITCH` resumes it.

Why a file and not an env var or config flag: files are atomic, visible in `ls`, work from any
shell or remote session without knowing the loop's environment, survive restarts, and need no
parsing. This **complements** the failure gate (halt-after-N-failures): the failure gate is the
loop protecting itself; the kill-switch is the operator overriding the loop. Both must exist.

## Fee selection for unattended writes

The explicit-fee rule stands (never let a tool auto-pick the fee at signing time). What the fee
*value* should be has evolved from our fixed-fee practice: a pinned fee overpays in quiet
mempools and under-bids during congestion, and can't react to either. An unattended agent
should compute a **bounded estimate** each tick and pass it explicitly:

1. Fetch the live contract-call fee percentiles from the public Stacks API
   (`GET /extended/v1/tx/mempool/stats` → `tx_simple_fee_averages.contract_call`).
2. Pick a percentile (p25 is a good default for patient agents), but **cap it at p25 × 4**.
   The Stacks mempool is thin — a few whale txs routinely drag p50+ to absurd levels (field
   observation: p75/p95 above 2,000 STX while p25 sat at ~0.009 STX). During genuine
   congestion all percentiles rise together, so the cap rises too; during whale skew p25 stays
   put and the spike is discarded.
3. On fetch failure, fall back to `GET /extended/v2/mempool/fees` (map `no_priority`→p25,
   `low`→p50, `medium`→p75, `high`→p95; apply the same cap), then to a static default.
4. Clamp the result to a hard `[min, max]` window so no data anomaly can ever set a fee
   outside the risk budget.
5. The final fee is **`min(charter fee cap, max(charter fee target, estimate))`** — the
   campaign charter always wins on both ends.

For stuck transactions, pair this with a bounded replace-by-fee ladder (bump ×1.5, max 3
bumps, never past the max clamp) per the stuck-transaction runbook — timely confirmations
with spend that can never leave the envelope.

## Notes

- **Evidence base:** accepted Campaign Closeouts #4/#5 (dlmm_6), #21/#22 (dlmm_3 campaign-002 —
  the scheduled-exit failure and recovery this runbook exists to prevent), #11–#13 (Hex Stallion 7D
  — staged-repair and actuator-chain lessons), and **#28 (dlmm_1 campaign-003 — the promotion
  citation: a scheduled loop ran this doctrine end-to-end on mainnet: day-0 validated script monitor,
  per-tick gated auto-repair, planned-end exit with renewal check, and disarm at close, with a
  degraded-LLM fallback exercised mid-campaign)**, and **#35 (Hex Stallion dlmm_1 control-plane
  addendum — a generic signer-enabled resident survived closure via an implicit campaign default;
  the DISARM step's host-level proof exists to catch exactly this)**. KB lessons: LSN-0007,
  LSN-0008, LSN-0011, LSN-0015, LSN-0017.
- **Relationship to other runbooks:** this runbook owns the harness (schedules, gates, halts,
  alerts, rehearsal, disarm). The write branches themselves are the recenter and exit runbooks;
  nothing here overrides their procedures. If a conflict appears, the operation runbook wins for
  the operation, this runbook wins for the harness.
- **Boundary tags ([memo-tag spec](../specs/campaign-memo-tags.md)): the loop never emits them.**
  Tag composition is a labeling concern; teaching an unattended signer to send memo transfers
  expands the write path against write-path minimalism (LSN-0015/LSN-0017 — the signer surface
  stays exactly the approved write branches, nothing more). Instead the agent emits **catch-up `R`
  tags at the next supervised cycle**, each bound with `:txid8` to the auto-repair leg it labels
  (the per-tick ledger lines from step 6 are the work-list). Parse-later semantics make late tags
  equivalent to prompt ones; a missing tag degrades to heuristics and never blocks anything.
- **LLM-in-the-loop variants:** if a model is part of the loop (diagnosis, planning), treat model
  unavailability as a first-class failure mode: detection and alerting must be fully deterministic,
  and every model-dependent branch needs a defined degraded behavior (alert with context instead of
  act). Field-proven: a campaign ran safely for days in exactly this degraded mode.
- Scheduler tech varies (crontab, launchd, agent-runtime crons): the environment-parity and
  watchdog gates apply to all of them; only the mechanics differ.
