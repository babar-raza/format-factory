"""Spec normalization adapter — loads normalized spec chunks with provenance.

AI consumes only normalized artifacts, never raw PDFs or ad hoc files.
Each chunk retains format, source path, source hash, section, extraction method,
normalization version, and chunk hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class NormalizedChunk:
    """A single normalized chunk from a format specification."""
    format_id: str
    source_path: str
    source_hash: str
    section: str = ""
    page: str = ""
    extraction_method: str = ""
    normalization_version: str = ""
    chunk_hash: str = ""
    content: str = ""

    def compute_hash(self) -> str:
        self.chunk_hash = hashlib.sha256(self.content.encode()).hexdigest()[:16]
        return self.chunk_hash

    def validate_provenance(self) -> list[str]:
        """Validate that all provenance fields are present."""
        errors: list[str] = []
        if not self.format_id:
            errors.append("missing format_id")
        if not self.source_path:
            errors.append("missing source_path")
        if not self.source_hash:
            errors.append("missing source_hash")
        if not self.extraction_method:
            errors.append("missing extraction_method")
        if not self.normalization_version:
            errors.append("missing normalization_version")
        if not self.chunk_hash:
            errors.append("missing chunk_hash")
        return errors

    def to_dict(self) -> dict[str, Any]:
        return {
            "format_id": self.format_id,
            "source_path": self.source_path,
            "source_hash": self.source_hash,
            "section": self.section,
            "page": self.page,
            "extraction_method": self.extraction_method,
            "normalization_version": self.normalization_version,
            "chunk_hash": self.chunk_hash,
            "content": self.content,
        }


class NormalizationNotAvailable(Exception):
    """Raised when no normalized artifact exists for a format."""
    pass


def discover_normalized_artifacts(format_id: str, base_dir: Path | None = None) -> list[Path]:
    """Discover available normalized spec artifacts for a format.

    Looks in generated-requirements/{format_id}/ and
    acquisition-packs/{format_id}/normalized/ for JSONL/Markdown files.
    """
    if base_dir is None:
        base_dir = Path(".")

    search_dirs = [
        base_dir / "generated-requirements" / format_id,
        base_dir / "acquisition-packs" / format_id / "normalized",
    ]

    artifacts: list[Path] = []
    for d in search_dirs:
        if d.exists():
            for ext in ("*.jsonl", "*.md", "*.json"):
                artifacts.extend(d.glob(ext))
    return sorted(artifacts)


def load_chunks_from_jsonl(path: Path) -> list[NormalizedChunk]:
    """Load normalized chunks from a JSONL file."""
    chunks: list[NormalizedChunk] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            chunk = NormalizedChunk(
                format_id=data.get("format_id", ""),
                source_path=data.get("source_path", ""),
                source_hash=data.get("source_hash", ""),
                section=data.get("section", ""),
                page=data.get("page", ""),
                extraction_method=data.get("extraction_method", ""),
                normalization_version=data.get("normalization_version", ""),
                chunk_hash=data.get("chunk_hash", ""),
                content=data.get("content", ""),
            )
            chunks.append(chunk)
    return chunks


def load_normalized_chunks(format_id: str, base_dir: Path | None = None) -> list[NormalizedChunk]:
    """Load all normalized chunks for a format.

    Raises NormalizationNotAvailable if no artifacts exist.
    """
    artifacts = discover_normalized_artifacts(format_id, base_dir)
    if not artifacts:
        raise NormalizationNotAvailable(
            f"No normalized artifacts found for format '{format_id}'. "
            f"Spec normalization must be completed before AI can consume this format."
        )

    all_chunks: list[NormalizedChunk] = []
    for artifact in artifacts:
        if artifact.suffix == ".jsonl":
            all_chunks.extend(load_chunks_from_jsonl(artifact))

    return all_chunks


def validate_chunk_freshness(chunk: NormalizedChunk, current_source_hash: str) -> bool:
    """Check if a chunk's source hash matches the current source hash."""
    return chunk.source_hash == current_source_hash
