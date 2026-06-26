// Tests for FodsDocument.GetCellFormula dedicated coverage.
// Sprint: ff-sprint-s173-dotnet-deepening-20260628
// Ledger: PC-FODS-R180

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R180: Dedicated tests for FodsDocument.GetCellFormula(string sheetName, int row, int col).
/// Returns the table:formula attribute of the cell, or null if:
///   - the sheet does not exist (returns null, does NOT throw)
///   - the row index is out of range (returns null)
///   - the col index is out of range (returns null)
///   - the cell has no formula attribute (returns null)
/// Throws ArgumentException for null or whitespace sheetName.
/// SetCellFormula can be used to set a formula; GetCellFormula reads it back.
/// Covers: null sheetName throws; whitespace sheetName throws;
/// nonexistent sheet returns null; negative row returns null;
/// negative col returns null; row-at-count returns null;
/// col-at-count returns null; plain cell returns null;
/// SetCellFormula then GetCellFormula returns formula;
/// dogfood multi-cell formula roundtrip.
/// </summary>
public class FodsR180GetCellFormulaDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests — throws
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetCellFormula(null!, 0, 0));
    }

    [Fact]
    public void GetCellFormula_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Throws<ArgumentException>(() => doc.GetCellFormula("   ", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Guard tests — null return (no throw)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NonexistentSheet_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        Assert.Null(doc.GetCellFormula("NoSuchSheet", 0, 0));
    }

    [Fact]
    public void GetCellFormula_NegativeRow_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        Assert.Null(doc.GetCellFormula("Data", -1, 0));
    }

    [Fact]
    public void GetCellFormula_NegativeCol_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        Assert.Null(doc.GetCellFormula("Data", 0, -1));
    }

    [Fact]
    public void GetCellFormula_RowAtCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        var count = doc.GetRowCount("Data");
        Assert.Null(doc.GetCellFormula("Data", count, 0));
    }

    [Fact]
    public void GetCellFormula_ColAtCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "val");
        var count = doc.GetColumnCount("Data");
        Assert.Null(doc.GetCellFormula("Data", 0, count));
    }

    [Fact]
    public void GetCellFormula_PlainCell_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.SetCellValue(0, 0, "hello");
        // Plain string cell has no formula
        Assert.Null(doc.GetCellFormula("Data", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline — SetCellFormula then GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetCellFormula_GetCellFormula_ReturnsFormula()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "10");
        doc.SetCellValue(1, 0, "20");
        doc.SetCellFormula("Sheet1", 2, 0, "=SUM(A1:A2)");
        var formula = doc.GetCellFormula("Sheet1", 2, 0);
        // Formula should be stored
        Assert.NotNull(formula);
        Assert.Contains("SUM", formula);
    }

    [Fact]
    public void DogfoodPipeline_MultiCell_FormulaRoundtrip()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Calc");
        doc.SetCellFormula("Calc", 0, 0, "=1+1");
        doc.SetCellFormula("Calc", 1, 0, "=A1*2");
        var f0 = doc.GetCellFormula("Calc", 0, 0);
        var f1 = doc.GetCellFormula("Calc", 1, 0);
        Assert.NotNull(f0);
        Assert.NotNull(f1);
    }
}
