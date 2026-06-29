# Lane Separation and Collision Risk — ff-arch-20260621-001

## Current State

Lane separation is DEFINED in `plans/strategic/spec-to-feature-radical-correction-plan.md` but
NOT mechanically enforced. Collision between machinery and product lanes has occurred
historically and can occur again.

---

## Lane Collision Scenarios

### Scenario 1: Product deepening runs before system healing (HIGH RISK — CONFIRMED)

**What happens:** An agent runs a product deepening sprint (add analytics function) before
Lanes 1-6 healing is complete. Result: more format-prefixed code is added, deepening the
technical debt that healing lanes are trying to repair.

**Evidence this occurred:** MEMORY.md records: "after TC-C3-001/TC-C3-003, fell back to
next-sprint.md product deepening instead of continuing to TC-DIAG-001."

**Current mitigation:** TC-GUARD-001 (BLOCK mode) requires spec_fact_refs for new product source.
V42 blocks the suspended analytics rotation.

**Remaining risk:** TC-GUARD-001 can be bypassed if agent declares a synthetic capability_ref.
V42 only blocks the specific _mod_N_times_M pattern, not general spurious product additions.

---

### Scenario 2: Skill writes source at wrong location (MEDIUM RISK — LIKELY OCCURRING)

**What happens:** A skill like `/add-dotnet-api` creates `Model/FodsNewFeature.cs` at the
wrong path instead of `Compat/Fods/FodsNewFeature.cs` or `Spec/Table/NewElement.cs`.

**Current mitigation:** None. No validator checks file path against qname-to-code-map.yaml.

**Required fix:** Add a source path validator that checks new .cs/.py file paths match
the canonical location for their QName/capability.

---

### Scenario 3: Spec/ stubs remain architecture_only indefinitely (MEDIUM RISK — IN PROGRESS)

**What happens:** The FODT spec/ stubs were created as architecture_only on 2026-06-20.
If product deepening continues without implementing the stubs, the system stays in
"spec layer partially created, never activated" state permanently.

**Current state:** `compat.py` explicitly blocks import from spec/ until stubs are implemented.
This is documented. But no sprint task forces stub implementation.

**Required fix:** A governed taskcard that implements spec/ stubs and switches compat.py.

---

### Scenario 4: SAL pipeline runs without product generation (LOW RISK — STRUCTURAL)

**What happens:** SAL extracts facts but they have no path to source. The capability
compiler converts them to taskcards. Taskcards sit in .local/ without execution.

**Current state:** This is the normal operating mode. The pipeline is advisory only.

**Required fix:** An automated source generation step that converts taskcards to source.

---

## Collision Risk Matrix

| Collision Type | Probability | Impact | Mitigation |
|---|---|---|---|
| Product deepening before healing | HIGH (proven) | HIGH (technical debt growth) | TC-GUARD-001, V42 |
| Wrong source path from skill | MEDIUM | MEDIUM (restructuring cost) | None |
| Spec stubs stuck at architecture_only | HIGH (by inertia) | HIGH (no Gen 4 ever activates) | Manual sprint |
| Analytics rotation restarts | LOW (V42 blocks) | MEDIUM | V42 validator |
| Cross-chat state contamination | LOW (CCI-MVP) | HIGH (sprint collision) | CCI-MVP, plan lock |
| Agent self-approves Gate 11 | LOW (stop rules) | CRITICAL | stop_reason_adjudicator |

---

## Recommended Collision Prevention Additions

1. **Source path validator**: Before any .cs/.py file is written, check path against qname-to-code-map.yaml
2. **Lane active check**: `check_continuation.py` should verify healing lanes are complete before allowing product deepening
3. **Spec stub completion gate**: No new product deepening for FODT until spec/ stubs are `implemented`
4. **Compat.py switch validator**: Test that confirms FodtParagraph from spec/ matches behavior from models.py
5. **QName class name validator**: New class names in PRODUCT_SOURCE must match canonical name in registry
