"""Read-only README drift detection."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from tools.readme_sync.collector import REPO_ROOT
from tools.readme_sync.reconciler import render_existing_with_generated, strip_timestamps
from tools.readme_sync.renderer import generate_blocks
from tools.readme_sync.collector import collect_format_state


def readme_targets() -> list[tuple[str, str, Path]]:
    targets: list[tuple[str, str, Path]] = []
    for track, root in (("python", REPO_ROOT / "src" / "python"), ("dotnet", REPO_ROOT / "src" / "net")):
        for path in sorted(root.glob("*/README.md")):
            targets.append((path.parent.name, track, path))
    return targets


def _hash(text: str) -> str:
    return hashlib.sha256(strip_timestamps(text).encode("utf-8")).hexdigest()


def check_readme_drift(format_id: str, track: str, path: Path) -> dict:
    current = path.read_text(encoding="utf-8", errors="replace")
    expected = render_existing_with_generated(current, generate_blocks(collect_format_state(format_id, track), "STRIPPED"))
    drifted = _hash(current) != _hash(expected)
    return {"format_id": format_id, "track": track, "path": str(path.relative_to(REPO_ROOT)), "drifted": drifted}


def check_all_drift() -> dict:
    checks = [check_readme_drift(format_id, track, path) for format_id, track, path in readme_targets()]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall": "DRIFT" if any(c["drifted"] for c in checks) else "NO_DRIFT",
        "checks": checks,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--format")
    parser.add_argument("--track", choices=["python", "dotnet"])
    parser.add_argument("--output")
    args = parser.parse_args()
    if args.format and args.track:
        path = REPO_ROOT / "src" / ("python" if args.track == "python" else "net") / args.format / "README.md"
        report = {"checks": [check_readme_drift(args.format, args.track, path)]}
        report["overall"] = "DRIFT" if report["checks"][0]["drifted"] else "NO_DRIFT"
    else:
        report = check_all_drift()
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2), encoding="utf-8")
    stale = [c["path"] for c in report["checks"] if c["drifted"]]
    if stale:
        print("DRIFT detected in: " + ", ".join(stale))
        return 1
    print("NO_DRIFT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
