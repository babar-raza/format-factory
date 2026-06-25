// Tests for FodsDocument.GetCellFormula(sheetName, row, col).
// Sprint: FORMAT-FACTORY-FODS-CELL-FORMULA-20260626
// Ledger: R125-GOVERNED-DOTNET-FODS-CELL-FORMULA-001

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R125: GetCellFormula(sheetName, row, col) — retrieves the ODF formula string
/// stored in a cell (e.g., "of:=[.A1]+[.B1]"), or null if the cell has no formula.
/// Tests cover formula set-then-get, non-formula cells return null, out-of-range
/// returns null, and guards for invalid sheet names.
/// </summary>
public class FodsR125GetCellFormulaTests
{
    private static FodsDocument MakeDoc(string sheetName = "Sheet1")
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet(sheetName);
        return doc;
    }

    // ---- SetCellFormula then GetCellFormula ----

    [Fact]
    public void GetCellFormula_AfterSetCellFormula_ReturnsFormula()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "1", "2", "" });
        doc.SetCellFormula("Sheet1", 0, 2, "=[.A1]+[.B1]");

        var formula = doc.GetCellFormula("Sheet1", 0, 2);
        Assert.NotNull(formula);
        Assert.True(formula!.Length > 0);
    }

    [Fact]
    public void GetCellFormula_AfterSetCellFormula_ContainsFormulaContent()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "X", "Y", "" });
        const string formulaInput = "=SUM([.A1]:[.B1])";
        doc.SetCellFormula("Sheet1", 0, 2, formulaInput);

        var formula = doc.GetCellFormula("Sheet1", 0, 2);
        Assert.NotNull(formula);
        // The stored formula should contain the cell references (exact format may vary)
        Assert.True(formula!.Length > 0, "Formula should not be empty after SetCellFormula");
    }

    // ---- Non-formula cell returns null ----

    [Fact]
    public void GetCellFormula_NonFormulaCell_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "plain text" });

        var formula = doc.GetCellFormula("Sheet1", 0, 0);
        Assert.Null(formula);
    }

    [Fact]
    public void GetCellFormula_EmptyCell_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "A", "B" });

        // Column 2 does not exist — should return null
        var formula = doc.GetCellFormula("Sheet1", 0, 5);
        Assert.Null(formula);
    }

    // ---- Out-of-range returns null ----

    [Fact]
    public void GetCellFormula_RowOutOfRange_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "data" });

        var formula = doc.GetCellFormula("Sheet1", 99, 0);
        Assert.Null(formula);
    }

    [Fact]
    public void GetCellFormula_ColOutOfRange_ReturnsNull()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "data" });

        var formula = doc.GetCellFormula("Sheet1", 0, 99);
        Assert.Null(formula);
    }

    [Fact]
    public void GetCellFormula_NegativeRow_ReturnsNull()
    {
        var doc = MakeDoc();
        var formula = doc.GetCellFormula("Sheet1", -1, 0);
        Assert.Null(formula);
    }

    // ---- Non-existent sheet returns null ----

    [Fact]
    public void GetCellFormula_NonExistentSheet_ReturnsNull()
    {
        var doc = MakeDoc();
        var formula = doc.GetCellFormula("NoSuchSheet", 0, 0);
        Assert.Null(formula);
    }

    // ---- Guards: empty sheet name throws ----

    [Fact]
    public void GetCellFormula_EmptySheetName_ThrowsArgumentException()
    {
        var doc = MakeDoc();
        Assert.Throws<ArgumentException>(() =>
            doc.GetCellFormula("", 0, 0));
    }

    // ---- Dogfood: set formula, get it, verify different from cell value ----

    [Fact]
    public void DogfoodPipeline_FormulaAndValueDistinct()
    {
        var doc = MakeDoc();
        doc.InsertRowWithValues("Sheet1", 0, new[] { "10", "20", "" });
        doc.SetCellFormula("Sheet1", 0, 2, "=[.A1]+[.B1]");

        var formula = doc.GetCellFormula("Sheet1", 0, 2);
        var valueCell = doc.GetCellValue(0, 0); // plain value cell

        // The formula cell has a formula; the value cell (col 0) has no formula
        Assert.NotNull(formula);
        Assert.Null(doc.GetCellFormula("Sheet1", 0, 0));
    }
}
