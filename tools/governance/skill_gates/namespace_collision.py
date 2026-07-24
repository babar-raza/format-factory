"""Namespace collision — guard a new package name against stdlib / popular PyPI names.

BLOCKING POLICY (revised 2026-07-20, governance fix following TC-PA-039 review)
--------------------------------------------------------------------------------
STDLIB collisions BLOCK (`.blocked == True`). A same-named stdlib module always
wins or gets hijacked (see MODE 1 / MODE 2 below) — there is no safe outcome, so
new packages are refused and existing ones must rename (csv -> ff_csv, TC-PA-013).

POPULAR-PYPI collisions do NOT block (`.blocked == False`) — they WARN only. A
name matching `_POPULAR_PACKAGE_NAMES` (e.g. `toml`) is a *possible* future
collision, contingent on whether that specific distribution ever gets installed
in the same environment. It is not a stdlib module, so absent that distribution
our package resolves correctly under its own name today. Renaming every format
package away from any name that some PyPI project also uses is neither
tractable (the popular-package list is large and grows) nor proportionate to a
risk that has not materialized. TC-PA-039 (`toml` -> `ff_toml` rename) was
CLOSED_NOT_REQUIRED on this basis — `toml` is not stdlib, nothing in this
project's dependency tree installs the PyPI `toml` package, and the WARN from
V250 plus this baseline entry is the correct standing signal, not a red-lined
mandatory rename. If a project dependency later starts pulling in the colliding
PyPI package, the WARN becomes actionable at that point, not before.

WHAT ACTUALLY GOES WRONG (measured 2026-07-17, this repo's venv, CPython 3.13)
-----------------------------------------------------------------------------
`src/python/csv/` is the worked example. Naming a package `csv` produces TWO
mutually exclusive failure modes depending on sys.path order. Both are bad, and
they cannot both be fixed by ordering -- only by not taking the name.

  MODE 1 -- STDLIB WINS (the default in this venv; our package is unreachable)
    sys.path order: C:\\Python313\\Lib is at [3]; the .pth-injected src/python
    is at [7]. Therefore:
        >>> import csv; csv.__file__
        'C:\\Python313\\Lib\\csv.py'
    Our csv package is DEAD under its own name. Every `import csv` in the repo
    silently gets the stdlib. Consumers who `pip install` our csv package get
    nothing importable as `csv`.

  MODE 2 -- OURS WINS (only with an explicit sys.path.insert(0, src/python))
        >>> import csv; csv.__file__
        '.../src/python/csv/__init__.py'
        >>> csv.reader
        AttributeError: module 'csv' has no attribute 'reader'
    Our csv exposes 130 names but NONE of reader/writer/DictReader/DictWriter/
    QUOTE_MINIMAL. So the insert does not merely "prefer ours" -- it HIJACKS
    stdlib csv process-wide for every other library in the interpreter. Anything
    that does `import csv; csv.reader(...)` now crashes.

  These two modes explain why the sys.path hacks in this repo are load-bearing
  for csv specifically (see the plan's PA-F1): the hack is what makes our csv
  importable at all, at the cost of breaking everyone else's csv.

  NOTE: an earlier plan draft described this as "our csv package shadows Python's
  stdlib csv". That is BACKWARDS for mode 1, which is the default. Do not repeat
  the inverted claim; a guard justified by an inverted fault model gets tuned the
  wrong way.

VERSION CAVEAT (honest limitation)
----------------------------------
`sys.stdlib_module_names` describes the RUNNING interpreter only. A name that is
clean on 3.13 may collide on another version (and vice versa: `tomllib` is 3.11+).
Consumers of a published package do not necessarily run 3.13. `_EXTRA_STDLIB_NAMES`
therefore adds names from other supported versions that the running interpreter
would not report. This list is maintained by hand and is not exhaustive.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

# Stdlib top-level names that the RUNNING interpreter may not report but that
# collide on some supported CPython version (removed, deprecated, or newer).
_EXTRA_STDLIB_NAMES = frozenset({
    "tomllib",      # 3.11+
    "asynchat", "asyncore", "smtpd",   # removed in 3.12
    "distutils",    # removed in 3.12
    "imp",          # removed in 3.12
    "cgi", "cgitb", "pipes", "telnetlib", "uu", "crypt", "nis",  # removed 3.13
    "audioop", "chunk", "sndhdr", "imghdr", "mailcap", "msilib", "nntplib",
    "ossaudiodev", "spwd", "sunau", "xdrlib",
})

# Widely-installed PyPI distributions whose IMPORT name would be shadowed by a
# same-named package in src/python. Taking one of these names breaks any
# environment where both are installed, and the winner depends on sys.path order.
_POPULAR_PACKAGE_NAMES = frozenset({
    "yaml", "toml", "numpy", "pandas", "requests", "six", "attrs", "attr",
    "click", "jinja2", "flask", "django", "pytest", "setuptools", "pip",
    "wheel", "lxml", "PIL", "pillow", "scipy", "matplotlib", "boto3",
    "urllib3", "certifi", "chardet", "idna", "packaging", "pyparsing",
    "dateutil", "pytz", "openpyxl", "xlrd", "docutils", "markdown",
    "cryptography", "zstandard", "protobuf", "grpc", "torch", "tensorflow",
    "sqlalchemy", "pydantic", "typing_extensions", "rich", "tqdm", "httpx",
    "aiohttp", "starlette", "fastapi", "uvicorn", "jsonschema", "regex",
    "safetensors",  # HuggingFace tensor serialization — not installed here (latent, not live)
})

VERDICT_OK = "OK"
VERDICT_STDLIB = "STDLIB_COLLISION"
VERDICT_POPULAR = "POPULAR_PACKAGE_COLLISION"
VERDICT_INVALID = "INVALID_IDENTIFIER"


@dataclass(frozen=True)
class CollisionResult:
    name: str
    verdict: str
    detail: str

    @property
    def blocked(self) -> bool:
        return self.verdict in (VERDICT_STDLIB, VERDICT_INVALID)


def stdlib_names() -> frozenset[str]:
    """Stdlib top-level module names: running interpreter + cross-version extras."""
    running = getattr(sys, "stdlib_module_names", frozenset())
    return frozenset(running) | _EXTRA_STDLIB_NAMES


def check_name(name: str) -> CollisionResult:
    """Classify a candidate package name.

    Returns a CollisionResult; `.blocked` is True for any collision. The caller
    decides the exit code -- this function never exits or prints.
    """
    n = (name or "").strip()
    if not n.isidentifier():
        return CollisionResult(n, VERDICT_INVALID,
                               f"{n!r} is not a valid Python identifier and cannot "
                               "be a package directory name")
    low = n.lower()
    if n in stdlib_names() or low in stdlib_names():
        return CollisionResult(
            n, VERDICT_STDLIB,
            f"'{n}' is a Python standard-library module name. A package at "
            f"src/python/{n}/ has two failure modes and no good one: (1) stdlib "
            f"wins on sys.path order -> our package is unreachable under its own "
            f"name; (2) if a sys.path.insert(0, ...) forces ours to win, it "
            f"hijacks stdlib '{n}' process-wide for every library in the "
            f"interpreter. Choose a non-colliding name (e.g. 'ff_{low}').")
    if n in _POPULAR_PACKAGE_NAMES or low in _POPULAR_PACKAGE_NAMES:
        return CollisionResult(
            n, VERDICT_POPULAR,
            f"'{n}' is the import name of a widely-installed PyPI distribution. "
            f"In any environment where both are present the winner depends on "
            f"sys.path order, which is not something this project controls. "
            f"Choose a non-colliding name (e.g. 'ff_{low}').")
    return CollisionResult(n, VERDICT_OK, f"'{n}' does not collide with a known "
                                          "stdlib or popular-package name")
