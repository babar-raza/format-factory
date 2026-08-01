---
artifact_id: FF6-HANDOVER-START-EVENT-39
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
`c421940ae70a3dc949318eee00cbfc5e3cf8b9a3`; the accepted XLIFF semantic
commit is `39b2e89fde0f7dd5e1acebc424f4d700dfe74765`. The final handover commit
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

The native authority is `FF6-EVENT-000039`, hash
`5f76c75ca4f7bc0845b22dccd38a195e962fb49b5f4161651737ab23d560cd36`,
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

Event 39 accepts only a bounded XLIFF contract result:

- candidate dispositions are `8/1,130`; `1,122` remain unverified;
- Core obligation coverage remains `30/105`; `75` remain missing;
- one existing target-language obligation was profile-corrected; no denominator
  row was added;
- XLIFF 2.0 requires exact language-tag equality;
- XLIFF 2.1 normative F4T Schematron permits an exact or more-specific target
  language tag;
- the normative machine-readable 2.1 rule controls over conflicting display
  prose, and that contradiction is recorded explicitly;
- the freshly compiled XLIFF contract remains `DRAFT` with 15 capabilities;
- XLF-04, product source, certification, promotion, release, and every gate
  remain incomplete.

## Exact next work

Execute `XLF-04-BATCH-005-PARTIAL-002-H` under
`TC-FF6-XLIFF-PROFILE-SURFACE-001`.

The exact candidate is
`XLF-CAND-CORE-SCHEMATRON-E891C4DEC555F165`, XLIFF 2.1
`schemas/xliff_core_2.1.sch` at
`schematron/rule[15]/report[1]`. It reports an `sc` in source content with
`isolated='yes'` when a referencing `ec` exists in the same unit.

Treat all eight generated mappings as unverified proposals:

- `SAL-XLIFF-CORE-AGENT-VALIDATOR-001`
- `SAL-XLIFF-CORE-HIERARCHY-IGNORABLE-001`
- `SAL-XLIFF-CORE-HIERARCHY-SEGMENT-001`
- `SAL-XLIFF-CORE-HIERARCHY-UNIT-CHILDREN-001`
- `SAL-XLIFF-CORE-INLINE-EC-001`
- `SAL-XLIFF-CORE-INLINE-SC-001`
- `SAL-XLIFF-CORE-REFERENCE-STARTREF-001`
- `SAL-XLIFF-CORE-SOURCE-REQUIRED-001`

Independently locate the exact authority and determine the direct semantic
owner. Expand the denominator only when authority proves a distinct obligation.
Explicitly reject trigger context, child surfaces, and downstream validation
behavior that do not directly own the rule. Never select a mapping to improve
coverage.

## Mandatory resume sequence

1. Read [AGENTS.md](../../../AGENTS.md), [Claude start](CLAUDE-START.md), and
   the active [taskcard](../../../taskcards/TC-FF6-XLIFF-PROFILE-SURFACE-001.md).
2. Fetch GitLab and prove `c421940a` and `39b2e89f` are ancestors of
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
local execution state. Event 39 demonstrates the intended remedy: one exact
authority occurrence, a discriminating RED test, explicit contradiction
handling, independent adjudication, deterministic descendants, immutable
replay, then a hash-chained event.

## Truth boundary

Event 39 proves one profile-specific target-language fact, one corrected
existing obligation, one candidate disposition, and fresh contract
recompilation. It does not complete XLF-04, implement a production library,
certify any format, satisfy Gate 10, or authorize publication.
