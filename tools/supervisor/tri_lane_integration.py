"""
tri_lane_integration.py
Tri-Lane Integration Fabric

Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
Updated: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

Loads Supervisor, Skills, and Acceleration outputs, normalizes families and capability paths,
merges by target family, resolves conflicts, preserves authority boundaries,
and produces a Mainstream execution packet.

Conflict rules:
- Supervisor controls routing priority.
- Skills controls governed handoff structure.
- Acceleration contributes advisory design/test ideas only.
- Product source truth comes from Mainstream execution later.
- Capability readiness is not upgraded by integration alone.

Resolver priority (updated in refresh sprint):
- Skills FODS: reports/skills-product-first/mainstream-consumption-packet.json
- Skills FODT Markdown: reports/skills-product-breadth-finalization/fodt-markdown-packet.json
- Skills FODT TXT: reports/skills-product-breadth-finalization/fodt-txt-packet.json
- Skills Netpbm: reports/skills-product-breadth-finalization/netpbm-proof-packet.json
- Acceleration: reports/acceleration-hardening/mainstream-packet-index.json (with fallback to product-first)
- Supervisor: reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json
  (FODT/Netpbm Skills fields patched from finalization)

Usage:
    python tools/supervisor/tri_lane_integration.py [--output <packet.json>]

Exit codes:
    0  Integration packet produced successfully
    1  Critical input missing
    2  Integration produced with limitations
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ─────────────────────────────────────────────────────────────────────────────
# Path resolution
# ─────────────────────────────────────────────────────────────────────────────

def _project_root() -> Path:
    """Resolve project root relative to this file."""
    return Path(__file__).resolve().parent.parent.parent


def _resolve(rel: str) -> Path:
    return _project_root() / rel


# ─────────────────────────────────────────────────────────────────────────────
# Input loading
# ─────────────────────────────────────────────────────────────────────────────

SUPERVISOR_RECONCILIATION_PATH = "reports/supervisor-tri-lane-reconciliation/mainstream-readiness-packet.json"
SUPERVISOR_ROUTING_PATH = "reports/supervisor-streams/supervisor/routing-packet.json"
SKILLS_ROUTING_PATH = "reports/supervisor-streams/skills/routing-packet.json"
ACCELERATION_ROUTING_PATH = "reports/supervisor-streams/acceleration/routing-packet.json"

# Legacy acceleration directory — used as fallback only
ACCELERATION_PACKETS_DIR_LEGACY = "reports/acceleration-product-first/mainstream-consumption-packets"

# Preferred acceleration hardening index (v2 — updated in refresh sprint)
ACCELERATION_HARDENING_INDEX_PATH = "reports/acceleration-hardening/mainstream-packet-index.json"
ACCELERATION_HARDENING_REPLAY_DIR = "reports/acceleration-hardening/replay-run-2"

# Skills finalization paths — preferred over reconciliation-embedded shell packets
SKILLS_FODS_PACKET_PATH = "reports/skills-product-first/mainstream-consumption-packet.json"
SKILLS_FODT_MARKDOWN_PACKET_PATH = "reports/skills-product-breadth-finalization/fodt-markdown-packet.json"
SKILLS_FODT_TXT_PACKET_PATH = "reports/skills-product-breadth-finalization/fodt-txt-packet.json"
SKILLS_NETPBM_PACKET_PATH = "reports/skills-product-breadth-finalization/netpbm-proof-packet.json"

FAMILY_ALIASES = {
    "fods": "FODS",
    "fodt": "FODT",
    "netpbm": "Netpbm",
    "sylk": "SYLK",
    "zst": "ZST",
    "dif": "DIF",
    "pbm": "PBM",
    "pgm": "PGM",
    "ppm": "PPM",
}


def normalize_family(name: str) -> str:
    """Normalize family name to canonical form."""
    return FAMILY_ALIASES.get(name.lower(), name)


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file, returning None if not found."""
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_supervisor_reconciliation(root: Path) -> Tuple[Optional[Dict], bool]:
    """Load Supervisor tri-lane reconciliation packet."""
    p = root / SUPERVISOR_RECONCILIATION_PATH
    data = load_json(p)
    found = data is not None
    return data, found


def load_supervisor_routing(root: Path) -> Tuple[Optional[Dict], bool]:
    """Load Supervisor routing packet."""
    p = root / SUPERVISOR_ROUTING_PATH
    data = load_json(p)
    return data, data is not None


def load_skills_routing(root: Path) -> Tuple[Optional[Dict], bool]:
    """Load Skills routing packet."""
    p = root / SKILLS_ROUTING_PATH
    data = load_json(p)
    return data, data is not None


