# GitHub PAT Readiness Probe

**Sprint:** DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001
**Lane:** D
**Date:** 2026-05-12

## PAT Environment Scope

| Scope | Result |
|-------|--------|
| Machine (System) | MISSING — not stored at system level |
| User | PRESENT — stored as User environment variable |
| Process/Bash | NOT_VISIBLE — Windows User env vars do not propagate to running bash processes |

**Note:** Human stated "Windows system environment variable" but token is in User scope, not Machine scope. Token is accessible from PowerShell sessions that inherit User env vars. Not accessible from Git Bash / subprocess without explicit mapping.

## gh Auth Probe Result

Method: Set GH_TOKEN from User env var (no print) → `gh auth status`

GH_AUTH_PROBE: PASS
Account: babar-raza
Auth method: GH_TOKEN (fine-grained PAT, github_pat_11... prefix — masked by gh)
Active account via GH_TOKEN: true

Also found: keyring token with scopes 'gist', 'read:org', 'repo' (existing gh CLI auth)

## Repo Remote Detection

git remote -v: origin https://github.com/babar-raza/format-factory.git

CURRENT_REMOTE_GITHUB_DETECTED: YES
Owner: babar-raza
Repo: format-factory
Visibility: PUBLIC (confirmed via gh repo view)

## Push Permission Inference

The keyring token has `repo` scope which includes push to owned repos.
The fine-grained PAT (GITHUB_PAT) — scope not confirmed via this probe.
The repo is PUBLIC and owned by babar-raza — push is likely authorized.

PUSH_PERMISSION_INFERRED: LIKELY (based on repo ownership + keyring token scopes)
NOTE: Push permission not tested by mutation — this is an inference only.

## No Remote Mutation Confirmed

NO_PUSH_EXECUTED: YES
NO_REMOTE_BRANCH_CREATED: YES
NO_PR_CREATED: YES
NO_REMOTE_MUTATION_CONFIRMED: YES

## PAT Handling Note

GITHUB_PAT value was NOT printed.
GITHUB_PAT was NOT written to any file on disk.
GITHUB_PAT was NOT committed.
Mapping to GH_TOKEN was in-memory only (PowerShell process scope).

## bash Propagation Note

GITHUB_PAT is stored as a Windows User env var. It does NOT automatically propagate
to Git Bash processes or Python subprocesses. To use from bash, explicit export is needed:
  `export GITHUB_PAT=$(powershell.exe -NoProfile -Command ...)`
Or: use PowerShell to invoke gh commands directly.

## Lane D Verdict

PAT_PRESENT_MACHINE_ENV: NO (User scope, not Machine)
PAT_PRESENT_USER_ENV: YES
PAT_VISIBLE_IN_BASH: NO (requires explicit export)
GH_AUTH_PROBE_PASS: YES (github.com, babar-raza, GH_TOKEN)
CURRENT_REMOTE_GITHUB_DETECTED: YES (babar-raza/format-factory, PUBLIC)
PUSH_PERMISSION_INFERRED: LIKELY
NO_REMOTE_MUTATION_CONFIRMED: YES

LANE_D_PASS_WITH_ENV_PROPAGATION_NOTE
