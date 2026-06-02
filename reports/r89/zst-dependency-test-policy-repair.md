# R89 ZST Dependency Test Policy Repair (Train F)

See: reports/r89/train-fg-test-policy.md for full details.

## Summary
9 ZST tests fail in environments without zstandard (pip dependency).
In .local/venv/ (development environment), zstandard IS installed and all 73 ZST tests pass.
Classification: environment-dependent, not regression.
Policy: authoritative test environment is .local/venv/ which includes zstandard.

## Status: COMPLETE
