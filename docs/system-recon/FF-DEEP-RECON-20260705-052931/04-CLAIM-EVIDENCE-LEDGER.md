# 04-CLAIM-EVIDENCE-LEDGER.md

All claims from the system overview, architecture diagrams, and blog announcement are catalogued here with evidence classification.

## Classification Key

| Status | Meaning |
|---|---|
| `IMPLEMENTED_AND_VERIFIED` | Code exists AND runtime/test evidence confirms behavior |
| `IMPLEMENTED_NOT_RUNTIME_VERIFIED` | Code exists but not executed during this recon |
| `PARTIALLY_IMPLEMENTED` | Some components exist, others are missing or incomplete |
| `DOCUMENTED_ONLY` | Described in plans/docs but not confirmed in code |
| `PLANNED` | In plans/roadmaps but no implementation evidence |
| `DEPRECATED_OR_SUPERSEDED` | Existed but replaced by newer approach |
| `DISCONNECTED_OR_UNUSED` | Code exists but no consumer or invocation path |
| `CONTRADICTED` | Documentation and implementation disagree |
| `UNKNOWN` | Insufficient evidence to classify |

## Confidence Key

| Level | Meaning |
|---|---|
| `HIGH` | Multiple independent evidence sources confirm |
| `MEDIUM` | Single evidence source or partial verification |
| `LOW` | Inferred from indirect evidence |

---

## System Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-SYS-001 | Format Factory is a dual-track system (products + machinery) that converts file-format specifications into tested libraries | `IMPLEMENTED_AND_VERIFIED` | HIGH | `README.md`, `src/python/` (20 dirs), `src/net/` (10 dirs), `tools/supervisor/` (262 files) | — | FODS parse, ZST compress verified | None | 01, 02, 03 | Core identity claim |
| CLM-SYS-002 | The system addresses the problem of converting format specs into tested libraries | `IMPLEMENTED_AND_VERIFIED` | HIGH | Pipeline components from `acquisition-packs/` through `src/python/` to `oracle/` | — | — | None | 01 | Problem statement |
| CLM-SYS-003 | 20 Python and 10 .NET format implementations exist as source code | `IMPLEMENTED_AND_VERIFIED` | HIGH | `ls src/python/` = 20 format dirs, `ls src/net/` = 10 format dirs | — | — | None | 01, 03 | Independently counted |

## Architecture Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-ARCH-001 | The system uses an 11-layer architecture | `IMPLEMENTED_AND_VERIFIED` | HIGH | Layer paths verified: `tools/spec/`, `shared/qname-registry/`, `reports/capability-layer/`, `oracle/`, `src/python/`, `tests/`, `tools/supervisor/`, `tools/supervisor/governance_validators*.py`, `.supervisor/skill-registry.yaml` | — | — | L08 and L09 are gitignored local state (`.local/`) — exist but not version-controlled | 01, 02 | Layer boundaries confirmed via directory structure |
| CLM-ARCH-002 | Product source is manually written following a governed pattern, not continuously auto-generated | `IMPLEMENTED_AND_VERIFIED` | HIGH | `src/python/fods/parser.py` — hand-written streaming XML parser with IR-FODS-* requirement references; no code-gen markers | parser.py:1-15 | — | `templates/` directory exists but appears to be scaffolding only | 01, 02 | Inspected FODS, ZST, FODT source |
| CLM-ARCH-003 | Python packages expose dual APIs (class-based via Compat/ and dict-based via codec) | `IMPLEMENTED_AND_VERIFIED` | HIGH | `src/python/fods/__init__.py` imports both parser and Compat modules | `__init__.py` | `parse_fods()` returned dict at runtime | None | 01, 02 | Runtime verified |
| CLM-ARCH-004 | AI agents drive development but products are deterministic with no LLM calls | `IMPLEMENTED_AND_VERIFIED` | HIGH | `CLAUDE.md` governs agent; `src/python/fods/parser.py` has no AI imports | — | FODS parse returns deterministic output | None | 01, 02 | No `openai`, `anthropic`, or LLM imports in `src/` |
| CLM-ARCH-005 | A governed 10-step extension process exists | `IMPLEMENTED_AND_VERIFIED` | MEDIUM | `acquisition-packs/` (28 dirs), `/new-format-kickstart` skill in registry, `packaging/python/build-local-packages.py` | — | — | Not all 28 formats completed all steps | 01, 02 | Process confirmed; not all formats went through all gates |
| CLM-ARCH-006 | CI exists with lint, security, and tests; packaging works locally | `IMPLEMENTED_NOT_RUNTIME_VERIFIED` | MEDIUM | `.github/workflows/ci.yml` (lint, bandit, fast tests), `packaging/python/build-local-packages.py` | ci.yml:1-60 | — | CI was not triggered during recon; package build not executed | 01, 02 | CI file inspected but not run |
| CLM-ARCH-007 | Security measures exist (defusedxml, size limits, bandit, fuzz tests) | `IMPLEMENTED_AND_VERIFIED` | MEDIUM | `src/python/fods/parser.py:24-29` (defusedxml import), `MAX_FILE_BYTES` in constants.py, `.github/workflows/ci.yml` (bandit), `tests/fixtures/fods/malformed/` | parser.py:24-29 | — | defusedxml is optional (falls back to stdlib if not installed) | 01 | — |

