---
visibility: generated
generated_by: codex
sprint: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
---

# R90 Governed Skill Registry

R90 installs `.supervisor/skill-registry.yaml` as the machine-readable minimum registry for
repeatable product-factory work. The registry is advisory execution infrastructure subordinate to
`AGENTS.md` and `plans/master-plan.md`.

## Registered Skills

| Skill | Track | Purpose | Current Status |
|---|---|---|---|
| `/add-dotnet-api` | commercial .NET | Add one bounded .NET API with focused tests | fail closed until ledger validator exists |
| `/add-python-api` | Python FOSS | Add one bounded Python API with focused tests | fail closed until ledger validator exists |
| `/add-dogfood-export` | cross-product export | Add one FF-library-backed export with reload proof | fail closed until ledger validator exists |
| `/update-capability-matrix` | shared snapshot | Reconcile proven status into the POC matrix | active |

## Governance Boundary

The registry does not grant permission to edit `src/`. Product source work still requires an
explicit sprint prompt or generated execution handoff naming the selected skill and exact paths.
Gate, publication, commit, push, and commercial-readiness changes remain prohibited.

The first three skills intentionally stop with `BLOCKED_GOVERNED_LEDGER_NOT_INSTALLED` until the
R90 product-code ledger and validator are implemented. This preserves the R90 lane-ownership rule
that source remains read-only until registry, command docs, and ledger validation all exist.

