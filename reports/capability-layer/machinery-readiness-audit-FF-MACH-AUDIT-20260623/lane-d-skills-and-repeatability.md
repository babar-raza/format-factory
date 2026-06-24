# Lane D — Skills and Repeatability Audit
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-D | **Requirement:** REQ-LANE-D

## 1. Skills Inventory
- **Total registered:** 60+ (52 active, 1 suspended, 1 deprecated)
- **spec_qname_required: true:** 15 skills (add-python-api, add-dotnet-api, add-*-object-model-feature, spec-literal-*, python-qname-code-reviewer, implement-spec-stub, add-analytics-function)
- **Product tracks:** foss_python, commercial_dotnet, cross_product, spec_parity, planning, acquisition, infrastructure

## 2. SAL Integration Assessment
- **add-python-api.md:** SAL facts read BEFORE code generation (handoff validation step)
- **add-dotnet-api.md:** Same pattern — SAL facts checked before C# class generation
- **Timeline:** spec_fact_refs in execution handoff → verify against sal-facts-latest.json → code generation
- **Enforcement:** Prompt-based ("execution handoff MUST include at least one spec_fact_refs entry")

## 3. V49 Status — ALREADY EXISTS
- **Function:** validate_qname_structure() at governance_validators.py:3028-3071
- **TC reference:** TC-QNAME-VALIDATORS-001
- **Mode:** WARN-only (not blocking until backfill taskcards complete)
- **Behavior:** Uses tools/validators/qname_structure_validator.py (standalone AST scanner). Checks spec/ class files in changed_files for spec_qname attribute. Graceful fallback when scanner unavailable.
- **RC-4 UPDATE:** Original analysis stated V49 was missing. Investigation reveals V49 EXISTS but is WARN-only. The gap is not "V49 missing" but "V49 is not blocking."

## 4. V50 Insertion Point
- **After V48 import:** governance_validators.py line 3076
- **Before re-export block:** Lines 3078-3083 (run_all_governance_validators import)
- **Note:** governance_validators.py is at 3181 LOC (near cap). New validators should go in governance_validators_ext.py per established pattern.

## 5. V49 Validator Design (Updated)
Since V49 already exists as WARN-only for spec_qname attribute checking, the plan's TC-MACH-VAL-001 should be RESCOPED to:
- **Option A:** Upgrade V49 from WARN to BLOCK mode (after grace period)
- **Option B:** Add V50 for spec_fact_refs DENSITY checking (distinct from V49's spec_qname structure check)
- **Recommended:** Option B — V49 checks structure (spec_qname present), V50 checks density (≥1 spec_fact_ref per new class)
