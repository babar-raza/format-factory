---
artifact_id: FF6-HANDOVER-EVENT-28-RUNBOOK
artifact_type: execution_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 28 exact resume runbook

## Phase A — revalidate

```powershell
git fetch origin
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor f98d220a0a3903b1107de90b2e39bf480ec4b19d origin/main
git merge-base --is-ancestor cde3b417 origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --self-test
python -m tools.supervisor.coordination --json status
```

Read the latest event and controller. If Event 29 or later exists, stop using
this selection projection and rebuild it from the newer journal head.

## Phase B — register and own

Register a new identity. Never reuse the prior Codex token.

For XLIFF, use `takeover --lease <id> --reason <specific reason>` only when
the live status is stale. Take over the logical scope and all exact files that
will be written. Recapture baselines before mutation.

For UBL, claim only the disjoint graph/test/report/receipt paths.

Create the execution manifest and mutation authorizations before writing.

## Phase C1 — XLIFF Batch 005

Verify the five recovery digests in `INFLIGHT-RECOVERY.yaml`. Inspect every
diff. Then run:

```powershell
.venv\Scripts\python.exe -m pytest -q tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m pytest -q tests\format_contract --deselect tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent
.venv\Scripts\python.exe -m pytest -q tests\production_program
.venv\Scripts\python.exe -m ruff check tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m mypy --strict tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py
npx --yes pyright@1.1.411 tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
.venv\Scripts\python.exe -m py_compile tools\spec\extract_sal_facts.py tools\spec\xliff_core_candidate_binding.py tests\tools\test_extract_sal_facts.py tests\tools\test_extract_sal_facts_candidate_binding.py
```

Run all relevant `--check` modes exposed by
`tools/spec/extract_sal_facts.py --help`. Rebuild changed canonical artifacts
three times in isolated temporary destinations. Prove byte equality. Audit all
five XLIFF authorities. Validate each skill transcript with zero warnings.

Do not weaken or delete:

- the existing 25 source-bound obligation rows;
- the 105 expected-ID denominator;
- candidate content/source/location binding;
- candidate-class semantics;
- fail-closed incomplete conditions;
- XLIFF 2.0/2.1 stable-profile isolation.

Commit only after determining which Batch 005 acceptance criteria are truly
met. A green focused suite alone is insufficient.

## Phase C2 — UBL fallback

Start from `f98d220a`. The next RED test must discriminate:

- offline import and include resolution;
- missing `schemaLocation` policy;
- remote import rejection;
- path escape;
- namespace/import mismatch;
- unresolved global reference;
- ambiguous duplicate global reference;
- deterministic closure independent of member discovery order.

Implement the minimal graph closure and rerun:

```powershell
.venv\Scripts\python.exe -m pytest -q tests\tools\test_ubl_schema_graph.py tests\tools\test_compile_ubl_schema_graph.py
.venv\Scripts\python.exe -m ruff check tools\spec\compile_ubl_schema_graph.py tools\spec\ubl_schema_graph.py tests\tools\test_ubl_schema_graph.py
.venv\Scripts\python.exe -m mypy --explicit-package-bases tools\spec\compile_ubl_schema_graph.py tools\spec\ubl_schema_graph.py --ignore-missing-imports
npx --yes pyright@1.1.411 tools\spec\compile_ubl_schema_graph.py tools\spec\ubl_schema_graph.py tests\tools\test_ubl_schema_graph.py
.venv\Scripts\python.exe -m py_compile tools\spec\compile_ubl_schema_graph.py tools\spec\ubl_schema_graph.py tests\tools\test_ubl_schema_graph.py
```

Run the pinned official package three times and compare canonical identity.
Keep the complete-graph flag false.

## Phase D — integration

1. Fetch GitLab and verify ancestry.
2. Stage only exact owned implementation/evidence files.
3. Run coordination precommit check.
4. Commit and push implementation.
5. Independently rerun evidence from the immutable commit.
6. Append exactly one native event.
7. Rebuild controller/task projections.
8. Commit and push the plan-control checkpoint.
9. Refresh this handover through the registered skill.
10. Validate packet hashes, links, YAML/JSON, journal, projections, ancestry,
    dirty-path classification, and negative controls.
11. Commit and push the handover.
12. Release only the current identity’s leases and complete the session.

## Required self-challenge

Before closure, answer the AGENTS.md fifteen questions. In addition:

1. Does every readiness statement bind exact executed evidence?
2. Did any uncommitted byte become a status authority?
3. Did the provider shift change task priority without a native event?
4. Did any synthetic fixture become the only interoperability oracle?
5. Did any known broad failure get hidden by an unnamed exclusion?
6. Can a clean checkout reproduce the checkpoint without provider-local state?

Any wrong answer keeps the task nonterminal.
