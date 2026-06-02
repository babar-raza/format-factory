---
sprint: R91
generated_by: r91-worker
---

# R91 Lane Ownership

## Coordinator-Owned Files

The Coordinator owns the following files exclusively. No lane may modify these without Coordinator authorization:

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Session instructions |
| `plans/master-plan.md` | Master plan |
| `.supervisor/policies.yaml` | Supervisor policies |
| `.supervisor/skill-registry.yaml` | Skill registry |
| `product-capability-matrix/poc-targets.yaml` | POC target matrix |
| `memory/00-index.md` | Memory index |
| `state/current-state.md` | Current state (human-readable) |
| `state/current-state.json` | Current state (machine-readable) |
| `reports/supervisor/next-sprint.md` | Next sprint prompt |
| `reports/supervisor/session-resume.md` | Session resume |
| `reports/r91/final-verdict.md` | R91 final verdict |
| `.local/evidences/r91/evidence-declaration.yaml` | R91 evidence declaration |

## Lane-Local Ownership

Lanes A through Y write only to their own lane-local report files under `reports/r91/`. They do not modify Coordinator-owned files.

| Lane | Scope | Output Path |
|------|-------|-------------|
| A | Sprint setup, environment | `reports/r91/lane-a-*.md` |
| B | Context pack | `reports/r91/lane-b-*.md` |
| C | Inherited failure repair | `reports/r91/lane-c-*.md` |
| D | Per-item supervisor grading | `reports/r91/lane-d-*.md` |
| E | Next-sprint generator update | `reports/r91/lane-e-*.md` |
| F | Flow documentation | `reports/r91/lane-f-*.md` |
| G | FODS .NET SetCellValue | `reports/r91/lane-g-*.md` |
| H | FODT .NET SaveToFile | `reports/r91/lane-h-*.md` |
| I | Netpbm .NET SetPixelColor | `reports/r91/lane-i-*.md` |
| J | Python Netpbm PPM example | `reports/r91/lane-j-*.md` |
| K | Context pack definition | `reports/r91/lane-k-*.md` |
| L | .NET FODS product deepening | `reports/r91/lane-l-*.md` |
| M | .NET FODT product deepening | `reports/r91/lane-m-*.md` |
| N | .NET Netpbm product deepening | `reports/r91/lane-n-*.md` |
| O | Python FOSS packaging | `reports/r91/lane-o-*.md` |
| P | SYLK CSV hardening | `reports/r91/lane-p-*.md` |
| Q | DIF CSV hardening | `reports/r91/lane-q-*.md` |
| R | FODT .NET TXT dogfood bridge | `reports/r91/lane-r-*.md` |
| S | PPM→PGM dogfood verify | `reports/r91/lane-s-*.md` |
| T | Package matrix update | `reports/r91/lane-t-*.md` |
| U | Docs update | `reports/r91/lane-u-*.md` |
| V | Supervisor work-item-grades output | `reports/r91/lane-v-*.md` |
| W | Continuation signal update | `reports/r91/lane-w-*.md` |
| X | Evidence declaration | `reports/r91/lane-x-*.md` |
| Y | Supervisor autonomous-cycle run | `reports/r91/lane-y-*.md` |

## Conflict Resolution

If two lanes would write to the same file, the Coordinator resolves by assigning ownership explicitly. Lanes must not speculatively modify files outside their scope.
