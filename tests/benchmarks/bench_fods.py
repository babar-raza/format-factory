"""Benchmark: FODS parser load time. TC-W7-003.

Run with: python -m timeit -s "from tests.benchmarks.bench_fods import run" "run()"
Or: python tests/benchmarks/bench_fods.py
"""
from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "python"))

SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "by-format" / "fods" / "valid" / "simple.fods"
RUNS = 20


def run() -> float:
    """Parse FODS sample N times; return avg seconds per parse."""
    from fods import parse_fods_strict
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        parse_fods_strict(str(SAMPLE))
        times.append(time.perf_counter() - t0)
    avg = sum(times) / len(times)
    return avg


if __name__ == "__main__":
    avg = run()
    print(f"FODS parse avg over {RUNS} runs: {avg*1000:.2f} ms")
