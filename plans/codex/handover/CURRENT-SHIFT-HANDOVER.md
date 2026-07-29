---
artifact_id: FF6-CURRENT-SHIFT-HANDOVER-EVENT-28
artifact_type: provider_shift_handover
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Codex to Claude shift handover — Event 28

## Mission

Build six independently publishable, production-grade Python libraries for
IPYNB, OpenRaster, NRRD, XLIFF 2.0/2.1, SafeTensors, and UBL 2.3. Each library
must provide complete format-specific developer capabilities, professional
package architecture, secure parsing/writing, typing, documentation,
interoperability, installed-wheel proof, reproducible artifacts, SBOM,
provenance, signatures, repository extraction, and technical certification.

The mission is autonomous and continuous. Provider changes do not change the
goal, task ordering, evidence rules, or completion criteria.

## Clean authority boundary

The last two GitLab commits created by this shift are:

1. `f98d220a0a3903b1107de90b2e39bf480ec4b19d`
   — bounded UBL root/type graph implementation and TDD evidence.
2. `cde3b417`
   — Event 28, controller projection, UBL taskcard microstate, and
   plan-control receipt.

The packet commit containing this document must descend from both.

Native state:

```text
CONTRACT
Event 28
canonical task: TC-FF6-XLIFF-PROFILE-SURFACE-001
canonical microstep: XLF-04-BATCH-005
parallel task: TC-FF6-UBL-TYPING-001
parallel microstep complete: UBL-03-PARTIAL-001
parallel next microstep: UBL-03-PARTIAL-002
certified products: 0/6
```

## Work completed this shift

The first UBL-03 graph primitive was built under `test-driven-development` and
`sal-pipeline-heal`, with independent plan-control serialization:

- RED 1: graph entrypoint absent.
- GREEN 1: deterministic root-to-declared-type graph.
- RED 2: security pre-scan falsely rejected a DOCTYPE string inside a comment.
- GREEN 2: comments are excluded from the declaration pre-scan while active
  DOCTYPE and ENTITY declarations remain rejected.

Observed official-package result:

```text
schemas: 106
document roots: 91
reachable root/type nodes: 182
type-reference edges: 91
graph SHA-256: 7b754187690ce1bb04db62657cfb552653cb381a1bdd745a56856e58215af029
three equivalent runs: identical
focused tests: 14 passed
Ruff: pass
Mypy: pass
Pyright 1.1.411: zero diagnostics
py_compile: pass
```

The SAL transcript is intentionally `FAIL` at the whole-task level because no
complete graph output exists. The TDD transcript is `PASS` for the bounded
behavior. This distinction is deliberate.

## Work not completed

UBL-03 remains open. Do not change the taskcard to `PASS` until every graph
component and edge listed in the taskcard is present and the checked-in graph
artifact is reproducible.

XLIFF Batch 005 remains uncommitted. The stale working set now passes the two
focused files (`62 passed`), but broad verification, artifact check modes,
three-run replay, authority audit, receipts, exact-path commit scope, and
native event serialization have not been established by this shift.

No product source, package certification, promotion, release, or gate state
advanced.

## Preserved dirty paths

| Path | LF SHA-256 | Bytes | Lines |
|---|---|---:|---:|
| `reports/ff6/xliff-core-authority-candidate-census.yaml` | `2b2557a09a0a7c95ecbcecf72ac6c8bedb7addcb221787b9eab254f687bf8207` | 2,629,952 | 45,847 |
| `tests/tools/test_extract_sal_facts.py` | `86dcfd486fe76552e35c0efd24c0c5036d0f11bc22b08507cb8c7e0e94274e62` | 60,349 | 1,664 |
| `tools/spec/extract_sal_facts.py` | `8f98868393719aa249a73acdc6597536b54d674e56fbfb80539f3490e4fdb82d` | 161,850 | 4,072 |
| `tests/tools/test_extract_sal_facts_candidate_binding.py` | `34a9cddb5986548c0a3602a90ff914eab4a9940bbebe03141936cc977a8c7db6` | 14,247 | 452 |
| `tools/spec/xliff_core_candidate_binding.py` | `042c670acefff8d0a6932ea3df7f1582f887f756148dd0bdfc356f69ca56f8b7` | 14,443 | 387 |

The table records the current filesystem observation. The packet does not
adopt those bytes as canonical proof. If any digest changes before Claude
takes ownership, preserve the changed version and investigate; do not force it
back to this table.

## Claude’s first decision

Claude must not start by editing.

1. Fetch GitLab and validate the packet.
2. Read Event 28, controller, XLIFF taskcard, UBL taskcard, and coordination
   status.
3. Register a fresh Claude identity.
4. If the XLIFF leases remain stale, use governed takeover on the logical
   scope and all five current paths. Recapture baselines.
5. If the leases are active, leave XLIFF untouched and claim the UBL graph
   paths for `UBL-03-PARTIAL-002`.
6. If a newer commit or event exists, independently verify it and rebuild the
   projection before selecting work.

## XLIFF takeover path

After a successful governed takeover:

1. Verify all five LF digests and inspect diffs against `HEAD`.
2. Rerun both focused files. The captured result is `62 passed`; any other
   result is drift requiring diagnosis.
3. Inspect whether Batch 005 receipts and local transcripts exist. Do not
   synthesize a passing receipt from test output.
4. Run the full validation matrix in `event-28/RUNBOOK.md`.
5. Run every supported `extract_sal_facts.py --check` mode for changed
   artifacts.
6. Generate canonical outputs three times in isolated temporary destinations
   and compare bytes.
7. Verify all XLIFF authorities remain `MATCH`.
8. Determine the honest state:
   - if Batch 005 acceptance is complete, commit the exact implementation
     paths;
   - if only a bounded subset is complete, commit and journal it as partial;
   - if evidence fails, repair through another RED-GREEN cycle.
9. Push GitLab main, append one native event, rebuild projections, refresh this
   handover, and release leases.

## UBL fallback path

Continue from commit `f98d220a`, not from scratch.

Next exact TDD cycle:

```text
UBL-03-PARTIAL-002
behavior: exact offline import/include closure and unique global-reference resolution
RED: synthetic package proves missing/unresolved/remote/ambiguous closure fails
GREEN: add minimal closure graph while preserving current node/edge identities
VERIFY: focused suite + real package + three equivalent runs + static checks
```

Then add one RED-GREEN cycle for each remaining UBL-03 behavior family. Keep
`reachable_schema_graph_complete: false` and do not emit a complete canonical
report until all exit criteria pass.

## Checkpoint handback requirement

Claude must end its shift with:

- bounded implementation commit pushed to GitLab main;
- exactly one new native event for the verified boundary;
- matching controller/taskcard/task-index projection;
- receipts validating with zero warnings;
- refreshed provider-neutral packet and manifest;
- packet self-test passing;
- exact dirty-path classification;
- its own leases released and session completed.

If work ends in RED or a failed broad gate, commit nothing that claims
completion. Preserve a content-addressed recovery record and leave the last
clean Event 28 boundary available.
