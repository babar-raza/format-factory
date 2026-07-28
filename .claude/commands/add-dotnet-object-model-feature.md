---
version: "1.1"
last-updated: "2026-07-03"
phase-available: "3+"
gate-required: "Explicit product implementation authorization for the named format"
generated_by: r92-worker
---

# /add-dotnet-object-model-feature

## Step 0 — Execution Manifest (run BEFORE the mandatory pre-check below and every other step)

```
python -m tools.governance.skills_first.manifest create \
  --task-id <task_id> --agent-type CLAUDE_CODE \
  --operation "<one-line description of this invocation>" \
  --skill add-dotnet-object-model-feature \
  --allowed-paths src/net/<format_id>/** \
  --write
```

Record the printed `execution_id`. On `ManifestError`, STOP -- do not proceed
until the manifest is created. This is what lets the tool-layer skill gate
(`tools/supervisor/coordination/hooks/skill_gate.py`) recognize this invocation
as `MANIFEST_COVERING` instead of blocking it once `check_mode:skill_resolution`
is promoted to `enforcing` for `src/net/`.

## MANDATORY PRE-CHECK: QName Compliance

Before modifying any model class:
1. Read `registry/odf-ontology/qname-to-code-map.yaml` — identify the ODF QName for this feature.
2. Add `public const string QName = "<spec:qname>";` to the class if not present.
3. If no ODF QName exists for this feature, stop with `BLOCKED_SPEC_QNAME_REQUIRED`.

**STOP and reject (`BLOCKED_INVALID_TASK_SHAPE`) if:**
- Implementation would use `Dictionary<string, X?> _field = new()` to back persistent document state.
  Dictionary fields for persistent features are PROHIBITED. Implement XML read/write path instead.
- Feature adds a property that claims persistence but has no XML source.

**For any property setter that persists document state:**
Add a Type 4 roundtrip test before closing:
`SetX(value) → Save() → Load() → Assert.Equal(value, GetX())`
A setter task is INCOMPLETE without this test.

---

Add one bounded object-model feature to a commercial .NET product. This command extends
an existing parsed object model (e.g., WorkbookModel, DocumentModel, ImageModel) with
a new read or write capability.

## Required Inputs

- `format_id` (fods | fodt | netpbm)
- `feature_name` and user-visible behavior
- `model_class` — which object model class to extend
- exact source paths and exact test paths
- ledger entry path
- focused `dotnet test` command

## Steps

1. Read `plans/master-plan.md`, `.supervisor/skill-registry.yaml`, `product-capability-matrix/poc-targets.yaml`.
2. Confirm the sprint prompt names this skill, format, and exact paths.
3. Confirm product-code ledger and validator exist and pass before touching source.
4. Inspect the existing model class and public surface.
5. Add or modify only the exact authorized files under `src/net/<format_id>/`.
6. Add focused tests: normal, boundary, invalid-input.
7. Write ledger record with skill ID, format, model class, changed paths, behavior, tests run.
8. Run ledger validator and focused dotnet tests.
9. Do not commit, push, publish, change gates.

## Allowed Paths

- `src/net/<format_id>/Model/**`
- `src/net/<format_id>/<FormatId>Document.cs`
- `tests/net/<format_id>/<format_id>R<sprint>*Tests.cs`

## Forbidden Paths

- `src/python/**`
- Gate/release state files
- registry/format-registry.yaml
- plans/master-plan.md

## Stop Conditions

- Ledger or validator missing
- Writable paths exceed handoff
- Feature implies gate or commercial readiness change
- Focused tests fail

## Output Format

Report skill_id, format, feature, model class, changed files, ledger record, commands run, pass/fail.

## Validation

Complete only when ledger validation and focused dotnet tests pass.

## Rollback

1. Revert the feature addition from `src/net/<format_id>/`
2. Remove test file `tests/net/<format_id>/<format_id>R<sprint>*Tests.cs`
3. Remove the ledger entry from `reports/r90/product-code-change-ledger.json`
4. Re-run `python tools/supervisor/validate_product_code_ledger.py` to confirm PASS

## Transcript Requirement

After execution, emit a skill invocation transcript JSON to `reports/skills-r<N>/skill-transcripts/`
with: skill_id, format_id, feature_name, model_class, changed_files, test_results, ledger_entry_id, verdict.

## Sample Invocation

```
/add-dotnet-object-model-feature
# Inputs provided by execution handoff:
#   format_id: netpbm
#   feature_name: ExtractChannel
#   model_class: NetpbmImage
#   exact_source_paths: [src/net/netpbm/Model/NetpbmImage.cs]
#   exact_test_paths: [tests/net/netpbm/NetpbmR103ExtractChannelTests.cs]
#   ledger_entry_path: reports/r90/product-code-change-ledger.json
```

## Changelog

- 1.0 (2026-06-02): Initial R92 governed command.
- 1.2 (2026-06-03): Added rollback, transcript requirement, sample invocation, changelog (Skills R101).
- 1.1 (2026-07-03): TC-PQLM-007 — Added MANDATORY PRE-CHECK (QName compliance, dictionary-backing prohibition, roundtrip test requirement for setters).
