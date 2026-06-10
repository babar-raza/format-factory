"""
R3 ODF Driver — builds scoped FODT context pack from existing fetched ODF abstract.
Uses the same ODF abstract already fetched in R2 (odf-abstract.html).
Produces FODT context pack alongside FODS.
"""
import sys, json, hashlib, pathlib, re, html.parser
from datetime import datetime, timezone

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SAL_DIR = REPO_ROOT / "tools" / "specification-authority-layer"
sys.path.insert(0, str(SAL_DIR))

from spec_source_registry import register_source, load_registry
from spec_vault_ingest import ingest_text_fixture, verify_snapshot_integrity
from spec_parser import parse_spec_from_text
from spec_normalizer import normalize_spec, load_normalized_artifact
from spec_indexer import build_index, load_index
from spec_digestor import compute_digest, check_staleness
from requirement_extractor import extract_requirements
from context_pack_builder import build_context_pack, verify_context_pack

R3_EVIDENCE = REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r3"
R2_EVIDENCE = REPO_ROOT / ".local/evidences/spec-authority-real-pilot-r2"
ARTIFACTS_DIR = str(R3_EVIDENCE / "normalized")
CP_DIR = R3_EVIDENCE / "context-packs"
SAMPLE_DIR = R3_EVIDENCE / "sample-outputs"
REGISTRY_DIR = str(R3_EVIDENCE)

pathlib.Path(ARTIFACTS_DIR).mkdir(parents=True, exist_ok=True)
CP_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

