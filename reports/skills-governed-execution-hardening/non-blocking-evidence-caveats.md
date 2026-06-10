# Non-Blocking Evidence Caveats
Sprint: FORMAT-FACTORY-SKILLS-GOVERNED-EXECUTION-HARDENING-IV-001

---

Each caveat below was raised by the autonomous cycle or inspector. All are classified
as non-blocking. None require evidence repair.

---

## CAVEAT-01: Missing Sample Outputs
- Raised by: autonomous cycle anti-skip check
- Severity: LOW
- Root cause: Skills-only sprint. No product execution occurred. Sample outputs exist only
  after product code is run.
- Classification: NON_BLOCKING — expected for governance/skills sprint
- Action: None. Sample outputs are Mainstream's responsibility when executing the live handoff.

---

## CAVEAT-02: MCP Promotion Deferred
- Raised by: TC-W4-001 evaluation
- Severity: INFO
- Root cause: 4/10 criteria pass. .claude/commands/check-mcp-status.md does not exist yet.
  Registry has pre-existing `deferred` status.
- Classification: NON_BLOCKING — KEEP_DEFERRED is a valid sprint outcome per the plan
- Action: None. Deferred taskcard TC-MCP-READINESS-001 created at
  reports/skills-product-first/mcp-readiness/taskcard-TC-MCP-READINESS-001.md

---

## CAVEAT-03: wrong_stream_next_sprint (MEDIUM)
- Raised by: autonomous cycle anti-skip check
- Severity: MEDIUM
- Root cause: autonomous_cycle.py generated mainstream next-sprint.md (not skills).
  This is correct behavior — skills lane feeds Mainstream.
- Classification: NON_BLOCKING — skills output is designed to be consumed by Mainstream
- Action: None.

---

## CAVEAT-04: External Skill Wrapper Template Missing Standard Sections
- Raised by: Lane C template verification
- Severity: INFO
- Root cause: external-skill-wrapper-template.md has a different 17-section schema
  (Authority boundary, Activation gate, Source plugin, etc.) vs. the standard 15 product
  template sections.
- Classification: NON_BLOCKING — intentional different template type
- Action: None. external-skill-wrapper-template.md passes its own 17-section check.

---

## CAVEAT-05: Capability Matrix Update as Mandatory Guidance
- Raised by: Lane B packet hardening
- Severity: LOW
- Root cause: expected_capability_matrix_update in mainstream-consumption-packet.json
  says "fods.dogfood_status.fods_to_csv_dotnet → IMPLEMENTED" which reads as a mandatory
  direct update to poc-targets.yaml.
- Classification: NON_BLOCKING — existing packet accepted with limitation.
  Future packets should use proposed_delta instead.
- Action: Hardening note added in fods-csv-packet-hardening.md. Next packet version
  should downgrade to proposed delta.

---

## Summary
Total caveats: 5
All non-blocking.
Zero items require evidence repair.
