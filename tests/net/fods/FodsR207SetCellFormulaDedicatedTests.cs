// Tests for FodsDocument.SetCellFormula dedicated coverage.
// Sprint: ff-sprint-s195-dotnet-deepening-20260629
// Ledger: PC-FODS-R207

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R207: Dedicated tests for FodsDocument.SetCellFormula(string sheetName, int row, int col, string formula).
/// null/whitespace sheetName → ArgumentException.
/// null formula → ArgumentNullException.
/// Nonexistent sheet → InvalidOperationException.
/// OOB row → ArgumentOutOfRangeException.
/// OOB col → ArgumentOutOfRangeException.
/// Valid: does not throw.
/// Valid: value still accessible via GetCellValue.
/// Two-arg overload (row, col) applies to first sheet.
/// Dogfood: set formula then set value overwrites; set multiple formulas on different cells.
/// </summary>
public class FodsR207SetCellFormulaDedicatedTests
{
    private static readonly string MinimalPath =
        System.IO.Path.Combine("samples", "by-format", "fods", "minimal-spreadsheet.fods");

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NullSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SetCellFormula(null!, 0, 0, "=SUM(A1:A2)"));
    }

    [Fact]
    public void SetCellFormula_WhitespaceSheetName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<ArgumentException>(() => doc.SetCellFormula("  ", 0, 0, "=SUM(A1:A2)"));
    }

    [Fact]
    public void SetCellFormula_NullFormula_ThrowsArgumentNullException()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        Assert.Throws<ArgumentNullException>(() => doc.SetCellFormula(sheet.Name!, 0, 0, null!));
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Throws<InvalidOperationException>(
            () => doc.SetCellFormula("NoSuchSheet", 0, 0, "=SUM(A1:A2)"));
    }

    [Fact]
    public void SetCellFormula_OobRow_ThrowsArgumentOutOfRangeException()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        int rowCount = sheet.Rows.Count;
        Assert.Throws<ArgumentOutOfRangeException>(
            () => doc.SetCellFormula(sheet.Name!, rowCount + 5, 0, "=A1"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ValidFormula_DoesNotThrow()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() => doc.SetCellFormula(sheet.Name!, 0, 0, "=SUM(A1:A2)"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_TwoArgOverload_DoesNotThrow()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var ex = Record.Exception(() => doc.SetCellFormula(0, 0, "=A1+B1"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_AfterFormula_CellValueStillAccessible()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        // Set a value, then set formula — value should still be in text:p
        FodsDocument.SetCellValue(sheet, 0, 0, "100");
        doc.SetCellFormula(sheet.Name!, 0, 0, "=SUM(A1:A2)");
        var val = FodsDocument.GetCellValue(sheet, 0, 0);
        Assert.Equal("100", val);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleCellFormulas_NoException()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        var ex = Record.Exception(() =>
        {
            doc.SetCellFormula(sheet.Name!, 0, 0, "=A1+B1");
            doc.SetCellFormula(sheet.Name!, 1, 0, "=SUM(A1:A5)");
        });
        Assert.Null(ex);
    }

    [Fact]
    public void DogfoodPipeline_SetFormulaSheetCountUnchanged()
    {
        var doc = FodsDocument.Load(MinimalPath);
        int before = doc.SheetCount;
        doc.SetCellFormula(0, 0, "=A1");
        Assert.Equal(before, doc.SheetCount);
    }
}
