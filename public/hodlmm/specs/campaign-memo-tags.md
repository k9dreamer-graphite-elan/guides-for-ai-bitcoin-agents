---
name: Campaign Memo-Tag Spec
type: spec
version: 1.3
updated: 2026-07-29
handbook: v0.9
enforces: [INV-1, INV-6, INV-8, INV-10, INV-11]
status: draft
---

# Campaign Memo-Tag Spec (grammar v1)

> Conforms to the [HODLMM Agent Handbook](../handbook/HODLMM-Agent-Handbook.md) **v0.9**.
> Origin: Bitflow / BFF Army dashboard team handoff (2026-07-10), adopted with amendments in
> [#39](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/39).
> Consumer: BFF Army episode-level accounting (BitflowFinance/bff-army#44) — parse-later; tags
> emitted now are fixtures for a parser that lands later.

## Purpose

Chain data cannot express where one campaign ends and the next begins: campaign IDs live in the
agent's ledger and GitHub issues, and a 100%-withdraw-then-re-add is indistinguishable from
close-then-new-campaign. This spec demarcates campaign boundaries **on-chain** with one tiny
memo transfer per boundary — zero protocol changes, permanent, retroactively parseable.

This is the **standing, operator-approved exception** to the closeout runbook's zero-gas marker
rule ("never send standalone marker transactions"): that rule's escape hatch is explicit operator
approval, and adopting this spec for a campaign *is* that approval. The closeout addendum's ad-hoc
memo IDs (`<CAMPAIGN-ID>-EXIT`, `<CAMPAIGN-ID>-CLOSE`) are **superseded** by this grammar; its
`tx_role` *report-layer* vocabulary (`OPEN`/`REPAIR`/`WITHDRAW`/`MOVE`/`EXIT`/`CLOSE`) is unchanged
and maps onto tag roles below.

## Trust model (load-bearing — read first)

- **Tags label, transfers measure.** Nothing in a memo ever feeds the money math — basis,
  inventory, gas, and net always come from the actual token legs (INV-8).
- **Closure proof is untouched:** position closed = wallet DLP 0 **and** chain-confirmed withdraw.
  An `X` tag labels a campaign; it cannot close or un-close a position. A tag contradicting chain
  reality gets flagged, not obeyed.
- **Declared intent, never inferred.** A 100% withdraw is ambiguous by nature (withdraw-MAX-then-
  recenter is routine). The withdraw leg carries the intent the agent declares at emit time;
  nothing is inferred from amounts.
- **Purely additive.** Untagged history keeps heuristic segmentation; the convention is backwards
  compatible.

## Grammar v1

One STX-transfer memo (≤ 34 bytes, ASCII, parsers trim trailing padding) per campaign boundary:

```
[H1][role]:[pool]-[yymmdd]-[nnn][:txid8]

H1E:dlmm1-260710-004              entry            (20 bytes)
H1R:dlmm1-260710-004:ab12cd34     recenter leg     (29 bytes)
H1D:dlmm3-260717-006              daily checkpoint (20 bytes, payload-free — see §D)
H1X:dlmm1-260710-004:ab12cd34     exit             (29 bytes)
```

Parser regex: `^H1([EXRD]):([a-z0-9]+)-(\d{6})-(\d{3})(?::([0-9a-f]{8}))?$`

| Field | Meaning | Rules |
|---|---|---|
| `H1` | magic | fixed; the magic bump to `H2` is reserved for **breaking** grammar changes once a parser ships. Additive roles fold in under `H1` with a spec-version bump (this is how `D` landed in v1.3 — pre-parser was the cheap moment) |
| role | `E` entry · `X` exit · `R` recenter/rebalance · `D` daily checkpoint (v1.3, non-boundary — see §D) | one byte; top-up/partial adds are non-boundaries and stay untagged |
| pool | compact pool id | mechanical: `dlmm_1` → `dlmm1` (drop underscore, lowercase) |
| `yymmdd` | **campaign start date** — part of the campaign's identity, constant across every tag of that campaign (NOT the tag emission date) | `260710` = 2026-07-10 |
| `nnn` | campaign counter, **the exact canonical counter, all digits** | canonical `…-004` → `004` (never truncate) |
| `:txid8` | first 8 hex chars of the tx being tagged | optional on **any** role; **REQUIRED on retroactively-emitted tags** — exact binding, kills correlation heuristics |

**Round-trip requirement:** `dlmm1-260710-004` ⇄ `HODLMM-DLMM1-20260710-004` must map mechanically
in both directions (case, underscore, century prefix — no numeric rules), or chain and ledger drift
apart on names.

## Identity scoping — campaign ids are wallet-scoped, NOT globally unique

Nothing in the grammar identifies the agent or wallet, so **two agents can legitimately mint the
byte-identical campaign id** (same pool, same start date, same counter — e.g. both enter `dlmm_1`
on the same day as their respective campaign `002`). This is by design, not a defect: the canonical
key is the tuple

```
(watched principal, campaign id)
```

which is unique because each agent's counter is unique within its own ledger.

Consequences (normative):

- **Consumers MUST partition by sender.** Parser identity already comes from the sender (see the
  emission recipe); the sink's incoming history is a convenience index that will genuinely contain
  identical memo strings from different senders. Keying episodes on the bare memo string merges
  unrelated agents' campaigns — always key on `(sender, campaign id)`.
- **A bare campaign id is unambiguous only inside one wallet's history** (or one agent's ledger /
  memory). Any cross-agent context — KB pages, closeout-issue searches, shared dashboards,
  aggregated report/card output — must carry the agent or wallet alongside the id (the closeout
  issue-title convention `[<Agent> · <Campaign-ID>]` already does this).
- **`X` terminality and `R` same-id matching are per-sender.** One agent's `X` never terminates
  another agent's identically-named campaign.

## Emission recipe (mechanism A — companion memo tx)

1. Broadcast the LP tx (entry add / exit withdraw / recenter leg) and **wait for confirmation**
   (INV-10 — never tag an unconfirmed tx; if it fails, no tag is emitted).
2. Send a **1 µSTX transfer from the watched principal to the tag sink** with the memo string.
   The sender must be the position-holding wallet the dashboard watches (if LP calls route via a
   smart wallet, the tag still comes from the watched principal); the fixed recipient is the
   **designated tag sink**:

   ```
   SP1DK6YXB474DEENXSK3HXDYNW5K4MC5SMAQBY6Y3
   ```

   *Erratum (v1.1, field-confirmed 2026-07-10):* v1.0 specified a self-transfer
   (sender = recipient). Stacks node mempool admission **rejects self-transfers**
   (`TransferRecipientCannotEqualSender`), so the recipient must differ from the sender.
   Parser identity comes from the **sender**; the fixed sink is a secondary filter and lets the
   consumer enumerate all tags network-wide from one address's incoming history.
   Normal explicit fee; **serialize the nonce** through the nonce oracle (INV-6 — one in-flight
   tx per signer, globally).
3. **Ledger-log the tag tx** alongside the LP tx it labels (INV-11). Cost ~0.0002–0.003 STX per
   boundary vs ~3 STX gas per campaign — noise.

## When to emit which tag

| Event | Tag(s) |
|---|---|
| Campaign entry (first add) | `E` after the add confirms — this **mints the campaign id** on-chain. Emit as a **Day-0 artifact**, same session as the entry (batching with a later ledger write risks a dead session leaving the campaign unminted). Optional `:txid8` of the entry tx |
| Atomic recenter (`move-*-liquidity-multi`) | **no tag** — the function name already declares it on-chain |
| Non-atomic recenter (withdraw → re-add, incl. withdraw→swap→redeposit repairs) | `R` on the withdraw leg **and** `R` (same campaign id) on the re-add — the tag that prevents one campaign from being split into two |
| Top-up add / partial withdraw inside a campaign | untagged — not boundaries |
| Campaign exit | `X` **as part of the closeout ritual** (measure → report → ledger write), carrying `:txid8` of the confirmed exit tx — the *deferred exit stamp*. Exit is a declaration, not an inference: the campaign isn't over when DLP hits zero; it's over when the books close |
| Daily checkpoint (while open) | `D`, at most one per UTC day per campaign — see §D. Payload-free, never `:txid8` |

## §D — the `D` checkpoint role (v1.3; role set is `[E, X, R, D]`)

> **Version-numbering erratum.** The `D` role was drafted in the consumer thread
> (BitflowFinance/bff-army#44, 2026-07-17) as "grammar v1.2". This spec's **v1.2 was already
> taken** by the identity-scoping revision (2026-07-13), so the canonical numbering is this
> document's: **`D` lands in spec v1.3**. The consumer thread's "v1.2" refers to the same role
> definition, unchanged in substance.

- **Purpose: a shared, chain-anchored snapshot clock.** Unrealized PnL is computable at any
  moment — what `D` adds is the *agreed moment to measure at*. Each `D` pins a block height; any
  party recomputing the campaign values the position at that block and gets the same series.
  Periodic reports cite their anchor ("Day-5 mark, tx `0x…`") and become independently
  recomputable instead of trust-my-timing. Report **values** stay off-chain; the **measurement
  grid** is on-chain.
- **Bonus semantics:** an unbroken `D` chain is attended-operation evidence; a missed mark is
  honest operational transparency (renderable as `✓✓✓✗✓ — one missed checkpoint`).
- **Hard rule — `D` is payload-free.** It is the one role with no LP tx to validate against, so
  it must never carry values (no marks, no PnL figures, no `:txid8`) — self-attested values must
  never feed or decorate the math. Its validity check is positional instead: **valid only while
  the campaign is open** (wallet holds DLP in the pool at the `D`'s block; timestamp between the
  `E`'s add and the `X`'s withdraw). Outside that window → flagged invalid.
- **`D` never moves a boundary.** Episode start/end remain exclusively E/X + closure proof —
  checkpoints cannot slice a campaign into flattering windows.
- **Cadence is operator policy** (daily recommended; the field automation emits at 14:00 UTC with
  a per-UTC-day dedupe marker and self-retires when the campaign closes).
- **Missed days are never retro-emitted.** A late "daily" checkpoint would misdate the
  measurement grid; the gap stands as honest evidence of non-monitoring (007 field case: two
  missed days from silent host-cron non-execution — detected, alerted, not backfilled).
- **Unattended-emission carve-out** (amends the retroactive-emission rule below for `D` only):
  the never-tag rule protects the LP-signing write path (LSN-0015/LSN-0017). `D` emission runs as
  a **separate, minimal scheduled signer** that can only send 1 µSTX memo transfers to the sink —
  no LP authority, no payload, per-day dedupe, fee booked into the campaign ledger at emission
  (LSN-0019). This adds no surface to the LP signer and is the only sanctioned scheduled tag
  emitter; `E`/`R`/`X` remain supervised-or-catch-up only.

## Retroactive emission (legal, and the unattended-path rule)

**Scheduled monitors and executors never emit boundary tags** (`E`/`R`/`X`; the `D` role has its
own sanctioned minimal scheduled emitter — see §D). Tag composition is a labeling concern; adding
it to an unattended signer expands the write path against write-path minimalism
([LSN-0015](../knowledge/lessons/lessons-catalog.md#lsn-0015) /
[LSN-0017](../knowledge/lessons/lessons-catalog.md#lsn-0017)). Instead, the agent emits **catch-up
tags at the next supervised cycle**, each carrying `:txid8` of the leg it labels. Parse-later
semantics make a late tag equivalent to a prompt one; the `:txid8` requirement keeps the binding
exact. The same rule onboards campaigns that entered before this spec existed (late `E` with the
entry txid).

## Precedence: `X` is terminal

A withdraw leg tagged `R` (declared recenter intent) whose re-add is later abandoned (staged repair
→ give-up path, cf. [LSN-0016](../knowledge/lessons/lessons-catalog.md#lsn-0016)) does **not** leave
the campaign open: the closeout `X` supersedes any prior `R` declaration. A campaign with an `X` is
closed regardless of dangling `R`s; parsers treat a trailing `R`-without-re-add before an `X` as
part of the exit sequence. (The reverse never occurs: nothing supersedes an `X` — a new campaign
mints a new `E`.)

## Mapping to the report-layer `tx_role` vocabulary

Tags demarcate **boundaries on-chain**; `tx_role` attributes **every tx in reports** (closeout
runbook, tx-attribution addendum). They coexist:

| tag role | `tx_role` of the labeled tx |
|---|---|
| `E` | `OPEN` |
| `R` (withdraw leg / re-add leg) | `WITHDRAW` + `MOVE`/`REBAL`/`REPAIR` |
| `X` | `EXIT` (the tag tx itself logs as `CLOSE`-phase evidence) |
| `D` | none — labels no LP tx; the tag tx itself books as a `TAG-D` ledger row with its fee (LSN-0019) |

## Worked examples (first natively-demarcated campaigns)

```
H1E:dlmm1-260710-004:<txid8 of entry add>     late E — HODLMM-DLMM1-20260710-004 (sBTC/USDCx)
H1E:dlmm3-260710-005:<txid8 of entry add>     late E — HODLMM-DLMM3-20260710-005 (STX/USDCx)
H1X:dlmm1-260710-004:<txid8 of exit>          at 004 closeout (planned 2026-07-17)
```

`D` field fixtures (all confirmed on-chain, sender `SP1AK5ZKG…`, sink `SP1DK6YXB…Y6Y3`):
first two `H1D:dlmm3-260717-006` checkpoints `0x543e2912…` (supervised) and `0x42fbb0de…`
(scheduled-emitter live fire, 2026-07-18); five `H1D:dlmmv2-260722-007` checkpoints
(`0x389aac72…`, `0x3e5db9dc…`, `0x709d015a…`, `0xd7582a35…`, `0x919c2ef5…` — Jul 22–25 + 28;
Jul 26–27 missed and left as an honest gap per §D). A complete E→D×5→X lifecycle is on-chain for
campaign 007 (closeout [#73](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/73)).

## Failure handling

| Symptom | Handling |
|---|---|
| Labeled LP tx failed / never confirmed | No tag — a tag references a confirmed boundary or nothing (INV-10) |
| Tag tx itself fails or stalls | Retry under normal nonce discipline (INV-6); a missing tag degrades to today's heuristics, never blocks the campaign — auxiliary-data failures never block a bounded terminal exit (LSN-0016) |
| Tag emitted with wrong content | Emit a corrected tag (same campaign id, correct fields, `:txid8`); ledger-note the bad one. Parsers prefer txid-bound tags on conflict |
| Daily `D` missed (emitter or host didn't run) | The gap stands — **never retro-emit** (§D); alert the operator (the campaign monitor carries a missed-day detector) and let the unbroken-chain evidence honestly show the miss |
| `D` carrying a payload or `:txid8`, or landing outside the open window | Flagged invalid; ignored for all purposes. Payload-free is a parser acceptance criterion, not a style rule |
| Tag contradicts chain reality | Consumers flag it; chain wins. Tags never override transfers |
