"""Select and rank product-factory POC gaps from the capability matrix.

v3 improvements (R99):
- Stream-aware output (mainstream, acceleration, skills, supervisor)
- Skill registry integration for decision enrichment
- Depth-priority scoring (save/export/dogfood > shallow query APIs)

v4 improvements (R101):
- Stale sprint detection: requested_sprint must match matrix sprint
- Skill registry hash in output for provenance
- is_stale flag in payload

v5 improvements (DOTNET-TARGET-WRITER-READINESS-HARDENING):
- Proof-backed writer readiness: detect_target_writer_readiness() checks source, project,
  tests, raw log, and sample output — not just source-file existence.
- Readiness statuses: READY | MISSING_SOURCE | MISSING_PROJECT | MISSING_TESTS |
  MISSING_RAW_LOG | MISSING_SAMPLE_OUTPUT | SOURCE_PRESENT_TESTS_REQUIRED
- A gap is only truly unblocked (READY) when all five proof conditions are met.
- SOURCE_PRESENT_TESTS_REQUIRED is a provisional state used when source exists but logs
  have not yet been generated (e.g. first-run before dotnet test has executed).
- accepted_for_poc is set only when readiness status is READY.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from choose_skill_or_handoff import choose_skill_or_handoff


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_MATRIX = REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"
DEFAULT_SKILL_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"
DEFAULT_JSON = REPO_ROOT / ".local" / "supervisor" / "selected-product-gaps.json"
DEFAULT_REPORT = REPO_ROOT / "reports" / "supervisor" / "product-gap-selection.md"

GAP_STATUSES = {
    "GAP_DOGFOOD_EXTERNAL",
    "GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED",
    "NOT_IMPLEMENTED",
    "NOT_STARTED",
    "NOT_YET",
    "PARTIAL",
    "R85_TARGET",
}

ACTION_SCORE = {
    "NOT_IMPLEMENTED": 100,
    "GAP_DOGFOOD_EXTERNAL": 95,
    "R85_TARGET": 90,
    "NOT_YET": 85,
    "PARTIAL": 80,
    "NOT_STARTED": 30,
    "GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED": 40,
}

# Gap IDs that were confirmed as architecture-blocked when no target writer library existed.
# Sprint FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001 may implement writers.
# Use detect_target_writer_status() to dynamically resolve which gaps are still blocked.
_ARCHITECTURE_BLOCKED_SEED: frozenset[str] = frozenset({
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet",
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet",
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet",
})

# Map from gap_id → full proof descriptor (v5: proof-backed readiness)
# TC-CAP-011: This dict is INTENTIONAL — it is the authoritative proof registry for
# commercial .NET writer gaps (not the FOSS capability gap ledger).
# These gap_ids are commercial-net-* dotnet writer verification records, distinct from
# the capability layer gap-ledger.json (which tracks FOSS Python capability gaps).
# DEFAULT_MATRIX (poc-targets.yaml) is used as the dashboard selection source for commercial
# gap enumeration; it is NOT the capability authority for FOSS gaps (see capability-authority-model.yaml).
_GAP_WRITER_PROOF: dict[str, dict[str, str]] = {
    "commercial-net-fods-dogfood-status-fods-to-csv-dotnet": {
        "target_writer_name": "FormatFactory.Csv.CsvWriter",
        "source_path": "src/net/csv/CsvWriter.cs",
        "project_path": "src/net/csv/FormatFactory.Csv.csproj",
        "test_project_path": "tests/net/csv/FormatFactory.Csv.Tests.csproj",
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-csv.csv",
    },
    "commercial-net-fods-dogfood-status-fods-to-html-dotnet": {
        "target_writer_name": "FormatFactory.Html.HtmlWriter",
        "source_path": "src/net/html/HtmlWriter.cs",
        "project_path": "src/net/html/FormatFactory.Html.csproj",
        "test_project_path": "tests/net/html/FormatFactory.Html.Tests.csproj",
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fods-to-html.html",
    },
    "commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet": {
        "target_writer_name": "FormatFactory.Markdown.MarkdownWriter",
        "source_path": "src/net/markdown/MarkdownWriter.cs",
        "project_path": "src/net/markdown/FormatFactory.Markdown.csproj",
        "test_project_path": "tests/net/markdown/FormatFactory.Markdown.Tests.csproj",
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-markdown.md",
    },
    "commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet": {
        "target_writer_name": "FormatFactory.Txt.TxtWriter",
        "source_path": "src/net/txt/TxtWriter.cs",
        "project_path": "src/net/txt/FormatFactory.Txt.csproj",
        "test_project_path": "tests/net/txt/FormatFactory.Txt.Tests.csproj",
        "raw_log_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/raw-logs/writer-tests.log",
        "sample_output_path": "reports/dotnet-target-writer-mwp-dogfood-unblocking/sample-outputs/sample-fodt-to-txt.txt",
    },
}

# Backward-compat alias: source-only map derived from proof descriptor
_GAP_WRITER_SOURCE: dict[str, str] = {
    gap_id: proof["source_path"]
    for gap_id, proof in _GAP_WRITER_PROOF.items()
}

# Readiness status constants
READINESS_READY = "READY"
READINESS_MISSING_SOURCE = "MISSING_SOURCE"
READINESS_MISSING_PROJECT = "MISSING_PROJECT"
READINESS_MISSING_TESTS = "MISSING_TESTS"
READINESS_MISSING_RAW_LOG = "MISSING_RAW_LOG"
READINESS_MISSING_SAMPLE_OUTPUT = "MISSING_SAMPLE_OUTPUT"
READINESS_SOURCE_PRESENT_TESTS_REQUIRED = "SOURCE_PRESENT_TESTS_REQUIRED"


def _raw_log_proves_pass(log_path: Path) -> bool:
    """Return True if the raw log file exists and contains a test pass marker."""
    if not log_path.exists():
        return False
    content = log_path.read_text(encoding="utf-8", errors="replace")
    return "Passed!" in content or "passed" in content.lower()


def detect_target_writer_readiness(
    repo_root: Path,
    gap_id: str,
) -> dict[str, Any]:
    """Return a structured readiness object for a dogfood gap's target writer.

    Readiness is READY only when:
      1. source (.cs) exists
      2. project (.csproj) exists
      3. test project (.csproj) exists
      4. raw log proves tests passed
      5. sample output exists

    If source exists but logs are not yet generated:
      status = SOURCE_PRESENT_TESTS_REQUIRED (provisional — not accepted_for_poc)
    """
    proof = _GAP_WRITER_PROOF.get(gap_id)
    if proof is None:
        return {
            "gap_id": gap_id,
            "target_writer_name": "UNKNOWN",
            "source_path": None,
            "project_path": None,
            "test_project_path": None,
            "raw_log_path": None,
            "sample_output_path": None,
            "source_exists": False,
            "project_exists": False,
            "tests_exist": False,
            "raw_log_passed": False,
            "sample_output_exists": False,
            "status": READINESS_MISSING_SOURCE,
            "accepted_for_poc": False,
        }

    source_path = repo_root / proof["source_path"]
    project_path = repo_root / proof["project_path"]
    test_project_path = repo_root / proof["test_project_path"]
    raw_log_path = repo_root / proof["raw_log_path"]
    sample_output_path = repo_root / proof["sample_output_path"]

    source_exists = source_path.exists()
    project_exists = project_path.exists()
    tests_exist = test_project_path.exists()
    raw_log_passed = _raw_log_proves_pass(raw_log_path)
    sample_output_exists = sample_output_path.exists()

    if not source_exists:
        status = READINESS_MISSING_SOURCE
    elif not project_exists:
        status = READINESS_MISSING_PROJECT
    elif not tests_exist:
        status = READINESS_MISSING_TESTS
    elif not raw_log_passed:
        # Source and project exist — provisional state until tests are run
        status = READINESS_SOURCE_PRESENT_TESTS_REQUIRED
    elif not sample_output_exists:
        status = READINESS_MISSING_SAMPLE_OUTPUT
    else:
        status = READINESS_READY

    accepted_for_poc = status == READINESS_READY

    return {
        "gap_id": gap_id,
        "target_writer_name": proof["target_writer_name"],
        "source_path": proof["source_path"],
        "project_path": proof["project_path"],
        "test_project_path": proof["test_project_path"],
        "raw_log_path": proof["raw_log_path"],
        "sample_output_path": proof["sample_output_path"],
        "source_exists": source_exists,
        "project_exists": project_exists,
        "tests_exist": tests_exist,
        "raw_log_passed": raw_log_passed,
        "sample_output_exists": sample_output_exists,
        "status": status,
        "accepted_for_poc": accepted_for_poc,
    }


def detect_target_writer_status(repo_root: Path) -> frozenset[str]:
    """Return the set of gap IDs that remain architecture-blocked.

    A gap is unblocked only when its writer has READY readiness status
    (source + project + tests + raw-log-pass + sample output all confirmed).

    If source exists but proof is incomplete, the gap moves to
    SOURCE_PRESENT_TESTS_REQUIRED — still blocked for routing purposes.
    """
    still_blocked = set()
    for gap_id in _ARCHITECTURE_BLOCKED_SEED:
        readiness = detect_target_writer_readiness(repo_root, gap_id)
        if readiness["status"] != READINESS_READY:
            still_blocked.add(gap_id)
    return frozenset(still_blocked)


# Compute at import time against the live repo
BLOCKED_GAP_IDS: frozenset[str] = detect_target_writer_status(REPO_ROOT)

DECISION_BONUS = {
    "GOVERNED_SKILL_REQUIRED": 20,
    "GOVERNED_HANDOFF_REQUIRED": 10,
    "EXTERNAL_GATE_ESCALATION": 0,
}

# Depth-priority: prefer save/export/dogfood over shallow query APIs
DEPTH_KEYWORDS_HIGH = {"save", "export", "write", "dogfood", "roundtrip", "package", "install"}
DEPTH_KEYWORDS_LOW = {"get", "count", "enumerate", "list", "inspect"}

STREAM_LABELS = ("mainstream", "acceleration", "skills", "supervisor")


def _content_hash(items: list[dict[str, Any]]) -> str:
    """Compute a stable hash of gap content for stale detection."""
    ids = sorted(g.get("gap_id", "") for g in items)
    return hashlib.sha256(json.dumps(ids).encode()).hexdigest()[:16]


def _yaml_hash(data: dict[str, Any] | None) -> str:
    """Hash a YAML dict for provenance tracking."""
    if not data:
        return "none"
    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def detect_stale(matrix_sprint: str | None, requested_sprint: str | None) -> bool:
    """Return True if requested sprint doesn't match matrix sprint."""
    if not requested_sprint or not matrix_sprint:
        return False
    return str(requested_sprint).strip() != str(matrix_sprint).strip()


