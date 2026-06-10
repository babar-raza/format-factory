"""Temporary script to write all 8 pilot reports."""
import json
from datetime import datetime, timezone
from pathlib import Path

PILOTS_DIR = Path("reports/capability-layer/pilots")
PILOTS_DIR.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat()
RUN_ID = "capability-feature-understanding-layer-healing-20260608-e382e5f"


def write_pilot(pilot_id, data):
    md_path = PILOTS_DIR / f"{pilot_id}.md"
    json_path = PILOTS_DIR / f"{pilot_id}.json"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    verdict = data["final_verdict"]
    md = (
        f"# Pilot Report: {pilot_id}\n\n"
        f"**Format**: {data['format']}  \n"
        f"**Product Type**: {data['product_type']}  \n"
        f"**Verdict**: {verdict}  \n"
        f"**Generated**: {NOW}  \n"
        f"**Run ID**: {RUN_ID}\n\n"
        f"## Authority Inputs\n\n"
        + "\n".join(f"- {a}" for a in data["authority_inputs"])
        + f"\n\n## Inspected\n\n"
        f"- Source files: {', '.join(data['source_files_inspected']) or 'None'}\n"
        f"- Test files: {data['tests_inspected']}\n"
        f"- Examples: {data['examples_inspected']}\n\n"
        f"## Generated Records\n\n"
        f"- Count: {data['generated_capability_records']['count']}\n"
        f"- Sample: {data['generated_capability_records'].get('sample', 'see map')}\n\n"
        f"## Gaps Found\n\n"
        f"{data['generated_gap_entries']['count']} gaps. {data['generated_gap_entries'].get('summary', '')}\n\n"
        f"## Validator Result\n\n"
        f"Exit code: {data['validator_result']['exit_code']} - {data['validator_result']['summary']}\n\n"
        f"## Test Result\n\n"
        f"{data['test_result']['pass_count']} pass / {data['test_result']['fail_count']} fail\n\n"
        f"## Contradictions\n\n"
        + ("\n".join(f"- {c}" for c in data["contradictions_found"]) or "None")
        + f"\n\n## Final Verdict\n\n**{verdict}**\n\n{data.get('verdict_reason', '')}\n"
    )
    md_path.write_text(md, encoding="utf-8")
    print(f"[OK] {pilot_id}: {verdict}")


