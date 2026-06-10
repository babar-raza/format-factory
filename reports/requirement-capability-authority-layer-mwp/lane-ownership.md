# Lane Ownership — MWP Sprint

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-MWP-001

## Lanes

| Lane | Purpose | Primary Outputs |
|------|---------|----------------|
| Lane 0 | Coordinator: preflight, gate, dirty-state, taskcard-state | coordinator files in reports/requirement-capability-authority-layer-mwp/ |
| Lane A | Schemas and models | requirements-authority/schemas/*.json, requirements-authority/README.md |
| Lane B | Core runtime tools | tools/requirements_authority/*.py |
| Lane C | Fixtures and tests | requirements-authority/fixtures/**; tests/supervisor/test_requirement_capability_*.py |
| Lane D | Governance and templates | docs/governance/requirement-capability-authority-layer.md updates; docs/prompt-templates/*.md |
| Lane E | Sample integration run | reports/requirement-capability-authority-layer-mwp/sample-* |
| Lane F | Validation + evidence | reports/requirement-capability-authority-layer-mwp/validation-results.*, final-git-status.txt, evidence files |
