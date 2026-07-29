---
artifact_id: FF6-PROVIDER-NEUTRAL-RUNBOOK-EVENT-25
artifact_type: autonomous_resume_runbook
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-29
---

# Autonomous Resume Runbook — Event 25

## 1. Resume preflight

Run from the repository root:

```powershell
git fetch origin main --prune
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 220ee7f5b9d39c3684cff6af6331b56a03ae9e75 origin/main
git merge-base --is-ancestor 2522752776f64ab800a2a21c8fa46c1f2a4e361c origin/main
python tools/evidence/check_current_state_consistency.py
python -m tools.supervisor.coordination --json status
```

Do not reset, stash, restore, clean, or discard a dirty shared tree. Attribute
every path and work only on disjoint, leased scope.

## 2. Validate the native FF6 journal

```powershell
@'
import hashlib
import json
import pathlib
import yaml

events_path = pathlib.Path("plans/strategic/ff6/events.jsonl")
controller_path = pathlib.Path("plans/strategic/ff6/controller-state.yaml")
events = [
    json.loads(line)
    for line in events_path.read_text(encoding="utf-8").splitlines()
    if line.strip()
]
previous = None
for sequence, event in enumerate(events, 1):
    assert event["schema"] == "ff6/controller-event@1"
    assert event["sequence"] == sequence
    assert event["event_id"] == f"FF6-EVENT-{sequence:06d}"
    assert event.get("previous_event_hash") == previous
    claimed = event["event_hash"]
    body = dict(event)
    del body["event_hash"]
    observed = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert observed == claimed, event["event_id"]
    previous = claimed

controller = yaml.safe_load(controller_path.read_text(encoding="utf-8"))
assert len(events) == 25
assert controller["transition_sequence"] == 25
assert controller["last_verified_event"]["event_hash"] == previous
assert previous == "237f7759e2286cfc08c547c53a0b47d44e1c77307329ec0215c5326e3f811e48"
print(f"PASS events={len(events)} head={previous}")
'@ | .venv\Scripts\python.exe -
```

Do not use generic `tools.plan_control doctor` as the FF6 journal validator.
It expects `previous_hash`; FF6 uses `previous_event_hash`. The mismatch is the
known `FF6-GAP-011`, not proof that the native chain is corrupt.

## 3. Revalidate batch 003

Required:

```powershell
.venv\Scripts\python.exe -m pytest -q tests/tools/test_extract_sal_facts.py
.venv\Scripts\python.exe -m pytest -q tests/format_contract --deselect tests/format_contract/test_consumption_chain.py::test_full_slice_second_run_is_idempotent
.venv\Scripts\python.exe -m pytest -q tests/production_program
.venv\Scripts\python.exe -m ruff check tools/spec/extract_sal_facts.py tests/tools/test_extract_sal_facts.py
.venv\Scripts\python.exe -m mypy --strict --explicit-package-bases --ignore-missing-imports tools/spec/extract_sal_facts.py tests/tools/test_extract_sal_facts.py
npx --yes pyright@1.1.411 tools/spec/extract_sal_facts.py tests/tools/test_extract_sal_facts.py
.venv\Scripts\python.exe -m py_compile tools/spec/extract_sal_facts.py tests/tools/test_extract_sal_facts.py
.venv\Scripts\python.exe -m tools.format_contract.authority_materializer audit --format xliff --contracts
```

Require:

- 27 focused tests;
- 94 format-contract tests plus the one explicit baseline-known deselection;
- 69 production-program tests;
- static checks pass;
- five XLIFF authorities match;
- source/test/report hashes equal `CHECKPOINT.yaml`;
- both batch-003 transcripts validate with zero warnings;
- matrix, denominator, and inventory check mode pass.

If a recorded input changed, invalidate only its descendants and repair before
continuing. Do not select whichever evidence makes the test pass.

## 4. Acquire ownership

Claude follows ambient hooks and explicit broad claims. Codex follows
`docs/governance/codex-adapter.md`.

The invariant is:

```text
register
→ claim exact paths
→ create skill execution manifest
→ mutation guard
→ preflight before each write
→ execute registered skill
→ record-write after each write
→ validate receipt
→ precommit-check
→ exact-path commit
→ remote verification
→ release own leases
→ complete own identity
```

Never reuse an outgoing provider token or release another provider's lease.

## 5. Execute XLF-04-BATCH-004

Use TDD plus the registered authority/SAL ingestion pipeline.