def load_acceleration_packets(root: Path) -> Dict[str, Dict[str, Any]]:
    """Load Acceleration consumption packets using hardening index if available.

    Priority:
    1. Prefer reports/acceleration-hardening/mainstream-packet-index.json
       → load packets from replay-run-2/ directory referenced by the index
    2. Fallback to reports/acceleration-product-first/mainstream-consumption-packets/
       only if hardening index is missing.

    Returns packets keyed by normalized family name.
    """
    hardening_index_path = root / ACCELERATION_HARDENING_INDEX_PATH
    hardening_index = load_json(hardening_index_path)

    if hardening_index is not None:
        # Preferred path: load from hardening index
        return _load_packets_from_hardening_index(root, hardening_index)

    # Fallback: legacy product-first directory
    return _load_packets_from_legacy_dir(root)


def _load_packets_from_hardening_index(
    root: Path, index: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """Load acceleration packets via the hardening index."""
    packets: Dict[str, Dict[str, Any]] = {}
    replay_dir = root / ACCELERATION_HARDENING_REPLAY_DIR

    for entry in index.get("packets", []):
        file_name = entry.get("file", "")
        fmt = entry.get("format", "")
        if not fmt:
            continue
        family = normalize_family(fmt)

        # Try to load from replay-run-2 directory first
        candidate = replay_dir / file_name
        if not candidate.exists():
            # Fall back to just the index entry data
            data = {
                "format": fmt,
                "capability_path": entry.get("capability_path", ""),
                "product_track": entry.get("product_track", "commercial_net"),
                "runtime_status": entry.get("runtime_status", "ok"),
                "directly_consumable": entry.get("directly_consumable", True),
                "authority_state": index.get("authority_state", "ai_draft"),
                "source": "hardening_index_metadata",
                "hardening_index_path": str(hardening_index_path_str(root)),
                "fallback_used": False,
            }
        else:
            data = load_json(candidate) or {}
            if not data:
                continue
            data["_hardening_index_file"] = str(candidate.relative_to(root))
            data["fallback_used"] = False

        # Ensure authority_state is ai_draft
        data["authority_state"] = "ai_draft"
        data["source_via_hardening_index"] = True
        packets[family] = data

    return packets


def hardening_index_path_str(root: Path) -> str:
    """Return the hardening index path as a relative string."""
    return ACCELERATION_HARDENING_INDEX_PATH


def _load_packets_from_legacy_dir(root: Path) -> Dict[str, Dict[str, Any]]:
    """Load acceleration packets from the legacy product-first directory (fallback)."""
    dir_path = root / ACCELERATION_PACKETS_DIR_LEGACY
    packets: Dict[str, Dict[str, Any]] = {}
    if not dir_path.exists():
        return packets
    for json_file in dir_path.glob("*.json"):
        try:
            data = load_json(json_file)
            if isinstance(data, dict) and "format" in data:
                family = normalize_family(data["format"])
                data["authority_state"] = "ai_draft"
                data["fallback_used"] = True
                data["source_via_legacy_dir"] = True
                packets[family] = data
        except (json.JSONDecodeError, Exception):
            pass
    return packets


# ─────────────────────────────────────────────────────────────────────────────
# Skills finalization resolver (dynamic latest-output resolver)
# ─────────────────────────────────────────────────────────────────────────────

class SelectedInput:
    """Records which input was selected and why."""
    def __init__(
        self,
        family: str,
        selected_path: str,
        source_sprint_id: str,
        freshness_status: str,
        reason_selected: str,
        fallback_used: bool = False,
        packet_type: str = "FULL",
    ):
        self.family = family
        self.selected_path = selected_path
        self.source_sprint_id = source_sprint_id
        self.freshness_status = freshness_status
        self.reason_selected = reason_selected
        self.fallback_used = fallback_used
        self.packet_type = packet_type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "family": self.family,
            "selected_path": self.selected_path,
            "source_sprint_id": self.source_sprint_id,
            "freshness_status": self.freshness_status,
            "reason_selected": self.reason_selected,
            "fallback_used": self.fallback_used,
            "packet_type": self.packet_type,
        }


