#!/usr/bin/env python3
"""Docs lint for the guides repo. Stdlib only; exits non-zero on any finding.

Checks:
  1. Runbook frontmatter schema (name/type/handbook/enforces/skills/status) and that every
     `enforces:` invariant is actually defined in the handbook.
  2. KB content-page frontmatter schema (type/handbook/status/sources).
  3. Each runbook's body "Conforms to ... **vX.Y**" line matches its frontmatter pin.
  4. Cross-document handbook-version consistency: templates and navigational docs
     (READMEs, operating guide, authoring guide, VERSIONING.md, llms.txt) must declare the
     CURRENT handbook version, read from the handbook's own banner. Content docs (runbooks,
     KB pages) may pin any version <= current.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HANDBOOK = ROOT / "public/hodlmm/handbook/HODLMM-Agent-Handbook.md"

RUNBOOK_STATUSES = {"draft", "active", "deprecated"}
KB_STATUSES = {"active", "stale", "deprecated"}
KB_TYPES = {"kb-pool", "kb-lessons"}

errors = []


def err(path, msg):
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def read(path):
    return path.read_text(encoding="utf-8")


def parse_frontmatter(text):
    """Minimal YAML-ish frontmatter parser: `key: value` pairs, trailing # comments stripped,
    inline lists kept as raw strings. Returns None if no frontmatter block."""
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        line = re.sub(r"\s+#.*$", "", line).rstrip()
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip()
    return fm


def parse_version(v):
    m = re.fullmatch(r"v(\d+)\.(\d+)", v or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def inv_ids(list_str):
    return set(re.findall(r"INV-(\d+)", list_str or ""))


# --- Handbook: current version + defined invariants -------------------------------------------
handbook_text = read(HANDBOOK)
banner = re.search(r"Community Edition · v(\d+\.\d+)", handbook_text)
if not banner:
    err(HANDBOOK, "cannot find version banner ('Community Edition · vX.Y')")
    print("\n".join(errors))
    sys.exit(1)
CURRENT = f"v{banner.group(1)}"
CURRENT_T = parse_version(CURRENT)

defined_invs = set(re.findall(r"\*\*INV-(\d+) —", handbook_text))
if not defined_invs:
    err(HANDBOOK, "no invariant definitions ('**INV-n — ...') found")
max_inv = max(int(i) for i in defined_invs) if defined_invs else 0

if f"| {CURRENT} |" not in handbook_text:
    err(HANDBOOK, f"Appendix C change log has no row for current version {CURRENT}")


def check_pin(path, fm, key="handbook"):
    """Pin must be a valid vX.Y and <= current. Returns the parsed pin or None."""
    pin = parse_version(fm.get(key, ""))
    if pin is None:
        err(path, f"frontmatter `{key}:` missing or not vX.Y (got {fm.get(key)!r})")
    elif pin > CURRENT_T:
        err(path, f"frontmatter `{key}: {fm[key]}` is ahead of handbook {CURRENT}")
    return pin


# --- Runbooks ----------------------------------------------------------------------------------
runbooks = sorted(ROOT.glob("public/**/*-runbook.md"))
if not runbooks:
    err(ROOT / "public", "glob found no runbooks — lint paths are stale")

for rb in runbooks:
    text = read(rb)
    fm = parse_frontmatter(text)
    if fm is None:
        err(rb, "missing frontmatter block")
        continue
    for key in ("name", "type", "handbook", "enforces", "skills", "status"):
        if key not in fm:
            err(rb, f"frontmatter missing `{key}:`")
    if fm.get("type") != "runbook":
        err(rb, f"frontmatter `type:` should be 'runbook' (got {fm.get('type')!r})")
    if fm.get("status") not in RUNBOOK_STATUSES:
        err(rb, f"frontmatter `status:` must be one of {sorted(RUNBOOK_STATUSES)} (got {fm.get('status')!r})")
    unknown = inv_ids(fm.get("enforces")) - defined_invs
    if unknown:
        err(rb, f"`enforces:` cites undefined invariant(s): {', '.join('INV-' + i for i in sorted(unknown, key=int))}")
    pin = check_pin(rb, fm)

    # Body conformance line must match the frontmatter pin.
    body = text.split("---", 2)[-1]
    bold = re.search(r"\*\*v(\d+\.\d+)\*\*", body)
    if pin and bold and parse_version(f"v{bold.group(1)}") != pin:
        err(rb, f"body declares **v{bold.group(1)}** but frontmatter pins {fm['handbook']}")

    # Templates must pin the CURRENT version so new docs never inherit a stale pin.
    if rb.name.startswith("_TEMPLATE") and pin and pin != CURRENT_T:
        err(rb, f"template pins {fm['handbook']} — must pin current {CURRENT}")

# --- KB content pages ---------------------------------------------------------------------------
kb_pages = sorted(ROOT.glob("public/hodlmm/knowledge/pools/*.md")) + sorted(
    ROOT.glob("public/hodlmm/knowledge/lessons/*.md")
)
for page in kb_pages:
    if page.name == "README.md":
        continue
    fm = parse_frontmatter(read(page))
    if fm is None:
        err(page, "missing frontmatter block")
        continue
    if fm.get("type") not in KB_TYPES:
        err(page, f"frontmatter `type:` must be one of {sorted(KB_TYPES)} (got {fm.get('type')!r})")
    if fm.get("status") not in KB_STATUSES:
        err(page, f"frontmatter `status:` must be one of {sorted(KB_STATUSES)} (got {fm.get('status')!r})")
    if "sources" not in fm:
        err(page, "frontmatter missing `sources:`")
    pin = check_pin(page, fm)
    if page.name.startswith("_TEMPLATE") and pin and pin != CURRENT_T:
        err(page, f"template pins {fm['handbook']} — must pin current {CURRENT}")

# --- Cross-document version consistency ---------------------------------------------------------
MUST_DECLARE_CURRENT = [
    (ROOT / "public/hodlmm/README.md", rf"currently \*\*{re.escape(CURRENT)}\*\*"),
    (ROOT / "public/hodlmm/operating-guide/hodlmm-operating-guide.md", rf"Conforms to .*\*\*{re.escape(CURRENT)}\*\*"),
    (ROOT / "public/hodlmm/runbooks/AGENT-AUTHORING-GUIDE.md", rf"Currently \*\*{re.escape(CURRENT)}\*\*"),
    (ROOT / "public/hodlmm/runbooks/AGENT-AUTHORING-GUIDE.md", rf"handbook: {re.escape(CURRENT)}"),
    (ROOT / "VERSIONING.md", rf"handbook: {re.escape(CURRENT)}"),
    (ROOT / "llms.txt", rf"handbook {re.escape(CURRENT)}"),
]
for path, pattern in MUST_DECLARE_CURRENT:
    if not path.exists():
        err(path, "file missing")
    elif not re.search(pattern, read(path)):
        err(path, f"does not declare current handbook version {CURRENT} (pattern: {pattern})")

# Authoring guide must state the full invariant range.
auth_guide = ROOT / "public/hodlmm/runbooks/AGENT-AUTHORING-GUIDE.md"
if auth_guide.exists() and f"`INV-1`…`INV-{max_inv}`" not in read(auth_guide):
    err(auth_guide, f"invariant range should read `INV-1`…`INV-{max_inv}`")

# --- Report -------------------------------------------------------------------------------------
if errors:
    print(f"docs-lint: {len(errors)} finding(s) against handbook {CURRENT} (INV-1…INV-{max_inv}):\n")
    print("\n".join(f"  - {e}" for e in errors))
    sys.exit(1)

print(f"docs-lint: OK — handbook {CURRENT}, {len(runbooks)} runbooks, "
      f"{len(kb_pages)} KB pages, invariants INV-1…INV-{max_inv}")
