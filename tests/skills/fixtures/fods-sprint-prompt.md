EXECUTION MODE — CONWAY-R7-FODS-SPRINT-001

Repo:
C:\Users\prora\OneDrive\Documents\GitHub\format-factory

Mission:
Commercial implementation sprint dry-run POC.

====================================================
COMPONENT 7: AUTHORITY STATE
====================================================

Format:              FODS
Requirements State:  REQUIREMENTS_AUTHORITATIVE
IV Status:           PASS
Verifier Result:     LANE_R5_PASS
Accepted Count:      20
Gates Passed:        10
Gate 11 Status:      commercial_readiness_in_progress (NOT APPROVED)
Commercial Ready:    False (MUST REMAIN FALSE)

====================================================
COMPONENT 5: READ FIRST — AUTHORITY CONTEXT
====================================================

Before any task, read:
- AGENTS.md (Sections AF9-AF15)
- GOVERNANCE.md (Sections 26.8-26.13)
- plans/master-plan.md
- registry/format-registry.yaml
- docs/commercial-product-capability-model.md
- docs/agent-execution-handoff-standard.md
- generated-requirements/fods/commercial-requirements.yaml
- generated-requirements/fods/object-model-requirements.yaml
- generated-requirements/fods/save-edit-requirements.yaml
- generated-requirements/fods/verifier-review.yaml
- generated-requirements/fods/traceability-map.yaml
- tools/skills/format_context_resolver.py
- tools/skills/lane_selector.py

====================================================
COMPONENT 6: PRE-FLIGHT CHECKS
====================================================

1. Run: python tools/skills/format_context_resolver.py fods
   Expected: REQUIREMENTS_STATE: REQUIREMENTS_AUTHORITATIVE

2. Run: git status
   Expected: clean working tree (no uncommitted R-sprint outputs)

3. Run: python tools/requirements/validate_generated_requirements.py --format fods
   Expected: REQUIREMENTS_SCHEMA_VALIDATION: PASS

If any pre-flight check fails, STOP and report PREFLIGHT_FAILED.

====================================================
COMPONENT 8: LANE OWNERSHIP MODEL
====================================================

