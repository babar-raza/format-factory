"""Standalone probe run inside the isolated pynrrd oracle venv.

Deliberately has ZERO imports from this repository -- it must be
runnable using only the isolated venv's own site-packages (pynrrd and
its own numpy dependency), never this project's own `format_factory`
package or its legacy top-level `nrrd` compatibility shim. See
`setup_nrrd_pynrrd_venv.py`'s own module docstring for why this
isolation exists at all (the `nrrd`/`pynrrd` import-name collision).

Usage: <isolated-venv-python> nrrd_pynrrd_probe.py <sample-path>
Prints one JSON object to stdout: {"type", "dimension", "sizes",
"encoding", "data"} on success, or {"error": "..."} on any exception --
errors are reported as data rather than a nonzero exit, so a caller
across the subprocess boundary always gets parseable JSON.
"""

from __future__ import annotations

import json
import sys


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: nrrd_pynrrd_probe.py <sample-path>"}))
        return 2
    sample_path = sys.argv[1]
    try:
        import nrrd  # the REAL pynrrd package -- only possible in this isolated venv

        # index_order="C": pynrrd defaults to "F" (Fortran/column-major,
        # matching the NRRD spec's own fastest-axis-first storage order
        # directly), which nests a multi-dimensional array with the
        # FASTEST axis outermost -- the opposite of
        # format_factory.nrrd's own to_array() convention (slowest axis
        # outermost, confirmed directly: a sizes=[2,3] sample nests as
        # 3 groups of 2, not 2 groups of 3). "C" order reverses pynrrd's
        # own axes to match that same slowest-outer convention, so this
        # probe's own JSON output needs no reshaping by its caller.
        #
        # The ignore below is load-bearing, not boilerplate: mypy
        # resolves `nrrd` against the main project's own site-packages,
        # where it means this repo's legacy compat shim
        # (src/python/nrrd/__init__.py), not pynrrd -- the exact
        # collision this script exists to sidestep at runtime. Only
        # ever actually executed inside the isolated venv described
        # above, where `nrrd` genuinely is pynrrd.
        data, header = nrrd.read(sample_path, index_order="C")  # type: ignore[attr-defined]
        result = {
            "type": header.get("type"),
            "dimension": int(header.get("dimension")),
            "sizes": [int(size) for size in header.get("sizes", [])],
            "encoding": header.get("encoding"),
            "data": data.tolist(),
        }
    except Exception as exc:  # noqa: BLE001 -- reported as data, not raised across the subprocess boundary
        result = {"error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
