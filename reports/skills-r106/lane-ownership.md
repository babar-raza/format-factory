# Lane Ownership — Skills R106

| Lane | Owner | Files (exclusive) |
|------|-------|-------------------|
| Coordinator | Skills coordinator | .supervisor/skill-registry.yaml, .local/evidences/skills-r106/*, reports/skills-r106/scoreboard.md |
| A | Review supervisor | reports/skills-r106/r105-work-item-regrading.* |
| B | Transcript supervisor | reports/skills-r106/transcript-grading-integration.md, tests/python/supervisor/test_r106_*.py |
| C | Registry supervisor | reports/skills-r106/skill-registry-maturity.md, reports/skills-r106/orphan-command-resolution.md |
| D | Handoff supervisor | reports/skills-r106/governed-handoff-proof.md, reports/skills-r106/generated-handoffs/* |
| E | Adoption supervisor | reports/skills-r106/cross-stream-adoption-enforcement.md, reports/skills-r106/adoption-checklists/* |
| F | Command validator | reports/skills-r106/command-validator-hardening.md |
| G | State supervisor | reports/skills-r106/stream-state-classification.md |
| H | Prompt supervisor | reports/skills-r106/generated-next-skills-prompt.md |
| I | IV supervisor | reports/skills-r106/final-adversarial-independent-verification.md |

## Overlap Resolution
- `.supervisor/skill-registry.yaml` — Coordinator only (Lane C proposes, Coordinator applies)
- `tests/python/supervisor/` — Lane B (new R106 tests), Lane F (validator tests)
- No lane touches `src/python/` or `src/net/` directly
