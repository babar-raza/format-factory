"""Benchmark: ZST parser load time. TC-W7-003.

Run with: python tests/benchmarks/bench_zst.py
"""
from __future__ import annotations

import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "python"))

SAMPLE = Path(__file__).resolve().parents[2] / "samples" / "by-format" / "zst" / "valid" / "minimal-synthetic.zst"
RUNS = 20


def run() -> float:
    from zst import decompress_bytes
    data = SAMPLE.read_bytes()
    times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        decompress_bytes(data)
        times.append(time.perf_counter() - t0)
    return sum(times) / len(times)


if __name__ == "__main__":
    avg = run()
    print(f"ZST parse avg over {RUNS} runs: {avg*1000:.2f} ms")
