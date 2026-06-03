# HODLMM Agent Handbook (Community Edition)

The canonical safety + operating reference for autonomous agents — and the operators
supervising them — that trade and provide liquidity on Bitflow **HODLMM** (DLMM)
concentrated-liquidity pools on Stacks, to earn fees, trade and increase agents participation and safety.

> **Read Chapter 0 before any autonomous trade or LP action.** It is the safety floor.

## Who this is for
Builders of AIBTC/BFF Army agents and skills, and operators running them. Machine-first
by design: rules are stated as MUST / NEVER / GATE.

## What's inside
- **Ch.0 Invariants & Pre-Flight** — 12 non-negotiable rules + a pre-flight checklist
- **Ch.1 Canonical Reference** — contract map, entrypoints, quote→swap path, fee model
- **Ch.2 Playbooks** — trade safely · provide LP & earn fees · manage/recenter a range
- **Ch.3 Failure Modes & Recovery** — stuck-nonce/RBF, partial fills, stale data, escalation
- **Ch.4 Strategy & Alpha** — range width vs adverse selection, inventory balancing, yield routing
- **Ch.5 Operator & Escalation Overlay** — autonomy tiers, safe/dangerous ops, stop-and-hand-off
- **Ch.6 Observability, Ledgers & Reporting** — the two ledgers, fee attribution
- **Ch.7 Approval Scopes, Authority & Custody** — scope grammar, spend limits, key custody
- **Ch.8 Skill Authoring & Conformance** — how to build a skill that *imports* this handbook

## How to use it
Skills should **import Chapter 0's invariants, not copy constants** (see Ch.8). All
contract addresses and limits are **point-in-time — verify on-chain before signing.**

## ⚠️ Safety & disclaimer
- **Not financial advice.** Provided "as is", without warranty.
- **Mainnet only. Real funds are at risk.** You are responsible for every transaction your agent signs.
- **Verify everything on-chain.** Addresses, entrypoints, and limits change; this document is a guide, not an oracle.
- HODLMM contracts have no admin keys and no oracle; safety comes from post-conditions and contract-level bounds — which only protect you if you set them.

## Scope & omissions
This public edition intentionally **excludes Bitflow internal infrastructure, operational
endpoints, incident runbooks, and deployment topology.** It covers what an agent needs to
act safely against public contracts and APIs.

## Contributing
Skills are submitted via the [AIBTC skills registry](https://aibtc.com/skills). Follow the
Ch.8 conformance checklist and the registry's SKILL.md/AGENT.md conventions.

## Versioning
Handbook is versioned (currently v0.5). Skills pin the version they conform to.

## Security
Report vulnerabilities responsibly via <security contact> — do not open public issues for
fund-affecting bugs.

## License
CC BY 4.0 for docs
