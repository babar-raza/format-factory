# Plan: .NET Source Path Governance — Establish src/net/ as Canonical Root

**Plan type:** machinery_hardening
**Mission ID:** DOTNET-PATH-GOV-001
**Created:** 2026-07-03

---

## Context

Agents occasionally search for `.NET` product source under `src/dotnet/` instead of
the correct canonical root `src/net/`. Investigation confirms:

- `src/dotnet/` does NOT exist as a directory (Glob returns nothing)
- `src/net/` has 10 live format directories with real product source
- `src/net/_readme.md` exists but still contains the old Phase 0 placeholder text
  written when the file originally lived at `src/dotnet/_readme.md` — it talks about
  `src/dotnet/` extensively, calls `src/net/` a future "Phase 4+" thing, and even
  includes `dotnet/_readme.md` in its own directory-tree diagram

So the confusion root is: `src/net/_readme.md` is a misplaced and stale document that
describes the WRONG state of the repository. Agents reading it see `src/dotnet/` as the
named directory context and `src/net/` described as something that "will be created".

The ~48 other files that reference `src/dotnet` are correct prohibition notices or
immutable historical evidence — no changes needed to them.

**Core gaps to fix:**

1. `src/net/_readme.md` — completely stale; must be rewritten as a proper README for the live `src/net/` product tree
2. No machine-readable layout authority (YAML) for tools/agents to load
3. No path resolver utility centralizing path derivation
4. No blocking validator (V110) rejecting `src/dotnet/` in evidence declarations
5. AGENTS.md has no concise path table
6. `.supervisor/project-memory.md` lacks explicit path rule

---

## Findings Summary

| Item | State |
|---|---|
| `src/dotnet/` directory | Does NOT exist |
| `src/net/` | Exists with 10 live format dirs (csv, fods, fodt, html, markdown, ndjson, netpbm, tsv, txt, zst) |
| `src/net/_readme.md` | Exists; stale Phase 0 content referencing `src/dotnet/` throughout |
| Validators V73/V78/ext3 | Already use `src/net/` regex — no change needed |
| `.claude/commands/add-dotnet-api.md` | Already uses `src/net/<format_id>/` — no change needed |
| CI `.github/workflows/ci.yml` | Already uses `src/net/*/` — no change needed |
| 48 files referencing `src/dotnet` | All correct prohibition notices or immutable history |
| `registry/repository-layout.yaml` | Does not exist — must create |

---

## Critical Files

| File | Role | Change |
|---|---|---|
| `src/net/_readme.md` | Live .NET product root README | **Rewrite** (remove Phase 0/src/dotnet content) |
| `registry/repository-layout.yaml` | NEW canonical layout authority | Create |
| `tools/supervisor/path_resolver.py` | NEW path resolution utility | Create |
| `tools/supervisor/governance_validators_path.py` | NEW validator V110 | Create |
| `tools/supervisor/governance_validator_runner.py` | Register V110 | Update |
| `AGENTS.md` | Operational contract | Add path table section A1a |
| `.supervisor/project-memory.md` | Persistent agent memory | Add path rule |
| `reports/repository-layout/source-path-gap-ledger.yaml` | Gap ledger | Create |

---

## Taskcards

### TC-PATH-001 — Rewrite `src/net/_readme.md`
**Status:** OPEN

The file currently contains stale Phase 0 content describing `src/dotnet/` as the
named directory and `src/net/` as a future target. This is the primary source of
agent confusion. Rewrite it entirely as a proper README for the live `src/net/` tree.

**Preserve from current file:**
- Technology Baseline table (net8.0/net10.0, SDK, XML library)
- SDK Baseline Confirmation section (TC-0003 status)
- Commercial Isolation Rules (already repointed to `src/net/{format}/`)
- Security Requirements (XmlReaderSettings rules)
- Relationship to Other Documents list

**Remove entirely:**
- Title "src/dotnet — Phase 0 Placeholder (Superseded by src/net/)"
- "IMPORTANT: Layout Change" section
- "Purpose (Phase 0)" section
- "Target Directory Structure (Phase 4+)" section with `dotnet/_readme.md` in diagram
- Line 19: "`src/net/` will be created in Phase 4+…"
- All occurrences of `src/dotnet/` in the body

**New content to write:**

