"""
TC-ACP-014-02 — Agent bundle completeness tests (FF-AGENTS-PARITY-001)

Verifies codex-bundle.yaml and kilo-bundle.yaml exist, are valid YAML,
and contain the required structural fields.
"""
import pathlib
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
BUNDLES_DIR = REPO / "docs" / "agents" / "bundles"
REGISTRY = REPO / ".governance" / "capabilities" / "registry.yaml"


def _load_bundle(agent: str) -> dict:
    path = BUNDLES_DIR / f"{agent}-bundle.yaml"
    assert path.exists(), f"{agent}-bundle.yaml missing at {path}"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_codex_bundle_exists_and_valid():
    """codex-bundle.yaml exists, parses as YAML, and has required bundle fields."""
    d = _load_bundle("codex")
    bundle = d.get("bundle", {})
    assert bundle.get("agent") == "codex", "bundle.agent must be 'codex'"
    assert "capabilities" in bundle, "bundle.capabilities missing"
    assert "governance" in bundle, "bundle.governance missing"
    assert "blocked_capabilities" in bundle, "bundle.blocked_capabilities missing"


def test_kilo_bundle_exists_and_valid():
    """kilo-bundle.yaml exists, parses as YAML, and has required bundle fields."""
    d = _load_bundle("kilo")
    bundle = d.get("bundle", {})
    assert bundle.get("agent") == "kilo", "bundle.agent must be 'kilo'"
    assert "capabilities" in bundle, "bundle.capabilities missing"
    assert "governance" in bundle, "bundle.governance missing"
    assert "blocked_capabilities" in bundle, "bundle.blocked_capabilities missing"


def test_bundle_references_registry_source():
    """Verify bundles reference .governance/capabilities/registry.yaml as source."""
    for agent in ("codex", "kilo"):
        d = _load_bundle(agent)
        bundle = d.get("bundle", {})
        source = bundle.get("source", {})
        # source may be a dict (key->path) or a string; accept either form
        if isinstance(source, dict):
            source_str = " ".join(str(v) for v in source.values())
        else:
            source_str = str(source)
        assert "registry.yaml" in source_str, (
            f"{agent}-bundle.yaml bundle.source does not reference registry.yaml: {source!r}"
        )
