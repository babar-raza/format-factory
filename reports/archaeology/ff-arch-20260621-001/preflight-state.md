# Preflight State — ff-arch-20260621-001
# Generated: 2026-06-21

## Git State
- Branch: main
- HEAD: 23d1333fdb51b8f07d517a29af311d46ffdd3eb9
- Recent commits (last 5):
  1. 23d1333f test(fodt): add compat bootstrap import/attribute test (TC-HARD-005)
  2. 20a823b9 chore(registry): add known-failures ledger and FODT pilot audit
  3. b93889cb test(fodt): add spec registry, QName stub, compat e2e, ingest test suites
  4. fd0395a7 feat(fodt): add FODT QName registry, Python spec stubs, .NET Spec stubs
  5. 1c8e4a4f feat(spec-tooling): add FODT pilot audit generator, spec registry validators

## Dirty / Modified Files
- ~90+ modified tracked files across: .supervisor/, plans/, reports/, taskcards/, src/
- ~200+ untracked files (test files, report outputs, evidence directories)

## Plans Found
- plans/master-plan.md
- plans/strategic/spec-to-feature-radical-correction-plan.md
- plans/strategic/snoopy-juggling-seal.md
- plans/strategic/continuation-isolation-plan.md
- plans/healing/product-code-healing-plan.md
- plans/strategic/capability-fact-to-feature-production-plan.md

## Taskcards Found (count by prefix)
- TC-SRC-REVIEW-*: 8 files
- FODS-COMMERCIAL-*: 2 files
- FODT-COMMERCIAL-*: 1 file
- NEXT-COMMERCIAL-*: 1 file
- TC-0002 through TC-0020: infrastructure taskcards
- DEEPEN-*, DRIFT-*, AI-*: archived/planning taskcards (100+)

## Evidence Directories
- .local/evidences/: 40+ sprint evidence bundles
- .local/qname-output/: FODS, FODT, FODG, FODP qname maps
- .local/spec-cache/: 15 formats with cached spec facts

## Key Governance Docs
- registry/format-registry.yaml — format registry (authoritative)
- registry/gate11-criteria.yaml — Gate 11 criteria
- registry/odf-ontology/qname-to-code-map.yaml — QName mapping (authoritative)
- shared/qname-registry/fodt.yaml — FODT QName registry
- schemas/neutral-model/fods/model.yaml — FODS neutral model schema
- schemas/neutral-model/fodt/model.yaml — FODT neutral model schema

## Source Layout
```
src/
  net/           .NET products (10 formats)
  python/        Python products (21 formats + _shared)
  src.zip        Source archive (artifact)
  format_factory_dev.egg-info/  Build artifact
```

## Dirty File Classification

| Classification | Examples | Count (approx) |
|---|---|---|
| current sprint artifact | reports/supervisor/*, .supervisor/state/* | 30+ |
| generated evidence | reports/skills-r*/*, reports/supervisor/evidence-review.* | 50+ |
| product source | src/python/fods/*, src/python/fodt/* | 5+ |
| machinery source | src/python/toml/*, src/python/zst/*, src/python/xcf/* | 3+ |
| risky/conflicting | src/python/fods/fods/ (triple nesting) | 1 structural |
| unknown | reports/gv-triage/, reports/sv-sampling/ | 5+ |

## Supervisor Mode
- MODE 4 (MCP ACTIVE)
- Session-resume: last sprint tc-harden-003-test, ACCEPTED_WITH_REWORK
- Autonomous continue: False (requires reset or plan completion)

## No Plan File Loaded
- No per-chat plan is active in this conversation
- Session-resume file noted prior sprint; user's request is an archaeology investigation (unrelated)
- CCI-MVP rule: treat session-resume as background context only
