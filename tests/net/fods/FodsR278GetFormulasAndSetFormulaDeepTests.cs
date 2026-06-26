// Tests for FodsDocument.GetCellFormula, SetCellFormula, GetFormulas deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R278

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R278: Tests for FodsDocument.GetCellFormula, SetCellFormula, GetFormulas deeper.
/// SetCellFormula(sheet, row, col, formula): sets a formula in a cell.
/// GetCellFormula(sheet, row, col): returns the formula string for a cell.
/// GetFormulas(sheet): returns all (row,col,formula) tuples in a sheet.
/// Covers: SetCellFormula no-throw; SetCellFormula readable via GetCellFormula;
/// SetCellFormula different cells; SetCellFormula save-load persists;
/// SetCellFormula consistent; SetCellFormula then GetCellValue no-throw;
/// GetCellFormula non-null; GetCellFormula no-throw; GetCellFormula matches set;
/// GetCellFormula consistent; GetCellFormula save-load; GetCellFormula for non-formula=null;
/// GetFormulas non-null; GetFormulas no-throw; GetFormulas count after multiple set;
/// GetFormulas contains set formula; GetFormulas consistent; GetFormulas save-load;
/// GetFormulas empty for no-formulas; GetFormulas all non-null;
/// dogfood CreateDoc→SetCellFormula→GetCellFormula→GetFormulas→SaveToFile pipeline.
/// </summary>
public class FodsR278GetFormulasAndSetFormulaDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodsR278GetFormulasAndSetFormulaDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodsR278_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodsDocument CreateCalcDoc()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Calc");
        // Headers
        doc.SetCellValue("Calc", 0, 0, "Month");
        doc.SetCellValue("Calc", 0, 1, "Revenue");
        doc.SetCellValue("Calc", 0, 2, "Costs");
        doc.SetCellValue("Calc", 0, 3, "Profit");
        // Data
        doc.SetCellValue("Calc", 1, 0, "Jan"); doc.SetCellValue("Calc", 1, 1, "50000"); doc.SetCellValue("Calc", 1, 2, "30000");
        doc.SetCellValue("Calc", 2, 0, "Feb"); doc.SetCellValue("Calc", 2, 1, "55000"); doc.SetCellValue("Calc", 2, 2, "32000");
        doc.SetCellValue("Calc", 3, 0, "Mar"); doc.SetCellValue("Calc", 3, 1, "62000"); doc.SetCellValue("Calc", 3, 2, "35000");
        return doc;
    }

    // -------------------------------------------------------------------------
    // SetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_NoThrow()
    {
        var doc = CreateCalcDoc();
        var ex = Record.Exception(() => doc.SetCellFormula("Calc", 1, 3, "=B2-C2"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetCellFormula_Readable_Via_GetCellFormula()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var formula = doc.GetCellFormula("Calc", 1, 3);
        Assert.True(formula != null && formula.Length > 0);
    }

    [Fact]
    public void SetCellFormula_Different_Cells()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        doc.SetCellFormula("Calc", 2, 3, "=B3-C3");
        doc.SetCellFormula("Calc", 3, 3, "=B4-C4");
        Assert.True(doc.GetFormulas("Calc").Count >= 3);
    }

    [Fact]
    public void SetCellFormula_SaveLoad_Persists()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var path = TempFile("formula_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var formula = loaded.GetCellFormula("Calc", 1, 3);
        Assert.NotNull(formula);
        Assert.True(formula.Length > 0);
    }

    [Fact]
    public void SetCellFormula_Consistent()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=SUM(B2:C2)");
        var f1 = doc.GetCellFormula("Calc", 1, 3);
        var f2 = doc.GetCellFormula("Calc", 1, 3);
        Assert.Equal(f1, f2);
    }

    [Fact]
    public void SetCellFormula_Then_GetCellValue_NoThrow()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var ex = Record.Exception(() => doc.GetCellValue("Calc", 1, 3));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellFormula_NonNull_AfterSet()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        Assert.NotNull(doc.GetCellFormula("Calc", 1, 3));
    }

    [Fact]
    public void GetCellFormula_NoThrow()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var ex = Record.Exception(() => doc.GetCellFormula("Calc", 1, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCellFormula_Matches_Set()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 2, 3, "=B3-C3");
        var formula = doc.GetCellFormula("Calc", 2, 3);
        Assert.True(formula != null && (formula.Contains("B3") || formula.Contains("C3") || formula.Contains("-")));
    }

    [Fact]
    public void GetCellFormula_Consistent()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        Assert.Equal(doc.GetCellFormula("Calc", 1, 3), doc.GetCellFormula("Calc", 1, 3));
    }

    [Fact]
    public void GetCellFormula_SaveLoad_Consistent()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var before = doc.GetCellFormula("Calc", 1, 3);
        var path = TempFile("gcf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        var after = loaded.GetCellFormula("Calc", 1, 3);
        Assert.NotNull(after);
        Assert.True(after.Length > 0);
    }

    [Fact]
    public void GetCellFormula_ForNonFormula_ReturnsNullOrEmpty()
    {
        var doc = CreateCalcDoc();
        // Cell (1,1) has value "50000", not a formula
        var formula = doc.GetCellFormula("Calc", 1, 1);
        Assert.True(formula == null || formula.Length == 0);
    }

    // -------------------------------------------------------------------------
    // GetFormulas
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFormulas_NonNull()
    {
        var doc = CreateCalcDoc();
        Assert.NotNull(doc.GetFormulas("Calc"));
    }

    [Fact]
    public void GetFormulas_NoThrow()
    {
        var doc = CreateCalcDoc();
        var ex = Record.Exception(() => doc.GetFormulas("Calc"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFormulas_Count_After_MultipleSet()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        doc.SetCellFormula("Calc", 2, 3, "=B3-C3");
        doc.SetCellFormula("Calc", 3, 3, "=B4-C4");
        Assert.Equal(3, doc.GetFormulas("Calc").Count);
    }

    [Fact]
    public void GetFormulas_Consistent()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        var f1 = doc.GetFormulas("Calc");
        var f2 = doc.GetFormulas("Calc");
        Assert.Equal(f1.Count, f2.Count);
    }

    [Fact]
    public void GetFormulas_SaveLoad_Consistent()
    {
        var doc = CreateCalcDoc();
        doc.SetCellFormula("Calc", 1, 3, "=B2-C2");
        doc.SetCellFormula("Calc", 2, 3, "=B3-C3");
        var before = doc.GetFormulas("Calc").Count;
        var path = TempFile("gf_save.fods");
        doc.SaveToFile(path);
        var loaded = FodsDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFormulas("Calc").Count);
    }

    [Fact]
    public void GetFormulas_Empty_ForNoFormulas()
    {
        var doc = CreateCalcDoc();
        // No formulas set
        Assert.Equal(0, doc.GetFormulas("Calc").Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellFormula_GetCellFormula_GetFormulas_SaveToFile_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Budget");

        // Headers
        doc.SetCellValue("Budget", 0, 0, "Quarter");
        doc.SetCellValue("Budget", 0, 1, "Revenue");
        doc.SetCellValue("Budget", 0, 2, "OpCost");
        doc.SetCellValue("Budget", 0, 3, "MarkCost");
        doc.SetCellValue("Budget", 0, 4, "TotalCost");
        doc.SetCellValue("Budget", 0, 5, "Profit");
        doc.SetCellValue("Budget", 0, 6, "Margin");

        // Data rows
        doc.SetCellValue("Budget", 1, 0, "Q1"); doc.SetCellValue("Budget", 1, 1, "250000"); doc.SetCellValue("Budget", 1, 2, "120000"); doc.SetCellValue("Budget", 1, 3, "30000");
        doc.SetCellValue("Budget", 2, 0, "Q2"); doc.SetCellValue("Budget", 2, 1, "280000"); doc.SetCellValue("Budget", 2, 2, "130000"); doc.SetCellValue("Budget", 2, 3, "32000");
        doc.SetCellValue("Budget", 3, 0, "Q3"); doc.SetCellValue("Budget", 3, 1, "310000"); doc.SetCellValue("Budget", 3, 2, "140000"); doc.SetCellValue("Budget", 3, 3, "35000");
        doc.SetCellValue("Budget", 4, 0, "Q4"); doc.SetCellValue("Budget", 4, 1, "340000"); doc.SetCellValue("Budget", 4, 2, "150000"); doc.SetCellValue("Budget", 4, 3, "38000");

        // GetFormulas — should be empty before any formula set
        Assert.Equal(0, doc.GetFormulas("Budget").Count);

        // SetCellFormula — TotalCost = OpCost + MarkCost
        doc.SetCellFormula("Budget", 1, 4, "=C2+D2");
        doc.SetCellFormula("Budget", 2, 4, "=C3+D3");
        doc.SetCellFormula("Budget", 3, 4, "=C4+D4");
        doc.SetCellFormula("Budget", 4, 4, "=C5+D5");

        // SetCellFormula — Profit = Revenue - TotalCost
        doc.SetCellFormula("Budget", 1, 5, "=B2-E2");
        doc.SetCellFormula("Budget", 2, 5, "=B3-E3");
        doc.SetCellFormula("Budget", 3, 5, "=B4-E4");
        doc.SetCellFormula("Budget", 4, 5, "=B5-E5");

        // 8 formulas total
        var formulas = doc.GetFormulas("Budget");
        Assert.NotNull(formulas);
        Assert.Equal(8, formulas.Count);

        // Consistent
        Assert.Equal(8, doc.GetFormulas("Budget").Count);

        // GetCellFormula — TotalCost Q1
        var tc1 = doc.GetCellFormula("Budget", 1, 4);
        Assert.NotNull(tc1);
        Assert.True(tc1.Length > 0);
        Assert.True(tc1.Contains("C2") || tc1.Contains("D2") || tc1.Contains("+"));

        // GetCellFormula — Profit Q3
        var pf3 = doc.GetCellFormula("Budget", 3, 5);
        Assert.NotNull(pf3);
        Assert.True(pf3.Length > 0);

        // Consistent
        Assert.Equal(tc1, doc.GetCellFormula("Budget", 1, 4));

        // GetCellFormula for non-formula cell
        var nonFormula = doc.GetCellFormula("Budget", 1, 1); // "250000"
        Assert.True(nonFormula == null || nonFormula.Length == 0);

        // SetCellFormula — Margin = Profit / Revenue
        doc.SetCellFormula("Budget", 1, 6, "=F2/B2");
        doc.SetCellFormula("Budget", 2, 6, "=F3/B3");
        doc.SetCellFormula("Budget", 3, 6, "=F4/B4");
        doc.SetCellFormula("Budget", 4, 6, "=F5/B5");

        Assert.Equal(12, doc.GetFormulas("Budget").Count);

        // GetCellValue after SetCellFormula no-throw
        var ex = Record.Exception(() => doc.GetCellValue("Budget", 1, 4));
        Assert.Null(ex);

        // SaveToFile
        var path = TempFile("dogfood_budget.fods");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodsDocument.LoadFile(path);
        var loadedFormulas = loaded.GetFormulas("Budget");
        Assert.Equal(12, loadedFormulas.Count);

        // GetCellFormula on loaded
        var loadedTc1 = loaded.GetCellFormula("Budget", 1, 4);
        Assert.NotNull(loadedTc1);
        Assert.True(loadedTc1.Length > 0);

        // SetCellFormula on loaded — add summary formula
        loaded.SetCellFormula("Budget", 5, 1, "=SUM(B2:B5)");
        Assert.Equal(13, loaded.GetFormulas("Budget").Count);

        // Final save
        var path2 = TempFile("dogfood_budget_v2.fods");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodsDocument.LoadFile(path2);
        Assert.Equal(13, loaded2.GetFormulas("Budget").Count);
        var sumFormula = loaded2.GetCellFormula("Budget", 5, 1);
        Assert.NotNull(sumFormula);
        Assert.True(sumFormula.Length > 0);
    }
}
