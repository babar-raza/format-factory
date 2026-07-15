"""Semantic roundtrip test for UBL: an edit made before save survives reload.

Distinct from the identity roundtrip test in test_ubl_codec.py::TestRoundtrip,
which only proves load -> write -> load produces the SAME document unchanged.
This module proves load -> mutate -> write -> reload preserves the mutation.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from ubl.ubl_codec import load_ubl, write_ubl

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ubl"
VALID_DIR = SAMPLES / "valid"


class TestMutationRoundtrip:
    def test_add_invoice_line_survives_reload(self):
        """load -> mutate (append line) -> save -> reload: new line is present."""
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        original_count = len(model["lines"])
        model["lines"].append(
            {
                "id": "NEW-1",
                "quantity": "5",
                "amount": "25.00",
                "item_name": "New Widget",
            }
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            assert len(reloaded["lines"]) == original_count + 1
            reloaded_ids = [line["id"] for line in reloaded["lines"]]
            assert "NEW-1" in reloaded_ids

    def test_added_line_item_name_preserved(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        model["lines"].append(
            {"id": "NEW-2", "quantity": "3", "amount": "15.00", "item_name": "Gizmo"}
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated2.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            new_line = next(line for line in reloaded["lines"] if line["id"] == "NEW-2")
            assert new_line["item_name"] == "Gizmo"

    def test_added_line_quantity_and_amount_preserved(self):
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        model["lines"].append(
            {"id": "NEW-3", "quantity": "42", "amount": "99.99", "item_name": "Sprocket"}
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated3.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            new_line = next(line for line in reloaded["lines"] if line["id"] == "NEW-3")
            assert new_line["quantity"] == "42"
            assert new_line["amount"] == "99.99"

    def test_original_lines_preserved_after_addition(self):
        """Adding a line to a multi-line invoice must not disturb existing lines."""
        model = load_ubl(VALID_DIR / "multi-line-invoice.xml")
        original_ids = {line["id"] for line in model["lines"]}
        model["lines"].append(
            {"id": "NEW-4", "quantity": "1", "amount": "1.00", "item_name": "Extra"}
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated4.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            reloaded_ids = {line["id"] for line in reloaded["lines"]}
            assert original_ids.issubset(reloaded_ids)
            assert len(reloaded["lines"]) == len(original_ids) + 1

    def test_add_order_line_survives_reload(self):
        """Same mutation-roundtrip contract holds for Order documents."""
        model = load_ubl(VALID_DIR / "minimal-order.xml")
        original_count = len(model["lines"])
        model["lines"].append({"id": "O-NEW", "quantity": "2", "item_name": "Extra Gadget"})
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated_order.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            assert len(reloaded["lines"]) == original_count + 1
            reloaded_ids = [line["id"] for line in reloaded["lines"]]
            assert "O-NEW" in reloaded_ids

    def test_add_creditnote_line_survives_reload(self):
        """Same mutation-roundtrip contract holds for CreditNote documents."""
        model = load_ubl(VALID_DIR / "minimal-creditnote.xml")
        original_count = len(model["lines"])
        model["lines"].append(
            {"id": "CN-NEW", "quantity": "1", "amount": "5.00", "item_name": "Extra Widget"}
        )
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated_creditnote.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            assert len(reloaded["lines"]) == original_count + 1
            reloaded_ids = [line["id"] for line in reloaded["lines"]]
            assert "CN-NEW" in reloaded_ids
            assert reloaded["document_type"] == "CreditNote"

    def test_document_id_unchanged_by_line_mutation(self):
        """Mutating lines must not disturb unrelated header fields."""
        model = load_ubl(VALID_DIR / "minimal-invoice.xml")
        original_id = model["id"]
        model["lines"].append({"id": "NEW-5", "quantity": "1", "amount": "1.00", "item_name": "X"})
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td) / "mutated5.xml"
            write_ubl(model, dest)
            reloaded = load_ubl(dest)
            assert reloaded["id"] == original_id
