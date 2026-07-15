"""L0 smoke tests — package importability, public API surface, exception hierarchy."""

from __future__ import annotations


class TestPackageImport:
    def test_import_ubl_package(self):
        import ubl

        assert ubl is not None

    def test_all_exports_are_importable(self):
        import ubl

        for name in ubl.__all__:
            assert hasattr(ubl, name), f"{name} listed in __all__ but not importable"

    def test_version_attr_present(self):
        import ubl

        assert isinstance(ubl.__version__, str)


class TestCompatImport:
    def test_import_compat_package(self):
        from ubl import Compat

        assert hasattr(Compat, "UblInvoice")
        assert hasattr(Compat, "UblCreditNote")
        assert hasattr(Compat, "UblOrder")
        assert hasattr(Compat, "UblLineItem")

    def test_compat_all_matches_exports(self):
        from ubl import Compat

        assert set(Compat.__all__) == {
            "UblInvoice",
            "UblCreditNote",
            "UblOrder",
            "UblLineItem",
        }


class TestSpecImport:
    def test_import_spec_package(self):
        from ubl import spec

        assert hasattr(spec, "Invoice")
        assert hasattr(spec, "Order")
        assert hasattr(spec, "LineItem")


class TestAnalyticsImport:
    def test_import_analytics_module(self):
        from ubl import ubl_analytics

        assert callable(ubl_analytics.ubl_total_line_count)
        assert callable(ubl_analytics.ubl_supplier_name)
        assert callable(ubl_analytics.ubl_document_type_summary)


class TestExceptionHierarchy:
    def test_exceptions_defined(self):
        from ubl.exceptions import UblError, UblParseError, UblWriteError

        assert issubclass(UblParseError, UblError)
        assert issubclass(UblWriteError, UblError)

    def test_ubl_error_is_exception(self):
        from ubl.exceptions import UblError

        assert issubclass(UblError, Exception)


class TestFromFile:
    def test_ubl_document_from_file(self):
        from pathlib import Path

        from ubl.models import UblDocument

        samples = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
        doc = UblDocument.from_file(samples / "valid" / "minimal-invoice.xml")
        assert doc.document_type == "Invoice"
