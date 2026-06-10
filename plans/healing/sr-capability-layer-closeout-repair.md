# Healing Plan: Capability Layer Sprint Closeout Repair

## Context
Sprint `capability-feature-understanding-layer-healing-20260608-e382e5f` completed with
autonomous-cycle exit 0, but two anti-skip violations were NOT addressed before reporting:
1. MEDIUM: `dirty_git_state` — declaration has no `dirty_state_classification` field
2. LOW: `missing_sample_outputs` — no sample output generated from new FODG write/export functions

## Gap Table

| Gap ID | Description | Taskcard |
|--------|-------------|----------|
| SR-01 | `dirty_state_classification` missing from evidence declaration | SR-TC-01 |
| SR-02 | No sample output for FODG write_fodg / export_to_txt | SR-TC-02 |

---

## SR-TC-01: Add dirty_state_classification to evidence declaration

**Status:** Done
**Gap:** SR-01
**Role:** Senior engineer. Drop-in, production-ready.

**Scope:**
- Fix: Add `dirty_state_classification: sprint_work_uncommitted` to `.local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/evidence-declaration.yaml`
- Allowed: Edit the evidence declaration YAML only
- Forbidden: Change any other fields; no commits; no pushes

**Acceptance checks:**
- `dirty_state_classification` key present in declaration YAML
- `autonomous-cycle` re-run exits 0
- Anti-skip no longer reports `dirty_git_state` as MEDIUM caveat

**Deliverables:**
- Updated `evidence-declaration.yaml` with `dirty_state_classification` field
- autonomous-cycle re-run output (exit 0)

**Hard rules:**
- Do not modify any sprint work artifacts
- No git operations

**Now (runbook):**
```
1. Read evidence-declaration.yaml
2. Add `dirty_state_classification: sprint_work_uncommitted` after git_status_final
3. Re-run autonomous-cycle
4. Verify exit 0 and no MEDIUM dirty_git_state caveat
```

---

## SR-TC-02: Generate FODG sample output

**Status:** Done
**Gap:** SR-02
**Role:** Senior engineer. Drop-in, production-ready.

**Scope:**
- Fix: Run create_fodg + write_fodg to generate a `.fodg` sample file; run export_to_txt to generate a `.txt` sample
- Save to `.local/evidences/capability-feature-understanding-layer-healing-20260608-e382e5f/sample-outputs/`
- Allowed: Run Python using .local/venv; write files under evidence_root/sample-outputs/
- Forbidden: Modify source; no commits

**Acceptance checks:**
- `sample-outputs/sample_fodg_output.fodg` exists and is valid XML
- `sample-outputs/sample_fodg_text_export.txt` exists and is non-empty
- `autonomous-cycle` re-run exits 0
- Anti-skip no longer reports `missing_sample_outputs` as LOW violation

**Deliverables:**
- Two sample output files under `evidence_root/sample-outputs/`
- Review package rebuilt with samples included

**Hard rules:**
- Sample must be produced from actual running code (not hand-crafted)
- Use `.local/venv/Scripts/python` — no PYTHONPATH prefix

**Now (runbook):**
```
1. Run python script to create_fodg + write_fodg → sample_fodg_output.fodg
2. Run python script to export_to_txt → sample_fodg_text_export.txt
3. Verify both files exist and are non-empty
4. Re-run autonomous-cycle
5. Rebuild review package
```
