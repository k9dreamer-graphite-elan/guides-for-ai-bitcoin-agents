<!--
  For MAINTAINERS opening a PR from an accepted closeout issue.
  Contributing agents submit ISSUES, not PRs (see CONTRIBUTING.md).
  Guide changes should be ADDITIVE and follow the AGENT-AUTHORING-GUIDE.
-->

## Summary

What this changes and why (1–3 lines).

## Source

- Closes: #<closeout issue>
- Campaign ID(s): `HODLMM-…`
- Built against commit: `<sha>`

## Changes (additive docs)

- [ ] `path/to/file` — what changed

## Conformance checklist (AGENT-AUTHORING-GUIDE)

- [ ] Cites handbook invariants by ID; **no restated handbook constants**
- [ ] No hardcoded mutable state / invented addresses or limits
- [ ] Hyphenated filenames; relative links resolve
- [ ] Frontmatter `version` / `updated` / `handbook` bumped where edited
- [ ] `CHANGELOG.md` updated; version/release implications noted
- [ ] If a constant/invariant changed: conforming docs' `handbook:` bumped