def resolve_skills_inputs(
    root: Path,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, SelectedInput], List[str]]:
    """
    Resolve the latest Skills packets for each family.

    Priority:
    - FODS: skills-product-first/mainstream-consumption-packet.json (no newer FODS finalization)
    - FODT Markdown: skills-product-breadth-finalization/fodt-markdown-packet.json
    - FODT TXT: skills-product-breadth-finalization/fodt-txt-packet.json
    - Netpbm: skills-product-breadth-finalization/netpbm-proof-packet.json

    Shell packets from skills-governed-execution-hardening are REJECTED when finalization packets exist.

    Returns:
    - skills_packets: dict keyed by (family, sub_capability_key)
    - selections: dict of SelectedInput records
    - warnings: list of warning strings
    """
    skills_packets: Dict[str, Dict[str, Any]] = {}
    selections: Dict[str, SelectedInput] = {}
    warnings: List[str] = []

    # FODS
    fods_path = root / SKILLS_FODS_PACKET_PATH
    fods_data = load_json(fods_path)
    if fods_data:
        skills_packets["FODS"] = fods_data
        selections["FODS"] = SelectedInput(
            family="FODS",
            selected_path=SKILLS_FODS_PACKET_PATH,
            source_sprint_id=fods_data.get("sprint_id", "FORMAT-FACTORY-SKILLS-PRODUCT-FIRST-GOVERNED-EXECUTION-001"),
            freshness_status="LATEST_FOR_FODS",
            reason_selected="No newer FODS finalization packet; product-first packet is authoritative",
            fallback_used=False,
            packet_type="FULL",
        )
    else:
        warnings.append("FODS Skills packet not found — will use spec defaults")

    # FODT Markdown
    fodt_md_path = root / SKILLS_FODT_MARKDOWN_PACKET_PATH
    fodt_md_data = load_json(fodt_md_path)
    if fodt_md_data:
        skills_packets["FODT_MARKDOWN"] = fodt_md_data
        selections["FODT_MARKDOWN"] = SelectedInput(
            family="FODT",
            selected_path=SKILLS_FODT_MARKDOWN_PACKET_PATH,
            source_sprint_id=fodt_md_data.get("sprint_id", "FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001"),
            freshness_status="LATEST_FINALIZATION",
            reason_selected="Full finalization packet supersedes shell packet from skills-governed-execution-hardening",
            fallback_used=False,
            packet_type="FULL",
        )
    else:
        warnings.append("FODT Markdown Skills finalization packet not found — shell packets REJECTED")

    # FODT TXT
    fodt_txt_path = root / SKILLS_FODT_TXT_PACKET_PATH
    fodt_txt_data = load_json(fodt_txt_path)
    if fodt_txt_data:
        skills_packets["FODT_TXT"] = fodt_txt_data
        selections["FODT_TXT"] = SelectedInput(
            family="FODT",
            selected_path=SKILLS_FODT_TXT_PACKET_PATH,
            source_sprint_id=fodt_txt_data.get("sprint_id", "FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001"),
            freshness_status="LATEST_FINALIZATION",
            reason_selected="New in finalization sprint — FODT TXT capability previously missing from integration",
            fallback_used=False,
            packet_type="FULL",
        )
    else:
        warnings.append("FODT TXT Skills finalization packet not found")

    # Netpbm
    netpbm_path = root / SKILLS_NETPBM_PACKET_PATH
    netpbm_data = load_json(netpbm_path)
    if netpbm_data:
        skills_packets["Netpbm"] = netpbm_data
        selections["Netpbm"] = SelectedInput(
            family="Netpbm",
            selected_path=SKILLS_NETPBM_PACKET_PATH,
            source_sprint_id=netpbm_data.get("sprint_id", "FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001"),
            freshness_status="LATEST_FINALIZATION",
            reason_selected="Full finalization packet supersedes shell packet from skills-governed-execution-hardening",
            fallback_used=False,
            packet_type="FULL",
        )
    else:
        warnings.append("Netpbm Skills finalization packet not found — shell packets REJECTED")

    return skills_packets, selections, warnings


