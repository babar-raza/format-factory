"""Benchmark: NDJSON parser load time. TC-W7-003.

Run with: python tests/benchmarks/bench_ndjson.py
"""
from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "python"))

SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"
RUNS = 50


def run() -> float:
    from ndjson import load_ndjson
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        load_ndjson(str(SAMPLE))
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


if __name__ == "__main__":
    avg = run()
    print(f"NDJSON parse avg over {RUNS} runs: {avg*1000:.2f} ms")
