---
taskcard_id: GITHUB-PAT-readiness-probe
sprint_id: DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001
lane: D
status: completed
completed_at: "2026-05-12"
completed_by: claude-sonnet-4-6
visibility: internal
---

# GITHUB PAT Readiness Probe

**Sprint:** DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001
**Lane:** D
**Status:** COMPLETED

## Objective

Probe GitHub PAT availability and gh CLI authentication readiness WITHOUT:
- Printing the token value
- Writing the token to disk
- Mutating any remote state (no push, no branch, no PR)

## Findings

| Check | Result |
|-------|--------|
| GITHUB_PAT Machine scope | MISSING — token is User scope, not Machine scope |
| GITHUB_PAT User scope | PRESENT |
| PAT visible in bash process | NOT_VISIBLE (Windows User env vars do not auto-propagate to bash) |
| gh auth status via GH_TOKEN | PASS — babar-raza logged in, fine-grained PAT |
| Remote repo detected | YES — babar-raza/format-factory (PUBLIC) |
| Push permission inferred | LIKELY (repo owned by authenticated account, keyring has repo scope) |
| Remote mutation executed | NO |

## Key Note: User vs Machine Scope

The human described GITHUB_PAT as a "Windows system environment variable." However, the
probe confirmed the token is in **User** scope, not Machine (System) scope. This distinction
matters for subprocess propagation:

- PowerShell sessions (interactive) inherit User env vars → GH_TOKEN mapping works
- Git Bash / Python subprocesses → do NOT inherit User env vars by default
- To use from bash: `export GITHUB_PAT=$(powershell.exe -NoProfile -Command ...)`

## Artifacts Produced

- `reports/github/github-pat-readiness-probe-20260512.md` — full probe narrative
- `reports/github/github-pat-readiness-probe-20260512.yaml` — machine-readable summary
- `taskcards/GITHUB-PAT-readiness-probe.md` — this taskcard

## Verdict

LANE_D_PASS_WITH_ENV_PROPAGATION_NOTE

Push is ready once .NET 10 SDK is installed and Gate 11 implementation is complete.
The env propagation note is documented; no action required before Gate 11.