def emit_latest_input_selection(
    root: Path,
    skills_selections: Dict[str, SelectedInput],
    accel_packets: Dict[str, Dict],
    accel_fallback_used: bool,
    output_dir: str = "reports/tri-lane-integration-refresh",
) -> None:
    """Emit the latest-input-selection.json and .md to the refresh output directory."""
    selections_list = [sel.to_dict() for sel in skills_selections.values()]

    # Add acceleration selection entry
    accel_selection = {
        "family": "Acceleration (all families)",
        "selected_path": ACCELERATION_HARDENING_INDEX_PATH if not accel_fallback_used else ACCELERATION_PACKETS_DIR_LEGACY,
        "source_sprint_id": "FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001" if not accel_fallback_used else "FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001",
        "freshness_status": "LATEST_HARDENING" if not accel_fallback_used else "FALLBACK_LEGACY",
        "reason_selected": "Hardening index preferred" if not accel_fallback_used else "Hardening index missing — fallback to legacy dir",
        "fallback_used": accel_fallback_used,
        "packet_type": "index_with_packets",
    }
    selections_list.append(accel_selection)

    out = {
        "sprint_id": "FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001",
        "generated_at": "2026-06-04T00:00:00Z",
        "purpose": "Records which input was selected for each family and why",
        "acceleration_fallback_used": accel_fallback_used,
        "skills_selections": [s.to_dict() for s in skills_selections.values()],
        "acceleration_selection": accel_selection,
        "all_selections": selections_list,
        "stale_inputs_rejected": [
            {
                "path": "reports/skills-governed-execution-hardening/fodt-packet-shell.json",
                "reason": "Shell packet superseded by full finalization packet",
                "classification": "STALE_BLOCKING",
                "replaced_by": SKILLS_FODT_MARKDOWN_PACKET_PATH,
            },
            {
                "path": "reports/skills-governed-execution-hardening/netpbm-packet-shell.json",
                "reason": "Shell packet superseded by full finalization packet",
                "classification": "STALE_BLOCKING",
                "replaced_by": SKILLS_NETPBM_PACKET_PATH,
            },
            {
                "path": ACCELERATION_PACKETS_DIR_LEGACY,
                "reason": "Product-first dir superseded by hardening index (when index available)",
                "classification": "STALE_WITH_REPAIR_REQUIRED",
                "replaced_by": ACCELERATION_HARDENING_INDEX_PATH,
            },
        ],
    }

    out_dir = root / output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "latest-input-selection.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    md_lines = [
        "# Latest Input Selection",
        "# Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001",
        "",
        "## Skills Selections",
        "",
    ]
    for sel in skills_selections.values():
        d = sel.to_dict()
        md_lines.append(f"### {d['family']} — {d.get('selected_path', '').split('/')[-1]}")
        md_lines.append(f"- Path: `{d['selected_path']}`")
        md_lines.append(f"- Sprint: `{d['source_sprint_id']}`")
        md_lines.append(f"- Freshness: `{d['freshness_status']}`")
        md_lines.append(f"- Reason: {d['reason_selected']}")
        md_lines.append(f"- Fallback used: `{d['fallback_used']}`")
        md_lines.append("")

    md_lines.extend([
        "## Acceleration Selection",
        f"- Path: `{accel_selection['selected_path']}`",
        f"- Freshness: `{accel_selection['freshness_status']}`",
        f"- Fallback used: `{accel_selection['fallback_used']}`",
        "",
        "## Stale Inputs Rejected",
    ])
    for rej in out["stale_inputs_rejected"]:
        md_lines.append(f"- `{rej['path']}` — {rej['classification']}: {rej['reason']}")

    md_path = out_dir / "latest-input-selection.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines) + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# Normalization
# ─────────────────────────────────────────────────────────────────────────────

def extract_supervisor_families(reconciliation: Dict) -> Dict[str, Dict]:
    """Extract per-family routing data from the reconciliation packet."""
    families: Dict[str, Dict] = {}
    for cap in reconciliation.get("selected_capabilities", []):
        family = normalize_family(cap.get("family", ""))
        if family:
            families[family] = {
                "family": family,
                "capability": cap.get("capability", ""),
                "product_track": cap.get("product_track", ""),
                "gap_id": cap.get("gap_id", ""),
                "priority": cap.get("priority", 99),
                "readiness": cap.get("readiness", "UNKNOWN"),
                "supervisor_routing": cap.get("supervisor_routing", {}),
                "allowed_files": cap.get("allowed_files", []),
                "forbidden_files": cap.get("forbidden_files", []),
                "expected_tests": cap.get("expected_tests", ""),
                "proposed_delta": cap.get("proposed_delta", ""),
                "evidence_expectations": cap.get("evidence_expectations", []),
            }
    return families


def extract_skills_families(reconciliation: Dict) -> Dict[str, Dict]:
    """Extract per-family skills handoff data from the reconciliation packet."""
    families: Dict[str, Dict] = {}
    for cap in reconciliation.get("selected_capabilities", []):
        family = normalize_family(cap.get("family", ""))
        if family:
            sh = cap.get("skills_handoff", {})
            families[family] = {
                "family": family,
                "packet_type": sh.get("packet_type", "unknown"),
                "packet_path": sh.get("packet_path", sh.get("shell_path", "")),
                "skill": sh.get("skill", ""),
                "note": sh.get("note", ""),
            }
    return families


def extract_acceleration_families(accel_packets: Dict[str, Dict]) -> Dict[str, Dict]:
    """Normalize acceleration packets per family — always ai_draft."""
    families: Dict[str, Dict] = {}
    for family, pkt in accel_packets.items():
        cap_path = pkt.get("capability_path", pkt.get("selected_gap", ""))
        source_dir = (
            ACCELERATION_HARDENING_INDEX_PATH
            if pkt.get("source_via_hardening_index")
            else ACCELERATION_PACKETS_DIR_LEGACY
        )
        # Derive packet_path from hardening replay dir or legacy dir
        if pkt.get("_hardening_index_file"):
            pkt_path = pkt["_hardening_index_file"]
        elif pkt.get("source_via_hardening_index"):
            pkt_path = ACCELERATION_HARDENING_INDEX_PATH
        else:
            pkt_path = str(Path(ACCELERATION_PACKETS_DIR_LEGACY) / f"{family.lower()}-{cap_path.replace('.', '-').replace('_', '-')}.json")
        families[family] = {
            "family": family,
            "capability_path": cap_path,
            "packet_path": pkt_path,
            "authority_state": "ai_draft",
            "use_for": pkt.get("skills_handoff_compatibility", {}).get("note", "advisory reference only"),
            "directly_consumable": pkt.get("directly_consumable", False),
            "runtime_status": pkt.get("runtime_status", "unknown"),
            "source_via_hardening_index": pkt.get("source_via_hardening_index", False),
            "fallback_used": pkt.get("fallback_used", False),
        }
    return families


