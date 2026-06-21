# Preflight State — Format Factory Machinery Readiness Audit
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Repository Identity

| Field | Value |
|-------|-------|
| Branch | main |
| HEAD | 23d1333fdb51b8f07d517a29af311d46ffdd3eb9 |
| Session mode | INVESTIGATION ONLY (no src/ edits) |
| Date | 2026-06-21 |

## Recent Commits (last 10)

```
23d1333f test(fodt): add compat bootstrap import/attribute test (TC-HARD-005 complement)
20a823b9 chore(registry): add known-failures ledger and machine-generated FODT pilot audit
b93889cb test(fodt): add spec registry, QName stub, compat e2e, and ingest test suites
fd0395a7 feat(fodt): add FODT QName registry, Python spec stubs, and .NET Spec stubs
1c8e4a4f feat(spec-tooling): add FODT pilot audit generator and spec registry validators
0a92ff0f fix(governance): extract run_all_governance_validators to runner module with lazy imports
962e6ea9 chore(test-governance): add flaky-test tracking to slow-test-ledger
1320e557 fix(governance): plan-execution machinery forensic healing
4998619d feat(dotnet): add FODS numeric values and ZST probing
959552e2 fix(zst): repair analytics fallback import
```

## Supervisor State

| Field | Value |
|-------|-------|
| Mode | MODE 4 (ACTIVE_MCP_ACTIVATION) |
| Last sprint | tc-harden-003-test |
| Last verdict | ACCEPTED_WITH_REWORK |
| Autonomous continue (session-resume) | False |
| Continuation signal | YES_RESET_CLEAN (manual reset, not organic) |
| Active plan lock | polished-hopping-glacier.md TC-HARD-011 IN_PROGRESS |
| next-sprint.md plan reference | wiggly-doodling-wirth.md (discrepancy from active lock) |

## Active Plan Lock (CRITICAL)

File: `.local/supervisor/active-plan-lock.json`
```json
{
  "plan_path": "C:/Users/prora/.claude/plans/polished-hopping-glacier.md",
  "status": "IN_PROGRESS",
  "last_taskcard": "TC-HARD-011"
}
```

**This lock BLOCKS autonomous continuation per CLAUDE.md rules.**
The lock file belongs to prior session (session_id: 45da76b0e59c).
Resolution: The plan (polished-hopping-glacier.md) may be complete from a prior session.
Until resolved, autonomous product deepening is mechanically blocked.

## Key Directory Layout

```
src/
  python/
    _shared/         # Shared base classes
    abw/             # ABW codec (single file)
    csv/             # CSV parser, writer, stats
    dif/             # DIF parser
    fodg/            # FODG codec (single file, 1476 LOC)
    fodp/            # FODP codec (single file)
    fods/            # FODS - modular (parser, writer, neutral_model, models, constants, exceptions)
      fods/          # NESTED package (anomaly)
    fodt/            # FODT - modular (similar to FODS)
    gnumeric/        # Gnumeric
    ndjson/          # NDJSON
    ods/             # ODS
    odt/             # ODT
    pbm/pgm/ppm/     # Netpbm
    qoi/             # QOI
    sylk/            # SYLK
    toml/            # TOML
    tsv/             # TSV
    xcf/             # XCF (xcf_analytics.py: 5725 LOC MONOLITH)
    zst/             # ZST (zst_codec.py: 1549 LOC)
  net/
    csv/             # CsvDocument, CsvReader, CsvWriter
    fods/            # FodsDocument, FodsParser, FodsWriter, 8 exporters, Model/
    fodt/            # FodtDocument, FodtParser, FodtWriter, 6 exporters, Model/
    html/            # HtmlWriter
    markdown/        # MarkdownWriter
    ndjson/          # NdjsonDocument, NdjsonReader, NdjsonWriter
    netpbm/          # NetpbmParser, NetpbmWriter
    tsv/             # TsvDocument, TsvReader, TsvWriter
    txt/             # TxtWriter
    zst/             # ZstDocument, ZstParser

NO src/net/FormatFactory/Office/ (canonical namespace) — NOT IMPLEMENTED
NO src/net/FormatFactory/Table/ — NOT IMPLEMENTED
NO src/python/{format}/office/ — NOT IMPLEMENTED
NO src/python/{format}/table/ — NOT IMPLEMENTED
```

## Dirty Files Classification

The git status shows 100+ modified files. Classification by category:

- **Current sprint artifacts** (governance harness): tests/supervisor/*, tools/supervisor/*
- **Product source (modified)**: src/python/fods/fods/__init__.py, src/python/fods/fods/neutral_model.py, src/python/fods/fods/exceptions.py, src/python/zst/zst_codec.py, src/python/xcf/xcf_analytics.py, src/python/toml/toml_codec.py
- **Report/evidence artifacts**: reports/supervisor/*, reports/gate11/*, reports/capability-layer/*, etc.
- **Registry state**: registry/*.json, registry/*.yaml
- **Planning documents**: plans/*, taskcards/*, .supervisor/*
- **Unknown/untracked**: Hundreds of new test files under tests/python/deepening/ (arithmetic deepening tests, SUSPENDED)
- **Risky**: tests/python/fods/ contains 31+ ImportError test files for unimplemented functions

## Spec Cache State

```
.local/spec-cache/
  fods/1.3/workbench/
    verified-facts-review.yaml    # 78 real verified FODS facts
    verified-facts-auto-seed.yaml
    workbench-report.md
  zst/, csv/, dif/, fodg/, fodp/, fodt/, gnumeric/, ods/, odt/
  pbm/, pgm/, ppm/, tsv/         # Cache dirs exist, content unknown
```

Only FODS has verified facts. No other format has verified facts in the workbench.
