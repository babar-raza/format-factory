---
artifact_id: FF6-HANDOVER-START-EVENT-40
artifact_type: provider_neutral_handover_entry
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# FF6 production program: start here

This is the single entry point for every Claude or Codex shift:

```text
C:\Users\prora\OneDrive\Documents\GitHub\format-factory\plans\codex\handover\START-HERE.md
```

The canonical forge is GitLab, remote `origin`, branch `main`. Do not use
GitHub, create another branch, reuse another agent's identity, or depend on
ignored local state. This packet is derived from control checkpoint
`de569544eebc1fff011901e61d3574dcc48e5e08`; the accepted XLIFF semantic
commit is `d95af5aeb248907b4d23457ecd288723fc9c2050`. The final handover commit
must descend from the control checkpoint but cannot self-reference its own hash.

## Mission

Build six independently publishable, production-grade Python libraries for:

- Jupyter Notebook;
- OpenRaster;
- NRRD;
- XLIFF;
- SafeTensors; and
- OASIS UBL.

The goal is not six minimally functional codecs. Each package must expose the
full stable format-specific capability surface developers reasonably need:
professional typed APIs and package segregation, safe streaming parsers and
writers, preservation and diagnostics, deterministic serialization,
interoperability with independent implementations, Python 3.11–3.14
installed-wheel matrices, security and resource limits, documentation,
reproducible builds, SBOMs, provenance, signatures, and release evidence.

## Honest current state

The native authority is `FF6-EVENT-000040`, hash
`c9c7167d447fbe0945c7a65c288f3cece78c64090e09c1ce2d674fdbf9bf2d63`,
in controller state `CONTRACT`.

- All six products remain `UNASSESSED`; technical certification is `0/6`.
- OpenRaster product source is absent.
- IPYNB, NRRD, XLIFF, SafeTensors, and UBL source trees are partial,
  profile-limited, and pre-production.
- All six ProductContracts remain `DRAFT`.
- XLF-04 is the first unmet XLIFF task step.
- UBL-03 is independently resumable but incomplete.
- No contract row, focused test, generated type, source-file presence, or
  handover statement is product certification.

Event 40 accepts only a bounded XLIFF contract result:

- candidate dispositions are `9/1,130`; `1,121` remain unverified;
- Core obligation coverage is `31/105`; `74` remain missing;
- one new `INLINE-ISOLATION` obligation and one decision were added while all
  30 predecessor obligations and 8 predecessor decisions were preserved;
- exact XLIFF 2.0 and 2.1 prose states the full `sc` isolated biconditional;
- XLIFF 2.1 F5S Schematron supplies source-side executable rejection evidence;
- generated validator, hierarchy, element, reference, and cardinality mappings
  were rejected as direct owners;
- the freshly compiled XLIFF contract remains `DRAFT` with 15 capabilities;
- XLF-04, product source, certification, promotion, release, and every gate
  remain incomplete.

## Exact next work

Execute `XLF-04-BATCH-005-PARTIAL-002-I` under
`TC-FF6-XLIFF-PROFILE-SURFACE-001`.

The exact candidate is
`XLF-CAND-CORE-SCHEMATRON-60B596A00F7FA06A`, XLIFF 2.1
`schemas/xliff_core_2.1.sch` at
`schematron/rule[16]/report[1]`. It reports an `sc` in target content with
`isolated='yes'` when a referencing `ec` exists in the same unit.

Treat all eight generated mappings as unverified proposals:

- `SAL-XLIFF-CORE-AGENT-VALIDATOR-001`
- `SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001`
- `SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001`
- `SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001`
- `SAL-XLIFF-CORE-INLINE-EC-001`
- `SAL-XLIFF-CORE-INLINE-SC-001`
- `SAL-XLIFF-CORE-REFERENCE-STARTREF-001`
- `SAL-XLIFF-CORE-SOURCE-TARGET-OPTIONAL-001`