### RED contract

Add tests that fail because no complete candidate census and reconciliation
exists. Tests must require:

- deterministic direct/leaf prose candidate extraction;
- no ancestor/descendant double counting;
- Core XSD element/type/attribute/cardinality/order candidates;
- Core Schematron/assertion candidates;
- explicit 2.0-only, 2.1-only, common, changed, and removed rule identity;
- exactly one disposition per candidate;
- mappings to one or more stable expected obligation IDs;
- explicit reason for every non-obligation disposition;
- rejection of unmapped, duplicate, ambiguous, stale-digest, foreign-profile,
  or preview-leaking candidates;
- deterministic, checkable tracked outputs.

### GREEN boundary

Implement only enough generic, maintainable machinery to compile and validate
the candidate census and mapping. Do not hardcode success counts into tests.
Keep source extraction, candidate normalization, reconciliation, and artifact
serialization separate.

Suggested artifacts:

- `reports/ff6/xliff-core-authority-census.yaml`;
- `reports/ff6/xliff-core-authority-reconciliation.yaml`.

The census must include authority source ID/digest, package member, exact
location, profile applicability, candidate class, normalized requirement, and
candidate digest.

The reconciliation must include candidate ID, expected obligation IDs or
non-obligation disposition, rationale, and validation status.

### Completion boundary

Batch 004 may pass while XLF-04 remains open. Do not close XLF-04 unless:

- the authority surface denominator is proven exhaustive;
- zero candidates are unmapped or multiply dispositioned;
- zero expected IDs are unresolved;
- every obligation is canonically SAL-verified;
- all referential and profile constraints pass.

## 6. Regression tiers

For the bounded batch:

1. new focused RED/GREEN tests;
2. full extractor tests;
3. format-contract and production-program regressions;
4. Ruff, strict Mypy, Pyright 1.1.411, bytecode compile;
5. authority audit and artifact check mode;
6. three isolated byte-identical generations;
7. malformed/duplicate/stale/profile-leak negative controls;
8. zero-warning skill transcripts.

At XLF-08, additionally require strict six-format compilation, canonical SAL
verification, all module denominators, three clean full replays, and exact
ownership.

## 7. Checkpoint transaction

At a clean GREEN boundary:

1. commit only implementation/test/report/receipt files;
2. fetch GitLab and verify no overlapping remote movement;
3. push the immutable implementation commit to GitLab `main`;
4. append exactly one native FF6 event referencing that commit;
5. rebuild controller, taskcard, current-gap, and packet projections;
6. validate chain, projections, links, hashes, task registration, and ancestry;
7. commit only control/packet/receipt files;
8. push to GitLab `main`;
9. fetch and prove remote equals the checkpoint commit;
10. complete the outgoing coordination identity.

Never leave required state only in chat or an unpushed commit.

## 8. Remaining mission route

After XLF-04:

- XLF-05: all eight official XLIFF 2.1 modules as separate capability families;
- XLF-06: SAL/family/product-requirement/capability ownership repair;
- XLF-07: exact stable and preview profile compilation;
- XLF-08: full XLIFF contract verification and checkpoint;
- UBL typing prerequisite task;
- program architecture and taskcard generation;
- per-format implementation, independent verification, installed-wheel
  certification, extraction, reproducible packages, SBOM/provenance/signature,
  and release preparation.

Each library promotes independently, but the mission is not complete until all
six are technically certified. Publication can remain externally blocked
without blocking technical completion.

## 9. Known limits and risks

- OpenRaster has an early-draft authority and must use a bounded
  interoperability certification claim.
- XLIFF category presence is not an obligation denominator.
- UBL schema typing is a large generated-family problem; generic roots are not
  acceptable substitutes.
- Legacy product counts and tests can hide shallow semantics.
- Synthetic fixtures cannot be the only interoperability proof.
- Reproducible generation does not prove normative completeness.
- Dead-process long-TTL leases currently delay governed takeover; preserve
  bytes and use disjoint work until eligibility, then repair the coordination
  design as a separate governed machinery task.

## 10. Stop conditions

Do not ask the user whether to continue.

Stop only an affected write when:

- another live owner holds the path;
- preflight detects drift;
- the event chain is invalid;
- required authority bytes fail digest verification;
- a true external legal/business/publication gate is reached.

Continue all other safe, selected work. Record technical blockers after three
materially different failed repair attempts; never convert difficulty,
uncertainty, or a token boundary into a false external blocker.
