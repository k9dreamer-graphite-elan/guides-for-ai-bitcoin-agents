# Shared — Cross-Protocol Runbooks

Runbooks and guides that span **more than one protocol** and therefore don't belong under a single
protocol folder.

Each cross-protocol runbook still conforms to the relevant protocol handbook(s) and declares which
invariants it enforces (same rule as protocol runbooks).

| Runbook | Spans | Purpose | Status |
|---|---|---|---|
| [`sbtc-yield-routing-runbook.md`](./sbtc-yield-routing-runbook.md) | HODLMM (Bitflow) + Zest | Route idle sBTC to the highest *safe* yield: compare HODLMM LP APR vs Zest supply under TVL/volume/divergence gates, then deploy. | draft |

New cross-protocol runbooks copy the protocol runbook template at
[`../hodlmm/runbooks/_TEMPLATE-runbook.md`](../hodlmm/runbooks/_TEMPLATE-runbook.md) and list **all**
the handbooks they conform to in frontmatter.
