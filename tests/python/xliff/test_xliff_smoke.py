"""L0 smoke tests for the xliff package — importability and public surface."""

from __future__ import annotations


class TestSmoke:
    def test_package_importable(self):
        import xliff

        assert xliff.__version__

    def test_from_file_classmethod_exists(self):
        from xliff.models import XliffDocument

        assert hasattr(XliffDocument, "from_file")
        assert callable(XliffDocument.from_file)

    def test_exceptions_are_exception_subclasses(self):
        from xliff.exceptions import XliffError, XliffParseError, XliffWriteError

        assert issubclass(XliffParseError, XliffError)
        assert issubclass(XliffWriteError, XliffError)
        assert issubclass(XliffError, Exception)

    def test_compat_and_spec_packages_importable(self):
        from xliff import Compat
        from xliff import spec

        assert hasattr(Compat, "XliffFile")
        assert hasattr(spec, "File")

    def test_all_exports_include_new_analytics_functions(self):
        import xliff

        for name in (
            "xliff_translated_segment_count",
            "xliff_untranslated_segment_count",
            "xliff_average_source_length",
        ):
            assert name in xliff.__all__
            assert callable(getattr(xliff, name))
