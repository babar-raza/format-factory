"""Update format-registry.yaml with gate_4 evidence_type fields for all formats."""
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "registry" / "format-registry.yaml"

# evidence_type to add to existing gate_4 blocks (canonical prototypes)
GATE4_EVIDENCE_TYPE_UPDATES = {
    "fods": {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/fods/"},
    "fodt": {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/fodt/"},
    "zst":  {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/zst/"},
    "fodp": {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/fodp/"},
    "fodg": {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/fodg/"},
    "gnumeric": {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/gnumeric/"},
    "abw":  {"evidence_type": "STANDALONE_PROTOTYPE", "prototype_path": "prototypes/by-format/abw/"},
    # source-track equivalents — add evidence_type
    "ods":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/ods/", "delegated_source_path": "src/python/ods/ods_parser.py"},
    "odt":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/odt/", "delegated_source_path": "src/python/odt/odt_parser.py"},
    "qoi":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/qoi/", "delegated_source_path": "src/python/qoi/qoi_parser.py"},
    "xcf":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/xcf/", "delegated_source_path": "src/python/xcf/xcf_parser.py"},
    "dif":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/dif/", "delegated_source_path": "src/python/dif/dif_parser.py"},
    "ppm":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/ppm/", "delegated_source_path": "src/python/ppm/ppm_parser.py"},
    "pgm":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/pgm/", "delegated_source_path": "src/python/pgm/pgm_parser.py"},
    "pbm":  {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/pbm/", "delegated_source_path": "src/python/pbm/pbm_parser.py"},
    "sylk": {"evidence_type": "EVIDENCE_WRAPPER", "prototype_path": "prototypes/by-format/sylk/", "delegated_source_path": "src/python/sylk/sylk_parser.py"},
    # also add to ora which had not_started gate_4
    "ora":  {"evidence_type": "BLOCKED_BEFORE_GATE4", "reason": "gate1_not_passed",
             "blocker": "Score 6.8/10 below 7.0 threshold", "next_gate": "gate_1_rescore_or_defer"},
}

# New gate_4 blocks for formats that had ABSENT gate_4
GATE4_NEW_BLOCKS = {
    "csv": {
        "status": "passed", "evidence_type": "EVIDENCE_WRAPPER",
        "prototype_path": "prototypes/by-format/csv/",
        "delegated_source_path": "src/python/csv/csv_parser.py",
        "tests": ["tests/skills/test_csv_gate4_prototype.py"],
        "corpus": ["samples/by-format/csv/"],
        "acquisition_pack": "acquisition-packs/csv/pack.yaml",
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "tsv": {
        "status": "passed", "evidence_type": "EVIDENCE_WRAPPER",
        "prototype_path": "prototypes/by-format/tsv/",
        "delegated_source_path": "src/python/tsv/tsv_parser.py",
        "tests": ["tests/skills/test_tsv_gate4_prototype.py"],
        "corpus": ["samples/by-format/tsv/"],
        "acquisition_pack": "acquisition-packs/tsv/pack.yaml",
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "ndjson": {
        "status": "passed", "evidence_type": "EVIDENCE_WRAPPER",
        "retrospective": True,
        "prototype_path": "prototypes/by-format/ndjson/",
        "delegated_source_path": "src/python/ndjson/ndjson_codec.py",
        "tests": ["tests/skills/test_ndjson_gate4_prototype.py"],
        "corpus": ["samples/by-format/ndjson/valid/"],
        "acquisition_pack": "acquisition-packs/ndjson/pack.yaml",
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "toml": {
        "status": "passed", "evidence_type": "EVIDENCE_WRAPPER",
        "retrospective": True,
        "prototype_path": "prototypes/by-format/toml/",
        "delegated_source_path": "src/python/toml/toml_codec.py",
        "tests": ["tests/skills/test_toml_gate4_prototype.py"],
        "corpus": ["samples/by-format/toml/"],
        "acquisition_pack": "acquisition-packs/toml/pack.yaml",
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "xpm": {
        "status": "passed", "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/xpm/",
        "tests": ["tests/skills/test_xpm_gate4_prototype.py"],
        "corpus": ["samples/by-format/xpm/"],
        "acquisition_pack": "acquisition-packs/xpm/pack.yaml",
        "limitations": ["XPM3 only", "Max 4096x4096", "No write"],
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "pam": {
        "status": "passed", "evidence_type": "STANDALONE_PROTOTYPE",
        "prototype_path": "prototypes/by-format/pam/",
        "tests": ["tests/skills/test_pam_gate4_prototype.py"],
        "corpus": ["samples/by-format/pam/"],
        "acquisition_pack": "acquisition-packs/pam/pack.yaml",
        "limitations": ["P7 magic required", "Max 4096x4096 depth 4", "No write"],
        "mission_id": "FF-G4-BACKFILL-001",
    },
    "zpaq": {
        "status": "blocked", "evidence_type": "BLOCKED_BEFORE_GATE4",
        "reason": "gate3_prerequisite_incomplete",
        "blocker": "ZPAQL VM / zpaq CLI unavailable; cannot create corpus samples",
        "next_gate": "gate_3_recovery",
        "mission_id": "FF-G4-BACKFILL-001",
    },
}


def main():
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    formats = data["formats"]

    for fmt in formats:
        fid = fmt["format_id"]
        gates = fmt.setdefault("gates", {})

        if fid in GATE4_EVIDENCE_TYPE_UPDATES:
            g4 = gates.setdefault("gate_4", {})
            for k, v in GATE4_EVIDENCE_TYPE_UPDATES[fid].items():
                if k not in g4:
                    g4[k] = v

        if fid in GATE4_NEW_BLOCKS and "gate_4" not in gates:
            gates["gate_4"] = dict(GATE4_NEW_BLOCKS[fid])
        elif fid in GATE4_NEW_BLOCKS:
            # Merge into existing block
            g4 = gates["gate_4"]
            for k, v in GATE4_NEW_BLOCKS[fid].items():
                if k not in g4:
                    g4[k] = v

    REGISTRY.write_text(
        yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"Updated {REGISTRY}")

    # Verify
    data2 = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    print("\nVerification:")
    missing_et = []
    for fmt in data2["formats"]:
        fid = fmt["format_id"]
        g4 = fmt.get("gates", {}).get("gate_4", None)
        if g4:
            et = g4.get("evidence_type", "MISSING")
            status = g4.get("status", "?")
            print(f"  {fid}: status={status} evidence_type={et}")
            if et == "MISSING":
                missing_et.append(fid)
        elif fid == "odf-shared":
            print(f"  {fid}: NOT_APPLICABLE (shared family entry)")
        else:
            print(f"  {fid}: gate_4=ABSENT")
            missing_et.append(fid)

    print(f"\nFormats missing gate_4.evidence_type: {missing_et}")


if __name__ == "__main__":
    main()
