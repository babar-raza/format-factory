// Tests for FodsDocument.GetRowValues dedicated coverage.
// Sprint: ff-sprint-s167-dotnet-deepening-20260628
// Ledger: PC-FODS-R174

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R174: Dedicated tests for FodsDocument.GetRowValues(int row) and GetRowValues(string sheetName, int row).
/// GetRowValues returns all cell values from the specified row as nullable strings.
/// No-arg overload throws ArgumentOutOfRangeException if document has no sheets.
/// Named overload throws ArgumentException if sheet not found.
/// Both overloads throw ArgumentOutOfRangeException for invalid row index.
/// Covers: no-sheet (no-arg) throws ArgumentOutOfRangeException; named nonexistent throws ArgumentException;
/// negative row throws ArgumentOutOfRangeException; row beyond count throws;
/// single row single cell returns one value; multiple cells all returned;
/// result count matches cell count; returns IReadOnlyList;
/// dogfood CreateNew->AddSheet->SetCellValue->GetRowValues pipeline;
/// dogfood named and unnamed return same for first sheet first row.
/// </summary>
public class FodsR174GetRowValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_NoSheets_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues(0));
    }

    [Fact]
    public void GetRowValues_NamedNonexistentSheet_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetRowValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetRowValues_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues("Sheet1", -1));
    }

    [Fact]
    public void GetRowValues_RowBeyondCount_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues("Sheet1", 5));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_SingleCell_ReturnsOneItem()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "OnlyCell");
        var result = doc.GetRowValues("Sheet1", 0);
        Assert.Single(result);
    }

    [Fact]
    public void GetRowValues_MultipleCells_AllReturned()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet1", 0, 1, "B");
        doc.SetCellValue("Sheet1", 0, 2, "C");
        var result = doc.GetRowValues("Sheet1", 0);
        Assert.Equal(3, result.Count);
    }

    [Fact]
    public void GetRowValues_ReturnsIReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "X");
        var result = doc.GetRowValues("Sheet1", 0);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<string?>>(result);
    }

    [Fact]
    public void GetRowValues_ResultCountMatchesCellCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Col1");
        doc.SetCellValue("Data", 0, 1, "Col2");
        var result = doc.GetRowValues("Data", 0);
        var sheet = doc.GetSheetByName("Data")!;
        Assert.Equal(sheet.Rows[0].Cells.Count, result.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_GetRowValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.SetCellValue("Report", 0, 0, "Name");
        doc.SetCellValue("Report", 0, 1, "Score");
        var result = doc.GetRowValues("Report", 0);
        Assert.Equal(2, result.Count);
    }

    [Fact]
    public void DogfoodPipeline_NamedAndUnnamed_SameForFirstSheetFirstRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Value1");
        doc.SetCellValue("Sheet1", 0, 1, "Value2");
        var unnamed = doc.GetRowValues(0);
        var named = doc.GetRowValues("Sheet1", 0);
        Assert.Equal(unnamed.Count, named.Count);
    }
}
