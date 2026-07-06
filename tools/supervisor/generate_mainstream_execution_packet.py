"""
generate_mainstream_execution_packet.py
Generates the Mainstream Execution Packet from tri-lane integration.

Sprint: FORMAT-FACTORY-TRI-LANE-INTEGRATION-FABRIC-001
Updated: FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001

The Mainstream execution packet is the final advisory feed from the tri-lane
integration into Mainstream product implementation. It contains:
- Per-family execution context (Supervisor route, Skills handoff, Acceleration advisory)
- Allowed and forbidden files
- Expected tests, dogfood output, transcript
- Proposed capability delta
- Validation commands (dotnet test only for .NET families â€” NO python pytest for .cs files)
- Stop conditions
- Rollback requirements

This packet does NOT:
- Authorize implementation (Mainstream does that)
- Mutate poc-targets.yaml
- Approve any gates
- Act as evidence (it is advisory)

Changes in v2 (refresh sprint):
- FODT TXT added as fourth required family
- FODT Markdown uses full finalization packet (not shell)
- Netpbm uses full finalization packet + Pipeline method capability (not shell)
- Acceleration source: hardening index (not product-first dir)
- Validation commands: only 'dotnet test --filter ...' for .NET families (never python pytest for .cs)
- Netpbm readiness: READY_FOR_EXECUTION_WITH_VALIDATION (advisory capability mismatch noted)

Usage:
    python tools/supervisor/generate_mainstream_execution_packet.py [--output <path>]

Exit codes:
    0  Packet generated (3+ families)
    1  Critical failure
    2  Packet generated with limitations (fewer than 3 families or partial data)
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import integration module
_here = Path(__file__).parent
sys.path.insert(0, str(_here))
from tri_lane_integration import run_integration, _project_root


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Per-family packet builders
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_FAMILY_SPEC = {
    "FODS": {
        "capability": "dogfood_status.fods_to_csv_dotnet",
        "gap_id": "GAP-FODS-DOGFOOD-CSV-DOTNET-001",
        "product_track": "commercial_net",
        "readiness": "READY_FOR_EXECUTION",
        "skills_packet_path": "reports/skills-product-first/mainstream-consumption-packet.json",
        "skills_packet_type": "full",
        "expected_dogfood_output": "CSV file produced from FODS spreadsheet using FodsDocument.ExportToCsv()",
        "expected_transcript": "reports/{sprint}/skill-transcripts/transcript-fods-csv-{id}.json",
        "validation_commands": [
            "dotnet test --filter FodsR114",
            "python tools/supervisor/validate_skill_transcript.py <transcript-path>",
        ],
        "allowed_files": [
            "src/net/fods/FodsDocument.cs",
            "src/net/fods/FodsWorkbook.cs",
            "tests/net/fods/FodsR114ExportToCsvTests.cs",
            "examples/net/fods/",
        ],
        "forbidden_files": [
            "src/python/",
            "registry/format-registry.yaml",
            "plans/master-plan.md",
            "product-capability-matrix/poc-targets.yaml",
        ],
        "expected_tests": "tests/net/fods/FodsR114ExportToCsvTests.cs with 8+ test methods",
        "proposed_capability_delta": {
            "file": "product-capability-matrix/poc-targets.yaml",
            "path": "fods.dogfood_status.fods_to_csv_dotnet",
            "proposed_status": "IMPLEMENTED",
            "requires_test_evidence": True,
            "proposed_only": True,
            "authority_note": "Do not write directly â€” requires test evidence and Mainstream product authority",
        },
    },
    "FODT": {
        # FODT Markdown â€” primary FODT capability
        "capability": "dogfood_status.fodt_to_markdown_dotnet",
        "gap_id": "GAP-FODT-DOGFOOD-MD-DOTNET-001",
        "product_track": "commercial_net",
        "readiness": "READY_FOR_EXECUTION",
        "skills_packet_path": "reports/skills-product-breadth-finalization/fodt-markdown-packet.json",
        "skills_packet_type": "full",
        "expected_dogfood_output": "Markdown file produced from FODT document using FodtDocument.ExportToMarkdown()",
        "expected_transcript": "reports/{sprint}/skill-transcripts/transcript-fodt-markdown-{id}.json",
        "validation_commands": [
            "dotnet test --filter FodtR114",
            "python tools/supervisor/validate_skill_transcript.py <transcript-path>",
        ],
        "allowed_files": [
            "src/net/fodt/FodtDocument.cs",
            "src/net/fodt/FodtMarkdownExporter.cs",
            "tests/net/fodt/FodtR114ExportToMarkdownTests.cs",
            "examples/net/fodt/",
        ],
        "forbidden_files": [
            "src/python/",
            "registry/format-registry.yaml",
            "plans/master-plan.md",
            "product-capability-matrix/poc-targets.yaml",
        ],
        "expected_tests": "tests/net/fodt/FodtR114ExportToMarkdownTests.cs with 8+ test methods",
        "proposed_capability_delta": {
            "file": "product-capability-matrix/poc-targets.yaml",
            "path": "fodt.dogfood_status.fodt_to_markdown_dotnet",
            "proposed_status": "IMPLEMENTED",
            "requires_test_evidence": True,
            "proposed_only": True,
            "authority_note": "Do not write directly â€” requires test evidence and Mainstream product authority",
        },
    },
    "FODT_TXT": {
        # FODT TXT â€” new in v2 (was missing from v1)
        "capability": "dogfood_status.fodt_to_txt_dotnet",
        "gap_id": "GAP-FODT-DOGFOOD-TXT-DOTNET-001",
        "product_track": "commercial_net",
        "readiness": "READY_FOR_EXECUTION",
        "skills_packet_path": "reports/skills-product-breadth-finalization/fodt-txt-packet.json",
        "skills_packet_type": "full",
        "expected_dogfood_output": "Plain text file produced from FODT document using FodtDocument.ExportToTxt()",
        "expected_transcript": "reports/{sprint}/skill-transcripts/transcript-fodt-txt-{id}.json",
        "validation_commands": [
            "dotnet test --filter FodtR114ExportToTxt",
            "python tools/supervisor/validate_skill_transcript.py <transcript-path>",
        ],
        "allowed_files": [
            "src/net/fodt/FodtDocument.cs",
            "src/net/fodt/FodtTxtExporter.cs",
            "tests/net/fodt/FodtR114ExportToTxtTests.cs",
            "examples/net/fodt/",
        ],
        "forbidden_files": [
            "src/python/",
            "registry/format-registry.yaml",
            "plans/master-plan.md",
            "product-capability-matrix/poc-targets.yaml",
        ],
        "expected_tests": "tests/net/fodt/FodtR114ExportToTxtTests.cs with 8+ test methods",
        "acceleration_advisory_note": "No acceleration advisory packet for FODT TXT â€” optional missing allowed per sprint spec",
        "proposed_capability_delta": {
            "file": "product-capability-matrix/poc-targets.yaml",
            "path": "fodt.dogfood_status.fodt_to_txt_dotnet",
            "proposed_status": "IMPLEMENTED",
            "requires_test_evidence": True,
            "proposed_only": True,
            "authority_note": "Do not write directly â€” requires test evidence and Mainstream product authority",
        },
    },
    "Netpbm": {
        "capability": "dotnet_status.netpbm_flip_and_merge_pipeline",
        "gap_id": "GAP-NETPBM-DOGFOOD-PIPELINE-DOTNET-001",
        "product_track": "commercial_net",
        "readiness": "READY_FOR_EXECUTION_WITH_VALIDATION",
        "skills_packet_path": "reports/skills-product-breadth-finalization/netpbm-proof-packet.json",
        "skills_packet_type": "full",
        "expected_dogfood_output": "Netpbm image produced using NetpbmImage.Pipeline() method chain (flip + merge steps)",
        "expected_transcript": "reports/{sprint}/skill-transcripts/transcript-netpbm-pipeline-{id}.json",
        "validation_commands": [
            "dotnet test --filter NetpbmR114",
            "python tools/supervisor/validate_skill_transcript.py <transcript-path>",
        ],
        "allowed_files": [
            "src/net/netpbm/Model/NetpbmImage.cs",
            "tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs",
            "examples/net/netpbm/",
        ],
        "forbidden_files": [
            "src/python/",
            "registry/format-registry.yaml",
            "plans/master-plan.md",
            "product-capability-matrix/poc-targets.yaml",
            "src/net/svg/",
        ],
        "expected_tests": "tests/net/netpbm/NetpbmR114FlipMergePipelineTests.cs with 8+ test methods",
        "svg_replacement_rejected": True,
        "svg_rejection_note": "SVG cannot replace Netpbm â€” format class mismatch (vector vs raster)",
        "acceleration_advisory_note": "Acceleration advisory targets flip_diagonal (already implemented R106). Skills target: Pipeline method at R114. Follow Skills handoff.",
        "proposed_capability_delta": {
            "file": "product-capability-matrix/poc-targets.yaml",
            "path": "netpbm.dotnet_status.netpbm_image_pipeline_dotnet",
            "proposed_status": "IMPLEMENTED",
            "requires_test_evidence": True,
            "proposed_only": True,
            "authority_note": "Do not write directly â€” requires test evidence and Mainstream product authority",
        },
    },
}


def build_family_packet(
    family: str,
    merged_entry: Dict[str, Any],
    spec: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the execution packet for a single family."""
    sup_routing = merged_entry.get("supervisor_routing", {})
    skills_handoff = merged_entry.get("skills_handoff", {})
    accel_advisory = merged_entry.get("acceleration_advisory", {})

    # Use spec for static configuration, augment with merged entry data
    packet = {
        "family": family,
        "capability": spec.get("capability", sup_routing.get("capability", "")),
        "gap_id": spec.get("gap_id", sup_routing.get("gap_id", "")),
        "product_track": spec.get("product_track", sup_routing.get("product_track", "")),
        "readiness": spec.get("readiness", sup_routing.get("readiness", "READY_FOR_EXECUTION_WITH_DISCOVERY")),
        "supervisor_route": {
            "source_file": sup_routing.get("routing_details", {}).get("source_file", ""),
            "git_status": sup_routing.get("routing_details", {}).get("git_status", ""),
            "family_active": sup_routing.get("routing_details", {}).get("family_active", True),
            "svg_replacement_rejected": spec.get("svg_replacement_rejected", False),
            "routing_note": spec.get("svg_rejection_note", ""),
            "authority_state": "routing_authority",
        },
        "skills_handoff": {
            "packet_type": spec.get("skills_packet_type", skills_handoff.get("packet_type", "full")),
            "packet_path": spec.get("skills_packet_path", skills_handoff.get("packet_path", "")),
            "skill": skills_handoff.get("skill", "add-dotnet-api"),
            "note": skills_handoff.get("note", ""),
            "authority_state": "governed_execution_authority",
        },
        "acceleration_advisory": {
            "packet_path": accel_advisory.get("packet_path", ""),
            "capability_path": accel_advisory.get("capability_path", ""),
            "authority_state": "ai_draft",
            "use_for": accel_advisory.get("use_for", "advisory reference only"),
            "non_authoritative": True,
        },
        "allowed_files": spec.get("allowed_files", sup_routing.get("allowed_files", [])),
        "forbidden_files": spec.get("forbidden_files", sup_routing.get("forbidden_files", [])),
        "expected_tests": spec.get("expected_tests", sup_routing.get("expected_tests", "")),
        "expected_dogfood_output": spec.get("expected_dogfood_output", ""),
        "expected_transcript": spec.get("expected_transcript", ""),
        "proposed_capability_delta": spec.get("proposed_capability_delta", {}),
        "validation_commands": spec.get("validation_commands", []),
        "stop_conditions": [
            "git push without SCM Agent policy authorization (AGENTS.md Â§AG4)",
            "Gate 11 G11-G approval without Babar Raza authorization",
            "product source edit outside allowed_files",
            "product-capability-matrix/poc-targets.yaml direct write",
            "AI output declared authoritative without test evidence",
            "SVG declared as Netpbm replacement",
        ],
        "rollback_requirements": [
            "If tests fail after source edit, revert the edit before re-attempting",
            "If governed transcript validation fails, do not declare evidence accepted",
            "If capability delta lacks test evidence, do not update poc-targets.yaml",
        ],
    }
    return packet


