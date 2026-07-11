# HODLMM Knowledge Base

The **distilled, cross-campaign memory** of HODLMM operations — what worked, what failed, and the
lessons worth carrying into the next launch. It is the reviewed, shared counterpart to an agent's
private local memory (`memory/hodlmm-lessons.md`).

> **Read this before launching a campaign on a pool.** Then read that pool's playbook and the lessons
> catalog. This is the operationalized "read recent closeout issues before the next launch" step
> (closeout runbook §7).

## How it works (the three layers)

This KB follows the "LLM wiki" pattern — an LLM-maintained knowledge base built on top of immutable
raw sources:

| Layer | Where | Authority |
|---|---|---|
| **Raw sources** | Campaign Closeout **issues** (the [`campaign-closeout`](../../../CONTRIBUTING.md) label) | Immutable, agent-authored. The issue always wins on conflict. |
| **The wiki** | this folder | **Maintainer-maintained, PR-only.** Distilled from *accepted* closeout issues. Agents read it; they never edit it. |
| **The schema** | [`KB-MAINTAINER-GUIDE.md`](./KB-MAINTAINER-GUIDE.md) | How a maintainer INGESTs / QUERYs / LINTs this KB. |

This KB **cites** the handbook by invariant ID (`INV-8`, `§4.2`) and **cites** issues by URL — it never
restates handbook constants, never re-hosts secrets, and never reports a DLP/display mark as realized
profit (INV-8). It holds no live state (pool lists, TVL, APR, active bins are queried live).

## Contents

| Page | What it holds |
|---|---|
| [`pools/`](./pools/) | Per-pool playbooks — what worked / what failed / effective recenter targeting / gotchas, per pool. Start here for a pool you're about to run. |
| [`lessons/lessons-catalog.md`](./lessons/lessons-catalog.md) | Cross-campaign lessons & failure patterns, organized by the six memory categories of `INV-12`. |
| [`log.md`](./log.md) | Append-only ingestion ledger — which closeout issue was distilled into which pages, when. |
| [`KB-MAINTAINER-GUIDE.md`](./KB-MAINTAINER-GUIDE.md) | The maintainer schema: INGEST / QUERY / LINT. |

### Pools

| Pool | Pair | Status |
|---|---|---|
| [`dlmm_1`](./pools/dlmm_1.md) | sBTC/USDCx | active |
| [`dlmm_3`](./pools/dlmm_3.md) | STX/USDCx | active |
| [`dlmm_6`](./pools/dlmm_6.md) | STX/sBTC | active |

## QUERY — how to use this before a launch

1. Open the pool's page under [`pools/`](./pools/) (e.g. [`dlmm_6`](./pools/dlmm_6.md)). Read its
   status/liveness, what worked, what failed, and recenter targeting.
2. Skim [`lessons/lessons-catalog.md`](./lessons/lessons-catalog.md) for the categories relevant to your
   plan (failed-tx patterns, flaky APIs, recenter targeting…).
3. For anything load-bearing, **follow the `sources` link to the raw closeout issue** — the issue is
   authoritative; this KB is a fast index over it.

Agents QUERY freely and never write. New knowledge enters only via a maintainer INGEST PR from an
*accepted* closeout issue — see [`KB-MAINTAINER-GUIDE.md`](./KB-MAINTAINER-GUIDE.md).
