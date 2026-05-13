---
taskcard_id: FODS-FODT-GATE11-TIER0-DEC034-IV
sprint_id: GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001
lane: E
status: pending_separate_session
visibility: internal
---

# DEC-034 Independent Verification — Gate 11 Tier 0

## Status: PENDING SEPARATE SESSION

Per DEC-034 (AGENTS.md Section V), independent verification must be executed in a
**separate session** from the implementation work. This taskcard records the
verification checklist to run in that session.

## Scope

Verify the Tier 0 .NET commercial implementations for FODS and FODT
(GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001, 2026-05-13).

## Verification Checklist (run in separate session)

### FODS

- [ ] `src/net/fods/FodsParser.cs` exists and contains Tier 0 implementation
- [ ] `src/net/fods/FormatFactory.Fods.csproj` version = 0.1.0-tier0, target = net10.0
- [ ] `src/net/fods/README.md` contains "commercial-only" and Tier 0 status
- [ ] `tests/net/fods/FormatFactory.Fods.Tests.csproj` exists
- [ ] `tests/net/fods/FodsParserTests.cs` exists
- [ ] `dotnet build src/net/fods/` succeeds (0 errors, 0 warnings)
- [ ] `dotnet test tests/net/fods/` reports 12/12 PASS, 0 FAIL
- [ ] FodsParser contains: DtdProcessing.Prohibit, XmlResolver = null
- [ ] FodsParser contains: MaxFileSizeBytes size guard
- [ ] FodsParser.Parse returns FodsParseResult with Sheets list
- [ ] No .NET FOSS package reference in csproj (DEC-033 Option B)
- [ ] registry/format-registry.yaml: dec033_option: B, dec033_status: resolved
- [ ] No forbidden paths created (src/dotnet/, src/python/open-source/)

### FODT

- [ ] `src/net/fodt/FodtParser.cs` exists and contains Tier 0 implementation
- [ ] `src/net/fodt/FormatFactory.Fodt.csproj` version = 0.1.0-tier0, target = net10.0
- [ ] `src/net/fodt/README.md` contains "commercial-only" and Tier 0 status
- [ ] `tests/net/fodt/FormatFactory.Fodt.Tests.csproj` exists
- [ ] `tests/net/fodt/FodtParserTests.cs` exists
- [ ] `dotnet build src/net/fodt/` succeeds (0 errors, 0 warnings)
- [ ] `dotnet test tests/net/fodt/` reports 13/13 PASS, 0 FAIL
- [ ] FodtParser contains: DtdProcessing.Prohibit, XmlResolver = null
- [ ] FodtParser contains: MaxFileSizeBytes size guard
- [ ] FodtParser.Parse returns FodtParseResult with ParagraphCount, HeadingCount, ListCount, Tables
- [ ] No .NET FOSS package reference in csproj (DEC-033 Option B)

### ACCEL-003 (Lane A)

- [ ] `tools/evidence/build_evidence_bundle.py` contains "PRE-PROOF" and "PASS 3"
- [ ] `tests/evidence/test_auto_proof_bundle.py` has 9 tests including
      `test_proof_inside_zip_is_not_candidate_only`
- [ ] `dotnet test tests/evidence/` or `python -m pytest tests/evidence/` 9/9 PASS

### SDK (Lane B)

- [ ] `dotnet --version` outputs 10.x.xxx

## Verdict Template

After running all checks:

```
FODS_TIER0_IV: PASS (N/N checks)
FODT_TIER0_IV: PASS (N/N checks)
ACCEL003_IV: PASS (N/N checks)
SDK_IV: PASS
OVERALL: GATE11_TIER0_DEC034_IV_PASS
```
