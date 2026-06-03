# HODLMM Agent Handbook — Community Edition

The canonical safety + operating reference for autonomous agents — and the operators supervising
them — that **trade and provide liquidity on Bitflow HODLMM** (DLMM concentrated-liquidity pools on
Stacks) to earn fees safely.

> **Read [Chapter 0](./HODLMM-Agent-Handbook.md#chapter-0--invariants--pre-flight) before any
> autonomous trade or LP action.** It is the safety floor.

## Who this is for

Builders of Bitcoin/Stacks DeFi agents and skills (e.g. for the AIBTC / BFF Army ecosystem), and the
operators who run them. The handbook is **machine-first**: rules are stated as `MUST` / `NEVER` /
`GATE` so an agent can consume them directly, with enough rationale that a human can supervise.

## What's inside

| Chapter | Topic |
|---|---|
| **0 — Invariants & Pre-Flight** | The 12 non-negotiable rules + a pre-flight checklist. The brakes. |
| **1 — Canonical Reference** | Contract map, addresses, entrypoints, quote→swap path, cost limits, fee model. |
| **2 — Playbooks** | Trade safely · provide LP & earn fees · manage / recenter a range. |
| **3 — Failure Modes & Recovery** | Stuck-nonce / RBF, partial fills, stale data, escalation. |
| **4 — Strategy & Alpha** | Range width vs adverse selection, inventory balancing, yield routing. |
| **5 — Operator & Escalation Overlay** | Autonomy tiers, safe/dangerous ops, stop-and-hand-off. |
| **6 — Observability, Ledgers & Reporting** | The two ledgers, fee attribution (DLP ≠ fees). |
| **7 — Approval Scopes, Authority & Custody** | Scope grammar, spend limits, key custody. |
| **8 — Skill Authoring & Conformance** | How to build a skill that *imports* this handbook. |

→ **[Read the handbook](./HODLMM-Agent-Handbook.md)**

## How to use it

- **Agents/skills should *import* Chapter 0's invariants, not copy constants** (see Ch.8). 
- All contract addresses and limits are **point-in-time — verify on-chain before signing.** This
  document is a guide, not an oracle.
- The single highest-value rule: **use bounded swap entrypoints** (`*-simple-range-multi`,
  `max-steps ≤ 230`) and **always attach the correct fund-protection** for the operation (Deny-mode
  post-conditions for swaps; contract-level `min-dlp` / fee-cap / active-bin bounds for LP).

## ⚠️ Safety & disclaimer

- **Not financial advice.** Provided "as is", without warranty of any kind.
- **Mainnet only. Real funds are at risk.** You are responsible for every transaction your agent signs.
- **Verify everything on-chain.** Addresses, entrypoints, and limits change.
- HODLMM contracts have **no admin keys and no oracle** — safety comes from post-conditions and
  contract-level bounds, which only protect you if you set them.

## Scope & omissions

This Community Edition covers **public contracts and APIs** only. Bitflow's internal infrastructure,
operational endpoints, and incident runbooks are **intentionally excluded** — it documents what an
agent needs to act safely, not how the protocol is operated internally.

## Contributing

Skills are submitted to and published via the **[AIBTC skills registry](https://aibtc.com/skills)**.
Follow the [Chapter 8 conformance checklist](./HODLMM-Agent-Handbook.md#86-conformance-checklist-handbook-compliant-skill)
and the registry's `SKILL.md` / `AGENT.md` conventions. See [CONTRIBUTING.md](./CONTRIBUTING.md).

## Versioning

Handbook is versioned (currently **v0.6**); skills pin the version they conform to. The change log
lives in Appendix C of the handbook.

## Security

Report vulnerabilities responsibly — see [SECURITY.md](./SECURITY.md). Do **not** open public issues
for fund-affecting bugs.

## Links

- Bitflow — <https://bitflow.finance>
- AIBTC skills registry — <https://aibtc.com/skills>
- Stacks explorer (verify contracts) — <https://explorer.hiro.so>

## License

Documentation is licensed under **CC BY 4.0**.
