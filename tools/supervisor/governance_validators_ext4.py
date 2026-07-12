"""governance_validators_ext4.py — V111-V127: Architecture QName Validators (TC-ARC-012)

Added 2026-07-04 as part of ARC-QNAME-001 architecture governance program.

V111: public_symbol_without_qname_authority
    Block Python spec/ or .NET Model/ classes missing spec_qname ClassVar / SpecQName.

V112: model_type_without_spec_authority
    Block model classes in Model/ or spec/ without spec_qname / SpecQName constant.

V113: nested_concept_on_root_document
    Block root document classes (FodsDocument, CsvDocument, etc.) owning nested-QName methods.

V114: getter_without_parser_obligation
    Block getters in fods-public-api-to-qname-map.yaml without parser_path.

V115: setter_without_writer_obligation
    Block setters in fods-public-api-to-qname-map.yaml without writer_path.

V116: detached_persistent_dict_on_model
    Block model classes with private Dictionary<>/_dict persistent state.

V117: dumping_ground_or_catchall_file
    Block product source files with catch-all naming (MissingMethods, ExtendedApis, etc.).

V118: sprint_history_identifier_in_source
    Warn when sprint/wave/train history IDs appear in production .cs/.py source.

V119: promoted_code_changed_without_reopening
    Block modifications to files at PROMOTED_STABLE or CERTIFIED level without REOPENED status.

V120: certification_without_architecture_proof
    Block CERTIFIED products that are not COMPLIANT in product-architecture-audit.yaml.

V121: missing_public_documentation
    Block public Python functions in product source without docstrings.

V122: broken_traceability_chain
    Block public symbols in fods-public-api-to-qname-map.yaml missing spec_fact_ids[].

V123: ungoverned_code_marker
    Warn for TODO/FIXME/HACK in product source without GAP-* or TC-* reference.

V124: semantic_stub_constant_return
    Block .cs/.py methods whose sole body is a constant-return stub.

V125: new_product_bypassing_architecture_gate
    Block new format directories in src/ without entry in qname-code-organization-plan.yaml.

V126: file_outside_approved_qname_layout
    Block source files placed outside approved subdirs in qname-code-organization-plan.yaml.

V127: type_outside_approved_qname_hierarchy
    Warn for class names in spec/Model source not derivable from any QName in hierarchy.
"""

from __future__ import annotations
from governance_validators_contract import validator  # noqa: F401

import ast
import re
from pathlib import Path

# ── Constants ─────────────────────────────────────────────────────────────────

_ROOT_DOC_TYPES = {
    "FodsDocument", "FodtDocument", "CsvDocument", "TsvDocument",
    "NdjsonDocument", "HtmlDocument", "MarkdownDocument", "Document",
}
_NESTED_VOCAB = re.compile(
    r"\b(GetCell|SetCell|GetRow|SetRow|GetColumn|SetColumn|GetSheet|SetSheet"
    r"|GetParagraph|SetParagraph|GetRun|SetRun|MergeCell|SortRow|InsertRow"
    r"|DeleteRow|DeleteColumn|InsertColumn|GetCellValue|SetCellValue"
    r"|GetColumnHeaders|ClearSheet)\b",
    re.IGNORECASE,
)
_SPRINT_HISTORY = re.compile(
    r"\b(sprint\d+|wave\d+|train\d+|R\d{3}-R\d{3})\b", re.IGNORECASE
)
_CATCHALL_STEMS = {
    "missingmethods", "extendedapis", "misc", "helpers", "extra",
    "stubs", "utils", "extensions",
}
_CONSTANT_RETURN = re.compile(
    r"^\s*return\s+(0|0L|0d|0m|null|false|true|\"\"|\[\]|new\s+\w+\[\]\s*\{?\}?)\s*;?\s*$",
    re.IGNORECASE,
)
_PYTHON_CONST_RETURN = re.compile(
    r"^\s*return\s+(0|None|False|True|\[\]|\{\}|\"\")\s*$"
)


def _result(vid: str, name: str, passed: bool, violations: list[str]) -> dict:
    return {
        "validator_id": vid,
        "validator_name": name,
        "passed": passed,
        "violations": violations,
    }


# ── V111 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_PUBLIC_SYMBOL_WITHOUT_QNAME_AUTHORITY", domain="naming")
def validate_public_symbol_without_qname_authority(source_text: str, file_path: str = "") -> dict:
    """V111: Python spec/ or .NET Model/ classes must have spec_qname / SpecQName."""
    violations: list[str] = []
    path = Path(file_path)
    is_python_spec = "spec" in path.parts or "spec/" in file_path
    is_dotnet_model = "Model" in path.parts or "Model/" in file_path

    if path.suffix == ".py" and is_python_spec:
        try:
            tree = ast.parse(source_text)
        except SyntaxError:
            return _result("V111", "public_symbol_without_qname_authority", True, [])
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                has_qname = any(
                    isinstance(stmt, ast.Assign)
                    and any(
                        (isinstance(t, ast.Name) and t.id == "spec_qname")
                        for t in stmt.targets
                    )
                    for stmt in node.body
                )
                if not has_qname:
                    violations.append(
                        f"[V111] {file_path}: class '{node.name}' in spec/ has no spec_qname ClassVar"
                    )

    elif path.suffix == ".cs" and is_dotnet_model:
        if "SpecQName" not in source_text and "spec_qname" not in source_text.lower():
            name = path.stem
            violations.append(
                f"[V111] {file_path}: .NET Model/ class '{name}' has no SpecQName constant"
            )

    return _result("V111", "public_symbol_without_qname_authority", not violations, violations)


