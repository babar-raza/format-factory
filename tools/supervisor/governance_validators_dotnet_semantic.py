"""governance_validators_dotnet_semantic.py — .NET Semantic Stub Validators

Implements three validators for GI-FODS-NET-001 (FODS .NET governance incident):

V87: validate_dotnet_constant_return_public_api
  Detects public Get* methods in src/net/**/*.cs that unconditionally return
  a constant literal (0, false, true, string.Empty, ""). These are semantic stubs
  masquerading as real APIs.

V88: validate_dotnet_detached_dictionary_fields
  Detects private readonly Dictionary fields in src/net/**/*.cs that are
  initialized in-place (= new()) but whose variable name does not appear in
  any XML read path (Attribute(, Element(, XDocument.Load() etc.) in any partial
  class file in the same directory. Heuristic; WARN-only.

V89: validate_dotnet_missingmethods_filename
  FAIL if any src/net/**/*Missing*.cs or src/net/**/*Stub*.cs file appears in
  changed_files as an ADDITION (not a deletion). These filenames signal test-shaped
  implementations.

Incident reference: reports/gov-incidents/GI-FODS-NET-001.yaml
Plan reference:     plans/.claude/buzzing-wiggling-whistle.md
"""

from __future__ import annotations

import re
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_PRODUCT_SOURCE_TYPES = {"PRODUCT_SOURCE", "RELEASE_GATE"}


def _is_release_gate(declaration: dict) -> bool:
    items = declaration.get("planned_work_items", [])
    return any(i.get("item_type") in {"RELEASE_GATE"} for i in items)


def _get_dotnet_source_files(changed_files: list[str]) -> list[str]:
    """Filter changed_files to only src/net/**/*.cs paths."""
    return [f for f in changed_files if re.search(r"src[/\\]net[/\\].*\.cs$", f)]


def _load_whitelist(repo_root: Path) -> set[str]:
    """Load registry/dotnet-semantic-stub-whitelist.yaml; return set of allowed method FQNs."""
    whitelist_path = repo_root / "registry" / "dotnet-semantic-stub-whitelist.yaml"
    if not whitelist_path.exists():
        return set()
    try:
        data = yaml.safe_load(whitelist_path.read_text(encoding="utf-8"))
        return set(data.get("known_constant_return_ok", []))
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# Constant-return detection patterns
# ---------------------------------------------------------------------------

# Matches single-expression arrow methods returning a constant:
#   public int GetFooCount() => 0;
#   public bool GetSomething() => false;
#   public string GetName() => string.Empty;
#   public string GetName() => "";
_CONSTANT_RETURN_ARROW_RE = re.compile(
    r"""
    public \s+                      # public keyword
    (?:\w+\??\s+)+                  # return type (possibly nullable)
    Get\w+                          # Get* method name
    \s* \( [^)]* \)                 # parameter list (any params)
    \s* =>  \s*                     # arrow expression
    (?:0|false|true|string\.Empty|""|'')  # constant literal
    \s* ;                           # semicolon
    """,
    re.VERBOSE,
)

# Matches block-body methods whose ENTIRE body is a single return of a constant:
#   public int GetFooCount(string s) {
#       return 0;
#   }
# We look for the pattern across lines (simplified): after the opening brace,
# optional whitespace/comments, then return <constant>; then closing brace.
_CONSTANT_RETURN_BLOCK_RE = re.compile(
    r"""
    public \s+
    (?:\w+\??\s+)+
    Get\w+
    \s* \( [^)]* \)
    \s* \{
    \s*
    (?://[^\n]*)?\s*         # optional single-line comment
    return \s+
    (?:0|false|true|string\.Empty|""|'')
    \s* ;
    \s* \}
    """,
    re.VERBOSE,
)

# Matches the declaring class + method name for whitelist lookup.
# Looks for:  namespace Foo.Bar; ... public sealed class Baz ... public int GetXxx()
_NAMESPACE_RE = re.compile(r"^namespace\s+([\w.]+)", re.MULTILINE)
_CLASS_RE = re.compile(r"public\s+(?:sealed\s+)?(?:partial\s+)?class\s+(\w+)", re.MULTILINE)
_METHOD_NAME_RE = re.compile(
    r"public\s+(?:\w+\??\s+)+Get(\w+)\s*\([^)]*\)\s*(?:=>|{)",
)


