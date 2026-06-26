// Tests for CsvDocument.IsEmpty and CsvDocument.RemoveRow(int index).
// Sprint: ff-sprint-s133-dotnet-deepening-20260627
// Ledger: PC-CSV-R132

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R132: Tests for CsvDocument.IsEmpty (bool computed from Rows.Count==0) and
/// CsvDocument.RemoveRow(int index) (removes the row at the given index).
/// Covers: IsEmpty on empty doc=true; IsEmpty with data=false; IsEmpty after RemoveRow
/// removes last row=true; RemoveRow reduces RowCount; RemoveRow removes correct row;
/// RemoveRow last index works; RemoveRow first index works; GetCellValue after RemoveRow
/// returns updated values; IsEmpty after RemoveRow all=true; dogfood Load→RemoveRow→ToCsv.
/// </summary>
public class CsvR132IsEmptyAndRemoveRowTests
{
    private static CsvDocument LoadThreeRows() =>
        CsvDocument.Load("Name,Score,City\nAlice,95,London\nBob,72,Paris\nCarol,88,Berlin\n", hasHeaders: true);

    // -------------------------------------------------------------------------
    // CsvDocument.IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvDocument_IsEmpty_EmptyDoc_IsTrue()
    {
        var doc = CsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void CsvDocument_IsEmpty_WithDataRows_IsFalse()
    {
        var doc = LoadThreeRows();
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void CsvDocument_IsEmpty_AfterRemoveAllRows_IsTrue()
    {
        var doc = LoadThreeRows();
        doc.RemoveRow(2);
        doc.RemoveRow(1);
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // CsvDocument.RemoveRow
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvDocument_RemoveRow_ReducesRowCount()
    {
        var doc = LoadThreeRows();
        Assert.Equal(3, doc.RowCount);
        doc.RemoveRow(0);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void CsvDocument_RemoveRow_FirstRow_ShiftsRemainingRows()
    {
        var doc = LoadThreeRows();
        doc.RemoveRow(0);
        // Bob should now be at row 0
        Assert.Equal("Bob", doc.GetCellValue(0, 0));
    }

    [Fact]
    public void CsvDocument_RemoveRow_LastRow_RemovesCorrectly()
    {
        var doc = LoadThreeRows();
        doc.RemoveRow(2);
        Assert.Equal(2, doc.RowCount);
        // Carol should be gone; Bob should still be at row 1
        Assert.Equal("Bob", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void CsvDocument_RemoveRow_MiddleRow_RemovesCorrectly()
    {
        var doc = LoadThreeRows();
        doc.RemoveRow(1);  // Remove Bob
        Assert.Equal(2, doc.RowCount);
        // Alice at 0, Carol at 1
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Carol", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void CsvDocument_RemoveRow_SingleRow_ResultIsEmpty()
    {
        var doc = CsvDocument.Load("Alice,95,London\n", hasHeaders: false);
        Assert.Equal(1, doc.RowCount);
        doc.RemoveRow(0);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load → RemoveRow → ToCsv roundtrip
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_Load_RemoveRow_ToCsv_NoLongerContainsRemovedRow()
    {
        var doc = LoadThreeRows();
        // Remove Bob (row 1)
        doc.RemoveRow(1);

        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Carol", csv);
        Assert.DoesNotContain("Bob", csv);
    }
}