# ── V112 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_MODEL_TYPE_WITHOUT_SPEC_AUTHORITY", domain="naming")
def validate_model_type_without_spec_authority(source_text: str, file_path: str = "") -> dict:
    """V112: Model/spec classes without spec_qname authority."""
    violations: list[str] = []
    path = Path(file_path)
    in_spec = "spec" in path.parts or "/spec/" in file_path or "\\spec\\" in file_path
    in_model = "Model" in path.parts or "/Model/" in file_path or "\\Model\\" in file_path

    if not (in_spec or in_model):
        return _result("V112", "model_type_without_spec_authority", True, [])

    if path.suffix == ".py":
        try:
            tree = ast.parse(source_text)
        except SyntaxError:
            return _result("V112", "model_type_without_spec_authority", True, [])
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                has_qname = any(
                    isinstance(stmt, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "spec_qname" for t in stmt.targets)
                    for stmt in node.body
                )
                if not has_qname:
                    violations.append(
                        f"[V112] {file_path}: class '{node.name}' in spec/Model dir missing spec_qname"
                    )
    elif path.suffix == ".cs" and in_model:
        if "SpecQName" not in source_text:
            violations.append(
                f"[V112] {file_path}: .NET Model class missing SpecQName constant"
            )

    return _result("V112", "model_type_without_spec_authority", not violations, violations)


# ── V113 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_NESTED_CONCEPT_ON_ROOT_DOCUMENT", domain="naming")
def validate_nested_concept_on_root_document(source_text: str, file_path: str = "") -> dict:
    """V113: Root document classes must not own nested-QName methods."""
    violations: list[str] = []
    path = Path(file_path)
    is_root_file = any(path.stem == t for t in _ROOT_DOC_TYPES)
    if not is_root_file:
        return _result("V113", "nested_concept_on_root_document", True, [])

    matches = _NESTED_VOCAB.findall(source_text)
    if matches:
        unique = sorted(set(matches))
        violations.append(
            f"[V113] {file_path}: root document type '{path.stem}' contains nested-QName methods: {unique}"
        )
    return _result("V113", "nested_concept_on_root_document", not violations, violations)


# ── V114 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_GETTER_WITHOUT_PARSER_OBLIGATION", domain="naming")
def validate_getter_without_parser_obligation(symbol_entry: dict) -> dict:
    """V114: Getter symbols must have parser_path defined."""
    violations: list[str] = []
    sym_type = symbol_entry.get("member_type", "")
    disposition = symbol_entry.get("disposition", "")
    if "getter" in sym_type.lower() or "property" in sym_type.lower():
        if disposition not in ("VIOLATION_WRONG_OWNER", "VIOLATION_NO_QNAME", "INTENTIONAL_UNMAPPED"):
            if not symbol_entry.get("parser_path"):
                sym_id = symbol_entry.get("symbol_id", symbol_entry.get("member_name", "?"))
                violations.append(
                    f"[V114] Symbol '{sym_id}': getter has no parser_path defined"
                )
    return _result("V114", "getter_without_parser_obligation", not violations, violations)


# ── V115 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_SETTER_WITHOUT_WRITER_OBLIGATION", domain="naming")
def validate_setter_without_writer_obligation(symbol_entry: dict) -> dict:
    """V115: Setter symbols must have writer_path defined."""
    violations: list[str] = []
    sym_type = symbol_entry.get("member_type", "")
    disposition = symbol_entry.get("disposition", "")
    if "setter" in sym_type.lower() or ("method" in sym_type.lower() and "set" in sym_type.lower()):
        if disposition not in ("VIOLATION_WRONG_OWNER", "VIOLATION_NO_QNAME", "INTENTIONAL_UNMAPPED"):
            if not symbol_entry.get("writer_path"):
                sym_id = symbol_entry.get("symbol_id", symbol_entry.get("member_name", "?"))
                violations.append(
                    f"[V115] Symbol '{sym_id}': setter has no writer_path defined"
                )
    return _result("V115", "setter_without_writer_obligation", not violations, violations)


# ── V116 ──────────────────────────────────────────────────────────────────────

_DICT_PATTERN = re.compile(
    r"(Dictionary\s*<[^>]+>\s*\w+\s*=\s*new|private\s+\w*[Dd]ict\w*\s+_\w+)",
)


@validator(rule_id="V_VALIDATE_DETACHED_PERSISTENT_DICT_ON_MODEL", domain="naming")
def validate_detached_persistent_dict_on_model(source_text: str, file_path: str = "") -> dict:
    """V116: Model classes must not use private Dictionary/dict for persistent state."""
    violations: list[str] = []
    path = Path(file_path)
    in_model = "Model" in path.parts or "/Model/" in file_path
    in_spec = "spec" in path.parts or "/spec/" in file_path
    if not (in_model or in_spec):
        return _result("V116", "detached_persistent_dict_on_model", True, [])

    matches = _DICT_PATTERN.findall(source_text)
    if matches:
        violations.append(
            f"[V116] {file_path}: model class has private dict/Dictionary persistent state: {matches[:3]}"
        )
    return _result("V116", "detached_persistent_dict_on_model", not violations, violations)


# ── V117 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_DUMPING_GROUND_OR_CATCHALL_FILE", domain="naming")
def validate_dumping_ground_or_catchall_file(file_path: str) -> dict:
    """V117: Product source files must not have catch-all naming."""
    violations: list[str] = []
    path = Path(file_path)
    stem_lower = path.stem.lower()
    if any(pattern in stem_lower for pattern in _CATCHALL_STEMS):
        violations.append(
            f"[V117] {file_path}: filename stem '{path.stem}' is a prohibited catch-all name"
        )
    return _result("V117", "dumping_ground_or_catchall_file", not violations, violations)


