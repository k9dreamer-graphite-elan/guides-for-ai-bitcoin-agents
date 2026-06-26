# Versioning

How versions work in this repo, so contributors and agents can rely on them.

## Two layers

1. **GitHub Releases / tags — authoritative.** The repo is versioned with Semantic Versioning at the
   repo level: `vMAJOR.MINOR.PATCH`. Each meaningful change set ships as a GitHub **Release** (an
   annotated tag + notes). Releases are immutable snapshots and appear in the repo's **Releases** tab.
   - `MAJOR` — breaking change to doctrine (e.g., an invariant changes meaning).
   - `MINOR` — new chapter / runbook / guide, or a constant update.
   - `PATCH` — fixes, clarifications, typos.
2. **Per-document frontmatter — self-reporting.** Every doc declares its own version so you can tell
   what you're reading without checking the release:
   ```yaml
   ---
   version: 1.0          # this document's own version
   updated: 2026-06-03   # ISO date of last change
   handbook: v0.6        # (docs that conform to the handbook) the doctrine version they target
   status: active        # (runbooks) draft | active | deprecated
   ---
   ```

The **Release bundles** the current document versions; the **`CHANGELOG.md`** maps each release to what
changed and which doc versions it contains.

## Cutting a release

**GitHub UI:** Releases → *Draft a new release* → choose/create tag `v0.6.0` (target `main`) → title
`HODLMM Agent Guides v0.6.0` → paste the matching `CHANGELOG.md` section → *Publish release*.

**CLI (git):**
```bash
git tag -a v0.6.0 -m "HODLMM Agent Guides v0.6.0"
git push origin v0.6.0
```

**CLI (gh):**
```bash
gh release create v0.6.0 --title "HODLMM Agent Guides v0.6.0" --notes-file CHANGELOG.md
```

## Pinning an exact version (for agents / skills)

When an agent or skill must reference a *fixed* version of a file, use a **commit- or tag-pinned
permalink**, never the `main` URL (which moves):
- On GitHub, open the file and press **`y`** → the URL rewrites to the commit SHA. Copy that.
- Or reference the tag: `…/blob/v0.6.0/public/hodlmm/handbook/HODLMM-Agent-Handbook.md`.

## When to bump what

- Edit a runbook's steps → bump that runbook's frontmatter `version`, update `CHANGELOG.md` `[Unreleased]`.
- Change a handbook constant or invariant → bump the handbook `version`, and bump every conforming doc's
  `handbook:` field; cut at least a `MINOR` repo release.
- Ship a batch → move `[Unreleased]` into a new dated `[x.y.z]` section and tag the release.

## Optional: component tags

If documents later need independent release cadences, GitHub allows component-scoped tags
(`handbook-v0.7`, `campaign-prompt-v1.1`) alongside the repo `vX.Y.Z` line. Keep to repo-level releases
until that's actually needed.
