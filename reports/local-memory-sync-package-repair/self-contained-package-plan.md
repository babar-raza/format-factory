# Self-Contained Package Plan
# Sprint: FORMAT-FACTORY-LOCAL-MEMORY-SYNC-EVIDENCE-PACKAGE-REPAIR-001
# Date: 2026-06-04

## Target Package

- **Path:** `.local/supervisor/reviews/local-memory-sync-self-contained/declaration-review-package.zip`

## Inclusion List (all must be present)

### Evidence (root)
| Source Path | ZIP Path |
|---|---|
| .local/evidences/local-memory-sync/evidence-declaration.yaml | evidence/evidence-declaration.yaml |
| .local/evidences/local-memory-sync/evidence-manifest.yaml | evidence/evidence-manifest.yaml |

### Sprint Reports
| Source Path | ZIP Path |
|---|---|
| reports/local-memory-sync/preflight.md | reports/local-memory-sync/preflight.md |
| reports/local-memory-sync/read-files.md | reports/local-memory-sync/read-files.md |
| reports/local-memory-sync/allowed-paths.md | reports/local-memory-sync/allowed-paths.md |
| reports/local-memory-sync/forbidden-paths.md | reports/local-memory-sync/forbidden-paths.md |
| reports/local-memory-sync/taskcard-state.json | reports/local-memory-sync/taskcard-state.json |
| reports/local-memory-sync/product-first-sync.md | reports/local-memory-sync/product-first-sync.md |
| reports/local-memory-sync/four-stream-sync.md | reports/local-memory-sync/four-stream-sync.md |
| reports/local-memory-sync/ai-operating-model-sync.md | reports/local-memory-sync/ai-operating-model-sync.md |
| reports/local-memory-sync/external-tool-sync.md | reports/local-memory-sync/external-tool-sync.md |
| reports/local-memory-sync/mainstream-train-sync.md | reports/local-memory-sync/mainstream-train-sync.md |
| reports/local-memory-sync/plan-status-sync.md | reports/local-memory-sync/plan-status-sync.md |
| reports/local-memory-sync/prompt-template-sync.md | reports/local-memory-sync/prompt-template-sync.md |
| reports/local-memory-sync/validation-results.md | reports/local-memory-sync/validation-results.md |
| reports/local-memory-sync/changed-files.md | reports/local-memory-sync/changed-files.md |
| reports/local-memory-sync/final-git-status.txt | reports/local-memory-sync/final-git-status.txt |
| reports/local-memory-sync/review-package-proof.md | reports/local-memory-sync/review-package-proof.md |

### Package Repair Reports
| Source Path | ZIP Path |
|---|---|
| reports/local-memory-sync-package-repair/package-gap-analysis.md | reports/local-memory-sync-package-repair/package-gap-analysis.md |
| reports/local-memory-sync-package-repair/manifest-vs-zip-audit.json | reports/local-memory-sync-package-repair/manifest-vs-zip-audit.json |
| reports/local-memory-sync-package-repair/self-contained-package-plan.md | reports/local-memory-sync-package-repair/self-contained-package-plan.md |
| reports/local-memory-sync-package-repair/final-validation-results.md | reports/local-memory-sync-package-repair/final-validation-results.md |
| reports/local-memory-sync-package-repair/review-package-proof.md | reports/local-memory-sync-package-repair/review-package-proof.md |

### Governance Docs
| Source Path | ZIP Path |
|---|---|
| docs/governance/product-first-operating-model.md | docs/governance/product-first-operating-model.md |
| docs/governance/four-stream-operating-model.md | docs/governance/four-stream-operating-model.md |
| docs/governance/ai-authority-boundary.md | docs/governance/ai-authority-boundary.md |
| docs/governance/external-tool-architecture.md | docs/governance/external-tool-architecture.md |
| docs/governance/ruflo-runtime-governance.md | docs/governance/ruflo-runtime-governance.md |
| docs/governance/superpowers-skill-intake.md | docs/governance/superpowers-skill-intake.md |
| docs/governance/ghidra-mcp-compliance-gate.md | docs/governance/ghidra-mcp-compliance-gate.md |
| docs/governance/mainstream-poc-mega-train.md | docs/governance/mainstream-poc-mega-train.md |

### Prompt Templates
| Source Path | ZIP Path |
|---|---|
| docs/prompt-templates/mainstream-poc-mega-train-template.md | docs/prompt-templates/mainstream-poc-mega-train-template.md |
| docs/prompt-templates/format-factory-stream-prompt-requirements.md | docs/prompt-templates/format-factory-stream-prompt-requirements.md |
| docs/prompt-templates/external-tool-aware-repair-template.md | docs/prompt-templates/external-tool-aware-repair-template.md |
| docs/prompt-templates/repair-order-reference.md | docs/prompt-templates/repair-order-reference.md |

### State
| Source Path | ZIP Path |
|---|---|
| state/current-state.md | state/current-state.md |

### Package Manifest
| Source Path | ZIP Path |
|---|---|
| reports/local-memory-sync-package-repair/self-contained-package-manifest.json | package-manifest.json |

## Exclusion List (stale global-state from Mainstream R113)

| File | Reason |
|---|---|
| global-state/context-pack.yaml | Stale Mainstream R113 global state — not relevant to memory-sync |
| global-state/continuation-signal.json | Stale Mainstream R113 continuation signal |
| global-state/mcp.json | Stale MCP config snapshot |
| global-state/poc-targets.yaml | Stale POC targets from Mainstream R113 |
| global-state/product-code-change-ledger.json | Stale product ledger |
| global-state/selected-product-gaps.json | Stale gap selection |
| global-state/supervisor/* | Stale supervisor outputs from Mainstream R113 |
| historical/r91-work-item-grades.* | Stale R91 historical grades |
| supervisor/work-item-grades.* | Stale grading artifacts |
| supervisor/materialized-evidence-review.md | Stale review artifact |

These files are EXCLUDED because they are from Mainstream R113 (a different sprint) and would mislead a reviewer into thinking the memory-sync sprint produced product work or triggered continuation decisions.