# ─────────────────────────────────────────────────────────────────────────────
# Merging and conflict resolution
# ─────────────────────────────────────────────────────────────────────────────

def merge_by_family(
    sup_families: Dict[str, Dict],
    skills_families: Dict[str, Dict],
    accel_families: Dict[str, Dict],
) -> Dict[str, Dict]:
    """Merge all three lane inputs by family. Supervisor controls routing priority.

    Special handling for FODT_TXT: Supervisor reconciliation does not have a FODT_TXT
    entry (it predates finalization). FODT_TXT is merged as MERGED_SKILLS_ONLY with
    Supervisor routing inherited from the FODT entry.
    """
    all_families = set(sup_families.keys()) | set(skills_families.keys())
    merged: Dict[str, Dict] = {}

    for family in sorted(all_families):
        sup_entry = sup_families.get(family, {})
        skills_entry = skills_families.get(family, {})
        # For acceleration, FODT_TXT maps to FODT acceleration advisory
        accel_family_key = "FODT" if family == "FODT_TXT" else family
        accel_entry = accel_families.get(accel_family_key, {})

        # Special case: FODT_TXT — inherit FODT supervisor routing
        if family == "FODT_TXT" and not sup_entry:
            sup_entry = sup_families.get("FODT", {})
            if sup_entry:
                # Override capability for FODT_TXT
                sup_entry = dict(sup_entry)
                sup_entry["capability"] = skills_entry.get("capability", "dogfood_status.fodt_to_txt_dotnet")
                sup_entry["gap_id"] = skills_entry.get("gap_id", "GAP-FODT-DOGFOOD-TXT-DOTNET-001")

        # Supervisor controls routing — if Supervisor has no entry, family is deprioritized
        if not sup_entry:
            merged[family] = {
                "family": family,
                "status": "SUPERVISOR_NOT_ROUTING",
                "skills_only": bool(skills_entry),
                "accel_advisory": accel_entry if accel_entry else None,
                "conflict_resolution": "Supervisor has no routing entry — deprioritized",
            }
            continue

        # Determine acceleration source path
        accel_source = (
            ACCELERATION_HARDENING_INDEX_PATH
            if accel_entry.get("source_via_hardening_index")
            else ACCELERATION_PACKETS_DIR_LEGACY
        )

        # Build merged entry
        merged[family] = {
            "family": family,
            "status": "MERGED",
            # Supervisor controls routing
            "supervisor_routing": {
                "source": SUPERVISOR_RECONCILIATION_PATH,
                "capability": sup_entry.get("capability", ""),
                "product_track": sup_entry.get("product_track", ""),
                "gap_id": sup_entry.get("gap_id", ""),
                "priority": sup_entry.get("priority", 99),
                "readiness": sup_entry.get("readiness", "UNKNOWN"),
                "allowed_files": sup_entry.get("allowed_files", []),
                "forbidden_files": sup_entry.get("forbidden_files", []),
                "expected_tests": sup_entry.get("expected_tests", ""),
                "proposed_delta": sup_entry.get("proposed_delta", ""),
                "routing_details": sup_entry.get("supervisor_routing", {}),
                "authority_state": "routing_authority",
            },
            # Skills controls governed execution — from finalization packets
            "skills_handoff": {
                "source": skills_entry.get("packet_path", SKILLS_ROUTING_PATH) if skills_entry else SKILLS_ROUTING_PATH,
                "packet_type": skills_entry.get("packet_type", "unavailable") if skills_entry else "unavailable",
                "packet_path": skills_entry.get("packet_path", "") if skills_entry else "",
                "skill": skills_entry.get("skill", "") if skills_entry else "",
                "note": skills_entry.get("note", "No Skills packet found") if skills_entry else "No Skills packet found",
                "capability": skills_entry.get("capability", "") if skills_entry else "",
                "gap_id": skills_entry.get("gap_id", "") if skills_entry else "",
                "authority_state": "governed_execution_authority",
            },
            # Acceleration is advisory only
            "acceleration_advisory": {
                "source": accel_source,
                "capability_path": accel_entry.get("capability_path", "") if accel_entry else "",
                "packet_path": accel_entry.get("packet_path", "") if accel_entry else "",
                "use_for": accel_entry.get("use_for", "not available") if accel_entry else "not available",
                "authority_state": "ai_draft",
                "non_authoritative": True,
                "source_via_hardening_index": accel_entry.get("source_via_hardening_index", False) if accel_entry else False,
                "advisory_note": (
                    "Acceleration advisory for FODT_TXT not available — capability not in hardening index"
                    if family == "FODT_TXT" and not accel_entry
                    else ""
                ),
            },
            "conflict_resolution": _resolve_conflicts(sup_entry, skills_entry, accel_entry),
        }

    return merged


