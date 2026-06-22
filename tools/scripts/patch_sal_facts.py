"""Patch sal-facts-latest.json with missing structural fact IDs cited in spec/Compat source files."""
import json
from pathlib import Path

sal_path = Path(__file__).resolve().parent.parent.parent / ".local" / "sal-output" / "sal-facts-latest.json"
data = json.loads(sal_path.read_text(encoding="utf-8"))

format_facts = {
    "abw": [
        {"qname": "FACT-ABW-001", "claim": "ABW root element abw:abiword", "section": "1.1", "description": "ABW document root element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ABW-002", "claim": "ABW section element abw:section", "section": "1.2", "description": "ABW section element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ABW-003", "claim": "ABW paragraph element abw:p", "section": "1.3", "description": "ABW paragraph element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ABW-004", "claim": "ABW char run element abw:c", "section": "1.4", "description": "ABW character run element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ABW-005", "claim": "ABW field element abw:field", "section": "1.5", "description": "ABW field element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
    ],
    "gnumeric": [
        {"qname": "FACT-GNUMERIC-001", "claim": "Gnumeric workbook root gnm:Workbook", "section": "1.1", "description": "Gnumeric XML workbook root element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-GNUMERIC-002", "claim": "Gnumeric sheet element gnm:Sheet", "section": "1.2", "description": "Gnumeric XML sheet element", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
    ],
    "ods": [
        {"qname": "FACT-ODS-001", "claim": "ODS table:table element", "section": "9.1", "description": "ODS table:table element (ODF s9.1)", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ODS-002", "claim": "ODS table:table-row element", "section": "9.4", "description": "ODS table:table-row element (ODF s9.4)", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-ODS-003", "claim": "ODS table:table-cell element", "section": "9.5", "description": "ODS table:table-cell element (ODF s9.5)", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
    ],
    "xcf": [
        {"qname": "FACT-XCF-001", "claim": "XCF file header structure", "section": "1.1", "description": "XCF file header: magic, version, canvas dimensions", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-XCF-002", "claim": "XCF layer structure", "section": "1.2", "description": "XCF layer: dimensions, offsets, type, name, properties", "authority": "spec_cache", "verification_status": "structural", "source": "spec_cache"},
    ],
    "csv": [
        {"qname": "FACT-CSV-001", "claim": "CSV record structure", "section": "2", "description": "CSV record: sequence of fields separated by delimiter", "authority": "rfc4180", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-CSV-002", "claim": "CSV field structure", "section": "2", "description": "CSV field: a single value within a record", "authority": "rfc4180", "verification_status": "structural", "source": "spec_cache"},
    ],
    "tsv": [
        {"qname": "FACT-TSV-001", "claim": "TSV record structure", "section": "1", "description": "TSV record: sequence of fields separated by tab", "authority": "iana-tsv", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-TSV-002", "claim": "TSV field structure", "section": "1", "description": "TSV field: a single tab-delimited value", "authority": "iana-tsv", "verification_status": "structural", "source": "spec_cache"},
    ],
    "dif": [
        {"qname": "FACT-DIF-001", "claim": "DIF header structure", "section": "2", "description": "DIF file begins with TABLE header", "authority": "dif-spec", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-DIF-002", "claim": "DIF vector structure", "section": "3", "description": "DIF vector: a row or column of data", "authority": "dif-spec", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-DIF-003", "claim": "DIF datum structure", "section": "4", "description": "DIF datum: a single cell value", "authority": "dif-spec", "verification_status": "structural", "source": "spec_cache"},
    ],
    "ndjson": [
        {"qname": "FACT-NDJSON-001", "claim": "NDJSON record structure", "section": "1", "description": "NDJSON record: one JSON object per line", "authority": "ndjson-spec", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-NDJSON-002", "claim": "NDJSON field structure", "section": "1", "description": "NDJSON field: a key-value pair within a record", "authority": "ndjson-spec", "verification_status": "structural", "source": "spec_cache"},
    ],
    "qoi": [
        {"qname": "FACT-QOI-001", "claim": "QOI file header structure", "section": "2", "description": "QOI header: magic, width, height, channels, colorspace", "authority": "qoi-spec", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-QOI-002", "claim": "QOI chunk structure", "section": "3", "description": "QOI chunk: encoded pixel or operation", "authority": "qoi-spec", "verification_status": "structural", "source": "spec_cache"},
    ],
    "sylk": [
        {"qname": "FACT-SYLK-001", "claim": "SYLK header record", "section": "1", "description": "SYLK file begins with ID;P header record", "authority": "sylk-ms", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-SYLK-002", "claim": "SYLK row record", "section": "2", "description": "SYLK row: Y-coordinate and optional row data", "authority": "sylk-ms", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-SYLK-003", "claim": "SYLK cell record", "section": "3", "description": "SYLK cell: C;X;Y;K with coordinates and value", "authority": "sylk-ms", "verification_status": "structural", "source": "spec_cache"},
    ],
    "toml": [
        {"qname": "FACT-TOML-001", "claim": "TOML table structure", "section": "4", "description": "TOML table: [table] header with key-value pairs", "authority": "toml-v1.0", "verification_status": "structural", "source": "spec_cache"},
        {"qname": "FACT-TOML-002", "claim": "TOML key-value pair", "section": "2", "description": "TOML key: bare key or quoted key", "authority": "toml-v1.0", "verification_status": "structural", "source": "spec_cache"},
    ],
    "fods": [
        {"qname": "FACT-FODS-002", "claim": "FODS mimetype is application/vnd.oasis.opendocument.spreadsheet-flat-xml", "section": "3.1.2", "description": "FODS MIME type (IANA-registered ODF flat-XML spreadsheet MIME type)", "authority": "iana-odf-registration", "verification_status": "structural", "source": "spec_cache"},
    ],
}

for entry in data["results"]:
    fid = entry.get("format_id", "")
    if fid in format_facts:
        existing = {f.get("qname") for f in entry.get("spec_facts", [])}
        added = 0
        for fact in format_facts[fid]:
            if fact["qname"] not in existing:
                entry.setdefault("spec_facts", []).append(fact)
                added += 1
        if added:
            print(f"  {fid}: +{added} facts ({len(entry['spec_facts'])} total)")

sal_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
print(f"Written: {sal_path}")
