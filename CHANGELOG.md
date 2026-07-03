# Changelog

All notable changes to the **Guides for AI Bitcoin Agents** are recorded here.

- Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Repo versioning: **[Semantic Versioning](https://semver.org/)** at the repo level — `vMAJOR.MINOR.PATCH`,
  published as GitHub **Releases / tags**.
- Per-document versions live in each file's frontmatter (`version:` / `updated:` / `handbook:` / `status:`).
- This file is the source for Release notes.

## [Unreleased]

### Added
- **KB ingest — dlmm_3** (issues #11–#13, Hex Stallion 7-day autonomous campaign; issues #21/#22,
  K9Dreamer campaign-002): new pool page `knowledge/pools/dlmm_3.md` (two independent campaigns,
  both chain-proven clean exits); new lessons **LSN-0011** (tx confirmation is not repair proof —
  prove the actuator chain end-to-end) and **LSN-0012** (a posted contribution is not a closeout —
  report operational / artifact / upstream / accounting-confidence outcomes separately);
  LSN-0005/-0006/-0008 confirmed from a second campaign.
- **Field-confirmed addenda** from the Hex Stallion 7D closeout (#11–#13): lifecycle clocks &
  Day-0 artifacts + clean-slate inventory classification (campaign prompt), actuator failure
  states & separate proof fields (active-LP runbook), staged-repair continuation state machine
  (recenter runbook), closeout outcome taxonomy with `closeout_unresolved` (closeout runbook).

---

## [0.9.0] - 2026-07-02

Two handbook doctrine bumps in one release (no `v0.8.0` was tagged; this bundles both): the **v0.8
on-chain corrective** (inverted bin-side rule, phantom staking, exact step cap) and the **v0.9
refinements** from its third-party verification pass (INV-2 Strict/Simple fund-protection forms;
INV-7 freshness headers + `X-API-Key`). Plus the repo-hygiene layer added alongside v0.8: root
README, `llms.txt`, docs-lint CI, runbook status lifecycle, LF normalization. Promotes the handbook
to **v0.9**; the repo version now tracks the handbook version.

### Changed
- **Handbook v0.9** — doctrine refinements from the third-party verification pass on v0.8
  (issue #18; explicitly deferred from the v0.8 corrective as non-blockers):
  - **INV-2 reframed** as *"use the correct fund-protection form for the variant you call"*, adopting
    the official **Strict vs Simple** LP terminology. The v0.6–v0.8 claim that LP ops *cannot* be
    expressed as sender-side post-conditions held only for the relative/simple variants the approved
    skills call. The **Strict** entrypoints — `add-liquidity-multi` / `withdraw-liquidity-multi` /
    `move-liquidity-multi`, verified on-chain against the live `dlmm-liquidity-router-v-1-2` interface
    (new verification row V8) — take absolute bin-ids and exact per-bin amounts, so they broadcast in
    `PostConditionMode.Deny` **with** sender post-conditions (FT bounds + per-bin conditions), while
    still carrying `min-dlp` / fee-cap args (strict withdraw adds per-bin `min-x/y-amount`). The
    **Simple** variants keep `Allow` + contract bounds. §1.3, §2.0, the pre-flight GATE, Playbooks
    B/C rows, §4.4, §5.2, and §8 updated to the three-form terminology.
  - **INV-7 gains a detection surface** (new verification row V9): request header `X-Allow-Fallback`
    opts into the API's on-chain fallback; response header `X-Data-Fallback-Applied` (observed live,
    2026-07-02, alongside `x-bins-price-source`) plus the docs' data-source/age headers make staleness
    **detectable and controllable** rather than only inferable from the indexer-lag check. The
    fresh-scan-before-broadcast obligation is unchanged. §1.4, §3.1 R4, and §3.4 updated.
  - **`X-API-Key`** — documented as not required during BETA but required later; skills should send it
    now (config-driven, empty-tolerant) or they break silently at the flag-flip (§1.4). Upstream note
    for `aibtcdev/skills` to be filed separately.
  - **Drift fix:** Playbook B still carried a v0.7-era "stake LP shares into `dlmm-staking-…`" bullet
    contradicting v0.8's finding that no staking contracts exist on mainnet (V7); removed.
  - No entrypoint, address, or limit changed — existing `handbook: v0.8` pins remain safe; skills
    adding Strict-form LP writes or the auth/freshness headers should re-pin v0.9. Navigational docs
    and templates bumped to v0.9 per the docs-lint rules.
- **Handbook v0.8 (corrective)** — full on-chain verification pass (2026-07-01) of every published
  address, entrypoint, and limit against live Hiro contract interfaces and source. Three findings
  corrected, one closed as exact:
  - **Bin-side rule was inverted** in v0.6/v0.7 (§1.x bins bullet, §1.3, §6.6, Appendix B V5) and in
    the campaign-entry, recenter, and PnL runbooks. On-chain truth (core `add-liquidity` asserts, and
    confirmed by live dlmm_3 campaign behavior): **above active = X only, below active = Y only**, at
    active = both with the imbalance taxed. Ch.2's placement rules already had it right — the docs
    were internally inconsistent. Agents/skills that encoded the old direction must re-verify.
  - **Staking does not exist on mainnet** — no `dlmm-staking-{pair}` contract or `dlmm-staking-trait`
    in the complete deploy history of any Bitflow deployer; §1.2/§1.3/Ch.2 staking references replaced
    with a not-deployed notice (new verification row V7).
  - **Router step cap is exact, not approximate** — `MAX_STEPS = u319` constant, asserted on every
    swap entrypoint; the "≈350–384 bins" estimate is retired (V3). Classic `*-simple-multi` delegate
    to the range variants with `MAX_STEPS`.
  - Smaller accuracy fixes: quotes-API pool-contract field is `pool_token` (not `pool-contract`);
    per-pool naming is `dlmm-pool-{pair}-v-{n}-bps-{bin-step}`; pool read-only functions are
    `get-bin-balances` / `get-balance` / `get-user-bins` / `get-active-bin-id` (SFT token-id =
    bin-id + 500, per `NUM_OF_BINS u1001` / `CENTER_BIN_ID`, now V6); traits are
    `dlmm-core-trait-v-1-1` / `dlmm-pool-trait-v-1-1`.
  - Verified clean: core/router/liquidity-router contract IDs and deployers, bounded entrypoint names,
    liquidity entrypoints (`add-relative-liquidity-same-multi`, `move-relative-liquidity-multi`),
    permissionless `claim-protocol-fees`, active-bin add-liquidity fee taxation, 1,001 bins at ±500,
    legacy-plane deployer (xyk/stableswap), BFF quotes API base + endpoints.
  - Campaign-entry, recenter, and PnL runbooks re-pinned `handbook: v0.8` (their corrected text
    conforms to the fixed doctrine); navigational docs and templates bumped per the docs-lint rules.

### Added
- **Root `README.md`** — landing page stating what the repo is and its unofficial/community
  relationship to the protocols it documents, with pointers into `public/`.
- **`llms.txt`** — machine-readable index (need → document → version) for agent consumers.
- **Docs lint in CI** (`scripts/lint_docs.py` + `docs-lint` workflow) — validates runbook/KB
  frontmatter schema, that every `enforces:` invariant exists in the handbook, that each runbook body's
  conformance line matches its frontmatter pin, and cross-document handbook-version consistency
  (templates and navigational docs must declare the current version, read from the handbook banner).
- **Runbook status lifecycle** (authoring guide §3) — `draft` → `active` promotion requires an accepted
  Campaign Closeout that exercised the procedure end-to-end on mainnet, cited in the promotion PR;
  demotion rules and `deprecated` successor-naming defined.
- **`.gitattributes`** — all text normalized to LF (previously mixed CRLF/LF across ten files).

### Fixed
- **v0.7 version drift** — the v0.7.0 release bumped the handbook but left stale `v0.6` declarations
  in navigational and template docs. Corrected: `public/hodlmm/README.md` ("currently v0.6"), the
  operating-guide conformance banner (it already gated on INV-13 doctrine), the authoring guide
  (`Currently v0.6`, invariant range `INV-1…INV-12` → `INV-13`, example frontmatter), the runbook and
  KB pool templates' `handbook:` pins, `VERSIONING.md` examples, and the KB maintainer guide's
  frontmatter schema note. Existing runbooks legitimately written against v0.6 doctrine keep their
  pins. Also removed the authoring guide's stale "planned runbooks" list (all five now exist).

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