def _resolve_conflicts(
    sup_entry: Dict,
    skills_entry: Dict,
    accel_entry: Dict,
) -> str:
    """Generate conflict resolution note for a family."""
    notes = []

    # Supervisor always takes routing priority
    notes.append("Supervisor controls routing priority")

    # Skills controls handoff structure
    if skills_entry:
        packet_type = skills_entry.get("packet_type", "unknown")
        notes.append(f"Skills handoff available (type={packet_type})")
    else:
        notes.append("Skills handoff unavailable — Mainstream must discover structure")

    # Acceleration is advisory
    if accel_entry:
        notes.append("Acceleration advisory available (ai_draft)")
    else:
        notes.append("Acceleration advisory not available")

    return "; ".join(notes)


# ─────────────────────────────────────────────────────────────────────────────
# Authority boundary enforcement
# ─────────────────────────────────────────────────────────────────────────────

def enforce_authority_boundaries(merged: Dict[str, Dict]) -> List[str]:
    """Verify authority boundaries are preserved in merged output. Returns violation messages."""
    violations = []
    for family, entry in merged.items():
        if entry.get("status") == "SUPERVISOR_NOT_ROUTING":
            continue

        # Acceleration must not be routing authority
        accel = entry.get("acceleration_advisory", {})
        if accel.get("authority_state") != "ai_draft":
            violations.append(
                f"{family}: acceleration_advisory authority_state='{accel.get('authority_state')}' must be 'ai_draft'"
            )

        # Skills must be governed_execution_authority
        skills = entry.get("skills_handoff", {})
        if skills.get("authority_state") != "governed_execution_authority":
            violations.append(
                f"{family}: skills_handoff authority_state='{skills.get('authority_state')}' must be 'governed_execution_authority'"
            )

        # Supervisor must be routing_authority
        sup = entry.get("supervisor_routing", {})
        if sup.get("authority_state") != "routing_authority":
            violations.append(
                f"{family}: supervisor_routing authority_state='{sup.get('authority_state')}' must be 'routing_authority'"
            )

    return violations


def check_netpbm_present(merged: Dict[str, Dict]) -> bool:
    """Verify Netpbm is present in merged output."""
    netpbm_keys = {k for k in merged if k.lower() in {"netpbm"}}
    return bool(netpbm_keys)


def check_svg_not_replacing_netpbm(merged: Dict[str, Dict]) -> bool:
    """SVG must not replace Netpbm."""
    has_svg = "SVG" in merged or "svg" in merged
    has_netpbm = check_netpbm_present(merged)
    if has_svg and not has_netpbm:
        return False  # SVG replacing Netpbm — violation
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main integration function
# ─────────────────────────────────────────────────────────────────────────────

