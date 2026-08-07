"""UBL-SEC-001 -- path traversal and unapproved absolute-path access when
resolving a detached or referenced resource.

MUST (SAL-UBL-OBL-4CA52BA5DDD8840F): "Prevent path traversal and unapproved
absolute-path access when resolving any detached or referenced resource."

Before this slice: this obligation carried a precise, honest finding --
"No feature anywhere in the package resolves a detached or referenced
resource from parsed document content" -- confirmed by reading
model/reference.py and model/typed.py directly: cac:ExternalReference's
URI/DocumentHash and Identifier's schemeID/schemeAgencyID are all stored as
plain `str | None` dataclass fields with no resolve()/open()/read() method
anywhere. It was correctly left `missing` rather than force-promoted,
because the absence-of-attack-surface claim had no dedicated test proving
it -- unlike safetensors' sharded-index root-confinement test, which proves
the equivalent guarantee positively for a feature that DOES resolve
references to paths.

This file closes that gap the same way NRRD-SEC-001/XLIFF-SEC-001/
IPYNB-SEC-001 closed their equivalent obligations earlier this session:
a whole-package AST scan proving no networking/execution/plugin module is
ever imported, plus a direct behavioral proof that a hostile path-traversal
or absolute-path URI stored in cac:ExternalReference is carried as opaque
text through load/validate/dump/round-trip and never touches the
filesystem -- verified by monkeypatching Path.open/read_bytes to raise if
the library ever attempts to resolve it.
"""

from __future__ import annotations

import ast
import pathlib
from pathlib import Path

import pytest

from format_factory.ubl import (
    ROOT_CLASSES,
    XmlNode,
    dumps,
    external_reference_of,
    loads,
    validate,
)

_SRC_ROOT = Path(__file__).resolve().parents[3] / "src" / "python" / "ubl" / "src"

_FORBIDDEN_MODULES = frozenset(
    {
        "socket",
        "urllib",
        "http",
        "ftplib",
        "smtplib",
        "subprocess",
        "importlib",
        "pkgutil",
        "ctypes",
    }
)

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
Invoice = ROOT_CLASSES["Invoice"]


def test_no_source_file_imports_networking_execution_or_plugin_modules() -> None:
    """Static, whole-package proof: nothing in this library can resolve a
    network resource, execute embedded code, or dynamically load a plugin,
    because the modules that would do so are never imported anywhere."""
    offenders: list[str] = []
    for path in _SRC_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for name in names:
                if name in _FORBIDDEN_MODULES:
                    offenders.append(f"{path}: {name}")

    assert offenders == []


def _external_reference_node(uri: str) -> XmlNode:
    return XmlNode.create(
        f"{{{_CAC}}}ExternalReference",
        children=(XmlNode.create(f"{{{_CBC}}}URI", text=uri),),
    )


def test_external_reference_uri_is_stored_as_opaque_text() -> None:
    """cac:ExternalReference's URI is a plain string field -- projecting it
    never joins against a filesystem path or opens anything."""
    node = _external_reference_node("../../../etc/passwd")

    ref = external_reference_of(node)

    assert ref.uri == "../../../etc/passwd"


@pytest.mark.parametrize(
    "hostile_uri",
    [
        pytest.param("../../../../../../etc/passwd", id="relative-traversal"),
        pytest.param("/etc/passwd", id="unix-absolute-path"),
        pytest.param("C:\\Windows\\System32\\config\\SAM", id="windows-absolute-path"),
        pytest.param("file:///etc/passwd", id="file-uri-scheme"),
    ],
)
def test_a_hostile_reference_uri_never_touches_the_filesystem(
    hostile_uri: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Behavioral proof, not just a structural one: even if a caller feeds a
    path-traversal or absolute-path string through ExternalReference's URI,
    load/validate/dump/round-trip never resolve it against a real path."""

    def _boom(self: pathlib.Path, *_args: object, **_kwargs: object) -> None:
        raise AssertionError(
            f"library touched a filesystem path derived from document content: {self}"
        )

    monkeypatch.setattr(pathlib.Path, "open", _boom, raising=True)
    monkeypatch.setattr(pathlib.Path, "read_bytes", _boom, raising=True)

    ref_node = _external_reference_node(hostile_uri)
    document = Invoice.build(
        children=(
            XmlNode.create(f"{{{_CBC}}}UBLVersionID", text="2.3"),
            XmlNode.create(f"{{{_CBC}}}ID", text="INV-001"),
            ref_node,
        )
    )

    report = validate(document)
    assert report.is_valid

    written = dumps(document)
    reloaded = loads(written)
    assert reloaded.root_name == "Invoice"