def generate_mainstream_execution_packet(root: Optional[Path] = None) -> Dict[str, Any]:
    """Generate the full Mainstream execution packet from tri-lane integration."""
    if root is None:
        root = _project_root()

    # Run integration
    integration_result = run_integration(root)

    limitations = list(integration_result.get("limitations", []))
    merged_families = integration_result.get("merged_families", {})
    active_families = {k: v for k, v in merged_families.items() if v.get("status") == "MERGED"}

    # Build per-family packets for the 3 required families
    family_packets: List[Dict[str, Any]] = []
    for family, spec in _FAMILY_SPEC.items():
        merged_entry = active_families.get(family, {})
        if not merged_entry:
            # Build with defaults from spec even if not in merged (partial integration)
            merged_entry = {
                "family": family,
                "status": "SPEC_ONLY",
                "supervisor_routing": {"routing_details": {}, "capability": spec["capability"], "readiness": "READY_WITH_DISCOVERY"},
                "skills_handoff": {"packet_type": "shell", "packet_path": "", "skill": ""},
                "acceleration_advisory": {"packet_path": "", "capability_path": spec["capability"], "use_for": "advisory"},
            }
            limitations.append(f"FAMILY_SPEC_ONLY: {family} not in merged integration â€” using spec defaults")
        packet = build_family_packet(family, merged_entry, spec)
        family_packets.append(packet)

    # Overall packet structure
    packet = {
        "packet_version": "2.0",
        "packet_v1_path": "reports/tri-lane-integration-fabric/mainstream-execution-packet.json",
        "sprint_id": "FORMAT-FACTORY-TRI-LANE-INTEGRATION-REFRESH-AND-MAINSTREAM-READINESS-GATE-001",
        "generated_at": "2026-06-04T00:00:00Z",
        "packet_type": "mainstream_execution_packet",
        "authority_state": "advisory",
        "non_authoritative": True,
        "requires_mainstream_product_authority": True,
        "integration_status": integration_result["status"],
        "acceleration_hardening_index_used": integration_result.get("acceleration_hardening_index_used", False),
        "skills_finalization_packets_loaded": integration_result.get("skills_finalization_packets_loaded", []),
        "family_count": len(family_packets),
        "families": family_packets,
        "global_stop_conditions": [
            "git push without SCM Agent policy authorization (AGENTS.md Â§AG4)",
            "Gate 11 G11-G self-approval (sole TRUE_EXTERNAL_GATE â€” Babar Raza only)",
            "product-capability-matrix/poc-targets.yaml direct write from this packet",
            "Acceleration advisory used as authoritative evidence without test validation",
            "External tool activated without MODE 4+ authorization",
        ],
        "global_rollback_requirements": [
            "All src/ changes must be reversible via git revert",
            "No gate states may be permanently mutated by Mainstream alone",
            "Evidence declaration requires supervisor autonomous-cycle validation",
        ],
        "authority_boundaries": {
            "supervisor": "routing_authority",
            "skills": "governed_execution_authority",
            "acceleration": "ai_draft (advisory only)",
            "mainstream": "product_implementation_authority (this stream implements)",
            "format_factory_gates": "human_authority (never self-approved)",
        },
        "limitations": limitations,
        "metadata": {
            "integration_result_status": integration_result["status"],
            "integration_active_families": len(active_families),
            "integration_limitations": integration_result.get("limitations", []),
            "source_lanes": integration_result.get("source_lanes", {}),
        },
    }

    return packet