PILOTS = [
    {
        "pilot_id": "CAP-PILOT-C001",
        "format": "FODS",
        "product_type": "commercial",
        "authority_inputs": [
            "product-capability-matrix/poc-targets.yaml (commercial_net_products.FODS)",
            "Gate 11 G11-G approval by Babar Raza 2026-06-05",
        ],
        "source_files_inspected": ["src/net/fods/"],
        "tests_inspected": 68,
        "examples_inspected": "examples/net/fods/ (5 files)",
        "generated_capability_records": {
            "count": 25,
            "sample": "load, save_same_format, export_csv, export_html, export_json, export_markdown",
        },
        "generated_gap_entries": {"count": 0, "summary": "All expected capabilities implemented per poc-targets.yaml"},
        "taskcards_created_or_updated": [],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 547, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/net/fods/"],
            "key_checks": ["Gate 11 confirmed", "68 .NET test files", "547 tests pass"],
            "result": "VERIFIED",
        },
        "contradictions_found": [],
        "repairs_performed": [],
        "final_verdict": "PASS_VERIFIED",
        "verdict_reason": "All FODS commercial records test_verified. Gate 11 approved. 547 tests pass.",
    },
    {
        "pilot_id": "CAP-PILOT-C002",
        "format": "FODT",
        "product_type": "commercial",
        "authority_inputs": [
            "product-capability-matrix/poc-targets.yaml (commercial_net_products.FODT)",
            "Gate 11 G11-G approval by Babar Raza 2026-06-05",
        ],
        "source_files_inspected": ["src/net/fodt/"],
        "tests_inspected": 65,
        "examples_inspected": "examples/net/fodt/ (4 files)",
        "generated_capability_records": {
            "count": 25,
            "sample": "load, save_same_format, export_txt, export_markdown, export_html",
        },
        "generated_gap_entries": {"count": 0, "summary": "All expected capabilities implemented"},
        "taskcards_created_or_updated": [],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 520, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/net/fodt/"],
            "key_checks": ["Gate 11 confirmed", "520 tests pass"],
            "result": "VERIFIED",
        },
        "contradictions_found": [],
        "repairs_performed": [],
        "final_verdict": "PASS_VERIFIED",
        "verdict_reason": "All FODT commercial records verified. Gate 11 approved. 520 tests pass.",
    },
    {
        "pilot_id": "CAP-PILOT-C003",
        "format": "Netpbm",
        "product_type": "commercial",
        "authority_inputs": [
            "product-capability-matrix/poc-targets.yaml (commercial_net_products.Netpbm)",
            "Gate 11 G11-G approval by Babar Raza 2026-06-05",
        ],
        "source_files_inspected": ["src/net/netpbm/"],
        "tests_inspected": 50,
        "examples_inspected": "examples/net/netpbm/ (3 files)",
        "generated_capability_records": {
            "count": 25,
            "sample": "load, save_same_format, parse_pbm, parse_pgm, parse_ppm",
        },
        "generated_gap_entries": {"count": 0, "summary": "All expected capabilities implemented"},
        "taskcards_created_or_updated": [],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 465, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/net/netpbm/"],
            "key_checks": ["Gate 11 confirmed", "465 tests pass"],
            "result": "VERIFIED",
        },
        "contradictions_found": [
            "LIMITATION: poc-targets.yaml Netpbm Python FOSS split into pbm/pgm/ppm packages"
        ],
        "repairs_performed": [
            "capability_map_generator.py: impl_refs omitted when src dir absent"
        ],
        "final_verdict": "PASS_WITH_LIMITATIONS",
        "verdict_reason": "Commercial Netpbm verified at Gate 11. Python FOSS naming limitation documented.",
    },
    {
        "pilot_id": "CAP-PILOT-F001",
        "format": "ABW",
        "product_type": "foss_reduced",
        "authority_inputs": [
            "product-capability-matrix/poc-targets.yaml (foss_reduced_products.ABW)",
            "acquisition-packs/abw/pack.yaml",
        ],
        "source_files_inspected": ["src/python/abw/abw_codec.py"],
        "tests_inspected": 10,
        "examples_inspected": "None",
        "generated_capability_records": {
            "count": 22,
            "sample": "load, probe_abw, extract_text, export_to_txt, export_to_csv, export_to_json, write_abw, create_abw, edit_paragraph",
        },
        "generated_gap_entries": {"count": 0, "summary": "All expected capabilities present"},
        "taskcards_created_or_updated": [],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 189, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/python/abw/abw_codec.py"],
            "key_checks": ["18 public functions", "10 test files", "189 tests pass"],
            "result": "VERIFIED",
        },
        "contradictions_found": [],
        "repairs_performed": [],
        "final_verdict": "PASS_VERIFIED",
        "verdict_reason": "ABW FOSS fully implemented. 18 functions, 10 test files, 189 tests passing.",
    },
    {
        "pilot_id": "CAP-PILOT-F002",
        "format": "Gnumeric",
        "product_type": "foss_reduced",
        "authority_inputs": [
            "product-capability-matrix/poc-targets.yaml (foss_reduced_products.Gnumeric)",
            "acquisition-packs/gnumeric/pack.yaml",
        ],
        "source_files_inspected": ["src/python/gnumeric/gnumeric_codec.py"],
        "tests_inspected": 7,
        "examples_inspected": "None",
        "generated_capability_records": {
            "count": 23,
            "sample": "load, probe_gnumeric, create_gnumeric, write_gnumeric, export_to_csv, export_to_json, get_sheet_names, get_cell_value, set_cell_value",
        },
        "generated_gap_entries": {"count": 0, "summary": "All expected capabilities present"},
        "taskcards_created_or_updated": ["CAP-PROD-004"],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 189, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/python/gnumeric/gnumeric_codec.py"],
            "key_checks": ["set_cell_value present at lines 223-257", "17 public functions", "7 test files"],
            "result": "VERIFIED — DEC-001: set_cell_value was already present",
        },
        "contradictions_found": ["Plan said set_cell_value needed implementing - already present since R123"],
        "repairs_performed": ["plan-healing-decision-log.json DEC-001: corrected stale assumption"],
        "final_verdict": "PASS_VERIFIED",
        "verdict_reason": "Gnumeric FOSS fully implemented. set_cell_value already present (DEC-001). 189 tests pass.",
    },
    {
        "pilot_id": "CAP-PILOT-F003",
        "format": "NDJSON",
        "product_type": "foss_reduced",
        "authority_inputs": [
            "reports/capability-layer/foss-reduced-capability-map.json (source scan discovery)",
        ],
        "source_files_inspected": ["src/python/ndjson/ndjson_codec.py"],
        "tests_inspected": 4,
        "examples_inspected": "None",
        "generated_capability_records": {
            "count": 12,
            "sample": "load_ndjson, probe_ndjson, get_record_count, get_field_names, write_ndjson, append_record, filter_records, export_to_csv",
        },
        "generated_gap_entries": {"count": 1, "summary": "NDJSON not in poc-targets.yaml foss_reduced_products"},
        "taskcards_created_or_updated": ["CAP-PROD-005"],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 32, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/python/ndjson/ndjson_codec.py"],
            "key_checks": ["12 public functions", "4 test files", "NOT in poc-targets.yaml"],
            "result": "VERIFIED with limitation",
        },
        "contradictions_found": ["NDJSON not in poc-targets.yaml foss_reduced_products despite being implemented"],
        "repairs_performed": [],
        "final_verdict": "PASS_WITH_LIMITATIONS",
        "verdict_reason": "NDJSON FOSS implemented with 12 functions, 4 test files. poc-targets.yaml needs updating (CAP-PROD-005).",
    },
    {
        "pilot_id": "CAP-PILOT-E001",
        "format": "FODG",
        "product_type": "foss_reduced",
        "authority_inputs": [
            "tests/python/fodg/test_cap_fodg_write_export.py (22 tests PASS)",
            "reports/capability-layer/foss-reduced-capability-map.json",
        ],
        "source_files_inspected": ["src/python/fodg/fodg_codec.py"],
        "tests_inspected": 3,
        "examples_inspected": "None",
        "generated_capability_records": {
            "count": 10,
            "sample": "load, probe_fodg, get_page_count, create_fodg (new), write_fodg (new), export_to_txt (new)",
        },
        "generated_gap_entries": {"count": 0, "summary": "write_fodg and export_to_txt now implemented"},
        "taskcards_created_or_updated": ["CAP-PROD-002", "CAP-PROD-003", "CAP-PROD-006"],
        "validator_result": {"exit_code": 2, "summary": "PASS advisory warnings only"},
        "test_result": {"pass_count": 22, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": ["src/python/fodg/fodg_codec.py", "tests/python/fodg/test_cap_fodg_write_export.py"],
            "key_checks": [
                "create_fodg() builds valid model",
                "write_fodg() serializes to valid XML",
                "export_to_txt() returns formatted string",
                "roundtrip probe and load verified",
                "22/22 tests pass",
            ],
            "result": "VERIFIED",
        },
        "contradictions_found": [],
        "repairs_performed": [
            "Added create_fodg() to fodg_codec.py",
            "Added write_fodg() to fodg_codec.py",
            "Added export_to_txt() to fodg_codec.py",
            "Updated __init__.py exports",
            "Added ledger entry FODG-CREATE-WRITE-EXPORT-CAP-001",
        ],
        "final_verdict": "PASS_VERIFIED",
        "verdict_reason": "FODG feature expansion complete. create_fodg, write_fodg, export_to_txt added and tested. 22/22 pass.",
    },
    {
        "pilot_id": "CAP-PILOT-A001",
        "format": "TOML",
        "product_type": "foss_reduced",
        "authority_inputs": [
            "TOML selected as new acquisition candidate (no gates passed yet)",
            "Python 3.11+ stdlib: tomllib (read-only)",
        ],
        "source_files_inspected": [],
        "tests_inspected": 0,
        "examples_inspected": "None",
        "generated_capability_records": {"count": 0, "sample": "No records yet"},
        "generated_gap_entries": {"count": 1, "summary": "Format not in poc-targets.yaml, no src/ implementation"},
        "taskcards_created_or_updated": [],
        "validator_result": {"exit_code": 2, "summary": "Not applicable"},
        "test_result": {"pass_count": 0, "fail_count": 0, "log_path": ""},
        "manual_agent_verification_result": {
            "artifacts_opened": [],
            "key_checks": [
                "TOML not in src/python/ (no acquisition started)",
                "TOML not in acquisition-packs/",
                "Python stdlib tomllib available (3.11+) read-only",
                "Write requires tomli-w (PyPI)",
                "Gates 1-7 not run",
            ],
            "result": "NOT_STARTED",
        },
        "contradictions_found": [],
        "repairs_performed": [],
        "final_verdict": "NOT_ENOUGH_AUTHORITY_DATA",
        "verdict_reason": "TOML acquisition not started. Requires gates 1-7 before any source work. Good candidate for next acquisition sprint.",
    },
]

for pilot in PILOTS:
    write_pilot(pilot["pilot_id"], pilot)

print(f"Written {len(PILOTS)} pilot reports to {PILOTS_DIR}")
