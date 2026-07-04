# Validator Gap Mapping — TC-ROOT-001 + TC-VAL-001
Generated: 2026-07-04 | Authority: plans/.claude/drifting-wobbling-honey.md

## Root-Cause Matrix: Gap Class → Failed Control → Governing Validator

| Gap Class | Root Cause | Failed Control | Validator | Status |
|-----------|-----------|----------------|-----------|--------|
| VIOLATION_WRONG_OWNER (method on wrong type) | No ownership enforcement at code-write time | pre_execution_checklist missing | V113 (governance_validators_ext4.py) | ACTIVE |
| VIOLATION_NO_QNAME (public symbol without spec authority) | No QName requirement at code-write time | traceability_required missing | V111 (governance_validators_ext4.py) | ACTIVE |
| DETACHED_STATE (models wrap dicts not spec objects) | No model-class requirement | V_MODEL_CLASS_REQUIRED absent | V116 (governance_validators_ext4.py) | ADVISORY |
| MONOLITH_ROOT (>800 LOC root file) | No LOC gate at commit time | pre-commit hook not installed | V35 (governance_validators.py) | ACTIVE (local) |
| NO_PARSING_SUBDIR (flat parser at root) | No layout enforcement | V126 (ext4) not enforced at commit | V126 (governance_validators_ext4.py) | ACTIVE |
| NO_MODEL_SUBDIR (flat model at root) | No layout enforcement | V126 (ext4) not enforced at commit | V126 (governance_validators_ext4.py) | ACTIVE |
| FULL_REBUILD_STUB (no real implementation) | No parser-required gate | V_DOTNET_PARSER_REQUIRED absent | NEW: V128 (honey TC-VAL-002) | PLANNED |
| ANALYTICS_ON_MODEL (analytics in models.py) | No analytics separation gate | V77 not catching Python | V77 (governance_validators_ext.py) | ACTIVE |
| COMPAT_NOT_BEHAVIORAL (Compat/ is marker only) | No behavioral facade requirement | No dedicated validator | NEW: V129 (honey TC-VAL-002) | PLANNED |
| LOC_EXCEEDS_CAP (file > baseline_loc_cap) | No pre-commit block for cap | pre-commit not installed | V78 (governance_validators.py) | ACTIVE (local) |

## Validator Coverage by Gap Class

| Validator | ID | Gap Classes Covered | File | Blocking? |
|-----------|----|--------------------|------|-----------|
| monolith_detection_validator | V35 | MONOLITH_ROOT | governance_validators.py | YES |
| multi_responsibility_file | V66 | MONOLITH_ROOT | governance_validators_ext.py | YES |
| analytics_masquerade | V77 | ANALYTICS_ON_MODEL | governance_validators_ext.py | YES |
| dotnet_loc_cap_enforced | V78 | LOC_EXCEEDS_CAP (.NET) | governance_validators.py | YES |
| dependency_direction | V75 | IMPORT_DIRECTION | governance_validators_ext2.py | YES |
| error_hierarchy | V76 | ERROR_HIERARCHY | governance_validators_ext2.py | YES |
| product_code_quality | V100-V109 | Multiple (PQLM-001) | governance_validators_ext3.py | YES |
| prohibited_path | V110 | WRONG_PATH | governance_validators_path.py | YES |
| public_symbol_without_qname | V111 | VIOLATION_NO_QNAME | governance_validators_ext4.py | ADVISORY |
| model_type_without_spec | V112 | VIOLATION_NO_QNAME | governance_validators_ext4.py | ADVISORY |
| nested_concept_on_root | V113 | VIOLATION_WRONG_OWNER | governance_validators_ext4.py | ADVISORY |
| getter_without_parser_obligation | V114 | DETACHED_STATE | governance_validators_ext4.py | ADVISORY (skill-time) |
| setter_without_writer_obligation | V115 | DETACHED_STATE | governance_validators_ext4.py | ADVISORY (skill-time) |
| detached_persistent_dict | V116 | DETACHED_STATE | governance_validators_ext4.py | ADVISORY |
| dumping_ground_file | V117 | BAD_NAMING | governance_validators_ext4.py | ADVISORY |
| sprint_history_identifier | V118 | UNGOVERNED_MARKER | governance_validators_ext4.py | ADVISORY |
| promoted_code_changed_without_reopening | V119 | PROMOTION_VIOLATION | governance_validators_ext4.py | ADVISORY |
| certification_without_arch_proof | V120 | CERTIFICATION_GAP | governance_validators_ext4.py | ADVISORY |
| missing_public_documentation | V121 | DOC_GAP | governance_validators_ext4.py | ADVISORY |
| broken_traceability_chain | V122 | TRACEABILITY_GAP | governance_validators_ext4.py | ADVISORY |
| ungoverned_code_marker | V123 | UNGOVERNED_MARKER | governance_validators_ext4.py | ADVISORY |
| semantic_stub_constant_return | V124 | SEMANTIC_STUB | governance_validators_ext4.py | ADVISORY |
| new_product_bypassing_architecture_gate | V125 | ARCH_GATE_BYPASS | governance_validators_ext4.py | BLOCKING |
| file_outside_approved_qname_layout | V126 | NO_PARSING_SUBDIR/NO_MODEL_SUBDIR | governance_validators_ext4.py | ADVISORY |
| type_outside_approved_qname_hierarchy | V127 | VIOLATION_NO_QNAME | governance_validators_ext4.py | ADVISORY |
| **dotnet_parser_required** | **V128** | **FULL_REBUILD_STUB** | **governance_validators_ext4.py (PLANNED)** | **PLANNED** |
| **compat_facade_behavioral** | **V129** | **COMPAT_NOT_BEHAVIORAL** | **governance_validators_ext4.py (PLANNED)** | **PLANNED** |

## Gaps with No Current Validator Coverage

| Gap Class | Description | Planned Validator | TC |
|-----------|-------------|------------------|----|
| FULL_REBUILD_STUB | .NET format is stub-only (HTML/MD/TXT/ZST have no real parsers) | V128: dotnet_parser_required | TC-VAL-002 |
| COMPAT_NOT_BEHAVIORAL | Compat/ facade declares inheritance but has no real behavior | V129: compat_facade_behavioral | TC-VAL-002 |

## Pre-commit Hook Status (FINDING-001)

Current `.git/hooks/pre-commit` → `.hooks/pre-commit-skill-guard` (symlink present).
`pre-commit install` (full ruff + architecture hooks) not confirmed.
All V35/V77/V78/V110 validators are LOCALLY CALLABLE but not auto-blocking on commit.
**Remediation: TC-CQGA-014 (blossom) — install and verify full pre-commit chain.**

## Acceptance: PASS — all gap classes mapped to validators or PLANNED entries