def main() -> int:
    """CLI entry point."""
    root = _project_root()
    output_path: Optional[str] = None
    output_md_path: Optional[str] = None

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
        elif arg == "--output-md" and i + 1 < len(sys.argv):
            output_md_path = sys.argv[i + 1]

    packet = generate_mainstream_execution_packet(root)

    print("\n=== Mainstream Execution Packet ===")
    print(f"Sprint: {packet['sprint_id']}")
    print(f"Families: {packet['family_count']}")
    print(f"Integration status: {packet['integration_status']}")
    if packet["limitations"]:
        print(f"Limitations ({len(packet['limitations'])}):")
        for lim in packet["limitations"]:
            print(f"  - {lim}")

    for fam_pkt in packet["families"]:
        print(f"\n  [{fam_pkt['family']}]")
        print(f"    Capability: {fam_pkt['capability']}")
        print(f"    Skills handoff type: {fam_pkt['skills_handoff']['packet_type']}")
        print(f"    Acceleration advisory: {fam_pkt['acceleration_advisory']['authority_state']}")

    # Write JSON
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(packet, f, indent=2)
        print(f"\nJSON packet written to: {output_path}")

    # Write Markdown
    if output_md_path:
        md = build_markdown(packet)
        out_md = Path(output_md_path)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Markdown packet written to: {output_md_path}")

    # Exit code
    if packet["family_count"] < 3:
        return 2
    if packet["integration_status"] == "CRITICAL_INPUT_MISSING":
        return 1
    if packet["limitations"]:
        return 2
    return 0