def _extract_constant_return_methods(source: str) -> list[str]:
    """Return list of method names in source that have constant returns."""
    found = set()
    for m in _CONSTANT_RETURN_ARROW_RE.finditer(source):
        name = _METHOD_NAME_RE.search(m.group())
        if name:
            found.add("Get" + name.group(1))
    for m in _CONSTANT_RETURN_BLOCK_RE.finditer(source):
        name = _METHOD_NAME_RE.search(m.group())
        if name:
            found.add("Get" + name.group(1))
    return sorted(found)


def _extract_fqn_prefix(source: str) -> str:
    """Try to build a fully-qualified prefix 'Namespace.ClassName.' for whitelist lookup."""
    ns_m = _NAMESPACE_RE.search(source)
    cls_m = _CLASS_RE.search(source)
    ns = ns_m.group(1) if ns_m else ""
    cls = cls_m.group(1) if cls_m else ""
    if ns and cls:
        return f"{ns}.{cls}."
    return ""


# ---------------------------------------------------------------------------
# V87: validate_dotnet_constant_return_public_api
# ---------------------------------------------------------------------------

def validate_dotnet_constant_return_public_api(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V87: Detect public Get* methods unconditionally returning constant literals.

    Severity:
      FAIL  — for RELEASE_GATE declarations
      WARN  — for all other declarations (PRODUCT_SOURCE, etc.)
    blocks_sprint: True for RELEASE_GATE, False otherwise.

    Whitelist: registry/dotnet-semantic-stub-whitelist.yaml
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)

    if not dotnet_files:
        return {
            "validator": "validate_dotnet_constant_return_public_api",
            "result": "PASS",
            "items": [],
            "summary": "No .NET source files in changed_files — V87 skipped.",
            "blocks_sprint": False,
        }

    whitelist = _load_whitelist(_repo)
    is_rg = _is_release_gate(declaration)
    severity = "FAIL" if is_rg else "WARN"

    violations = []
    for rel_path in dotnet_files:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        fqn_prefix = _extract_fqn_prefix(source)
        methods = _extract_constant_return_methods(source)
        for method in methods:
            fqn = fqn_prefix + method
            # Check whitelist (by FQN or by bare method name)
            if fqn in whitelist or method in whitelist:
                continue
            violations.append({
                "file": rel_path,
                "method": method,
                "fqn": fqn or method,
                "issue": "constant_return_public_api",
                "severity": severity,
                "remediation": (
                    "Remove the method, implement from ODF XML, or add to "
                    "registry/dotnet-semantic-stub-whitelist.yaml if architecturally intentional."
                ),
            })

    if not violations:
        return {
            "validator": "validate_dotnet_constant_return_public_api",
            "result": "PASS",
            "items": [],
            "summary": "V87: No constant-return public APIs detected in .NET source.",
            "blocks_sprint": False,
        }

    blocks = is_rg and any(v["severity"] == "FAIL" for v in violations)
    result = "FAIL" if (is_rg and violations) else "WARN"
    return {
        "validator": "validate_dotnet_constant_return_public_api",
        "result": result,
        "items": violations,
        "summary": (
            f"V87: {len(violations)} constant-return public API(s) detected in .NET source "
            f"({'RELEASE_GATE: blocks sprint' if blocks else 'WARN: advisory'})."
        ),
        "blocks_sprint": blocks,
    }


# ---------------------------------------------------------------------------
# Detached-dictionary detection patterns
# ---------------------------------------------------------------------------

# Matches: private readonly Dictionary<...> _fieldName = new();
# Also matches the fully qualified: private readonly System.Collections.Generic.Dictionary<...>
_DICT_FIELD_RE = re.compile(
    r"private\s+readonly\s+(?:[\w.]*\.)?Dictionary\s*<[^>]+>\s+(_\w+)\s*=\s*new\(\s*\)\s*;",
)

# XML read path keywords that indicate the dictionary is wired to XML
_XML_READ_PATTERNS = [
    "Attribute(",
    "Element(",
    "Elements(",
    "XDocument.Load(",
    "XDocument.Parse(",
    "XElement.Load(",
    "XElement.Parse(",
    ".Load(stream",
    ".Load(filePath",
    "XmlReader",
    "XmlDocument",
]


def _is_dict_wired_to_xml(field_name: str, source_files: list[str], repo_root: Path) -> bool:
    """Heuristic: check if field_name appears near an XML read path in any partial class file."""
    for rel_path in source_files:
        full_path = repo_root / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if field_name not in source:
            continue
        # Check if any XML read pattern appears in the same file
        for pattern in _XML_READ_PATTERNS:
            if pattern in source:
                # Rough proximity: both appear in the file
                return True
    return False


