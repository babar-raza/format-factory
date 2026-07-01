---
version: "1.3"
last-updated: "2026-06-03"
phase-available: "all"
gate-required: null
created-by: R12 sprint session
---

# /export-plan-context

Bundle the long-term plan context files into a zip suitable for sharing with an LLM.

## Usage

```
/export-plan-context
```

## Purpose

Produce a single zip at `.local/format-factory-longterm-plan-context.zip` containing
all files an LLM needs to understand the project's long-term plan, architecture,
governance, and current acquisition state.

## Steps

0. **DEPENDENCY + CURRENCY CHECK** — Verify standard files exist and detect staleness:
   ```python
   import pathlib, glob as _g
   required = ["plans/master-plan.md", "memory/00-index.md", "AGENTS.md", "GOVERNANCE.md"]
   missing_req = [f for f in required if not pathlib.Path(f).exists()]
   if missing_req:
       print("BLOCKED: missing required files:", missing_req)
   all_mem = sorted(_g.glob("memory/[0-9]*.md"))
   print("Latest memory in repo:", all_mem[-1] if all_mem else "NONE")
   ```
   If BLOCKED: stop. If latest memory is not in the standard file list below, add it before building.

1. Verify all standard files listed below exist. Print any that are missing.
2. Build the zip using Python's `zipfile` module (no shell zip dependency):

```python
import zipfile, os, glob as _g

files = [
    # Single operational authority
    "plans/master-plan.md",
    # Core docs
    "docs/code-quality/architecture.md",
    "docs/gates.md",
    "docs/product-factory/product-tracks.md",
    "docs/python-foss/format-expansion-roadmap.md",
    "docs/product-factory/commercial-product-capability-model.md",
    "docs/ai/ai-usage-operating-model.md",
    "docs/python-foss/acquisition-workflow.md",
    "docs/automation/assistant-supervision-methodology.md",
    # Root governance
    "README.md",
    "GOVERNANCE.md",
    "AGENTS.md",
    # Memory — project intent + decisions + latest acquisition state
    "memory/00-index.md",
    "memory/01-project-origin-and-intent.md",
    "memory/03-architecture-and-product-tracks.md",
    "memory/05-decision-register-expanded.md",
    "memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md",
    "memory/34-zst-r17-gate4-and-multi-format-gate1-intake-20260516.md",
    "memory/35-r18-quarter-mile-zst-gate4-multi-format-gate1-20260516.md",
    "memory/38-r21-foss-release-readiness-and-gate11-preexecution-20260517.md",
    # Current acquisition planning state
    "reports/planning/r17-taskcard-roadmap-memory-normalization-report-20260516.md",
    "reports/planning/r17-multi-format-gate1-intake-and-scoring-20260516.md",
    "reports/planning/r18-quarter-mile-roadmap-and-wip-control-20260516.md",
    "reports/planning/r18-fodp-fodg-gate2-fastpath-decision-20260516.md",
    "reports/planning/r21-registry-pack-taskcard-roadmap-memory-normalization-report-20260517.md",
    "reports/planning/cross-category-ranking-validation-20260514.md",
]

out = ".local/format-factory-longterm-plan-context.zip"
os.makedirs(".local", exist_ok=True)
missing = [f for f in files if not os.path.exists(f)]
if missing:
    print("MISSING:", missing)
present = [f for f in files if os.path.exists(f)]
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for f in present:
        zf.write(f)
uncompressed = sum(os.path.getsize(f) for f in present)
print(f"Files included: {len(present)}/{len(files)}")
print(f"Uncompressed: {uncompressed:,} bytes")
print(f"Zip size: {os.path.getsize(out):,} bytes")
print(f"Output: {os.path.abspath(out)}")

# Staleness guard
all_mem = sorted(_g.glob("memory/[0-9]*.md"))
latest_repo_mem = all_mem[-1] if all_mem else "none"
zipped_mem = [f for f in present if f.startswith("memory/")]
latest_zip_mem = max(zipped_mem) if zipped_mem else "none"
if latest_repo_mem != latest_zip_mem:
    print(f"\nSTALENESS_WARNING: Latest memory in repo: {latest_repo_mem}")
    print(f"  Latest memory in zip: {latest_zip_mem}")
    print("  Update the files list to include current sprint memory + readiness reports.")
    print("  See Notes section of this command for update instructions.")
else:
    print(f"CONTEXT_CURRENCY: OK ({latest_zip_mem})")
```

