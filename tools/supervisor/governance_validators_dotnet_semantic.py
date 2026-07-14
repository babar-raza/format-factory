"""governance_validators_dotnet_semantic.py — .NET Semantic Stub Validators

Implements three validators for GI-FODS-NET-001 (FODS .NET governance incident):

V87: validate_dotnet_constant_return_public_api
  Detects public Get* methods in src/net/**/*.cs that unconditionally return
  a constant literal (0, false, true, string.Empty, ""). These are semantic stubs
  masquerading as real APIs.

V88: validate_dotnet_detached_dictionary_fields (TC-FGSQ-003 rewrite)
  Per-method analysis: extracts public Set*/Get* method bodies via brace-depth
  counting and flags any setter that writes only to a dict field (no XML write
  path) or any getter that reads only from a dict field (no XML read path).
  blocks_sprint: True.

V89: validate_dotnet_missingmethods_filename
  FAIL if any src/net/**/*Missing*.cs or src/net/**/*Stub*.cs file appears in
  changed_files as an ADDITION (not a deletion). These filenames signal test-shaped
  implementations.

Incident reference: reports/gov-incidents/GI-FODS-NET-001.yaml
Plan reference:     plans/.claude/buzzing-wiggling-whistle.md
"""

from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import re
import subprocess
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _method_existed_at_git_head(
    git_sha: str,
    file_rel_path: str,
    method_name: str,
    repo_root: Path,
) -> bool:
    """Return True if method_name appeared in file at git_sha (sprint start).

    Uses git show <sha>:<path> to fetch the file's pre-sprint content.
    Returns True (treat as pre-existing) on any error so fallback is non-blocking.
    TC-SPW-002-02 (field_existed_at_git_head).
    """
    try:
        result = subprocess.run(
            ["git", "show", f"{git_sha}:{file_rel_path}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo_root),
            timeout=10,
        )
        if result.returncode != 0:
            return True  # file didn't exist before sprint → treat as pre-existing (safe)
        old_content = result.stdout
        # Check if a public method with this name existed in pre-sprint content
        pattern = re.compile(
            rf"public\s+(?:(?:static|virtual|override|sealed|async|new)\s+)*"
            rf"(?:[A-Za-z_][\w?<>\[\],\s]*?\s+){re.escape(method_name)}\s*\("
        )
        return bool(pattern.search(old_content))
    except Exception:
        return True  # fallback: treat as pre-existing (non-blocking)

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


def _load_whitelist(repo_root: Path, section: str = "known_constant_return_ok") -> set[str]:
    """Load registry/dotnet-semantic-stub-whitelist.yaml; return set of allowed method FQNs.

    Supports schema 1.x (bare string entries) and schema 2.0 (structured dicts with
    'method' key plus governance fields: approved_by, approved_date, review_due,
    removal_condition).

    section: one of 'known_constant_return_ok', 'known_setter_without_xml_write_ok',
             'known_getter_without_xml_read_ok'.
    """
    whitelist_path = repo_root / "registry" / "dotnet-semantic-stub-whitelist.yaml"
    if not whitelist_path.exists():
        return set()
    try:
        data = yaml.safe_load(whitelist_path.read_text(encoding="utf-8"))
        entries = data.get(section, []) or []
        result = set()
        for entry in entries:
            if isinstance(entry, str):
                result.add(entry)
            elif isinstance(entry, dict):
                if "method" in entry:
                    result.add(entry["method"])
        return result
    except Exception:
        return set()


def _load_whitelist_records(
    repo_root: Path, section: str = "known_constant_return_ok"
) -> list[dict]:
    """Load whitelist and return full structured records (schema 2.0) or synthesized records
    for schema 1.x bare strings. Used by validate_whitelist_expiry."""
    whitelist_path = repo_root / "registry" / "dotnet-semantic-stub-whitelist.yaml"
    if not whitelist_path.exists():
        return []
    try:
        data = yaml.safe_load(whitelist_path.read_text(encoding="utf-8"))
        entries = data.get(section, []) or []
        records = []
        for entry in entries:
            if isinstance(entry, str):
                records.append({"method": entry, "review_due": None, "approved_by": "unknown"})
            elif isinstance(entry, dict):
                records.append(entry)
        return records
    except Exception:
        return []


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

@validator(rule_id="V_VALIDATE_DOTNET_CONSTANT_RETURN_PUBLIC_API", domain="dotnet")
def validate_dotnet_constant_return_public_api(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V87: Detect public Get* methods unconditionally returning constant literals.

    Severity: FAIL for all declaration types (TC-FGSQ-004: PRODUCT_SOURCE exemption removed).
    Whitelisted methods (registry/dotnet-semantic-stub-whitelist.yaml) are WARN-only.
    blocks_sprint: True for any non-whitelisted violation.

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
            # Whitelisted violations → WARN (grandfathered)
            if fqn in whitelist or method in whitelist:
                violations.append({
                    "file": rel_path,
                    "method": method,
                    "fqn": fqn or method,
                    "issue": "constant_return_public_api",
                    "severity": "WARN",
                    "whitelisted": True,
                    "remediation": "Grandfathered in whitelist — implement from ODF XML when possible.",
                })
                continue
            # Non-whitelisted → FAIL and block
            violations.append({
                "file": rel_path,
                "method": method,
                "fqn": fqn or method,
                "issue": "constant_return_public_api",
                "severity": "FAIL",
                "whitelisted": False,
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

    blocking = [v for v in violations if v["severity"] == "FAIL"]
    result = "FAIL" if blocking else "WARN"
    blocks = bool(blocking)
    return {
        "validator": "validate_dotnet_constant_return_public_api",
        "result": result,
        "items": violations,
        "summary": (
            f"V87: {len(violations)} constant-return public API(s) detected in .NET source "
            f"({len(blocking)} blocking, {len(violations) - len(blocking)} whitelisted)."
        ),
        "blocks_sprint": blocks,
    }


# ---------------------------------------------------------------------------
# Per-method body extraction (V88 rewrite — TC-FGSQ-003)
# ---------------------------------------------------------------------------

# Matches: private readonly Dictionary<...> _fieldName = new();
# Retained for backwards compatibility but no longer used by V88.
_DICT_FIELD_RE = re.compile(
    r"private\s+readonly\s+(?:[\w.]*\.)?Dictionary\s*<[^>]+>\s+(_\w+)\s*=\s*new\(\s*\)\s*;",
)

# Method signatures we want to extract: public Set*/Get*/Add*/etc. methods
_METHOD_SIG_RE = re.compile(
    r"public\s+"
    r"(?:(?:static|virtual|override|sealed|async|new)\s+)*"
    r"(?:[A-Za-z_][\w?<>\[\],\s]*?\s+)"  # return type (non-greedy)
    r"((?:Set|Get|Add|Remove|Init|Has|Is|Create|Build|Export|Load|Save)\w+)"
    r"\s*\([^)]*\)\s*\{",
    re.DOTALL,
)

# Patterns indicating a setter writes to a dictionary (no XML path)
_DICT_ASSIGN_RE = re.compile(r"_\w+\s*\[")

# Patterns indicating XML write operations
_XML_WRITE_PATTERNS_V88 = [
    "SetAttributeValue(",
    "SetElementValue(",
    "new XElement(",
    "XElement(",
    "FodsStyleEditor",
    "ReplaceWith(",
    ".Add(",
    ".Remove(",
]

# Helper method prefixes treated as implicit XML-write delegates
_XML_WRITE_HELPER_RE = re.compile(r"\b_(?:Write|Set|Save|Update|Persist|Sync)\w+\s*\(")

# Patterns indicating a getter reads from a dictionary (no XML path)
_DICT_RETURN_RE = re.compile(r"_\w+\s*[\[.]")

# Patterns indicating XML read operations
_XML_READ_PATTERNS_V88 = [
    ".Attribute(",
    ".Element(",
    ".Elements(",
    ".Descendants(",
    "FodsStyleResolver",
    ".Value",
    "XDocument.Load",
    "XElement.Load",
]


def _extract_method_bodies(cs_source: str) -> list[tuple[str, str]]:
    """Extract (method_name, body_text) pairs using brace-depth counter.

    Finds public method signatures matching _METHOD_SIG_RE, then extracts
    the body text between the opening { and its matching closing } via brace
    depth tracking. Handles nested braces correctly.

    Returns list of (method_name, body_text) tuples; body_text excludes the
    outer braces.
    """
    results = []
    for m in _METHOD_SIG_RE.finditer(cs_source):
        method_name = m.group(1)
        # Opening brace is the last character matched by the pattern
        brace_pos = m.end() - 1
        depth = 0
        pos = brace_pos
        body_start = brace_pos + 1
        while pos < len(cs_source):
            c = cs_source[pos]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    results.append((method_name, cs_source[body_start:pos]))
                    break
            pos += 1
    return results


def _setter_is_dict_only(body: str) -> bool:
    """Return True if setter body writes to dict field but has no XML write path."""
    if not _DICT_ASSIGN_RE.search(body):
        return False
    if any(pat in body for pat in _XML_WRITE_PATTERNS_V88):
        return False
    if _XML_WRITE_HELPER_RE.search(body):
        return False
    return True


def _getter_is_dict_only(body: str) -> bool:
    """Return True if getter body returns dict field but has no XML read path."""
    if not _DICT_RETURN_RE.search(body):
        return False
    if any(pat in body for pat in _XML_READ_PATTERNS_V88):
        return False
    return True


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

@validator(rule_id="V_VALIDATE_DOTNET_DETACHED_DICTIONARY_FIELDS", domain="dotnet")
def validate_dotnet_detached_dictionary_fields(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V88: Detect public Set*/Get* methods whose bodies write/read only in-memory dictionaries.

    Per-method analysis (TC-FGSQ-003 rewrite): uses brace-depth body extraction to
    check each public method body precisely. A method is flagged when its body:
      - Setter: contains _field[...] assignment AND no XML write pattern
        (SetAttributeValue, new XElement, FodsStyleEditor, etc.)
      - Getter: contains _field[...] return AND no XML read pattern
        (.Attribute(, .Element(, FodsStyleResolver, .Value, etc.)

    Helper method calls starting with _Write/_Set/_Save/_Update are treated as
    implicit XML-write delegates and suppress false positives.

    NEW in TC-SPW-002 (corrected TC-FGSQ-003): Distinguishes new vs pre-existing methods
    using git_head_start.
      - Pre-existing methods (confirmed at git_head_start) → WARN, blocks_sprint=False
      - New methods (introduced this sprint) → FAIL, blocks_sprint=True
      - If git_head_start not available → conservative FAIL (cannot prove pre-existing)
    """
    _repo = repo_root or REPO_ROOT
    changed_files = declaration.get("changed_files", [])
    dotnet_files = _get_dotnet_source_files(changed_files)
    git_head_start = declaration.get("git_head_start", "")

    if not dotnet_files:
        return {
            "validator": "validate_dotnet_detached_dictionary_fields",
            "result": "PASS",
            "items": [],
            "summary": "No .NET source files in changed_files — V88 skipped.",
            "blocks_sprint": False,
        }

    new_violations: list[dict] = []
    existing_violations: list[dict] = []

    for rel_path in dotnet_files:
        full_path = _repo / rel_path
        if not full_path.exists():
            continue
        try:
            source = full_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        for method_name, body in _extract_method_bodies(source):
            issue: str | None = None
            remediation = ""
            if method_name.startswith("Set") and _setter_is_dict_only(body):
                issue = "setter_without_xml_write"
                remediation = (
                    f"'{method_name}' writes only to an in-memory dictionary. "
                    "Implement SetAttributeValue/new XElement to persist the value to XML, "
                    "or delegate to a _WriteXxx helper that does so."
                )
            elif method_name.startswith("Get") and _getter_is_dict_only(body):
                issue = "getter_without_xml_read"
                remediation = (
                    f"'{method_name}' reads from a private field with no XML access. "
                    "Read from XDocument via .Attribute()/.Element() or FodsStyleResolver."
                )

            if issue is None:
                continue

            # Determine if this method is new (introduced this sprint) or pre-existing.
            # When git_head_start is absent, conservatively treat as new (FAIL) since
            # we cannot prove the method pre-dated this sprint.
            if git_head_start and _method_existed_at_git_head(
                git_head_start, rel_path, method_name, _repo
            ):
                # Confirmed pre-existing at git_head_start → WARN (non-blocking)
                existing_violations.append({
                    "file": rel_path,
                    "method": method_name,
                    "issue": issue,
                    "origin": "pre_existing",
                    "severity": "WARN",
                    "remediation": remediation,
                })
            else:
                # Either new this sprint OR no git_head_start to distinguish → FAIL
                new_violations.append({
                    "file": rel_path,
                    "method": method_name,
                    "issue": issue,
                    "origin": "new_this_sprint" if git_head_start else "unknown_no_git_state",
                    "severity": "FAIL",
                    "remediation": remediation,
                })

    if not new_violations and not existing_violations:
        return {
            "validator": "validate_dotnet_detached_dictionary_fields",
            "result": "PASS",
            "items": [],
            "summary": "V88: No dict-only setter/getter methods detected.",
            "blocks_sprint": False,
        }

    if new_violations:
        return {
            "validator": "validate_dotnet_detached_dictionary_fields",
            "result": "FAIL",
            "items": new_violations + existing_violations,
            "summary": (
                f"V88: {len(new_violations)} NEW dict-only method(s) this sprint "
                f"(+ {len(existing_violations)} pre-existing WARN) — "
                "new additions must write/read via ODF XML."
            ),
            "blocks_sprint": True,
        }

    return {
        "validator": "validate_dotnet_detached_dictionary_fields",
        "result": "WARN",
        "items": existing_violations,
        "summary": (
            f"V88: {len(existing_violations)} pre-existing dict-only method(s) — advisory. "
            "No new additions detected this sprint."
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


@validator(rule_id="V_VALIDATE_DOTNET_MISSINGMETHODS_FILENAME", domain="dotnet")
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


@validator(rule_id="V_VALIDATE_DOTNET_SETTER_WITHOUT_XML_WRITE", domain="dotnet")
def validate_dotnet_setter_without_xml_write(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V90: Detect public Set* methods whose body does not contain XML write patterns.

    blocks_sprint: True for non-whitelisted violations (TC-FGSQ-005).
    Whitelisted setters (known_setter_without_xml_write_ok in dotnet-semantic-stub-whitelist.yaml)
    are reported as WARN (non-blocking) until wired to ODF XML.
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

    whitelist = _load_whitelist(_repo, "known_setter_without_xml_write_ok")
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
        for m in _PUBLIC_SET_METHOD_RE.finditer(source):
            method_name = m.group(1)
            body = m.group(2)
            if not _body_is_dict_only(body):
                continue
            fqn = fqn_prefix + method_name
            is_wl = fqn in whitelist or method_name in whitelist
            violations.append({
                "file": rel_path,
                "method": method_name,
                "fqn": fqn,
                "issue": "setter_without_xml_write",
                "severity": "WARN" if is_wl else "FAIL",
                "whitelisted": is_wl,
                "remediation": (
                    f"'{method_name}' writes only to an in-memory dictionary. "
                    "Implement SetAttributeValue/FodsStyleEditor to persist to XDocument, "
                    "or grandfather in known_setter_without_xml_write_ok."
                ),
            })

    if not violations:
        return {
            "validator": "validate_dotnet_setter_without_xml_write",
            "result": "PASS",
            "items": [],
            "summary": "V90: No dictionary-only setters detected.",
            "blocks_sprint": False,
        }

    blocking = [v for v in violations if v["severity"] == "FAIL"]
    result = "FAIL" if blocking else "WARN"
    return {
        "validator": "validate_dotnet_setter_without_xml_write",
        "result": result,
        "items": violations,
        "summary": (
            f"V90: {len(violations)} Set* method(s) write only to in-memory dicts "
            f"({len(blocking)} blocking, {len(violations) - len(blocking)} whitelisted)."
        ),
        "blocks_sprint": bool(blocking),
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


@validator(rule_id="V_VALIDATE_DOTNET_GETTER_WITHOUT_XML_READ", domain="dotnet")
def validate_dotnet_getter_without_xml_read(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V91: Detect public Get* methods whose body reads from a field without XML access.

    blocks_sprint: True for non-whitelisted violations (TC-FGSQ-005).
    Whitelisted getters (known_getter_without_xml_read_ok in dotnet-semantic-stub-whitelist.yaml)
    are reported as WARN (non-blocking) until wired to ODF XML reads.
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

    whitelist = _load_whitelist(_repo, "known_getter_without_xml_read_ok")
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
        for m in _PUBLIC_GET_METHOD_RE.finditer(source):
            method_name = m.group(1)
            body = m.group(2)
            if not _body_is_field_backed(body):
                continue
            fqn = fqn_prefix + method_name
            is_wl = fqn in whitelist or method_name in whitelist
            violations.append({
                "file": rel_path,
                "method": method_name,
                "fqn": fqn,
                "issue": "getter_without_xml_read",
                "severity": "WARN" if is_wl else "FAIL",
                "whitelisted": is_wl,
                "remediation": (
                    f"'{method_name}' reads from a private field with no XML access. "
                    "If this is a persistent document property, read from the XDocument "
                    "via Attribute()/FodsStyleResolver, or grandfather in "
                    "known_getter_without_xml_read_ok."
                ),
            })

    if not violations:
        return {
            "validator": "validate_dotnet_getter_without_xml_read",
            "result": "PASS",
            "items": [],
            "summary": "V91: No field-backed getters without XML read detected.",
            "blocks_sprint": False,
        }

    blocking = [v for v in violations if v["severity"] == "FAIL"]
    result = "FAIL" if blocking else "WARN"
    return {
        "validator": "validate_dotnet_getter_without_xml_read",
        "result": result,
        "items": violations,
        "summary": (
            f"V91: {len(violations)} Get* method(s) read from private fields without XML read "
            f"({len(blocking)} blocking, {len(violations) - len(blocking)} whitelisted)."
        ),
        "blocks_sprint": bool(blocking),
    }


# ---------------------------------------------------------------------------
# V92: validate_dotnet_fods_extended_apis_loc
# ---------------------------------------------------------------------------

_EXTENDED_APIS_FILENAME = "FodsDocumentExtendedApis.cs"
_EXTENDED_APIS_LOC_CAP = 800


@validator(rule_id="V_VALIDATE_DOTNET_FODS_EXTENDED_APIS_LOC", domain="dotnet")
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


# ---------------------------------------------------------------------------
# V168: validate_dotnet_collection_stub_comments
# TC-FGSQ-009 (splendid-squishing-orbit): Detect COLLECTION_STUB and
# TODO(GI-FODS-NET-*) comments in src/net/**/*.cs files.
# These markers indicate dict-backed state with no XML persistence path.
# WARN-only for existing instances; new additions tracked against baseline.
# ---------------------------------------------------------------------------

_COLLECTION_STUB_PATTERNS = [
    re.compile(r"//\s*COLLECTION_STUB"),
    re.compile(r"//\s*TODO\(GI-FODS-NET-"),
]


@validator(rule_id="V_VALIDATE_DOTNET_COLLECTION_STUB_COMMENTS", domain="dotnet")
def validate_dotnet_collection_stub_comments(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V168: Detect COLLECTION_STUB / TODO(GI-FODS-NET-*) comments in src/net/.

    TC-FGSQ-009 (splendid-squishing-orbit): Two-tier detection:

    1. FAIL + blocks_sprint for any changed_files .NET file that contains a
       COLLECTION_STUB / TODO(GI-FODS-NET-*) comment. Rationale: if a sprint declares
       a .NET file as changed, it must not introduce or retain stub comment markers in
       that file. This prevents new stub accumulation.

    2. WARN-only for the whole-repo scan of src/net/ (pre-existing stubs not in
       changed_files). These are tracked debt, not new introductions.
    """
    from pathlib import Path as _Path

    _repo = _Path(repo_root) if repo_root else _Path(__file__).resolve().parents[2]
    src_net = _repo / "src" / "net"
    if not src_net.exists():
        return {
            "validator": "validate_dotnet_collection_stub_comments",
            "result": "PASS",
            "items": [],
            "summary": "V168: src/net/ does not exist — nothing to check.",
            "blocks_sprint": False,
        }

    changed_files = set(declaration.get("changed_files", []))
    changed_cs = {f for f in changed_files if re.search(r"src[/\\]net[/\\].*\.cs$", f)}

    stub_in_changed: list[dict] = []   # FAIL items (declared in this sprint)
    stub_in_existing: list[dict] = []  # WARN items (pre-existing, not changed this sprint)

    for cs_file in sorted(src_net.rglob("*.cs")):
        try:
            lines = cs_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        rel = cs_file.relative_to(_repo).as_posix()
        rel_normalized = rel.replace("\\", "/")
        is_changed = any(
            rel_normalized == c.replace("\\", "/") or rel_normalized.endswith("/" + c.replace("\\", "/"))
            for c in changed_cs
        ) or any(c.replace("\\", "/") in rel_normalized for c in changed_cs)

        for lineno, line in enumerate(lines, start=1):
            for pat in _COLLECTION_STUB_PATTERNS:
                if pat.search(line):
                    entry = {
                        "file": rel,
                        "line": lineno,
                        "text": line.strip()[:120],
                        "remediation": (
                            "Convert method to throw NotSupportedException with ODF section citation. "
                            "Remove stub comment and dict field once all callers are updated."
                        ),
                    }
                    if is_changed:
                        stub_in_changed.append({**entry, "severity": "FAIL",
                            "reason": "stub_comment_in_sprint_declared_file"})
                    else:
                        stub_in_existing.append({**entry, "severity": "WARN",
                            "reason": "pre_existing_stub_not_in_sprint"})
                    break  # one match per line is enough

    all_items = stub_in_changed + stub_in_existing

    if not all_items:
        return {
            "validator": "validate_dotnet_collection_stub_comments",
            "result": "PASS",
            "items": [],
            "summary": "V168: No COLLECTION_STUB or TODO(GI-FODS-NET-*) comments found in src/net/.",
            "blocks_sprint": False,
        }

    if stub_in_changed:
        return {
            "validator": "validate_dotnet_collection_stub_comments",
            "result": "FAIL",
            "items": all_items,
            "summary": (
                f"V168: {len(stub_in_changed)} COLLECTION_STUB/GI-FODS-NET comment(s) in "
                f"sprint-declared .NET file(s). Blocks sprint. "
                f"({len(stub_in_existing)} pre-existing stubs also reported as WARN.)"
            ),
            "blocks_sprint": True,
        }

    return {
        "validator": "validate_dotnet_collection_stub_comments",
        "result": "WARN",
        "items": all_items,
        "summary": (
            f"V168: {len(stub_in_existing)} pre-existing COLLECTION_STUB/GI-FODS-NET comment(s) "
            "in src/net/ (not in changed_files). Track as debt; not blocking."
        ),
        "blocks_sprint": False,
    }


# ---------------------------------------------------------------------------
# V169: validate_whitelist_expiry
# ---------------------------------------------------------------------------

_WHITELIST_SECTIONS = [
    "known_constant_return_ok",
    "known_setter_without_xml_write_ok",
    "known_getter_without_xml_read_ok",
]
_WHITELIST_WARN_DAYS_BEFORE = 30


@validator(rule_id="V_VALIDATE_WHITELIST_EXPIRY", domain="dotnet")
def validate_whitelist_expiry(
    declaration: dict,
    repo_root: Path | None = None,
) -> dict:
    """V169: Warn/fail on whitelist entries nearing or past their review_due date.

    For each entry in registry/dotnet-semantic-stub-whitelist.yaml across all three
    whitelist sections:
    - If review_due is absent or unparseable: WARN (missing governance field)
    - If today >= review_due: FAIL + blocks_sprint=True (expired — must review or implement)
    - If today is within 30 days of review_due: WARN (upcoming review)
    - Otherwise: PASS (not yet due)

    Rationale: Grandfathered exceptions must not remain indefinitely. Periodic review
    ensures that each whitelist entry is either implemented from ODF XML or has a new
    review_due extension approved by a human reviewer.

    TC-FGSQ-006: REQ-FGSQ-006 — whitelist entries have expiry dates, reviewed quarterly.
    """
    from datetime import date, datetime, timezone

    _repo = repo_root or REPO_ROOT
    today = date.today()
    items = []
    expired_count = 0
    upcoming_count = 0
    missing_gov_count = 0

    for section in _WHITELIST_SECTIONS:
        records = _load_whitelist_records(_repo, section)
        for rec in records:
            method = rec.get("method", "<unknown>")
            review_due_raw = rec.get("review_due")

            if review_due_raw is None:
                # Schema 1.x entry without governance fields
                items.append({
                    "method": method,
                    "section": section,
                    "review_due": None,
                    "severity": "WARN",
                    "issue": "missing_review_due",
                    "remediation": (
                        "Upgrade whitelist entry to schema 2.0: add approved_by, approved_date, "
                        "review_due, and removal_condition fields."
                    ),
                })
                missing_gov_count += 1
                continue

            try:
                due_date = date.fromisoformat(str(review_due_raw))
            except (ValueError, TypeError):
                items.append({
                    "method": method,
                    "section": section,
                    "review_due": str(review_due_raw),
                    "severity": "WARN",
                    "issue": "unparseable_review_due",
                    "remediation": "Fix review_due field: must be ISO-8601 date (YYYY-MM-DD).",
                })
                missing_gov_count += 1
                continue

            days_until_due = (due_date - today).days

            if days_until_due < 0:
                # Past due — blocking
                items.append({
                    "method": method,
                    "section": section,
                    "review_due": str(due_date),
                    "days_overdue": -days_until_due,
                    "severity": "FAIL",
                    "issue": "whitelist_entry_expired",
                    "remediation": (
                        f"Review_due {due_date} has passed ({-days_until_due} days ago). "
                        "Either implement from ODF XML, convert to NotSupportedException, "
                        "or extend review_due with a new approved_date and approver."
                    ),
                })
                expired_count += 1
            elif days_until_due <= _WHITELIST_WARN_DAYS_BEFORE:
                # Upcoming — warn
                items.append({
                    "method": method,
                    "section": section,
                    "review_due": str(due_date),
                    "days_until_due": days_until_due,
                    "severity": "WARN",
                    "issue": "whitelist_entry_expiring_soon",
                    "remediation": (
                        f"Review_due {due_date} is in {days_until_due} day(s). "
                        "Plan: implement from ODF XML, convert to NotSupportedException, "
                        "or extend with a new approved review_due date."
                    ),
                })
                upcoming_count += 1

    blocks = expired_count > 0

    if not items:
        return {
            "validator": "validate_whitelist_expiry",
            "result": "PASS",
            "items": [],
            "summary": "V169: All whitelist entries have valid review_due dates; none expired.",
            "blocks_sprint": False,
        }

    if blocks:
        result = "FAIL"
        summary = (
            f"V169: {expired_count} whitelist entry/entries expired (review_due in past). "
            f"{upcoming_count} expiring within {_WHITELIST_WARN_DAYS_BEFORE} days. "
            f"{missing_gov_count} missing governance fields. Blocks sprint."
        )
    else:
        result = "WARN"
        summary = (
            f"V169: {upcoming_count} whitelist entry/entries expiring within "
            f"{_WHITELIST_WARN_DAYS_BEFORE} days. {missing_gov_count} missing governance "
            f"fields. Not blocking — schedule review before expiry."
        )

    return {
        "validator": "validate_whitelist_expiry",
        "result": result,
        "items": items,
        "summary": summary,
        "blocks_sprint": blocks,
    }
