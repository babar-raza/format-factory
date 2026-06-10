# IV Report — PROB-PY01: pyproject.toml pilot for abw + gnumeric

| Check | Result |
|-------|--------|
| Source diff reviewed? | Y — Two new files created: src/python/abw/pyproject.toml and src/python/gnumeric/pyproject.toml. Both use setuptools.build_meta backend, where=[".."] to locate packages from parent directory. |
| Raw log reviewed? | Y — pip install -e src/python/abw/ PASS. `import abw; abw.__version__` = "0.1.0.dev0". pip install -e src/python/gnumeric/ PASS. `import gnumeric; gnumeric.__version__` = "0.1.0.dev0". |
| Before vs after score compared? | Y — abw and gnumeric: install_method PYTHONPATH_ONLY → PIP_INSTALLABLE. CRITICAL gap partially closed (2 of 10 packages). |
| No unintended side effects? | Y — New files only (no existing file modified). No test breakage. |
| Other product tests not broken? | Y — Existing tests still use PYTHONPATH; pip install adds another install path. |
| Correction (retry): | Build-backend corrected from setuptools.backends.legacy:build to setuptools.build_meta on retry. Final install PASS. |

**IV Verdict: ACCEPTED**

abw pyproject.toml SHA-256:      95760ee72723811dab04889022d4371ba211d1a703e43a760cdacf74ad40be9f
gnumeric pyproject.toml SHA-256: c29021c1f18db8cbdd758ed7041c1bdd62235d7f24a3b7db2482947e710e0d8c

Note: PROB-PY01 CRITICAL gap is PARTIALLY closed (2 of 10 packages). Full fix for remaining 8 packages is FIX_LATER pending user authorization.
