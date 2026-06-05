# Skills Governed Execution Hardening IV Template

**Sprint ID:** FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001
**Stream:** Skills
**Type:** Hardening / Independent Verification
**Added:** 2026-06-04

## Mission

Harden and independently verify the latest Skills/Governed Execution before Mainstream consumes it.

NOT: Mainstream implementation / plugin install / MCP promotion / evidence cleanup / template expansion beyond product consumption proof.

## Hard Prohibitions
- No src/net/* or src/python/* edits (Skills may not write product source)
- No `.claude-plugin` mutation
- No `/plugin install`
- No MCP registration
- No `.vscode/mcp.json` mutation
- No SessionStart injection
- No gate approval, push, commit, publish

## Allowed Paths
- tools/supervisor/validate_*.py (validation tools)
- .supervisor/skill-registry.yaml (updates only)
- reports/skills-product-first/
- .local/evidences/skills-hardening-iv/

## Lanes

### Lane 0: Coordinator/Safety
Declare lane ownership. Confirm no product source changes. Confirm no plugin install.

### Lane A: Evidence-to-Implementation Reconciliation
Verify bundle 70 declared work matches actual files on disk:
- Governed source-change contract exists and is valid
- `reports/skills-product-first/mainstream-consumption-packet.json` exists
- 6 reusable Mainstream templates present and valid
- 10 receiver fixtures exist with expected results
- `validate_adoption_compliance.py` runs
- `validate_skill_transcript.py` runs

### Lane B: FODS CSV Packet Hardening
Independently validate `mainstream-consumption-packet.json`:
- `GAP-FODS-DOGFOOD-CSV-DOTNET-001` target valid
- Recommended skill `add-dotnet-api` valid
- Expected test `tests/net/fods/FodsR114ExportToCsvTests.cs` referenced correctly
- Expected source `src/net/fods/FodsDocument.cs` or `FodsWorkbook.cs` referenced correctly
- Capability `dogfood_status.fods_to_csv_dotnet` correctly stated
- Packet labeled as proposed delta (not direct authority mutation)

### Lane C: Template/Transcript Validator Hardening
Verify all 6 reusable templates:
- add-dotnet-api template valid
- add-python-api template valid
- add-export template valid
- add-dogfood-pipeline template valid
- add-roundtrip-test template valid
- update-capability-matrix template valid (proposed delta only, not authority mutation)

Verify all 10 receiver fixtures produce expected outcomes:
- 1 compliant → PASS
- 8 expected-failing → correct failure modes
- 1 YES_WITH_LIMITATIONS → correct caveat

### Lane D: Product Breadth Handoff Hardening
Create/validate safe packet shells for:
- FODT Markdown dogfood/export shell
- FODT TXT dogfood/export shell
- Netpbm proof/dogfood/package shell

Each shell must:
- Be labeled `NEEDS_MAINSTREAM_DISCOVERY` when full discovery needed
- Be consumable by Mainstream as fallback handoff
- Reference expected source/test paths (not create them)
- Be valid JSON

### Lane E: Superpowers/External Skill Boundary Hardening
Verify:
- No `.claude-plugin` mutation in any executed step
- No `/plugin install` called
- No MCP registration written
- No `.vscode/mcp.json` mutation
- No SessionStart injection
- Superpowers evaluation artifacts labeled `evaluated_not_installed`

### Lane F: Cross-Stream Consumption Readiness Packet
Produce updated `reports/skills-product-first/hardening-iv-readiness.json`:
- skills_readiness_status: `SKILLS_CONSUMABLE_WITH_LIMITATIONS` or `SKILLS_CONSUMABLE`
- full_packets: [list]
- shell_packets: [list]
- receiver_fixtures: pass/fail counts
- superpowers_boundary_verified: true/false

### Lane G: Skills Hardening Tests
Write tests for:
- Packet JSON schema validation
- Fixture result verification
- Template structure validation
- Shell packet format
- Superpowers boundary checks
Target: 15+ new tests.

### Lane H: Evidence Closeout
- Write `evidence-declaration.yaml`
- Run: `.local/venv/Scripts/python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/skills-hardening-iv/evidence-declaration.yaml`
- Run: `.local/venv/Scripts/python tools/supervisor/build_declaration_review_package.py --declaration .local/evidences/skills-hardening-iv/evidence-declaration.yaml`

## Evidence Closeout Requirements
- taskcard-state.json: all CLOSED_VERIFIED
- No PENDING markers
- No product source edits
- No plugin install
- Declaration-driven autonomous-cycle run captured

## Expected Skills Readiness Status
If FODS full packet validates and FODT/Netpbm shells exist: `SKILLS_CONSUMABLE_WITH_LIMITATIONS`

## Allowed Verdicts
- `SKILLS_GOVERNED_EXECUTION_HARDENED_INDEPENDENTLY_VERIFIED`
- `SKILLS_GOVERNED_EXECUTION_HARDENED_WITH_LIMITATIONS`
- `SKILLS_GOVERNED_EXECUTION_HARDENING_FAILED_NEEDS_REWORK`

## Final Response Contract
- Exact verdict
- FODS CSV packet validation: PASS/FAIL/PARTIAL
- Shell packets: FODT Markdown/TXT, Netpbm — created or not
- Receiver fixtures: N/10 passed
- Superpowers boundary: VERIFIED or BREACH
- Test count: passed/failed/skipped
- Skills readiness status
- Evidence declaration path
- Review package absolute path: C:\Users\prora\...\
- Review package SHA-256
- Explicit: no plugin install, no product source edits, no commit, no push
