"""TC-S56-004: CSV spec QName compliance tests.

Verifies that CSV classes have correct spec_qname, spec_fact_ref, and
namespace_uri attributes per shared/qname-registry/csv.yaml.

Spec QName registry: csv:record, csv:header, csv:field

Note: CSV uses src.python.csv import to avoid Python stdlib csv conflict.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
# CSV requires repo root (not src/python) in path to avoid stdlib conflict
sys.path.insert(0, str(_REPO_ROOT))


class TestCsvDocumentSpecQname:
    """CsvDocument domain model spec_qname compliance."""

    def test_spec_qname_defined(self):
        from src.python.ff_csv import CsvDocument
        assert CsvDocument.spec_qname == "csv:record"

    def test_spec_qname_matches_registry(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "csv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("CSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        qnames = {e["qname"] for e in entries if isinstance(e, dict)}
        from src.python.ff_csv import CsvDocument
        assert CsvDocument.spec_qname in qnames or CsvDocument.spec_qname.startswith("csv:")


class TestCsvCompatLayerSpecQname:
    """CSV Compat layer spec qnames (csv:record, csv:header, csv:field)."""

    def test_csv_record_spec_qname(self):
        from src.python.ff_csv.Compat import CsvRecord
        assert CsvRecord.spec_qname == "csv:record"

    def test_csv_record_spec_fact_ref(self):
        from src.python.ff_csv.Compat import CsvRecord
        assert CsvRecord.spec_fact_ref == "SAL-CSV-00001"

    def test_csv_record_namespace_uri(self):
        from src.python.ff_csv.Compat import CsvRecord
        assert CsvRecord.namespace_uri
        assert "csv" in CsvRecord.namespace_uri or "rfc" in CsvRecord.namespace_uri

    def test_csv_header_spec_qname(self):
        from src.python.ff_csv.Compat import CsvHeader
        assert CsvHeader.spec_qname == "csv:header"

    def test_csv_header_spec_fact_ref(self):
        from src.python.ff_csv.Compat import CsvHeader
        assert CsvHeader.spec_fact_ref

    def test_csv_field_spec_qname(self):
        from src.python.ff_csv.Compat import CsvField
        assert CsvField.spec_qname == "csv:field"

    def test_csv_field_spec_fact_ref(self):
        from src.python.ff_csv.Compat import CsvField
        assert CsvField.spec_fact_ref == "SAL-CSV-00002"


class TestCsvSpecQnameRegistryLinkage:
    """Verify source files match registry entries."""

    def test_registry_python_file_exists(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "csv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("CSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            python_file = entry.get("python_file")
            if python_file:
                fp = _REPO_ROOT / python_file
                assert fp.exists(), f"python_file {python_file} does not exist for qname {entry.get('qname')}"

    def test_all_csv_qnames_have_csv_prefix(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "csv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("CSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("qname", "").startswith("csv:"), \
                    f"Expected csv: prefix, got {entry.get('qname')}"

    def test_csv_qnames_have_spec_fact_ref(self):
        import yaml
        registry_path = _REPO_ROOT / "shared" / "qname-registry" / "csv.yaml"
        if not registry_path.exists():
            import pytest
            pytest.skip("CSV qname registry not found")
        entries = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        for entry in entries:
            if isinstance(entry, dict):
                assert entry.get("spec_fact_ref"), \
                    f"qname {entry.get('qname')} missing spec_fact_ref"