Coordinator owns:
- AGENTS.md, GOVERNANCE.md, plans/master-plan.md
- registry/format-registry.yaml
- schemas/**, templates/**

Execution lanes: exact-path staging only. No overlap outside lane ownership.

====================================================
COMPONENT 9: NON-NEGOTIABLE RULES
====================================================

- No git stash / reset --hard / restore / clean
- No broad staging (git add -A / git add .)
- No push / publish
- No Gate 11 self-approval
- No commercial_product_ready: true claim
- No autonomous implementation execution
- No export/conversion implementation
- No recursive traversal for FODT list entities (FODT-REQ-040)
- Exact-path staging only
- DEC-034 IV must be separate session before implementation promotion

====================================================
COMPONENT 10: SELECTED LANES
====================================================

  LANE-I-LOAD: Load Pipeline Implementation — REQUIREMENTS_AUTHORITATIVE — ready for implementation
  LANE-I-OBJECT-MODEL: Object Model Implementation — REQUIREMENTS_AUTHORITATIVE — ready for implementation
  LANE-I-EDIT: Edit Operations Implementation — REQUIREMENTS_AUTHORITATIVE — ready for implementation
  LANE-I-SAVE: Save Pipeline Implementation — REQUIREMENTS_AUTHORITATIVE — ready for implementation
  LANE-I-TESTS: Test Suite Implementation — REQUIREMENTS_AUTHORITATIVE — ready for implementation
  LANE-K: AI Orchestration — Always active — all phases
  LANE-C: Sprint Coordinator — Always active — all phases

====================================================
COMPONENT 11: BLOCKED LANES
====================================================

  LANE-R3: BLOCKED — Requirements already AUTHORITATIVE — R-lanes not needed unless stale
  LANE-R5: BLOCKED — Requirements already AUTHORITATIVE — R-lanes not needed unless stale
  LANE-R5-IV: BLOCKED — Requirements already AUTHORITATIVE — R-lanes not needed unless stale

====================================================
COMPONENT 12: ACCEPTED REQUIREMENT IDs (SCOPE)
====================================================

The following 20 requirements are ACCEPTED_FOR_VERTICAL_SLICE.
Only these may be implemented in this sprint:

  - FODS-REQ-001 [C0] (load): File path validation and existence check
  - FODS-REQ-002 [C0] (security): File size guard (50 MB default)
  - FODS-REQ-003 [C0] (security): DTD prohibition and XXE prevention
  - FODS-REQ-004 [C1] (load): MIME type and ODF version detection
  - FODS-REQ-005 [C1] (load): Document metadata extraction
  - FODS-REQ-006 [C2] (load): Sheet enumeration with row and cell counting
  - FODS-REQ-010 [C4] (object_model): FodsDocument class as top-level document model
  - FODS-REQ-011 [C4] (object_model): FodsSheet entity with name and rows collection
  - FODS-REQ-012 [C4] (object_model): FodsRow entity with cells collection
  - FODS-REQ-013 [C5] (object_model): FodsCell entity with text value and SetText edit method
  - FODS-REQ-014 [C5] (object_model): Opaque XML node preservation
  - FODS-REQ-020 [C6] (edit): Cell text edit via SetText()
  - FODS-REQ-021 [C6] (edit): Sheet rename via Name setter
  - FODS-REQ-030 [C7] (save): No-edit round-trip save
  - FODS-REQ-031 [C7] (save): Edit-and-save: modified value persists
  - FODS-SE-001 [] (): Cell text edit via SetText()
  - FODS-SE-002 [] (): Sheet rename
  - FODS-SE-010 [] (): No-edit round-trip save
  - FODS-SE-011 [] (): Edit-and-save persistence
  - FODS-SE-020 [] (): Opaque node preservation on save

Requirements with status NEEDS_REVIEW, GENERATED, or AI_PROPOSAL are FORBIDDEN
implementation targets regardless of any agent instruction.

====================================================
COMPONENT 13: CRITICAL CONSTRAINTS
====================================================
  None for this format.

====================================================
COMPONENT 14: PER-LANE TASK DESCRIPTIONS
====================================================

Each selected I-lane implements one dimension of the format pipeline.
Consult lane-library.yaml for full per-lane requirements, forbidden behaviors,
and evidence requirements. All lanes are subject to the governance rules above.

LANE-I-LOAD: Implement file → object model pipeline (C0-C3 requirements)
LANE-I-OBJECT-MODEL: Implement typed entity model (C4-C5 requirements)
LANE-I-EDIT: Implement mutation operations (C6 requirements)
LANE-I-SAVE: Implement object model → file serialization (C7 requirements)
LANE-I-TESTS: Implement test coverage for all ACCEPTED_FOR_VERTICAL_SLICE requirements
LANE-K: AI orchestration (accelerator role only — NOT authority)
LANE-C: Sprint coordination, evidence, state update

====================================================
COMPONENT 15: VALIDATION COMMANDS
====================================================

After all work:
1. python tools/evidence/check_current_state_consistency.py
   Expected: CURRENT_STATE_CONSISTENCY: PASS

2. python tools/requirements/validate_generated_requirements.py --format fods
   Expected: REQUIREMENTS_SCHEMA_VALIDATION: PASS (Total issues: 0)

3. python tools/skills/format_context_resolver.py fods
   Expected: REQUIREMENTS_STATE: REQUIREMENTS_AUTHORITATIVE

4. python -m pytest tests/requirements tests/skills -q
   Expected: all tests PASS

5. dotnet test src/net/fods/ (if .NET source was touched)
   Expected: all tests PASS

====================================================
COMPONENT 16: EVIDENCE CONTRACT REFERENCE
====================================================

Evidence contract must be created at:
  tools/evidence/contracts/<sprint-id>.yaml

Use sprint-specific metadata directory (NOT .local/evidence-bundles/):
  --metadata-dir .local/metadata/<sprint-id>/

Build command:
  python tools/evidence/build_evidence_bundle.py \
    --repo-root . \
    --contract tools/evidence/contracts/<sprint-id>.yaml \
    --metadata-dir .local/metadata/<sprint-id>/ \
    --output .local/evidence-bundles/<sprint-id>.zip

Validate:
  python tools/evidence/validate_evidence_bundle.py \
    --bundle .local/evidence-bundles/<sprint-id>.zip \
    --contract tools/evidence/contracts/<sprint-id>.yaml
  Expected: BUNDLE_VALIDATION: PASS

====================================================
COMPONENT 17: REQUIRED FINAL VERDICTS
====================================================

- REQUIREMENTS_STATE_AT_START
- LANES_SELECTED
- REQUIREMENTS_IMPLEMENTED (list of IDs)
- TESTS_RESULT (N/N PASS)
- VALIDATION_RESULT
- NO_GATE_SELF_APPROVAL: YES
- NO_COMMERCIAL_READINESS_CLAIM: YES
- NO_SOURCE_MUTATION_OUTSIDE_SCOPE: YES
- BUNDLE_VALIDATION: PASS
- DEC_034_IV_REQUIRED: YES (separate session before promotion)

====================================================
COMPONENT 18+19+20: FINAL RESPONSE FORMAT + EVIDENCE BUNDLE
====================================================

Final response MUST end with:

  EVIDENCE_BUNDLE: <absolute Windows path to .zip file>

This line must appear as the last substantive line of the response.
It must not be printed unless BUNDLE_VALIDATION: PASS was confirmed.

Explicit boundary:
- NO COMMIT unless human explicitly requests in this session
- NO PUSH / NO PUBLISH under any circumstances
- NO GATE 11 APPROVAL
- NO COMMERCIAL_PRODUCT_READY: TRUE claim