def _status_name(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _walk_statuses(value: Any, prefix: str = "") -> Iterable[tuple[str, str]]:
    if not isinstance(value, dict):
        return
    for key, child in value.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(child, dict):
            yield from _walk_statuses(child, path)
        elif _status_name(child) in GAP_STATUSES:
            yield path, _status_name(child)


def _depth_bonus(capability_path: str) -> int:
    """Return a bonus for deep product capabilities (save/export) over shallow queries."""
    lower = capability_path.lower()
    if any(kw in lower for kw in DEPTH_KEYWORDS_HIGH):
        return 10
    if any(kw in lower for kw in DEPTH_KEYWORDS_LOW):
        return -5
    return 0


def _classify_stream(gap: dict[str, Any]) -> str:
    """Assign a gap to a stream: mainstream, acceleration, skills, or supervisor."""
    decision = gap.get("decision", "")
    cap = gap.get("capability_path", "").lower()
    if decision == "EXTERNAL_GATE_ESCALATION":
        return "supervisor"
    if "skill" in cap or "registry" in cap or "acceleration" in cap:
        return "acceleration"
    if decision == "GOVERNED_SKILL_REQUIRED":
        return "mainstream"
    return "mainstream"


def _gap(
    *,
    track: str,
    product: dict[str, Any],
    capability_path: str,
    current_status: str,
    description: str,
    skill_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gap = {
        "product_track": track,
        "format": product["format"],
        "capability_path": capability_path,
        "current_status": current_status,
        "description": description,
    }
    decision = choose_skill_or_handoff(gap, skill_registry=skill_registry)
    base_score = ACTION_SCORE.get(current_status, 70)
    depth = _depth_bonus(capability_path)
    gap.update(decision)
    gap["poc_impact_score"] = base_score
    gap["depth_bonus"] = depth
    gap["priority_score"] = base_score + DECISION_BONUS[decision["decision"]] + depth
    gap["stream"] = _classify_stream(gap)
    gap["gap_id"] = (
        f"{track}-{product['format']}-{capability_path}"
        .lower()
        .replace(".", "-")
        .replace("_", "-")
        .replace(" ", "-")
    )
    # Reclassify architecture-blocked gaps so they are not routed to skill execution.
    if gap["gap_id"] in BLOCKED_GAP_IDS:
        gap["current_status"] = "GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED"
        gap["poc_impact_score"] = ACTION_SCORE["GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED"]
        gap["priority_score"] = (
            ACTION_SCORE["GAP_DOGFOOD_EXTERNAL_ARCHITECTURE_BLOCKED"]
            + DECISION_BONUS.get(gap.get("decision", ""), 0)
            + gap.get("depth_bonus", 0)
        )
        gap["architecture_blocked"] = True
    return gap


def load_skill_registry(path: Path | None = None) -> dict[str, Any] | None:
    """Load the skill registry YAML if available."""
    registry_path = path or DEFAULT_SKILL_REGISTRY
    if not registry_path.exists():
        return None
    return yaml.safe_load(registry_path.read_text(encoding="utf-8")) or {}


def select_gaps(
    matrix: dict[str, Any],
    skill_registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return ranked gaps from confirmed commercial and reduced/FOSS products."""
    gaps: list[dict[str, Any]] = []
    for track, products in (
        ("commercial_net", matrix.get("commercial_net_products", [])),
        ("foss_reduced", matrix.get("foss_reduced_products", [])),
    ):
        for product in products:
            for path, status in _walk_statuses(product):
                gaps.append(
                    _gap(
                        track=track,
                        product=product,
                        capability_path=path,
                        current_status=status,
                        description=f"{product['format']} capability {path} is {status}.",
                        skill_registry=skill_registry,
                    )
                )
            for index, blocker in enumerate(product.get("blockers", []), start=1):
                gaps.append(
                    _gap(
                        track=track,
                        product=product,
                        capability_path=f"blockers.{index}",
                        current_status="BLOCKED",
                        description=str(blocker),
                        skill_registry=skill_registry,
                    )
                )
    return sorted(
        gaps,
        key=lambda item: (
            -item["priority_score"],
            item["product_track"],
            item["format"].lower(),
            item["capability_path"],
        ),
    )


def split_by_stream(gaps: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Split selected gaps into per-stream lists."""
    streams: dict[str, list[dict[str, Any]]] = {s: [] for s in STREAM_LABELS}
    for gap in gaps:
        stream = gap.get("stream", "mainstream")
        streams.setdefault(stream, []).append(gap)
    return streams


def build_payload(
    matrix_path: Path,
    matrix: dict[str, Any],
    skill_registry: dict[str, Any] | None = None,
    requested_sprint: str | None = None,
) -> dict[str, Any]:
    gaps = select_gaps(matrix, skill_registry=skill_registry)
    streams = split_by_stream(gaps)
    matrix_sprint = matrix.get("sprint")
    is_stale = detect_stale(matrix_sprint, requested_sprint) if requested_sprint else False
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_matrix": matrix_path.as_posix(),
        "matrix_version": matrix.get("poc_matrix_version"),
        "sprint": matrix_sprint,
        "requested_sprint": requested_sprint,
        "is_stale": is_stale,
        "skill_registry_hash": _yaml_hash(skill_registry),
        "selection_policy": (
            "Rank POC capability impact first, depth-priority (save/export/dogfood > query), "
            "favor governed-skill execution over handoff; retain external gates as visible "
            "non-autonomous blockers. v4: stale detection, registry hash."
        ),
        "selected_gap_count": len(gaps),
        "selected_gaps": gaps,
        "streams": {label: len(items) for label, items in streams.items()},
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "---",
        "visibility: generated",
        "generated_by: codex",
        "---",
        "",
        "# Product Gap Selection",
        "",
        f"Source matrix: `{payload['source_matrix']}`",
        f"Selected gaps: {payload['selected_gap_count']}",
        "",
        "| Rank | Track | Format | Capability | Status | POC impact | Decision | Skill |",
        "|---:|---|---|---|---|---:|---|---|",
    ]
    for rank, gap in enumerate(payload["selected_gaps"], start=1):
        skill = gap["governed_skill"] or "-"
        lines.append(
            f"| {rank} | {gap['product_track']} | {gap['format']} | "
            f"`{gap['capability_path']}` | `{gap['current_status']}` | "
            f"{gap['poc_impact_score']} | `{gap['decision']}` | `{skill}` |"
        )
    lines.extend(
        [
            "",
            "External-gate entries remain visible but are not autonomous implementation work.",
            "",
        ]
    )
    return "\n".join(lines)


def write_selection(
    matrix_path: Path,
    json_path: Path,
    report_path: Path,
    skill_registry_path: Path | None = None,
    stream_output_dir: Path | None = None,
    requested_sprint: str | None = None,
) -> dict[str, Any]:
    matrix = yaml.safe_load(matrix_path.read_text(encoding="utf-8")) or {}
    skill_registry = load_skill_registry(skill_registry_path)
    payload = build_payload(matrix_path, matrix, skill_registry=skill_registry,
                            requested_sprint=requested_sprint)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_markdown(payload), encoding="utf-8")

    # Write per-stream JSON files with sprint_id and content hash
    if stream_output_dir:
        streams = split_by_stream(payload["selected_gaps"])
        stream_output_dir.mkdir(parents=True, exist_ok=True)
        sprint = payload.get("sprint", "unknown")
        for label, items in streams.items():
            stream_payload = {
                "generated_at": payload["generated_at"],
                "sprint_id": sprint,
                "matrix_version": payload.get("matrix_version"),
                "stream": label,
                "gap_count": len(items),
                "gaps": items,
                "source_hash": _content_hash(items),
            }
            content = json.dumps(stream_payload, indent=2) + "\n"
            # Sprint-stamped file
            (stream_output_dir / f"selected-product-gaps-{label}-{sprint}.json").write_text(content, encoding="utf-8")
            # Backward-compatible unstamped file
            (stream_output_dir / f"selected-product-gaps-{label}.json").write_text(content, encoding="utf-8")

    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank POC product gaps from the matrix.")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--skill-registry", type=Path, default=None)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--stream-output-dir",
        type=Path,
        default=None,
        help="Directory for per-stream JSON outputs",
    )
    parser.add_argument("--requested-sprint", default=None, help="Expected sprint ID for stale detection")
    args = parser.parse_args()
    payload = write_selection(
        args.matrix,
        args.json_output,
        args.report_output,
        skill_registry_path=args.skill_registry,
        stream_output_dir=args.stream_output_dir,
        requested_sprint=args.requested_sprint,
    )
    print(f"SELECTED_PRODUCT_GAPS: {payload['selected_gap_count']}")
    print(f"STREAMS: {payload.get('streams', {})}")
    print(f"IS_STALE: {payload.get('is_stale', False)}")
    print(f"JSON_OUTPUT: {args.json_output}")
    print(f"REPORT_OUTPUT: {args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
