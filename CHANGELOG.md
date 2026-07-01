# Changelog

All notable changes to the **Guides for AI Bitcoin Agents** are recorded here.

- Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Repo versioning: **[Semantic Versioning](https://semver.org/)** at the repo level — `vMAJOR.MINOR.PATCH`,
  published as GitHub **Releases / tags**.
- Per-document versions live in each file's frontmatter (`version:` / `updated:` / `handbook:` / `status:`).
- This file is the source for Release notes.

## [Unreleased]

---

## [0.7.0] - 2026-07-01

Volatile-pair market-making plus two safety/recovery gaps closed, and the Knowledge Base aggregation layer over Campaign Closeouts. Promotes the handbook to **v0.7**.

### Added
- **Handbook v0.7 doctrine** — `INV-13` (gate every write on the divergence & feed-safety tier:
  aligned / defensive / abnormal; the `d_warn < d_halt` ordering invariant; a fixed, absolute peg band;
  feed-lag vs decoupling disambiguation), **Ch.3 §3.7** (stuck-tx root-cause discrimination — RBF only
  cures underpricing; an oversized/read-ceiling tx must be replaced, not repriced), and the **Ch.4 §4.4**
  asymmetric-inventory extension (V-only soft/hard caps for volatile/cash pairs). Version banner +
  Appendix C change-log bumped v0.6 → v0.7.
- **Volatile major / cash-pair market-making profile** — operating-guide §3.2 profile + a cross-cutting
  safety/recovery block (§3.3), and six new runbooks: `hodlmm-volatile-pair-mm`, `hodlmm-divergence-safety`,
  `hodlmm-stuck-transaction`, `hodlmm-adverse-selection`, `hodlmm-pair-calibration`, and the shared
  `peg-monitor-runbook`. Inventory-balancing runbook gains an asymmetric-inventory addendum; README
  catalogs updated. All parameters are operator-tunable `[bracket]` values over public contracts/APIs.
- **Knowledge Base** (`public/hodlmm/knowledge/`) — an LLM-maintained, git-versioned distillation of
  accepted Campaign Closeout issues: per-pool playbooks (`pools/`, seeded with `dlmm_6`), a
  cross-campaign lessons & failure-pattern catalog organized by the six `INV-12` memory categories
  (`lessons/lessons-catalog.md`), an append-only ingestion `log.md`, and the maintainer schema
  `KB-MAINTAINER-GUIDE.md` (INGEST / QUERY / LINT). Closeout issues stay the authoritative raw source;
  agents read the KB, maintainers write it via PR. Wired into `CONTRIBUTING.md`, the closeout runbook,
  and the autonomous-campaign prompt.

### Fixed
- **Skill-reference accuracy** — verified every runbook's command surface (subcommands, flags, confirm
  tokens) against each skill's `SKILL.md` in **`aibtcdev/skills`**. All asserted forms matched
  (`--confirm=DEPOSIT/SWAP/BALANCE/MAXIMIZE`, `hodlmm-move-liquidity` bare `--confirm`, etc.). Corrected
  three frontmatter/text items: removed `bitflow-earnings-card` from the PnL runbook `skills:` (the
  earnings card renders from the BFF API, not a registry skill); removed `memory` from the Closeout
  runbook `skills:` (runtime capability, not a registry skill); pinned the Exit runbook withdraw confirm
  token to `--confirm=EXIT`.

---

## [0.6.0] - 2026-06-26

First public, fully-structured release of the HODLMM agent guides.

### Added
- **Handbook (Community Edition) v0.6** — Ch.0 Invariants/Pre-Flight · Ch.1 Canonical Reference ·
  Ch.2 Playbooks · Ch.3 Failure & Recovery · Ch.4 Strategy & Alpha · Ch.5 Operator Overlay ·
  Ch.6 Observability/Ledgers · Ch.7 Approval Scopes/Custody · Ch.8 Skill Authoring + appendices A–C.
- **Impermanent-loss doctrine** — Handbook **§6.6** (definition + net-PnL identity) and the §4.2
  width↔IL note, the operating-guide "Managing impermanent loss" subsection, and the IL/PnL core of
  `hodlmm-pnl-runbook.md`.
- Repo structure: `public/{README, hodlmm/{handbook, operating-guide, runbooks}, shared}`.
- Operating guide (with strategy-profiles table); runbook **template**; **AGENT-AUTHORING-GUIDE**.
- **Runbooks** — `hodlmm-active-lp-management-runbook` (active); `hodlmm-exit-runbook`,
  `hodlmm-campaign-entry-runbook`, `hodlmm-recenter-runbook`, `hodlmm-inventory-balancing-runbook`,
  `hodlmm-pnl-runbook`, `hodlmm-closeout-runbook` (draft); plus shared `sbtc-yield-routing-runbook` (draft).
- `hodlmm-autonomous-campaign-prompt` — tiered intake (mandatory → basic-with-defaults → advanced gate)
  with a recommended-defaults table and the authority-vs-tuning safety line.
- **Campaign Closeout standard** — repo-root `CONTRIBUTING.md` (single-issue learning loop),
  `.github/ISSUE_TEMPLATE/campaign-closeout.yml` + `config.yml`, and `.github/PULL_REQUEST_TEMPLATE.md`;
  hooks in the campaign prompt, operating guide, and a Handbook Ch.6 note. Agents submit one closeout
  issue; maintainers open any PRs.
- **Repo governance** — `CHANGELOG.md` + `VERSIONING.md` (repo-level SemVer, GitHub Releases as the
  authoritative version line).
- Onboarding notes, SECURITY, CONTRIBUTING (handbook), LICENSE (CC BY 4.0).

### Changed / Fixed
- Resolved DLMM **core/router contract IDs** and split the two deployers (`SP1PFR4V08…` core,
  `SM1FKX…` routers/pools).
- Corrected **INV-2** to the two-form rule (swap = Deny post-conditions; LP = Allow + contract bounds).
- Reclassified the bin-cap / read-ceiling `‹VERIFY›` items as non-load-bearing.
- Removed the agent-irrelevant fee address; generalized internal-infra wording for public release.

---

### Versions in this release

| Document | Version | Status |
|---|---|---|
| Handbook | 0.6 | published |
| Operating guide | 1.0 | published |
| Autonomous campaign prompt | 1.0 | published |
| Runbook template / Authoring guide | 1.0 | published |
| Active LP Management runbook | 1.0 | active |
| Exit runbook | 0.1 | draft |
| Campaign Entry runbook | 0.1 | draft |
| Recenter runbook | 0.1 | draft |
| Inventory Balancing runbook | 0.1 | draft |
| PnL runbook | 0.1 | draft |
| Closeout runbook | 0.1 | draft |
| sBTC Yield Routing runbook (shared) | 0.1 | draft |
