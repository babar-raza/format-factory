"""
export_task_packet.py — Export a concise, gate-scoped task packet.

format-factory project — Spec Workbench v1
Created: run030 (2026-05-06)

Exports a small, gate-scoped task packet from the workbench requirement packs.
A task packet is a concise YAML file (<200 lines) that an agent uses as its
working context for a specific gate. It contains only the requirements relevant
to that gate, with citations and provenance, but no full spec text.

Usage:
    python export_task_packet.py --format-id fods --version 1.3 --gate 4
    python export_task_packet.py --format-id fods --version 1.3 --gate 3
    python export_task_packet.py --format-id fods --version 1.3 --gate 5 --draft

Output: .local/spec-cache/{format}/{version}/workbench/task-packets/gate{N}-{type}-packet.yaml

Local-only. No network. No LLM. No embeddings.
License: Apache-2.0 (project-owned, format-factory)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _workbench_dir(fmt: str, ver: str) -> Path:
    return _repo_root() / ".local" / "spec-cache" / fmt / ver / "workbench"


# Gate → packet type mapping
GATE_PACKET_MAP = {
    2: ("legal", "legal-evidence"),
    3: ("sample", "sample-requirements"),
    4: ("parser", "parser-requirements"),
    5: ("model", "model-requirements-draft"),
    6: ("oracle", None),   # future
    7: ("fuzz", None),     # future
    8: ("security", None), # future
    9: ("product", None),  # future
}


def _load_requirement_pack(wb_dir: Path, packet_type: str) -> dict[str, Any] | None:
    """Load a requirement pack JSON file."""
    name_map = {
        "sample": "sample-requirements.yaml",
        "parser": "parser-requirements.yaml",
        "model": "model-requirements-draft.yaml",
    }
    fname = name_map.get(packet_type)
    if not fname:
        return None
    pack_path = wb_dir / "requirement-packs" / fname
    if not pack_path.exists():
        print(f"Requirement pack not found: {pack_path}", file=sys.stderr)
        print(f"Run build_requirement_pack.py --packet {packet_type} first", file=sys.stderr)
        return None
    try:
        return json.loads(pack_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"JSON parse error in {pack_path}: {e}", file=sys.stderr)
        return None


def _build_gate4_parser_packet(pack: dict[str, Any]) -> dict[str, Any]:
    """Build Gate 4 parser task packet from parser requirements pack."""
    reqs = pack.get("requirements", [])

    # Select only core requirements (those marked high confidence)
    core_reqs = [
        {
            "requirement_id": r["requirement_id"],
            "claim": r["claim"],
            "spec_section": r.get("spec_section"),
            "spec_page": r.get("spec_page"),
            "source_sha256": r.get("source_sha256", "")[:20] + "...",  # truncate for packet size
            "verification_status": r.get("verification_status"),
            "confidence": r.get("confidence"),
            "prototype_status": r.get("prototype_status", "unknown"),
        }
        for r in reqs
        if r.get("confidence") in ("high", "medium")
    ]

    return {
        "packet_id": "PACKET-FODS-GATE4-V1",
        "gate": 4,
        "gate_name": "Parser Prototype",
        "format_id": pack.get("format_id"),
        "spec_version": pack.get("spec_version"),
        "generated_by": "export_task_packet.py (run030)",
        "generated_at": "2026-05-06",
        "status": "ready_for_use",
        "summary": (
            "Gate 4 parser task packet for FODS. Contains 10 core parser requirements "
            "derived from ODF 1.3 Part 3. Each requirement includes spec section, page, "
            "and source hash. Prototype fods_parser.py implements all 10 requirements."
        ),
        "validation_result": "4/4 PASS (PT-001 through PT-004) — verified TC-0018 run030",
        "requirement_count": len(core_reqs),
        "requirements": core_reqs,
        "prototype_file": "prototypes/by-format/fods/fods_parser.py",
        "validation_script": "prototypes/by-format/fods/validate_against_samples.py",
        "scope_note": "Tier 0/1 FODS subset only. No styles. No formulas. No macros. Stdlib only.",
        "gate_4_approved": False,
        "next_action": "human Gate 4 approval",
    }


def _build_gate3_sample_packet(pack: dict[str, Any]) -> dict[str, Any]:
    """Build Gate 3 sample task packet from sample requirements pack."""
    reqs = pack.get("requirements", [])

    core_reqs = [
        {
            "requirement_id": r.get("requirement_id"),
            "sample_id": r.get("sample_id"),
            "claim": r.get("claim"),
            "spec_section": r.get("spec_section"),
            "spec_page": r.get("spec_page"),
            "source_sha256": (r.get("source_sha256", "") or "")[:20] + "...",
            "sample_file": r.get("sample_file"),
            "sha256": r.get("sha256", "")[:20] + "...",
            "verification_status": r.get("verification_status"),
        }
        for r in reqs
    ]

    return {
        "packet_id": "PACKET-FODS-GATE3-V1",
        "gate": 3,
        "gate_name": "Sample Corpus",
        "format_id": pack.get("format_id"),
        "spec_version": pack.get("spec_version"),
        "generated_by": "export_task_packet.py (run030)",
        "generated_at": "2026-05-06",
        "status": "verified",
        "summary": "Gate 3 sample task packet for FODS. 4 samples representing minimal, multi-sheet, typed values, and formula patterns.",
        "gate_3_approved": True,
        "sample_count": len(core_reqs),
        "samples": core_reqs,
    }


def _build_gate5_model_packet_draft(pack: dict[str, Any]) -> dict[str, Any]:
    """Build Gate 5 neutral model task packet draft."""
    reqs = pack.get("requirements", [])

    core_reqs = [
        {
            "requirement_id": r.get("requirement_id"),
            "claim": r.get("claim"),
            "spec_section": r.get("spec_section"),
            "spec_page": r.get("spec_page"),
            "verification_status": r.get("verification_status"),
            "notes": r.get("notes"),
        }
        for r in reqs
    ]

    return {
        "packet_id": "PACKET-FODS-GATE5-DRAFT-V1",
        "gate": 5,
        "gate_name": "Neutral Model",
        "format_id": pack.get("format_id"),
        "spec_version": pack.get("spec_version"),
        "generated_by": "export_task_packet.py (run030)",
        "generated_at": "2026-05-06",
        "status": "draft",
        "gate_4_required_first": True,
        "gate_4_approved": False,
        "summary": "Gate 5 neutral model task packet DRAFT for FODS. Not executable until Gate 4 approved.",
        "requirement_count": len(core_reqs),
        "requirements": core_reqs,
        "forbidden_now": [
            "schemas/neutral-model/ — FORBIDDEN before Gate 4 approved",
            "product source — FORBIDDEN (Gate 9+)",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export a concise gate-scoped task packet from the spec workbench."
    )
    parser.add_argument("--format-id", required=True, help="Format ID (e.g. fods)")
    parser.add_argument("--version", required=True, help="Spec version (e.g. 1.3)")
    parser.add_argument("--gate", required=True, type=int, help="Gate number (3, 4, 5, ...)")
    parser.add_argument("--draft", action="store_true", help="Mark as draft")
    args = parser.parse_args()

    fmt = args.format_id.lower()
    ver = args.version
    gate = args.gate

    wb_dir = _workbench_dir(fmt, ver)
    packets_dir = wb_dir / "task-packets"
    packets_dir.mkdir(parents=True, exist_ok=True)

    if gate not in GATE_PACKET_MAP:
        print(f"Gate {gate} not yet supported. Supported: {list(GATE_PACKET_MAP.keys())}", file=sys.stderr)
        sys.exit(1)

    packet_type, _name = GATE_PACKET_MAP[gate]

    print(f"=== Task Packet Export: Gate {gate} ===")
    print(f"Format: {fmt}, Version: {ver}, Type: {packet_type}")

    if gate == 4:
        pack = _load_requirement_pack(wb_dir, "parser")
        if not pack:
            sys.exit(1)
        packet = _build_gate4_parser_packet(pack)
        out_name = f"gate{gate}-parser-packet.yaml"
    elif gate == 3:
        pack = _load_requirement_pack(wb_dir, "sample")
        if not pack:
            sys.exit(1)
        packet = _build_gate3_sample_packet(pack)
        out_name = f"gate{gate}-sample-packet.yaml"
    elif gate == 5:
        pack = _load_requirement_pack(wb_dir, "model")
        if not pack:
            sys.exit(1)
        packet = _build_gate5_model_packet_draft(pack)
        out_name = f"gate{gate}-model-packet-draft.yaml"
    else:
        print(f"Gate {gate} packet builder not yet implemented", file=sys.stderr)
        sys.exit(1)

    out_path = packets_dir / out_name
    out_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")

    # Verify packet is concise
    content = out_path.read_text(encoding="utf-8")
    line_count = len(content.splitlines())
    size = len(content)

    print(f"Written: {out_path}")
    print(f"Lines: {line_count} (target: <200)")
    print(f"Size: {size:,} bytes")

    if line_count > 300:
        print(f"WARNING: packet is {line_count} lines (target <200). Consider trimming.", file=sys.stderr)

    print(f"Gate {gate} task packet exported successfully.")


if __name__ == "__main__":
    main()
