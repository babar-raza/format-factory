---
artifact_id: github-pat-and-remote-readiness-20260513
artifact_type: report
visibility: internal
generated_by: claude-opus-4-6
generated_at: "2026-05-13"
sprint_id: GATE11-APPROVAL-AND-RELEASE-READINESS-SWARM-001
lane: F
---

# GitHub PAT and Remote Readiness

## Authentication

| Check | Result |
|-------|--------|
| gh auth status | PASS — babar-raza authenticated |
| Active token source | GH_TOKEN environment variable |
| Token scopes | repo, workflow |
| Missing scope | read:org (advisory, not blocking for repo ops) |
| Token printed | NO |
| Token persisted | NO |

## Remote

| Check | Result |
|-------|--------|
| Remote URL | https://github.com/babar-raza/format-factory.git |
| Repo name | format-factory |
| Owner | babar-raza |
| Visibility | public |
| Default branch | main |

## Permissions

| Permission | Granted |
|------------|---------|
| admin | YES |
| maintain | YES |
| push | YES |
| pull | YES |
| triage | YES |

## Environment Note

read:org scope missing from active GH_TOKEN. Only needed for org-level queries.
Not required for push, PR, or release operations on babar-raza/format-factory.

## Mutations

PUSH_NOT_EXECUTED: YES
NO_REMOTE_MUTATION: YES
NO_TOKEN_PRINTED: YES
NO_TOKEN_PERSISTED: YES

## Verdict

LANE_F_PASS_WITH_ENV_NOTE
