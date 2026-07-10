# Changelog

All notable changes to the **Guides for AI Bitcoin Agents** are recorded here.

- Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Repo versioning: **[Semantic Versioning](https://semver.org/)** at the repo level — `vMAJOR.MINOR.PATCH`,
  published as GitHub **Releases / tags**.
- Per-document versions live in each file's frontmatter (`version:` / `updated:` / `handbook:` / `status:`).
- This file is the source for Release notes.

## [Unreleased]

### Changed
- **`hodlmm-pnl-runbook` — Campaign PnL Report contract (medium-agnostic), card demoted to a renderer**
  ([#37](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/37), field
  basis [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)).
  The honest hierarchy — `NET PnL after gas` as the sole hero, `% vs hold, after gas` on the
  **deployed-basis** `V_hold`, deployed hold baseline (USD + native inventory) and final inventory as
  core rows, `Earnings`/`Fee/TVL`/`Gas` as **subordinate, non-additive** context — is now a
  **text/markdown report contract** that ships in *every* channel (CLI, Claude Code, LLM turn, GitHub
  issue) whenever the operator runs PnL. The Bitflow PNG earnings card is reframed as **one renderer
  of that same object, image-channels only (TG/Discord/social)** and never a substitute for the text
  report. Adds the period-label rule (never hardcode `7D`; derive from campaign vs report basis and
  record the source), the low-confidence/display-only earnings guardrail, `Fee/TVL` spelling, and
  `report_period`/`period_source`/`final_inventory_mark` output fields. Card layout, dynamic-period
  code, and renderer tests remain in the agent-workspace generator script, out of scope for this repo.

### Added
- **KB: Hex Stallion `dlmm_1` control-plane closeout addendum ingested**
  ([#35](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/35)): new
  **LSN-0017** — disarm is host-level; no signer-enabled process may outlive campaign closure. A
  campaign's exit, zero-DLP proof, and PnL were all valid, yet a *generic, signer-enabled* resident
  stayed loaded against a separate ended campaign via an **implicit campaign default** (no tx
  submitted, but stale `rebalance,exit` authority survived closure). Adds a **host-level disarm
  proof** checklist to the `hodlmm-closeout-runbook` terminal gates (enumerate generic + specific
  schedules, verify no signer-enabled process references the campaign, reconcile repository ↔
  installed ↔ loaded config, prove the runtime fails closed before heartbeat launch) and extends the
  `hodlmm-unattended-automation-runbook` DISARM step to the same host-level proof. Extends LSN-0015
  from the campaign-specific write-path gate to the shared control plane.
- **KB: Hex Stallion `7D-LP-Campaign-2` (dlmm_1) field report ingested**
  ([#11 update](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11#issuecomment-4931652170), exit tx chain-verified): new **LSN-0016** — auxiliary-data failures must
  not block a bounded terminal exit, and closure-proof acceptance = confirmed withdraw + zero user
  bins + zero/absent DLP; **LSN-0015 extended** with the failure-side evidence (post-deadline
  repair path re-entered the pool three times on-chain) and broadened to cover ALL write paths
  incl. missing-LP re-entry/top-up. Full closeout issue + `pools/dlmm_1.md` second-campaign update
  invited from the Hex Stallion team.

---

## [0.9.3] - 2026-07-10

Accounting-precision patch: the component-basis convention from the campaign-003 methodology
sign-off, prompted by a downstream analyzer and the closeout report publishing different (both
correct) hold/exit component values from the same campaign. No handbook doctrine changes — the
handbook stays at **v0.9**.

### Added
- `hodlmm-pnl-runbook` — field-confirmed addendum: **component basis conventions** (from the
  [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28)
  methodology sign-off). Every PnL component states its basis: deployed basis for attribution and
  all percentages (canonical `V_hold`), campaign-total basis for wallet reconciliation only; the
  net headline is basis-invariant but component absolutes are not. Includes the event-level
  "no intermediate legs" check that atomic native recenters emit only DLP events.

---

## [0.9.2] - 2026-07-10

The unattended-automation release: the harness doctrine for scheduled monitor/executor loops arrives
as a new runbook and earns `active` within the same cycle, proven end-to-end by the dlmm_1
campaign-003 closeout (#28) — the first campaign with an unattended gated auto-repair and a clean
scheduled planned-end exit. Bundles the #26 runbook status promotions, the campaign's
field-confirmed addenda (incl. the campaign tx-attribution convention), and its KB ingest (first
sBTC/USDCx pool page, LSN-0013–0015). No handbook doctrine changes — the handbook stays at
**v0.9**, so this ships as a patch.

### Added
- **New runbook: `hodlmm-unattended-automation-runbook`** (`draft`) — the harness doctrine for
  scheduled monitor/executor loops: day-0 environment parity (explicit PATH, `env -i` dry-run of
  every action branch, flag verification against the installed skill), per-tick write gates
  (INV-7/INV-13, N-scan confirmation, charter caps, serialized nonces), external watchdog +
  failure alerts, actuator-chain verification (LSN-0011), halt-after-N-fail with operator-only
  resume, terminal-trigger rehearsal, and disarm-at-close. Consolidates the automation lessons
  from closeouts [#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21)/[#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22)
  (dlmm_3 campaign-002 scheduled-exit failure), [#11–#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)
  (actuator chain), and [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)/[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5),
  previously scattered as addenda. Started `draft` per the §3 lifecycle; promoted to `active` in
  this same cycle on the dlmm_1 campaign-003 closeout (see Changed below).

- **Field-confirmed addenda from the dlmm_1 campaign-003 closeout**
  ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28) —
  K9Dreamer `HODLMM-DLMM1-20260702-003`, sBTC/USDCx 7d, clean scheduled exit, net ≈ +$9 vs hold
  after gas at the 3.0 STX gas cap, 16 gated recenters incl. one unattended auto-repair):
  - `hodlmm-closeout-runbook` (v0.3) — two addenda: (1) closeout belongs in the terminal
    checklist — a campaign is `operationally_closed` only after exit proof + PnL report + a posted
    closeout issue or saved unposted draft; (2) campaign tx attribution without extra gas — per-tx
    `campaign_id` / `tx_role` / `campaign_state_after_tx` in reports (roles: OPEN / REPAIR /
    WITHDRAW / MOVE / REBAL / EXIT / CLOSE; `EXIT` is terminal-only), zero-gas default (no marker
    txs), optional memo rule only when a memo-bearing tx is already being sent.
  - `hodlmm-exit-runbook` + `hodlmm-recenter-runbook` — **fee bumping is a new approval scope**:
    if the configured fee target fails, stop and alert; never auto-bump. Recenter also gains:
    repair-count caps are campaign policy (the gate stack is the safety invariant), and invariants
    must be enforced at sign time, not only at dry-run time (a pre-sign active-bin refresh can
    shift the executed destination).
  - `hodlmm-active-lp-management-runbook` — autonomous repair loops must read campaign lifecycle
    before signing and refuse post-planned-end writes without a renewal scope; codifies the
    guarded-repair-daemon shape as the unattended-automation runbook's per-tick write branch.

- **KB ingest: dlmm_1 campaign-003 closeout ([#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28))** —
  `knowledge/pools/dlmm_1.md` (new, first sBTC/USDCx pool page), three new lessons
  (LSN-0013 single-source active-bin read jitter → multi-source agreement gate; LSN-0014 fee bumping
  is a new approval scope; LSN-0015 autonomous repair loops must read campaign lifecycle before
  signing), confirmations of LSN-0002/-0007/-0011 from an additional campaign, KB log row, and the
  KB README pool-catalog row.

### Changed
- **Runbook status promotions** (`draft` → `active`, per the AGENT-AUTHORING-GUIDE §3 lifecycle —
  each promotion cites the accepted Campaign Closeout issue(s) that exercised the procedure
  end-to-end on mainnet):
  - `hodlmm-exit-runbook` — chain-proven bounded exits by two independent campaigns on `dlmm_3`:
    K9Dreamer campaign-002 ([#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21),
    exit matched the plan to the µSTX, position/DLP confirmed zero) and Hex Stallion 7D
    ([#11–#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11),
    exit tx verified canonical on Hiro).
  - `hodlmm-recenter-runbook` — dlmm_6 exercised the withdraw → swap → redeposit recenter route
    ([#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)/[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5),
    realized); the Hex Stallion 7D closeout ([#11–#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11))
    exercised staged-repair recenters and fed the continuation state machine back into the runbook (v0.9.1).
  - `hodlmm-pnl-runbook` — full realized vs-hold accounting produced by both closeouts:
    dlmm_6 ([#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)/[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5))
    and dlmm_3 campaign-002 ([#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21),
    gas-inclusive net vs hold, realized on chain).
  - `hodlmm-closeout-runbook` — the procedure has produced three accepted closeout packages:
    dlmm_6 ([#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4)/[#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5)),
    dlmm_3 campaign-002 ([#21](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/21)/[#22](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/22)),
    and the Hex Stallion 7D ingest ([#11–#13](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/11)),
    which also field-confirmed the runbook's outcome taxonomy (v0.9.1).
  - `hodlmm-unattended-automation-runbook` — promoted on the strength of closeout
    [#28](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/28):
    the dlmm_1 campaign-003 ran the doctrine end-to-end on mainnet — day-0-validated script
    monitor, per-tick gated writes, one unattended auto-repair (all gates passed), planned-end
    scheduled exit with renewal check, disarm at close, zero failed broadcasts — including a live
    degraded-LLM fallback (model outage → deterministic zero-LLM monitor), the runbook's own
    prescribed failure mode. README catalog row updated to match.

  Status metadata only (frontmatter `status:` + the hodlmm README catalog table) — no procedure or
  doctrine changes; each runbook's `handbook:` conformance version is unchanged.

---

## [0.9.1] - 2026-07-03

The field-learning layer catching up with two campaigns on the same pool: the KB ingest of both
`dlmm_3` closeout packages (Hex Stallion's 7-day autonomous run, #11–#13, and K9Dreamer's
campaign-002, #21/#22) plus the field-confirmed addenda they produced. No handbook doctrine
changes — the handbook stays at **v0.9**, so this ships as a patch.

### Added
- **Field-confirmed addenda from campaign-002** (PR #23, issues #21/#22): automation environment
  parity — cron/scheduler `PATH` self-setting, dry-running every action branch under the scheduler
  environment before arming, never discarding automation stderr, day-0 signing-CLI flag checks
  (campaign prompt); boundary (floor-pinned) entry geometry and direct-on-chain-read withdraw
  minimums (recenter runbook).
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
