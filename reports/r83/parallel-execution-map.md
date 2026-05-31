# R83 Parallel Execution Map

## Phase 1 — Simultaneous Setup (NOW)
- [RUNNING] Full Python test suite (background)
- [RUNNING] Package artifact build (background)
- [RUNNING] FODS .NET tests (background)
- Wave 0 reports (foreground)

## Phase 2 — Technical Trains (parallel safe lanes)
- Trains B+C: Build review package infrastructure + fix metadata
- Trains D: Validator tests
- Trains F+I: FODS/FODT feature deepening
- Train K: .NET parity
- Trains M+N: Netpbm/SYLK/DIF
- Trains O+P: Gate 8/probe truth
- Trains Q+R: Examples/docs/publication readiness
- Train S: AI gap extraction
- Train T: Closeout automation

## Phase 3 — Installed Workflow (requires package artifacts)
- Trains E+H: FODS/FODT real sample workflows (after packages built)
- Train J: ZST dependency workflow

## Phase 4 — Authority Sync (before bundle build)
- Train U: state/master-plan/registry sync
- Generate all metadata files (all FINAL, no PENDING)

## Phase 5 — Evidence Build
- Commit all R83 work
- Build inner evidence bundle (Pass 1)
- Update final-verdict with Pass 1 SHA
- Commit
- Build Pass 2 inner evidence bundle
- Generate sidecar
- Build delivery package (build_delivery_package.py)
- Generate final artifact authority JSON
- Build supervisor review package (build_supervisor_review_package.py)
- Validate everything from extracted temp folder

## Phase 6 — Final IV
- Train V: Final adversarial IV
- Repair any fixable issues
- Final commit

## Phase 7 — Final Response
- Print: UPLOAD PRIMARY ARTIFACT: r83-supervisor-review-package.zip
