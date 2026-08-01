---
artifact_id: FF6-CLAUDE-START-41BFAEF
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Claude exact start and stop sequence

## 1. Reconstruct authority without changing state

```powershell
Set-Location 'C:\Users\prora\OneDrive\Documents\GitHub\format-factory'
Get-Content -LiteralPath AGENTS.md
git fetch origin main --prune
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 6fca743ca55a8c221e63954b4c8a371b73e2246d origin/main
.venv\Scripts\python.exe plans\codex\handover\validate_committed_checkpoint.py --ref origin/main
git status --short --branch
.venv\Scripts\python.exe -m tools.supervisor.coordination --json status
```

At this packet, the expected native head is `FF6-EVENT-000037` /
`09a3ae3d4521afc5c6c6c937d667c2246a8ad1fbae6ffb8af04a5b32e0e2b2b6`.
If GitLab has advanced, validate the newer chain and regenerate this packet;
do not reset or force-push. If the shared tree is clean, also run:

```powershell
.venv\Scripts\python.exe plans\codex\handover\validate_handover.py --require-clean --self-test
```

If it is dirty, attribute every path through coordination. Never use restore,
stash, reset, clean, checkout, or broad staging on unexplained state.

## 2. Read the binding execution context

Read, in order:

1. `plans/master-plan.md`
2. `plans/strategic/ff6/product-goal.yaml`
3. `plans/strategic/ff6/controller-state.yaml`
4. the complete `plans/strategic/ff6/events.jsonl`
5. `taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md`
6. `plans/codex/handover/NEXT-MICROSTEP.yaml`
7. `.supervisor/knowledge/registry.yaml` and every applicable verified contract
8. every selected `.claude/commands/<skill>.md` contract
9. `docs/governance/codex-adapter.md` if the next provider is Codex

Do not reimplement the accepted reciprocal skeleton change or its checkout
repair. They are immutable history at `2dcb161e`, repair commit
`809cc18cc6e62ae19f6ea5c11ed41ab9a7ec5956`, and Event 36. Do not
reimplement the accepted unit-cardinality change at
`1b758c2e05856552169de098d8719a82f425a1c2` / Event 37.

## 3. Establish a fresh shift identity

```powershell
.venv\Scripts\python.exe -m tools.supervisor.coordination register `
  --provider claude-code --mode interactive `
  --task TC-FF6-XLIFF-PROFILE-SURFACE-001
```

Use only the returned identity/token for this shift. Claim the logical
microstep and exact files, preflight every write, record every write, heartbeat
during long validation, and never release another provider's lease.

## 4. Execute the exact next microstep

Run `XLF-04-BATCH-005-PARTIAL-002-F` for
`XLF-CAND-CORE-SCHEMATRON-B0961B8D3678CA73`.

Before mutation, reconfirm:

- controller Event 37 and GitLab checkpoint `6fca743c`;
- 6 verified / 1,124 open candidate dispositions;
- 29 resolved / 76 missing of 105 obligations;
- candidate content digest `fc6bfe29...`, requirement digest `4d6ff61b...`,
  and occurrence digest `0102e918...`;
- exact authority occurrence `schematron/rule[13]/report[1]` in the pinned
  XLIFF 2.1 Core Schematron member;
- checkout identity and all predecessor proof hashes.

The prior shift independently inspected the authority and reached this
non-promoting conclusion, which Claude must reproduce before adopting it:

- accept only `SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001` as the direct
  semantic owner;
- reject `AGENT-VALIDATOR` as a downstream capability;
- reject `HIERARCHY-IGNORABLE` and `HIERARCHY-SEGMENT` as trigger context;
- reject `SOURCE-REQUIRED` because an existing source only triggers the rule
  and proves no presence/cardinality requirement;
- additionally reject the nearby unproposed
  `SAL-XLIFF-CORE-LANGUAGE-SOURCE-001`, because omitted-value inheritance is a
  distinct obligation from explicit language compatibility.

The prior RED run selected deterministic proposed fact ID
`SAL-XLIFF-39A807E74F92A266` and failed exactly two focused tests:

```powershell
.venv\Scripts\python.exe -m pytest -q `
  tests/tools/test_xliff_core_candidate_adjudication.py::test_source_language_adjudicates_only_document_compatibility_owner `
  tests/tools/test_extract_sal_facts.py::test_batch_five_source_language_seed_requires_exact_candidate_proof
```

Expected RED causes are: the canonical decision list is empty, and the
extractor does not yet fail closed when the exact candidate proof is absent.
The tracked RED edits were quarantined and reverted before transfer, so Claude
must recreate them with `test-driven-development` under fresh leases.

Do not seed the full legacy queue. The registered seeder currently fails with
`new SAL candidate has no acquired source_ids` because an unrelated historical
candidate no longer matches the canonical store exactly and lacks provenance.
Repair this structurally through `ingest-spec-sal`: add a deterministic
`--candidate-id` selector, require exactly one matching queue row, retain all
authority validation, reject missing/duplicate IDs, and prove that unrelated
rows are neither validated nor written. Add
`candidate_id: XLF-SAL-CAND-CORE-SOURCE-LANGUAGE-COMPATIBILITY-001` to the new
queue row and invoke only that row. Never weaken the source-ID check or patch
legacy rows merely to make this run pass.

Execution order is RED test, independent authority adjudication, SAL/proof
repair if required, deterministic artifact compilation, complete focused and
regression validation, immutable checkout replay, then native controller
projection. Generated owner mappings are proposals only. If no existing
denominator row is the direct owner, record and schedule the gap; never force a
mapping to make coverage rise.

## 5. Required proof before the next event

- positive, rejection, tamper, and predecessor-preservation tests;
- exact candidate/occurrence/authority/SAL/decision digest closure;
- all 29 accepted predecessor rows semantically equal;
- all 1,130 candidate identities unchanged;
- three byte-identical clean generations;
- Ruff, strict Mypy, Pyright when available, and bytecode compilation on
  touched code; unavailability must be recorded, never reported as a pass;
- SAL verification and 5/5 XLIFF authority matches;
- affected tool tests plus format-contract and production-program regressions;
- zero-warning skill transcripts;
- detached checkout replay from the candidate commit;
- native event chain and controller/task/handover agreement.

## 6. Close the shift safely

1. Stage only reviewed leased files.
2. Commit to `main`; push only `origin main`; prove `HEAD == origin/main`.
3. Replay the exact immutable commit with digest-pinned authority inputs.
4. Refresh every operational handover file and LF-normalized manifest from the
   new native journal head.
5. Run both handover validators and their negative controls.
6. Record writes, release only this shift's leases, and complete the identity.

Never report a production-ready library unless the full product certification
graph—not a focused contract microstep—proves it. Current status is 0/6.