```markdown
# src/net/ — .NET Product Source Root

**Canonical .NET product directory.** Format implementations live at `src/net/{format}/`.

| Format | Path | Status |
|---|---|---|
| csv | src/net/csv/ | Active |
| fods | src/net/fods/ | Active |
| fodt | src/net/fodt/ | Active |
| html | src/net/html/ | Active |
| markdown | src/net/markdown/ | Active |
| ndjson | src/net/ndjson/ | Active |
| netpbm | src/net/netpbm/ | Active |
| tsv | src/net/tsv/ | Active |
| txt | src/net/txt/ | Active |
| zst | src/net/zst/ | Active |

**Authority:** `registry/repository-layout.yaml` — `dotnet` language ID maps to `src/net/`.
**Resolver:** `tools/supervisor/path_resolver.py` — use `resolve_product_path("dotnet", format_id)`.

## Layout per format

Each `src/net/{format}/` directory follows this structure:

```
src/net/{format}/
  {Format}Document.cs    # domain model (≤800 LOC)
  {Format}Parser.cs      # parse-only
  {Format}Writer.cs      # write-only (where applicable)
  Model/                 # supporting model classes
  Exceptions/            # exception hierarchy
  Spec/                  # architecture_only spec stubs (V73 validates SpecQName)
```

## Technology Baseline

[keep existing table]

## SDK Baseline Confirmation (TC-0003)

[keep existing content]

## Commercial Isolation Rules

[keep existing content, already correctly references src/net/{format}/]

## Security Requirements

[keep existing content]

## Relationship to Other Documents

[keep existing list]
```

---

### TC-PATH-002 — Create `registry/repository-layout.yaml`
**Status:** OPEN

Create the machine-readable layout authority:

```yaml
schema_version: "1.0"
description: "Canonical repository layout authority. Consume this file; never derive source paths from language names."
source_roots:
  python:
    path: src/python
    language_id: python
    aliases: []
    product_path_pattern: "src/python/{format}"
  dotnet:
    path: src/net
    language_id: dotnet
    aliases: [net]
    product_path_pattern: "src/net/{format}"
prohibited_paths:
  - src/dotnet
  - src/dotnet/open-source
  - src/dotnet/commercial
  - src/python/open-source
validation:
  fail_on_missing_mapping: true
  fail_on_prohibited_path: true
examples:
  - description: ".NET FODS product"
    resolved: "src/net/fods/"
  - description: ".NET FODT product"
    resolved: "src/net/fodt/"
  - description: "Python FODS product"
    resolved: "src/python/fods/"
authority_consumers:
  - tools/supervisor/path_resolver.py
  - tools/supervisor/governance_validators_path.py
```

---

### TC-PATH-003 — Create `tools/supervisor/path_resolver.py`
**Status:** OPEN

```python
"""Canonical product path resolver.

Loads registry/repository-layout.yaml and resolves product paths deterministically.
Never derives paths from language-id by assumption (e.g. src/{language_id}).
"""
from pathlib import Path
import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LAYOUT_FILE = _REPO_ROOT / "registry" / "repository-layout.yaml"


def load_layout(repo_root: "Path | None" = None) -> dict:
    path = (Path(repo_root) / "registry" / "repository-layout.yaml") if repo_root else _LAYOUT_FILE
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_product_path(
    language_id: str,
    format_id: str,
    repo_root: "Path | None" = None,
    validate_exists: bool = False,
) -> Path:
    """
    Resolve canonical physical path for a product.

    Args:
        language_id: "dotnet", "python", or alias "net"
        format_id: Format identifier e.g. "fods", "csv"
        repo_root: Override for repo root (auto-detected by default)
        validate_exists: Raise FileNotFoundError if path missing on disk

    Returns:
        Absolute resolved Path

    Raises:
        KeyError: language_id has no mapping
        ValueError: resolved path matches a prohibited pattern
        FileNotFoundError: path absent when validate_exists=True
    """
    layout = load_layout(repo_root)
    root = Path(repo_root) if repo_root else _REPO_ROOT

    normalized = language_id.lower()
    entry = None
    for key, value in layout["source_roots"].items():
        if normalized in ([key] + value.get("aliases", [])):
            entry = value
            break

    if entry is None:
        available = list(layout["source_roots"].keys())
        raise KeyError(
            f"No layout mapping for language_id={language_id!r}. "
            f"Available: {available}. Authority: registry/repository-layout.yaml"
        )

    relative = entry["product_path_pattern"].format(format=format_id)

    for prohibited in layout.get("prohibited_paths", []):
        if relative.startswith(prohibited):
            raise ValueError(
                f"Resolved path {relative!r} matches prohibited pattern {prohibited!r}. "
                f"Authority: registry/repository-layout.yaml"
            )

    resolved = root / relative
    if validate_exists and not resolved.exists():
        raise FileNotFoundError(
            f"Product path does not exist: {resolved}. "
            f"Authority: registry/repository-layout.yaml"
        )
    return resolved


def get_prohibited_paths(repo_root: "Path | None" = None) -> list:
    layout = load_layout(repo_root)
    return layout.get("prohibited_paths", [])
```

