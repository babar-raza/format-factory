"""
R71 Train D — test_r71_delivery_manifest_separates_sidecar_file_and_bundle_sha.py
Verify that the delivery manifest clearly separates:
  - evidence_zip_sha256: SHA of the inner evidence ZIP
  - sidecar_sha256: SHA of the .sha256-proof.json sidecar FILE (not the inner ZIP)

These two values MUST be different. If they are equal, it means the manifest
was incorrectly populated (R70 IV-R70-001 defect pattern).

The R71 proof model requires:
  Layer 1: Inner ZIP owns source+reports+inner validation
  Layer 2: Sidecar owns inner ZIP SHA
  Layer 3: Delivery manifest owns sidecar file SHA + inner ZIP SHA
  Layer 4: Outer delivery package SHA = external/final, NOT inside inner ZIP
"""

import hashlib
import io
import json
import os
import pathlib
import zipfile
import pytest

LOCAL = pathlib.Path(".local")


def _get_delivery_package() -> tuple:
    """
    Returns (outer_zip_path, source) where source is 'env' or 'local'.
    Returns (None, None) if no package is available.
    Raises pytest.fail if env var is set but file not found.
    """
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        p = pathlib.Path(env_path)
        if not p.exists():
            pytest.fail(
                f"DELIVERY_PACKAGE_UNDER_TEST={env_path} but file not found. "
                "Delivery-mode tests cannot run without the delivery package."
            )
        return p, "env"

    for name in ["r71-delivery-package.zip", "r70-delivery-package.zip"]:
        p = LOCAL / name
        if p.exists():
            return p, "local"

    return None, None


def _get_sprint_name() -> str:
    """Get sprint name from env or detect from available files."""
    env_path = os.environ.get("DELIVERY_PACKAGE_UNDER_TEST", "")
    if env_path:
        name = pathlib.Path(env_path).name
        return name.split("-delivery-package")[0]
    for name in ["r71", "r70"]:
        if (LOCAL / f"{name}-delivery-package.zip").exists():
            return name
    return "unknown"


def test_manifest_has_both_sha_fields():
    """Delivery manifest must have both evidence_zip_sha256 and sidecar_sha256."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        manifest = json.loads(outer.read(manifest_name))

    assert "evidence_zip_sha256" in manifest, (
        "Delivery manifest missing 'evidence_zip_sha256'. "
        "This field must contain the SHA of the inner evidence ZIP file."
    )
    assert "sidecar_sha256" in manifest, (
        "Delivery manifest missing 'sidecar_sha256'. "
        "This field must contain the SHA of the .sha256-proof.json sidecar FILE."
    )


def test_manifest_sidecar_sha_differs_from_evidence_sha():
    """sidecar_sha256 and evidence_zip_sha256 must be different values.
    They are SHAs of different files; equal values indicate R70-IV-001 defect pattern."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        manifest = json.loads(outer.read(manifest_name))

    evidence_sha = manifest.get("evidence_zip_sha256", "")
    sidecar_sha = manifest.get("sidecar_sha256", "")

    assert evidence_sha, "evidence_zip_sha256 must not be empty"
    assert sidecar_sha, "sidecar_sha256 must not be empty"
    assert evidence_sha != sidecar_sha, (
        f"manifest sidecar_sha256 == evidence_zip_sha256 == {evidence_sha[:16]}...\n"
        "These are SHAs of different files (inner ZIP vs sidecar JSON) and MUST differ.\n"
        "This is the R70 IV-R70-001 defect pattern: sidecar_sha256 was set to inner ZIP SHA."
    )


def test_sidecar_sha_matches_actual_sidecar_file():
    """manifest.sidecar_sha256 must match the actual SHA of the sidecar file in the package."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert sidecar_name is not None, f"No sidecar file found. Contents: {names}"
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        sidecar_bytes = outer.read(sidecar_name)
        manifest = json.loads(outer.read(manifest_name))

    actual_sidecar_sha = hashlib.sha256(sidecar_bytes).hexdigest()
    recorded_sidecar_sha = manifest.get("sidecar_sha256", "")

    assert recorded_sidecar_sha == actual_sidecar_sha, (
        f"manifest.sidecar_sha256={recorded_sidecar_sha[:16]}... does not match "
        f"actual sidecar file SHA={actual_sidecar_sha[:16]}...\n"
        "The sidecar_sha256 field must be the SHA of the sidecar JSON file, "
        "not the SHA of the inner evidence ZIP."
    )


def test_evidence_sha_matches_actual_inner_zip():
    """manifest.evidence_zip_sha256 must match the actual SHA of the inner ZIP."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert inner_name is not None, f"No inner ZIP found. Contents: {names}"
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        inner_bytes = outer.read(inner_name)
        manifest = json.loads(outer.read(manifest_name))

    actual_inner_sha = hashlib.sha256(inner_bytes).hexdigest()
    recorded_inner_sha = manifest.get("evidence_zip_sha256", "")

    assert recorded_inner_sha == actual_inner_sha, (
        f"manifest.evidence_zip_sha256={recorded_inner_sha[:16]}... does not match "
        f"actual inner ZIP SHA={actual_inner_sha[:16]}..."
    )


