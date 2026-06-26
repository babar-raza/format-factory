// Tests for FodsDocument.GetNumericColumnValues dedicated coverage.
// Sprint: ff-sprint-s164-dotnet-deepening-20260628
// Ledger: PC-FODS-R171

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R171: Dedicated tests for FodsDocument.GetNumericColumnValues(string sheetName, int col).
/// GetNumericColumnValues returns double values from cells with office:value-type="float".
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException for nonexistent sheet.
/// Throws ArgumentOutOfRangeException for negative col.
/// Non-float cells (string, empty) are skipped (not included in result).
/// Covers: null sheetName throws ArgumentException; whitespace throws;
/// nonexistent sheet throws InvalidOperationException; negative col throws ArgumentOutOfRangeException;
/// empty sheet returns empty list; string cells are skipped;
/// column beyond row count skipped; result type is IReadOnlyList;
/// dogfood CreateNew->AddSheet->SetCellValue->GetNumericColumnValues pipeline;
/// dogfood multiple skipped non-float cells.
/// </summary>
public class FodsR171GetNumericColumnValuesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetNumericColumnValues(null!, 0));
    }

    [Fact]
    public void GetNumericColumnValues_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.GetNumericColumnValues("   ", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.GetNumericColumnValues("NoSuchSheet", 0));
    }

    [Fact]
    public void GetNumericColumnValues_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetNumericColumnValues("Sheet1", -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNumericColumnValues_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Empty");
        var result = doc.GetNumericColumnValues("Empty", 0);
        Assert.Empty(result);
    }

    [Fact]
    public void GetNumericColumnValues_StringCells_Skipped()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Text"); // string cell — should be skipped
        var result = doc.GetNumericColumnValues("Sheet1", 0);
        Assert.Empty(result);
    }

    [Fact]
    public void GetNumericColumnValues_ColBeyondRowWidth_Skipped()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "OnlyOneCol");
        var result = doc.GetNumericColumnValues("Sheet1", 5); // col 5 doesn't exist
        Assert.Empty(result);
    }

    [Fact]
    public void GetNumericColumnValues_ReturnsIReadOnlyList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var result = doc.GetNumericColumnValues("Sheet1", 0);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<double>>(result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_GetNumericColumnValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 1, 0, "Alice");
        // Columns with string values only — should return empty
        var result = doc.GetNumericColumnValues("Data", 0);
        Assert.IsAssignableFrom<System.Collections.Generic.IReadOnlyList<double>>(result);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSkippedNonFloatCells_ReturnsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Mixed");
        doc.SetCellValue("Mixed", 0, 0, "Header");
        doc.SetCellValue("Mixed", 1, 0, "SubHeader");
        doc.SetCellValue("Mixed", 2, 0, "Footer");
        var result = doc.GetNumericColumnValues("Mixed", 0);
        Assert.Empty(result);
    }
}
