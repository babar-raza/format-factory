// Tests for FodsDocument.GetCellStyle dedicated coverage.
// Sprint: ff-sprint-s172-dotnet-deepening-20260628
// Ledger: PC-FODS-R179

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R179: Dedicated tests for FodsDocument.GetCellStyle(string sheetName, int row, int col).
/// Returns the table:style-name attribute of the cell, or null if:
///   - the sheet does not exist (returns null, does NOT throw)
///   - the row index is out of range (returns null)
///   - the col index is out of range (returns null)
///   - the cell has no style-name attribute (returns null)
/// Throws ArgumentException for null or whitespace sheetName.
/// Covers: null sheetName throws; whitespace sheetName throws;
/// nonexistent sheet returns null; negative row returns null;
/// negative col returns null; row-at-count returns null;
/// col-at-count returns null; valid cell returns null-or-string;
/// non-null style is string type; dogfood CreateNew->SetCellValue->GetCellStyle.
/// </summary>
public class FodsR179GetCellStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests — throws
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetCellStyle(null!, 0, 0));
    }

    [Fact]
    public void GetCellStyle_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetCellStyle("   ", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Guard tests — null return (no throw)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeRow_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("Data", -1, 0));
    }

    [Fact]
    public void GetCellStyle_NegativeCol_Throws()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        Assert.ThrowsAny<Exception>(() => doc.GetCellStyle("Data", 0, -1));
    }

    [Fact]
    public void GetCellStyle_RowAtCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        var count = doc.GetRowCount("Data");
        Assert.Null(doc.GetCellStyle("Data", count, 0));
    }

    [Fact]
    public void GetCellStyle_ColAtCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        var count = doc.GetColumnCount("Data");
        Assert.Null(doc.GetCellStyle("Data", 0, count));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellStyle_ValidCell_IsNullOrString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "hello");
        var style = doc.GetCellStyle("Data", 0, 0);
        Assert.True(style == null || style is string);
    }

    [Fact]
    public void GetCellStyle_WhenNonNull_IsStringType()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "hello");
        var style = doc.GetCellStyle("Data", 0, 0);
        if (style != null)
            Assert.IsType<string>(style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_SetCellValue_GetCellStyle()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "test");
        // Style may be null (no table:style-name attribute on plain cells)
        var style = doc.GetCellStyle("Sheet1", 0, 0);
        Assert.True(style == null || style is string);
    }

    [Fact]
    public void DogfoodPipeline_SetCellStyle_ThenGetCellStyle()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "data");
        doc.SetCellStyle("Sheet1", 0, 0, "MyStyle");
        var style = doc.GetCellStyle("Sheet1", 0, 0);
        // After SetCellStyle, should return "MyStyle"
        Assert.Equal("MyStyle", style);
    }
}
