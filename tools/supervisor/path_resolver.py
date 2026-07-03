"""Canonical product path resolver.

Loads registry/repository-layout.yaml and resolves product source paths
deterministically. Never derives paths from language-id names by assumption
(e.g. src/{language_id}/).

Usage:
    from tools.supervisor.path_resolver import resolve_product_path

    # .NET FODS product
    path = resolve_product_path("dotnet", "fods")
    # -> PosixPath('/repo/src/net/fods')

    # Alias 'net' also works
    path = resolve_product_path("net", "fods")

    # Python product
    path = resolve_product_path("python", "fods")
    # -> PosixPath('/repo/src/python/fods')

    # Validate the directory exists on disk
    path = resolve_product_path("dotnet", "fods", validate_exists=True)

Authority: registry/repository-layout.yaml
"""
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_LAYOUT_FILE = _REPO_ROOT / "registry" / "repository-layout.yaml"


def load_layout(repo_root: "Path | None" = None) -> dict:
    """Load the repository layout authority YAML."""
    layout_path = (
        Path(repo_root) / "registry" / "repository-layout.yaml"
        if repo_root
        else _LAYOUT_FILE
    )
    with open(layout_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_product_path(
    language_id: str,
    format_id: str,
    repo_root: "Path | None" = None,
    validate_exists: bool = False,
) -> Path:
    """Resolve canonical physical path for a product.

    Args:
        language_id: Logical language ID — "dotnet", "python", or alias "net".
        format_id: Format identifier, e.g. "fods", "csv", "html".
        repo_root: Override for repository root (auto-detected by default).
        validate_exists: If True, raise FileNotFoundError when path is absent.

    Returns:
        Absolute resolved Path.

    Raises:
        KeyError: language_id has no mapping in the layout authority.
        ValueError: Resolved path matches a prohibited pattern.
        FileNotFoundError: Path absent on disk (only when validate_exists=True).
    """
    layout = load_layout(repo_root)
    root = Path(repo_root) if repo_root else _REPO_ROOT

    normalized = language_id.lower()
    entry = None
    for key, value in layout.get("source_roots", {}).items():
        if normalized in ([key] + value.get("aliases", [])):
            entry = value
            break

    if entry is None:
        available = list(layout.get("source_roots", {}).keys())
        raise KeyError(
            f"No layout mapping for language_id={language_id!r}. "
            f"Available: {available}. "
            f"Authority: registry/repository-layout.yaml"
        )

    relative = entry["product_path_pattern"].format(format=format_id)

    for prohibited in layout.get("prohibited_paths", []):
        if relative.startswith(prohibited):
            raise ValueError(
                f"Resolved path {relative!r} matches prohibited pattern {prohibited!r}. "
                f"Use language_id='dotnet' to resolve to src/net/, not src/dotnet/. "
                f"Authority: registry/repository-layout.yaml"
            )

    resolved = root / relative

    if validate_exists and not resolved.exists():
        raise FileNotFoundError(
            f"Product path does not exist: {resolved}. "
            f"Authority: registry/repository-layout.yaml"
        )

    return resolved


def get_prohibited_paths(repo_root: "Path | None" = None) -> list:
    """Return list of prohibited paths from the layout authority."""
    layout = load_layout(repo_root)
    return list(layout.get("prohibited_paths", []))


def get_source_root(language_id: str, repo_root: "Path | None" = None) -> Path:
    """Return the absolute source root for a language ID.

    Examples:
        get_source_root("dotnet")  -> .../src/net
        get_source_root("python")  -> .../src/python
        get_source_root("net")     -> .../src/net  (alias)
    """
    layout = load_layout(repo_root)
    root = Path(repo_root) if repo_root else _REPO_ROOT

    normalized = language_id.lower()
    for key, value in layout.get("source_roots", {}).items():
        if normalized in ([key] + value.get("aliases", [])):
            return root / value["path"]

    available = list(layout.get("source_roots", {}).keys())
    raise KeyError(
        f"No source root for language_id={language_id!r}. "
        f"Available: {available}. "
        f"Authority: registry/repository-layout.yaml"
    )


if __name__ == "__main__":
    import sys

    # Quick smoke-test
    print("=== path_resolver smoke test ===")
    for lang, fmt, expect_suffix in [
        ("dotnet", "fods", "src/net/fods"),
        ("net", "fods", "src/net/fods"),       # alias
        ("dotnet", "csv", "src/net/csv"),
        ("python", "fods", "src/python/fods"),
    ]:
        result = resolve_product_path(lang, fmt)
        ok = str(result).replace("\\", "/").endswith(expect_suffix)
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] resolve_product_path({lang!r}, {fmt!r}) -> {result}")

    # Prohibited path test
    try:
        resolve_product_path("dotnet", "fods")  # should succeed
        print("  [PASS] dotnet resolves (not to src/dotnet)")
    except ValueError as e:
        print(f"  [FAIL] unexpected error: {e}", file=sys.stderr)

    print("=== done ===")
