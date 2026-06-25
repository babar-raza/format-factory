"""Clean consumer proof: TOML load -> inspect -> mutate -> save -> reload.

Uses only the installed format-factory-toml / toml package API.
No src/ path manipulation — pure installed-package consumer.

Steps:
  1. Load TOML file to neutral dict
  2. Inspect: keys, nested sections, values
  3. Mutate: change value, add key, update nested
  4. Save to new TOML file
  5. Reload and verify mutations persisted

Runnable:
  python examples/python/toml/consumer_roundtrip.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]

import toml as toml_pkg
from toml import load_toml, write_toml
from toml.toml_codec import get_value, get_all_keys, has_section, has_key

SAMPLE_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"
OUTPUT_DIR = _REPO / ".local" / "dogfood-proofs" / "toml"


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Source: {SAMPLE_TOML}")
    print(f"TOML package: {toml_pkg.__file__}")
    print()

    # Step 1: Load
    result = load_toml(str(SAMPLE_TOML))
    assert result.get("format") == "toml", f"Expected format=toml, got {result.get('format')}"
    data = result["data"]
    print(f"[LOAD] Top-level keys: {result['top_level_keys']}")
    assert len(result["top_level_keys"]) >= 3

    # Step 2: Inspect
    port = get_value(str(SAMPLE_TOML), "server.port")
    print(f"[INSPECT] server.port={port}")
    assert isinstance(port, int)

    all_keys = get_all_keys(str(SAMPLE_TOML))
    print(f"[INSPECT] All keys: {all_keys}")
    assert "server" in all_keys or "server.port" in all_keys

    assert has_section(str(SAMPLE_TOML), "server")
    assert has_key(str(SAMPLE_TOML), "server.port")
    print("[INSPECT] has_section(server)=True, has_key(server.port)=True")

    # Step 3: Mutate (dict-based mutation)
    data["server"]["port"] = 9999
    data["consumer_proof_key"] = "VERIFIED"
    data["server"]["host"] = "consumer-host"
    print(f"[MUTATE] server.port -> 9999")
    print(f"[MUTATE] consumer_proof_key -> 'VERIFIED'")

    # Step 4: Save
    out_path = OUTPUT_DIR / "consumer_proof.toml"
    write_toml(data, str(out_path))
    assert out_path.exists() and out_path.stat().st_size > 0
    print(f"\n[SAVE] {out_path} ({out_path.stat().st_size} bytes)")
    print(out_path.read_text(encoding="utf-8")[:300])

    # Step 5: Reload and verify
    result2 = load_toml(str(out_path))
    data2 = result2["data"]
    assert data2["server"]["port"] == 9999, f"port={data2['server']['port']}"
    assert data2["consumer_proof_key"] == "VERIFIED", f"key={data2.get('consumer_proof_key')}"
    assert data2["server"]["host"] == "consumer-host"
    print(f"\n[RELOAD] server.port={data2['server']['port']}  OK")
    print(f"[RELOAD] consumer_proof_key={data2['consumer_proof_key']!r}  OK")
    print(f"[RELOAD] server.host={data2['server']['host']!r}  OK")

    print("\nCONSUMER_PROOF: PASS -- load -> inspect -> mutate -> save -> reload verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
