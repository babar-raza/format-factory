---
visibility: generated
generated_by: codex
sprint: FORMAT-FACTORY-R90-MAINSTREAM-POC-PRODUCT-ACCELERATION-GOVERNED-SKILLS-SUPERVISOR-REPAIR-MEGA-TRAIN-001
---

# R90 Governed Skills Minimum Viable Set

## Scope Completed

The R90 minimum command documentation set now covers the four recurring product-factory operations:

| Operation | Command | Required Proof |
|---|---|---|
| Extend a commercial .NET product | `/add-dotnet-api` | ledger validation plus focused .NET tests |
| Extend a Python FOSS product | `/add-python-api` | ledger validation plus focused Python tests |
| Add a dogfood export | `/add-dogfood-export` | FF target writer, dependency scan, reload proof, focused tests |
| Reconcile the POC snapshot | `/update-capability-matrix` | local evidence, YAML parse, entry-scoped diff |

Each command requires exact writable paths, explicit handoff authorization, bounded claims, and
no commit or push. Product commands also prohibit gate, publication, and commercial-readiness edits.

## Remaining Blocker

The minimum docs are installed, but product source remains read-only. R90 still needs the
product-code ledger, ledger validator, and pre-governance R89 backfill described in the R90 plan.
Until those exist and pass, the three source-mutating skills fail closed.

## Non-Goals

This lane did not edit `src/`, shared policies, `product-capability-matrix/poc-targets.yaml`, existing
reports, supervisor tools, tests, gate state, release state, or publication state.