class HTMLStripper(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.chunks = []
        self._skip = False
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self._skip = True
        if tag in ('p','h1','h2','h3','h4','li','tr','dt','dd','pre'): self.chunks.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self._skip = False
        if tag in ('p','h1','h2','h3','h4','pre'): self.chunks.append('\n')
    def handle_data(self, data):
        if not self._skip: self.chunks.append(data)
    def get_text(self):
        text = ''.join(self.chunks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return re.sub(r'[ \t]+', ' ', text).strip()

def strip_html(b):
    s = HTMLStripper()
    s.feed(b.decode('utf-8', errors='replace'))
    return s.get_text()

results = {"generated_at": now_iso()}

print("=== R3 ODF Driver: FODT scoped context pack ===")

# Use the same ODF abstract from R2
ODF_HTML = R2_EVIDENCE / "spec-vault/fods/odf-abstract.html"
odf_html = ODF_HTML.read_bytes()
odf_text_raw = strip_html(odf_html)

# FODT uses ODF text document structure — scope to text-document-relevant portion
fodt_scoped = (
    "ODF 1.3 — Scoped Flat Text Document (FODT) Structure\n"
    "Source: OASIS Open Document Format for Office Applications v1.3\n"
    "URL: https://docs.oasis-open.org/office/OpenDocument/v1.3/os/\n"
    "Scope: SCOPED EXTRACTION — ODF text document model from introduction.\n"
    "License caveat: OASIS ODF 1.3 open specification; license review pending.\n"
    "Note: FODT is the flat (non-ZIP) variant of ODF Text Document format.\n\n"
    + odf_text_raw[:5000]
)

print(f"  FODT scoped text: {len(fodt_scoped)} chars")

# Register FODT source
register_source(
    source_id="src-r3-fodt-odf13",
    format_id="fodt",
    title="ODF 1.3 — Flat Text Document (FODT) — Scoped Introduction",
    source_type="odf_standard",
    url_or_path="https://docs.oasis-open.org/office/OpenDocument/v1.3/os/",
    fetch_policy="deferred_local_fixture",
    registry_dir=REGISTRY_DIR,
)

vault_fodt = ingest_text_fixture(
    "src-r3-fodt-odf13", fodt_scoped,
    vault_dir=str(R3_EVIDENCE / "spec-vault/fodt"),
)
print(f"  FODT vault SHA-256: {vault_fodt['sha256']}")

parsed_fodt = parse_spec_from_text(
    "src-r3-fodt-odf13", vault_fodt["sha256"], "fodt", fodt_scoped
)
norm_fodt = normalize_spec(parsed_fodt, artifacts_dir=ARTIFACTS_DIR)
artifact_fodt = load_normalized_artifact("src-r3-fodt-odf13", ARTIFACTS_DIR)
digest_fodt = compute_digest("src-r3-fodt-odf13", vault_fodt["sha256"], artifact_fodt, artifacts_dir=ARTIFACTS_DIR)
idx_fodt = build_index("src-r3-fodt-odf13", vault_fodt["sha256"], "fodt", artifact_fodt, artifacts_dir=ARTIFACTS_DIR)
reqs_fodt = extract_requirements("src-r3-fodt-odf13", "fodt", artifact_fodt, artifacts_dir=ARTIFACTS_DIR)
print(f"  FODT: sections={norm_fodt.sections_normalized}, requirements={len(reqs_fodt)}")

# Build context pack
idx_doc = load_index("src-r3-fodt-odf13", ARTIFACTS_DIR)
src_records = [{
    "source_id": "src-r3-fodt-odf13",
    "sha256": vault_fodt["sha256"],
    "sections_count": norm_fodt.sections_normalized,
    "title": "ODF 1.3 FODT Scoped Introduction",
    "source_type": "odf_standard",
}]
reqs_dicts = [r.to_dict() for r in reqs_fodt]

cp_fodt = build_context_pack(
    format_id="fodt",
    source_records=src_records,
    normalized_artifacts={"src-r3-fodt-odf13": artifact_fodt},
    requirements_by_source={"src-r3-fodt-odf13": reqs_dicts},
    index_docs={"src-r3-fodt-odf13": idx_doc} if idx_doc else None,
    output_dir=str(CP_DIR),
)
ok = verify_context_pack(cp_fodt.output_path)
print(f"  FODT CP: {cp_fodt.context_pack_id}, sha={cp_fodt.manifest_sha256[:16]}..., verify={ok.get('valid')}")

# Determinism check
cp_det1 = build_context_pack(
    format_id="fodt", source_records=src_records,
    normalized_artifacts={"src-r3-fodt-odf13": artifact_fodt},
    requirements_by_source={"src-r3-fodt-odf13": reqs_dicts},
    index_docs={"src-r3-fodt-odf13": idx_doc} if idx_doc else None,
    output_dir=str(R3_EVIDENCE / "context-packs/det1"),
)
cp_det2 = build_context_pack(
    format_id="fodt", source_records=src_records,
    normalized_artifacts={"src-r3-fodt-odf13": artifact_fodt},
    requirements_by_source={"src-r3-fodt-odf13": reqs_dicts},
    index_docs={"src-r3-fodt-odf13": idx_doc} if idx_doc else None,
    output_dir=str(R3_EVIDENCE / "context-packs/det2"),
)
deterministic = cp_det1.manifest_sha256 == cp_det2.manifest_sha256
print(f"  FODT deterministic: {deterministic}")

# Sample output
sample = {
    "sample_type": "context_pack_sample",
    "format": "fodt",
    "context_pack_id": cp_fodt.context_pack_id,
    "manifest_sha256": cp_fodt.manifest_sha256,
    "source_sha256": vault_fodt["sha256"],
    "authority_status": "ACCEPTED_WITH_CAVEAT",
    "caveat": "Scoped ODF 1.3 intro only; full FODT spec deferred; ODF license pending",
    "sample_requirements": [r.to_dict() for r in reqs_fodt[:3]],
    "generated_at": now_iso(),
}
(SAMPLE_DIR / "fodt-context-pack-sample.json").write_text(json.dumps(sample, indent=2))

results["fodt"] = {
    "source_id": "src-r3-fodt-odf13",
    "sha256": vault_fodt["sha256"],
    "sections": norm_fodt.sections_normalized,
    "requirements": len(reqs_fodt),
    "context_pack_id": cp_fodt.context_pack_id,
    "manifest_sha256": cp_fodt.manifest_sha256,
    "deterministic": deterministic,
    "verified": ok.get("valid"),
    "authority_status": "ACCEPTED_WITH_CAVEAT",
}

(R3_EVIDENCE / "pilot-results-r3.json").write_text(json.dumps(results, indent=2))
print(f"\nR3 ODF driver complete. FODT requirements: {len(reqs_fodt)}")
print("PILOT R3 ODF DRIVER COMPLETE")
