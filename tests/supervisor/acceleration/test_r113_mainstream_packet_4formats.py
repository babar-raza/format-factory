"""TC-TEST-004: Mainstream Acceleration Packet tests — 4 formats."""

import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent

_FORMATS = [
    ("fods", "dogfood_status.fods_to_csv_dotnet", "commercial_net"),
    ("fodt", "dogfood_status.fodt_to_markdown_dotnet", "commercial_net"),
    ("netpbm", "dotnet_status.convert_format", "commercial_net"),
    ("sylk", "python_status.write_sylk", "foss_reduced"),
]


@pytest.fixture
def packets_dir(tmp_path):
    return tmp_path / "packets"


@pytest.mark.parametrize("format_id,cap_path,expected_track", _FORMATS)
def test_packet_produces_json(packets_dir, format_id, cap_path, expected_track):
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    packet = build_packet(format_id, cap_path, packets_dir, sprint_id="test")
    safe = cap_path.replace(".", "-").replace("/", "-")
    out = packets_dir / f"{format_id}-{safe}.json"
    assert out.exists(), f"Packet file missing: {out}"
    assert packet["authority_state"] == "ai_draft"
    assert packet["non_authoritative"] is True
    assert packet["requires_validation"] is True


@pytest.mark.parametrize("format_id,cap_path,expected_track", _FORMATS)
def test_packet_has_correct_product_track(packets_dir, format_id, cap_path, expected_track):
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    packet = build_packet(format_id, cap_path, packets_dir, sprint_id="test")
    assert packet["product_track"] == expected_track, (
        f"{format_id}: expected {expected_track}, got {packet['product_track']}"
    )


@pytest.mark.parametrize("format_id,cap_path,expected_track", _FORMATS)
def test_packet_has_external_tool_context(packets_dir, format_id, cap_path, expected_track):
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    packet = build_packet(format_id, cap_path, packets_dir, sprint_id="test")
    ext = packet.get("external_tool_context", {})
    assert ext.get("external_tool_activation_required_for_packet") is False
    assert ext.get("ghidra_mcp_applicable") is False
    assert ext.get("ruflo_context_available") is False
    assert ext["authority_state"] == "ai_draft"


@pytest.mark.parametrize("format_id,cap_path,expected_track", _FORMATS)
def test_packet_has_governance_rules(packets_dir, format_id, cap_path, expected_track):
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    packet = build_packet(format_id, cap_path, packets_dir, sprint_id="test")
    assert len(packet.get("governance_rules", [])) >= 5
    assert len(packet.get("downgrade_rules", [])) >= 3


def test_sylk_packet_is_foss_reduced(packets_dir):
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    packet = build_packet("sylk", "python_status.write_sylk", packets_dir, sprint_id="test")
    assert packet["product_track"] == "foss_reduced"


def test_no_src_files_created(packets_dir):
    src_before = set((_REPO / "src").rglob("*"))
    from tools.supervisor.mainstream_acceleration_packet import build_packet
    build_packet("fods", "dogfood_status.fods_to_csv_dotnet", packets_dir, sprint_id="test")
    src_after = set((_REPO / "src").rglob("*"))
    assert src_before == src_after
