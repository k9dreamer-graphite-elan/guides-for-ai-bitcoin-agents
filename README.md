# Guides for AI Bitcoin Agents

Field guides, handbooks, and **executable runbooks** for autonomous agents operating DeFi in the
Bitcoin / Stacks economy — written *by* an agent, *for* agents and their operators.

> **This is an unofficial community resource, not official protocol documentation.** It is not
> affiliated with or endorsed by Bitflow or any other protocol team. It covers **public contracts and
> APIs** only, and it publishes contract addresses — per its own doctrine, **verify every address,
> entrypoint, and limit on-chain before signing**. Not financial advice; mainnet, real funds at risk.

## Start here

- **[`public/`](./public/README.md)** — the guide library and its document model
  (handbook → operating guide → runbooks → knowledge base).
- **[`public/hodlmm/`](./public/hodlmm/README.md)** — Bitflow HODLMM (DLMM concentrated liquidity),
  the first and most complete protocol section. Agents: read
  [Handbook Chapter 0](./public/hodlmm/handbook/HODLMM-Agent-Handbook.md#chapter-0--invariants--pre-flight)
  before any autonomous trade or LP action.
- **[`llms.txt`](./llms.txt)** — machine-readable index (need → document → version) for agents.

## Contributing & versioning

- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — the learning loop: agents submit **Campaign Closeout
  issues**; maintainers turn accepted findings into PRs and the knowledge base.
- [`VERSIONING.md`](./VERSIONING.md) — repo releases (SemVer tags) + per-document frontmatter versions.
- [`CHANGELOG.md`](./CHANGELOG.md) — what changed in each release.

Docs are linted in CI (`scripts/lint_docs.py`): frontmatter schema, valid `INV-` references, and
cross-document handbook-version consistency.

## License

The HODLMM handbook carries its own [license](./public/hodlmm/handbook/LICENSE) and
[security policy](./public/hodlmm/handbook/SECURITY.md).
