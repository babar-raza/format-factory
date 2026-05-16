# R19 Preflight: R18 Baseline Verification and Lane Ownership
Sprint: FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
Date: 2026-05-16
Gate: 0 — Preflight

## R18 Baseline Verification

### Git State
- Branch: main
- HEAD: 42052c2 feat(acquisition): complete R18 quarter-mile format acquisition sprint
- Working tree: clean (2 pre-existing untracked files excluded from sprint scope)
  - .claude/commands/export-plan-context.md (pre-existing, unrelated)
  - format-factory.zip (pre-existing, unrelated)

### R18 Commit Verification
- Commit 42052c2: CONFIRMED EXISTS
- 37 files changed, 4008 insertions(+), 40 deletions(-)
- Key artifacts confirmed present:
  - prototypes/by-format/zst/ (frame_header.py, zst_probe.py, validate_corpus.py, README.md)
  - acquisition-packs/{fodp,fodg,gnumeric,abw,ora}/
  - reports/verification/r18-zst-gate4-prototype-iv-20260516.md
  - tests/skills/test_zst_gate4_prototype.py
  - registry/format-registry.yaml (8 formats)

### R18 Bundle
- Path: .local/r18-bundle.zip
- Size: 2,507,979 bytes
- Exists: YES
- BUNDLE_VALIDATION: PASS (from R18 evidence record)

## R18 Stale Metadata Classification

### Classified Stale Items (documented in evidence hygiene report)
1. verdict.md HEAD reference: shows 8ba4f83 but actual commit was 42052c2
   - Root cause: verdict.md written before commit
   - Classification: PRE-COMMIT_ARTIFACT — historical, do not retroactively fix
2. r18-sprint-gate-status.md Gate 14 status: "IN_PROGRESS" after bundle completed
   - Root cause: status file written before bundle build
   - Classification: PRE-COMMIT_ARTIFACT — historical
3. Test count narratives: pasted summary said 1405/11, metadata said 38/38
   - Root cause: different test scopes (full suite vs ZST-specific)
   - Classification: SCOPE_AMBIGUITY — both correct for their scope
4. multiple taskcards with "human approval required" for agent-actionable decisions
   - Classification: POLICY_DRIFT — to be corrected in Gate 2

## Format State (Pre-R19)

| Format | Gates Passed | Current Status | R19 Target |
|--------|-------------|----------------|------------|
| FODS | 1-10 | Gate 11 in_progress | No change (separate track) |
| FODT | 1-10 | Gate 11 in_progress | No change (separate track) |
| ZST | 1-3, Gate 4 prototype_complete | Gate 4 needs delegated approval | Gates 4-7 |
| FODP | 1 | Gate 2 not_started | Gates 2-4 |
| FODG | 1 | Gate 2 not_started | Gates 2-4 |
| Gnumeric | 1 | Gate 2 not_started | Gates 2-3 |
| ABW | 1 | Gate 2 not_started | Gates 2-3 |
| ORA | Scored 6.8 (borderline) | pending human | DEFER decision |

## Lane Ownership Matrix (R19)

| Lane | Format | Current Gate | R19 Action |
|------|--------|-------------|------------|
| Compression | ZST | Gate 4 → 7 | Delegated approval + oracle + security |
| ODF-flat | FODP | Gate 2 → 4 | Fast-path Gate 2 + Gate 3 corpus + Gate 4 planning |
| ODF-flat | FODG | Gate 2 → 4 | Fast-path Gate 2 + Gate 3 corpus + Gate 4 planning |
| Spreadsheet | Gnumeric | Gate 2 → 3 | Spec retrieval + sample sources |
| Word processor | ABW | Gate 2 → 3 | Spec retrieval + sample sources |
| Image | ORA | Deferred | Delegated DEFER decision |
| Office | FODS | Gate 11 | Commercial train plan only |
| Office | FODT | Gate 11 | Commercial train plan only |

## Hard Invariants Confirmed Pre-R19

- commercial_product_ready: false (all 8 formats)
- FODS Gate 11: NOT APPROVED
- FODT Gate 11: NOT APPROVED
- No src/net mutations authorized
- No git push authorized
- No PR creation authorized
- ZST implementation_authorized: false (will remain false until Gate 9+)

GATE_0_PREFLIGHT: PASS