def build_markdown(packet: Dict[str, Any]) -> str:
    """Build a Markdown rendering of the mainstream execution packet."""
    lines = [
        "# Mainstream Execution Packet",
        f"# Sprint: {packet['sprint_id']}",
        f"# Generated: {packet['generated_at']}",
        "",
        "> **Authority**: Advisory only. Mainstream product authority governs actual implementation.",
        "> Acceleration advisory is `ai_draft` and must NOT be used as evidence.",
        "> No gate approvals from this packet.",
        "",
        f"## Integration Status: `{packet['integration_status']}`",
        f"**Families**: {packet['family_count']}",
        "",
    ]

    if packet["limitations"]:
        lines.append("## Limitations")
        for lim in packet["limitations"]:
            lines.append(f"- {lim}")
        lines.append("")

    lines.append("## Families")
    lines.append("")

    for fam in packet["families"]:
        lines.append(f"### {fam['family']}")
        lines.append(f"- **Capability**: `{fam['capability']}`")
        lines.append(f"- **Gap ID**: `{fam['gap_id']}`")
        lines.append(f"- **Product track**: `{fam['product_track']}`")
        lines.append(f"- **Readiness**: `{fam['readiness']}`")
        lines.append("")
        lines.append("**Supervisor Route**")
        lines.append(f"- Source file: `{fam['supervisor_route'].get('source_file', '')}`")
        lines.append(f"- SVG replacement rejected: `{fam['supervisor_route'].get('svg_replacement_rejected', False)}`")
        lines.append(f"- Authority: `{fam['supervisor_route']['authority_state']}`")
        lines.append("")
        lines.append("**Skills Handoff**")
        lines.append(f"- Packet type: `{fam['skills_handoff']['packet_type']}`")
        lines.append(f"- Authority: `{fam['skills_handoff']['authority_state']}`")
        lines.append(f"- Note: {fam['skills_handoff']['note']}")
        lines.append("")
        lines.append("**Acceleration Advisory** *(ai_draft â€” not authoritative)*")
        lines.append(f"- Use for: {fam['acceleration_advisory']['use_for']}")
        lines.append(f"- Authority: `{fam['acceleration_advisory']['authority_state']}`")
        lines.append("")
        lines.append("**Allowed Files**")
        for f in fam["allowed_files"]:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append("**Forbidden Files**")
        for f in fam["forbidden_files"]:
            lines.append(f"- `{f}`")
        lines.append("")
        lines.append(f"**Expected Tests**: {fam['expected_tests']}")
        lines.append(f"**Expected Dogfood Output**: {fam['expected_dogfood_output']}")
        lines.append(f"**Expected Transcript**: `{fam['expected_transcript']}`")
        lines.append("")
        lines.append("**Proposed Capability Delta** *(proposed only â€” not a direct write)*")
        cd = fam.get("proposed_capability_delta", {})
        lines.append(f"- `{cd.get('path', '')}` â†’ `{cd.get('proposed_status', '')}`")
        lines.append(f"- Requires test evidence: `{cd.get('requires_test_evidence', True)}`")
        lines.append("")
        lines.append("**Validation Commands**")
        for cmd in fam["validation_commands"]:
            lines.append(f"```\n{cmd}\n```")
        lines.append("")
        lines.append("**Stop Conditions**")
        for sc in fam["stop_conditions"]:
            lines.append(f"- {sc}")
        lines.append("")

    lines.append("## Global Stop Conditions")
    for sc in packet["global_stop_conditions"]:
        lines.append(f"- {sc}")
    lines.append("")

    lines.append("## Authority Boundaries")
    for stream, boundary in packet["authority_boundaries"].items():
        lines.append(f"- **{stream}**: {boundary}")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
