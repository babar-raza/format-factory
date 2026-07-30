---
artifact_id: FF6-EVENT-30-RUNBOOK
artifact_type: immutable_checkpoint_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 30 exact resume runbook

## 1. Verify repository authority

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor e13e103de0bb789ff51a8e931af0fb649474be20 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py
```

Only GitLab `origin/main` is authorized. If the current journal has Event 31
or later, validate and follow the newer event.

## 2. Register and coordinate

Register a fresh provider identity using the repository coordination CLI.
Query status, live leases, and conflicts. Do not reuse another provider's
identity. Claim only exact files needed after RED establishes mutation scope.

## 3. Replay the immutable artifacts

```powershell
.venv\Scripts\python.exe tools\spec\xliff_core_candidate_adjudication.py `
  --candidate-census reports\ff6\xliff-core-authority-candidate-census.yaml `
  --denominator reports\ff6\xliff-core-obligation-denominator.yaml `
  --sal-store shared\sal-facts\xliff.yaml `
  --sal-manifest shared\sal-facts\evidence\xliff.yaml `
  --sal-receipt reports\sal-verification\xliff.json `
  --decisions shared\sal-facts\evidence\xliff-core-candidate-decisions.yaml `
  --output reports\sal-verification\xliff-core-candidate-adjudications.yaml `
  --check

.venv\Scripts\python.exe tools\spec\extract_sal_facts.py `
  --format-id xliff `
  --artifact core-obligations `
  --source-20 .local\format-contracts\acquired\xliff\src-xlf-001.bin `
  --source-20-id SRC-XLF-001 `
  --source-20-sha256 aaefef5797c2387cfaaa2ca69bfeabe59fa5248535d45d3056b7fad024916055 `
  --source-21 .local\format-contracts\acquired\xliff\src-xlf-002.bin `
  --source-21-id SRC-XLF-002 `
  --source-21-sha256 73efc952aed29a31e8a6af1f985224d49c7bb67e6691fec8c2c994aa3d3d1751 `
  --denominator reports\ff6\xliff-core-obligation-denominator.yaml `
  --batch-id XLF-04-BATCH-005 `
  --adjudications reports\sal-verification\xliff-core-candidate-adjudications.yaml `
  --candidate-census reports\ff6\xliff-core-authority-candidate-census.yaml `
  --sal-store shared\sal-facts\xliff.yaml `
  --sal-manifest shared\sal-facts\evidence\xliff.yaml `
  --sal-receipt reports\sal-verification\xliff.json `
  --output reports\ff6\xliff-core-obligation-inventory.yaml `
  --check

.venv\Scripts\python.exe -m pytest -q `
  tests\tools\test_extract_sal_facts.py::test_batch_five_compiles_only_the_independently_adjudicated_obligation `
  tests\tools\test_extract_sal_facts.py::test_cli_batch_five_requires_validated_adjudications `
  tests\tools\test_extract_sal_facts.py::test_cli_batch_five_compiles_only_validated_adjudication_ids
```

Expected digests are recorded in `CHECKPOINT.yaml`. Any mismatch invalidates
the affected proof and must be investigated before mutation.

## 4. Execute Partial-002-B

Candidate `XLF-CAND-CORE-SCHEMATRON-00C4A041AF12C8A1` requires
`subFlowsStart` and `subFlowsEnd` to be paired. Use the exact candidate,
occurrence, member, source, denominator, SAL, decision, and tool digests.

1. Add the failing independent-decision test.
2. Determine the direct semantic owner from authority.
3. Reject incidental `segment`, `ignorable`, and generic validator mappings
   unless a separate authority occurrence proves them.
4. Add positive and rejection tests for paired and one-sided attributes.
5. Update the decision source and generated projection.
6. Compile an obligation only when the decision proves it.
7. Preserve all existing IDs and rows.
8. Run every affected regression and three clean generations.

## 5. Seal the next checkpoint

Explicitly stage reviewed files, pass coordination precommit, commit and push
GitLab main. Replay from that immutable commit. Append exactly one native
event, update controller/task projections, refresh the root handover, validate
semantic negative controls, then commit/push checkpoint metadata separately.

Never edit promotion state to reflect partial work.
