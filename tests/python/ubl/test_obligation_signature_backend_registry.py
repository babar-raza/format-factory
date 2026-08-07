"""UBL-SIGN-001 -- pluggable signing/verification backend registry.

MUST, quoted from the format contract (SAL-UBL-OBL-175ADB055BC12E8F,
SAL-UBL-OBL-452B9C973F40966B):

  "Report before saving whenever an edit invalidates an existing
   enveloped or detached signature, and never rewrite signed subtrees in
   lossless mode; verification and signing remain a separate pluggable
   opt-in."
  "Preserve signature structures without rewriting signed subtrees in
   lossless mode; report edits that invalidate existing signatures before
   saving."

The "report/never-rewrite" half is proven elsewhere
(UblDocument.signature_preserved and with_root). This file proves the
other half: a caller can register a verify/sign backend and get real
results back, while calling either function with no backend registered
returns a clear, explicit not-registered result rather than raising or
silently succeeding -- this package never bundles actual XMLDSig
cryptography itself.

Mirrors test_obligation_extension_adapter_registry.py's already-proven
pluggable-registry test pattern, since signature_backend.py mirrors
extension_adapters.py's registry shape.
"""

from __future__ import annotations

from format_factory.ubl import (
    ROOT_CLASSES,
    SignatureBackend,
    SignatureBackendRegistry,
    SignatureVerificationResult,
    XmlNode,
    sign_document,
    verify_signature,
)

_CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
Invoice = ROOT_CLASSES["Invoice"]


def _document():
    return Invoice.build(
        children=(
            XmlNode.create(f"{{{_CBC}}}UBLVersionID", text="2.3"),
            XmlNode.create(f"{{{_CBC}}}ID", text="INV-1"),
        )
    )


class TestRegistryPopulation:
    def test_an_empty_registry_has_no_backend(self) -> None:
        assert bool(SignatureBackendRegistry()) is False
        assert SignatureBackendRegistry().get() is None

    def test_register_then_get_round_trips(self) -> None:
        registry = SignatureBackendRegistry()
        backend = SignatureBackend(verify=lambda doc: True)
        registry.register(backend)
        assert registry.get() is backend
        assert bool(registry) is True

    def test_registering_a_second_backend_replaces_the_first(self) -> None:
        registry = SignatureBackendRegistry()
        registry.register(SignatureBackend(verify=lambda doc: True))
        second = SignatureBackend(verify=lambda doc: False)
        registry.register(second)
        assert registry.get() is second

    def test_a_backend_may_supply_only_verify_or_only_sign(self) -> None:
        verify_only = SignatureBackend(verify=lambda doc: True)
        assert verify_only.verify is not None
        assert verify_only.sign is None
        sign_only = SignatureBackend(sign=lambda doc: doc)
        assert sign_only.sign is not None
        assert sign_only.verify is None


class TestVerifySignature:
    def test_no_backend_registered_is_reported_not_an_error(self) -> None:
        registry = SignatureBackendRegistry()

        result = verify_signature(registry, _document())

        assert isinstance(result, SignatureVerificationResult)
        assert result.backend_registered is False
        assert result.verified is None

    def test_a_backend_with_no_verify_callable_is_reported_not_an_error(self) -> None:
        registry = SignatureBackendRegistry()
        registry.register(SignatureBackend(sign=lambda doc: doc))

        result = verify_signature(registry, _document())

        assert result.backend_registered is False
        assert result.verified is None

    def test_a_registered_verify_backend_returns_its_real_result(self) -> None:
        registry = SignatureBackendRegistry()
        registry.register(SignatureBackend(verify=lambda doc: True))

        result = verify_signature(registry, _document())

        assert result.backend_registered is True
        assert result.verified is True

    def test_a_registered_verify_backend_can_report_failure(self) -> None:
        registry = SignatureBackendRegistry()
        registry.register(SignatureBackend(verify=lambda doc: False))

        result = verify_signature(registry, _document())

        assert result.backend_registered is True
        assert result.verified is False


class TestSignDocument:
    def test_no_backend_registered_returns_none_not_an_error(self) -> None:
        registry = SignatureBackendRegistry()

        assert sign_document(registry, _document()) is None

    def test_a_backend_with_no_sign_callable_returns_none(self) -> None:
        registry = SignatureBackendRegistry()
        registry.register(SignatureBackend(verify=lambda doc: True))

        assert sign_document(registry, _document()) is None

    def test_a_registered_sign_backend_is_invoked_and_its_result_returned(self) -> None:
        registry = SignatureBackendRegistry()
        document = _document()
        registry.register(SignatureBackend(sign=lambda doc: doc))

        assert sign_document(registry, document) is document
