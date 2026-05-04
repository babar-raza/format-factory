---
artifact_id: TC-0003
artifact_type: taskcard
path: taskcards/TC-0003-sdk-baseline.md
format_id: null
product_family: null
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: 2026-05-03
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Infrastructure taskcard. Resolves G-003 (SDK baselines not CI-verified).
---

# TC-0003: SDK Baseline Confirmation

**Phase:** 1
**Status:** not_started
**Owner:** TBD (developer)
**Created:** 2026-05-03
**Last updated:** 2026-05-03
**Blocking:** Phase 4+ CI setup
**Blocked by:** Phase 0 completion
**Format:** none (infrastructure)
**Gate:** none (supports Gate 10 CI readiness)

---

## Objective

Confirm that the Python and .NET SDK baselines defined in `docs/product-tracks.md` are correct, available in the development environment, and that a minimal project setup is achievable. Produce a confirmed baseline record in `tools/_readme.md` and update `src/python/_readme.md` and `src/dotnet/_readme.md` with verified SDK details. This resolves Gap G-003 (SDK baselines not CI-verified).

---

## Context

Phase 0 declared baselines: Python 3.11+ and .NET net8.0/net10.0 (no net9.0, which is EOL). The developer's machine has Python 3.13.2 and .NET SDK 9.0.200 installed. The task is to verify that the declared product baselines are achievable:
- Python 3.11+ means the product code must run on Python 3.11, not just on the developer's 3.13.
- .NET net8.0 must be targetable even though .NET 9 SDK is installed (cross-targeting).
- .NET 9.0.200 can compile net8.0 projects; this needs confirmation.

---

## Scope

### In scope

- Verify Python 3.11 is available (via venv, pyenv, or system install) or document how to obtain it
- Verify .NET SDK 9.0.200 can produce net8.0 and net10.0 binaries via multi-targeting
- Confirm `defusedxml` is pip-installable for Python security baseline
- Confirm `System.Xml` with `XmlReaderSettings` is available in net8.0 target
- Document confirmed SDK versions in `src/python/_readme.md` and `src/dotnet/_readme.md`
- Update `tools/_readme.md` with confirmed tool versions

### Out of scope

- Setting up CI (that is Phase 4+)
- Creating project files (`*.csproj`, `setup.py`, etc.) — that is Phase 4+ work
- Installing additional .NET SDKs unless they are needed immediately

---

## Acceptance Criteria

- [ ] Python 3.11 availability confirmed (or documented how to obtain it for CI)
- [ ] `python -c "import xml.etree.ElementTree"` succeeds on 3.11
- [ ] `pip install defusedxml` confirmed installable
- [ ] .NET SDK 9.0.200 can multi-target net8.0 (confirmed via `dotnet --version` and test csproj)
- [ ] net10.0 SDK availability noted (may require a separate download; document status)
- [ ] Confirmed baselines documented in `src/python/_readme.md` and `src/dotnet/_readme.md`
- [ ] `tools/_readme.md` updated with confirmed tool inventory
- [ ] Self-challenge completed (AGENTS.md Section I)
- [ ] `plans/master-plan.md` updated with taskcard completion and any gaps discovered

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Python readme update | `src/python/_readme.md` | internal | Confirmed SDK version |
| .NET readme update | `src/dotnet/_readme.md` | internal | Confirmed SDK version |
| Tools readme update | `tools/_readme.md` | internal | Confirmed tool inventory |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Product tracks doc | `docs/product-tracks.md` | Required |
| Security policy | `docs/security.md` | Required (defusedxml reference) |

---

## Steps

1. Check Python version on developer machine: `python --version` and `python3 --version`.
2. Verify Python 3.11 is available or document installation path for CI.
3. Test `pip install defusedxml` in a clean venv.
4. Check .NET SDK: `dotnet --version`. Confirm it can target net8.0.
5. Create a minimal test `.csproj` with `<TargetFrameworks>net8.0;net10.0</TargetFrameworks>` and run `dotnet build`. Note result.
6. Check if net10.0 SDK is installed or needs to be downloaded.
7. Update `src/python/_readme.md` with confirmed Python version and key package availability.
8. Update `src/dotnet/_readme.md` with confirmed .NET SDK version, targetable frameworks, and any gaps.
9. Update `tools/_readme.md` with tool inventory.
10. Complete self-challenge.
11. Update `plans/master-plan.md` with completion record and any new gaps.

---

## Completion Record

**Completed by:** (to be filled)
**Completion date:** (to be filled)
**Artifacts produced:** (to be filled)
**Gaps discovered:** (to be filled)
**Notes:** (to be filled)
