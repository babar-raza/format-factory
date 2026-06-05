"""Patch ledger entries to add csproj source_files that the validator detects as changed."""
import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
ledger = json.loads(ledger_path.read_text(encoding="utf-8"))

# Map: csproj path -> entry_id that should carry it
CSPROJ_TO_ENTRY = {
    "src/net/csv/FormatFactory.Csv.csproj":        ("MWP-CSV-WRITER-LIBRARY",        "a27781f20f0feac0b16e6ec86dc77a2402138fc7ca32668d294601287a6d37b2"),
    "src/net/fods/FormatFactory.Fods.csproj":      ("MWP-FODS-CSV-DOGFOOD-REFACTOR", "32dd10dc4740d40687c3ac939da47d52e44def0b82f60b892204979f242b6803"),
    "src/net/fodt/FormatFactory.Fodt.csproj":      ("MWP-FODT-TXT-DOGFOOD-REFACTOR", "622e7a52e9eadd92af50619f1007778dd0be65fccb059d2f830cf38476d901dd"),
    "src/net/html/FormatFactory.Html.csproj":      ("MWP-HTML-WRITER-LIBRARY",       "8addf61e0061be92fc18354f48cb9e5340128aa19883ad3283e9634664738e7c"),
    "src/net/markdown/FormatFactory.Markdown.csproj": ("MWP-MARKDOWN-WRITER-LIBRARY","3ce5c347de8b7e372976872bb68a49d1d9f2698eec762668efb3d9993048d1c0"),
    "src/net/txt/FormatFactory.Txt.csproj":        ("MWP-TXT-WRITER-LIBRARY",        "1fe8058a520ef7ab931da068e97d84265df48b87a7d765aa35f84df494b7f6ad"),
}

# Index entries by entry_id
entry_by_id = {e["entry_id"]: e for e in ledger["entries"]}

for csproj_path, (entry_id, sha) in CSPROJ_TO_ENTRY.items():
    entry = entry_by_id.get(entry_id)
    if entry is None:
        print(f"WARNING: entry {entry_id} not found")
        continue
    # Add csproj to source_files if not already present
    existing_paths = [s["path"] for s in entry.get("source_files", [])]
    if csproj_path not in existing_paths:
        entry.setdefault("source_files", []).append({
            "path": csproj_path,
            "state": "present",
            "sha256": sha,
        })
        print(f"  Added {csproj_path} -> {entry_id}")
    else:
        print(f"  Already present: {csproj_path}")

ledger_path.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
print("Ledger patched.")
