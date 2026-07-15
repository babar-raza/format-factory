"""Smoke/import tests for the professional-tier ipynb package additions
(spec/notebook stubs, Compat facades, ipynb_analytics module).
"""
from __future__ import annotations


class TestPackageImportSmoke:
    def test_import_analytics_module(self):
        from ipynb import ipynb_analytics

        assert ipynb_analytics is not None

    def test_import_compat_package(self):
        from ipynb import Compat

        assert Compat is not None

    def test_import_spec_notebook_package(self):
        from ipynb.spec import notebook

        assert notebook is not None

    def test_analytics_functions_exported_at_top_level(self):
        import ipynb

        assert callable(ipynb.ipynb_cell_type_histogram)
        assert callable(ipynb.ipynb_output_type_histogram)
        assert callable(ipynb.ipynb_average_source_length)
        assert callable(ipynb.ipynb_has_execution_errors)

    def test_all_contains_new_analytics_names(self):
        import ipynb

        for name in (
            "ipynb_cell_type_histogram",
            "ipynb_output_type_histogram",
            "ipynb_average_source_length",
            "ipynb_has_execution_errors",
        ):
            assert name in ipynb.__all__
