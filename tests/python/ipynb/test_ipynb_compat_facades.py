"""Tests for ipynb Compat facade classes (IpynbNotebook, IpynbCell, IpynbOutput).

Confirms each facade's spec_qname/spec_fact_ref/namespace_uri match the
shared/qname-registry/ipynb.yaml entries exactly, that each facade wraps
real parsed data correctly, and that each behaves sanely on an empty/
malformed dict (boundary condition).
"""
from __future__ import annotations

from pathlib import Path

from ipynb.Compat import IpynbCell, IpynbNotebook, IpynbOutput
from ipynb.ipynb_codec import load_ipynb

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ipynb"
VALID_DIR = SAMPLES / "valid"


class TestIpynbNotebookFacade:
    def test_spec_identity_matches_qname_registry(self):
        assert IpynbNotebook.spec_qname == "ipynb:notebook"
        assert IpynbNotebook.spec_fact_ref == "FACT-IPYNB-001"

    def test_namespace_uri_matches_registry(self):
        assert IpynbNotebook.namespace_uri == "urn:format:ipynb:4.5"

    def test_wraps_real_notebook_data(self):
        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        facade = IpynbNotebook(model)
        assert facade.nbformat == model["nbformat"]
        assert facade.cells == model["cells"]

    def test_empty_dict_defaults(self):
        facade = IpynbNotebook({})
        assert facade.nbformat == 0
        assert facade.nbformat_minor == 0
        assert facade.metadata == {}
        assert facade.cells == []


class TestIpynbCellFacade:
    def test_spec_identity_matches_qname_registry(self):
        assert IpynbCell.spec_qname == "ipynb:cell"
        assert IpynbCell.spec_fact_ref == "FACT-IPYNB-002"

    def test_namespace_uri_matches_registry(self):
        assert IpynbCell.namespace_uri == "urn:format:ipynb:4.5"

    def test_wraps_real_cell_data(self):
        model = load_ipynb(VALID_DIR / "code-and-markdown.ipynb")
        facade = IpynbCell(model["cells"][0])
        assert facade.cell_type == model["cells"][0]["cell_type"]

    def test_empty_dict_defaults(self):
        facade = IpynbCell({})
        assert facade.cell_type == "raw"
        assert facade.source == ""
        assert facade.outputs == []
        assert facade.execution_count is None


class TestIpynbOutputFacade:
    def test_spec_identity_matches_qname_registry(self):
        assert IpynbOutput.spec_qname == "ipynb:output"
        assert IpynbOutput.spec_fact_ref == "FACT-IPYNB-003"

    def test_namespace_uri_matches_registry(self):
        assert IpynbOutput.namespace_uri == "urn:format:ipynb:4.5"

    def test_wraps_real_output_data(self):
        model = load_ipynb(VALID_DIR / "with-outputs.ipynb")
        output_data = model["cells"][0]["outputs"][0]
        facade = IpynbOutput(output_data)
        assert facade.output_type == "execute_result"

    def test_empty_dict_defaults(self):
        facade = IpynbOutput({})
        assert facade.output_type == ""
        assert facade.data == {}
        assert facade.text == ""
        assert facade.ename == ""
        assert facade.traceback == []


class TestCompatModuleExports:
    def test_all_exports_present(self):
        from ipynb import Compat

        assert set(Compat.__all__) == {"IpynbNotebook", "IpynbCell", "IpynbOutput"}

    def test_facades_are_subclasses_of_spec_stubs(self):
        from ipynb.spec.notebook import Cell, Notebook, Output

        assert issubclass(IpynbNotebook, Notebook)
        assert issubclass(IpynbCell, Cell)
        assert issubclass(IpynbOutput, Output)
