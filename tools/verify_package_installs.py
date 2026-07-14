"""Verify that all 20 Format Factory Python format packages are importable.

TC-W1-004: Package install verification. Runs under the project venv.
Exit code 0 if all packages import successfully; 1 if any fail.
"""
import argparse
import importlib
import sys
from pathlib import Path


FORMAT_IDS = [
    "fods", "fodt", "ods", "gnumeric", "sylk", "dif", "csv", "tsv",
    "odt", "xcf", "zst", "ndjson", "toml", "abw", "fodp", "fodg",
    "qoi", "pbm", "pgm", "ppm",
]


def verify(venv: str | None = None) -> int:
    if venv:
        site_pkgs = list(Path(venv).glob("Lib/site-packages"))
        if site_pkgs:
            sys.path.insert(0, str(site_pkgs[0]))

    passed, failed = [], []
    for fmt in FORMAT_IDS:
        try:
            importlib.import_module(fmt)
            passed.append(fmt)
        except Exception as exc:
            failed.append((fmt, str(exc)))

    print(f"{len(passed)}/{len(FORMAT_IDS)} packages importable")
    for fmt, err in failed:
        print(f"  FAIL: {fmt} -> {err}")

    return 0 if not failed else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify Format Factory package installs")
    parser.add_argument("--venv", default=None, help="Path to venv (default: auto-detect)")
    args = parser.parse_args()
    sys.exit(verify(venv=args.venv))


if __name__ == "__main__":
    main()
