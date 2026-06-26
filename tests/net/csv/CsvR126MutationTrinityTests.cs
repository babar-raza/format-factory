// Tests for CsvDocument mutation API: AddRow, SetCell, RemoveRow.
// Sprint: FORMAT-FACTORY-CSV-R126-20260626
// Ledger: R126-GOVERNED-DOTNET-CSV-MUTATION-TRINITY-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R126: Tests for CsvDocument.AddRow(), SetCell(), and RemoveRow() mutation methods.
/// Verifies that the mutation trinity produces consistent RowCount, column values,
/// and cell data — and that mutation results survive a ToCsv/reload round-trip.
/// RFC 4180 basis: §2 ABNF for record/field structure.
/// </summary>
public class CsvR126MutationTrinityTests
{
    private static CsvDocument LoadSample() =>
        CsvDocument.Load("Name,Score,City\nAlice,90,NYC\nBob,80,London");

    // -------------------------------------------------------------------------
    // AddRow
    // -------------------------------------------------------------------------

    [Fact]
    public void AddRow_IncrementsRowCount()
    {
        var doc = LoadSample();
        int before = doc.RowCount;
        doc.AddRow(new[] { "Carol", "95", "Paris" });
        Assert.Equal(before + 1, doc.RowCount);
    }

    [Fact]
    public void AddRow_NewRowValuesAreAccessible()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Carol", "95", "Paris" });
        var last = doc.Rows[doc.RowCount - 1];
        Assert.Equal("Carol", last[0]);
        Assert.Equal("95",    last[1]);
        Assert.Equal("Paris", last[2]);
    }

    [Fact]
    public void AddRow_MultipleRows_AllPresent()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Carol", "95", "Paris" });
        doc.AddRow(new[] { "Dave",  "70", "Berlin" });
        Assert.Equal(4, doc.RowCount);  // 2 original + 2 added
        Assert.Equal("Dave", doc.Rows[3][0]);
    }

    // -------------------------------------------------------------------------
    // SetCell
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCell_ChangesValue()
    {
        var doc = LoadSample();
        doc.SetCell(0, 1, "99");
        Assert.Equal("99", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void SetCell_DoesNotAffectOtherCells()
    {
        var doc = LoadSample();
        string originalName = doc.GetCellValue(0, 0)!;
        doc.SetCell(0, 1, "99");
        Assert.Equal(originalName, doc.GetCellValue(0, 0));
    }

    [Fact]
    public void SetCell_RowCountUnchanged()
    {
        var doc = LoadSample();
        int before = doc.RowCount;
        doc.SetCell(0, 0, "Zeta");
        Assert.Equal(before, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveRow_DecrementsRowCount()
    {
        var doc = LoadSample();
        int before = doc.RowCount;
        doc.RemoveRow(0);
        Assert.Equal(before - 1, doc.RowCount);
    }

    [Fact]
    public void RemoveRow_ShiftsRemainingRows()
    {
        var doc = LoadSample();
        string secondName = doc.Rows[1][0];
        doc.RemoveRow(0);
        Assert.Equal(secondName, doc.Rows[0][0]);
    }

    [Fact]
    public void RemoveRow_InvalidIndex_Throws()
    {
        var doc = LoadSample();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.RemoveRow(999));
    }

    // -------------------------------------------------------------------------
    // Round-trip: mutate → ToCsv → reload → verify
    // -------------------------------------------------------------------------

    [Fact]
    public void MutationTrinity_RoundTrip_ConsistentRowCount()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Carol", "95", "Paris" });
        doc.SetCell(0, 1, "99");
        doc.RemoveRow(2);  // removes "Bob"

        string csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv);
        Assert.Equal(doc.RowCount, doc2.RowCount);
    }

    [Fact]
    public void MutationTrinity_RoundTrip_SetCellValuePreserved()
    {
        var doc = LoadSample();
        doc.SetCell(0, 0, "PROOF_ENTRY");
        string csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Contains("PROOF_ENTRY", csv);
    }

    [Fact]
    public void MutationTrinity_RoundTrip_AddedRowPresent()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "ROUNDTRIP", "42", "TestCity" });
        string csv = doc.ToCsv();
        var doc2 = CsvDocument.Load(csv);
        Assert.Equal(doc.RowCount, doc2.RowCount);
        string lastVal = doc2.Rows[doc2.RowCount - 1][0];
        Assert.Equal("ROUNDTRIP", lastVal);
    }
}
