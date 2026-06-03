# Security Policy

## Scope

This repository is **documentation** — a guide for autonomous agents operating on Bitflow HODLMM. It
contains no private keys, secrets, or credentials, and ships no executable that moves funds.

## Reporting a vulnerability

If you find an error in this handbook that could lead an agent to **lose or risk funds** (e.g. an
incorrect contract address, a wrong invariant, an unsafe entrypoint or post-condition recommendation):

- **Do not open a public issue.** Report it privately to the maintainers / the Bitflow team through a
  secure channel.
- Include the exact section, the claimed fact, and the corrected/verified value (ideally with an
  on-chain reference such as a Hiro `/v2/contracts/interface` or `/v2/contracts/source` result).

For vulnerabilities in the Bitflow **protocol or contracts** themselves (not this document), use
Bitflow's official disclosure channel.

## Operating guidance for agents

The handbook itself is the security guidance. The load-bearing rules:

- **Verify every address and limit on-chain before signing** — this document is point-in-time.
- **Never pass secrets as CLI arguments**; use environment variables and re-lock after writes
  (Ch.7 §7.3).
- **Use bounded swap entrypoints and attach the correct fund-protection** for every write (INV-2/3).
- **When in doubt, stop and escalate** — never act unilaterally on a suspected fund-risk or
  key-exposure event (Ch.3 §3.6, Ch.5).
