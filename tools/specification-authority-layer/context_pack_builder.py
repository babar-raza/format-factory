"""
context_pack_builder.py — Build deterministic context packs for product formats.

A context pack bundles:
  - manifest.sha256 (digest of all included sources)
  - format_id
  - included_sources: [{source_id, sha256, sections_count, ...}]
  - requirement_summary: [{req_id, heading, keyword, text_fragment}]
  - index_terms: [top N terms]
  - context_pack_id (deterministic from manifest SHA)
  - created_at

Anti-bypass:
  - Context pack missing manifest.sha256 is rejected.
  - Stale context pack (source sha changed) is rejected at use-time.

Storage: reports/specification-authority-layer-mwp/context-pack-sample/
         or a custom output_dir.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _compute_manifest_sha256(sources: List[Dict[str, Any]]) -> str:
    """Deterministic SHA256 of included sources (sorted by source_id)."""
    parts = []
    for s in sorted(sources, key=lambda x: x.get("source_id", "")):
        parts.append(f"{s['source_id']}:{s.get('sha256', '')}:{s.get('sections_count', 0)}")
    digest_input = "\n".join(parts).encode("utf-8")
    return hashlib.sha256(digest_input).hexdigest()


@dataclass
class ContextPack:
    context_pack_id: str
    format_id: str
    manifest_sha256: str
    included_sources: List[Dict[str, Any]]
    requirement_summary: List[Dict[str, Any]]
    index_terms: List[str]
    created_at: str
    output_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context_pack_id": self.context_pack_id,
            "format_id": self.format_id,
            "manifest": {
                "sha256": self.manifest_sha256,
                "sources_count": len(self.included_sources),
            },
            "included_sources": self.included_sources,
            "requirement_summary": self.requirement_summary,
            "index_terms": self.index_terms,
            "created_at": self.created_at,
            "output_path": self.output_path,
        }


def build_context_pack(
    format_id: str,
    source_records: List[Dict[str, Any]],
    normalized_artifacts: Optional[Dict[str, Dict[str, Any]]] = None,
    requirements_by_source: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    index_docs: Optional[Dict[str, Dict[str, Any]]] = None,
    output_dir: Optional[str] = None,
    max_index_terms: int = 50,
) -> ContextPack:
    """
    Build a deterministic context pack for a format.

    Parameters:
      format_id: e.g. "zst", "netpbm", "dif"
      source_records: list of {source_id, sha256, sections_count, title, ...}
      normalized_artifacts: {source_id -> artifact dict}
      requirements_by_source: {source_id -> [req dicts]}
      index_docs: {source_id -> index doc}
      output_dir: where to write the pack
    """
    out_root = Path(output_dir) if output_dir else Path("reports/specification-authority-layer-mwp/context-pack-sample")
    out_root.mkdir(parents=True, exist_ok=True)

    # Build included sources summary
    included: List[Dict[str, Any]] = []
    for sr in source_records:
        entry = {
            "source_id": sr.get("source_id", ""),
            "title": sr.get("title", ""),
            "sha256": sr.get("sha256", ""),
            "sections_count": sr.get("sections_count", 0),
            "source_type": sr.get("source_type", ""),
        }
        included.append(entry)

    manifest_sha = _compute_manifest_sha256(included)
    context_pack_id = f"CP-{format_id.upper()}-{manifest_sha[:12]}"

    # Aggregate requirements
    req_summary: List[Dict[str, Any]] = []
    if requirements_by_source:
        for source_id, reqs in requirements_by_source.items():
            for r in reqs[:20]:  # cap per source
                req_summary.append({
                    "req_id": r.get("req_id", ""),
                    "source_id": source_id,
                    "heading": r.get("heading", ""),
                    "keyword": r.get("keyword", ""),
                    "text_fragment": r.get("text_fragment", "")[:150],
                })

    # Aggregate top index terms
    all_terms: Dict[str, int] = {}
    if index_docs:
        for _, idx in index_docs.items():
            for term, sids in idx.get("terms", {}).items():
                all_terms[term] = all_terms.get(term, 0) + len(sids)
    top_terms = sorted(all_terms, key=lambda t: -all_terms[t])[:max_index_terms]

    pack = ContextPack(
        context_pack_id=context_pack_id,
        format_id=format_id,
        manifest_sha256=manifest_sha,
        included_sources=included,
        requirement_summary=req_summary,
        index_terms=top_terms,
        created_at=_now_iso(),
    )

    # Write pack
    pack_path = out_root / f"{format_id}-context-pack.json"
    pack_dict = pack.to_dict()
    with open(pack_path, "w", encoding="utf-8") as f:
        json.dump(pack_dict, f, indent=2)
    pack.output_path = str(pack_path)

    # Write manifest separately
    manifest_path = out_root / f"{format_id}-manifest.json"
    manifest = {
        "context_pack_id": context_pack_id,
        "format_id": format_id,
        "sha256": manifest_sha,
        "sources": [s["source_id"] for s in included],
        "created_at": pack.created_at,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return pack


def verify_context_pack(pack_path: str) -> Dict[str, Any]:
    """
    Verify a context pack has valid manifest.sha256 and expected fields.
    Anti-bypass: reject pack without manifest.sha256.
    """
    path = Path(pack_path)
    if not path.exists():
        return {"valid": False, "reason": f"Pack file not found: {pack_path}"}

    with open(path, "r", encoding="utf-8") as f:
        pack = json.load(f)

    manifest = pack.get("manifest", {})
    sha = manifest.get("sha256", "")
    if not sha:
        return {"valid": False, "reason": "manifest.sha256 missing — anti-bypass rejected."}

    format_id = pack.get("format_id", "")
    if not format_id:
        return {"valid": False, "reason": "format_id missing."}

    context_pack_id = pack.get("context_pack_id", "")
    if not context_pack_id:
        return {"valid": False, "reason": "context_pack_id missing."}

    # Recompute manifest sha from included_sources
    included = pack.get("included_sources", [])
    computed_sha = _compute_manifest_sha256(included)
    if computed_sha != sha:
        return {
            "valid": False,
            "reason": f"manifest.sha256 mismatch: stored={sha[:16]}... computed={computed_sha[:16]}...",
        }

    return {
        "valid": True,
        "context_pack_id": context_pack_id,
        "format_id": format_id,
        "manifest_sha256": sha,
        "sources_count": len(included),
    }


def load_context_pack(pack_path: str) -> Optional[Dict[str, Any]]:
    """Load a context pack from disk."""
    path = Path(pack_path)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# SAL Fact Coverage Integration (TC-SAL-008)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def get_sal_coverage_summary(format_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load SAL fact coverage summary from .local/sal-output/fact-coverage-report.json.

    Returns a dict with coverage metrics for the supervisor context pack, or None if
    the report has not been generated yet (graceful degradation).

    Args:
        format_id: If given, return coverage for only that format. Otherwise return summary.
    """
    report_path = _REPO_ROOT / ".local" / "sal-output" / "fact-coverage-report.json"
    if not report_path.is_file():
        return None
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    if format_id:
        for fmt in report.get("formats", []):
            if fmt.get("format_id") == format_id:
                return {
                    "format_id": format_id,
                    "effective_verified": fmt.get("effective_verified", 0),
                    "total_registered": fmt.get("total_registered", 0),
                    "coverage_percent": fmt.get("coverage_percent", 0.0),
                    "pending": fmt.get("pending", 0),
                    "generated_at": report.get("generated_at"),
                }
        return None

    s = report.get("summary", {})
    return {
        "total_verified": s.get("total_verified", 0),
        "total_registered": s.get("total_registered", 0),
        "overall_coverage_percent": s.get("overall_coverage_percent", 0.0),
        "total_pending": s.get("total_pending", 0),
        "formats": [
            {
                "format_id": f["format_id"],
                "effective_verified": f.get("effective_verified", 0),
                "total_registered": f.get("total_registered", 0),
                "coverage_percent": f.get("coverage_percent", 0.0),
            }
            for f in report.get("formats", [])
        ],
        "generated_at": report.get("generated_at"),
    }


