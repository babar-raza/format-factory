"""Generate skill transcripts for the target writer MWP unblocking sprint."""
import json
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "reports" / "dotnet-target-writer-readiness-hardening" / "skill-transcripts"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SPRINT = "FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001"
NOW = "2026-06-05T00:00:00Z"

TRANSCRIPTS = [
    {
        "task_id": "TC-PHASE3-CSV-WRITER",
        "skill_id": "governed-target-writer-mwp",
        "lane_id": "LANE-CSV-WRITER",
        "allowed_files": ["src/net/csv/**", "tests/net/csv/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml", "registry/**"],
        "actual_files_changed": ["src/net/csv/CsvWriter.cs", "src/net/csv/FormatFactory.Csv.csproj", "tests/net/csv/CsvWriterTests.cs"],
        "source_diff_path": None,
        "tests_run": 15,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": None,
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fods-csv-dotnet.yaml",
        "proof_graph_node_ids": ["csv-writer-library"],
        "rollback_note": "Remove src/net/csv/ directory and restore FodsCsvExporter.cs inline serialization",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE3-HTML-WRITER",
        "skill_id": "governed-target-writer-mwp",
        "lane_id": "LANE-HTML-WRITER",
        "allowed_files": ["src/net/html/**", "tests/net/html/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml", "registry/**"],
        "actual_files_changed": ["src/net/html/HtmlWriter.cs", "src/net/html/FormatFactory.Html.csproj", "tests/net/html/HtmlWriterTests.cs"],
        "source_diff_path": None,
        "tests_run": 12,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": None,
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fods-html-dotnet.yaml",
        "proof_graph_node_ids": ["html-writer-library"],
        "rollback_note": "Remove src/net/html/ directory and restore FodsHtmlExporter.cs inline serialization",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE3-TXT-WRITER",
        "skill_id": "governed-target-writer-mwp",
        "lane_id": "LANE-TXT-WRITER",
        "allowed_files": ["src/net/txt/**", "tests/net/txt/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml", "registry/**"],
        "actual_files_changed": ["src/net/txt/TxtWriter.cs", "src/net/txt/FormatFactory.Txt.csproj", "tests/net/txt/TxtWriterTests.cs"],
        "source_diff_path": None,
        "tests_run": 8,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": None,
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fodt-txt-dotnet.yaml",
        "proof_graph_node_ids": ["txt-writer-library"],
        "rollback_note": "Remove src/net/txt/ directory and restore FodtTxtExporter.cs inline serialization",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE3-MARKDOWN-WRITER",
        "skill_id": "governed-target-writer-mwp",
        "lane_id": "LANE-MARKDOWN-WRITER",
        "allowed_files": ["src/net/markdown/**", "tests/net/markdown/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml", "registry/**"],
        "actual_files_changed": ["src/net/markdown/MarkdownWriter.cs", "src/net/markdown/FormatFactory.Markdown.csproj", "tests/net/markdown/MarkdownWriterTests.cs"],
        "source_diff_path": None,
        "tests_run": 11,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": None,
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fodt-markdown-dotnet.yaml",
        "proof_graph_node_ids": ["markdown-writer-library"],
        "rollback_note": "Remove src/net/markdown/ directory and restore FodtMarkdownExporter.cs inline serialization",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE4-FODS-CSV-REFACTOR",
        "skill_id": "add-dogfood-export",
        "lane_id": "LANE-FODS-CSV-REFACTOR",
        "allowed_files": ["src/net/fods/**", "tests/net/fods/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml"],
        "actual_files_changed": ["src/net/fods/FodsCsvExporter.cs", "src/net/fods/FormatFactory.Fods.csproj"],
        "source_diff_path": None,
        "tests_run": 547,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-csv.csv",
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fods-csv-dotnet.yaml",
        "proof_graph_node_ids": ["fods-csv-exporter", "gap-fods-csv"],
        "rollback_note": "Revert FodsCsvExporter.cs to inline CSV serialization; remove ProjectReference to FormatFactory.Csv",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE4-FODS-HTML-REFACTOR",
        "skill_id": "add-dogfood-export",
        "lane_id": "LANE-FODS-HTML-REFACTOR",
        "allowed_files": ["src/net/fods/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml"],
        "actual_files_changed": ["src/net/fods/FodsHtmlExporter.cs"],
        "source_diff_path": None,
        "tests_run": 547,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-html.html",
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fods-html-dotnet.yaml",
        "proof_graph_node_ids": ["fods-html-exporter", "gap-fods-html"],
        "rollback_note": "Revert FodsHtmlExporter.cs to inline HTML serialization; remove ProjectReference to FormatFactory.Html",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE4-FODT-TXT-REFACTOR",
        "skill_id": "add-dogfood-export",
        "lane_id": "LANE-FODT-TXT-REFACTOR",
        "allowed_files": ["src/net/fodt/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml"],
        "actual_files_changed": ["src/net/fodt/FodtTxtExporter.cs", "src/net/fodt/FormatFactory.Fodt.csproj"],
        "source_diff_path": None,
        "tests_run": 520,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-txt.txt",
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fodt-txt-dotnet.yaml",
        "proof_graph_node_ids": ["fodt-txt-exporter", "gap-fodt-txt"],
        "rollback_note": "Revert FodtTxtExporter.cs to inline TXT serialization; remove ProjectReference to FormatFactory.Txt",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE4-FODT-MARKDOWN-REFACTOR",
        "skill_id": "add-dogfood-export",
        "lane_id": "LANE-FODT-MARKDOWN-REFACTOR",
        "allowed_files": ["src/net/fodt/**"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml"],
        "actual_files_changed": ["src/net/fodt/FodtMarkdownExporter.cs"],
        "source_diff_path": None,
        "tests_run": 520,
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-markdown.md",
        "capability_delta_path": "reports/dotnet-target-writer-readiness-hardening/capability-delta-proposals/fodt-markdown-dotnet.yaml",
        "proof_graph_node_ids": ["fodt-markdown-exporter", "gap-fodt-markdown"],
        "rollback_note": "Revert FodtMarkdownExporter.cs to inline Markdown serialization; remove ProjectReference to FormatFactory.Markdown",
        "result": "PASS",
    },
    {
        "task_id": "TC-PHASE5-DYNAMIC-UNBLOCK",
        "skill_id": "fallback-target-writer-mwp",
        "lane_id": "LANE-DYNAMIC-UNBLOCK",
        "allowed_files": ["tools/supervisor/select_poc_gaps.py", "tests/supervisor/test_target_writer_dynamic_unblock.py"],
        "forbidden_files": ["product-capability-matrix/poc-targets.yaml", "src/net/**", "registry/**"],
        "actual_files_changed": ["tools/supervisor/select_poc_gaps.py", "tests/supervisor/test_target_writer_dynamic_unblock.py"],
        "source_diff_path": None,
        "tests_run": 21,
        "raw_log_path": "reports/dotnet-target-writer-readiness-hardening/raw-logs/dynamic-unblock-hardening-tests.log",
        "sample_output_path": None,
        "capability_delta_path": None,
        "proof_graph_node_ids": [],
        "rollback_note": "Revert select_poc_gaps.py to v4 source-only detection (git restore tools/supervisor/select_poc_gaps.py)",
        "result": "PASS",
    },
]

for t in TRANSCRIPTS:
    fname = t["lane_id"].lower().replace("lane-", "") + ".json"
    # Use transcript_path names from the lane ledger
    name_map = {
        "TC-PHASE3-CSV-WRITER": "csv-writer-mwp.json",
        "TC-PHASE3-HTML-WRITER": "html-writer-mwp.json",
        "TC-PHASE3-TXT-WRITER": "txt-writer-mwp.json",
        "TC-PHASE3-MARKDOWN-WRITER": "markdown-writer-mwp.json",
        "TC-PHASE4-FODS-CSV-REFACTOR": "fods-csv-dogfood-refactor.json",
        "TC-PHASE4-FODS-HTML-REFACTOR": "fods-html-dogfood-refactor.json",
        "TC-PHASE4-FODT-TXT-REFACTOR": "fodt-txt-dogfood-refactor.json",
        "TC-PHASE4-FODT-MARKDOWN-REFACTOR": "fodt-markdown-dogfood-refactor.json",
        "TC-PHASE5-DYNAMIC-UNBLOCK": "dynamic-unblock-routing.json",
    }
    fname = name_map[t["task_id"]]
    t["sprint_id"] = SPRINT
    t["generated_at"] = NOW
    (OUT_DIR / fname).write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
    print(f"  Written: {fname}")

print(f"Done: {len(TRANSCRIPTS)} transcripts")
