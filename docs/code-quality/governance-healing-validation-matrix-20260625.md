# Governance Healing Validation Matrix — 2026-06-25
Sprint: GOVERNANCE-HEALING-20260625 (warm-jingling-sutherland)
Type: machinery_hardening

| Category | Item | Before | After | Evidence Path |
|----------|------|--------|-------|---------------|
| Documentation | production-library-checklist.md | Missing cross-language, import direction, error handling sections | Extended with §16 (cross-language), §17 (import direction RULE-LIB-003), §18 (error handling RULE-LIB-006) | docs/code-quality/production-library-checklist.md |
| Documentation | src-architecture-gap-inventory.md | STALE (2026-06-17) | UPDATED: 2026-06-25 section at top with HEAD LOC counts for 5 Python monolith files | docs/code-quality/src-architecture-gap-inventory.md |
| Documentation | root-cause-analysis.md | STALE (2026-06-17) | UPDATED: 2026-06-25 section at top with RCA-6 through RCA-9 | docs/code-quality/root-cause-analysis.md |
| Validators | V75 validate_dependency_direction | MISSING | ADDED to governance_validators_ext2.py (AST-based import scan; WARN existing, FAIL new) | tools/supervisor/governance_validators_ext2.py |
| Validators | V76 validate_error_handling_hierarchy | MISSING | ADDED to governance_validators_ext2.py (exceptions.py check; WARN existing, FAIL new) | tools/supervisor/governance_validators_ext2.py |
| Validator runner | governance_validator_runner.py | V1-V74 registered | V75/V76 imported from ext2, registered, docstring updated to V1-V76; canonical count = 77 | tools/supervisor/governance_validator_runner.py |
| Tests | test_v75_v76_validators.py | MISSING | CREATED: 11 tests, all PASS | tests/supervisor/test_v75_v76_validators.py |
| Tests | test_governance_validators.py validator count | Expected 75 | Updated to 77; all 92 tests PASS | tests/supervisor/test_governance_validators.py |
| Production rules | RULE-LIB-003 (import direction) | MISSING | ADDED to production-readiness-standard.md §3.6 | docs/code-quality/production-readiness-standard.md |
| Production rules | RULE-LIB-006 (error handling hierarchy) | MISSING | ADDED to production-readiness-standard.md §3.7 | docs/code-quality/production-readiness-standard.md |
| Production rules | V59 upgrade for RELEASE_GATE | WARN-only | Upgrade sentence added: FAIL for RELEASE_GATE items where .NET/Python API diff >20% | docs/code-quality/production-readiness-standard.md |
| Pre-commit | .pre-commit-config.yaml | Already existed | VERIFIED: 2 hooks with correct flags (--check-baseline-growth, --check-new-files) | .pre-commit-config.yaml |
| Baseline metadata | healing_plan fields | MISSING from all entries | 13 src/ violations annotated with healing_plan, healing_priority, healing_target_file | registry/source-structure-baseline.json |
| Machinery proof | Growth prevention (Step 2 of TC-GH-007) | NOT TESTED | PASS — new 850-LOC file detected as NEW violation, then deleted | .local/evidences/governance-healing-20260625/growth-prevention-proof.txt |
| Machinery proof | V75 manual test | NOT TESTED | PASS — ran against fods/neutral_model.py; WARN for grandfathered file | .local/evidences/governance-healing-20260625/v75-proof.txt |
| Machinery proof | V76 manual test | NOT TESTED | PASS — ran against csv/tabular_document.py; reported correctly | .local/evidences/governance-healing-20260625/v76-proof.txt |
| Machinery proof | Validator test suite | -- | PASS — 11 V75/V76 tests pass, 92 governance validator tests pass | .local/evidences/governance-healing-20260625/validator-tests.txt |
| Product healing | csv/tabular_document.py LOC | 960 LOC (over 800) | 799 LOC (HEALED below 800) | src/python/csv/tabular_document.py |
| Product healing | csv_analytics.py (new) | MISSING | CREATED: 180 LOC, 14 functions extracted, clean file (<800 LOC, not in known_violations) | src/python/csv/csv_analytics.py |
| Tests preserved | CSV format tests | 160 PASS | 160 PASS (no regressions) | .local/evidences/governance-healing-20260625/csv-healing-tests.txt |
| Tests added | V75/V76 tests | 0 | 11 tests added | tests/supervisor/test_v75_v76_validators.py |
| Baseline | tabular_document.py loc updated | loc=960 | loc=799 (cap=968 unchanged — write-once policy) | registry/source-structure-baseline.json |
| Master plan | Architecture healing taskcards | MISSING | Section 72 added with 8 taskcards (TC-ARCH-ZST/XCF/FODS/ABW/DIF/FODT/NETPBM) | plans/master-plan.md |
| Master plan | Operating rule for healing | MISSING | Rule 17 added to Section 1 (all src/ >800 LOC require healing_plan entry) | plans/master-plan.md |
| .NET healing plan | NetpbmImage.cs | No healing plan | healing_plan=responsibility_split, healing_priority=P1, healing_target_file=NetpbmImageReader.cs | registry/source-structure-baseline.json |