def run_integration(root: Optional[Path] = None) -> Dict[str, Any]:
    """
    Main integration function. Returns the integration result as a dict.

    Updated in FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001:
    - Uses dynamic latest-output resolver for Skills (finalization packets preferred over shells)
    - Uses acceleration hardening index as primary (with fallback to legacy dir)
    - Patches stale Supervisor reconciliation FODT/Netpbm Skills fields with fresh finalization data
    - Emits latest-input-selection.json to refresh output directory

    Returns a dict with keys:
    - status: "OK" | "OK_WITH_LIMITATIONS" | "CRITICAL_INPUT_MISSING"
    - limitations: list of limitation strings
    - violations: list of authority boundary violations
    - merged_families: dict of merged family entries
    - metadata: sprint and source metadata
    """
    if root is None:
        root = _project_root()

    limitations: List[str] = []
    violations: List[str] = []

    # 1. Load Supervisor tri-lane reconciliation (primary routing input)
    recon, recon_found = load_supervisor_reconciliation(root)
    if not recon_found:
        return {
            "status": "CRITICAL_INPUT_MISSING",
            "limitations": ["Supervisor tri-lane reconciliation packet not found — cannot integrate"],
            "violations": [],
            "merged_families": {},
            "metadata": {
                "sprint_id": "FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001",
                "supervisor_reconciliation_found": False,
            },
        }

    # 2. Load Supervisor and Skills routing packets (for metadata)
    sup_routing, sup_routing_found = load_supervisor_routing(root)
    if not sup_routing_found:
        limitations.append("Supervisor routing packet not found — using reconciliation packet only")

    skills_routing, skills_routing_found = load_skills_routing(root)
    if not skills_routing_found:
        limitations.append("Skills routing packet not found — using finalization packets directly")

    # 3. Load Acceleration packets via hardening index (preferred) or legacy dir (fallback)
    accel_packets = load_acceleration_packets(root)
    accel_fallback_used = any(
        pkt.get("fallback_used", False) for pkt in accel_packets.values()
    )
    if not accel_packets:
        limitations.append("No Acceleration consumption packets found — advisory layer unavailable")
    elif accel_fallback_used:
        limitations.append(
            "ACCELERATION_FALLBACK_USED: Hardening index missing — loaded from legacy product-first directory"
        )

    # 4. Resolve latest Skills inputs (dynamic resolver — v2 update)
    skills_finalization_packets, skills_selections, skills_warnings = resolve_skills_inputs(root)
    for w in skills_warnings:
        limitations.append(f"SKILLS_RESOLVER_WARNING: {w}")

    # 5. Emit latest-input-selection report
    try:
        emit_latest_input_selection(root, skills_selections, accel_packets, accel_fallback_used)
    except Exception as e:
        limitations.append(f"SELECTION_REPORT_WRITE_FAILED: {e}")

    # 6. Normalize families from reconciliation packet (supervisor routing)
    sup_families = extract_supervisor_families(recon)

    # 7. Build skills families from RESOLVED finalization packets (not reconciliation shell data)
    skills_families = _build_skills_families_from_finalization(skills_finalization_packets)

    # 8. Normalize acceleration families
    accel_families = extract_acceleration_families(accel_packets)

    # 9. Merge by family (now includes FODT_TXT as separate entry if present)
    merged = merge_by_family(sup_families, skills_families, accel_families)

    # 10. Enforce authority boundaries
    violations = enforce_authority_boundaries(merged)
    if violations:
        limitations.append(f"Authority boundary violations detected: {violations}")

    # 11. Verify Netpbm present
    if not check_netpbm_present(merged):
        limitations.append("NETPBM_MISSING_FROM_INTEGRATION: Netpbm not in merged families")

    # 12. Verify SVG not replacing Netpbm
    if not check_svg_not_replacing_netpbm(merged):
        limitations.append("SVG_REPLACING_NETPBM_DETECTED: SVG present but Netpbm absent")

    # 13. Determine status
    active_families = {k: v for k, v in merged.items() if v.get("status") == "MERGED"}
    if len(active_families) < 3:
        limitations.append(
            f"INSUFFICIENT_FAMILIES: Only {len(active_families)} merged families, need 3+"
        )

    status = "OK" if not limitations else "OK_WITH_LIMITATIONS"

    # Authority boundaries block
    authority_boundaries = {
        "supervisor": "Stream-control authority — routing decisions, continuation states, cross-stream status",
        "skills": "Governed execution authority — handoff templates, transcript validation, dry-run contracts",
        "acceleration": "Advisory only — ai_draft outputs, require deterministic validation before use as evidence",
        "mainstream": "Product implementation authority — source changes, tests, dogfood, capability delta proposals",
        "format_factory_gates": "Human authority — Gate 8 and Gate 11 require human approval (never self-approved)",
    }

    return {
        "status": status,
        "limitations": limitations,
        "violations": violations,
        "merged_families": merged,
        "active_family_count": len(active_families),
        "authority_boundaries": authority_boundaries,
        "skills_finalization_packets_loaded": list(skills_finalization_packets.keys()),
        "acceleration_hardening_index_used": not accel_fallback_used,
        "metadata": {
            "sprint_id": "FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001",
            "integration_tool": "tri_lane_integration.py",
            "supervisor_reconciliation_found": True,
            "supervisor_reconciliation_path": SUPERVISOR_RECONCILIATION_PATH,
            "supervisor_routing_found": sup_routing_found,
            "skills_routing_found": skills_routing_found,
            "acceleration_packets_found": len(accel_packets),
            "acceleration_fallback_used": accel_fallback_used,
            "families_in_reconciliation": list(sup_families.keys()),
            "skills_finalization_families_loaded": list(skills_finalization_packets.keys()),
            "acceleration_families_loaded": list(accel_families.keys()),
        },
        "source_lanes": {
            "supervisor": {
                "reconciliation_path": SUPERVISOR_RECONCILIATION_PATH,
                "routing_path": SUPERVISOR_ROUTING_PATH,
                "authority": "routing_authority",
            },
            "skills": {
                "fods_packet": SKILLS_FODS_PACKET_PATH,
                "fodt_markdown_packet": SKILLS_FODT_MARKDOWN_PACKET_PATH,
                "fodt_txt_packet": SKILLS_FODT_TXT_PACKET_PATH,
                "netpbm_packet": SKILLS_NETPBM_PACKET_PATH,
                "authority": "governed_execution_authority",
                "resolver_version": "v2_finalization",
            },
            "acceleration": {
                "hardening_index": ACCELERATION_HARDENING_INDEX_PATH,
                "legacy_fallback": ACCELERATION_PACKETS_DIR_LEGACY,
                "authority": "ai_draft",
                "non_authoritative": True,
            },
        },
    }


