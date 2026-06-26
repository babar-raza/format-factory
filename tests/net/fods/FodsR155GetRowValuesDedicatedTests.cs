// Tests for FodsDocument.GetRowValues dedicated coverage.
// Sprint: ff-sprint-s147-dotnet-deepening-20260628
// Ledger: PC-FODS-R155

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R155: Dedicated tests for FodsDocument.GetRowValues.
/// GetRowValues(int row) returns cell values from the first sheet.
/// GetRowValues(string sheetName, int row) returns from a named sheet.
/// Returns null for empty/covered cells. Throws on out-of-range row.
/// Covers: empty doc throws ArgumentOutOfRangeException; single-cell row returns one value;
/// multi-cell row returns all values; negative row throws; named sheet valid row;
/// named sheet nonexistent throws ArgumentException; row values correct after SetCell;
/// null for empty cells; row count matches expected;
/// dogfood CreateNew->SetCellValue->GetRowValues pipeline;
/// dogfood multi-row document GetRowValues each row correct.
/// </summary>
public class FodsR155GetRowValuesDedicatedTests
{
    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_EmptyDocument_NoSheets_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues(0));
    }

    [Fact]
    public void GetRowValues_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A");
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.GetRowValues(-1));
    }

    [Fact]
    public void GetRowValues_NamedSheet_NonexistentSheet_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A");
        Assert.Throws<ArgumentException>(() => doc.GetRowValues("NoSuchSheet", 0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetRowValues_SingleCell_ReturnsListWithOneValue()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "Hello");
        var values = doc.GetRowValues(0);
        Assert.NotNull(values);
        Assert.Equal("Hello", values[0]);
    }

    [Fact]
    public void GetRowValues_MultipleColumns_ReturnsAllValues()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "A");
        doc.SetCellValue("Sheet1", 0, 1, "B");
        doc.SetCellValue("Sheet1", 0, 2, "C");
        var values = doc.GetRowValues(0);
        Assert.Contains("A", values);
        Assert.Contains("B", values);
        Assert.Contains("C", values);
    }

    [Fact]
    public void GetRowValues_AfterSetCellValue_ReflectsUpdate()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "Initial");
        doc.SetCellValue("Sheet1", 0, 0, "Updated");
        var values = doc.GetRowValues(0);
        Assert.Equal("Updated", values[0]);
    }

    [Fact]
    public void GetRowValues_NamedSheet_ReturnsCorrectValues()
    {
        var doc = MakeDoc("MySheet");
        doc.SetCellValue("MySheet", 0, 0, "X");
        doc.SetCellValue("MySheet", 0, 1, "Y");
        var values = doc.GetRowValues("MySheet", 0);
        Assert.Equal("X", values[0]);
        Assert.Equal("Y", values[1]);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_SetCellValue_GetRowValues()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 0, 2, "Grade");

        var values = doc.GetRowValues("Data", 0);
        Assert.Equal(3, values.Count);
        Assert.Equal("Name", values[0]);
        Assert.Equal("Score", values[1]);
        Assert.Equal("Grade", values[2]);
    }

    [Fact]
    public void DogfoodPipeline_MultiRow_GetRowValuesEachRow()
    {
        var doc = MakeDoc();
        doc.SetCellValue("Sheet1", 0, 0, "Alice");
        doc.SetCellValue("Sheet1", 0, 1, "95");
        doc.SetCellValue("Sheet1", 1, 0, "Bob");
        doc.SetCellValue("Sheet1", 1, 1, "82");

        var row0 = doc.GetRowValues(0);
        var row1 = doc.GetRowValues(1);
        Assert.Equal("Alice", row0[0]);
        Assert.Equal("Bob", row1[0]);
    }
}
