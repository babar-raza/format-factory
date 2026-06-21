# Next Agent Execution Prompt — ff-arch-20260621-001
# Run this in the next session as the sprint prompt

## Context

Format Factory archaeology investigation (run ff-arch-20260621-001) produced VERDICT:
**NOT_READY_REPAIR_MACHINERY_FIRST**

Three machinery repairs must complete before unrestricted product deepening.

---

## Next Sprint: Machinery Repair Phase 1

**Sprint ID**: `ff-machinery-repair-phase1-20260621-001`

**Mission**: Fix the three BLOCKER-level gaps that prevent safe product deepening.

---

## Task 1: Fix FODS Python triple nesting (TC-HYGIENE-FODS-001)

```bash
# Step 1: Find which level the installed package resolves to
python -c "import format_factory_fods; print(format_factory_fods.__file__)"

# Step 2: Identify the correct canonical level (likely innermost: fods/fods/fods/)
# Step 3: Remove the intermediate fods/fods/ level
# Step 4: Verify import still works
# Step 5: Run all FODS tests
.venv/Scripts/pytest tests/python/fods/ -x --tb=short
```

Expected result: Single package root; all FODS tests pass.

---

## Task 2: Add V43 QName class name validator (TC-GOV-QNAME-VALIDATOR-001)

Add to `tools/supervisor/governance_validators.py`:

```python
def validate_qname_class_names(declaration: dict, baseline: dict) -> dict:
    """V43: New source classes must use canonical QName names or be in Compat/."""
    violations = []
    for item in declaration.get("work_items", []):
        if item.get("item_type") not in ("PRODUCT_SOURCE", "PRODUCT_TEST"):
            continue
        for path in item.get("evidence_paths", []):
            if not (path.endswith(".cs") or path.endswith(".py")):
                continue
            if "Compat/" in path or "compat/" in path:
                continue  # Compat facades are allowed to be format-prefixed
            # Check for format-prefixed class names in new files
            content = Path(path).read_text(errors="replace") if Path(path).exists() else ""
            import re
            classes = re.findall(r'\bclass\s+(Fods\w+|Fodt\w+|Fodg\w+|Fodp\w+)', content)
            if classes:
                violations.append({
                    "path": path,
                    "classes": classes,
                    "reason": f"Format-prefixed class names found: {classes}. Use canonical names (Table.TableCell, Text.Paragraph) or place in Compat/ directory."
                })
    return {
        "validator": "validate_qname_class_names",
        "status": "FAIL" if violations else "PASS",
        "violations": violations,
        "blocks_sprint": len(violations) > 0
    }
```

Wire into `run_all_governance_validators()`.
Add test: `tests/supervisor/test_governance_validators.py::TestV43QNameClassNames`

---

## Task 3: Update /add-python-api and /add-dotnet-api skills (TC-SKILL-QNAME-ENFORCE-001)

Add to both skill command files a mandatory pre-step:

```markdown
## MANDATORY PRE-CHECK: QName Compliance

Before naming any new class, MUST:
1. Check `registry/odf-ontology/qname-to-code-map.yaml` for canonical class name
2. If adding a class for a spec element: use canonical name (e.g., Table.TableCell, not FodsCell)
3. Format-prefixed names (FodsXxx, FodtXxx) ONLY in Compat/{Format}/ directories
4. Add spec_qname attribute to all new model classes:
   - C#: `public const string QName = "table:table-cell";`
   - Python: `spec_qname = "table:table-cell"`
5. After adding class: verify V43 governance validator passes
```

---

## Declaration Template for This Sprint

```yaml
run_id: ff-machinery-repair-phase1-20260621-001
work_items:
  - item_id: "TC-HYGIENE-FODS-001"
    item_type: MACHINERY_REPAIR
    status: completed
    evidence_paths: ["tests/python/fods/test_parser_basic.py"]
    gap_ledger_ref: "GAP-ARCH-001"

  - item_id: "TC-GOV-QNAME-VALIDATOR-001"
    item_type: GOVERNANCE_TASKCARD
    status: completed
    evidence_paths: ["tests/supervisor/test_governance_validators.py"]
    gap_ledger_ref: "GAP-ARCH-009"

  - item_id: "TC-SKILL-QNAME-ENFORCE-001"
    item_type: GOVERNANCE_TASKCARD
    status: completed
    evidence_paths: [".claude/commands/add-python-api.md", ".claude/commands/add-dotnet-api.md"]
    gap_ledger_ref: "GAP-ARCH-008"
```

---

## Success Criteria

- [ ] FODS Python: single package root; `parse_fods` imports correctly
- [ ] V43 validator: PASS when canonical names used; FAIL when FodsXxx in non-Compat path
- [ ] Skills updated: QName pre-check included in both add-python-api and add-dotnet-api
- [ ] All existing tests still pass (no regressions)
