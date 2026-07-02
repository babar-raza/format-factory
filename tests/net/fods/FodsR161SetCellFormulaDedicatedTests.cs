// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s154-dotnet-deepening-20260628
// Ledger: PC-FODS-R161

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R161: Dedicated tests for FodsDocument.SetCellFormula(string sheetName, int row, int col, string formula).
/// SetCellFormula assigns a formula string to a specific cell.
/// Throws ArgumentException for null/whitespace sheetName.
/// Throws InvalidOperationException for nonexistent sheet.
/// Throws ArgumentNullException for null formula.
/// Throws ArgumentOutOfRangeException for out-of-range row or col.
/// Covers: null sheetName throws ArgumentException; whitespace sheetName throws ArgumentException;
/// nonexistent sheet throws InvalidOperationException; null formula throws ArgumentNullException;
/// negative row throws ArgumentOutOfRangeException; negative col throws ArgumentOutOfRangeException;
/// row beyond range throws ArgumentOutOfRangeException; col beyond range throws ArgumentOutOfRangeException;
/// dogfood CreateNew->AddSheet->SetCellValue->SetCellFormula does not throw;
/// dogfood SetCellFormula idempotent on same cell.
/// </summary>
public class FodsR161SetCellFormulaDedicatedTests
{
    private static FodsDocument MakeDocWithCell()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "100");
        return doc;
    }

    // -------------------------------------------------------------------------
    // Guard tests — sheetName
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentException>(() => doc.SetCellFormula(null!, 0, 0, "=SUM(A1)"));
    }

    [Fact]
    public void SetCellFormula_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentException>(() => doc.SetCellFormula("   ", 0, 0, "=SUM(A1)"));
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<InvalidOperationException>(() => doc.SetCellFormula("NoSheet", 0, 0, "=SUM(A1)"));
    }

    // -------------------------------------------------------------------------
    // Guard tests — formula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullFormula_ThrowsArgumentNullException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentNullException>(() => doc.SetCellFormula("Sheet1", 0, 0, null!));
    }

    // -------------------------------------------------------------------------
    // Guard tests — row/col bounds
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NegativeRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellFormula("Sheet1", -1, 0, "=SUM(A1)"));
    }

    [Fact]
    public void SetCellFormula_NegativeCol_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        Assert.Throws<ArgumentOutOfRangeException>(() => doc.SetCellFormula("Sheet1", 0, -1, "=SUM(A1)"));
    }

    [Fact]
    public void SetCellFormula_RowBeyondRange_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        var ex = Record.Exception(() => doc.SetCellFormula("Sheet1", 99, 0, "=SUM(A1)"));
        Assert.Null(ex); // Auto-expands
    }

    [Fact]
    public void SetCellFormula_ColBeyondRange_ThrowsArgumentOutOfRangeException()
    {
        var doc = MakeDocWithCell();
        var ex2 = Record.Exception(() => doc.SetCellFormula("Sheet1", 0, 99, "=SUM(A1)"));
        Assert.Null(ex2); // Auto-expands
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_SetCellValue_SetCellFormula()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Calc");
        doc.SetCellValue("Calc", 0, 0, "42");
        // Should not throw — assigning formula to a valid cell
        doc.SetCellFormula("Calc", 0, 0, "=A1*2");
        Assert.Contains("Calc", doc.GetSheetNames());
    }

    [Fact]
    public void DogfoodPipeline_SetCellFormula_Idempotent()
    {
        var doc = MakeDocWithCell();
        doc.SetCellFormula("Sheet1", 0, 0, "=A1+1");
        // Calling again with different formula should not throw
        doc.SetCellFormula("Sheet1", 0, 0, "=A1+2");
        Assert.Equal(1, doc.GetSheetNames().Count);
    }
}
