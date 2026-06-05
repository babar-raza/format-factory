"""Update product code ledger with MWP-DOGFOOD-UNBLOCKING sprint entries."""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

SPRINT = "FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001"

new_entries = [
    {
        "entry_id": "MWP-CSV-WRITER-LIBRARY",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FormatFactory.Csv .NET",
        "capability_refs": ["commercial_net_products.FODS.dogfood_status.fods_to_csv_dotnet"],
        "api_symbols": ["CsvWriter.WriteRows", "CsvWriter.WriteRowsToFile", "CsvWriter.EscapeField"],
        "api_behavior": (
            "Standalone .NET CSV target writer library. WriteRows: RFC4180 CSV string (LF). "
            "WriteRowsToFile: UTF-8 no-BOM. EscapeField: wraps in quotes when field contains comma, quote, or newline."
        ),
        "changed_files": ["src/net/csv/CsvWriter.cs", "src/net/csv/FormatFactory.Csv.csproj"],
        "test_files": ["tests/net/csv/CsvWriterTests.cs"],
        "test_count": 15,
        "validation_command": "dotnet test tests/net/csv/FormatFactory.Csv.Tests.csproj -v quiet",
        "validation_result": "15/15 PASS",
        "rollback": "Remove src/net/csv/ and restore FodsCsvExporter.cs inline serialization",
        "source_files": [{"path": "src/net/csv/CsvWriter.cs", "state": "present",
                          "sha256": "3ba05f7c6ba4c373f0075a086db4b3110c5f1fcbdf3e5740751ec75df4f35092"}],
        "skill_id": "add-same-format-writer-feature",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
    },
    {
        "entry_id": "MWP-HTML-WRITER-LIBRARY",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FormatFactory.Html .NET",
        "capability_refs": ["commercial_net_products.FODS.dogfood_status.fods_to_html_dotnet"],
        "api_symbols": ["HtmlWriter.WriteTable", "HtmlWriter.WriteTableToFile", "HtmlWriter.EscapeHtml"],
        "api_behavior": (
            "Standalone .NET HTML target writer library. WriteTable: HTML5 table string. "
            "WriteTableToFile: full HTML5 document, UTF-8 no-BOM. EscapeHtml: delegates to WebUtility.HtmlEncode."
        ),
        "changed_files": ["src/net/html/HtmlWriter.cs", "src/net/html/FormatFactory.Html.csproj"],
        "test_files": ["tests/net/html/HtmlWriterTests.cs"],
        "test_count": 12,
        "validation_command": "dotnet test tests/net/html/FormatFactory.Html.Tests.csproj -v quiet",
        "validation_result": "12/12 PASS",
        "rollback": "Remove src/net/html/ and restore FodsHtmlExporter.cs inline serialization",
        "source_files": [{"path": "src/net/html/HtmlWriter.cs", "state": "present",
                          "sha256": "25f566b0b6569b8af2c7c30199d9fced74184f4662aa64bb780dd5274e31a370"}],
        "skill_id": "add-same-format-writer-feature",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
    },
    {
        "entry_id": "MWP-TXT-WRITER-LIBRARY",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FormatFactory.Txt .NET",
        "capability_refs": ["commercial_net_products.FODT.dogfood_status.fodt_to_txt_dotnet"],
        "api_symbols": ["TxtWriter.WriteLines", "TxtWriter.WriteLinesToFile"],
        "api_behavior": (
            "Standalone .NET TXT target writer library. WriteLines: joins with LF, normalises CRLF. "
            "WriteLinesToFile: UTF-8 no-BOM."
        ),
        "changed_files": ["src/net/txt/TxtWriter.cs", "src/net/txt/FormatFactory.Txt.csproj"],
        "test_files": ["tests/net/txt/TxtWriterTests.cs"],
        "test_count": 8,
        "validation_command": "dotnet test tests/net/txt/FormatFactory.Txt.Tests.csproj -v quiet",
        "validation_result": "8/8 PASS",
        "rollback": "Remove src/net/txt/ and restore FodtTxtExporter.cs inline serialization",
        "source_files": [{"path": "src/net/txt/TxtWriter.cs", "state": "present",
                          "sha256": "822057f4069e2f049c80daa47798d03a909460bda6f5cb917c85d9135f4ae31e"}],
        "skill_id": "add-same-format-writer-feature",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
    },
    {
        "entry_id": "MWP-MARKDOWN-WRITER-LIBRARY",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FormatFactory.Markdown .NET",
        "capability_refs": ["commercial_net_products.FODT.dogfood_status.fodt_to_markdown_dotnet"],
        "api_symbols": ["MarkdownWriter.WriteHeading", "MarkdownWriter.WriteParagraphs", "MarkdownWriter.WriteLinesToFile"],
        "api_behavior": (
            "Standalone .NET Markdown target writer library. WriteHeading: ATX-style, clamps [1,6]. "
            "WriteParagraphs: blank-line-separated. WriteLinesToFile: UTF-8 no-BOM."
        ),
        "changed_files": ["src/net/markdown/MarkdownWriter.cs", "src/net/markdown/FormatFactory.Markdown.csproj"],
        "test_files": ["tests/net/markdown/MarkdownWriterTests.cs"],
        "test_count": 11,
        "validation_command": "dotnet test tests/net/markdown/FormatFactory.Markdown.Tests.csproj -v quiet",
        "validation_result": "11/11 PASS",
        "rollback": "Remove src/net/markdown/ and restore FodtMarkdownExporter.cs inline serialization",
        "source_files": [{"path": "src/net/markdown/MarkdownWriter.cs", "state": "present",
                          "sha256": "0bdf47acc5bff20939aa05a45b2e055779cd045a31d5805bd7a747607e9471a8"}],
        "skill_id": "add-same-format-writer-feature",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
    },
    {
        "entry_id": "MWP-FODS-CSV-DOGFOOD-REFACTOR",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FODS .NET",
        "capability_refs": ["commercial_net_products.FODS.dogfood_status.fods_to_csv_dotnet"],
        "api_symbols": ["FodsCsvExporter.ExportSheetToCsv", "FodsCsvExporter.ExportSheetToCsvString", "FodsCsvExporter.EscapeCsvField"],
        "api_behavior": (
            "FodsCsvExporter delegates CSV serialization to FormatFactory.Csv.CsvWriter. "
            "dogfood_status: GAP_DOGFOOD_EXTERNAL -> IMPLEMENTED. Zero regressions in 547 FODS tests."
        ),
        "changed_files": ["src/net/fods/FodsCsvExporter.cs", "src/net/fods/FormatFactory.Fods.csproj"],
        "test_files": ["tests/net/fods/FodsR104DogfoodCsvExportTests.cs"],
        "test_count": 547,
        "validation_command": "dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj -v quiet",
        "validation_result": "547/547 PASS",
        "rollback": "Revert FodsCsvExporter.cs to inline CSV, remove ProjectReference to FormatFactory.Csv",
        "source_files": [{"path": "src/net/fods/FodsCsvExporter.cs", "state": "present",
                          "sha256": "3d1c294eca93495221c9bd81545f922e4c7ef3066c7b063e6a6e0d9ef8fbf703"}],
        "skill_id": "add-dogfood-export",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
    },
    {
        "entry_id": "MWP-FODS-HTML-DOGFOOD-REFACTOR",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FODS .NET",
        "capability_refs": ["commercial_net_products.FODS.dogfood_status.fods_to_html_dotnet"],
        "api_symbols": ["FodsHtmlExporter.ExportToHtml", "FodsHtmlExporter.HtmlEscape"],
        "api_behavior": (
            "FodsHtmlExporter delegates HTML table serialization to FormatFactory.Html.HtmlWriter. "
            "dogfood_status: GAP_DOGFOOD_EXTERNAL -> IMPLEMENTED. Zero regressions."
        ),
        "changed_files": ["src/net/fods/FodsHtmlExporter.cs"],
        "test_files": ["tests/net/fods/FodsR94ExportSheetToHtmlTests.cs"],
        "test_count": 547,
        "validation_command": "dotnet test tests/net/fods/FormatFactory.Fods.Tests.csproj -v quiet",
        "validation_result": "547/547 PASS",
        "rollback": "Revert FodsHtmlExporter.cs to inline HTML, remove ProjectReference to FormatFactory.Html",
        "source_files": [{"path": "src/net/fods/FodsHtmlExporter.cs", "state": "present",
                          "sha256": "1098a6b3356e00fc24300346fc634c31cb31b4aa4b94520ddd82776304f02ec4"}],
        "skill_id": "add-dogfood-export",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
    },
    {
        "entry_id": "MWP-FODT-TXT-DOGFOOD-REFACTOR",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FODT .NET",
        "capability_refs": ["commercial_net_products.FODT.dogfood_status.fodt_to_txt_dotnet"],
        "api_symbols": ["FodtTxtExporter.ExportTxt", "FodtTxtExporter.ExportToTxt"],
        "api_behavior": (
            "FodtTxtExporter delegates plaintext output to FormatFactory.Txt.TxtWriter. "
            "dogfood_status: GAP_DOGFOOD_EXTERNAL -> IMPLEMENTED. Zero regressions in 520 FODT tests."
        ),
        "changed_files": ["src/net/fodt/FodtTxtExporter.cs", "src/net/fodt/FormatFactory.Fodt.csproj"],
        "test_files": ["tests/net/fodt/FodtR107DogfoodPlainTextExportTests.cs"],
        "test_count": 520,
        "validation_command": "dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj -v quiet",
        "validation_result": "520/520 PASS",
        "rollback": "Revert FodtTxtExporter.cs to inline TXT, remove ProjectReference to FormatFactory.Txt",
        "source_files": [{"path": "src/net/fodt/FodtTxtExporter.cs", "state": "present",
                          "sha256": "77230854787da1d2367a5ab132d43946354ad3cb686e474470d5a43e4692db37"}],
        "skill_id": "add-dogfood-export",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
    },
    {
        "entry_id": "MWP-FODT-MARKDOWN-DOGFOOD-REFACTOR",
        "sprint_id": SPRINT,
        "classification": "GOVERNED_PRODUCT_CHANGE",
        "product": "FODT .NET",
        "capability_refs": ["commercial_net_products.FODT.dogfood_status.fodt_to_markdown_dotnet"],
        "api_symbols": ["FodtMarkdownExporter.ExportToMarkdown", "FodtMarkdownExporter.FormatParagraphAsMarkdown"],
        "api_behavior": (
            "FodtMarkdownExporter delegates heading formatting and file output to FormatFactory.Markdown.MarkdownWriter. "
            "dogfood_status: GAP_DOGFOOD_EXTERNAL -> IMPLEMENTED. Zero regressions."
        ),
        "changed_files": ["src/net/fodt/FodtMarkdownExporter.cs"],
        "test_files": ["tests/net/fodt/FodtR108DogfoodMarkdownExportTests.cs"],
        "test_count": 520,
        "validation_command": "dotnet test tests/net/fodt/FormatFactory.Fodt.Tests.csproj -v quiet",
        "validation_result": "520/520 PASS",
        "rollback": "Revert FodtMarkdownExporter.cs to inline Markdown, remove ProjectReference to FormatFactory.Markdown",
        "source_files": [{"path": "src/net/fodt/FodtMarkdownExporter.cs", "state": "present",
                          "sha256": "6d7969b8d4ff693dece79eba7837730a21344207fec9f0cea84174b25a8bcfd1"}],
        "skill_id": "add-dogfood-export",
        "raw_log": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/product-dogfood-tests.log",
    },
]

ledger["entries"].extend(new_entries)
ledger["latest_sprint"] = SPRINT

ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
print(f"Ledger updated: {len(ledger['entries'])} total entries (was 121, added 8)")
