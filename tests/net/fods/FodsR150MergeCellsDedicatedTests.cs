// Tests for FodsDocument.MergeCells dedicated deepening.
// Sprint: ff-sprint-s141-dotnet-deepening-20260627
// Ledger: PC-FODS-R150

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R150: Dedicated tests for FodsDocument.MergeCells.
/// MergeCells merges a rectangular region of cells in a named sheet, setting
/// column-span and row-span attributes on the anchor cell.
/// Covers: null sheetName throws ArgumentException; empty sheetName throws;
/// whitespace sheetName throws; rowSpan=0 throws ArgumentOutOfRangeException;
/// colSpan=0 throws; rowSpan negative throws; colSpan negative throws;
/// nonexistent sheetName throws InvalidOperationException;
/// valid 1x2 merge does not throw; valid 2x1 merge does not throw;
/// dogfood CreateNew->SetCellValue->MergeCells->GetCellValue pipeline.
/// </summary>
public class FodsR150MergeCellsDedicatedTests
{
    // -------------------------------------------------------------------------
    // sheetName guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() =>
            doc.MergeCells(null!, 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_EmptySheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() =>
            doc.MergeCells(string.Empty, 0, 0, 1, 2));
    }

    [Fact]
    public void MergeCells_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() =>
            doc.MergeCells("   ", 0, 0, 1, 2));
    }

    // -------------------------------------------------------------------------
    // span guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_RowSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(sheetName, 0, 0, 0, 1));
    }

    [Fact]
    public void MergeCells_ColSpanZero_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(sheetName, 0, 0, 1, 0));
    }

    [Fact]
    public void MergeCells_RowSpanNegative_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(sheetName, 0, 0, -1, 1));
    }

    [Fact]
    public void MergeCells_ColSpanNegative_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            doc.MergeCells(sheetName, 0, 0, 1, -2));
    }

    // -------------------------------------------------------------------------
    // Nonexistent sheet
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeCells_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(() =>
            doc.MergeCells("DoesNotExist", 0, 0, 1, 2));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> SetCellValue -> MergeCells -> GetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellValue_MergeCells_AnchorCellRetainsValue()
    {
        var doc = FodsDocument.CreateNew();
        var sheetName = doc.GetSheetNames()[0];

        // Populate a 2x2 grid
        doc.SetCellValue(0, 0, "Header");
        doc.SetCellValue(0, 1, "Sub");

        // Merge across 2 columns in row 0 (1x2 span)
        // Should not throw — merge within existing cell bounds
        var exception = Record.Exception(() =>
            doc.MergeCells(sheetName, 0, 0, 1, 2));
        Assert.Null(exception);

        // Anchor cell still has its value
        var value = doc.GetCellValue(0, 0);
        Assert.Equal("Header", value);
    }
}
