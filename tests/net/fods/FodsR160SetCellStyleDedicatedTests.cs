// Tests for FodsDocument.SetCellStyle dedicated coverage.
// Sprint: ff-sprint-s153-dotnet-deepening-20260628
// Ledger: PC-FODS-R160

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R160: Dedicated tests for FodsDocument.SetCellStyle(string sheetName, int row, int col, string styleName).
/// SetCellStyle assigns a named style to a specific cell in the document.
/// Throws ArgumentException for null/whitespace sheetName or nonexistent sheet.
/// Throws ArgumentNullException for null styleName.
/// Throws ArgumentOutOfRangeException for out-of-range row or col.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws ArgumentException;
/// nonexistent sheet throws ArgumentException; null styleName throws ArgumentNullException;
/// negative row throws ArgumentOutOfRangeException; negative col throws ArgumentOutOfRangeException;
/// row beyond range throws ArgumentOutOfRangeException; col beyond range throws ArgumentOutOfRangeException;
/// dogfood CreateNew->AddSheet->SetCellValue->SetCellStyle pipeline;
/// dogfood SetCellStyle idempotent on same cell.
/// </summary>
public class FodsR160SetCellStyleDedicatedTests
{
    private static FodsDocument MakeDocWithCell()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests — sheetName
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_NullSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentException>(() => doc.SetCellStyle(null!, 0, 0, "Default"));
    }

    [Fact]
    public void SetCellStyle_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentException>(() => doc.SetCellStyle("   ", 0, 0, "Default"));
    }

    [Fact]
    public void SetCellStyle_NonexistentSheet_ThrowsArgumentException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentException>(() => doc.SetCellStyle("NoSheet", 0, 0, "Default"));
    }

    // -------------------------------------------------------------------------
    // Guard tests — styleName
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_NullStyleName_ThrowsArgumentNullException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentNullException>(() => doc.SetCellStyle("Sheet1", 0, 0, null!));
    }

    // -------------------------------------------------------------------------
    // Guard tests — row/col bounds
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellStyle("Sheet1", -1, 0, "Default"));
    }

    [Fact]
    public void SetCellStyle_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellStyle("Sheet1", 0, -1, "Default"));
    }

    [Fact]
    public void SetCellStyle_RowBeyondRange_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellStyle("Sheet1", 99, 0, "Default"));
    }

    [Fact]
    public void SetCellStyle_ColBeyondRange_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellStyle("Sheet1", 0, 99, "Default"));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_SetCellStyle()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Header");
        // Should not throw — assigning a style name to a valid cell
        doc.SetCellStyle("Data", 0, 0, "BoldStyle");
        // Verify the sheet still has the cell value
        Assert.Equal("Header", doc.GetCellValue("Data", 0, 0));
    }

    [Fact]
    public void DogfoodPipeline_SetCellStyle_Idempotent()
    {
        var doc = MakeDocWithCell();
        doc.SetCellStyle("Sheet1", 0, 0, "StyleA");
        // Calling again should not throw
        doc.SetCellStyle("Sheet1", 0, 0, "StyleB");
        Assert.Equal("Value", doc.GetCellValue("Sheet1", 0, 0));
    }
}
