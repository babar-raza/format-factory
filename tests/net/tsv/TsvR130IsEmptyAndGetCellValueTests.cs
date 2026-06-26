// Tests for TsvDocument.IsEmpty and TsvDocument.GetCellValue(int row, int col).
// Sprint: ff-sprint-s131-dotnet-deepening-20260627
// Ledger: PC-TSV-R130

using System;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R130: Tests for TsvDocument.IsEmpty (computed bool: true when no rows) and
/// TsvDocument.GetCellValue(int row, int col) (returns string? with out-of-range → null).
/// Covers: IsEmpty on empty doc=true; IsEmpty after Load with data=false; IsEmpty
/// after all rows removed=true; GetCellValue valid row/col returns value; GetCellValue
/// out-of-range row returns null; GetCellValue out-of-range col returns null;
/// GetCellValue negative indices return null; GetCellValue with header row;
/// GetCellValue matches direct row access; dogfood Load→Filter→IsEmpty pipeline.
/// </summary>
public class TsvR130IsEmptyAndGetCellValueTests
{
    private static TsvDocument LoadSimple() =>
        TsvDocument.Load("Name\tScore\tCity\nAlice\t95\tLondon\nBob\t72\tParis\n", hasHeaders: true);

    // -------------------------------------------------------------------------
    // TsvDocument.IsEmpty
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvDocument_IsEmpty_EmptyContent_IsTrue()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    [Fact]
    public void TsvDocument_IsEmpty_WithDataRows_IsFalse()
    {
        var doc = LoadSimple();
        Assert.False(doc.IsEmpty);
    }

    [Fact]
    public void TsvDocument_IsEmpty_AfterClearingRows_IsTrue()
    {
        var doc = LoadSimple();
        doc.Rows.Clear();
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // TsvDocument.GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvDocument_GetCellValue_ValidRowCol_ReturnsValue()
    {
        var doc = LoadSimple();
        // Row 0 (first data row after headers) = Alice, 95, London
        var value = doc.GetCellValue(0, 0);
        Assert.Equal("Alice", value);
    }

    [Fact]
    public void TsvDocument_GetCellValue_SecondCol_ReturnsScore()
    {
        var doc = LoadSimple();
        Assert.Equal("95", doc.GetCellValue(0, 1));
    }

    [Fact]
    public void TsvDocument_GetCellValue_OutOfRangeRow_ReturnsNull()
    {
        var doc = LoadSimple();
        Assert.Null(doc.GetCellValue(99, 0));
    }

    [Fact]
    public void TsvDocument_GetCellValue_OutOfRangeCol_ReturnsNull()
    {
        var doc = LoadSimple();
        Assert.Null(doc.GetCellValue(0, 99));
    }

    [Fact]
    public void TsvDocument_GetCellValue_NegativeRow_ReturnsNull()
    {
        var doc = LoadSimple();
        Assert.Null(doc.GetCellValue(-1, 0));
    }

    [Fact]
    public void TsvDocument_GetCellValue_MatchesDirectRowAccess()
    {
        var doc = LoadSimple();
        // GetCellValue(1, 2) should match doc.Rows[1][2]
        var direct = doc.Rows[1][2];
        var cell = doc.GetCellValue(1, 2);
        Assert.Equal(direct, cell);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load → Filter → IsEmpty pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LoadFilterByPredicate_CheckIsEmpty()
    {
        var doc = LoadSimple();

        // Filter: keep only rows where score > 90 (Alice only)
        var filtered = doc.Filter(row => row.Length > 1 && int.TryParse(row[1], out var s) && s > 90);

        Assert.False(filtered.IsEmpty);
        Assert.Equal(1, filtered.RowCount);
        Assert.Equal("Alice", filtered.GetCellValue(0, 0));
    }
}