def rebuild_all_from_workbench(
    repo_root: Any,
    output_dir: Optional[str] = None,
) -> List["ContextPack"]:
    """Rebuild context packs for ODF-family formats and ZST from workbench facts.

    Reads verified-facts-review.yaml files from .local/spec-cache/ and builds
    context packs with real requirement_summary populated from workbench facts.
    All ODF-family packs share the canonical ODF 1.3 Part 3 SHA.

    Args:
        repo_root: Path to repository root (str or Path).
        output_dir: Where to write the packs. Defaults to the standard sample dir.

    Returns:
        List of ContextPack objects (one per format).
    """
    try:
        import yaml  # type: ignore
    except ImportError:
        raise RuntimeError("PyYAML required for rebuild_all_from_workbench")

    root = Path(repo_root)
    spec_cache = root / ".local" / "spec-cache"
    out_root = Path(output_dir) if output_dir else root / "reports" / "specification-authority-layer-mwp" / "context-pack-sample"
    out_root.mkdir(parents=True, exist_ok=True)

    _ODF_SHA = "92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066"

    _FORMAT_CONFIGS = {
        "fods": {"source_id": "FODS-SPEC-001", "title": "ODF 1.3 Part 3 Schema", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "fods" / "1.3" / "workbench" / "verified-facts-review.yaml"},
        "fodt": {"source_id": "FODT-SPEC-001", "title": "ODF 1.3 Part 3 Text Elements", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "fodt" / "odf-1.3" / "workbench" / "verified-facts-review.yaml"},
        "fodp": {"source_id": "FODP-SPEC-001", "title": "ODF 1.3 Part 3 Presentation", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "fodp" / "extracted" / "workbench" / "verified-facts-review.yaml"},
        "fodg": {"source_id": "FODG-SPEC-001", "title": "ODF 1.3 Part 3 Drawing", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "fodg" / "extracted" / "workbench" / "verified-facts-review.yaml"},
        "ods": {"source_id": "ODS-SPEC-001", "title": "ODF 1.3 Part 3 Spreadsheet", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "ods" / "extracted" / "workbench" / "verified-facts-review.yaml"},
        "odt": {"source_id": "ODT-SPEC-001", "title": "ODF 1.3 Part 3 Text Document", "source_type": "public_spec", "sha": _ODF_SHA, "wb": spec_cache / "odt" / "extracted" / "workbench" / "verified-facts-review.yaml"},
        "zst": {"source_id": "ZST-SPEC-001", "title": "RFC 8878 Zstandard Compression", "source_type": "rfc", "sha": "", "wb": spec_cache / "zst" / "rfc8878" / "workbench" / "verified-facts-review.yaml"},
    }

    packs = []
    for fmt_id, cfg in _FORMAT_CONFIGS.items():
        wb_path: Path = cfg["wb"]
        facts: List[Dict[str, Any]] = []
        if wb_path.is_file():
            try:
                data = yaml.safe_load(wb_path.read_text(encoding="utf-8")) or {}
                facts = data.get("facts", [])
            except Exception:
                facts = []

        # Build source record with verified SHA
        sha = cfg["sha"]
        if not sha and facts:
            sha = facts[0].get("source_sha256", "") or ""

        source_records: List[Dict[str, Any]] = [{
            "source_id": cfg["source_id"],
            "title": cfg["title"],
            "sha256": sha,
            "sections_count": len(facts),
            "source_type": cfg["source_type"],
        }]

        # Build requirement_summary from first 100 facts (no per-source cap)
        req_summary: List[Dict[str, Any]] = []
        for f in facts[:100]:
            claim_id = f.get("claim_id") or f.get("fact_id", "")
            claim_text = str(f.get("claim", ""))
            kw = "MUST" if "must" in claim_text.lower() else "SHALL"
            req_summary.append({
                "req_id": claim_id,
                "source_id": cfg["source_id"],
                "heading": str(f.get("section_id", "")),
                "keyword": kw,
                "text_fragment": claim_text[:150],
            })

        manifest_sha = _compute_manifest_sha256(source_records)
        context_pack_id = f"CP-{fmt_id.upper()}-{manifest_sha[:12]}"

        pack = ContextPack(
            context_pack_id=context_pack_id,
            format_id=fmt_id,
            manifest_sha256=manifest_sha,
            included_sources=source_records,
            requirement_summary=req_summary,
            index_terms=[],
            created_at=_now_iso(),
        )

        pack_path = out_root / f"{fmt_id}-context-pack.json"
        pack_dict = pack.to_dict()
        with open(pack_path, "w", encoding="utf-8") as fp:
            json.dump(pack_dict, fp, indent=2)
        pack.output_path = str(pack_path)

        manifest_path = out_root / f"{fmt_id}-manifest.json"
        manifest = {
            "context_pack_id": context_pack_id,
            "format_id": fmt_id,
            "sha256": manifest_sha,
            "sources": [s["source_id"] for s in source_records],
            "created_at": pack.created_at,
        }
        with open(manifest_path, "w", encoding="utf-8") as fp:
            json.dump(manifest, fp, indent=2)

        packs.append(pack)

    return packs


def format_sal_coverage_for_context_pack(format_id: Optional[str] = None) -> str:
    """Return a human-readable SAL coverage string for supervisor context packs.

    Returns empty string if coverage report is not available.
    """
    data = get_sal_coverage_summary(format_id)
    if data is None:
        return ""

    if format_id and "effective_verified" in data:
        return (
            f"SAL Fact Coverage ({format_id}): "
            f"{data['effective_verified']}/{data['total_registered']} verified "
            f"({data['coverage_percent']}%), {data['pending']} pending"
        )

    lines = [
        f"SAL Fact Coverage: {data['total_verified']}/{data['total_registered']} verified "
        f"({data['overall_coverage_percent']}%), {data['total_pending']} pending"
    ]
    for f in data.get("formats", []):
        lines.append(
            f"  [{f['format_id']}] {f['effective_verified']}/{f['total_registered']} "
            f"({f['coverage_percent']}%)"
        )
    return "\n".join(lines)