3. Run the script via Bash from the repo root.
4. Print the absolute Windows path to the zip.
5. Print a table of files included, grouped by category.
6. Print the suggested LLM prompt prefix (see Output Format below).

## Customization

If the user specifies additional files (e.g., "also include the R18 readiness report"),
add them to the `files` list before building. If the user wants to exclude files,
remove them. Re-run and report the updated zip.

## Output Format

Print:

```
EXPORT_PATH: C:\Users\prora\OneDrive\Documents\GitHub\format-factory\.local\format-factory-longterm-plan-context.zip

Files: <N> | Uncompressed: <X> bytes | Zip: <Y> bytes

| Category              | Files |
|-----------------------|-------|
| Single authority      | plans/master-plan.md |
| Core docs (8)         | architecture, gates, product-tracks, ... |
| Root governance (3)   | README, GOVERNANCE, AGENTS |
| Memory (8)            | 00-index, 01-origin, 03-arch, 05-decisions, 26-roadmap, 34-r17, 35-r18, 38-r21 |
| Planning state (6)    | r17-normalization, r17-intake, r18-wip, r18-fodp-fodg, r21-normalization, cross-category |

CONTEXT_CURRENCY: OK (memory/38-r21-...) [or STALENESS_WARNING if stale]

Suggested LLM prompt prefix:
"This zip contains the long-term plan and current state of the format-factory project.
Start with plans/master-plan.md as the single authority, then memory/00-index.md for
orientation. Key acquisition state: memory/38-r21-foss-release-readiness-and-gate11-preexecution-20260517.md."
```

## Notes

- Output zip is gitignored (`.local/` is excluded from version control).
- Do not commit the zip or any `.local/` file.
- Rebuild the zip at the start of any new session where plan context is needed.
- **MANDATORY MAINTENANCE:** After every R-sprint, add the new memory file and latest
  readiness-decision or normalization report to the standard `files` list. Run the staleness
  guard (it fires automatically after zip creation) to verify. Failure to update will produce
  `STALENESS_WARNING` on next execution. Current list reflects R21 state (memory/38).

## Validation

Zip must contain all required files. CONTEXT_CURRENCY must be OK (not STALENESS_WARNING).

## Allowed Paths

- `.local/` (write zip output)
- `memory/` (read memory files)
- `plans/master-plan.md` (read only)
- `docs/` (read architecture, gates, product tracks)
- `reports/planning/` (read planning state)

## Forbidden Paths

- `src/**` (no source edits)
- `registry/format-registry.yaml` (gate authority)
- `tests/**` (no test changes)

## Constraints

- Output zip must go to `.local/` (gitignored)
- Do not commit the zip or any `.local/` file
- Do not push

## Rollback

1. Delete `.local/format-factory-longterm-plan-context.zip`
2. No source or test changes to revert

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, files_included, zip_path, context_currency_status, verdict.

## Changelog

- 1.0 (2026-05-15): Initial version. Created in R12 sprint session from ad-hoc zip build.
- 1.1 (2026-05-17): Add Step 0 dependency + currency check. Add staleness guard Python snippet
  (fires automatically, prints STALENESS_WARNING or CONTEXT_CURRENCY: OK). Update standard file
  list from R11/R12 era to R18 state (memory/34, memory/35, r17/r18 planning reports). Remove
  stale memory/27, memory/28, r11-ranking, r11-plan, r13-readiness, weekly-report-r12 entries.
  Add MANDATORY MAINTENANCE note to Notes section. Sprint: FORMAT-FACTORY-SKILLS-PRD-HARDENING-001.
- 1.2 (2026-05-17): Update standard file list to R21 state. Add memory/38 and
  r21-registry-pack-taskcard-roadmap-memory-normalization-report-20260517.md. Update Output Format
  and Notes to reflect memory/38 as current. Sprint: SKILLS-PRD-HARDENING-001-CLOSURE-REPAIR-001.
- 1.3 (2026-06-03): Added allowed/forbidden paths, constraints, rollback, transcript (Skills R102).
