---
artifact_id: github-pat-refresh-20260513
artifact_type: report
path: reports/github/github-pat-refresh-20260513.md
visibility: internal
generated_by: claude-sonnet-4-6
generated_at: "2026-05-13"
sprint_id: GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001
lane: F
---

# GitHub PAT Refresh — Non-Mutating Probe

**Sprint:** GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001
**Lane:** F
**Date:** 2026-05-13

## Probe Results

| Check | Result |
|-------|--------|
| gh auth status | PASS — logged in as babar-raza |
| Active account | GH_TOKEN (babar-raza) |
| Token present | YES (NOT printed per security policy) |
| Token scopes (GH_TOKEN) | repo, workflow |
| Token scopes (keyring) | gist, read:org, repo |
| Remote URL | https://github.com/babar-raza/format-factory.git |
| Remote accessible | YES (gh auth confirms) |
| No remote mutation | YES — no push, no PR, no issue creation |

## Security Compliance

GITHUB_PAT_VALUE_NOT_PRINTED: YES
NO_REMOTE_MUTATION_CONFIRMED: YES
PUSH_NOT_EXECUTED: YES

## Notes

- `read:org` scope is absent from GH_TOKEN but present in keyring token.
  This is consistent with prior probe (2026-05-12, Lane D).
  `read:org` is not required for push operations.
- Token is User scope (not Machine scope) — consistent with prior probe.
- No PAT rotation performed (not required by sprint).

## Verdict

LANE_F_PASS