Independently locate the exact authority and determine whether this target-side
report supplies reciprocal proof for the existing inline-isolation obligation.
Do not add a duplicate obligation. Explicitly reject trigger context, child
surfaces, reference mechanisms, and downstream validation behavior that do not
directly own the rule. Never select a mapping to improve coverage.

## Mandatory resume sequence

1. Read [AGENTS.md](../../../AGENTS.md), [Claude start](CLAUDE-START.md), and
   the active [taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md).
2. Fetch GitLab and prove `de569544` and `d95af5ae` are ancestors of
   `origin/main`.
3. Run the committed packet validator before claiming work.
4. Query the off-repo coordination plane and preserve every foreign or
   unexplained change.
5. Register a fresh provider identity. Never reuse identities, tokens, leases,
   manifests, or authorizations recorded by a prior shift.
6. Resolve and invoke the registered production skills, claim exact paths, run
   preflight before every write, and record every write.
7. Execute only [NEXT-MICROSTEP.yaml](NEXT-MICROSTEP.yaml), starting with a
   genuine failing test.
8. Commit one bounded semantic slice to GitLab `main`, replay it from an
   immutable checkout with the full five-record XLIFF authority closure, then
   append the next native event.
9. Refresh this packet from the new event, push it to GitLab `main`, validate
   the committed checkpoint, and release only the current shift's leases.

A blocked path does not stop safe read-only work or a deterministic disjoint
task. It never authorizes takeover of a live lease, workspace cleanup, or a
fabricated progress label.

## Packet map

Operational state, in order:

1. [Exact Claude commands](CLAUDE-START.md)
2. [Active work checkpoint](ACTIVE-WORK-CHECKPOINT.md)
3. [Machine-readable state](CURRENT-MACHINE-STATE.yaml)
4. [Checkpoint contract](checkpoint.yaml)
5. [Exact next microstep](NEXT-MICROSTEP.yaml)
6. [Outgoing shift evidence](CURRENT-SHIFT-HANDOVER.md)
7. [Recovery and reconstruction](INFLIGHT-RECOVERY.yaml)
8. [Checkout/replay constraints](CLEAN-REPLAY-REPAIR.md)
9. [Symptoms, root causes, structural weaknesses, and durable design](CURRENT-STATE-AND-ROOT-CAUSES.md)
10. [Packet manifest](manifest.yaml)

Durable execution controls:

- [Provider shift contract](PROVIDER-SHIFT-CONTRACT.md)
- [Shift and resume protocol](SHIFT-AND-RESUME-PROTOCOL.md)
- [Execution runbook](EXECUTION-RUNBOOK.md)
- [State machine and taskcards](STATE-MACHINE-AND-TASKCARD-PROTOCOL.md)
- [Validation and release](VALIDATION-AND-RELEASE.md)
- [Parallel UBL checkpoint](PARALLEL-UBL-CHECKPOINT.yaml)

## What must be preserved and what must be redesigned

Preserve the content-addressed authorities, native event history, exact
negative controls, immutable replay discipline, working product behavior,
single-main GitLab policy, and off-repo lease coordination.

Continue redesigning the partial-authority system: status must be computed from
live proof; every mandatory obligation needs exact ownership and executed
positive/negative evidence; all source, test, fixture, authority, tool, lock,
environment, and package inputs must invalidate descendants; installed wheels
must be tested outside the source tree; and no provider may validate its own
claim without independent executable proof.

The main consistency failures are stale projections, incomplete dependency
closure, mutable or missing authority inputs in detached replay, proposal-to-
fact leakage, broad capability buckets hiding missing semantics, and provider-
local execution state. Event 40 demonstrates the intended remedy: one exact
authority occurrence, a discriminating RED test, explicit contradiction
handling, independent adjudication, deterministic descendants, immutable
replay, then a hash-chained event.

## Truth boundary

Event 40 proves one stable inline-isolation fact, one new direct obligation,
one candidate disposition, and fresh contract
recompilation. It does not complete XLF-04, implement a production library,
certify any format, satisfy Gate 10, or authorize publication.
