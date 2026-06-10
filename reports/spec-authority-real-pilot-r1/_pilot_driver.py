"""
Real Pilot Driver for FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R1-001
Exercises all SAL subsystems against ZST, Netpbm, DIF, and FODS/FODT (stretch).
"""
import sys, json
from pathlib import Path

REPO_ROOT = Path("c:/Users/prora/OneDrive/Documents/GitHub/format-factory")
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))

PILOT_REGISTRY_DIR = str(REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r1/spec-source-registry")
PILOT_VAULT_DIR    = str(REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r1/spec-vault")
PILOT_ARTIFACT_DIR = str(REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r1/artifacts")
PILOT_CP_DIR       = str(REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r1/context-packs")
PILOT_LEDGER_PATH  = str(REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r1/spec-usage-ledger/ledger.jsonl")

from spec_source_registry import register_source, load_registry, is_source_registered, validate_citation
from spec_vault_ingest import ingest_text_fixture, get_snapshot_meta, verify_snapshot_integrity
from spec_parser import parse_spec_from_text
from spec_normalizer import normalize_spec, load_normalized_artifact
from spec_indexer import build_index, search_index, load_index
from spec_digestor import compute_digest, check_staleness
from requirement_extractor import extract_requirements
from spec_verifier import verify_requirements, check_anti_bypass
from requirement_graph import build_requirement_graph
from context_pack_builder import build_context_pack, verify_context_pack
from spec_governance_runtime import check_citation_allowed, check_context_pack_use_allowed, check_memory_only_claim

ZST_FIXTURE = """# Zstandard Compression Format (RFC 8878 Summary Fixture)

## Overview

The Zstandard (zstd) format provides lossless data compression.
This specification is based on IETF RFC 8878 (Zstandard Compression and the "application/zstd" Media Type).
Files MUST begin with a magic number of 0xFD2FB528 stored in little-endian byte order.
The decompressor SHALL handle multiple independent frames sequentially.
A skippable frame MUST begin with a magic number in the range 0x184D2A50 to 0x184D2A5F.

## Frame Format

Each frame SHALL contain a Frame Header followed by one or more Data Blocks.
The Frame Header MUST include the FHD (Frame Header Descriptor) byte.
The Content Size field SHOULD be present to allow memory pre-allocation.
Data Blocks MUST each begin with a 3-byte Block Header.
The last block in a frame SHALL set the Last_Block bit to 1.

## Block Types

A block MUST be one of: Raw_Block, RLE_Block, Compressed_Block, or Reserved.
Reserved block types MUST NOT be used by an encoder.
A decoder MUST reject a frame containing a Reserved block type.

## Compression Levels

The compressor MAY operate at compression levels 1 through 22.
Level 1 SHOULD provide the fastest compression with lowest ratio.
Level 22 SHOULD provide the maximum compression ratio.
Default level SHOULD be 3 for balanced performance.

## Checksums

An optional Content Checksum field MAY be included at the end of the frame.
When present, it SHALL be a 4-byte xxHash32 checksum of the decompressed content.
"""

NETPBM_FIXTURE = """# Netpbm Format Family Documentation

## Overview

The Netpbm format family includes PBM, PGM, and PPM formats.
These are simple, portable bitmap formats from the Netpbm project.
Source authority: Netpbm project documentation (de facto standard; originally public domain).

## PBM - Portable Bitmap Format

PBM files MUST start with a magic number: P1 for ASCII, P4 for binary format.
Width and height values MUST be positive integers on the header line.
Each pixel value SHALL be either 0 (white) or 1 (black).
Whitespace between values MUST be ignored by a conforming reader.
Comments may appear after hash and MUST be ignored by the parser.

## PGM - Portable Graymap Format

PGM files MUST start with magic number P2 for ASCII or P5 for binary.
The header MUST include width, height, and maxval (maximum pixel value).
Maxval MUST be in the range 1 to 65535 inclusive.
Each pixel SHALL be a value from 0 to maxval.
A compliant reader MUST NOT assume maxval is always 255.

## PPM - Portable Pixmap Format

PPM files MUST start with magic number P3 for ASCII or P6 for binary.
The header SHALL include width, height, and maxval.
Each pixel SHALL have three channel values (R, G, B) each from 0 to maxval.
Binary PPM (P6) stores pixel values in big-endian byte order when maxval exceeds 255.
"""

DIF_FIXTURE = """# DIF Data Interchange Format Historical Specification

## Overview

DIF (Data Interchange Format) is a legacy spreadsheet exchange format.
Original specification was published by Software Arts, Inc. in 1981.
No current official standardization body maintains this specification.
Status: Historical public domain document; de facto standard only.

## Header Block

The DIF file MUST begin with the TABLE identifier.
The TABLE header SHALL specify the version number as 0,1.
Following header tuples may include VECTORS for column count and TUPLES for row count.
All header keywords should be uppercase for compatibility.

## Data Blocks

Each data block MUST include a type indicator and a numeric value.
String values MUST be enclosed in double quotes.
Numeric values SHALL be represented in decimal format.
The ENDOFDATA keyword SHALL terminate the file.

## Authority Status

This specification is based on historical documentation only.
No current IETF RFC, ISO standard, or ECMA specification covers DIF.
Implementations should treat requirements as EMPIRICAL_ONLY or ACCEPTED_WITH_CAVEAT.
"""

FODS_FIXTURE = """# FODS FODT Flat ODF Formats Summary

## Overview

FODS and FODT are flat non-ZIP variants of ODF (Open Document Format).
The authoritative specification is OASIS ODF 1.3 (OASIS Standard).
This summary covers only the most basic structural requirements.

## FODS Flat ODF Spreadsheet

FODS files MUST be valid XML documents conforming to ODF 1.3 schema.
The root element SHALL be office:spreadsheet with appropriate ODF namespace declarations.
Each sheet SHALL be represented as a table:table element.
Cell values MUST be stored in table:table-cell elements.

## FODT Flat ODF Text Document

FODT files MUST be valid XML documents conforming to ODF 1.3 schema.
The root element SHALL be office:document with appropriate ODF namespace declarations.
Paragraph content SHALL be stored in text:p elements.
Heading elements SHALL use the text:h element with the text:outline-level attribute.

## Authority Note

The full ODF 1.3 specification exceeds 1000 pages.
This pilot only extracts a scoped subset of structural requirements.
For full compliance verification, consult OASIS ODF 1.3 specification directly.
"""

print("=== PILOT DRIVER START ===")
results = {}

# STEP 1: Source Registration
print("\n[STEP 1] Source Registration")
sources_to_register = [
    ("src-zst-rfc8878",   "zst",    "Zstandard RFC 8878 (Summary Fixture)",  "rfc",                   "https://www.rfc-editor.org/rfc/rfc8878", "deferred_local_fixture"),
    ("src-netpbm-docs",   "netpbm", "Netpbm Format Family Documentation",    "public_domain_spec",    "http://netpbm.sourceforge.net/doc/",      "deferred_local_fixture"),
    ("src-dif-softarts",  "dif",    "DIF Specification (Software Arts 1981)","empirical_observation", "https://en.wikipedia.org/wiki/Data_Interchange_Format", "deferred_local_fixture"),
    ("src-fods-oasis",    "fods",   "FODS/FODT OASIS ODF 1.3 (Summary)",     "odf_standard",          "https://docs.oasis-open.org/office/OpenDocument/v1.3/", "deferred_local_fixture"),
]

registered_source_ids = []
for sid, fmtid, title, stype, url, policy in sources_to_register:
    if not is_source_registered(sid, PILOT_REGISTRY_DIR):
        register_source(sid, fmtid, title, stype, url, policy, registry_dir=PILOT_REGISTRY_DIR)
        print(f"  REGISTERED: {sid} ({stype})")
    else:
        print(f"  ALREADY_REGISTERED: {sid}")
    registered_source_ids.append(sid)

all_registered = load_registry(PILOT_REGISTRY_DIR)
print(f"  Total registered: {len(all_registered)}")

citation_zst = validate_citation("src-zst-rfc8878", PILOT_REGISTRY_DIR)
citation_bad  = validate_citation("src-fake-unknown", PILOT_REGISTRY_DIR)
print(f"  Citation ZST (expect valid=True): {citation_zst['valid']}")
print(f"  Citation fake (expect valid=False): {citation_bad['valid']}")
results["registration"] = {
    "count": len(all_registered),
    "ids": [s.source_id for s in all_registered],
    "citation_valid_pass": citation_zst["valid"],
    "citation_invalid_rejected": not citation_bad["valid"],
}

# STEP 2: Vault Ingest
print("\n[STEP 2] Vault Ingest")
fixtures = {
    "src-zst-rfc8878":  ZST_FIXTURE,
    "src-netpbm-docs":  NETPBM_FIXTURE,
    "src-dif-softarts":  DIF_FIXTURE,
    "src-fods-oasis":   FODS_FIXTURE,
}

ingested = {}
for sid, content in fixtures.items():
    rec = ingest_text_fixture(sid, content, label="pilot-fixture", vault_dir=PILOT_VAULT_DIR)
    integrity = verify_snapshot_integrity(sid, PILOT_VAULT_DIR)
    print(f"  {sid}: {rec['status']} sha256={rec['sha256'][:16]}... integrity={integrity['status']}")
    ingested[sid] = {
        "sha256": rec["sha256"],
        "vault_path": rec.get("vault_path", ""),
        "status": rec["status"],
        "integrity": integrity["status"],
    }

results["vault_ingest"] = ingested

# STEP 3: Parse
print("\n[STEP 3] Parse")
parsed_specs = {}
for sid, content in fixtures.items():
    sha256 = ingested[sid]["sha256"]
    fmt = sid.replace("src-", "").split("-")[0]
    parsed = parse_spec_from_text(sid, sha256, fmt, content)
    print(f"  {sid}: method={parsed.parse_method}, sections={len(parsed.sections)}")
    parsed_specs[sid] = parsed

# STEP 4: Normalize
print("\n[STEP 4] Normalize")
normalized_artifacts = {}
for sid, parsed in parsed_specs.items():
    norm = normalize_spec(parsed, artifacts_dir=PILOT_ARTIFACT_DIR)
    artifact = load_normalized_artifact(sid, PILOT_ARTIFACT_DIR)
    print(f"  {sid}: sections_normalized={norm.sections_normalized}")
    normalized_artifacts[sid] = {"norm": norm, "artifact": artifact}

results["normalization"] = {
    sid: {"sections": v["norm"].sections_normalized}
    for sid, v in normalized_artifacts.items()
}

# STEP 5: Index
print("\n[STEP 5] Index")
index_results = {}
for sid, nd in normalized_artifacts.items():
    artifact = nd["artifact"]
    sha256 = ingested[sid]["sha256"]
    fmt = artifact["format_id"]
    idx = build_index(sid, sha256, fmt, artifact, artifacts_dir=PILOT_ARTIFACT_DIR)
    print(f"  {sid}: terms={idx.term_count}, sections={idx.section_count}")
    if fmt == "zst":
        hits = search_index(sid, "magic frame", PILOT_ARTIFACT_DIR)
        print(f"    search('magic frame'): {len(hits)} hits")
    index_results[sid] = {"term_count": idx.term_count, "section_count": idx.section_count}

results["indexing"] = index_results

# STEP 6: Digest
print("\n[STEP 6] Digest")
digests = {}
for sid, nd in normalized_artifacts.items():
    artifact = nd["artifact"]
    sha256 = ingested[sid]["sha256"]
    digest = compute_digest(sid, sha256, artifact, artifacts_dir=PILOT_ARTIFACT_DIR)
    print(f"  {sid}: content_digest={digest.content_digest[:16]}...")
    digests[sid] = {"content_digest": digest.content_digest, "sha256_snapshot": digest.sha256_snapshot}

results["digests"] = digests

# STEP 7: Staleness
print("\n[STEP 7] Staleness Check")
staleness_results = {}
for sid in ingested:
    sha256 = ingested[sid]["sha256"]
    check = check_staleness(sid, sha256, PILOT_ARTIFACT_DIR)
    print(f"  {sid}: stale={check['stale']} — {check['reason'][:60]}")
    staleness_results[sid] = {"stale": check["stale"], "reason": check["reason"]}

fake_sha = "a" * 64
fake_stale = check_staleness("src-zst-rfc8878", fake_sha, PILOT_ARTIFACT_DIR)
print(f"  SYNTHETIC STALE: stale={fake_stale['stale']} — {fake_stale['reason'][:60]}")
results["staleness"] = {
    "all_fresh": all(not v["stale"] for v in staleness_results.values()),
    "synthetic_stale_detected": fake_stale["stale"],
    "per_source": staleness_results,
}

# STEP 8: Requirement Extraction
print("\n[STEP 8] Requirement Extraction")
requirements_by_source = {}
for sid, nd in normalized_artifacts.items():
    artifact = nd["artifact"]
    fmt = artifact["format_id"]
    reqs = extract_requirements(sid, fmt, artifact, artifacts_dir=PILOT_ARTIFACT_DIR)
    print(f"  {sid}: {len(reqs)} candidate requirements")
    requirements_by_source[sid] = [r.to_dict() for r in reqs]

total_reqs = sum(len(v) for v in requirements_by_source.values())
print(f"  TOTAL: {total_reqs} candidate requirements")
results["requirement_extraction"] = {sid: len(v) for sid, v in requirements_by_source.items()}
results["total_requirements"] = total_reqs

# STEP 9: Verify Requirements
print("\n[STEP 9] Verify Requirements")
verification_by_source = {}
for sid, reqs in requirements_by_source.items():
    artifact = normalized_artifacts[sid]["artifact"]
    vr = verify_requirements(reqs, normalized_artifact=artifact, registered_source_ids=registered_source_ids)
    counts = {"VERIFIED": 0, "UNVERIFIABLE": 0, "ANTI_BYPASS_REJECTED": 0}
    for v in vr:
        counts[v.status] = counts.get(v.status, 0) + 1
    print(f"  {sid}: {counts}")
    verification_by_source[sid] = counts

results["verification"] = verification_by_source

# STEP 10: Requirement Graph
print("\n[STEP 10] Requirement Graph")
for sid, reqs in requirements_by_source.items():
    artifact = normalized_artifacts[sid]["artifact"]
    fmt = artifact["format_id"]
    vr = verify_requirements(reqs, normalized_artifact=artifact, registered_source_ids=registered_source_ids)
    vr_dicts = [v.to_dict() for v in vr]
    graph = build_requirement_graph(sid, fmt, reqs, verified_results=vr_dicts, artifacts_dir=PILOT_ARTIFACT_DIR)
    print(f"  {sid}: nodes={len(graph.nodes)}, edges={len(graph.edges)}")

# STEP 11: Context Pack Build (Run 1)
print("\n[STEP 11] Context Pack Build (Run 1)")
source_type_map = {
    "src-zst-rfc8878": "rfc",
    "src-netpbm-docs": "public_domain_spec",
    "src-dif-softarts": "empirical_observation",
    "src-fods-oasis": "odf_standard",
}

cp_run1 = {}
for sid in ["src-zst-rfc8878", "src-netpbm-docs", "src-dif-softarts"]:
    nd = normalized_artifacts[sid]
    artifact = nd["artifact"]
    fmt_id = artifact["format_id"]
    sha256 = ingested[sid]["sha256"]
    src_records = [{
        "source_id": sid,
        "sha256": sha256,
        "sections_count": nd["norm"].sections_normalized,
        "title": f"Pilot source for {fmt_id}",
        "source_type": source_type_map[sid],
    }]
    idx_doc = load_index(sid, PILOT_ARTIFACT_DIR)
    cp = build_context_pack(
        format_id=fmt_id,
        source_records=src_records,
        normalized_artifacts={sid: artifact},
        requirements_by_source={sid: requirements_by_source[sid]},
        index_docs={sid: idx_doc} if idx_doc else None,
        output_dir=PILOT_CP_DIR,
    )
    print(f"  {fmt_id}: {cp.context_pack_id} manifest_sha256={cp.manifest_sha256[:16]}...")
    cp_run1[fmt_id] = {"context_pack_id": cp.context_pack_id, "manifest_sha256": cp.manifest_sha256, "output_path": cp.output_path}

# STEP 11b: Context Pack Build (Run 2 — Determinism)
print("\n[STEP 11b] Context Pack Determinism (Run 2)")
cp_run2 = {}
for sid in ["src-zst-rfc8878", "src-netpbm-docs", "src-dif-softarts"]:
    nd = normalized_artifacts[sid]
    artifact = nd["artifact"]
    fmt_id = artifact["format_id"]
    sha256 = ingested[sid]["sha256"]
    src_records = [{
        "source_id": sid,
        "sha256": sha256,
        "sections_count": nd["norm"].sections_normalized,
        "title": f"Pilot source for {fmt_id}",
        "source_type": source_type_map[sid],
    }]
    idx_doc = load_index(sid, PILOT_ARTIFACT_DIR)
    cp2 = build_context_pack(
        format_id=fmt_id,
        source_records=src_records,
        normalized_artifacts={sid: artifact},
        requirements_by_source={sid: requirements_by_source[sid]},
        index_docs={sid: idx_doc} if idx_doc else None,
        output_dir=PILOT_CP_DIR,
    )
    match = cp_run1[fmt_id]["manifest_sha256"] == cp2.manifest_sha256
    print(f"  {fmt_id}: deterministic={match}")
    cp_run2[fmt_id] = {"manifest_sha256": cp2.manifest_sha256, "deterministic": match}

# STEP 11c: Context Pack Verification
print("\n[STEP 11c] Context Pack Verification")
cp_verify = {}
for fmt_id, cp in cp_run1.items():
    r = verify_context_pack(cp["output_path"])
    print(f"  {fmt_id}: valid={r['valid']} id={r.get('context_pack_id','N/A')}")
    cp_verify[fmt_id] = r.get("valid", False)

results["context_packs"] = cp_run1
results["determinism"] = {fmt: cp_run2[fmt]["deterministic"] for fmt in cp_run2}
results["cp_verification"] = cp_verify

# STEP 12: Governance Runtime
print("\n[STEP 12] Governance Runtime Checks")
g1 = check_citation_allowed("src-zst-rfc8878", "zst", ledger_path=PILOT_LEDGER_PATH, registry_dir=PILOT_REGISTRY_DIR)
g2 = check_citation_allowed("src-UNREGISTERED", "zst", ledger_path=PILOT_LEDGER_PATH, registry_dir=PILOT_REGISTRY_DIR)
g3 = check_memory_only_claim({"raw_ai_summary_only": True}, "netpbm", ledger_path=PILOT_LEDGER_PATH, registry_dir=PILOT_REGISTRY_DIR)
g4 = check_memory_only_claim({"source_refs": ["src-netpbm-docs"]}, "netpbm", ledger_path=PILOT_LEDGER_PATH, registry_dir=PILOT_REGISTRY_DIR)
print(f"  cite_registered: allowed={g1['allowed']}")
print(f"  cite_unregistered: allowed={g2['allowed']}")
print(f"  memory_only: allowed={g3['allowed']}")
print(f"  valid_claim: allowed={g4['allowed']}")
results["governance"] = {
    "cite_registered_allowed": g1["allowed"],
    "cite_unregistered_rejected": not g2["allowed"],
    "memory_only_rejected": not g3["allowed"],
    "valid_claim_allowed": g4["allowed"],
}

# STEP 13: Authority Classification
authority_summary = {
    "src-zst-rfc8878":  {"source_type": "rfc",                   "authority_status": "ACCEPTED_SPEC",         "caveat": "Fixture-based; real RFC 8878 fetch deferred"},
    "src-netpbm-docs":  {"source_type": "public_domain_spec",    "authority_status": "ACCEPTED_WITH_CAVEAT",  "caveat": "De facto standard; no formal ISO/IETF standard"},
    "src-dif-softarts":  {"source_type": "empirical_observation", "authority_status": "EMPIRICAL_ONLY",        "caveat": "Historical doc only; no current standards body"},
    "src-fods-oasis":   {"source_type": "odf_standard",          "authority_status": "ACCEPTED_WITH_CAVEAT",  "caveat": "Partial scoped summary only; full ODF 1.3 too large"},
}
results["authority_classification"] = authority_summary

# Save summary
summary_path = Path(PILOT_ARTIFACT_DIR).parent / "pilot-results-summary.json"
summary_path.parent.mkdir(parents=True, exist_ok=True)
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n=== PILOT DRIVER COMPLETE ===")
print(f"Total candidate requirements: {total_reqs}")
print(f"Context packs built: {list(cp_run1.keys())}")
print(f"Determinism: {results['determinism']}")
print(f"All staleness fresh: {results['staleness']['all_fresh']}")
print(f"Synthetic stale detected: {results['staleness']['synthetic_stale_detected']}")
print(f"Summary: {summary_path}")
