"""
candidate_format_backlog.py -- Lane C Deliverable (FORMAT-FACTORY-R10)

Candidate Format Backlog Runtime for the format-factory governed planning layer.

PURPOSE:
  Load and classify the format candidate backlog from the format expansion roadmap.
  Supports:
  - Category classification
  - Support audit status classification
  - Spec availability classification
  - Expansion tier (near-term / short-term / long-term)
  - Individual format lookup

SAFETY RULES:
  - No internet fetch
  - No claiming unsupported_by_aspose=true unless verified (needs_audit by default)
  - All non-verified entries remain NEEDS_AUDIT
  - No advancing a format from NEEDS_AUDIT to READY without audit

CATEGORIES (13):
  word_processing, spreadsheet, presentation, archive, image,
  page_layout, cad_3d, gis, email_pim, project_management,
  game_voxel, ebook, audio_video

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

# Support audit status constants
AUDIT_STATUS_NEEDS_AUDIT = "needs_audit"
AUDIT_STATUS_AUDITED_SUPPORTED = "audited_supported"
AUDIT_STATUS_AUDITED_NOT_SUPPORTED = "audited_not_supported"
AUDIT_STATUS_AUDITED_PARTIAL = "audited_partial"

# Spec availability constants
SPEC_FULL_PUBLIC = "full_public"
SPEC_PARTIAL_PUBLIC = "partial_public"
SPEC_REVERSE_ENGINEERING = "reverse_engineering"
SPEC_COMMUNITY_DOCUMENTED = "community_documented"
SPEC_NONE = "none"
SPEC_UNKNOWN = "unknown"

# Expansion tier constants
TIER_A_NEAR_TERM = "TIER_A_NEAR_TERM"
TIER_B_MEDIUM_TERM = "TIER_B_MEDIUM_TERM"
TIER_C_LONG_TERM = "TIER_C_LONG_TERM"
TIER_ACTIVE = "TIER_ACTIVE"   # Already in governed pipeline

# Category constants
CATEGORY_WORD_PROCESSING = "word_processing"
CATEGORY_SPREADSHEET = "spreadsheet"
CATEGORY_PRESENTATION = "presentation"
CATEGORY_ARCHIVE = "archive"
CATEGORY_IMAGE = "image"
CATEGORY_PAGE_LAYOUT = "page_layout"
CATEGORY_CAD_3D = "cad_3d"
CATEGORY_GIS = "gis"
CATEGORY_EMAIL_PIM = "email_pim"
CATEGORY_PROJECT_MANAGEMENT = "project_management"
CATEGORY_GAME_VOXEL = "game_voxel"
CATEGORY_EBOOK = "ebook"
CATEGORY_AUDIO_VIDEO = "audio_video"

ALL_CATEGORIES = [
    CATEGORY_WORD_PROCESSING, CATEGORY_SPREADSHEET, CATEGORY_PRESENTATION,
    CATEGORY_ARCHIVE, CATEGORY_IMAGE, CATEGORY_PAGE_LAYOUT, CATEGORY_CAD_3D,
    CATEGORY_GIS, CATEGORY_EMAIL_PIM, CATEGORY_PROJECT_MANAGEMENT,
    CATEGORY_GAME_VOXEL, CATEGORY_EBOOK, CATEGORY_AUDIO_VIDEO,
]

# Governance flags
_GOVERNANCE_FLAGS = {
    "commercial_product_ready": False,
    "autonomous_execution_allowed": False,
    "gate_self_approval_allowed": False,
    "dry_run_only": True,
    "all_candidates_needs_audit_by_default": True,
    "unsupported_by_aspose_requires_audit": True,
}


def _stable_hash(data: Any) -> str:
    normalized = json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def _make_entry(
    format_id: str,
    extension: str,
    category: str,
    tier: str,
    spec_type: str,
    notes: str = "",
    audit_status: str = AUDIT_STATUS_NEEDS_AUDIT,
) -> dict:
    """Build a canonical backlog entry."""
    return {
        "format_id": format_id,
        "extension": extension,
        "category": category,
        "tier": tier,
        "spec_type": spec_type,
        "notes": notes,
        "audit_status": audit_status,
        "aspose_supported": None,  # None until audited
        "acquisition_state": "CANDIDATE",
    }


# ============================================================
# TIER A — Near-term public-spec expansion candidates
# ============================================================
TIER_A_CANDIDATES = [
    _make_entry("hwpx", ".hwpx", CATEGORY_WORD_PROCESSING, TIER_A_NEAR_TERM, SPEC_PARTIAL_PUBLIC,
                "Hancom Hangul XML/ZIP package. Partial public spec."),
    _make_entry("hwp", ".hwp", CATEGORY_WORD_PROCESSING, TIER_A_NEAR_TERM, SPEC_REVERSE_ENGINEERING,
                "Hancom Hangul binary. Requires careful audit."),
    _make_entry("hwt", ".hwt", CATEGORY_WORD_PROCESSING, TIER_A_NEAR_TERM, SPEC_PARTIAL_PUBLIC,
                "Hancom Hangul template. Partial public spec."),
    _make_entry("alz", ".alz", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_REVERSE_ENGINEERING,
                "ALZip archive. Reverse-engineering documented by community."),
    _make_entry("egg", ".egg", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_PARTIAL_PUBLIC,
                "ESTsoft EGG archive. Partial documentation available."),
    _make_entry("numbers", ".numbers", CATEGORY_SPREADSHEET, TIER_A_NEAR_TERM, SPEC_REVERSE_ENGINEERING,
                "Apple Numbers (iWork). No official public spec."),
    _make_entry("key", ".key", CATEGORY_PRESENTATION, TIER_A_NEAR_TERM, SPEC_REVERSE_ENGINEERING,
                "Apple Keynote (iWork). No official public spec."),
    _make_entry("pages", ".pages", CATEGORY_WORD_PROCESSING, TIER_A_NEAR_TERM, SPEC_REVERSE_ENGINEERING,
                "Apple Pages (iWork). No official public spec."),
    _make_entry("gnumeric", ".gnumeric", CATEGORY_SPREADSHEET, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "GNOME Gnumeric. Full public XML spec. Open source."),
    _make_entry("abw", ".abw", CATEGORY_WORD_PROCESSING, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "AbiWord. Full public XML spec. Open source."),
    _make_entry("xar", ".xar", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_PARTIAL_PUBLIC,
                "XAR archive format. Partial specification available."),
    _make_entry("lha", ".lha", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "LHA/LZH compression. Community-documented format."),
    _make_entry("lzh", ".lzh", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "LZH variant. Community-documented."),
    _make_entry("arj", ".arj", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_PARTIAL_PUBLIC,
                "ARJ archive. Partial documentation available."),
    _make_entry("zpaq", ".zpaq", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "ZPAQ archive. Full public specification."),
    _make_entry("zst", ".zst", CATEGORY_ARCHIVE, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "Zstandard compression. Full public RFC spec."),
    _make_entry("qoi", ".qoi", CATEGORY_IMAGE, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "Quite OK Image format. Minimal full public spec."),
    _make_entry("ora", ".ora", CATEGORY_IMAGE, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "OpenRaster. Full public XML ZIP spec. LGPL."),
    _make_entry("xcf", ".xcf", CATEGORY_IMAGE, TIER_A_NEAR_TERM, SPEC_FULL_PUBLIC,
                "GIMP native format. Fully documented."),
]

# ============================================================
# TIER B — Medium-term candidates
# ============================================================
TIER_B_CANDIDATES = [
    _make_entry("idml", ".idml", CATEGORY_PAGE_LAYOUT, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "InDesign IDML. XML-based, public spec."),
    _make_entry("indd", ".indd", CATEGORY_PAGE_LAYOUT, TIER_B_MEDIUM_TERM, SPEC_NONE,
                "InDesign binary. No public spec."),
    _make_entry("qxp", ".qxp", CATEGORY_PAGE_LAYOUT, TIER_B_MEDIUM_TERM, SPEC_NONE,
                "QuarkXPress. No public spec."),
    _make_entry("sla", ".sla", CATEGORY_PAGE_LAYOUT, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "Scribus. Full public XML spec. FOSS."),
    _make_entry("wpd", ".wpd", CATEGORY_WORD_PROCESSING, TIER_B_MEDIUM_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "WordPerfect. Community-documented."),
    _make_entry("wk1", ".wk1", CATEGORY_SPREADSHEET, TIER_B_MEDIUM_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "Lotus 1-2-3. Community-documented legacy format."),
    _make_entry("wk3", ".wk3", CATEGORY_SPREADSHEET, TIER_B_MEDIUM_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "Lotus 1-2-3 v3. Community-documented."),
    _make_entry("wk4", ".wk4", CATEGORY_SPREADSHEET, TIER_B_MEDIUM_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "Lotus 1-2-3 v4. Community-documented."),
    _make_entry("qpw", ".qpw", CATEGORY_SPREADSHEET, TIER_B_MEDIUM_TERM, SPEC_NONE,
                "Quattro Pro. No public spec."),
    _make_entry("skp", ".skp", CATEGORY_CAD_3D, TIER_B_MEDIUM_TERM, SPEC_NONE,
                "SketchUp. No public spec."),
    _make_entry("3dm", ".3dm", CATEGORY_CAD_3D, TIER_B_MEDIUM_TERM, SPEC_PARTIAL_PUBLIC,
                "Rhino 3DM. Partial documentation."),
    _make_entry("fcstd", ".fcstd", CATEGORY_CAD_3D, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "FreeCAD. Full public XML ZIP spec. FOSS."),
    _make_entry("mbtiles", ".mbtiles", CATEGORY_GIS, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "MBTiles. SQLite-based. Public spec."),
    _make_entry("pmtiles", ".pmtiles", CATEGORY_GIS, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "PMTiles. Cloud-optimized. Public spec."),
    _make_entry("osm", ".osm", CATEGORY_GIS, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "OpenStreetMap XML. Full public spec."),
    _make_entry("pbf", ".pbf", CATEGORY_GIS, TIER_B_MEDIUM_TERM, SPEC_FULL_PUBLIC,
                "OpenStreetMap Protobuf. Public spec."),
]

# ============================================================
# TIER C — Long-term advanced targets
# ============================================================
TIER_C_CANDIDATES = [
    _make_entry("sldprt", ".sldprt", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_NONE,
                "SolidWorks part file. No public spec."),
    _make_entry("sldasm", ".sldasm", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_NONE,
                "SolidWorks assembly. No public spec."),
    _make_entry("catpart", ".catpart", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_NONE,
                "CATIA V5 part. No public spec."),
    _make_entry("rvt", ".rvt", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_NONE,
                "Autodesk Revit. No public spec."),
    _make_entry("ifcxml", ".ifcxml", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_FULL_PUBLIC,
                "IFC XML BIM. Full public spec."),
    _make_entry("cr3", ".cr3", CATEGORY_IMAGE, TIER_C_LONG_TERM, SPEC_PARTIAL_PUBLIC,
                "Canon RAW v3. Partial reverse-engineering docs."),
    _make_entry("raf", ".raf", CATEGORY_IMAGE, TIER_C_LONG_TERM, SPEC_COMMUNITY_DOCUMENTED,
                "Fujifilm RAW. Community-documented."),
    _make_entry("gltf", ".gltf", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_FULL_PUBLIC,
                "GL Transmission Format. Full public spec."),
    _make_entry("glb", ".glb", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_FULL_PUBLIC,
                "GL Binary. Full public spec."),
    _make_entry("usd", ".usd", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_FULL_PUBLIC,
                "Universal Scene Description. Public spec from Pixar."),
    _make_entry("fbx", ".fbx", CATEGORY_CAD_3D, TIER_C_LONG_TERM, SPEC_PARTIAL_PUBLIC,
                "Autodesk FBX. Partial public documentation."),
    _make_entry("nsf", ".nsf", CATEGORY_EMAIL_PIM, TIER_C_LONG_TERM, SPEC_NONE,
                "Lotus Notes NSF. No public spec."),
    _make_entry("olm", ".olm", CATEGORY_EMAIL_PIM, TIER_C_LONG_TERM, SPEC_PARTIAL_PUBLIC,
                "Outlook for Mac. Partial documentation."),
    _make_entry("vox", ".vox", CATEGORY_GAME_VOXEL, TIER_C_LONG_TERM, SPEC_FULL_PUBLIC,
                "MagicaVoxel. Full public spec."),
]

# ============================================================
# ACTIVE formats (already in governed pipeline)
# ============================================================
ACTIVE_FORMATS = [
    {
        "format_id": "fods",
        "extension": ".fods",
        "category": CATEGORY_SPREADSHEET,
        "tier": TIER_ACTIVE,
        "spec_type": SPEC_FULL_PUBLIC,
        "notes": "Flat ODS XML. Active governed format. Gates 1-10 PASSED.",
        "audit_status": AUDIT_STATUS_AUDITED_SUPPORTED,
        "aspose_supported": True,
        "acquisition_state": "EVIDENCE_READY",
    },
    {
        "format_id": "fodt",
        "extension": ".fodt",
        "category": CATEGORY_WORD_PROCESSING,
        "tier": TIER_ACTIVE,
        "spec_type": SPEC_FULL_PUBLIC,
        "notes": "Flat ODT XML. Active governed format. Gates 1-10 PASSED.",
        "audit_status": AUDIT_STATUS_AUDITED_SUPPORTED,
        "aspose_supported": True,
        "acquisition_state": "EVIDENCE_READY",
    },
]

# Full backlog: all candidates + active formats
ALL_BACKLOG = ACTIVE_FORMATS + TIER_A_CANDIDATES + TIER_B_CANDIDATES + TIER_C_CANDIDATES


def get_backlog() -> list[dict]:
    """Return the full format backlog (immutable copy)."""
    return list(ALL_BACKLOG)


def get_candidates_by_tier(tier: str) -> list[dict]:
    """Return all candidates for a given tier."""
    if tier == TIER_ACTIVE:
        return list(ACTIVE_FORMATS)
    return [e for e in ALL_BACKLOG if e["tier"] == tier]


def get_candidates_by_category(category: str) -> list[dict]:
    """Return all candidates in a given category."""
    return [e for e in ALL_BACKLOG if e["category"] == category]


def get_candidates_by_audit_status(status: str) -> list[dict]:
    """Return all candidates with a given audit status."""
    return [e for e in ALL_BACKLOG if e["audit_status"] == status]


def get_candidates_by_spec_type(spec_type: str) -> list[dict]:
    """Return all candidates with a given spec type."""
    return [e for e in ALL_BACKLOG if e["spec_type"] == spec_type]


def get_format(format_id: str) -> dict | None:
    """Look up a single format by ID."""
    for entry in ALL_BACKLOG:
        if entry["format_id"] == format_id:
            return dict(entry)
    return None


def classify_backlog() -> dict:
    """
    Build a full classification of the backlog.

    Returns
    -------
    dict with:
      total_count: int
      by_tier: dict[str, int]
      by_category: dict[str, int]
      by_audit_status: dict[str, int]
      by_spec_type: dict[str, int]
      needs_audit_count: int
      active_count: int
      tier_a_count: int
      tier_b_count: int
      tier_c_count: int
      governance: dict
    """
    by_tier: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_audit_status: dict[str, int] = {}
    by_spec_type: dict[str, int] = {}

    for entry in ALL_BACKLOG:
        t = entry["tier"]
        by_tier[t] = by_tier.get(t, 0) + 1
        c = entry["category"]
        by_category[c] = by_category.get(c, 0) + 1
        a = entry["audit_status"]
        by_audit_status[a] = by_audit_status.get(a, 0) + 1
        s = entry["spec_type"]
        by_spec_type[s] = by_spec_type.get(s, 0) + 1

    return {
        "total_count": len(ALL_BACKLOG),
        "by_tier": by_tier,
        "by_category": by_category,
        "by_audit_status": by_audit_status,
        "by_spec_type": by_spec_type,
        "needs_audit_count": by_audit_status.get(AUDIT_STATUS_NEEDS_AUDIT, 0),
        "active_count": by_tier.get(TIER_ACTIVE, 0),
        "tier_a_count": by_tier.get(TIER_A_NEAR_TERM, 0),
        "tier_b_count": by_tier.get(TIER_B_MEDIUM_TERM, 0),
        "tier_c_count": by_tier.get(TIER_C_LONG_TERM, 0),
        "governance": dict(_GOVERNANCE_FLAGS),
    }


def validate_backlog_integrity() -> dict:
    """
    Validate backlog data integrity:
    - No format claims aspose_supported without audit
    - All non-verified entries are needs_audit
    - No duplicate format IDs
    - All required fields present

    Returns
    -------
    dict with:
      valid: bool
      violations: list[str]
    """
    violations = []
    seen_ids: set[str] = set()
    required_fields = {"format_id", "extension", "category", "tier", "spec_type",
                       "audit_status", "aspose_supported", "acquisition_state"}

    for entry in ALL_BACKLOG:
        fmt = entry.get("format_id", "UNKNOWN")

        # Duplicate check
        if fmt in seen_ids:
            violations.append(f"Duplicate format_id: {fmt}")
        seen_ids.add(fmt)

        # Required fields
        missing = required_fields - set(entry.keys())
        if missing:
            violations.append(f"{fmt}: missing required fields: {missing}")

        # Audit safety: aspose_supported must be None unless audited
        if entry.get("audit_status") == AUDIT_STATUS_NEEDS_AUDIT:
            if entry.get("aspose_supported") is not None:
                violations.append(
                    f"{fmt}: aspose_supported={entry['aspose_supported']} but audit_status=needs_audit. "
                    f"Cannot claim support status without audit."
                )

        # Category validity
        if entry.get("category") not in ALL_CATEGORIES:
            violations.append(f"{fmt}: invalid category '{entry.get('category')}'")

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "checked_count": len(ALL_BACKLOG),
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Candidate format backlog")
    parser.add_argument("action", nargs="?", default="classify",
                        choices=["classify", "validate", "tier-a", "tier-b", "tier-c",
                                 "active", "category", "format"])
    parser.add_argument("--category", help="Category filter")
    parser.add_argument("--format", help="Format ID lookup")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "classify":
        result = classify_backlog()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("=== Candidate Format Backlog Classification ===")
            print(f"  Total:     {result['total_count']}")
            print(f"  Active:    {result['active_count']}")
            print(f"  Tier A:    {result['tier_a_count']}")
            print(f"  Tier B:    {result['tier_b_count']}")
            print(f"  Tier C:    {result['tier_c_count']}")
            print(f"  Needs audit: {result['needs_audit_count']}")
            print(f"  Categories: {result['by_category']}")
    elif args.action == "validate":
        result = validate_backlog_integrity()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status = "PASS" if result["valid"] else "FAIL"
            print(f"  BACKLOG_INTEGRITY: {status} ({result['checked_count']} checked)")
            for v in result["violations"]:
                print(f"  VIOLATION: {v}")
    elif args.action in ("tier-a", "tier-b", "tier-c"):
        tier_map = {"tier-a": TIER_A_NEAR_TERM, "tier-b": TIER_B_MEDIUM_TERM, "tier-c": TIER_C_LONG_TERM}
        items = get_candidates_by_tier(tier_map[args.action])
        if args.json:
            print(json.dumps(items, indent=2))
        else:
            for item in items:
                print(f"  {item['extension']:12s} {item['category']:20s} {item['spec_type']:20s} {item['notes'][:60]}")
    elif args.action == "format" and args.format:
        item = get_format(args.format)
        if args.json:
            print(json.dumps(item, indent=2))
        else:
            print(f"  {item}" if item else f"  Not found: {args.format}")


if __name__ == "__main__":
    main()
