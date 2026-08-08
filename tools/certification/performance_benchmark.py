"""Performance benchmarks for pilot format parsers/writers.

TC-CERT-R4-001 certification hardening.

Usage:
    python tools/certification/performance_benchmark.py
"""
from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

RUNS = 5
RESULTS_DIR = REPO_ROOT / "reports" / "certification"


def benchmark_fods():
    """Benchmark FODS parse and write."""
    from fods.parser import parse_fods
    from fods.writer import write_fods
    import tempfile

    sample = REPO_ROOT / "samples" / "by-format" / "fods" / "valid" / "minimal-spreadsheet.fods"
    if not sample.exists():
        # Try alternative paths
        candidates = list((REPO_ROOT / "samples" / "by-format" / "fods").rglob("*.fods"))
        if candidates:
            sample = candidates[0]
        else:
            return {"error": "No FODS sample found"}

    # Parse benchmark
    parse_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        model = parse_fods(sample)
        parse_times.append(time.perf_counter() - t0)

    # Write benchmark
    write_times = []
    for _ in range(RUNS):
        dst = Path(tempfile.mktemp(suffix=".fods"))
        try:
            t0 = time.perf_counter()
            write_fods(model, dst)
            write_times.append(time.perf_counter() - t0)
        finally:
            dst.unlink(missing_ok=True)

    # Memory benchmark
    tracemalloc.start()
    _ = parse_fods(sample)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "fods",
        "sample": str(sample.relative_to(REPO_ROOT)),
        "parse_median_ms": round(statistics.median(parse_times) * 1000, 2),
        "parse_min_ms": round(min(parse_times) * 1000, 2),
        "write_median_ms": round(statistics.median(write_times) * 1000, 2),
        "write_min_ms": round(min(write_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def benchmark_csv():
    """Benchmark CSV parse and write."""
    sys.path.insert(0, str(REPO_ROOT / "src" / "python" / "csv"))
    from csv_parser import parse_csv
    from csv_writer import write_csv
    import tempfile

    sample = REPO_ROOT / "samples" / "by-format" / "csv" / "valid" / "simple.csv"
    if not sample.exists():
        candidates = list((REPO_ROOT / "samples" / "by-format" / "csv").rglob("*.csv"))
        if candidates:
            sample = candidates[0]
        else:
            # Create a synthetic sample
            sample = Path(tempfile.mktemp(suffix=".csv"))
            rows = ["name,age,city"] + [f"person{i},{20+i},city{i}" for i in range(100)]
            sample.write_text("\n".join(rows), encoding="utf-8")

    # Parse benchmark
    parse_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        model = parse_csv(sample)
        parse_times.append(time.perf_counter() - t0)

    # Write benchmark
    parsed_rows = model.get("rows", [])
    headers = model.get("headers")
    write_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        _ = write_csv(parsed_rows, headers=headers)
        write_times.append(time.perf_counter() - t0)

    # Memory benchmark
    tracemalloc.start()
    _ = parse_csv(sample)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "csv",
        "sample": str(sample.relative_to(REPO_ROOT)) if str(sample).startswith(str(REPO_ROOT)) else str(sample),
        "parse_median_ms": round(statistics.median(parse_times) * 1000, 2),
        "parse_min_ms": round(min(parse_times) * 1000, 2),
        "write_median_ms": round(statistics.median(write_times) * 1000, 2),
        "write_min_ms": round(min(write_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def benchmark_ipynb():
    """Benchmark ipynb parse (load) and write (dump)."""
    from format_factory.ipynb import load, dump
    import tempfile

    sample = REPO_ROOT / "samples" / "by-format" / "ipynb" / "valid" / "code-and-markdown.ipynb"
    if not sample.exists():
        candidates = list((REPO_ROOT / "samples" / "by-format" / "ipynb" / "valid").rglob("*.ipynb"))
        if candidates:
            sample = candidates[0]
        else:
            return {"error": "No ipynb sample found"}

    # Parse benchmark
    parse_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        document = load(sample)
        parse_times.append(time.perf_counter() - t0)

    # Write benchmark
    write_times = []
    for _ in range(RUNS):
        dst = Path(tempfile.mktemp(suffix=".ipynb"))
        try:
            t0 = time.perf_counter()
            dump(document, dst)
            write_times.append(time.perf_counter() - t0)
        finally:
            dst.unlink(missing_ok=True)

    # Memory benchmark
    tracemalloc.start()
    _ = load(sample)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "ipynb",
        "sample": str(sample.relative_to(REPO_ROOT)),
        "parse_median_ms": round(statistics.median(parse_times) * 1000, 2),
        "parse_min_ms": round(min(parse_times) * 1000, 2),
        "write_median_ms": round(statistics.median(write_times) * 1000, 2),
        "write_min_ms": round(min(write_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def benchmark_safetensors():
    """Benchmark safetensors parse (load) and write (dumps)."""
    from format_factory.safetensors import load, dumps

    sample = REPO_ROOT / "samples" / "by-format" / "safetensors" / "valid" / "multi-tensor.safetensors"
    if not sample.exists():
        candidates = list((REPO_ROOT / "samples" / "by-format" / "safetensors" / "valid").rglob("*.safetensors"))
        if candidates:
            sample = candidates[0]
        else:
            return {"error": "No safetensors sample found"}

    # Parse benchmark
    parse_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        document = load(sample)
        parse_times.append(time.perf_counter() - t0)

    # Write benchmark
    write_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        _ = dumps(document)
        write_times.append(time.perf_counter() - t0)

    # Memory benchmark
    tracemalloc.start()
    _ = load(sample)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "safetensors",
        "sample": str(sample.relative_to(REPO_ROOT)),
        "parse_median_ms": round(statistics.median(parse_times) * 1000, 2),
        "parse_min_ms": round(min(parse_times) * 1000, 2),
        "write_median_ms": round(statistics.median(write_times) * 1000, 2),
        "write_min_ms": round(min(write_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def benchmark_xliff():
    """Benchmark xliff parse (load) and write (dumps)."""
    from format_factory.xliff import load, dumps

    sample = REPO_ROOT / "samples" / "by-format" / "xliff" / "valid" / "multi-unit.xliff"
    if not sample.exists():
        candidates = list((REPO_ROOT / "samples" / "by-format" / "xliff" / "valid").rglob("*.xliff"))
        if candidates:
            sample = candidates[0]
        else:
            return {"error": "No xliff sample found"}

    # Parse benchmark
    parse_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        document = load(sample)
        parse_times.append(time.perf_counter() - t0)

    # Write benchmark
    write_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        _ = dumps(document)
        write_times.append(time.perf_counter() - t0)

    # Memory benchmark
    tracemalloc.start()
    _ = load(sample)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "xliff",
        "sample": str(sample.relative_to(REPO_ROOT)),
        "parse_median_ms": round(statistics.median(parse_times) * 1000, 2),
        "parse_min_ms": round(min(parse_times) * 1000, 2),
        "write_median_ms": round(statistics.median(write_times) * 1000, 2),
        "write_min_ms": round(min(write_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def benchmark_zst():
    """Benchmark ZST compress and decompress."""
    from zst import compress_bytes, decompress_bytes

    # Create synthetic data: 100KB of mixed content
    data = (b"Hello World! " * 1000 + b"\x00" * 5000) * 8

    # Compress benchmark
    compress_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        compressed = compress_bytes(data)
        compress_times.append(time.perf_counter() - t0)

    # Decompress benchmark
    decompress_times = []
    for _ in range(RUNS):
        t0 = time.perf_counter()
        _ = decompress_bytes(compressed)
        decompress_times.append(time.perf_counter() - t0)

    # Memory benchmark
    tracemalloc.start()
    _ = decompress_bytes(compressed)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "format": "zst",
        "input_size_kb": round(len(data) / 1024, 1),
        "compressed_size_kb": round(len(compressed) / 1024, 1),
        "compression_ratio": round(len(compressed) / len(data), 4),
        "compress_median_ms": round(statistics.median(compress_times) * 1000, 2),
        "compress_min_ms": round(min(compress_times) * 1000, 2),
        "decompress_median_ms": round(statistics.median(decompress_times) * 1000, 2),
        "decompress_min_ms": round(min(decompress_times) * 1000, 2),
        "memory_peak_kb": round(peak / 1024, 1),
        "runs": RUNS,
    }


def main():
    results = {}

    for name, fn in [
        ("fods", benchmark_fods),
        ("csv", benchmark_csv),
        ("zst", benchmark_zst),
        ("ipynb", benchmark_ipynb),
        ("safetensors", benchmark_safetensors),
        ("xliff", benchmark_xliff),
    ]:
        print(f"Benchmarking {name.upper()}...", end=" ", flush=True)
        try:
            r = fn()
            results[name] = r
            if "error" in r:
                print(f"ERROR: {r['error']}")
            else:
                print("OK")
        except Exception as e:
            results[name] = {"error": str(e), "traceback": tracemalloc.format_exc() if hasattr(tracemalloc, 'format_exc') else ""}
            print(f"FAILED: {e}")

    # Print summary
    print("\n=== Performance Baselines ===")
    for name, r in results.items():
        if "error" in r:
            print(f"  {name}: ERROR - {r['error']}")
            continue
        if name == "zst":
            print(f"  {name}: compress={r['compress_median_ms']}ms, "
                  f"decompress={r['decompress_median_ms']}ms, "
                  f"mem_peak={r['memory_peak_kb']}KB")
        else:
            print(f"  {name}: parse={r['parse_median_ms']}ms, "
                  f"write={r['write_median_ms']}ms, "
                  f"mem_peak={r['memory_peak_kb']}KB")

    # Write per-format results
    for name, r in results.items():
        out = RESULTS_DIR / name / "performance-baseline.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(r, indent=2) + "\n", encoding="utf-8")
        print(f"\nWritten: {out.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
