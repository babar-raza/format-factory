# Skill Inventory and Gaps — ff-arch-20260621-001

## Skills Present (.claude/commands/)

| Skill | File | Purpose | QName Enforced? | Spec Required? |
|-------|------|---------|-----------------|----------------|
| add-analytics-function | add-analytics-function.md | Add analytics function | NO | NO (spec_qname_required: false) |
| add-dogfood-export | add-dogfood-export.md | Add dogfood export path | NO | NO |
| add-dotnet-api | add-dotnet-api.md | Add .NET API method | NO | NO |
| add-dotnet-object-model-feature | add-dotnet-object-model-feature.md | Add .NET object model class | UNKNOWN | UNKNOWN |
| add-installed-package-example | add-installed-package-example.md | Add installed package example | NO | NO |
| add-python-api | add-python-api.md | Add Python API function | NO | NO |
| add-python-object-model-feature | add-python-object-model-feature.md | Add Python object model | UNKNOWN | UNKNOWN |
| add-roundtrip-test | add-roundtrip-test.md | Add roundtrip test | NO | NO |
| add-same-format-writer-feature | add-same-format-writer-feature.md | Add writer feature | NO | NO |
| autonomous-loop | autonomous-loop.md | Run autonomous loop | N/A | N/A |
| build-context-pack | build-context-pack.md | Build SAL context pack | N/A | N/A |
| build-evidence-bundle | build-evidence-bundle.md | Build evidence bundle | N/A | N/A |
| check-gate | check-gate.md | Check gate readiness | N/A | N/A |
| check-release-boundary | check-release-boundary.md | Check release boundary | N/A | N/A |
| create-acquisition-pack | create-acquisition-pack.md | Create acquisition pack | N/A | N/A |
| create-taskcard | create-taskcard.md | Create taskcard | N/A | N/A |
| post-sprint-audit | post-sprint-audit.md | Sprint audit | N/A | N/A |
| post-sprint-loop | post-sprint-loop.md | Sprint loop control | N/A | N/A |
| python-reduced-spec-parity-model | python-reduced-spec-parity-model.md | Spec parity model | PARTIAL | PARTIAL |
| score-format | score-format.md | Score a format | N/A | N/A |
| spec-literal-qname-to-code-mapping | spec-literal-qname-to-code-mapping.md | QName-to-code mapping | YES | YES |
| spec-parity-verification | (no file found by that name) | Verify spec parity | UNKNOWN | UNKNOWN |
| validate-product-code-ledger | validate-product-code-ledger.md | Validate code ledger | PARTIAL | PARTIAL |

---

## Critical Skill Gaps

### Gap 1: No QName enforcement in /add-python-api and /add-dotnet-api

These are the most-used product generation skills. They produce functions and classes
without any requirement to:
1. Reference a spec QName
2. Place classes in canonical locations (Table/, Text/, Office/)
3. Check the qname-to-code-map.yaml before naming a class
4. Produce a `spec_qname` attribute on model classes

**Impact**: Every API added through these skills is at risk of using format-prefixed names.

### Gap 2: /spec-literal-qname-to-code-mapping is not integrated into product deepening

This skill knows how to map spec QNames to code. It's available but NOT called
before product deepening sprints run. Product deepening sprints call `/add-python-api`
instead.

### Gap 3: /add-analytics-function is suspended but skill remains

The analytics rotation was suspended (per MEMORY.md: "Do NOT restart the rotation").
The skill exists. TC-GUARD-001 blocks new analytics functions without gap_ledger_ref.
But the skill itself doesn't enforce this — enforcement is in `autonomous_cycle.py`.

### Gap 4: No skill for implementing spec/ stubs from architecture_only to implemented

The FODT spec/ stubs are `architecture_only`. There is no skill that:
1. Reads a qname-registry entry
2. Generates the full implementation from the stub
3. Updates the status to `implemented`
4. Switches `compat.py` to import from `spec/`

### Gap 5: Skills cannot regenerate source safely

No skill has a "regenerate from spec" capability. If source is malformed, the only
option is a manual rewrite. There is no governed source regeneration procedure.

### Gap 6: /add-dotnet-object-model-feature doesn't know about Compat/ pattern

If this skill creates object model classes, it may place them at the wrong location
(e.g., `Model/FodsCell.cs` instead of `Compat/Fods/FodsCell.cs` with a canonical target).

---

## Governance Validators (tools/supervisor/governance_validators.py)

Total validators: 38 (confirmed from MEMORY.md)

Key validators relevant to QName/spec compliance:
- V41: `validate_analytics_skill_required` — ANALYTICS.PY changes need skill attribution
- V42: `validate_deepening_suspension` — blocks _mod_N_times_M functions
- TC-GUARD-001: PRODUCT_SOURCE items without gap_ledger_ref/spec_fact_refs → rework_items
- TC-GUARD-002: purpose_check — PURPOSEFUL/UNPURPOSEFUL/NOT_APPLICABLE classification

**Missing validators:**
- No validator checking that class names in new source match qname-to-code-map.yaml
- No validator that new .cs/.py files go to the correct canonical location
- No validator enforcing `spec_qname` attribute on model classes
