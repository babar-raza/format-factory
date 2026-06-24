"""
TC-AMD-MCP-001: Read-only MCP bridge for format-factory supervisor signals.

Exposes 3 read-only tools via JSON-RPC 2.0 with proper MCP stdio framing.
NO state mutations — reads only from reports/supervisor/*.

MCP stdio protocol (LSP-style):
  Content-Length: <N>\r\n\r\n<JSON body of N bytes>

NAIVE `for line in sys.stdin:` does NOT work — VS Code MCP host sends Content-Length frames.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent

TOOLS = [
    {
        "name": "format_factory__get_sprint_verdict",
        "description": "Returns latest sprint verdict and maturity signal from format-factory supervisor.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "format_factory__get_next_work_items",
        "description": "Returns current next-work-items.json from format-factory supervisor.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "format_factory__get_work_item_grade",
        "description": "Returns grade for a specific work item ID.",
        "inputSchema": {
            "type": "object",
            "properties": {"item_id": {"type": "string", "description": "Work item ID to look up"}},
            "required": ["item_id"],
        },
    },
]


def handle_call(name: str, args: dict) -> dict:
    """Dispatch a tool call to the appropriate read-only handler."""
    if name == "format_factory__get_sprint_verdict":
        p = _REPO / "reports" / "supervisor" / "maturity-signal.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {"error": "not_found", "detail": "maturity-signal.json not yet produced"}
    elif name == "format_factory__get_next_work_items":
        p = _REPO / "reports" / "supervisor" / "next-work-items.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {"error": "not_found", "detail": "next-work-items.json not yet produced"}
    elif name == "format_factory__get_work_item_grade":
        item_id = args.get("item_id", "")
        grades_path = _REPO / "reports" / "supervisor" / "work-item-grades.md"
        if not grades_path.exists():
            return {"error": "not_found", "detail": "work-item-grades.md not found"}
        for line in grades_path.read_text(encoding="utf-8").splitlines():
            if item_id in line:
                return {"item_id": item_id, "grade_line": line.strip()}
        return {"item_id": item_id, "grade": "not_found"}
    return {"error": f"unknown_tool: {name}"}


def _read_message(stdin: object) -> "dict | None":
    """Read one MCP message using Content-Length framing (LSP-style)."""
    header = b""
    while True:
        ch = stdin.buffer.read(1)  # type: ignore[attr-defined]
        if not ch:
            return None
        header += ch
        if header.endswith(b"\r\n\r\n"):
            break
    # Parse Content-Length from header
    length = None
    for line in header.decode("utf-8").splitlines():
        if line.lower().startswith("content-length:"):
            try:
                length = int(line.split(":", 1)[1].strip())
            except (ValueError, IndexError):
                pass
    if length is None:
        return None
    body = stdin.buffer.read(length)  # type: ignore[attr-defined]
    return json.loads(body.decode("utf-8"))


def _send_message(msg: dict) -> None:
    """Send one MCP message using Content-Length framing."""
    body = json.dumps(msg).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
    sys.stdout.buffer.write(header + body)
    sys.stdout.buffer.flush()


def main() -> None:
    """MCP stdio server loop (Content-Length framing)."""
    while True:
        try:
            req = _read_message(sys.stdin)
            if req is None:
                break
            method = req.get("method", "")
            params = req.get("params", {})
            rid = req.get("id")
            if method == "tools/list":
                result: dict = {"tools": TOOLS}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                result = {"content": [{"type": "text", "text": json.dumps(
                    handle_call(tool_name, tool_args)
                )}]}
            else:
                result = {"error": {"code": -32601, "message": f"Method not found: {method}"}}
            _send_message({"jsonrpc": "2.0", "id": rid, "result": result})
        except Exception as exc:
            _send_message({"jsonrpc": "2.0", "id": None, "error": {
                "code": -32603, "message": str(exc)
            }})


if __name__ == "__main__":
    main()
