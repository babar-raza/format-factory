# R112 Reconciliation

## Sprint: mainstream-r112
## Reconciliation Date: 2026-06-03

## Honest Classification
R112 was an **evidence repair + single-product progress** sprint, not a broad product depth sprint.

### What R112 Actually Delivered
1. **R111 reconciliation** - 18 items verified (DONE)
2. **Prompt-quality false positive analysis** - 7 refs classified, handoff produced (DONE)
3. **Anti-skip raw-log path analysis** - root cause identified, handoff produced (DONE)
4. **Sample outputs** - 5 samples packaged (DONE)
5. **Dirty-state classification** - 343 files classified (DONE, but not in declaration)
6. **Fresh gap selection** - 14 gaps across commercial/FOSS/dogfood (DONE)
7. **FODS GetUsedRange** - 1 new API, 3 overloads, 10 tests (DONE)
8. **Depth tests** - 72 .NET + 32 Python = 104 new tests (DONE)

### What R112 Did NOT Deliver
1. **Broad product breadth** - only 1 source file changed (FodsDocument.cs)
2. **FODT source progress** - 0 source changes, depth tests only
3. **Netpbm source progress** - 0 source changes, depth tests only
4. **Prompt-quality resolution** - handoff produced but not fixed (Supervisor stream)
5. **Dirty-state in declaration** - classification file exists but not referenced in evidence-declaration.yaml
6. **Sample-output detection** - samples exist but anti-skip still reports 0 found

### R112 Artifact Verification
| Artifact | Path | Exists |
|----------|------|--------|
| Preflight | reports/mainstream-r112/00-preflight.md | YES |
| R111 reconciliation | reports/mainstream-r112/r111-reconciliation.md | YES |
| Claim classification | reports/mainstream-r112/r111-claim-classification.json | YES |
| Prompt-quality analysis | reports/mainstream-r112/prompt-quality-failure-analysis.md | YES |
| Prompt-quality JSON | reports/mainstream-r112/prompt-quality-classification.json | YES |
| Anti-skip analysis | reports/mainstream-r112/anti-skip-raw-log-path-analysis.md | YES |
| Sample outputs (5) | reports/mainstream-r112/sample-outputs/ | YES |
| Dirty-state MD | reports/mainstream-r112/dirty-state-classification.md | YES |
| Dirty-state JSON | reports/mainstream-r112/dirty-state-classification.json | YES |
| Gap selection | reports/mainstream-r112/selected-mainstream-gaps-r112.json | YES |
| Source diff | reports/mainstream-r112/source-diffs/fods-getusedrange.diff | YES |
| Skill transcript | reports/mainstream-r112/skill-transcripts/fods-getusedrange-r112.json | YES |
| Raw logs (4) | reports/mainstream-r112/raw-logs/ | YES |
| Quota tracker | reports/mainstream-r112/quota-tracker.md | YES |
| Ledger entry | R112-GOVERNED-DOTNET-FODS-GETUSEDRANGE-001 | YES |
| Final IV | reports/mainstream-r112/final-adversarial-independent-verification.md | YES |

### R112 Verdict
EVIDENCE_REPAIR_AND_SINGLE_PRODUCT_PROGRESS - not broad product depth
