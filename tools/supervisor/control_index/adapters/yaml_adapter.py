"""YAML source adapters."""

from pathlib import Path
from typing import Iterator

import yaml

from . import SourceAdapter


class YamlAdapter(SourceAdapter):
    """Adapter for YAML files with records under a key.

    Example: "formats: [{...}, {...}]" with records_key="formats"
    If records_key is None, yields the entire parsed object as one record.
    """

    def __init__(self, source_path: Path, records_key: str | None = None):
        super().__init__(source_path)
        self.records_key = records_key

    def read_records(self) -> Iterator[dict]:
        data = yaml.safe_load(self.source_path.read_text(encoding="utf-8"))
        if data is None:
            return
        if self.records_key:
            records = data.get(self.records_key, [])
            if isinstance(records, list):
                yield from records
        else:
            if isinstance(data, dict):
                yield data
            elif isinstance(data, list):
                yield from data


class YamlArrayAdapter(SourceAdapter):
    """Adapter for YAML files that are plain arrays (no wrapping key).

    Example: shared/qname-registry/fods.yaml
    """

    def read_records(self) -> Iterator[dict]:
        data = yaml.safe_load(self.source_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            yield from data


class MultiFileYamlAdapter(SourceAdapter):
    """Adapter for a directory of YAML files.

    Reads each .yaml file, yields records with _source_file and _format_id.
    """

    def __init__(self, source_dir: Path, glob_pattern: str = "*.yaml",
                 exclude: list[str] | None = None):
        super().__init__(source_dir)
        self.glob_pattern = glob_pattern
        self.exclude = set(exclude or [])

    def file_hash(self) -> str:
        import hashlib
        h = hashlib.sha256()
        for f in sorted(self._files()):
            h.update(f.read_bytes())
        return h.hexdigest()

    def file_size(self) -> int:
        return sum(f.stat().st_size for f in self._files())

    def _files(self) -> list[Path]:
        return [
            f for f in sorted(self.source_path.glob(self.glob_pattern))
            if f.name not in self.exclude
        ]

    def read_records(self) -> Iterator[dict]:
        for f in self._files():
            try:
                data = yaml.safe_load(f.read_text(encoding="utf-8"))
                format_id = f.stem  # e.g., "fods" from "fods.yaml"
                if isinstance(data, list):
                    for record in data:
                        if isinstance(record, dict):
                            record["_source_file"] = f.name
                            record["_format_id"] = format_id
                            yield record
                elif isinstance(data, dict):
                    data["_source_file"] = f.name
                    data["_format_id"] = format_id
                    yield data
            except (yaml.YAMLError, OSError):
                continue
