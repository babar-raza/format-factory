# Backfill Facility Design

**Sprint/Run ID:** ff-archaeology-20260625

---

## Current Backfill Mechanism Assessment

### What Exists (As of 2026-06-25)

| Component | Status | Purpose |
|-----------|--------|---------|
| `generate_canonical_stubs.py` | ACTIVE | Generates architecture_only spec/ skeleton files |
| `validate_spec_registry.py` | ACTIVE | Validates shared/qname-registry/*.yaml against schema |
| `qname-backfill` skill | REGISTERED | Skill for executing per-format backfill tasks |
| V53 validator | ACTIVE | Enforces spec_qname ClassVar after submission |
| TC-QHARD-POST-* task pattern | USED | Per-format taskcard for qname injection |
| QName registry (21 YAML files) | COMPLETE | Source of truth for all qname-to-file mappings |

### What Does NOT Exist

| Missing Component | Impact |
|------------------|--------|
| `scan_qname_gaps.py` | No automated inventory of missing spec_qname ClassVars |
| `inject_spec_qname.py` | No auto-injection of ClassVar from registry |
| `generate_compat_facade.py` | No auto-generation of Compat/ entries from registry |
| `generate_domain_model.py` | No auto-generation of models.py from spec/ + registry |
| `backfill_evidence_snapshot.py` | No before/after SHA snapshot for migration proof |
| Migration rollback tool | No automated rollback (git revert only) |
| Pre-commit hook | No spec_qname enforcement before commit |

### Current Backfill Process (Manual)

1. Identify format needing backfill (from V53 failures or audit findings)
2. Create taskcard (TC-QHARD-POST-{format}-001)
3. Read `shared/qname-registry/{format}.yaml` to find spec_qname values
4. Open `src/python/{format}/{format}_codec.py` or `{format}_parser.py`
5. Add `from typing import ClassVar` if not present
6. Add `spec_qname: ClassVar[str] = "ns:element"` to each authority class
7. Run `.venv/Scripts/pytest tests/python/{format}/` to verify
8. Close taskcard with evidence

**This process takes 20-40 minutes per format. With 7 Gen3 formats needing domain model
upgrades and 2 formats needing qname fixes, total manual effort is ~5-7 hours.**

---

## Proposed Backfill Facility Design

### Tool 1: scan_qname_gaps.py

**Purpose:** Inventory all codec/parser/model classes missing spec_qname ClassVar.

**Algorithm:**
```python
# tools/backfill/scan_qname_gaps.py
import ast
from pathlib import Path
import yaml

def scan_format(format_name: str) -> list[dict]:
    """Scan a format's codec/parser for classes missing spec_qname."""
    registry = yaml.safe_load(
        Path(f"shared/qname-registry/{format_name}.yaml").read_text()
    )
    codec_files = list(Path(f"src/python/{format_name}").glob("*_codec.py")) + \
                  list(Path(f"src/python/{format_name}").glob("*_parser.py"))

    gaps = []
    for file in codec_files:
        tree = ast.parse(file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                has_spec_qname = any(
                    isinstance(stmt, ast.AnnAssign) and
                    isinstance(stmt.target, ast.Name) and
                    stmt.target.id == "spec_qname"
                    for stmt in node.body
                )
                if not has_spec_qname:
                    # Check if this class name appears in registry
                    for entry in registry.get("entries", []):
                        if entry.get("canonical_class", "").split(".")[-1] == node.name:
                            gaps.append({
                                "file": str(file),
                                "class": node.name,
                                "qname": entry["qname"],
                                "spec_fact_ref": entry.get("spec_fact_ref")
                            })
    return gaps
```

**Output:** JSON report of all classes needing spec_qname injection.

---

### Tool 2: inject_spec_qname.py

**Purpose:** Auto-inject `spec_qname: ClassVar[str] = "..."` into codec classes.

**Algorithm:**
1. Load `shared/qname-registry/{format}.yaml`
2. For each codec/parser class in the format
3. If class name matches a registry `canonical_class`
4. Add `spec_qname: ClassVar[str] = "{qname}"` as first class body statement
5. Add `spec_fact_ref: ClassVar[str] = "{spec_fact_ref}"` if present
6. Ensure `from typing import ClassVar` is in imports
7. Write patched file

**Safety constraints:**
- ONLY modify files in `src/python/{format}/` (not spec/ or Compat/)
- ONLY add ClassVar lines — never modify existing logic
- Require `--dry-run` flag for preview
- Generate before/after SHA-256 for each file

---

### Tool 3: generate_compat_facade.py

**Purpose:** Auto-generate Compat/ facade entry from registry.

**Algorithm:**
1. Load `shared/qname-registry/{format}.yaml`
2. For each entry with `facade_names`
3. Check if `src/python/{format}/Compat/{format}_{local_name}.py` exists
4. If not: generate stub file inheriting from spec class
5. Set spec_qname, spec_fact_ref in class body
6. Write file with `# GENERATED — backfill` marker

---

### Tool 4: generate_domain_model.py

**Purpose:** Auto-generate `models.py` with domain model class for Gen3 formats.

**Algorithm:**
1. Read format registry + spec/ hierarchy
2. Identify primary spec class (first entry in registry with `source_layer: Spec`)
3. Generate `{Format}Document` class with:
   - `spec_qname: ClassVar[str] = "{primary_qname}"`
   - `spec_fact_ref: ClassVar[str] = "{primary_spec_fact_ref}"`
   - `_model: dict` backing field
   - `@classmethod from_file(cls, path) -> cls`
   - Basic properties from codec's neutral model dict
   - `to_dict() -> dict` method
4. Write to `src/python/{format}/models.py`

---

### Tool 5: backfill_evidence_snapshot.py

**Purpose:** Generate before/after SHA-256 snapshots for migration evidence.

**Algorithm:**
1. Compute SHA-256 for all affected files before backfill
2. Execute backfill (inject_spec_qname or generate_domain_model)
3. Compute SHA-256 for all affected files after backfill
4. Write evidence YAML with before/after hashes
5. Run pytest for affected format and record pass/fail

---

## Backfill Governance Requirements

Any backfill operation MUST:
1. Reference a gap-ledger entry (GAP-* ID)
2. Reference a registry entry (qname-registry/{format}.yaml)
3. Reference a SAL fact (FACT-FORMAT-NNN)
4. Produce evidence snapshot (before/after SHA-256)
5. Pass V53 validation post-backfill
6. Include test results showing no regression
7. Create a ledger entry in `reports/r90/product-code-change-ledger.json`

Backfill operations MUST NOT:
- Modify behavioral logic
- Change function signatures
- Add new functions (use appropriate skill for that)
- Modify test files (only src/)
- Break existing tests

---

## Backfill Roadmap

### Immediate (Within This Sprint)
- Fix DIF spec_qname gaps (QNAME-BACKFILL-001) — 2 ClassVar injections, ~10 lines
- Fix FODG spec_qname gap (QNAME-BACKFILL-002) — 1 ClassVar injection, ~5 lines

### Short-Term (1-2 Sprints)
- Create domain models for 7 Gen3 Python formats (SRC-STD-001 through SRC-STD-007)
- Design and implement `scan_qname_gaps.py` (BACKFILL-003)

### Medium-Term (3-5 Sprints)
- Implement `inject_spec_qname.py` with dry-run mode
- Implement `generate_domain_model.py` for batch processing
- Run full backfill scan and close all CHAIN_BROKEN_AT_SAL gaps

### Long-Term (5+ Sprints)
- Pre-commit hook for spec_qname enforcement
- CI integration of scan_qname_gaps.py
- Automated regeneration from registry changes
