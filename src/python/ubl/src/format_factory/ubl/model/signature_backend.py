"""Pluggable signing/verification backend registry (UBL-SIGN-001).

UBL-SIGN-001 asks for two distinct things: "report before saving whenever
an edit invalidates an existing enveloped or detached signature, and
never rewrite signed subtrees in lossless mode" (built in
model/document.py's UblDocument.signature_preserved and with_root --
checksum-based presence/integrity tracking, not cryptographic
verification) and "verification and signing remain a separate pluggable
opt-in" (not previously built -- this module).

Mirrors :mod:`.codelist` and :mod:`.extension_adapters`' already-proven
pluggable-registry pattern: a caller registers a backend at runtime; this
package never bundles an actual XMLDSig implementation itself (real
signature verification/creation is a cryptography concern with real key
material, external trust anchors, and algorithm negotiation -- entirely
out of scope for a format library, and no SAL fact in this repository
documents a specific XMLDSig profile precisely enough to build one
without fabricating spec content). "Opt-in" is structural: calling
verify_signature()/sign_document() with no backend registered returns a
clear, explicit "no backend registered" result rather than raising or
silently succeeding.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .document import UblDocument

SignatureVerifier = Callable[[UblDocument], bool]
SignatureSigner = Callable[[UblDocument], UblDocument]


@dataclass(frozen=True, slots=True)
class SignatureBackend:
    """A caller-supplied pair of signing/verification callables.

    Either half may be omitted -- a backend that can verify but not sign
    (or vice versa) is a legitimate, partial registration.
    """

    verify: SignatureVerifier | None = None
    sign: SignatureSigner | None = None


@dataclass(frozen=True, slots=True)
class SignatureVerificationResult:
    """The outcome of attempting to verify one document's signature."""

    backend_registered: bool
    verified: bool | None
    detail: str


class SignatureBackendRegistry:
    """A pluggable, in-memory registry holding at most one backend.

    Populated at runtime by the caller, exactly like
    :class:`~.codelist.CodeListRegistry` and
    :class:`~.extension_adapters.ExtensionAdapterRegistry`. Unlike those
    two, there is no natural per-key namespace for a document-level
    signing/verification operation, so this registry holds a single
    backend slot, replaced wholesale on re-register.
    """

    def __init__(self) -> None:
        self._backend: SignatureBackend | None = None

    def register(self, backend: SignatureBackend) -> None:
        self._backend = backend

    def get(self) -> SignatureBackend | None:
        return self._backend

    def __bool__(self) -> bool:
        return self._backend is not None


def verify_signature(
    registry: SignatureBackendRegistry, document: UblDocument
) -> SignatureVerificationResult:
    """Verify `document`'s signature through `registry`'s backend.

    No backend registered, or a registered backend with no verify
    callable, is reported as `backend_registered=False` / `verified=None`
    -- not an error and not a silent pass. This is what makes verification
    opt-in: calling this function is always safe, whether or not a caller
    has plugged in a real XMLDSig implementation.
    """

    backend = registry.get()
    if backend is None or backend.verify is None:
        return SignatureVerificationResult(
            backend_registered=False,
            verified=None,
            detail="no signature verification backend registered",
        )
    return SignatureVerificationResult(
        backend_registered=True,
        verified=backend.verify(document),
        detail="verified by the registered backend",
    )


def sign_document(
    registry: SignatureBackendRegistry, document: UblDocument
) -> UblDocument | None:
    """Sign `document` through `registry`'s backend.

    No backend registered, or a registered backend with no sign callable,
    returns None rather than raising -- the same opt-in-safe shape as
    verify_signature(): calling this function is always safe, whether or
    not a caller has plugged in a real signing implementation. A caller
    that needs signing to be mandatory checks the result itself.
    """

    backend = registry.get()
    if backend is None or backend.sign is None:
        return None
    return backend.sign(document)


__all__ = [
    "SignatureBackend",
    "SignatureBackendRegistry",
    "SignatureSigner",
    "SignatureVerificationResult",
    "SignatureVerifier",
    "sign_document",
    "verify_signature",
]