def _build_skills_families_from_finalization(
    finalization_packets: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Build skills families dict from resolved finalization packets.

    Maps finalization packet keys to family entries used by merge_by_family.
    Handles FODT_MARKDOWN and FODT_TXT as separate sub-capability entries under FODT.
    """
    families: Dict[str, Dict[str, Any]] = {}

    # FODS
    fods = finalization_packets.get("FODS")
    if fods:
        families["FODS"] = {
            "family": "FODS",
            "packet_type": fods.get("packet_type", "FULL").lower(),
            "packet_path": SKILLS_FODS_PACKET_PATH,
            "skill": fods.get("recommended_skill", "add-dotnet-api"),
            "note": "Full FODS packet from skills-product-first sprint",
            "capability": fods.get("selected_product_gap", {}).get("capability", "dogfood_status.fods_to_csv_dotnet"),
            "gap_id": fods.get("selected_product_gap", {}).get("gap_id", "GAP-FODS-DOGFOOD-CSV-DOTNET-001"),
        }

    # FODT Markdown (primary FODT entry)
    fodt_md = finalization_packets.get("FODT_MARKDOWN")
    if fodt_md:
        families["FODT"] = {
            "family": "FODT",
            "packet_type": fodt_md.get("packet_type", "FULL").lower(),
            "packet_path": SKILLS_FODT_MARKDOWN_PACKET_PATH,
            "skill": fodt_md.get("recommended_skill", "add-dotnet-api"),
            "note": "Full FODT Markdown packet from skills-product-breadth-finalization sprint",
            "capability": fodt_md.get("capability", "dogfood_status.fodt_to_markdown_dotnet"),
            "gap_id": fodt_md.get("gap_id", "GAP-FODT-DOGFOOD-MD-DOTNET-001"),
        }

    # FODT TXT (separate entry)
    fodt_txt = finalization_packets.get("FODT_TXT")
    if fodt_txt:
        families["FODT_TXT"] = {
            "family": "FODT_TXT",
            "packet_type": fodt_txt.get("packet_type", "FULL").lower(),
            "packet_path": SKILLS_FODT_TXT_PACKET_PATH,
            "skill": fodt_txt.get("recommended_skill", "add-dotnet-api"),
            "note": "Full FODT TXT packet from skills-product-breadth-finalization sprint (new in refresh)",
            "capability": fodt_txt.get("capability", "dogfood_status.fodt_to_txt_dotnet"),
            "gap_id": fodt_txt.get("gap_id", "GAP-FODT-DOGFOOD-TXT-DOTNET-001"),
        }

    # Netpbm
    netpbm = finalization_packets.get("Netpbm")
    if netpbm:
        families["Netpbm"] = {
            "family": "Netpbm",
            "packet_type": netpbm.get("packet_type", "FULL").lower(),
            "packet_path": SKILLS_NETPBM_PACKET_PATH,
            "skill": netpbm.get("recommended_skill", "add-dotnet-api"),
            "note": "Full Netpbm packet from skills-product-breadth-finalization sprint (upgraded from shell)",
            "capability": netpbm.get("capability", "dotnet_status.netpbm_flip_and_merge_pipeline"),
            "gap_id": netpbm.get("gap_id", "GAP-NETPBM-DOGFOOD-PIPELINE-DOTNET-001"),
        }

    return families


def main() -> int:
    """CLI entry point."""
    root = _project_root()
    output_path_str: Optional[str] = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_path_str = sys.argv[i + 1]

    result = run_integration(root)

    # Print summary
    print("\n=== Tri-Lane Integration (Refresh v2) ===")
    print(f"Status: {result['status']}")
    print(f"Active families: {result.get('active_family_count', 0)}")
    print(f"Acceleration hardening index used: {result.get('acceleration_hardening_index_used', False)}")
    print(f"Skills finalization packets: {result.get('skills_finalization_packets_loaded', [])}")
    if result["limitations"]:
        print(f"Limitations ({len(result['limitations'])}):")
        for lim in result["limitations"]:
            print(f"  - {lim}")
    if result["violations"]:
        print(f"Violations ({len(result['violations'])}):")
        for v in result["violations"]:
            print(f"  - {v}")

    families = result.get("merged_families", {})
    if families:
        print(f"\nMerged families ({len(families)}):")
        for family, entry in sorted(families.items()):
            status = entry.get("status", "?")
            cap = entry.get("supervisor_routing", {}).get("capability", "")
            print(f"  [{status}] {family}: {cap}")

    # Write output if requested
    if output_path_str:
        out_path = Path(output_path_str)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"\nIntegration result written to: {output_path_str}")

    # Exit code
    status = result["status"]
    if status == "CRITICAL_INPUT_MISSING":
        return 1
    if status == "OK_WITH_LIMITATIONS":
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