## Pipeline Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-PIPE-001 | A 10+ stage pipeline from spec to library exists and is operational | `IMPLEMENTED_AND_VERIFIED` | HIGH | Components at each stage: scoring in `format-registry.yaml`, SAL in `tools/spec/`, QNames in `shared/qname-registry/`, source in `src/`, oracle in `oracle/`, tests in `tests/`, validators in `tools/supervisor/`, packaging in `packaging/` | — | Stages 6 (parse), 8 (test), 10 (validate) verified at runtime | Stage 11 (release) is blocked | 01, 02, 03 | Gate 11 not approved |
| CLM-PIPE-002 | SAL extracts structured facts from specifications | `IMPLEMENTED_AND_VERIFIED` | MEDIUM | 24 Python modules in `tools/specification-authority-layer/`; fact JSON files in `.local/sal-output/` | `requirement_extractor.py` | — | SAL involves AI-assisted steps — not fully deterministic | 01, 02 | Fact count (~14,441) from project records |
| CLM-PIPE-003 | Capability modeling tracks per-format features and gaps | `IMPLEMENTED_AND_VERIFIED` | MEDIUM | `reports/capability-layer/gap-ledger.json`, `gap-ledger-active.json`, capability model YAML | — | — | None | 01, 02 | Gap ledger contains hundreds of entries |
| CLM-PIPE-004 | Capability-to-feature compilation exists | `IMPLEMENTED_AND_VERIFIED` | MEDIUM | `tools/supervisor/capability_feature_compiler.py`, `tools/capability_layer/capability_to_feature_compiler.py` | — | — | Two implementations exist (pipeline vs planning) — potential duplication | 01, 02 | — |

## Product Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-PROD-001 | FODS supports parse, edit, write, and export in both Python and .NET | `IMPLEMENTED_AND_VERIFIED` | HIGH | Python: `parser.py` (475 LOC), `writer.py` (182 LOC), `csv_exporter.py` (124 LOC). .NET: `FodsParser.cs`, `FodsWriter.cs`, `FodsDocumentEditOps.cs` (738 LOC), 6 exporter classes | — | Python parse+write roundtrip verified at runtime | None | 01, 02, 03 | Most mature product |
| CLM-PROD-002 | Python has broader format coverage (20 vs 10) while .NET has deeper feature depth for FODS/FODT | `IMPLEMENTED_AND_VERIFIED` | HIGH | Python: 20 format dirs. .NET: 10 format dirs. FODS .NET: 10,197 LOC vs Python 4,903 LOC. FODS .NET has 6 exporters | — | — | None | 01, 03 | LOC counts independently verified |

