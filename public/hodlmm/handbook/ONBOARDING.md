# Onboarding — handing this handbook to an agent or operator

Copy-paste the note that fits your reader. Both assume the agent/operator also has access to
[`HODLMM-Agent-Handbook.md`](./HODLMM-Agent-Handbook.md).

---

## For an autonomous agent

Paste into the agent's instructions / system prompt:

> You operate on Bitflow HODLMM. Before any trade or LP action, load the **HODLMM Agent Handbook** and
> treat **Chapter 0 (Invariants & Pre-Flight) as binding** — not advisory.
>
> - Run every action through the loop: `SCAN → DECIDE → DRY-RUN → EXECUTE → VERIFY → REMEMBER → MEASURE`.
> - **Never broadcast** unless the Ch.0 pre-flight checklist passes: in-scope, fresh scan, bounded swap
>   (`*-simple-range-multi`, `max-steps ≤ 230`), correct fund-protection (swap = Deny post-conditions;
>   LP = `min-dlp` / fee-cap / active-bin bounds), nonce serialized, ledgers written.
> - **Verify every address/limit on-chain before signing** — the handbook is point-in-time, not an
>   oracle. Mainnet, real funds.
> - Dry-run first; only execute with the explicit confirm token. Stay inside your Approval Scope.
> - **When uncertain, stop and escalate** — never act unilaterally on suspected fund-risk or key
>   exposure.
>
> Cite the handbook's invariants by ID (e.g. INV-3); do not copy or re-derive its constants.

---

## For a human operator

Paste into Slack / email:

> Sending you the **HODLMM Agent Handbook (Community Edition)** — the safety + operating manual for
> trading and LPing on Bitflow HODLMM.
>
> - Start with **Chapter 0** (the non-negotiable invariants) and **Chapter 5** (what the agent will /
>   won't do autonomously, and when it escalates to you).
> - Before letting an agent execute, grant it an **Approval Scope** (Ch.7): which pool(s), how many
>   days, which permissions (`manage-existing` / `add-new` / `withdraw` / `swap`), and caps. Anything
>   outside that stays read-only.
> - It defaults to **dry-run**; real writes need an explicit confirm token. Expect it to **page you**
>   on repeated tx failures, suspected fund-risk, or anything out of scope.
> - It's a guide, not financial advice — mainnet, real funds. Skim the disclaimer in the README.

---

## One-liner

> HODLMM Agent Handbook — read Chapter 0 first; it's the safety floor. Verify on-chain, dry-run before
> you sign, stay in scope, escalate when unsure.
