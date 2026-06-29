"""JSON and JSONL source adapters."""

import json
from pathlib import Path
from typing import Iterator

from . import SourceAdapter


class JsonAdapter(SourceAdapter):
    """Adapter for JSON files with an array of records under a key.

    Example: {"gaps": [{...}, {...}]} with records_key="gaps"
    If records_key is None, yields the entire parsed object as one record.
    """

    def __init__(self, source_path: Path, records_key: str | None = None):
        super().__init__(source_path)
        self.records_key = records_key

    def read_records(self) -> Iterator[dict]:
        data = json.loads(self.source_path.read_text(encoding="utf-8"))
        if self.records_key:
            yield from data.get(self.records_key, [])
        else:
            yield data


class JsonlAdapter(SourceAdapter):
    """Adapter for JSONL (newline-delimited JSON) files.

    Each line is an independent JSON object.
    """

    def read_records(self) -> Iterator[dict]:
        with self.source_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue


class DictAdapter(SourceAdapter):
    """Adapter for JSON files where keys are record IDs.

    Example: {"item_id:hash": {adequate: true, ...}}
    Yields each value with _key added.
    """

    def read_records(self) -> Iterator[dict]:
        data = json.loads(self.source_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    yield {"_key": key, **value}


class MultiFileJsonAdapter(SourceAdapter):
    """Adapter for a directory of individual JSON files.

    Example: .local/supervisor/plan-locks/*.json
    Reads each .json file and yields its parsed content with _source_file.
    """

    def __init__(self, source_dir: Path, glob_pattern: str = "*.json"):
        super().__init__(source_dir)
        self.glob_pattern = glob_pattern

    def file_hash(self) -> str:
        """Combined hash of all files in directory."""
        import hashlib
        h = hashlib.sha256()
        for f in sorted(self.source_path.glob(self.glob_pattern)):
            h.update(f.read_bytes())
        return h.hexdigest()

    def file_size(self) -> int:
        """Total size of all files."""
        return sum(
            f.stat().st_size
            for f in self.source_path.glob(self.glob_pattern)
        )

    def read_records(self) -> Iterator[dict]:
        for f in sorted(self.source_path.glob(self.glob_pattern)):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    data["_source_file"] = f.name
                    yield data
            except (json.JSONDecodeError, OSError):
                continue
