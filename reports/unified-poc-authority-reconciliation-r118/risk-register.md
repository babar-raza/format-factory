# R118 Risk Register

**Sprint:** FORMAT-FACTORY-UNIFIED-POC-AUTHORITY-RECONCILIATION-R118-001

| Risk ID | Description | Probability | Impact | Mitigation | Status |
|---------|-------------|-------------|--------|------------|--------|
| R-001 | Export target writers missing → FODS/FODT export claims cannot be verified | HIGH | POC blocker | Audit source; downgrade claims if missing | MITIGATED |
| R-002 | Grading machinery fix does not achieve ACCEPTED_VERIFIED for all items | MEDIUM | Score remains low | Fixed via tests_supporting in declaration | RESOLVED |
| R-003 | autonomous_cycle exits non-zero after declaration repair | LOW | Restart required | Declaration validated before cycle run | RESOLVED |
| R-004 | Anti-skip missing_sample_outputs still fires at LOW | HIGH | Informational only | LOW severity = note only, non-blocking | ACCEPTED |
| R-005 | Gate 11 approval accidentally executed | VERY LOW | Hard stop | Policy: no approval without explicit authorization | MONITORED |
| R-006 | Product source files accidentally edited | LOW | Sprint invalidated | Forbidden path checks in place | MONITORED |
| R-007 | DIF write_dif CRLF behavior on non-Windows platform | MEDIUM | Test flakiness | Verified via Windows-specific test run | RESOLVED |

## Hard Stop Conditions

Any of these immediately stop all autonomous work:
1. Request to git push or commit
2. Request to approve Gate 8 or Gate 11
3. Request to publish to NuGet/PyPI
4. MCP activation change
5. Destructive git operation