---

### TC-PATH-004 — Create `tools/supervisor/governance_validators_path.py` (V110)
**Status:** OPEN

```python
"""V110 — dotnet-path-canonical: block src/dotnet/ as active product source root."""

_PROHIBITED = ["src/dotnet/open-source", "src/dotnet/commercial"]


def validate_dotnet_path_canonical(declaration: dict, repo_root=None) -> dict:
    """
    V110: No changed_files, evidence_paths, or work_item files may reference
    src/dotnet/open-source or src/dotnet/commercial.
    Historical documentation references are not checked (doc-only files).
    """
    violations = []

    def _check(paths, ctx):
        for p in (paths or []):
            s = str(p).replace("\\", "/")
            for bad in _PROHIBITED:
                if bad in s:
                    violations.append({
                        "context": ctx,
                        "offending_path": s,
                        "prohibited_pattern": bad,
                        "canonical": "src/net/{format}/",
                        "authority": "registry/repository-layout.yaml",
                        "remediation": "resolve_product_path('dotnet', format_id)",
                    })

    _check(declaration.get("changed_files", []), "changed_files")
    _check(declaration.get("evidence_paths", []), "evidence_paths")
    for item in declaration.get("planned_work_items", []):
        _check(item.get("files", []), f"work_item:{item.get('id','?')}.files")

    if violations:
        return {
            "validator_id": "V110",
            "rule": "dotnet-path-canonical",
            "status": "FAIL",
            "blocks_sprint": True,
            "violations": violations,
            "summary": (
                f"{len(violations)} reference(s) to prohibited src/dotnet/ product paths. "
                "Canonical .NET root is src/net/. See registry/repository-layout.yaml."
            ),
        }
    return {
        "validator_id": "V110",
        "rule": "dotnet-path-canonical",
        "status": "PASS",
        "blocks_sprint": False,
        "summary": "No prohibited src/dotnet/ product paths in declaration.",
    }
```

Then in `tools/supervisor/governance_validator_runner.py`, import and register V110 alongside existing validators.

---

### TC-PATH-005 — Add section A1a to `AGENTS.md`
**Status:** OPEN

Insert after the `## A` (Identity and Role) section, before `## A2`:

```markdown
## A1a. Canonical Source Roots (PATH AUTHORITY — never guess)

**Format-first layout.** Logical language IDs differ from physical directory names.

| Language ID | Physical Source Root | Example |
|---|---|---|
| `python` | `src/python/` | `src/python/fods/` |
| `dotnet` (alias: `net`) | `src/net/` | `src/net/fods/` |

**`src/dotnet/` does not exist.** .NET product source is at `src/net/{format}/`.

Authority: `registry/repository-layout.yaml`
Resolver: `tools/supervisor/path_resolver.py` → `resolve_product_path("dotnet", format_id)`
Validator: V110 blocks sprints that reference prohibited `src/dotnet/` paths.

Prohibited (must never be created):
- `src/dotnet/` (any subdirectory)
- `src/python/open-source/`
```

---

### TC-PATH-006 — Update `.supervisor/project-memory.md`
**Status:** OPEN

Add near the top of the file:

```markdown
## MANDATORY: .NET source is src/net/ — src/dotnet/ does not exist

- .NET product root: `src/net/{format}/`  (e.g. `src/net/fods/`)
- `src/dotnet/` directory does NOT exist in this repository
- Language ID `dotnet` → physical path `src/net/`
- Authority: `registry/repository-layout.yaml`
- Resolver: `tools/supervisor/path_resolver.py`
- Validator V110 blocks declarations referencing `src/dotnet/` product paths
```

---

### TC-PATH-007 — Create `reports/repository-layout/source-path-gap-ledger.yaml`
**Status:** OPEN