def test_sidecar_claims_inner_zip_sha_matches_manifest():
    """Sidecar file's sha256 field must match manifest.evidence_zip_sha256.
    These should both point to the inner ZIP hash."""
    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")
    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        sidecar_name = next((n for n in names if n.endswith(".sha256-proof.json")), None)
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert sidecar_name is not None, f"No sidecar file found. Contents: {names}"
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        sidecar = json.loads(outer.read(sidecar_name))
        manifest = json.loads(outer.read(manifest_name))

    sidecar_claimed_inner_sha = sidecar.get("sha256", "")
    manifest_inner_sha = manifest.get("evidence_zip_sha256", "")

    assert sidecar_claimed_inner_sha, "Sidecar must have 'sha256' field claiming inner ZIP SHA"
    assert manifest_inner_sha, "Manifest must have 'evidence_zip_sha256' field"
    assert sidecar_claimed_inner_sha == manifest_inner_sha, (
        f"Sidecar sha256={sidecar_claimed_inner_sha[:16]}... != "
        f"manifest evidence_zip_sha256={manifest_inner_sha[:16]}...\n"
        "Both should point to the inner evidence ZIP file hash."
    )


def test_inner_verdict_does_not_own_outer_delivery_sha():
    """The CURRENT sprint's inner final-verdict must NOT contain a concrete outer delivery SHA.
    Per the layered proof model, outer delivery SHA is external/unknown when inner ZIP is built.
    Acceptable values: 'external_delivery_manifest_authoritative', omitted, or empty.

    Note: Historical final-verdicts from prior sprints (e.g. r65/final-verdict.md) that are
    included in the inner ZIP as immutable records are NOT checked — they legitimately contain
    concrete SHAs from when those sprints were delivered. Only the CURRENT sprint's verdict
    is subject to the new proof model."""
    import re

    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    # Determine the current sprint name from the delivery package filename
    sprint_name = _get_sprint_name()

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        inner_name = next((n for n in names if n.endswith(".zip")), None)
        assert inner_name is not None, f"No inner ZIP found. Contents: {names}"
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        inner_names = inner.namelist()
        # Only check the CURRENT sprint's final-verdict, not historical ones
        current_verdict_path = f"repo/reports/{sprint_name}/final-verdict.md"
        verdict_files = [
            n for n in inner_names
            if n == current_verdict_path or n.endswith(f"/{sprint_name}/final-verdict.md")
        ]

    # This rule is only enforced for R71+ packages; R70 has the known PENDING defect
    # which is the motivation for R71 and this test.
    if sprint_name == "r70" or sprint_name == "unknown":
        pytest.skip(
            f"Sprint {sprint_name!r} pre-dates the layered proof model enforcement. "
            "This test enforces R71+ proof model requirements. "
            "R70's DELIVERY_PACKAGE_SHA: PENDING is the documented defect motivating R71."
        )

    if not verdict_files:
        pytest.skip(
            f"No current-sprint final-verdict.md found inside inner ZIP "
            f"(sprint={sprint_name!r}, looked for {current_verdict_path!r})"
        )

    for verdict_file in verdict_files:
        with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
            content = inner.read(verdict_file).decode("utf-8", errors="replace")

        for line in content.splitlines():
            stripped = line.strip()
            # Skip markdown list items and section headers
            if stripped.startswith(("- ", "* ", "# ")):
                continue
            if not stripped.startswith("DELIVERY_PACKAGE_SHA:"):
                continue
            value = stripped[len("DELIVERY_PACKAGE_SHA:"):].strip()
            assert not re.fullmatch(r"[0-9a-f]{64}", value), (
                f"Inner final-verdict {verdict_file!r} contains concrete outer delivery SHA:\n"
                f"  {stripped}\n"
                "Per the R71 layered proof model, inner ZIP cannot own outer delivery package SHA.\n"
                "Use: DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative"
            )
            assert value != "PENDING", (
                f"Inner final-verdict {verdict_file!r} has DELIVERY_PACKAGE_SHA: PENDING.\n"
                "This is the R70 proof model defect. "
                "Use: DELIVERY_PACKAGE_SHA: external_delivery_manifest_authoritative"
            )


def test_manifest_proof_model_layer_3_complete():
    """Delivery manifest (Layer 3) must contain both Layer-1 and Layer-2 references:
    - evidence_zip_sha256: SHA of inner ZIP (Layer 1 artifact)
    - sidecar_sha256: SHA of sidecar file (Layer 2 artifact)
    Both must be non-empty hex strings."""
    import re

    pkg_path, _ = _get_delivery_package()
    if pkg_path is None:
        pytest.skip("No delivery package available (pre-delivery mode)")

    with zipfile.ZipFile(pkg_path) as outer:
        names = outer.namelist()
        manifest_name = next(
            (n for n in names if n.endswith("-delivery-manifest.json") or n == "delivery-manifest.json"),
            None
        )
        assert manifest_name is not None, f"No delivery manifest found. Contents: {names}"
        manifest = json.loads(outer.read(manifest_name))

    evidence_sha = manifest.get("evidence_zip_sha256", "")
    sidecar_sha = manifest.get("sidecar_sha256", "")

    hex_pattern = re.compile(r"^[0-9a-f]{64}$")

    assert hex_pattern.match(evidence_sha), (
        f"manifest.evidence_zip_sha256={evidence_sha!r} is not a valid SHA-256 hex string. "
        "Layer 3 (delivery manifest) must record the Layer 1 (inner ZIP) SHA."
    )
    assert hex_pattern.match(sidecar_sha), (
        f"manifest.sidecar_sha256={sidecar_sha!r} is not a valid SHA-256 hex string. "
        "Layer 3 (delivery manifest) must record the Layer 2 (sidecar file) SHA."
    )
    assert evidence_sha != sidecar_sha, (
        "manifest.evidence_zip_sha256 == manifest.sidecar_sha256 — these must differ."
    )
