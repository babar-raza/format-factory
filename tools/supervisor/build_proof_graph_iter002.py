# TOMBSTONE: build_proof_graph_iter002.py quarantined 2026-07-06 — confirmed DEPRECATED_STILL_ACTIVE
# If this file is imported or executed, a record is written to
# .local/supervisor/invocation-tombstones/. Zero records after 30 days
# confirms dead. Any record fires: re-investigate this file.
import pathlib as _p
import datetime as _dt
import json as _j
import traceback as _tb
_repo_root = _p.Path(__file__).resolve()
while _repo_root.name not in ("format-factory", "") and _repo_root != _repo_root.parent:
    _repo_root = _repo_root.parent
_td = _repo_root / ".local" / "supervisor" / "invocation-tombstones"
_td.mkdir(parents=True, exist_ok=True)
_r = {"file": str(__file__), "module": __name__,
      "timestamp": _dt.datetime.utcnow().isoformat(),
      "caller": _tb.format_stack()[-3] if len(_tb.extract_stack()) > 2 else None}
(_td / f"{_p.Path(__file__).stem}_{_dt.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
 ).write_text(_j.dumps(_r, indent=2), encoding="utf-8")
raise DeprecationWarning(
    f"{__file__} is tombstoned — record written to {_td}. "
    "If this fires, the file is live. Update its register classification.")