# ── V118 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_SPRINT_HISTORY_IDENTIFIER_IN_SOURCE", domain="naming")
def validate_sprint_history_identifier_in_source(source_text: str, file_path: str = "") -> dict:
    """V118: Production source must not embed sprint/wave/train history identifiers."""
    violations: list[str] = []
    matches = _SPRINT_HISTORY.findall(source_text)
    if matches:
        unique = sorted(set(m if isinstance(m, str) else m[0] for m in matches))
        violations.append(
            f"[V118] {file_path}: sprint-history IDs found in production source: {unique}"
        )
    return _result("V118", "sprint_history_identifier_in_source", not violations, violations)


# ── V119 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_PROMOTED_CODE_CHANGED_WITHOUT_REOPENING", domain="naming")
def validate_promoted_code_changed_without_reopening(
    modified_files: list[str],
    promotion_registry: dict,
) -> dict:
    """V119: Files at PROMOTED_STABLE or CERTIFIED must not be modified without REOPENED status."""
    violations: list[str] = []
    records = promotion_registry.get("promotion_records", [])
    # Build map: file -> promotion_level
    protected: dict[str, str] = {}
    for rec in records:
        lvl = rec.get("promotion_level", "DRAFT")
        if lvl in ("PROMOTED_STABLE", "CERTIFIED"):
            for f in rec.get("promoted_files", []):
                protected[f] = lvl

    for mf in modified_files:
        if mf in protected:
            violations.append(
                f"[V119] {mf}: modified at level {protected[mf]} without reopening record"
            )
    return _result("V119", "promoted_code_changed_without_reopening", not violations, violations)


# ── V120 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_CERTIFICATION_WITHOUT_ARCHITECTURE_PROOF", domain="naming")
def validate_certification_without_architecture_proof(
    certification_status: str,
    architecture_classification: str,
    product: str = "",
) -> dict:
    """V120: CERTIFIED products must have COMPLIANT architecture classification."""
    violations: list[str] = []
    if certification_status == "CERTIFIED" and architecture_classification != "COMPLIANT":
        violations.append(
            f"[V120] {product}: CERTIFIED but architecture classification is "
            f"'{architecture_classification}' (must be COMPLIANT)"
        )
    return _result("V120", "certification_without_architecture_proof", not violations, violations)