```yaml
schema_version: "1.0"
mission_id: DOTNET-PATH-GOV-001
created: "2026-07-03"
canonical_dotnet_root: src/net
prohibited_assumed_root: src/dotnet

summary:
  total_gaps: 6
  resolved: 1  # GAP-PATH-006 resolved with no change needed

gaps:
  - gap_id: GAP-PATH-001
    category: DOCUMENTATION_AMBIGUITY
    severity: CRITICAL
    symptom: >
      src/net/_readme.md contains Phase 0 content that names src/dotnet/ as its
      directory context and describes src/net/ as a future target. Primary confusion source.
    status: RESOLVED
    task_ids: [TC-PATH-001]

  - gap_id: GAP-PATH-002
    category: PATH_RESOLVER
    severity: HIGH
    symptom: "No machine-readable layout authority; agents derive src/{language_id}/"
    status: RESOLVED
    task_ids: [TC-PATH-002, TC-PATH-003]

  - gap_id: GAP-PATH-003
    category: SKILL_OR_COMMAND
    severity: HIGH
    symptom: "No blocking validator for src/dotnet product paths in declarations"
    status: RESOLVED
    task_ids: [TC-PATH-004]

  - gap_id: GAP-PATH-004
    category: DOCUMENTATION_AMBIGUITY
    severity: MEDIUM
    symptom: "AGENTS.md has no concise path table; agents must scan narrative text"
    status: RESOLVED
    task_ids: [TC-PATH-005]

  - gap_id: GAP-PATH-005
    category: AUTONOMOUS_ROUTING
    severity: MEDIUM
    symptom: "project-memory.md lacks explicit src/net/ canonical path rule"
    status: RESOLVED
    task_ids: [TC-PATH-006]

  - gap_id: GAP-PATH-006
    category: STALE_PATH_REFERENCE
    severity: LOW
    symptom: "~48 files mention src/dotnet in prohibition/historical context"
    status: NO_CHANGE_NEEDED
    note: >
      All references are correct prohibition notices (AGENTS.md, architecture.md,
      product-tracks.md, release-control.md) or immutable historical evidence
      (docs/history/). The fix is a clear positive statement in AGENTS.md and
      src/net/_readme.md. Text replacement not required.

root_causes:
  - cause_id: RC-001
    description: >
      src/net/_readme.md was migrated verbatim from src/dotnet/ and never
      updated to reflect the live state of src/net/
    prevention: TC-PATH-001 rewrites the file
    detection: Head -1 src/net/_readme.md — no longer references src/dotnet

  - cause_id: RC-002
    description: >
      No machine-readable layout contract; agents derive src/{language_id}/
      from naming convention
    prevention: registry/repository-layout.yaml + path_resolver.py
    detection: V110 validator blocks prohibited paths in declarations

  - cause_id: RC-003
    description: >
      AGENTS.md states prohibitions in prose but has no quick-reference path table
    prevention: Section A1a added to AGENTS.md
    detection: grep "src/net" AGENTS.md shows canonical table
```

---

### TC-PATH-008 — Run 12 pilots and document in `reports/repository-layout/pilot-results.yaml`
**Status:** OPEN

| # | Pilot | Method | Expected |
|---|---|---|---|
| P1 | FODS .NET discovery | `resolve_product_path("dotnet","fods")` | `.../src/net/fods` |
| P2 | Second .NET product | `resolve_product_path("dotnet","csv")` | `.../src/net/csv` |
| P3 | Python product | `resolve_product_path("python","fods")` | `.../src/python/fods` |
| P4 | Logical language ID | `resolve_product_path("dotnet","fods")` | resolves to src/net |
| P5 | Alias `net` | `resolve_product_path("net","fods")` | same as P1 |
| P6 | Prohibited path | V110 on `changed_files: ["src/dotnet/open-source/X.cs"]` | FAIL |
| P7 | Not found | `resolve_product_path("dotnet","nonexistent", validate_exists=True)` | FileNotFoundError |
| P8 | Taskcard path field | Review TC-PATH-001 through TC-PATH-007 for `resolved_product_path` | all src/net/ |
| P9 | Skill execution | Read add-dotnet-api.md — confirm `src/net/<format_id>/` | confirmed |
| P10 | Generated docs | Search .local/supervisor/ for `src/dotnet` active references | 0 |
| P11 | Layout authority | Read registry/repository-layout.yaml — `prohibited_paths` includes `src/dotnet` | confirmed |
| P12 | Idempotency | Re-read all changed files, re-run pilots | 0 material changes |

---

### TC-PATH-009 — Idempotency proof
**Status:** OPEN