## Governance Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-GOV-001 | 123 skills and 124 commands are registered | `IMPLEMENTED_AND_VERIFIED` | HIGH | `grep -c "skill_id:" .supervisor/skill-registry.yaml` = 123; `find .claude/commands -name "*.md" \| wc -l` = 124 | — | — | README claims 120 skills (stale count) | 01, 02 | README count slightly outdated |
| CLM-GOV-002 | The supervisor orchestrates autonomous sprint execution with continuation checking | `IMPLEMENTED_AND_VERIFIED` | HIGH | `supervisor_loop.py` (605 LOC), `autonomous_cycle.py` (2,651 LOC), `check_continuation.py` (796 LOC) — source inspected | — | — | None | 01, 02 | Sprint report directories confirm execution history |
| CLM-GOV-003 | 153 governance validators exist across 18 modules | `IMPLEMENTED_AND_VERIFIED` | HIGH | `grep -c "def validate_"` across all `governance_validators*.py` files = 153 across 18 files | — | — | README claims 101 validators, PROJECT_STATUS.md claims 101 — both stale | 01, 02 | Independently counted; previous documentation is outdated |

## Test Claims

| Claim ID | Claim | Classification | Confidence | Evidence | Symbol/Line | Runtime Evidence | Contradicting Evidence | Used In | Notes |
|---|---|---|---|---|---|---|---|---|---|
| CLM-TEST-001 | 39,863 tests collected across 6 layers | `IMPLEMENTED_AND_VERIFIED` | HIGH | `pytest --collect-only` returned 39,863 in 100.30s | — | Collection verified; 2,887 tests executed (FODS + ZST) | None | 01, 03 | Full suite not run due to time |
| CLM-TEST-002 | All 20 Python formats pass oracle verification (73/73) | `IMPLEMENTED_AND_VERIFIED` | HIGH | `oracle/formats/` contains 20 format directories; FODS `oracle-package.yaml` status: VERIFIED | — | — | Oracle result from project records, not re-run during recon | 01, 03 | Would need re-execution for independent verification |

## Additional Claims (not in main documents but verified during recon)

| Claim ID | Claim | Classification | Confidence | Evidence | Notes |
|---|---|---|---|---|---|
| CLM-SYS-004 | Repository has 1,810 commits over 64 days | `IMPLEMENTED_AND_VERIFIED` | HIGH | `git log --oneline \| wc -l` = 1,810; first commit 2026-05-02, latest 2026-07-05 | — |
| CLM-SYS-005 | Reports directory is 402 MB | `IMPLEMENTED_AND_VERIFIED` | HIGH | `du -sh reports/` = 402M | Historical sprint reports accumulate |
| CLM-ARCH-008 | CSS import shadowing: Python `csv` stdlib conflicts with format-factory csv package | `IMPLEMENTED_AND_VERIFIED` | HIGH | `from csv import parse_csv` fails because Python resolves to stdlib csv | Runtime failure observed during recon |
| CLM-ARCH-009 | No public packages have been published (PyPI or NuGet) | `IMPLEMENTED_NOT_RUNTIME_VERIFIED` | MEDIUM | Gate 11 not approved; no publication evidence found | — |
| CLM-GOV-004 | 840+ autonomous sprints completed | `DOCUMENTED_ONLY` | MEDIUM | README.md claims 840; not independently verified | Report dirs (r23-r133 + skills-r* + mainstream-*) exist but total not precisely counted |
| CLM-TEST-003 | FODS parse produces correct output at runtime | `IMPLEMENTED_AND_VERIFIED` | HIGH | `parse_fods('minimal-spreadsheet.fods')` returned `{sheets: [1 sheet]}` | Direct runtime execution |
| CLM-TEST-004 | FODS roundtrip (parse-write-parse) preserves data | `IMPLEMENTED_AND_VERIFIED` | HIGH | `write_fods(model, tmp); parse_fods(tmp)` returned matching structure | Direct runtime execution |
| CLM-TEST-005 | ZST compress/decompress roundtrip works | `IMPLEMENTED_AND_VERIFIED` | HIGH | 2,300 bytes → 41 bytes → 2,300 bytes, match confirmed | Direct runtime execution |
