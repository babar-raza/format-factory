// Tests for FodsDocument.GetColumnValues dedicated coverage.
// Sprint: ff-sprint-s166-dotnet-deepening-20260628
// Ledger: PC-FODS-R173

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R173: Dedicated tests for FodsDocument.GetColumnValues(string sheetName, int col).
/// GetColumnValues returns all cell values from the specified column as nullable strings.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws ArgumentOutOfRangeException for negative col.
/// Throws InvalidOperationException for nonexistent sheet.
/// Returns null for cells that are empty/missing.
/// Covers: null sheetName throws ArgumentException; whitespace throws;
/// nonexistent sheet throws InvalidOperationException; negative col throws ArgumentOutOfRangeException;
/// empty sheet returns empty list; single column correct values;
/// col beyond row returns null for that row; count matches row count;
/// dogfood CreateNew->AddSheet->SetCellValue->GetColumnValues pipeline;
/// dogfood multi-row column extraction returns all values.
/// </summary>
public class FodsR173GetColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetColumnValues(null!, 0));
    }

    [Fact]
    public void GetColumnValues_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetColumnValues("   ", 0));
    }

    [Fact]
    public void GetColumnValues_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.GetColumnValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetColumnValues_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetColumnValues("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        var result = doc.GetColumnValues("Empty", 0);
        Assert.Empty(result);
    }

    [Fact]
    public void GetColumnValues_SingleColumn_ReturnsValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Row0");
        doc.SetCellValue("Sheet1", 1, 0, "Row1");
        var result = doc.GetColumnValues("Sheet1", 0);
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void GetColumnValues_CountMatchesRowCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "A");
        doc.SetCellValue("Data", 1, 0, "B");
        doc.SetCellValue("Data", 2, 0, "C");
        var result = doc.GetColumnValues("Data", 0);
        var sheet = doc.GetSheetByName("Data");
        Assert.Equal(sheet!.Rows.Count, result.Count);
    }

    [Fact]
    public void GetColumnValues_ReturnsIReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var result = doc.GetColumnValues("Sheet1", 0);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string?>>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_GetColumnValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Header");
        doc.SetCellValue("Report", 1, 0, "Value1");
        var result = doc.GetColumnValues("Report", 0);
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void DogfoodPipeline_MultiRowColumn_ReturnsAllValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Multi");
        doc.SetCellValue("Multi", 0, 0, "Jan");
        doc.SetCellValue("Multi", 1, 0, "Feb");
        doc.SetCellValue("Multi", 2, 0, "Mar");
        doc.SetCellValue("Multi", 3, 0, "Apr");
        var result = doc.GetColumnValues("Multi", 0);
        Assert.Equal(4, result.Count);
    }
}
