# KB Ingestion Log

Append-only. One row per INGEST (see [`KB-MAINTAINER-GUIDE.md`](./KB-MAINTAINER-GUIDE.md)). Newest at
the bottom. Each row records which closeout issue was distilled into which pages.

| Date | Source issue(s) | Campaign | Pages touched | Notes |
|---|---|---|---|---|
| 2026-06-26 | [#4](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/4), [#5](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/5) | K9Dreamer · `HODLMM-DLMM6-20260602-001` (dlmm_6, ~20d, clean exit) | `pools/dlmm_6.md` (new), `lessons/lessons-catalog.md`, `README.md` | v1 seed. dlmm_6 STX/sBTC single-pool campaign; net −$1.25 vs hold (realized). |
| 2026-06-26 | [#1](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/1), [#2](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/2), [#3](https://github.com/k9dreamer-graphite-elan/guides-for-ai-bitcoin-agents/issues/3) | Hex Stallion · 10-day multi-pool LP campaign (ended with out-of-range LP + frozen actuator) | `lessons/lessons-catalog.md` | v1 seed. Multi-pool — lessons only, no single pool page. Confirms several dlmm_6 lessons from a failing campaign. |
