"""Lossless structural UBL model with typed document-root subclasses."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import ClassVar, Iterator, Mapping

from .._generated import ROOT_NAMESPACES

#: cbc:UBLVersionID identifies the UBL specification version a document
#: instance declares (UBL-PROFILE-001 / SAL-UBL-OBL-FC5C33152AFDB187).
#: cbc:CustomizationID and cbc:ProfileID identify the customization profile
#: and business process profile a document instance follows
#: (SAL-UBL-OBL-965E8CAEA15E1281).
_CBC_NAMESPACE = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
_UBL_VERSION_QNAME = f"{{{_CBC_NAMESPACE}}}UBLVersionID"
_CUSTOMIZATION_ID_QNAME = f"{{{_CBC_NAMESPACE}}}CustomizationID"
_PROFILE_ID_QNAME = f"{{{_CBC_NAMESPACE}}}ProfileID"


def _first_child_text(root: "XmlNode", qname: str) -> str | None:
    for child in root.children:
        if child.qname == qname:
            return child.text.strip()
    return None


def ubl_version_id(root: "XmlNode") -> str | None:
    """The document's own declared cbc:UBLVersionID text, or None if absent.

    Reads the first matching child (a spec-conformant document has exactly
    one; validate() separately flags more than one as an error -- this
    accessor does not itself adjudicate that ambiguity).
    """
    return _first_child_text(root, _UBL_VERSION_QNAME)


@dataclass(frozen=True, slots=True)
class XmlNode:
    """Immutable XML node preserving QName, attributes, text, tail, and order."""

    qname: str
    attributes: tuple[tuple[str, str], ...] = ()
    text: str = ""
    children: tuple["XmlNode", ...] = ()
    tail: str = ""

    def __post_init__(self) -> None:
        if not self.qname:
            raise ValueError("qname must not be empty")
        if self.attributes != tuple(sorted(self.attributes)):
            raise ValueError("attributes must be sorted by QName")
        if len({key for key, _ in self.attributes}) != len(self.attributes):
            raise ValueError("attribute QNames must be unique")

    @classmethod
    def create(
        cls,
        qname: str,
        *,
        attributes: Mapping[str, str] | None = None,
        text: str = "",
        children: tuple["XmlNode", ...] = (),
        tail: str = "",
    ) -> "XmlNode":
        return cls(
            qname=qname,
            attributes=tuple(sorted((attributes or {}).items())),
            text=text,
            children=children,
            tail=tail,
        )

    def iter(self) -> Iterator["XmlNode"]:
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def with_children(self, children: tuple["XmlNode", ...]) -> "XmlNode":
        return replace(self, children=children)


@dataclass(frozen=True, slots=True)
class UblDocument:
    """Base class for a typed UBL document root."""

    root: XmlNode
    source_sha256: str | None = None
    signed_content_sha256: str | None = None
    detected_version: str | None = None

    ROOT_NAME: ClassVar[str] = ""

    def __post_init__(self) -> None:
        if self.ROOT_NAME and self.root_name != self.ROOT_NAME:
            raise ValueError(
                f"{type(self).__name__} requires root {self.ROOT_NAME}, "
                f"got {self.root_name}"
            )

    @property
    def root_name(self) -> str:
        return self.root.qname.rsplit("}", 1)[-1]

    @property
    def declared_version(self) -> str | None:
        """The version this document's tree currently declares (live).

        Distinct from `detected_version`, which is set only once by the
        reader from the file that was actually parsed and never changes
        afterward -- editing the tree (e.g. via `with_root`) changes what
        is declared without touching what was detected. UBL-LIFECYCLE-001:
        "expose the detected format version and any declared version
        separately; never silently rewrite a declared version."
        """
        return ubl_version_id(self.root)

    @property
    def customization_id(self) -> str | None:
        """The document's declared cbc:CustomizationID, or None if absent.

        Identifies the customization profile a document instance follows
        (UBL-PROFILE-001 / SAL-UBL-OBL-965E8CAEA15E1281). Live, like
        `declared_version`: reflects the current tree, not a value frozen
        at parse time.
        """
        return _first_child_text(self.root, _CUSTOMIZATION_ID_QNAME)

    @property
    def profile_id(self) -> str | None:
        """The document's declared cbc:ProfileID, or None if absent.

        Identifies the business process profile a document instance follows
        (UBL-PROFILE-001 / SAL-UBL-OBL-965E8CAEA15E1281).
        """
        return _first_child_text(self.root, _PROFILE_ID_QNAME)

    @property
    def namespace(self) -> str:
        if not self.root.qname.startswith("{"):
            return ""
        return self.root.qname[1:].split("}", 1)[0]

    @property
    def signature_preserved(self) -> bool:
        return (
            self.signed_content_sha256 is not None
            and self.source_sha256 == self.signed_content_sha256
        )

    def with_root(self, root: XmlNode) -> "UblDocument":
        """Return an edited document and invalidate any signature assertion.

        `detected_version` is carried forward unchanged: it records what the
        originally-read file declared, which an in-memory edit does not
        alter, even when the edit itself changes `declared_version`.
        """

        return type(self)(
            root=root,
            source_sha256=None,
            signed_content_sha256=None,
            detected_version=self.detected_version,
        )

    @classmethod
    def build(
        cls,
        *,
        attributes: Mapping[str, str] | None = None,
        children: tuple[XmlNode, ...] = (),
    ) -> "UblDocument":
        if not cls.ROOT_NAME:
            raise TypeError("build() must be called on a generated root subclass")
        namespace = ROOT_NAMESPACES[cls.ROOT_NAME]
        return cls(
            XmlNode.create(
                f"{{{namespace}}}{cls.ROOT_NAME}",
                attributes=attributes,
                children=children,
            )
        )
