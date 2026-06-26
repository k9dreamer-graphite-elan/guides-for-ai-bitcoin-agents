# Changelog

All notable changes to the **Guides for AI Bitcoin Agents** are recorded here.

- Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Repo versioning: **[Semantic Versioning](https://semver.org/)** at the repo level — `vMAJOR.MINOR.PATCH`,
  published as GitHub **Releases / tags**.
- Per-document versions live in each file's frontmatter (`version:` / `updated:` / `handbook:` / `status:`).
- This file is the source for Release notes.

## [Unreleased]

### Added
- **Campaign Closeout standard** — `public/hodlmm/runbooks/hodlmm-closeout-runbook.md`, repo-root
  `CONTRIBUTING.md` (single-issue learning loop), `.github/ISSUE_TEMPLATE/campaign-closeout.yml` +
  `config.yml`, and `.github/PULL_REQUEST_TEMPLATE.md`; hooks in the campaign prompt, operating guide,
  and a Handbook Ch.6 note. Agents submit one closeout issue; maintainers open any PRs.
- **Impermanent-loss sections** — Handbook **§6.6** (definition + net-PnL identity) and the §4.2
  width↔IL note, the operating-guide "Managing impermanent loss" subsection, and the IL/PnL core of
  `hodlmm-pnl-runbook.md`.

### In progress
- Verify skill command surfaces against each skill's `SKILL.md` in **`aibtcdev/skills`** (references are
  valid — confirmed via `skills.json`; no remap needed).

---

## [0.6.0] - 2026-06-XX

First public, fully-structured release of the HODLMM agent guides.

### Added
- **Handbook (Community Edition) v0.6** — Ch.0 Invariants/Pre-Flight · Ch.1 Canonical Reference ·
  Ch.2 Playbooks · Ch.3 Failure & Recovery · Ch.4 Strategy & Alpha · Ch.5 Operator Overlay ·
  Ch.6 Observability/Ledgers · Ch.7 Approval Scopes/Custody · Ch.8 Skill Authoring + appendices A–C.
- Repo structure: `public/{README, hodlmm/{handbook, operating-guide, runbooks}, shared}`.
- Operating guide (with strategy-profiles table); runbook **template**; **AGENT-AUTHORING-GUIDE**.
- Runbooks: `hodlmm-active-lp-management-runbook` (active), `hodlmm-exit-runbook` (draft).
- `hodlmm-autonomous-campaign-prompt` — tiered intake (mandatory → basic-with-defaults → advanced gate)
  with a recommended-defaults table and the authority-vs-tuning safety line.
- Onboarding notes, SECURITY, CONTRIBUTING, LICENSE (CC BY 4.0).

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
| Active LP Management runbook | 1.0 | active |
| Exit runbook | 0.1 | draft |
| Runbook template / Authoring guide | 1.0 | published |
