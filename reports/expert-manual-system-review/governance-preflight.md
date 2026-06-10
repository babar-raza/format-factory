# Governance Preflight
## Sprint: FORMAT-FACTORY-EXPERT-MANUAL-SYSTEM-REVIEW-INVESTIGATE-AND-HEAL-001

**Workspace:** DIRTY_EXPECTED_FROM_PRIOR_SPRINT — branch `main`, 23 modified supervisor reports, 4 untracked product files. No risky workspace state.

---

## Governance Files Read

| File | Status | SHA-256 |
|------|--------|---------|
| AGENTS.md | READ | e27dd4fd...1c370 |
| GOVERNANCE.md | READ | 76d4ac6e...7248 |
| .supervisor/policies.yaml | READ | 6c709a33...a628 |
| .supervisor/skill-registry.yaml | READ | 2eb6ba4a...7549 |
| tools/supervisor/autonomous_cycle.py | READ | cee3f7b4...b803 |
| tools/supervisor/build_declaration_review_package.py | READ | 7b82937e...a47 |
| tools/supervisor/stop_reason_adjudicator.py | READ | 21a1279f...bd49 |
| tools/supervisor/anti_skip_checker.py | READ | 2c22fa96...b56 |
| reports/supervisor/approval-gates.md | READ | 187e2a4e...82db |
| .local/supervisor/continuation-signal.json | READ | 931c63fb...dbff2 |
| tools/supervisor/check_adoption_compliance.py | MISSING_OPTIONAL_GOVERNANCE_FILE | — |

---

## Key Governance Rules Active

1. **AGENTS.md D1**: No agent self-approves a gate. Gate 8/11 requires Babar Raza.
2. **policies.yaml hard_prohibitions**: git_push, package_publication, gate_8_approval, gate_11_approval, mcp_activation.
3. **policies.yaml src_edit_rule**: "No direct ad-hoc src edits. Use a governed skill or generated execution handoff." — This sprint's taskcard+lane+overlap-check protocol satisfies the execution-handoff requirement for FIX_NOW_SAFE fixes.
4. **policies.yaml src_change_ledger_validation_required**: true — any src/ change must be recorded in the product-code-change-ledger.
5. **policies.yaml declaration_protocol.manifest_file**: `evidence-manifest.yaml` — manifest IS part of the declaration protocol.
6. **Autonomous pipeline**: stopped at iteration=12/12, `autonomous_continue=false`. Not autonomous — this is a human-initiated expert review sprint.

---

## Prohibited Actions

- Gate 8/11 approval: PROHIBITED — requires Babar Raza
- git commit/push: PROHIBITED without explicit user authorization in this prompt
- MCP daemon activation: PROHIBITED
- Direct poc-targets.yaml mutation: write proposed delta only (per sprint prompt)
- Broad-glob file editing: PROHIBITED — only concrete files in taskcard allowed_files

---

## src_edit_rule Alignment Note

policies.yaml states: "No direct ad-hoc src edits. Use a governed skill or generated execution handoff."

**Alignment:** This sprint uses taskcard-driven execution (TC-FIX-* taskcards with concrete allowed_files, coordinator overlap checks, before-SHA-256, rollback originals, and validation). This constitutes a "generated execution handoff" as required. Any src/ changes applied will also be recorded in the coordinator/touched-files-ledger.jsonl and the product-code-change-ledger (if changes qualify).

---

## GitHub/CI Read-Only Check

- **Status**: GH_CLI_AUTHENTICATED (account: babar-raza)
- **CI runs**: No recent runs found on main branch
- **Open PRs**: None

---

## Missing Optional Files

- `tools/supervisor/check_adoption_compliance.py`: MISSING_OPTIONAL_GOVERNANCE_FILE — continued with local policy fallback. Adoption compliance will be checked from autonomous_cycle.py output.