def _get_peer_partial_class_files(rel_path: str, repo_root: Path) -> list[str]:
    """Return all .cs files in the same directory as rel_path (potential partial class peers)."""
    dir_path = (repo_root / rel_path).parent
    if not dir_path.exists():
        return [rel_path]
    peers = [str(f.relative_to(repo_root)).replace("\\", "/")
             for f in dir_path.glob("*.cs")]
    return peers if peers else [rel_path]


# ---------------------------------------------------------------------------
# V88: validate_dotnet_detached_dictionary_fields
# ---------------------------------------------------------------------------

def validate_dotnet_detached_dictionary_fields(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V88 (WARN-only): Detect private readonly Dictionary fields not wired to XML parse paths.

    Heuristic: if the dictionary field name appears in the same file (or peer partial-class
    files) only in setter/getter assignments but never alongside XML read patterns
    (Attribute(, Element(, XDocument.Load( etc.), flag it as potentially detached.

    blocks_sprint: False (advisory only — cross-file dataflow analysis is approximate).
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)

    if not dotnet_files:
        return {
            "validator": "validate_dotnet_detached_dictionary_fields",
            "result": "PASS",
            "items": [],
            "summary": "No .NET source files in changed_files — V88 skipped.",
            "blocks_sprint": False,
        }

    warnings = []
    for rel_path in dotnet_files:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        dict_fields = _DICT_FIELD_RE.findall(source)
        if not dict_fields:
            continue

        peer_files = _get_peer_partial_class_files(rel_path, _repo)

        for field_name in dict_fields:
            if not _is_dict_wired_to_xml(field_name, peer_files, _repo):
                warnings.append({
                    "file": rel_path,
                    "field": field_name,
                    "issue": "detached_dictionary_field",
                    "severity": "WARN",
                    "remediation": (
                        f"Verify '{field_name}' is populated from parsed XML. "
                        "If not, implement the getter from ODF XML instead of this dict, "
                        "and ensure the setter writes to the XML document."
                    ),
                })

    if not warnings:
        return {
            "validator": "validate_dotnet_detached_dictionary_fields",
            "result": "PASS",
            "items": [],
            "summary": "V88: No detached dictionary fields detected (heuristic).",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_detached_dictionary_fields",
        "result": "WARN",
        "items": warnings,
        "summary": (
            f"V88 (advisory): {len(warnings)} potentially detached Dictionary field(s) "
            "in .NET source — verify each is wired to XML parse/write paths."
        ),
        "blocks_sprint": False,
    }


# ---------------------------------------------------------------------------
# V89: validate_dotnet_missingmethods_filename
# ---------------------------------------------------------------------------

_SUSPICIOUS_NAME_RE = re.compile(
    r"(?:Missing(?:Methods?)?|Stubs?|TempApi|MiscApi)\s*\.",
    re.IGNORECASE,
)

# Also detect filenames directly
_SUSPICIOUS_FILE_RE = re.compile(
    r"src[/\\]net[/\\].*?(?:Missing(?:Methods?)?|Stubs?|TempApi|MiscApi).*?\.cs$",
    re.IGNORECASE,
)


def validate_dotnet_missingmethods_filename(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V89: FAIL if src/net/**/*Missing*.cs or *Stub*.cs appears as an addition in changed_files.

    Rationale: 'MissingMethods', 'Stubs', 'TempApi', 'MiscApi' filenames signal
    test-shaped implementations rather than spec-grounded product code.

    Deletions of such files are ALLOWED (they represent remediation in progress).
    blocks_sprint: True on FAIL.
    """
    changed_files = declaration.get("changed_files", [])

    # Determine which files are deletions (not yet tracked in declaration schema,
    # so we use a heuristic: if a changed file no longer exists on disk, it's a deletion)
    _repo = repo_root or REPO_ROOT

    violations = []
    for rel_path in changed_files:
        if not _SUSPICIOUS_FILE_RE.search(rel_path):
            continue
        full_path = _repo / rel_path
        # If the file no longer exists, it was deleted — deletion is allowed
        if not full_path.exists():
            continue  # deletion allowed
        # The file exists and has the suspicious name — this is an addition or modification
        violations.append({
            "file": rel_path,
            "issue": "suspicious_dotnet_product_filename",
            "severity": "FAIL",
            "remediation": (
                "Rename or remove this file. Product APIs must live in domain-appropriate "
                "files (e.g., FodsDocumentAccessor.cs), not in 'MissingMethods'/'Stubs' files. "
                "If this is a staged-removal file (FodsDocumentLegacyCounters.cs pattern), "
                "rename it to use 'LegacyCounters' or 'PendingRemoval' suffix instead."
            ),
        })

    if not violations:
        return {
            "validator": "validate_dotnet_missingmethods_filename",
            "result": "PASS",
            "items": [],
            "summary": "V89: No suspicious .NET product filenames detected.",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_missingmethods_filename",
        "result": "FAIL",
        "items": violations,
        "summary": (
            f"V89: {len(violations)} suspicious .NET product filename(s) detected "
            "(MissingMethods/Stubs/TempApi). These filenames indicate test-shaped "
            "implementations. Blocks sprint."
        ),
        "blocks_sprint": True,
    }


# ---------------------------------------------------------------------------
# V90: validate_dotnet_setter_without_xml_write
# ---------------------------------------------------------------------------

# Detects Set* methods or property setters whose body does NOT contain
# XML write patterns (SetAttributeValue, SetElementValue, FodsStyleEditor, etc.)
_SET_METHOD_RE = re.compile(
    r"public\s+(?:void\s+Set\w+|(?:\w+\??\s+)?set\s*\{)[^}]*\}",
    re.DOTALL,
)
_XML_WRITE_PATTERNS = [
    "SetAttributeValue(",
    "SetElementValue(",
    "FodsStyleEditor",
    ".Add(",
    ".Remove(",
    "XElement(",
    "new XElement",
    "ReplaceWith(",
]

# Matches "public void SetXxx(" style
_PUBLIC_SET_METHOD_RE = re.compile(
    r"public\s+void\s+(Set\w+)\s*\([^)]*\)\s*\{([^}]*)\}",
    re.DOTALL,
)
# Matches "set { ... }" inside a property
_PROPERTY_SET_RE = re.compile(
    r"set\s*\{([^}]*)\}",
    re.DOTALL,
)


def _body_has_xml_write(body: str) -> bool:
    """Return True if the method body contains an XML write pattern."""
    for pat in _XML_WRITE_PATTERNS:
        if pat in body:
            return True
    return False


def _body_is_dict_only(body: str) -> bool:
    """Return True if the body only writes to a dictionary field (no XML)."""
    stripped = body.strip()
    # Heuristic: body contains dict assignment patterns like _field[key] = value
    # but no XML write
    if re.search(r"_\w+\s*\[", stripped) and not _body_has_xml_write(body):
        return True
    return False


def validate_dotnet_setter_without_xml_write(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V90 (WARN): Detect public Set* methods whose body does not contain XML write patterns.

    Advisory — setter in abstract/builder context may be valid.
    blocks_sprint: False.
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)

    if not dotnet_files:
        return {
            "validator": "validate_dotnet_setter_without_xml_write",
            "result": "PASS",
            "items": [],
            "summary": "No .NET source files in changed_files — V90 skipped.",
            "blocks_sprint": False,
        }

    warnings = []
    for rel_path in dotnet_files:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for m in _PUBLIC_SET_METHOD_RE.finditer(source):
            method_name = m.group(1)
            body = m.group(2)
            if _body_is_dict_only(body):
                warnings.append({
                    "file": rel_path,
                    "method": method_name,
                    "issue": "setter_without_xml_write",
                    "severity": "WARN",
                    "remediation": (
                        f"'{method_name}' writes only to an in-memory dictionary. "
                        "Setters for persistent document properties must call "
                        "SetAttributeValue/FodsStyleEditor to update the XDocument."
                    ),
                })

    if not warnings:
        return {
            "validator": "validate_dotnet_setter_without_xml_write",
            "result": "PASS",
            "items": [],
            "summary": "V90: No dictionary-only setters detected.",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_setter_without_xml_write",
        "result": "WARN",
        "items": warnings,
        "summary": (
            f"V90 (advisory): {len(warnings)} Set* method(s) write only to in-memory "
            "dictionaries without XML write path."
        ),
        "blocks_sprint": False,
    }


# ---------------------------------------------------------------------------
# V91: validate_dotnet_getter_without_xml_read
# ---------------------------------------------------------------------------

_PUBLIC_GET_METHOD_RE = re.compile(
    r"public\s+(?!\s*void)(?:\w+\??\s+)(Get\w+)\s*\([^)]*\)\s*\{([^}]*)\}",
    re.DOTALL,
)

_XML_READ_KEYWORD_PATTERNS = [
    "Attribute(",
    "Element(",
    "Elements(",
    "Descendants(",
    "FodsStyleResolver",
    ".Value",
    "XDocument.Load",
    "XElement.Load",
]


def _body_is_field_backed(body: str) -> bool:
    """Return True if the body only reads from a private field with no XML read."""
    stripped = body.strip()
    # Dictionary TryGetValue or direct field return with no XML read
    has_dict_read = bool(
        re.search(r"_\w+\s*\.", stripped) or "TryGetValue" in stripped
    )
    has_xml_read = any(p in body for p in _XML_READ_KEYWORD_PATTERNS)
    return has_dict_read and not has_xml_read


def validate_dotnet_getter_without_xml_read(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V91 (WARN): Detect public Get* methods whose body reads from a field without XML access.

    Advisory — not all getters need XML (e.g., computed properties from parsed model).
    blocks_sprint: False.
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)

    if not dotnet_files:
        return {
            "validator": "validate_dotnet_getter_without_xml_read",
            "result": "PASS",
            "items": [],
            "summary": "No .NET source files in changed_files — V91 skipped.",
            "blocks_sprint": False,
        }

    warnings = []
    for rel_path in dotnet_files:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for m in _PUBLIC_GET_METHOD_RE.finditer(source):
            method_name = m.group(1)
            body = m.group(2)
            if _body_is_field_backed(body):
                warnings.append({
                    "file": rel_path,
                    "method": method_name,
                    "issue": "getter_without_xml_read",
                    "severity": "WARN",
                    "remediation": (
                        f"'{method_name}' reads from a private field with no XML access. "
                        "If this is a persistent document property, the getter must "
                        "read from the XDocument via Attribute()/FodsStyleResolver."
                    ),
                })

    if not warnings:
        return {
            "validator": "validate_dotnet_getter_without_xml_read",
            "result": "PASS",
            "items": [],
            "summary": "V91: No field-backed getters without XML read detected.",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_getter_without_xml_read",
        "result": "WARN",
        "items": warnings,
        "summary": (
            f"V91 (advisory): {len(warnings)} Get* method(s) read from private fields "
            "without any XML read path."
        ),
        "blocks_sprint": False,
    }


# ---------------------------------------------------------------------------
# V92: validate_dotnet_fods_extended_apis_loc
# ---------------------------------------------------------------------------

_EXTENDED_APIS_FILENAME = "FodsDocumentExtendedApis.cs"
_EXTENDED_APIS_LOC_CAP = 800


def validate_dotnet_fods_extended_apis_loc(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V92 (FAIL): FodsDocumentExtendedApis.cs must not exceed 800 LOC.

    This file must be split before adding more content.
    blocks_sprint: True on FAIL (structural governance cap).
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)

    # Find the extended APIs file in changed_files or scan src/net/fods/ directly
    candidates = [
        f for f in dotnet_files if f.endswith(_EXTENDED_APIS_FILENAME)
    ]
    if not candidates:
        # Also check if it exists on disk (it may be unchanged but still violating)
        for pattern in ["src/net/fods/FodsDocumentExtendedApis.cs",
                        "src/net/fodt/FodtDocumentExtendedApis.cs"]:
            p = _repo / pattern
            if p.exists():
                candidates.append(pattern)

    if not candidates:
        return {
            "validator": "validate_dotnet_fods_extended_apis_loc",
            "result": "PASS",
            "items": [],
            "summary": "V92: No ExtendedApis files found to check.",
            "blocks_sprint": False,
        }

    violations = []
    for rel_path in candidates:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            loc = sum(1 for _ in full_path.open(encoding="utf-8", errors="replace"))
        except Exception:
            continue
        if loc > _EXTENDED_APIS_LOC_CAP:
            violations.append({
                "file": rel_path,
                "loc": loc,
                "cap": _EXTENDED_APIS_LOC_CAP,
                "excess": loc - _EXTENDED_APIS_LOC_CAP,
                "issue": "extended_apis_loc_exceeded",
                "severity": "FAIL",
                "remediation": (
                    f"Split {_EXTENDED_APIS_FILENAME} ({loc} LOC) into domain-specific "
                    f"partial class files before adding new methods. Cap: {_EXTENDED_APIS_LOC_CAP} LOC."
                ),
            })

    if not violations:
        return {
            "validator": "validate_dotnet_fods_extended_apis_loc",
            "result": "PASS",
            "items": [],
            "summary": f"V92: All ExtendedApis files within {_EXTENDED_APIS_LOC_CAP} LOC cap.",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_dotnet_fods_extended_apis_loc",
        "result": "FAIL",
        "items": violations,
        "summary": (
            f"V92: {len(violations)} ExtendedApis file(s) exceed {_EXTENDED_APIS_LOC_CAP} LOC. "
            "Split required before adding more content. Blocks sprint."
        ),
        "blocks_sprint": True,
    }
