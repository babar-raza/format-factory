# Lane D: Skill Inventory and Gaps
# Sprint: ff-machinery-readiness-audit-20260625

## Skill Registry Overview

**Location:** .supervisor/skill-registry.yaml
**Registry ID:** r98-governed-skills-expanded
**Status:** active_fail_closed
**Last Updated:** 2026-06-12

### Global Controls (enforced by registry — fail-closed)
```yaml
commercial_product_ready_changes_allowed: false
commit_allowed: false
gate_changes_allowed: false
product_code_ledger_required_before_source_edit: true
push_allowed: false
publication_changes_allowed: false
skill_invocation_transcript_required: true
source_edits_require_explicit_handoff: true
```

**Key finding:** skill-registry.yaml is fail-closed — any product source edit without a
registered skill triggers BLOCKED_SKILL_GAP verdict (missing_skill_workflow).

---

## Product-Generating Skills (Direct Evidence)

### /add-python-api (skill_id: add-python-api)
- **Purpose:** Add Python FOSS API function to a format codec
- **Track:** foss_python
- **QName Enforcement:** YES (KC-PYTHON-001 knowledge contract)
- **SAL Facts:** REQUIRED (spec_fact_ref required in handoff)
- **Capability Layer:** REQUIRED (gap_ledger_ref required in handoff)
- **Mandatory Validations:** loc_cap_not_exceeded, spec_fact_ref_in_sal_output, gap_ledger_ref_exists, no_forbidden_module_target
- **Repeatability:** HIGH — well-defined handoff fields
- **Idempotency:** create_or_update
- **Assessment:** STRONG — enforces SAL linkage AND gap_ledger_ref; correct skill design

### /add-dotnet-api (skill_id: add-dotnet-api)
- **Purpose:** Add .NET commercial API to format project
- **Track:** commercial_dotnet
- **QName Enforcement:** YES (via knowledge contracts)
- **SAL Facts:** REQUIRED
- **Capability Layer:** REQUIRED
- **Assessment:** STRONG — mirrors Python skill with .NET conventions

### /add-analytics-function (skill_id: add-analytics-function)
- **Purpose:** Add spec-backed domain analytics function
- **Track:** foss_python_spec_domain
- **Status:** SUSPENDED since 2026-06-18 (plan keen-dancing-hopper)
- **Reason:** Arithmetic-only functions with no spec backing; caused GOV_BLOCK:monolith_detection_validator
- **Mandatory Validations:** loc_cap_not_exceeded, spec_fact_ref_in_sal_output, gap_ledger_ref_exists, no_forbidden_module_target, analytics_skill_required_v41
- **Overflow splits:** PERMANENTLY FORBIDDEN (MODULE-NAME-001)
- **Assessment:** SUSPENDED — correct suspension; when reactivated must require spec_fact_ref