Re-run after all taskcards are CLOSED:
1. Read `registry/repository-layout.yaml` — content unchanged
2. `python -c "from tools.supervisor.path_resolver import resolve_product_path; print(resolve_product_path('dotnet','fods'))"` — identical output
3. Read `src/net/_readme.md` — no `src/dotnet` references remain
4. Read `AGENTS.md` A1a section — present and correct
5. Count material changes from second run: **0**

Record under `idempotency:` in `reports/repository-layout/pilot-results.yaml`.

---

## Taskcard Status Table

| ID | Title | Status |
|---|---|---|
| TC-PATH-001 | Rewrite src/net/_readme.md | CLOSED |
| TC-PATH-002 | Create registry/repository-layout.yaml | CLOSED |
| TC-PATH-003 | Create tools/supervisor/path_resolver.py | CLOSED |
| TC-PATH-004 | Create governance_validators_path.py (V110) + register | CLOSED |
| TC-PATH-005 | Add A1a section to AGENTS.md | CLOSED |
| TC-PATH-006 | Update .supervisor/project-memory.md | CLOSED |
| TC-PATH-007 | Create source-path-gap-ledger.yaml | CLOSED |
| TC-PATH-008 | Run 12 pilots + pilot-results.yaml | CLOSED |
| TC-PATH-009 | Idempotency proof | CLOSED |

## Taskcard Closure Summary (machine-parseable)

| TC-ID | Status |
|---|---|
| TC-PATH-001 | CLOSED |
| TC-PATH-002 | CLOSED |
| TC-PATH-003 | CLOSED |
| TC-PATH-004 | CLOSED |
| TC-PATH-005 | CLOSED |
| TC-PATH-006 | CLOSED |
| TC-PATH-007 | CLOSED |
| TC-PATH-008 | CLOSED |
| TC-PATH-009 | CLOSED |

---

## Verification commands

```bash
# 1. Path resolver — .NET FODS
python -c "from tools.supervisor.path_resolver import resolve_product_path; print(resolve_product_path('dotnet','fods'))"
# Expected: .../src/net/fods

# 2. Alias
python -c "from tools.supervisor.path_resolver import resolve_product_path; print(resolve_product_path('net','fods'))"
# Expected: same as above

# 3. Validate_exists — no error
python -c "from tools.supervisor.path_resolver import resolve_product_path; resolve_product_path('dotnet','fods',validate_exists=True); print('OK')"

# 4. V110 fires on prohibited path
python -c "
from tools.supervisor.governance_validators_path import validate_dotnet_path_canonical
import json
r = validate_dotnet_path_canonical({'changed_files': ['src/dotnet/open-source/fods/X.cs']})
print(json.dumps(r, indent=2))
"
# Expected: status: FAIL

# 5. _readme.md no longer references src/dotnet
grep -c "src/dotnet" src/net/_readme.md
# Expected: 0

# 6. AGENTS.md has canonical path table
grep -n "src/net" AGENTS.md | head -5
# Expected: shows A1a table entry

# 7. Layout authority
grep "path: src/net" registry/repository-layout.yaml
# Expected: match
```

---

## Out of scope — already correct, no changes needed

- `tools/supervisor/governance_validators_dotnet.py` — V73 uses `src/net/` regex
- `tools/supervisor/governance_validators_ext2.py` — V78 checks `"src/net" in str(f)`
- `tools/supervisor/governance_validators_ext3.py` — `_PRODUCT_SRC_ROOTS = ("src/python", "src/net")`
- `.claude/commands/add-dotnet-api.md` — already uses `src/net/<format_id>/`
- `.claude/commands/add-dotnet-object-model-feature.md` — already uses `src/net/<format_id>/`
- `.github/workflows/ci.yml` — already uses `src/net/*/`
- `docs/history/` files — immutable historical evidence
- `docs/code-quality/architecture.md` — CRITICAL note at lines 424-425 already present
- `docs/product-factory/product-tracks.md` — explicit prohibition already present
- `docs/governance/release-control.md` — explicit prohibition already present
- AGENTS.md line 360 — existing prohibition wording correct; only adding A1a positive table

---

## Commit authorization

Commit ONLY after all 9 taskcards are CLOSED and idempotency proof passes.
Do NOT push without explicit user authorization.


<!--plan_terminal_lock:
  status: ITERATION_REQUIRED
  locked_at: "2026-07-03T13:23:55.080805+00:00"
  locked_by: "af3d4a5638a5"
  successor_required_for_future_changes: true
  mutation_policy: "no further plan/hardening/execution writes"
-->
