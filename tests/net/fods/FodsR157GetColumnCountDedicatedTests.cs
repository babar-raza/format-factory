// Tests for FodsDocument.GetColumnCount dedicated coverage.
// Sprint: ff-sprint-s150-dotnet-deepening-20260628
// Ledger: PC-FODS-R157

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R157: Dedicated tests for FodsDocument.GetColumnCount and GetColumnCount(string sheetName).
/// GetColumnCount() returns the maximum column count across all rows of the first sheet.
/// GetColumnCount(string) uses the named sheet; throws InvalidOperationException if not found.
/// Returns 0 for empty document or sheet with no rows.
/// Covers: empty doc returns 0; empty sheet returns 0; single cell returns 1;
/// row with 3 cells returns 3; named sheet nonexistent throws;
/// wider row determines column count; named sheet correct count;
/// count is max across rows (not sum); idempotent; dogfood pipeline;
/// dogfood named sheet vs first sheet same when same data.
/// </summary>
public class FodsR157GetColumnCountDedicatedTests
{
    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // -------------------------------------------------------------------------
    // Zero-column tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_EmptyDocument_ReturnsZero()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_EmptySheet_ReturnsZero()
    {
        var doc = MakeDoc();
        Assert.Equal(0, doc.GetColumnCount());
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_NamedSheet_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = MakeDoc();
        Assert.Throws<InvalidOperationException>(() => doc.GetColumnCount("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_SingleCell_ReturnsOne()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A");
        Assert.Equal(1, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_ThreeCellsInRow_ReturnsThree()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet1", 0, 1, "B");
        doc.SetCellValue("Sheet1", 0, 2, "C");
        Assert.Equal(3, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_MaxAcrossRows_LongerRowDetermines()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A"); // row 0: 1 col
        doc.SetCellValue("Sheet1", 1, 0, "B"); // row 1: 3 cols
        doc.SetCellValue("Sheet1", 1, 1, "C");
        doc.SetCellValue("Sheet1", 1, 2, "D");
        Assert.Equal(3, doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_IsIdempotent()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "X");
        doc.SetCellValue("Sheet1", 0, 1, "Y");
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount());
    }

    [Fact]
    public void GetColumnCount_NamedSheet_ReturnsCorrectCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MySheet");
        doc.SetCellValue("MySheet", 0, 0, "A");
        doc.SetCellValue("MySheet", 0, 1, "B");
        doc.SetCellValue("MySheet", 0, 2, "C");
        doc.SetCellValue("MySheet", 0, 3, "D");
        Assert.Equal(4, doc.GetColumnCount("MySheet"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValues_GetColumnCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 0, 2, "Grade");
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "95");
        // row 0 has 3 columns, row 1 has 2 — max is 3
        Assert.True(doc.GetColumnCount() >= 3);
    }

    [Fact]
    public void DogfoodPipeline_NamedSheet_SameAsFirstSheet_WhenOnlyOneSheet()
    {
        var doc = MakeDoc("Single");
        doc.SetCellValue("Single", 0, 0, "X");
        doc.SetCellValue("Single", 0, 1, "Y");
        Assert.Equal(doc.GetColumnCount(), doc.GetColumnCount("Single"));
    }
}
