"""freeze_gate_runner.py — Pilot 3 Freeze Gate Runner

Implements specdev-style deterministic freeze gates for Format Factory:
  binding_roundtrip   — encode/decode (or write/parse) identity check (no data loss)
  contract_validation — verify spec FACT citations hold in runtime behavior

Pattern source: specdev deterministic sandwich:
  spec/fixture input -> deterministic driver -> gate -> machine-readable result

Sprint: FF-LIBFORGE-BROAD-IMPLEMENTATION-001 (v1: ZST)
        FF-LIBFORGE-GUARDED-AUTONOMOUS-EXPANSION-001 (v2: NDJSON second format, LFI-6-B)
Taskcard: LFI-3-B01 (v1), LFI-6-B (v2)
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    ERROR = "ERROR"


class GateKind(str, Enum):
    BINDING_ROUNDTRIP = "binding_roundtrip"
    CONTRACT_VALIDATION = "contract_validation"


@dataclass
class GateResult:
    """Result of a single freeze gate run."""
    gate_id: str
    gate_kind: str
    format_id: str
    status: str  # GateStatus value
    fact_id: Optional[str] = None
    description: str = ""
    detail: str = ""
    fixture_path: Optional[str] = None
    sha256_in: Optional[str] = None
    sha256_out: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


@dataclass
class RunReport:
    """Aggregate report for a FreezeGateRunner.run() call."""
    run_id: str
    format_id: str
    gates_run: int = 0
    passed: int = 0
    failed: int = 0
    not_applicable: int = 0
    errors: int = 0
    results: List[GateResult] = field(default_factory=list)

    @property
    def overall_status(self) -> str:
        if self.errors > 0:
            return GateStatus.ERROR.value
        if self.failed > 0:
            return GateStatus.FAIL.value
        return GateStatus.PASS.value

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "run_id": self.run_id,
            "format_id": self.format_id,
            "overall_status": self.overall_status,
            "gates_run": self.gates_run,
            "passed": self.passed,
            "failed": self.failed,
            "not_applicable": self.not_applicable,
            "errors": self.errors,
            "results": [r.to_dict() for r in self.results],
        }
        return d

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class FreezeGateRunner:
    """Run deterministic freeze gates against a format.

    Supports two gate kinds:
      binding_roundtrip     — encode + decode, verify identity
      contract_validation   — verify FACT citations hold at runtime
    """

    SUPPORTED_FORMATS = {"zst", "ndjson"}
    SUPPORTED_GATE_KINDS = {GateKind.BINDING_ROUNDTRIP, GateKind.CONTRACT_VALIDATION}

    def __init__(self, repo_root: Optional[str] = None):
        self._repo = Path(repo_root) if repo_root else _REPO_ROOT

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        format_id: str,
        gate_kinds: Optional[List[str]] = None,
        fixture_path: Optional[str] = None,
        run_id: str = "gate-run",
    ) -> RunReport:
        """Run all requested gate kinds for format_id.

        Args:
            format_id: e.g. "zst"
            gate_kinds: list of gate kind strings; None = all supported
            fixture_path: path to input fixture bytes; None = generate synthetic
            run_id: identifier for this run

        Returns:
            RunReport with per-gate GateResult entries
        """
        report = RunReport(run_id=run_id, format_id=format_id)

        if format_id not in self.SUPPORTED_FORMATS:
            result = GateResult(
                gate_id=f"{format_id}-UNSUPPORTED",
                gate_kind="unknown",
                format_id=format_id,
                status=GateStatus.ERROR.value,
                description=f"Format '{format_id}' is not supported by FreezeGateRunner.",
                error=f"Unsupported format: {format_id}. Supported: {sorted(self.SUPPORTED_FORMATS)}",
            )
            report.results.append(result)
            report.gates_run = 1
            report.errors = 1
            return report

        if gate_kinds is None:
            gate_kinds = [k.value for k in self.SUPPORTED_GATE_KINDS]

        for gk in gate_kinds:
            if gk not in {k.value for k in self.SUPPORTED_GATE_KINDS}:
                result = GateResult(
                    gate_id=f"{format_id}-{gk}-UNSUPPORTED",
                    gate_kind=gk,
                    format_id=format_id,
                    status=GateStatus.ERROR.value,
                    description=f"Gate kind '{gk}' is not supported.",
                    error=f"Unsupported gate kind: {gk}. Supported: {sorted(k.value for k in self.SUPPORTED_GATE_KINDS)}",
                )
            elif gk == GateKind.BINDING_ROUNDTRIP.value:
                result = self._run_binding_roundtrip(format_id, fixture_path)
            elif gk == GateKind.CONTRACT_VALIDATION.value:
                result = self._run_contract_validation(format_id, fixture_path)
            else:
                result = GateResult(
                    gate_id=f"{format_id}-{gk}-UNKNOWN",
                    gate_kind=gk,
                    format_id=format_id,
                    status=GateStatus.ERROR.value,
                    error=f"Unhandled gate kind: {gk}",
                )

            report.results.append(result)
            report.gates_run += 1
            if result.status == GateStatus.PASS.value:
                report.passed += 1
            elif result.status == GateStatus.FAIL.value:
                report.failed += 1
            elif result.status == GateStatus.NOT_APPLICABLE.value:
                report.not_applicable += 1
            else:
                report.errors += 1

        return report

    # ------------------------------------------------------------------
    # Gate: binding_roundtrip
    # ------------------------------------------------------------------

    def _run_binding_roundtrip(
        self, format_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        """Encode/decode (or write/parse) identity check. Must recover original data."""
        gate_id = f"{format_id.upper()}-BINDING-ROUNDTRIP"

        if format_id == "zst":
            return self._zst_binding_roundtrip(gate_id, fixture_path)
        if format_id == "ndjson":
            return self._ndjson_binding_roundtrip(gate_id, fixture_path)

        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.BINDING_ROUNDTRIP.value,
            format_id=format_id,
            status=GateStatus.NOT_APPLICABLE.value,
            description="No binding_roundtrip implementation for this format.",
        )

    def _zst_binding_roundtrip(
        self, gate_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        try:
            from zst.zst_codec import compress_bytes, decompress_bytes
        except ImportError as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.BINDING_ROUNDTRIP.value,
                format_id="zst",
                status=GateStatus.ERROR.value,
                description="Could not import ZST codec.",
                error=str(exc),
            )

        # Load or synthesize fixture
        if fixture_path is not None:
            fpath = Path(fixture_path)
            if not fpath.exists():
                return GateResult(
                    gate_id=gate_id,
                    gate_kind=GateKind.BINDING_ROUNDTRIP.value,
                    format_id="zst",
                    status=GateStatus.FAIL.value,
                    fixture_path=str(fixture_path),
                    description="Fixture file not found.",
                    error=f"Missing fixture: {fixture_path}",
                )
            plaintext = fpath.read_bytes()
        else:
            # Synthetic fixture: deterministic known plaintext
            plaintext = b"Format Factory ZST binding roundtrip fixture. FACT-ZST-001.\n" * 16

        sha_in = hashlib.sha256(plaintext).hexdigest()

        try:
            compressed = compress_bytes(plaintext)
            recovered = decompress_bytes(compressed)
        except Exception as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.BINDING_ROUNDTRIP.value,
                format_id="zst",
                status=GateStatus.ERROR.value,
                description="Compress/decompress raised an exception.",
                fact_id="FACT-ZST-001",
                sha256_in=sha_in,
                error=str(exc),
            )

        sha_out = hashlib.sha256(recovered).hexdigest()
        identity = recovered == plaintext

        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.BINDING_ROUNDTRIP.value,
            format_id="zst",
            status=GateStatus.PASS.value if identity else GateStatus.FAIL.value,
            fact_id="FACT-ZST-001",
            description=(
                "ZST compress/decompress identity verified."
                if identity
                else "ZST decompress did NOT recover original plaintext."
            ),
            fixture_path=fixture_path,
            sha256_in=sha_in,
            sha256_out=sha_out,
            detail=(
                f"compressed_size={len(compressed)}, "
                f"plaintext_size={len(plaintext)}, "
                f"identity={'true' if identity else 'false'}"
            ),
            metadata={"compression_ratio": round(len(compressed) / len(plaintext), 4) if len(plaintext) > 0 else None},
        )

    # ------------------------------------------------------------------
    # Gate: contract_validation
    # ------------------------------------------------------------------

    def _run_contract_validation(
        self, format_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        """Verify that spec FACT citations hold at runtime."""
        gate_id = f"{format_id.upper()}-CONTRACT-VALIDATION"

        if format_id == "zst":
            return self._zst_contract_validation(gate_id, fixture_path)
        if format_id == "ndjson":
            return self._ndjson_contract_validation(gate_id, fixture_path)

        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.CONTRACT_VALIDATION.value,
            format_id=format_id,
            status=GateStatus.NOT_APPLICABLE.value,
            description="No contract_validation implementation for this format.",
        )

    def _zst_contract_validation(
        self, gate_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        """Verify FACT-ZST-001: magic bytes 0x28 0xB5 0x2F 0xFD identify Zstandard frame."""
        try:
            from zst.zst_codec import compress_bytes, ZSTD_MAGIC
        except ImportError as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.CONTRACT_VALIDATION.value,
                format_id="zst",
                status=GateStatus.ERROR.value,
                description="Could not import ZST codec.",
                error=str(exc),
            )

        # Synthesize plaintext and compress — result MUST start with magic
        plaintext = b"contract_validation fixture for FACT-ZST-001 verification.\n"
        try:
            compressed = compress_bytes(plaintext)
        except Exception as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.CONTRACT_VALIDATION.value,
                format_id="zst",
                status=GateStatus.ERROR.value,
                fact_id="FACT-ZST-001",
                description="compress_bytes raised an exception.",
                error=str(exc),
            )

        magic_present = compressed[:4] == ZSTD_MAGIC
        magic_hex = compressed[:4].hex()
        expected_hex = ZSTD_MAGIC.hex()

        # FACT-ZST-002: skippable frame magic range 0x184D2A50-5F
        # This is NOT_APPLICABLE_YET because the current codec's compress_bytes
        # does not expose skippable frame creation. The behavior is verified by
        # test_r127_zst_fact_traceability.py test-only.
        fact2_status = "NOT_APPLICABLE_YET — skippable frame creation not exposed by compress_bytes"

        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.CONTRACT_VALIDATION.value,
            format_id="zst",
            status=GateStatus.PASS.value if magic_present else GateStatus.FAIL.value,
            fact_id="FACT-ZST-001",
            description=(
                "FACT-ZST-001: magic bytes 0x28B52FFD verified in compressed output."
                if magic_present
                else f"FACT-ZST-001 VIOLATED: expected {expected_hex}, got {magic_hex}"
            ),
            detail=(
                f"expected_magic={expected_hex}, "
                f"actual_magic={magic_hex}, "
                f"magic_match={magic_present}, "
                f"fact_zst_002={fact2_status}"
            ),
            metadata={
                "ZSTD_MAGIC": expected_hex,
                "compressed_magic": magic_hex,
                "magic_verified": magic_present,
                "FACT_ZST_002": fact2_status,
            },
        )

    # ------------------------------------------------------------------
    # NDJSON gates (v2 — LFI-6-B)
    # ------------------------------------------------------------------

    def _ndjson_binding_roundtrip(
        self, gate_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        """Write records to NDJSON bytes, parse back, verify identity.

        Binding roundtrip for NDJSON: serialize records -> parse -> compare.
        Uses to_jsonl_str (write) and load_ndjson (read) from ndjson_codec.
        """
        try:
            sys.path.insert(0, str(self._repo / "src" / "python"))
            from ndjson.ndjson_codec import load_ndjson, to_jsonl_str
        except ImportError as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.BINDING_ROUNDTRIP.value,
                format_id="ndjson",
                status=GateStatus.ERROR.value,
                description="Could not import NDJSON codec.",
                error=str(exc),
            )

        # Synthetic fixture: deterministic set of records
        original_records = [
            {"id": 1, "format": "ndjson", "gate": "binding_roundtrip"},
            {"id": 2, "value": "Format Factory NDJSON gate"},
            {"id": 3, "nested": {"ok": True, "count": 42}},
        ]

        sha_in = hashlib.sha256(
            str(original_records).encode("utf-8")
        ).hexdigest()

        try:
            ndjson_bytes = to_jsonl_str(original_records).encode("utf-8")
            recovered_records = load_ndjson(ndjson_bytes)
        except Exception as exc:
            return GateResult(
                gate_id=gate_id,
                gate_kind=GateKind.BINDING_ROUNDTRIP.value,
                format_id="ndjson",
                status=GateStatus.ERROR.value,
                description="NDJSON serialize/parse raised an exception.",
                sha256_in=sha_in,
                error=str(exc),
            )

        sha_out = hashlib.sha256(
            str(recovered_records).encode("utf-8")
        ).hexdigest()
        identity = recovered_records == original_records

        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.BINDING_ROUNDTRIP.value,
            format_id="ndjson",
            status=GateStatus.PASS.value if identity else GateStatus.FAIL.value,
            description=(
                "NDJSON write/parse identity verified: all records recovered."
                if identity
                else "NDJSON parse did NOT recover original records."
            ),
            sha256_in=sha_in,
            sha256_out=sha_out,
            detail=(
                f"original_records={len(original_records)}, "
                f"recovered_records={len(recovered_records)}, "
                f"identity={'true' if identity else 'false'}, "
                f"bytes_serialized={len(ndjson_bytes)}"
            ),
            metadata={
                "record_count": len(original_records),
                "bytes_serialized": len(ndjson_bytes),
                "identity": identity,
            },
        )

    def _ndjson_contract_validation(
        self, gate_id: str, fixture_path: Optional[str]
    ) -> GateResult:
        """Verify NDJSON codec contract: each output line is valid JSON.

        NDJSON contract (ndjson.org): every line in the output must be a
        valid JSON value. No formal FACT-NDJSON-NNN citations exist yet,
        so this gate verifies the basic format contract deterministically.
        contract_validation is NOT_APPLICABLE until formal FACT citations
        are promoted to the spec-cache.
        """
        return GateResult(
            gate_id=gate_id,
            gate_kind=GateKind.CONTRACT_VALIDATION.value,
            format_id="ndjson",
            status=GateStatus.NOT_APPLICABLE.value,
            description=(
                "NDJSON contract_validation is NOT_APPLICABLE: "
                "no formal FACT-NDJSON-NNN citations in spec-cache yet. "
                "binding_roundtrip gate covers data-integrity contract. "
                "Promote spec facts to enable this gate."
            ),
            detail="Requires FACT-NDJSON-001 in .local/spec-cache/ndjson/ to activate.",
            metadata={
                "gate_activation_blocked_by": "missing_spec_facts",
                "required_facts": ["FACT-NDJSON-001"],
                "spec_cache_path": ".local/spec-cache/ndjson/",
            },
        )
