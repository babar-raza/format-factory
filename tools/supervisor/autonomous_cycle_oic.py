"""
autonomous_cycle_oic.py — Output Invariant Check and Cross-Platform Parity helpers.

Extracted from autonomous_cycle_extensions.py to keep it within baseline_loc_cap.
FI-020 / FIOP-FULL-001: LOC healing 2026-07-15.
"""


def run_output_invariant_and_parity_checks(
    declaration_path: "Path | str",
    repo_root: "Path",
) -> list:
    """Run Step 0d (OIC) and 0e (CPF) checks (extracted from autonomous_cycle.py).

    TC-PGI-045: Extracted to reduce autonomous_cycle.py LOC below baseline_loc_cap.
    Non-blocking — any exception is caught and logged.
    Returns a list of rework entry strings (may be empty).
    """
    import json as _json
    from pathlib import Path as _Path

    _OIC_EXPORT_SIGS = [
        "ToJson", "ExportToJson", "ExportToNdjson",
        "ToHtml", "ExportToHtml", "ExportToXml",
        "to_json", "export_json", "to_html", "export_html",
    ]
    _oic_rework_entries: list = []

    # Step 0d (TC-B2): Output Invariant Check (OIC)
    print("=== STEP 0d: OUTPUT INVARIANT CHECK (OIC) ===")
    try:
        import sys as _oic_sys
        _oic_tools = str(_Path(__file__).resolve().parent.parent / "assurance")
        if _oic_tools not in _oic_sys.path:
            _oic_sys.path.insert(0, _oic_tools)
        from output_invariant_checker import OutputInvariantChecker as _OIC  # type: ignore[import]

        _oic_decl_path = _Path(declaration_path)
        _oic_diff = ""
        _oic_decl_raw: dict = {}
        if _oic_decl_path.exists():
            try:
                _oic_decl_raw = _json.loads(_oic_decl_path.read_text(encoding="utf-8"))
                _oic_diff = _oic_decl_raw.get("diff_content", "") or ""
            except Exception:
                pass

        _oic_triggered = any(sig in _oic_diff for sig in _OIC_EXPORT_SIGS)
        if not _oic_triggered:
            print("  [OIC] No JSON/HTML/XML export method changes detected — skipping")
        else:
            print("  [OIC] Export signature detected in diff — running invariant checks")
            _oic = _OIC()
            _oic_results: list = []
            _oic_failures: list = []

            _oic_fixtures_dir = repo_root / "tests" / "assurance" / "fixtures"
            if _oic_fixtures_dir.exists():
                for _oic_fix in sorted(_oic_fixtures_dir.iterdir()):
                    try:
                        _oic_content = _oic_fix.read_text(encoding="utf-8", errors="replace")
                        _oic_ctx = f"fixture:{_oic_fix.name}"
                        if _oic_fix.suffix in (".json", ".ndjson"):
                            for _ln in _oic_content.splitlines():
                                _ln = _ln.strip()
                                if _ln:
                                    _r = _oic.check_json(_ln, _oic_ctx)
                                    _oic_results.append({"context": _oic_ctx, "check": "json", "pass": _r.passed, "detail": _r.error})
                                    if not _r.passed:
                                        _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                        elif _oic_fix.suffix in (".html",):
                            _r = _oic.check_html_cell_safety(_oic_content, _oic_ctx)
                            _oic_results.append({"context": _oic_ctx, "check": "html", "pass": _r.passed, "detail": _r.error})
                            if not _r.passed:
                                _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                        elif _oic_fix.suffix in (".xml", ".fods", ".fodt", ".fodp", ".fodg"):
                            _r = _oic.check_xml(_oic_content, _oic_ctx)
                            _oic_results.append({"context": _oic_ctx, "check": "xml", "pass": _r.passed, "detail": _r.error})
                            if not _r.passed:
                                _oic_failures.append(f"{_oic_ctx}: {_r.error}")
                    except Exception as _oic_fix_err:
                        print(f"  [OIC] WARNING: fixture {_oic_fix.name} error: {_oic_fix_err}")
            else:
                print("  [OIC] No fixtures directory — invariant check skipped")

            import datetime as _oic_dt
            _oic_run_id = _oic_decl_raw.get("run_id", "unknown")
            _oic_report_dir = repo_root / "reports" / "assurance"
            _oic_report_dir.mkdir(parents=True, exist_ok=True)
            _oic_report_path = _oic_report_dir / f"oic-{_oic_run_id}.json"
            _oic_report_path.write_text(
                _json.dumps({
                    "run_id": _oic_run_id,
                    "timestamp": _oic_dt.datetime.utcnow().isoformat() + "Z",
                    "triggered_by": [s for s in _OIC_EXPORT_SIGS if s in _oic_diff],
                    "results": _oic_results,
                    "failures": _oic_failures,
                    "pass": len(_oic_failures) == 0,
                }, indent=2),
                encoding="utf-8",
            )

            if _oic_failures:
                print(f"  [OIC] {len(_oic_failures)} invariant failure(s) — adding to rework_items (non-blocking)")
                for _f in _oic_failures:
                    print(f"    FAIL: {_f}")
                _oic_rework_entries = [f"OIC_INVARIANT_FAIL:{_f}" for _f in _oic_failures]
            else:
                print(f"  [OIC] All {len(_oic_results)} invariant checks PASS")
            print(f"  [OIC] Report: {_oic_report_path}")
    except ImportError:
        print("  [OIC] output_invariant_checker not available — skipping (non-blocking)")
    except Exception as _oic_err:
        print(f"  [OIC] WARNING: OIC step failed ({_oic_err}) — skipping (non-blocking)")

    # Step 0e (TC-C2): Cross-Platform Parity Check
    print("=== STEP 0e: CROSS-PLATFORM PARITY CHECK ===")
    _CPF_TRIGGER_PATHS = ("src/net/csv/", "src/python/csv/")
    try:
        _cpf_decl_path = _Path(declaration_path)
        _cpf_changed: list = []
        if _cpf_decl_path.exists():
            try:
                _cpf_decl = _json.loads(_cpf_decl_path.read_text(encoding="utf-8"))
                _cpf_changed = _cpf_decl.get("changed_files", []) or []
            except Exception:
                pass

        _cpf_triggered = any(
            any(trigger in str(f).replace("\\", "/") for trigger in _CPF_TRIGGER_PATHS)
            for f in _cpf_changed
        )
        if not _cpf_triggered:
            print("  [CPF] No CSV source changes detected — skipping")
        else:
            import sys as _cpf_sys
            _cpf_tools = str(_Path(__file__).resolve().parent.parent / "assurance")
            if _cpf_tools not in _cpf_sys.path:
                _cpf_sys.path.insert(0, _cpf_tools)
            from cross_platform_parity_runner import CrossPlatformParityRunner as _CPF  # type: ignore[import]

            _cpf_fixtures_path = repo_root / "tests" / "cross-platform" / "csv" / "parity-fixtures.yaml"
            if not _cpf_fixtures_path.exists():
                print("  [CPF] No parity fixtures found — skipping")
            else:
                _cpf = _CPF()
                _cpf_fixtures = _cpf.load_fixtures(_cpf_fixtures_path)
                _cpf_results = _cpf.run_all(_cpf_fixtures)
                _cpf_summary = _cpf.summary(_cpf_results)
                print(f"  [CPF] {_cpf_summary['passed']}/{_cpf_summary['total']} fixtures PASS")

                _cpf_report_dir = repo_root / "reports" / "assurance"
                _cpf_report_dir.mkdir(parents=True, exist_ok=True)
                _cpf_run_id = (
                    _json.loads(_cpf_decl_path.read_text(encoding="utf-8")).get("run_id", "unknown")
                    if _cpf_decl_path.exists() else "unknown"
                )
                _cpf_report_path = _cpf_report_dir / f"cross-platform-parity-{_cpf_run_id}.json"
                _cpf_report_path.write_text(
                    _json.dumps({"run_id": _cpf_run_id, "summary": _cpf_summary,
                                 "results": [r.to_dict() for r in _cpf_results]}, indent=2),
                    encoding="utf-8",
                )

                if _cpf_summary["failures"]:
                    print(f"  [CPF] {len(_cpf_summary['failures'])} parity failure(s) — adding to rework_items (non-blocking)")
                    for _cpf_f in _cpf_summary["failures"]:
                        print(f"    FAIL: {_cpf_f['fixture_id']}: {_cpf_f.get('error', '')}")
                    _oic_rework_entries.extend([
                        f"CPF_PARITY_FAIL:{f['fixture_id']}" for f in _cpf_summary["failures"]
                    ])
                print(f"  [CPF] Report: {_cpf_report_path}")
    except ImportError:
        print("  [CPF] cross_platform_parity_runner not available — skipping (non-blocking)")
    except Exception as _cpf_err:
        print(f"  [CPF] WARNING: parity check failed ({_cpf_err}) — skipping (non-blocking)")

    return _oic_rework_entries