### /add-dogfood-export (skill_id: add-dogfood-export)
- **Purpose:** Add cross-format export using Format Factory library
- **Track:** cross_product_export
- **QName Enforcement:** NO (export patterns don't require spec_qname)
- **Assessment:** CORRECT scope — exports are behavioral, not spec-mapped

### /add-python-object-model-feature (skill_id: add-python-object-model-feature)
- **Purpose:** Add object model feature to existing domain model class
- **Assessment:** Enforces spec_qname requirement for domain model changes

### /add-same-format-writer-feature (skill_id: add-same-format-writer-feature)
- **Purpose:** Add or improve same-format write/serialize capability
- **Assessment:** Enforces roundtrip tests

### /add-roundtrip-test (skill_id: add-roundtrip-test)
- **Purpose:** Add load→modify→write→reload roundtrip test
- **Assessment:** Gate 6 evidence generation

### /implement-spec-stub (skill_id: implement-spec-stub)
- **Purpose:** Implement a spec stub (convert architecture_only → implementing)
- **Assessment:** Fills Compat/ facades with behavioral methods

### /decompose-monolithic-codec (skill_id: decompose-monolithic-codec)
- **Purpose:** Extract analytics from monolithic codec file
- **Assessment:** SRC-STANDARDIZATION-001 is the governance entry for this skill's use

---

## Governance and Infrastructure Skills

### /check-gate (skill_id: check-gate)
- Reads registry/gate-criteria.yaml, reports/gate11/, poc-targets.yaml
- Returns machine-readable gate status
- Verified: `/check-gate fods 11` → CONDITIONALLY_READY (6/7 pass; G11-G TRUE_EXTERNAL_GATE)

### /create-taskcard (skill_id: create-taskcard)
- Creates governed YAML taskcard with required fields
- Enforces: item_id, status, severity, allowed_paths, forbidden_paths, evidence_required

### /score-format (skill_id: score-format)
- 7-factor 100pt scoring model
- Used for Gate 9 readiness assessment

### /build-evidence-bundle (skill_id: build-evidence-bundle)
- Creates ZIP evidence bundle
- Required for sprint closeout

### /check-skill-coverage (skill_id: check-skill-coverage)
- Pre-sprint check: verifies a registered skill exists before product source edit
- Missing skill → BLOCKED_SKILL_GAP verdict + taskcard created

### /validate-skill-contracts (skill_id: validate-skill-contracts)
- Verifies all VERIFIED_CURRENT contracts in .supervisor/knowledge/contracts/
- Blocks sprint if contracts stale

---

## Skill Gap Analysis

### GAP-SKILL-001: No automated qname-backfill skill
**Severity:** HIGH
**Evidence:** qname-backfill.md NOT FOUND in .claude/commands/; skill not in registry
**Impact:** All 19 format backfill migrations must be manual; no governed workflow
**Required:** Create /qname-backfill skill that: scans format → maps symbols → generates Compat/ stubs → validates V53 → declares as PRODUCT_SOURCE work item

### GAP-SKILL-002: No spec-retrieval skill wired to SAL pipeline
**Severity:** HIGH
**Evidence:** TC-0015 (spec-retrieval-strategy-evaluation) is OPEN in next-sprint.md; SAL pipeline dormant
**Impact:** Facts are manually seeded; no skill exists to trigger SAL pipeline for a new format
**Required:** Create /sal-pipeline-heal skill (or extend existing) to wire spec_parser → spec_normalizer → fact_extraction for a given format

### GAP-SKILL-003: capability_compiler skill missing (listed in skill-registry.yaml known_open_gaps)
**Severity:** HIGH
**Evidence:** skill-registry.yaml missing_skill_workflow.known_open_gaps[0]: "capability_compiler" status=backlog
**Impact:** No skill converts gap-ledger entry into code skeleton; prevents automated feature planning
**Required:** Create /build-capability-routes or /feature-compiler skill (per capability-fact-to-feature-production-plan.md)

### GAP-SKILL-004: pre_sprint_governance_hook skill missing
**Severity:** MEDIUM
**Evidence:** skill-registry.yaml missing_skill_workflow.known_open_gaps[2]: "pre_sprint_governance_hook" status=backlog
**Impact:** No automatic governance check before each product sprint starts
**Required:** Create hook that runs governance validators before allowing product source edits

### GAP-SKILL-005: ci_transcript_verification skill missing
**Severity:** MEDIUM
**Evidence:** skill-registry.yaml missing_skill_workflow.known_open_gaps[3]: "ci_transcript_verification" status=backlog
**Impact:** skill_invocation_transcript_required is a global_control but no CI verification
**Required:** CI step that verifies skill transcript exists for every modified src/ file

### GAP-SKILL-006: extract_analytics_from_monolith not all formats covered
**Severity:** MEDIUM
**Evidence:** skill-registry.yaml missing_skill_workflow.known_open_gaps[1]: "extract_analytics_from_monolith" status=backlog
**Impact:** 5+ formats (CSV, DIF, FODG, Gnumeric, ABW) still have mixed model/analytics files at LOC cap
**Required:** Use /decompose-monolithic-codec for each remaining format

---

## Skill Repeatability Assessment

| Dimension | Status | Evidence |
|---|---|---|
| Skill-first execution | YES | skill_invocation_transcript_required=true in global_controls |
| Spec fact traceability | YES | spec_fact_ref required by add-python-api, add-analytics-function |
| Gap ledger linkage | YES | gap_ledger_ref required by add-python-api |
| LOC cap enforcement | YES | loc_cap_not_exceeded mandatory validation |
| QName enforcement | YES (Python) / PARTIAL (.NET) | V43/V53 for Python; no equivalent for .NET |
| Idempotency | YES | all skills: create_or_update |
| Skill invocation transcript | REQUIRED | global_control; transcript_required=true |
| Missing skill detection | YES | check-skill-coverage pre-sprint; BLOCKED_SKILL_GAP |

**Overall Skill Readiness:** HIGH for existing skills; LOW for missing skills (qname-backfill, SAL pipeline, capability compiler)

---

## Skill-to-Lane Mapping

| Skill | Lane | Status |
|---|---|---|
| /add-python-api | Product (Lane C3) | Active |
| /add-dotnet-api | Product (Lane C3) | Active |
| /add-analytics-function | Product (SUSPENDED) | Suspended 2026-06-18 |
| /add-dogfood-export | Product (Lane C4) | Active |
| /decompose-monolithic-codec | Machinery (SRC healing) | Active but gaps exist |
| /implement-spec-stub | Product (Compat/ fill) | Active |
| /check-gate | Governance | Active |
| /score-format | Governance | Active |
| /build-capability-routes | MISSING | Backlog |
| /sal-pipeline-heal | MISSING | No command file found |
| /qname-backfill | MISSING | No command file found |
