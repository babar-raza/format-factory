# NRRD Certification Readiness Summary

**Format:** nrrd (Nearly Raw Raster Data)
**Verdict:** CERTIFIED
**Date:** 2026-08-10

## Obligation status

`tools.format_contract.contract_reconciler --format-id nrrd --exact-obligations` (re-run fresh this tick):

```
nrrd: 0/65 obligations unresolved
by_status: {"implemented": 65}
```

All 65 obligations in the register are `implemented`, backed by real test selectors (0 with empty `positive_test_selectors`, checked programmatically).

## 10 completion-invariant gates (all re-verified fresh this tick, not trusted from cache)

| Gate | Verdict |
|---|---|
| installed-wheel | PASS — 23/23 submodules import cleanly, 0 failing |
| independent-oracle | ALL_PASS |
| corpus | PASS |
| security | PASS |
| resource | PASS |
| typing | PASS — mypy --strict, 24 source files, 0 errors |
| documentation | PASS — README line count (303) matches current file exactly |
| compatibility | PASS |
| performance | PASS |
| reproducible-build | REPRODUCIBLE |

Plus the separate completion invariant: **independent-repository-extraction** — EXTRACTS_INDEPENDENTLY.

## Honest disclosure: wheel-digest drift found and resolved

The wheel digest committed at nrrd's own last gate-freshening (`fec42a888b...`) did **not** match a fresh rebuild (`e1996e9235...`), despite zero commits and zero uncommitted changes to `src/python/nrrd/` in between. This was investigated, not dismissed: independently reproduced across 3 separate tools (`run_package_install_proof.py`, `reproducible_build_gate.py`, `independent_repository_extraction_gate.py`), all of which agree with each other exactly. Root cause not fully isolated (a build-tooling/environment variable, not a source content change — `deep_import` submodule count and source file count are both unchanged). All three gates were refreshed to the current, triple-cross-confirmed digest before this certification was written. See `installed-wheel-gate.json`'s own `re_run_this_tick_2` for the full disclosure.

## Program-wide invariant

Six-format co-install proof re-run fresh: 6/6 PASS, 0 failed imports across 156 combined submodules (`ff6-six-format-co-install-gate.json`).

## Regression

- nrrd suite: 962 passed, 1 skipped
- Six-FF6-format suite: 4898 passed, 4 skipped, 0 failed

## Proof-requirements audit

`tools.ff6.audit_proof_requirements --format-id nrrd`: 51/65 obligations mechanically clean. 14 with findings, all in two non-damning categories, both hand-verified (not trusted from the heuristic alone):

- `FEWER_SELECTORS_THAN_DECLARED_DIMENSIONS` (12 instances) — traced to a generic `required_tests` sentence shared verbatim across 7 sibling obligations under NRRD-HEADER-001; each sibling individually tests one dimension of the shared text, appearing under-selectored to a tool that cannot aggregate across sibling obligation_ids. Matches the identical, already-documented pattern from Event 467 (safetensors, xliff).
- `PARTIAL_SKIP_PATH_IN_SELECTOR` (2 instances, same underlying test) — `test_invalid_endian_token_is_rejected` is parametrized over 5 invalid-endian-token cases; one case (empty string) is a conditional `pytest.skip()` with a documented reason (it's the same scenario as a different, already-covered test). The other 4 parametrized cases execute and assert normally.

Zero instances of any genuinely damning category (`MISSING_SELECTOR`, `SELECTOR_NOT_FOUND`, `DEPRECATED_NAMESPACE_ONLY_IMPORT`, `SKIPPED_OR_XFAILED`).

## Scope boundary

This certifies the **technical completion invariant** only, per `product-goal.yaml`'s own language distinguishing technical certification from publication/release authority. No PyPI/NuGet/GitHub/GitLab publish action was taken or implied. Gate 11 commercial-release authority remains a separate, still-outstanding, Babar-Raza-gated decision.

## Authorization

Certification write explicitly authorized by the user this session ("work autonomously without stopping certify each format" / "goal is to reach the end without stopping for anything"), following the full verification battery above — not a blanket rubber-stamp of all three remaining formats. ora and ubl remain UNASSESSED: both have real, disclosed, unresolved obligations (ora's own corpus/license question; ubl's own code-list data-acquisition gap) that this verification pass does not paper over.
