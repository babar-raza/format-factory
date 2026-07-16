"""Format Factory — Skills-First Control System (SFC).

A cohesive, fail-closed control layer that binds agent material actions to the
skill system. Modules:

  registries  — canonical loaders for skill/command/capability registries
  audit       — deterministic parity + coverage reporter (CI-suitable)
  manifest    — execution-manifest schema + create/load/validate/close
  resolve     — deterministic skill resolution (operation -> route -> skill)
  closeout    — fail-closed closeout gate (changed files vs manifest + evidence)

Authority: docs/governance/skill-only-policy.yaml (SKILL-ONLY-POLICY-001).
This package implements the enforcement primitives the policy references but
previously lacked a concrete, tested, fail-closed implementation for.

Design invariants (all modules):
  * Missing/malformed registries -> hard error (exit 2 / raise), never a clean pass.
  * Every public function is import-safe and side-effect free unless it is a
    documented writer (create_manifest, close_manifest, audit --write).
  * No dependency beyond PyYAML + stdlib.
"""
from __future__ import annotations

SFC_VERSION = "1.0.0"
POLICY_ID = "SKILL-ONLY-POLICY-001"