# ── V121 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_MISSING_PUBLIC_DOCUMENTATION", domain="naming")
def validate_missing_public_documentation(source_text: str, file_path: str = "") -> dict:
    """V121: Public Python functions/classes in product source must have docstrings."""
    violations: list[str] = []
    path = Path(file_path)
    if path.suffix != ".py":
        return _result("V121", "missing_public_documentation", True, [])

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return _result("V121", "missing_public_documentation", True, [])

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name.startswith("_"):
                continue
            if not (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                violations.append(
                    f"[V121] {file_path}:{node.lineno}: public '{node.name}' has no docstring"
                )
    return _result("V121", "missing_public_documentation", not violations, violations)


# ── V122 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_BROKEN_TRACEABILITY_CHAIN", domain="naming")
def validate_broken_traceability_chain(symbol_entry: dict) -> dict:
    """V122: Public symbols must have spec_fact_ids in the API-to-QName map."""
    violations: list[str] = []
    disposition = symbol_entry.get("disposition", "")
    if disposition in ("VIOLATION_WRONG_OWNER", "VIOLATION_NO_QNAME", "INTENTIONAL_UNMAPPED"):
        return _result("V122", "broken_traceability_chain", True, [])
    facts = symbol_entry.get("spec_fact_ids") or symbol_entry.get("spec_facts") or []
    if not facts:
        sym_id = symbol_entry.get("symbol_id", symbol_entry.get("member_name", "?"))
        violations.append(
            f"[V122] Symbol '{sym_id}': missing spec_fact_ids — traceability chain broken"
        )
    return _result("V122", "broken_traceability_chain", not violations, violations)


# ── V123 ──────────────────────────────────────────────────────────────────────

_UNGOVERNED_MARKER = re.compile(r"\b(TODO|FIXME|HACK)\b", re.IGNORECASE)
_GOVERNED_REF = re.compile(r"(GAP-[A-Z0-9-]+|TC-[A-Z]+-\d+|TC-ARC-\d+)", re.IGNORECASE)


@validator(rule_id="V_VALIDATE_UNGOVERNED_CODE_MARKER", domain="naming")
def validate_ungoverned_code_marker(source_text: str, file_path: str = "") -> dict:
    """V123: TODO/FIXME/HACK in product source must reference a GAP-* or TC-* ID."""
    violations: list[str] = []
    for lineno, line in enumerate(source_text.splitlines(), 1):
        if _UNGOVERNED_MARKER.search(line):
            # Check same line or ±1 lines for governed ref
            context_start = max(0, lineno - 2)
            lines = source_text.splitlines()
            context_end = min(len(lines), lineno + 1)
            context = "\n".join(lines[context_start:context_end])
            if not _GOVERNED_REF.search(context):
                violations.append(
                    f"[V123] {file_path}:{lineno}: ungoverned marker — no GAP-*/TC-* reference"
                )
    return _result("V123", "ungoverned_code_marker", not violations, violations)


# ── V124 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_SEMANTIC_STUB_CONSTANT_RETURN", domain="naming")
def validate_semantic_stub_constant_return(source_text: str, file_path: str = "") -> dict:
    """V124: Methods whose sole body is a constant-return stub are semantic stubs."""
    violations: list[str] = []
    path = Path(file_path)

    if path.suffix == ".cs":
        # Match methods: find `{` then check if body is only constant-return
        method_pattern = re.compile(
            r"public\s+[^\{]+\{([^\{\}]*)\}", re.DOTALL
        )
        for m in method_pattern.finditer(source_text):
            body = m.group(1).strip()
            if body and _CONSTANT_RETURN.match(body):
                # Get approximate line
                lineno = source_text[: m.start()].count("\n") + 1
                violations.append(
                    f"[V124] {file_path}:{lineno}: public method has constant-return stub body: {body!r}"
                )

    elif path.suffix == ".py":
        try:
            tree = ast.parse(source_text)
        except SyntaxError:
            return _result("V124", "semantic_stub_constant_return", True, [])
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_"):
                    continue
                # Check if body is just a return with a constant
                stmts = [s for s in node.body if not isinstance(s, ast.Expr)]
                if len(stmts) == 1 and isinstance(stmts[0], ast.Return):
                    val = stmts[0].value
                    if val is None or (isinstance(val, ast.Constant)
                                       and val.value in (0, None, False, True, "", [], {})):
                        violations.append(
                            f"[V124] {file_path}:{node.lineno}: public '{node.name}' "
                            "is a constant-return semantic stub"
                        )

    return _result("V124", "semantic_stub_constant_return", not violations, violations)


# ── V125 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_NEW_PRODUCT_BYPASSING_ARCHITECTURE_GATE", domain="naming")
def validate_new_product_bypassing_architecture_gate(
    format_id: str,
    organization_plan_entries: list[dict],
) -> dict:
    """V125: New format dirs must have an entry in qname-code-organization-plan.yaml."""
    violations: list[str] = []
    known = {
        e.get("format", "").lower()
        for e in organization_plan_entries
    }
    if format_id.lower() not in known:
        violations.append(
            f"[V125] Format '{format_id}' has no entry in qname-code-organization-plan.yaml — "
            "PRODUCT_ARCHITECTURE_READY gate not passed"
        )
    return _result("V125", "new_product_bypassing_architecture_gate", not violations, violations)


# ── V126 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_FILE_OUTSIDE_APPROVED_QNAME_LAYOUT", domain="naming")
def validate_file_outside_approved_qname_layout(
    file_path: str,
    organization_plan_entries: list[dict],
) -> dict:
    """V126: Source files must reside in approved subdirs from qname-code-organization-plan.yaml."""
    violations: list[str] = []
    path = Path(file_path)

    # Extract format from path (e.g. src/net/fods/... → fods)
    parts = list(path.parts)
    format_id = None
    for i, p in enumerate(parts):
        if p in ("net", "python") and i + 1 < len(parts):
            format_id = parts[i + 1]
            break

    if format_id is None:
        return _result("V126", "file_outside_approved_qname_layout", True, [])

    entry = next(
        (e for e in organization_plan_entries if e.get("format", "").lower() == format_id.lower()),
        None,
    )
    if entry is None:
        violations.append(
            f"[V126] {file_path}: format '{format_id}' not in qname-code-organization-plan.yaml"
        )
        return _result("V126", "file_outside_approved_qname_layout", False, violations)

    approved_subdirs: list[str] = entry.get("target_subdirs", [])
    if not approved_subdirs:
        return _result("V126", "file_outside_approved_qname_layout", True, [])

    # Build approved path fragments
    root = entry.get("root", "")
    approved = [root + s.rstrip("/") + "/" for s in approved_subdirs] + [root]
    file_str = file_path.replace("\\", "/")
    if not any(file_str.startswith(a.replace("\\", "/")) or
               "/" + a.lstrip("./").replace("\\", "/") in file_str
               for a in approved):
        violations.append(
            f"[V126] {file_path}: not in any approved QName layout subdir for '{format_id}'"
        )
    return _result("V126", "file_outside_approved_qname_layout", not violations, violations)


# ── V127 ──────────────────────────────────────────────────────────────────────

def _qname_local_to_class_tokens(qname: str) -> set[str]:
    """Extract PascalCase tokens from a QName local name (e.g. 'table-cell' → {'TableCell','Cell'})."""
    local = qname.split(":", 1)[-1]
    parts = local.split("-")
    tokens: set[str] = set()
    tokens.add("".join(p.capitalize() for p in parts))  # TableCell
    if len(parts) > 1:
        tokens.add(parts[-1].capitalize())  # Cell
    return tokens


@validator(rule_id="V_VALIDATE_TYPE_OUTSIDE_APPROVED_QNAME_HIERARCHY", domain="naming")
def validate_type_outside_approved_qname_hierarchy(
    class_name: str,
    qname_nodes: list[dict],
) -> dict:
    """V127: Spec/Model class names must be derivable from a QName in the hierarchy."""
    violations: list[str] = []
    if not qname_nodes or not class_name:
        return _result("V127", "type_outside_approved_qname_hierarchy", True, [])

    all_tokens: set[str] = set()
    for node in qname_nodes:
        qname = node.get("qname", "")
        all_tokens |= _qname_local_to_class_tokens(qname)
        # Also allow the canonical_class direct name
        cc = node.get("canonical_class", "")
        if "." in cc:
            all_tokens.add(cc.split(".")[-1])

    # Aspose-style wrappers (FodsWorksheet → Worksheet, FodsCell → Cell)
    stripped = re.sub(r"^(Fods|Fodt|Csv|Tsv|Ndjson|Ods|Fodp|Fodg)", "", class_name)

    if class_name not in all_tokens and stripped not in all_tokens:
        # Allow collection wrappers (FodsCellCollection → Cell)
        stripped_coll = re.sub(r"Collection$", "", stripped)
        if stripped_coll not in all_tokens:
            violations.append(
                f"[V127] Class '{class_name}' (stripped='{stripped}') cannot be derived from "
                "any QName in the hierarchy"
            )
    return _result("V127", "type_outside_approved_qname_hierarchy", not violations, violations)


# ── PRODUCT_ARCHITECTURE_READY gate (TC-ARC-015) ─────────────────────────────

class ArchitectureGateNotPassed(Exception):
    """Raised when a format has not passed the PRODUCT_ARCHITECTURE_READY gate."""


@validator(rule_id="V_VALIDATE_PRODUCT_ARCHITECTURE_READY", domain="naming")
def validate_product_architecture_ready(
    format_id: str,
    organization_plan_entries: list[dict],
    gap_ledger_entries: list[dict] | None = None,
    promotion_records: list[dict] | None = None,
) -> dict:
    """TC-ARC-015: Check all PRODUCT_ARCHITECTURE_READY gate criteria for a format.

    Gate checks (per plan §10):
      1. Entry exists in qname-code-organization-plan.yaml
      2. At least one gap entry exists in aspose-qname-gap-ledger (audit done)
      3. Promotion level is DRAFT or higher (architecture review started)

    Raises ArchitectureGateNotPassed if any check fails.
    """
    violations: list[str] = []

    # Check 1: in organization plan
    known_formats = {e.get("format", "").lower() for e in organization_plan_entries}
    if format_id.lower() not in known_formats:
        violations.append(
            f"Gate 1 FAIL: '{format_id}' not in qname-code-organization-plan.yaml"
        )

    # Check 2: audit has been done (gap ledger has entry for format)
    if gap_ledger_entries is not None:
        fmt_gaps = [
            g for g in gap_ledger_entries
            if format_id.lower() in g.get("format", "").lower()
            or format_id.lower() in g.get("gap_id", "").lower()
        ]
        if not fmt_gaps:
            violations.append(
                f"Gate 2 FAIL: no entries in aspose-qname-gap-ledger for '{format_id}' — audit not done"
            )

    # Check 3: promotion record exists
    if promotion_records is not None:
        fmt_promo = [
            r for r in promotion_records
            if r.get("format", "").lower() == format_id.lower()
        ]
        if not fmt_promo:
            violations.append(
                f"Gate 3 FAIL: no promotion record for '{format_id}'"
            )

    if violations:
        raise ArchitectureGateNotPassed(
            f"PRODUCT_ARCHITECTURE_READY gate NOT passed for '{format_id}': "
            + "; ".join(violations)
        )

    return _result("V125", "product_architecture_ready_gate", True, [])


# ── V128 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_DOTNET_PARSER_REQUIRED", domain="naming")
def validate_dotnet_parser_required(
    format_id: str,
    format_root_files: list[str],
) -> dict:
    """V128: .NET format must have a real parser file (not stub-only).

    Detects FULL_REBUILD_STUB gap class — formats where the .NET implementation
    consists of a single stub file with no real parser or writer.
    """
    violations: list[str] = []
    has_parser = any(
        "Parser" in f or "Reader" in f or "Decoder" in f or "Codec" in f
        for f in format_root_files
        if f.endswith(".cs")
    )
    has_writer = any(
        "Writer" in f or "Encoder" in f or "Codec" in f
        for f in format_root_files
        if f.endswith(".cs")
    )
    cs_count = sum(1 for f in format_root_files if f.endswith(".cs"))
    if cs_count <= 1:
        violations.append(
            f"[V128] Format '{format_id}' .NET has only {cs_count} .cs file(s) — "
            "stub-only implementation, no real parser/writer"
        )
    elif not has_parser:
        violations.append(
            f"[V128] Format '{format_id}' .NET has no Parser/Reader/Decoder/Codec file — "
            "FULL_REBUILD_STUB gap: parser is required"
        )
    return _result("V128", "dotnet_parser_required", not violations, violations)


# ── V129 ──────────────────────────────────────────────────────────────────────

@validator(rule_id="V_VALIDATE_COMPAT_FACADE_BEHAVIORAL", domain="naming")
def validate_compat_facade_behavioral(
    source_text: str,
    file_path: str = "",
) -> dict:
    """V129: Compat/ facade classes must be behavioral (not architecture markers).

    Detects COMPAT_NOT_BEHAVIORAL gap class — Compat/ files that declare class
    inheritance but contain only docstrings and no real method implementations.
    """
    violations: list[str] = []
    lines = source_text.splitlines()
    in_compat = "Compat" in file_path or "compat" in file_path

    if not in_compat:
        return _result("V129", "compat_facade_behavioral", True, [])

    marker_phrases = [
        "not behavioral",
        "architecture marker",
        "not yet behavioral",
        "placeholder",
        "architecture only",
        "architecture-only",
    ]
    has_marker = any(
        phrase in source_text.lower() for phrase in marker_phrases
    )

    # Count real method definitions (not just pass or ...)
    real_methods = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("def ") and not stripped.startswith("def __"):
            # Look ahead for non-trivial body
            body_lines = [l.strip() for l in lines[i + 1 : i + 6] if l.strip()]
            if body_lines and body_lines[0] not in ("pass", "...", '"""', "'''"):
                real_methods += 1

    if has_marker and real_methods == 0:
        violations.append(
            f"[V129] '{file_path}': Compat/ facade is marked 'not behavioral' and has "
            "no real method implementations — COMPAT_NOT_BEHAVIORAL gap"
        )
    elif real_methods == 0 and "class " in source_text:
        violations.append(
            f"[V129] '{file_path}': Compat/ facade has class declaration but zero "
            "real method implementations — likely architecture marker only"
        )
    return _result("V129", "compat_facade_behavioral", not violations, violations)


# ── V145 ──────────────────────────────────────────────────────────────────────


def validate_maintenance_obligations_current(
    declaration: dict,
    repo_root: "Path | None" = None,
) -> dict:
    """V145: Warn when open MOR obligations are past their scheduled_date.

    Verdict: WARNING (never GOV_BLOCK) — overdue maintenance does not block sprint work
    but must be visible so authors cannot silently ignore scheduled tasks.
    blocks_sprint: False.

    MOR path: reports/supervisor/maintenance-obligations.json
    Non-blocking: returns PASS when MOR is absent or import fails.
    """
    from pathlib import Path as _Path
    from datetime import date as _date

    _repo = _Path(repo_root) if repo_root is not None else _Path(__file__).resolve().parent.parent.parent
    mor_path = _repo / "reports" / "supervisor" / "maintenance-obligations.json"

    if not mor_path.exists():
        return {
            "validator": "validate_maintenance_obligations_current",
            "result": "PASS",
            "detail": "MOR absent — no obligations to check",
            "blocks_sprint": False,
        }

    try:
        import json as _json
        mor = _json.loads(mor_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "validator": "validate_maintenance_obligations_current",
            "result": "PASS",
            "detail": f"MOR unreadable (skip): {exc}",
            "blocks_sprint": False,
        }

    today = _date.today()
    overdue: list[str] = []
    for o in mor.get("obligations", []):
        if o.get("status") != "open":
            continue
        sched = o.get("scheduled_date")
        if sched is None:
            continue
        try:
            d = _date.fromisoformat(str(sched))
            if d < today:
                overdue.append(
                    f"[V145] Obligation {o['obligation_id']!r} is overdue "
                    f"(scheduled {sched}, today {today}): {o.get('action', '')[:60]}"
                )
        except ValueError:
            pass  # Unparseable date — skip

    if not overdue:
        return {
            "validator": "validate_maintenance_obligations_current",
            "result": "PASS",
            "detail": "All open obligations are within schedule",
            "blocks_sprint": False,
        }

    # WARN only — overdue maintenance is advisory, never a sprint blocker.
    return {
        "validator": "validate_maintenance_obligations_current",
        "result": "WARN",
        "detail": f"{len(overdue)} overdue obligation(s)",
        "violations": overdue,
        "blocks_sprint": False,
    }


# ---------------------------------------------------------------------------
# V149: validate_source_stubs — stub enforcement via no_stub_scan.py
# ---------------------------------------------------------------------------


def validate_source_stubs(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V149: Block sprints introducing forbidden stub patterns in product source.

    Delegates to tools/review/no_stub_scan.py which detects:
    - Forbidden terms: TODO, FIXME, stub, placeholder, NotImplemented,
      dummy, temporary, TBD (case-insensitive, with ODF XML allowlist)
    - Pass-only method/class bodies (without authority_only=True marker)

    The scanner's own allowlist handles known exceptions (ODF XML element
    names like text:placeholder, anti-stub documentation, GAP-governed
    positional placeholders).

    blocks_sprint=True only when PRODUCT_SOURCE/RELEASE_GATE items exist
    AND violations survive the scanner's allowlist.

    Implemented: TC-PFF-R1 (parallel-foraging-fairy, 2026-07-09).
    """
    import sys as _sys

    repo = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent.parent.parent
    _sys.path.insert(0, str(repo / "tools" / "review"))
    try:
        from no_stub_scan import report as _stub_report  # type: ignore[import-untyped]
    except ImportError:
        return {
            "validator": "validate_source_stubs",
            "result": "PASS",
            "summary": "V149: no_stub_scan unavailable (skipped)",
            "blocks_sprint": False,
        }

    scan_root = repo / "src" / "python"
    if not scan_root.exists():
        return {
            "validator": "validate_source_stubs",
            "result": "PASS",
            "summary": "V149: src/python not found",
            "blocks_sprint": False,
        }

    result = _stub_report([scan_root])
    violations = result.get("violations", [])

    has_product = any(
        i.get("work_item_type") in ("PRODUCT_SOURCE", "RELEASE_GATE")
        for i in declaration.get("planned_work_items", [])
    )

    if not violations:
        return {
            "validator": "validate_source_stubs",
            "result": "PASS",
            "summary": "V149: No stub violations in src/python",
            "blocks_sprint": False,
        }

    # TC-SC-005: Pre-existing violations resolved (PFF-CLEANUP-002).
    # V149 now blocks sprints with PRODUCT_SOURCE/RELEASE_GATE items.
    return {
        "validator": "validate_source_stubs",
        "result": "FAIL" if has_product else "WARN",
        "summary": (
            f"V149: {len(violations)} stub violation(s) in src/python. "
            f"First: {violations[0]['file']}:{violations[0]['line']}"
        ),
        "items": violations[:10],
        "blocks_sprint": has_product,
    }


def validate_lane_contract_exists(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V171: Validate sprint declaration references a valid lane_id from lane-contracts.yaml.

    - If .governance/lanes/lane-contracts.yaml does not exist: WARN (non-blocking).
    - If lane_id not present in declaration: PASS (lane_id is optional).
    - If lane_id present but not in registry: FAIL + blocks_sprint=True.
    - If lane_id present and valid: PASS.

    Implements: TC-GFB-021 (FF-MR-2026-001). Fixes: GAP-LANE-CONTRACTS-MISSING.
    """
    import yaml as _yaml

    repo = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parent.parent.parent
    contracts_path = repo / ".governance" / "lanes" / "lane-contracts.yaml"

    if not contracts_path.exists():
        return {
            "validator": "validate_lane_contract_exists",
            "result": "WARN",
            "summary": "V171: .governance/lanes/lane-contracts.yaml not found — lane governance not yet active",
            "blocks_sprint": False,
        }

    try:
        data = _yaml.safe_load(contracts_path.read_text(encoding="utf-8"))
        valid_lane_ids = {lane["lane_id"] for lane in data.get("lanes", [])}
    except Exception as exc:
        return {
            "validator": "validate_lane_contract_exists",
            "result": "WARN",
            "summary": f"V171: Could not parse lane-contracts.yaml: {exc}",
            "blocks_sprint": False,
        }

    declared_lane_id = declaration.get("lane_id")
    if not declared_lane_id:
        return {
            "validator": "validate_lane_contract_exists",
            "result": "PASS",
            "summary": "V171: No lane_id declared — lane governance skipped",
            "blocks_sprint": False,
        }

    if declared_lane_id in valid_lane_ids:
        return {
            "validator": "validate_lane_contract_exists",
            "result": "PASS",
            "summary": f"V171: lane_id={declared_lane_id!r} is a valid registered lane",
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_lane_contract_exists",
        "result": "FAIL",
        "summary": (
            f"V171: lane_id={declared_lane_id!r} is not registered in "
            f".governance/lanes/lane-contracts.yaml. "
            f"Valid lane IDs: {sorted(valid_lane_ids)}"
        ),
        "blocks_sprint": True,
    }


# ---------------------------------------------------------------------------
# V172-V175: V_MACH_* Lifecycle Iteration Validators (TC-VWR-007)
# Require behavioral iteration proof for machinery_hardening plans.
# ---------------------------------------------------------------------------


def validate_mach_audit_after_exec(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V172: V_MACH_AUDIT_AFTER_EXEC — machinery sprints must declare lifecycle_audit was run.

    For declarations with plan_type=machinery_hardening: the sprint declaration must
    include 'lifecycle_audit_run: true' OR evidence_paths must reference lifecycle_audit output.
    WARN-only (non-blocking) so it doesn't break existing pipelines.
    Implements: TC-VWR-007 (velvet-swinging-wreath).
    """
    plan_type = declaration.get("plan_type") or ""
    if plan_type != "machinery_hardening":
        return {
            "validator": "validate_mach_audit_after_exec",
            "result": "PASS",
            "summary": "V172: plan_type is not machinery_hardening — skipped",
            "blocks_sprint": False,
        }
    lifecycle_run = declaration.get("lifecycle_audit_run")
    evidence = [str(p) for p in (declaration.get("evidence_paths") or [])]
    audit_evidence = any("lifecycle-audit-results" in e or "lifecycle_audit" in e for e in evidence)
    if lifecycle_run or audit_evidence:
        return {
            "validator": "validate_mach_audit_after_exec",
            "result": "PASS",
            "summary": "V172: machinery sprint has lifecycle audit evidence",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_mach_audit_after_exec",
        "result": "WARN",
        "summary": (
            "V172: machinery_hardening sprint does not declare lifecycle_audit_run=true "
            "or reference lifecycle audit output. "
            "Set lifecycle_audit_run: true in declaration or add .local/supervisor/lifecycle-audit-results.json "
            "to evidence_paths."
        ),
        "blocks_sprint": False,
    }


def validate_mach_iteration_proof(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V173: V_MACH_ITERATION_PROOF — machinery mission must have behavioral iteration count > 0.

    Reads .local/supervisor/machinery/mission-ledger.json and checks
    current_behavioral_iterations > 0 for the declared mission_id.
    WARN-only (non-blocking).
    Implements: TC-VWR-007 (velvet-swinging-wreath).
    """
    import json as _json  # noqa: PLC0415

    plan_type = declaration.get("plan_type") or ""
    if plan_type != "machinery_hardening":
        return {
            "validator": "validate_mach_iteration_proof",
            "result": "PASS",
            "summary": "V173: plan_type is not machinery_hardening — skipped",
            "blocks_sprint": False,
        }
    _repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    ledger_path = _repo / ".local" / "supervisor" / "machinery" / "mission-ledger.json"
    if not ledger_path.exists():
        return {
            "validator": "validate_mach_iteration_proof",
            "result": "WARN",
            "summary": "V173: mission-ledger.json absent — behavioral iteration not tracked yet",
            "blocks_sprint": False,
        }
    try:
        ledger = _json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "validator": "validate_mach_iteration_proof",
            "result": "WARN",
            "summary": "V173: mission-ledger.json unreadable",
            "blocks_sprint": False,
        }
    current_iter = ledger.get("current_behavioral_iterations", 0)
    if current_iter > 0:
        return {
            "validator": "validate_mach_iteration_proof",
            "result": "PASS",
            "summary": f"V173: behavioral_iterations={current_iter} > 0 — iteration proof present",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_mach_iteration_proof",
        "result": "WARN",
        "summary": (
            f"V173: machinery mission has current_behavioral_iterations=0. "
            "At least 1 audit-execute-reaudit cycle must complete before TERMINAL_CLOSED. "
            "Run lifecycle_audit.py with plan_type=machinery_hardening to increment counter."
        ),
        "blocks_sprint": False,
    }


def validate_mach_continuation_consumed(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V174: V_MACH_CONTINUATION_CONSUMED — machinery sprint signal must show consumed state.

    For machinery_hardening declarations: checks that the machinery continuation signal
    (if present) shows autonomous_continue=true or was freshly generated after execution.
    WARN-only (non-blocking).
    Implements: TC-VWR-007 (velvet-swinging-wreath).
    """
    import json as _json  # noqa: PLC0415

    plan_type = declaration.get("plan_type") or ""
    if plan_type != "machinery_hardening":
        return {
            "validator": "validate_mach_continuation_consumed",
            "result": "PASS",
            "summary": "V174: plan_type is not machinery_hardening — skipped",
            "blocks_sprint": False,
        }
    _repo = Path(repo_root) if repo_root else Path(__file__).resolve().parent.parent.parent
    signal_path = _repo / ".local" / "supervisor" / "machinery" / "continuation-signal.json"
    if not signal_path.exists():
        return {
            "validator": "validate_mach_continuation_consumed",
            "result": "WARN",
            "summary": "V174: machinery continuation-signal.json absent",
            "blocks_sprint": False,
        }
    try:
        sig = _json.loads(signal_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "validator": "validate_mach_continuation_consumed",
            "result": "WARN",
            "summary": "V174: machinery continuation-signal.json unreadable",
            "blocks_sprint": False,
        }
    if sig.get("autonomous_continue"):
        return {
            "validator": "validate_mach_continuation_consumed",
            "result": "PASS",
            "summary": "V174: machinery continuation signal shows autonomous_continue=true",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_mach_continuation_consumed",
        "result": "WARN",
        "summary": (
            "V174: machinery continuation signal shows autonomous_continue=false. "
            "Machinery sprint may not have been authorized by the lifecycle machinery."
        ),
        "blocks_sprint": False,
    }


def validate_mach_task_vs_mission(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V175: V_MACH_TASK_VS_MISSION — machinery taskcards must reference active mission.

    For machinery_hardening declarations: each planned_work_item must include a mission_ref
    or the declaration must declare mission_id.
    WARN-only (non-blocking).
    Implements: TC-VWR-007 (velvet-swinging-wreath).
    """
    plan_type = declaration.get("plan_type") or ""
    if plan_type != "machinery_hardening":
        return {
            "validator": "validate_mach_task_vs_mission",
            "result": "PASS",
            "summary": "V175: plan_type is not machinery_hardening — skipped",
            "blocks_sprint": False,
        }
    mission_id = declaration.get("mission_id") or declaration.get("sprint_id") or ""
    if mission_id:
        return {
            "validator": "validate_mach_task_vs_mission",
            "result": "PASS",
            "summary": f"V175: mission_id={mission_id!r} declared in machinery sprint",
            "blocks_sprint": False,
        }
    return {
        "validator": "validate_mach_task_vs_mission",
        "result": "WARN",
        "summary": (
            "V175: machinery_hardening sprint does not declare mission_id. "
            "Add mission_id: <MISSION_ID> to the declaration for traceability."
        ),
        "blocks_sprint": False,
    }


@validator(rule_id="V182", domain="gap_lifecycle")
def validate_no_open_implementation_verified_gaps(
    declaration: dict, repo_root: "Path | None" = None
) -> dict:
    """V182 (TC-BOOL-004): WARN if any gaps have status=open AND current_state=implementation_verified.

    These gaps are excluded from work item selection (_SKIP_STATUSES) and excluded from
    the declared-sprint closure path (no work item → no gap_ledger_ref → no closure).
    They are invisible to both pipelines — permanent limbo.

    WARN only (not BLOCK): use close_implementation_verified_gaps() to resolve.
    """
    import json
    _r = repo_root or Path(__file__).parent.parent.parent
    ledger_path = _r / "reports" / "capability-layer" / "gap-ledger.json"
    if not ledger_path.exists():
        ledger_path = _r / "reports" / "capability-layer" / "gap-ledger-active.json"
    if not ledger_path.exists():
        return {
            "validator": "validate_no_open_implementation_verified_gaps",
            "result": "PASS",
            "summary": "V182: gap-ledger.json not found — skipping",
            "blocks_sprint": False,
            "items": [],
        }
    try:
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "validator": "validate_no_open_implementation_verified_gaps",
            "result": "PASS",
            "summary": "V182: gap-ledger.json unreadable — skipping",
            "blocks_sprint": False,
            "items": [],
        }
    limbo_gaps = [
        g.get("gap_id", "(no id)")
        for g in ledger.get("gaps", [])
        if g.get("status") == "open" and g.get("current_state") == "implementation_verified"
    ]
    if not limbo_gaps:
        return {
            "validator": "validate_no_open_implementation_verified_gaps",
            "result": "PASS",
            "summary": "V182: No open+implementation_verified limbo gaps found.",
            "blocks_sprint": False,
            "items": [],
        }
    return {
        "validator": "validate_no_open_implementation_verified_gaps",
        "result": "WARN",
        "summary": (
            f"V182: {len(limbo_gaps)} gap(s) have status=open AND "
            "current_state=implementation_verified — excluded from both work selection "
            "and closure pipeline. Run close_implementation_verified_gaps() to resolve."
        ),
        "blocks_sprint": False,
        "items": limbo_gaps,
    }
