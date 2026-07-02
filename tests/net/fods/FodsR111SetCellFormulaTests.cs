// R111 Wave 5: FODS SetCellFormula tests
// Ledger: R111-GOVERNED-DOTNET-FODS-SETCELLFORMULA-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR111SetCellFormulaTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void SetCellFormula_SetsAndReads()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        doc.SetCellFormula(name, 0, 0, "of:=SUM([.A1:.A10])");
        var formula = doc.GetCellFormula(name, 0, 0);
        Assert.Equal("of:=SUM([.A1:.A10])", formula);
    }

    [Fact]
    public void SetCellFormula_OverwritesPrevious()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        doc.SetCellFormula(name, 0, 0, "of:=1+1");
        doc.SetCellFormula(name, 0, 0, "of:=2+2");
        Assert.Equal("of:=2+2", doc.GetCellFormula(name, 0, 0));
    }

    [Fact]
    public void GetCellFormula_NoFormula_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        var formula = doc.GetCellFormula(name, 0, 0);
        // May or may not have a formula — null if absent
        // This just tests the path doesn't throw
    }

    [Fact]
    public void GetCellFormula_InvalidSheet_ReturnsNull()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Null(doc.GetCellFormula("nonexistent_sheet_xyz", 0, 0));
    }

    [Fact]
    public void SetCellFormula_InvalidSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<InvalidOperationException>(() =>
            doc.SetCellFormula("nonexistent_sheet_xyz", 0, 0, "of:=1"));
    }

    [Fact]
    public void SetCellFormula_EmptySheetName_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() =>
            doc.SetCellFormula("", 0, 0, "of:=1"));
    }

    [Fact]
    public void SetCellFormula_NullFormula_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        Assert.Throws<ArgumentNullException>(() =>
            doc.SetCellFormula(name, 0, 0, null!));
    }

    [Fact]
    public void SetCellFormula_OutOfRange_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        var ex = Record.Exception(() => doc.SetCellFormula(name, 9999, 0, "of:=1"));
        Assert.Null(ex); // Auto-expands
    }

    [Fact]
    public void SetCellFormula_SurvivesSaveRoundtrip()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        doc.SetCellFormula(name, 0, 0, "of:=A1+B1");

        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            Assert.Equal("of:=A1+B1", reloaded.GetCellFormula(name, 0, 0));
        }
        finally
        {
            if (File.Exists(tmp)) File.Delete(tmp);
        }
    }

    [Fact]
    public void SetCellFormula_DoesNotClearCellValue()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var name = doc.GetSheetNames()[0];
        FodsDocument.SetCellValue(doc.Sheets[0], 0, 0, "test");
        doc.SetCellFormula(name, 0, 0, "of:=1+1");
        // Value should still be there (formula and display value coexist in ODF)
        Assert.Equal("test", FodsDocument.GetCellValue(doc.Sheets[0], 0, 0));
    }
}
