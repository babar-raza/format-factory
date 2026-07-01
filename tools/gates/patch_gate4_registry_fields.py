"""Patch gate_4 registry blocks to add missing tests/corpus fields and fix status values.

Also reclassifies source-track-equivalent formats from EVIDENCE_WRAPPER to
SOURCE_TRACK_EQUIVALENT (these formats have full src/python/ implementations but
no dedicated prototype directory).
"""
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry" / "format-registry.yaml"

# ── Canonical prototype formats — add tests + corpus ──────────────────────────
STANDALONE_ADDITIONS = {
    "fods": {
        "tests": ["tests/skills/test_fods_gate4_prototype.py",
                  "tests/python/fods/test_fods_cli.py"],
        "corpus": ["samples/by-format/fods/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "Schema validation limited to root element check"],
    },
    "fodt": {
        "tests": ["tests/skills/test_fodt_gate4_prototype.py",
                  "tests/python/fodt/test_fodt_cli.py"],
        "corpus": ["samples/by-format/fodt/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "ODF namespace prefix handling only"],
    },
    "zst": {
        "tests": ["tests/skills/test_zst_gate4_prototype.py"],
        "corpus": ["samples/by-format/zst/"],
        "limitations": ["No decompression bomb guard (prototype only)",
                        "Window size not enforced",
                        "Gate 4 scope only — not for production pipelines"],
    },
    "fodp": {
        "tests": ["tests/skills/test_fodp_gate4_prototype.py"],
        "corpus": ["samples/by-format/fodp/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "ODF presentation namespace handling only"],
    },
    "fodg": {
        "tests": ["tests/skills/test_fodg_gate4_prototype.py"],
        "corpus": ["samples/by-format/fodg/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "ODF drawing namespace handling only"],
    },
    "gnumeric": {
        "tests": ["tests/skills/test_gnumeric_gate4_prototype.py"],
        "corpus": ["samples/by-format/gnumeric/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "Requires gzip magic \\x1f\\x8b — non-gzip rejected"],
    },
    "abw": {
        "tests": ["tests/skills/test_abw_gate4_prototype.py"],
        "corpus": ["samples/by-format/abw/"],
        "limitations": ["Gate 4 scope only — not for production pipelines",
                        "Supports plain .abw and gzip'd .abw.gz"],
    },
}

# ── Source-track equivalents — reclassify + add corpus ───────────────────────
SOURCE_TRACK_RECLASSIFY = {
    "ods": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/ods/ods_parser.py",
        "corpus": ["samples/by-format/ods/"],
        "tests": ["tests/python/ods/test_dogfood_ods_csv_pipeline.py",
                  "tests/python/ods/test_exception_coverage.py"],
    },
    "odt": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/odt/odt_parser.py",
        "corpus": ["samples/by-format/odt/"],
        "tests": ["tests/python/odt/test_odt_codec.py"],
    },
    "qoi": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/qoi/qoi_parser.py",
        "corpus": ["samples/by-format/qoi/"],
        "tests": ["tests/python/qoi/test_qoi_codec.py"],
    },
    "xcf": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/xcf/xcf_parser.py",
        "corpus": ["samples/by-format/xcf/"],
        "tests": ["tests/python/xcf/test_xcf_codec.py"],
    },
    "dif": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/dif/dif_parser.py",
        "corpus": ["samples/by-format/dif/"],
        "tests": ["tests/python/dif/test_dif_codec.py"],
    },
    "ppm": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/ppm/ppm_parser.py",
        "corpus": ["samples/by-format/ppm/"],
        "tests": ["tests/python/ppm/test_ppm_codec.py"],
    },
    "pgm": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/pgm/pgm_parser.py",
        "corpus": ["samples/by-format/pgm/"],
        "tests": ["tests/python/pgm/test_pgm_codec.py"],
    },
    "pbm": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/pbm/pbm_parser.py",
        "corpus": ["samples/by-format/pbm/"],
        "tests": ["tests/python/pbm/test_pbm_codec.py"],
    },
    "sylk": {
        "evidence_type": "SOURCE_TRACK_EQUIVALENT",
        "status": "passed",
        "delegated_source_path": "src/python/sylk/sylk_parser.py",
        "corpus": ["samples/by-format/sylk/"],
        "tests": ["tests/python/sylk/test_sylk_codec.py"],
    },
}

# ── ORA fix ───────────────────────────────────────────────────────────────────
# ORA was written as 'not_started' but should be 'blocked' (gate 1 deferred)
ORA_STATUS_FIX = "blocked"


def main() -> None:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    formats = data["formats"]

    for fmt in formats:
        fid = fmt["format_id"]
        gates = fmt.setdefault("gates", {})
        g4 = gates.get("gate_4", {})

        if fid in STANDALONE_ADDITIONS and g4:
            patch = STANDALONE_ADDITIONS[fid]
            if not g4.get("tests"):
                g4["tests"] = patch["tests"]
            if not g4.get("corpus"):
                g4["corpus"] = patch["corpus"]
            if not g4.get("limitations"):
                g4["limitations"] = patch["limitations"]

        if fid in SOURCE_TRACK_RECLASSIFY and g4:
            patch = SOURCE_TRACK_RECLASSIFY[fid]
            g4["evidence_type"] = patch["evidence_type"]
            g4["status"] = patch["status"]
            if not g4.get("delegated_source_path"):
                g4["delegated_source_path"] = patch["delegated_source_path"]
            if not g4.get("corpus"):
                g4["corpus"] = patch["corpus"]
            if not g4.get("tests"):
                g4["tests"] = patch["tests"]
            # Remove prototype_path if it was erroneously set
            if g4.get("prototype_path") and not (REPO / g4["prototype_path"]).exists():
                del g4["prototype_path"]

        if fid == "ora" and g4:
            g4["status"] = ORA_STATUS_FIX

    REGISTRY.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"Updated {REGISTRY}")

    # Verify
    data2 = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    print("\nVerification:")
    for fmt in data2["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4")
        if g4:
            et = g4.get("evidence_type", "?")
            status = g4.get("status", "?")
            has_tests = bool(g4.get("tests"))
            has_corpus = bool(g4.get("corpus"))
            ok = "OK" if has_tests and has_corpus else "MISSING"
            if et in ("BLOCKED_BEFORE_GATE4", "NOT_APPLICABLE"):
                ok = "N/A"
            print(f"  {fid:<12} {et:<28} {status:<12} tests={has_tests} corpus={has_corpus}  [{ok}]")


if __name__ == "__main__":
    main()
