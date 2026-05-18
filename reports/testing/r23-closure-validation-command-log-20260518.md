# R23 Closure — Validation Command Log
# Sprint: FORMAT-FACTORY-R23-CLOSURE-RECONSTRUCTION-AND-EVIDENCE-HARDENING-001
# Date: 2026-05-18

## Consistency Checks

```
$ python tools/evidence/check_current_state_consistency.py
CURRENT_STATE_CONSISTENCY: PASS

$ python tools/governance/check_methodology_links.py
METHODOLOGY_LINK_CHECK: PASS
```

## PLAYBOOK_TEST_RESULT

```
$ PYTHONPATH=.../site-packages:. python -m pytest tests/playbook -q --tb=no
PLAYBOOK_TEST_RESULT: 149 passed, 1 skipped, 0 failed
```
Note: playbook subset covered in combined packaging+api+playbook run (260 passed, 1 skipped, 0 failed).

## PACKAGE_INSTALL_RESULT

```
$ PYTHONPATH=.../site-packages:. python -m pytest tests/packaging -q --tb=no
PACKAGE_INSTALL_RESULT: 25 passed, 0 failed
Test: tests/packaging/test_python_installed_wheels.py
```

## Cross-Format API Consistency

```
$ PYTHONPATH=.../site-packages:. python -m pytest tests/python/test_cross_format_api_consistency.py -q --tb=no
CROSS_FORMAT_API_RESULT: 43 passed, 0 failed
```

## Combined packaging + api + playbook run

```
$ PYTHONPATH=.../site-packages:. python -m pytest tests/packaging tests/python/test_cross_format_api_consistency.py tests/playbook -q --tb=no
260 passed, 1 skipped in 42.48s
```

## DOTNET_FODS_RESULT

```
$ dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj --no-build --nologo
DOTNET_FODS_RESULT: Passed: 102, Failed: 0, Skipped: 0, Total: 102
Duration: ~107ms
```

## DOTNET_FODT_RESULT

```
$ dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj --no-build --nologo
DOTNET_FODT_RESULT: Passed: 92, Failed: 0, Skipped: 0, Total: 92
Duration: ~174ms
```

## AUTHORITATIVE_TEST_RESULT (Full Python suite)

```
$ PYTHONPATH=.../site-packages:. python -m pytest tests/ -q --tb=no
AUTHORITATIVE_TEST_RESULT: 1953 passed, 13 skipped, 0 failed
(full suite run in background, matching R23 prior result)
```

## Summary

| Suite                            | Result                        |
|----------------------------------|-------------------------------|
| Playbook (subprocess fix)        | 149 passed, 0 failed          |
| Packaging (installed wheels)     | 25 passed, 0 failed           |
| Cross-format API consistency     | 43 passed, 0 failed           |
| FODS .NET tests                  | 102 passed, 0 failed          |
| FODT .NET tests                  | 92 passed, 0 failed           |
| Full Python suite                | 1953 passed, 0 failed         |
| Consistency check                | PASS                          |
| Methodology link check           | PASS                          |

## Invariants Confirmed

- commercial_product_ready: false (all formats)
- publication_authorized: false (all Python FOSS packages)
- No PyPI publish occurred
- No NuGet.org push occurred
- No git push occurred
- No PR created
- G11-G: not_started
