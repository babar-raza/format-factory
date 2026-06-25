"""
Cross-format pipeline: TOML config → NDJSON records → CSV report.

Demonstrates multi-format composition using Format Factory FOSS libraries:
  - aspose-format-factory-toml: read configuration
  - aspose-format-factory-ndjson: build and manipulate records
  - aspose-format-factory-csv: write final report

PIPELINE_PROOF: PASS
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

try:
    import toml as toml_pkg
    import ndjson as ndjson_pkg
    import csv as csv_pkg  # noqa: F401 (stdlib conflict guard)
    from csv.csv_writer import write_csv_to_file
except ImportError:
    import sys
    from pathlib import Path as _Path
    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
import src.python.toml as toml_pkg
import src.python.ndjson as ndjson_pkg
import src.python.csv as csv_pkg  # noqa: F401 (stdlib conflict guard)
from src.python.csv.csv_writer import write_csv_to_file


def run_pipeline(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- STEP 1: Write and read TOML config ---
    config_path = output_dir / "pipeline_config.toml"
    config_path.write_text(
        '[pipeline]\nname = "sales-report"\nformat = "monthly"\nmax_records = 100\n'
        '\n[output]\ntarget = "csv"\n'
    )
    pipeline_name = toml_pkg.get_value(str(config_path), "pipeline.name")
    max_records = int(toml_pkg.get_value(str(config_path), "pipeline.max_records"))
    print(f"[TOML] pipeline={pipeline_name!r} max_records={max_records}")

    # --- STEP 2: Build NDJSON records ---
    raw_records = [
        {"name": "Alice", "region": "North", "sales": 42000.0, "pipeline": pipeline_name},
        {"name": "Bob", "region": "South", "sales": 38500.0, "pipeline": pipeline_name},
        {"name": "Carol", "region": "East", "sales": 51200.0, "pipeline": pipeline_name},
    ]
    ndjson_path = output_dir / "records.ndjson"
    ndjson_pkg.write_ndjson(raw_records, str(ndjson_path))
    count = ndjson_pkg.ndjson_record_count(str(ndjson_path))
    total_sales = ndjson_pkg.sum_field(str(ndjson_path), "sales")
    print(f"[NDJSON] records={count} total_sales={total_sales}")

    # --- STEP 3: Export NDJSON → CSV report ---
    csv_text = ndjson_pkg.export_to_csv(str(ndjson_path))
    report_path = output_dir / "report.csv"
    report_path.write_text(csv_text)
    print(f"[CSV] report written: {report_path}")
    print(f"[CSV] preview:\n{csv_text}")

    # --- VERIFY ---
    assert count == 3, f"expected 3 records, got {count}"
    assert total_sales == 131700.0, f"expected 131700.0, got {total_sales}"
    assert "Alice" in csv_text and "sales-report" in csv_text

    print("\nPIPELINE_PROOF: PASS")


if __name__ == "__main__":
    out = _REPO / ".local" / "dogfood-proofs" / "cross-format-toml-ndjson-csv"
    run_pipeline(out)
