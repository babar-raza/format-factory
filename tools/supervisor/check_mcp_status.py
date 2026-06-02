"""
check_mcp_status.py — MCP Status Classifier

Classifies the MCP (Model Context Protocol) status based on:
1. Physical file presence (.vscode/mcp.json)
2. Supervisor mode from config.yaml
3. Server configuration content

Classifications:
  MCP_DISABLED          — MODE < 4 (not yet authorized)
  MCP_CONFIG_MISSING    — MODE >= 4 but .vscode/mcp.json not found
  MCP_CONFIG_PRESENT_NOT_ACTIVE — .vscode/mcp.json present, MODE < 4
  MCP_CONFIG_PRESENT_MODE4_ACTIVE — .vscode/mcp.json present + MODE 4+
  MCP_MISCONFIGURED     — .vscode/mcp.json present but malformed

Writes:
  reports/supervisor/mcp-status.md

Exit codes:
  0 — check complete
  9 — unexpected error

Usage:
  python tools/supervisor/check_mcp_status.py
  python tools/supervisor/check_mcp_status.py --repo-root .
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def read_current_mode(repo_root: Path) -> int:
    config_path = repo_root / ".supervisor" / "config.yaml"
    if not config_path.exists():
        return 0
    text = config_path.read_text(encoding="utf-8")
    m = re.search(r"Status:\s*MODE\s*(\d+)", text, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def check_mcp_status(repo_root: Path) -> dict:
    """Check and classify MCP status."""
    mcp_path = repo_root / ".vscode" / "mcp.json"
    mode = read_current_mode(repo_root)
    timestamp = datetime.now().isoformat()

    # Case 1: MODE < 4, file might not exist
    if not mcp_path.exists():
        if mode < 4:
            classification = "MCP_DISABLED"
            description = f"MODE {mode} — MCP not yet authorized. Requires MODE 4+ approval from user."
        else:
            classification = "MCP_CONFIG_MISSING"
            description = f"MODE {mode} — MCP authorized but .vscode/mcp.json not found. Recreate the file."
        return {
            "classification": classification,
            "file_present": False,
            "file_path": str(mcp_path),
            "mode": mode,
            "server_count": 0,
            "servers": [],
            "description": description,
            "timestamp": timestamp,
        }

    # Case 2: File present — check content
    try:
        mcp_data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {
            "classification": "MCP_MISCONFIGURED",
            "file_present": True,
            "file_path": str(mcp_path),
            "mode": mode,
            "server_count": 0,
            "servers": [],
            "description": f"MCP config present but JSON invalid: {e}",
            "timestamp": timestamp,
        }

    servers = mcp_data.get("servers", mcp_data.get("mcpServers", {}))
    if isinstance(servers, dict):
        server_list = [
            {"name": k, "type": v.get("type", "?"), "command": v.get("command", "?")}
            for k, v in servers.items()
        ]
        server_count = len(server_list)
    else:
        server_list = []
        server_count = 0

    if mode >= 4:
        classification = "MCP_CONFIG_PRESENT_MODE4_ACTIVE"
        description = (
            f"MODE {mode} — MCP authorized and config present. "
            f"{server_count} server(s) configured: {', '.join(s['name'] for s in server_list)}."
        )
    else:
        classification = "MCP_CONFIG_PRESENT_NOT_ACTIVE"
        description = (
            f"MODE {mode} — MCP config present but MODE < 4 (not yet activated). "
            f"User approval required to advance to MODE 4."
        )

    return {
        "classification": classification,
        "file_present": True,
        "file_path": str(mcp_path),
        "mode": mode,
        "server_count": server_count,
        "servers": server_list,
        "description": description,
        "timestamp": timestamp,
    }


def generate_md(status: dict) -> str:
    servers_table = "\n".join(
        f"| {s['name']} | {s['type']} | {s['command']} |"
        for s in status.get("servers", [])
    ) or "| (none) | — | — |"

    return f"""# MCP Status Report
# Format Factory — Supervisor-Generated
# Generated: {status['timestamp']}

## Classification

**{status['classification']}**

{status['description']}

## Details

| Item | Value |
|------|-------|
| .vscode/mcp.json present | {status['file_present']} |
| Supervisor mode | MODE {status['mode']} |
| Server count | {status['server_count']} |

## Configured Servers

| Name | Type | Command |
|------|------|---------|
{servers_table}

## Interpretation

| Classification | Meaning |
|---------------|---------|
| MCP_CONFIG_PRESENT_MODE4_ACTIVE | MCP authorized (MODE 4+) and config file present — servers can be used |
| MCP_CONFIG_PRESENT_NOT_ACTIVE | Config file exists but MODE < 4 — MCP not yet authorized |
| MCP_CONFIG_MISSING | MODE 4+ authorized but file missing — restore .vscode/mcp.json |
| MCP_DISABLED | MODE < 4 and no config — MCP not authorized |
| MCP_MISCONFIGURED | Config file present but malformed JSON |

## Important Note

MCP active = servers CAN be invoked by MCP-aware tools if the IDE is configured.
This script only checks configuration presence, NOT whether servers are running.
Actual server startup requires IDE/client integration.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Check MCP status for Format Factory supervisor")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    output_dir = args.output_dir or repo_root / "reports" / "supervisor"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=== CHECK MCP STATUS ===")
    status = check_mcp_status(repo_root)

    # Write JSON status
    status_json_path = output_dir / "mcp-status.json"
    status_json_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

    # Write MD report
    md_path = output_dir / "mcp-status.md"
    md_path.write_text(generate_md(status), encoding="utf-8")

    print(f"  Classification: {status['classification']}")
    print(f"  Mode: MODE {status['mode']}")
    print(f"  File present: {status['file_present']}")
    print(f"  Servers: {status['server_count']}")
    print(f"  Written: {md_path}")
    print("MCP_STATUS: CHECKED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
