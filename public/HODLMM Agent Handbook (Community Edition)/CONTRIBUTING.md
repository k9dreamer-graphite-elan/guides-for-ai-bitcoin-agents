# Contributing

Thanks for helping improve the HODLMM Agent Handbook (Community Edition).

## What belongs here

- Corrections to facts (contract IDs, entrypoints, limits, fee mechanics) — **with an on-chain or
  published-source reference.**
- Clearer phrasings of an invariant, playbook, or recovery procedure.
- New agent-facing guidance that fits the existing chapter structure and the "brakes before alpha"
  ordering.

## What does NOT belong here

- Bitflow internal infrastructure, operational endpoints, deployment topology, or incident runbooks.
- Secrets, keys, credentials, or operational wallet labels.
- Unverified contract addresses or limits. If you can't confirm it on-chain, mark it clearly in the
  verification register (Appendix B), don't assert it.

## How to propose a change

1. Fork and branch.
2. Make the edit. If you change a **constant or contract ID**, bump the handbook version (Appendix C)
   and cite how you verified it (e.g. Hiro `GET /v2/contracts/interface/{principal}/{name}`).
3. Open a PR describing the change and the verification.

## Building skills

Skills that operate on HODLMM should **import this handbook's invariants** rather than re-deriving
them (Chapter 8). Submit skills to the [AIBTC skills registry](https://aibtc.com/skills) following its
`SKILL.md` / `AGENT.md` conventions and the Chapter 8 conformance checklist.

## Style

- Machine-first: `MUST` / `NEVER` / `GATE`. Terse, rule-based.
- No mutable live state baked into the doc (pool lists, TVL, APR, fee rates are queried live).
- Every constant is point-in-time and must be re-verifiable on-chain.
