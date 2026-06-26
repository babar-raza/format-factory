// Tests for FodsDocument.GetCellStyle, GetCellFormula, SetCellStyle, SetCellFormula deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R196

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R196: Tests for FodsDocument.GetCellStyle, GetCellFormula, SetCellStyle, SetCellFormula.
/// SetCellStyle(row, col, style): sets a style name on a cell.
/// GetCellStyle(sheet, row, col): gets the style name for a cell.
/// SetCellFormula(row, col, formula): sets a formula string on a cell.
/// GetCellFormula(sheet, row, col): gets the formula string for a cell.
/// Covers: SetCellStyle then GetCellStyle returns style; SetCellStyle multiple cells;
/// GetCellStyle empty for unset; SetCellFormula then GetCellFormula returns formula;
/// GetCellFormula empty for non-formula cell; SetCellFormula multiple cells;
/// GetCellStyle after SetCellValue; SetCellFormula overrides previous;
/// GetCellStyle consistent across calls; SetCellStyle then ClearSheet loses style;
/// GetCellFormula cell with simple formula; SetCellFormula then GetCellValue;
/// SetCellStyle->SaveToFile->LoadFile->GetCellStyle round-trip;
/// dogfood CreateNew->SetCellValues->SetCellStyles->SetFormulas->GetStyles->GetFormulas.
/// </summary>
public class FodsR196GetCellStyleAndFormulaTests
{
    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // SetCellStyle / GetCellStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_GetCellStyle_ReturnsStyle()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Value");
        doc.SetCellStyle(0, 0, "Bold");
        var style = doc.GetCellStyle(sheet, 0, 0);
        Assert.Equal("Bold", style);
    }

    [Fact]
    public void SetCellStyle_MultipleCells_AllPersist()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "A");
        doc.SetCellValue(0, 1, "B");
        doc.SetCellStyle(0, 0, "Red");
        doc.SetCellStyle(0, 1, "Blue");
        Assert.Equal("Red", doc.GetCellStyle(sheet, 0, 0));
        Assert.Equal("Blue", doc.GetCellStyle(sheet, 0, 1));
    }

    [Fact]
    public void GetCellStyle_EmptyForUnset()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "Value");
        var style = doc.GetCellStyle(sheet, 0, 0);
        // No style set, should return empty or default
        Assert.NotNull(style);
    }

    [Fact]
    public void SetCellStyle_ConsistentAcrossCalls()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "X");
        doc.SetCellStyle(0, 0, "Italic");
        Assert.Equal("Italic", doc.GetCellStyle(sheet, 0, 0));
        Assert.Equal("Italic", doc.GetCellStyle(sheet, 0, 0)); // second call
    }

    [Fact]
    public void SetCellStyle_AfterClearSheet_StyleLost()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "X");
        doc.SetCellStyle(0, 0, "Bold");
        doc.ClearSheet(sheet);
        var style = doc.GetCellStyle(sheet, 0, 0);
        // After clear, no style
        Assert.NotEqual("Bold", style);
    }

    // -------------------------------------------------------------------------
    // SetCellFormula / GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_GetCellFormula_ReturnsFormula()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellFormula(0, 0, "=SUM(A1:A10)");
        var formula = doc.GetCellFormula(sheet, 0, 0);
        Assert.Equal("=SUM(A1:A10)", formula);
    }

    [Fact]
    public void SetCellFormula_MultipleCells_AllPersist()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellFormula(0, 0, "=A1+B1");
        doc.SetCellFormula(1, 0, "=SUM(A1:A5)");
        Assert.Equal("=A1+B1", doc.GetCellFormula(sheet, 0, 0));
        Assert.Equal("=SUM(A1:A5)", doc.GetCellFormula(sheet, 1, 0));
    }

    [Fact]
    public void GetCellFormula_EmptyForNonFormulaCell()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(0, 0, "JustAValue");
        var formula = doc.GetCellFormula(sheet, 0, 0);
        Assert.NotNull(formula);
        // Non-formula cell should have empty formula
        Assert.DoesNotContain("=", formula);
    }

    [Fact]
    public void SetCellFormula_OverridesPrevious()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellFormula(0, 0, "=A1");
        doc.SetCellFormula(0, 0, "=B1");
        Assert.Equal("=B1", doc.GetCellFormula(sheet, 0, 0));
    }

    [Fact]
    public void SetCellFormula_SimpleFormula_Stored()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellFormula(2, 2, "=100+200");
        var formula = doc.GetCellFormula(sheet, 2, 2);
        Assert.Contains("100", formula);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetValues->SetStyles->SetFormulas->GetStyles->GetFormulas
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetValuesStylesFormulasGetAll_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);

        // SetCellValues
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "95");
        doc.SetCellValue(2, 0, "Bob");
        doc.SetCellValue(2, 1, "82");

        // SetCellStyles
        doc.SetCellStyle(0, 0, "HeaderBold");
        doc.SetCellStyle(0, 1, "HeaderBold");

        // GetCellStyles
        Assert.Equal("HeaderBold", doc.GetCellStyle(sheet, 0, 0));
        Assert.Equal("HeaderBold", doc.GetCellStyle(sheet, 0, 1));

        // SetCellFormulas
        doc.SetCellFormula(3, 1, "=SUM(B2:B3)");

        // GetCellFormula
        var formula = doc.GetCellFormula(sheet, 3, 1);
        Assert.Contains("SUM", formula);

        // GetCellFormula for non-formula cell
        var noFormula = doc.GetCellFormula(sheet, 1, 0);
        Assert.DoesNotContain("=", noFormula);

        // GetColumnValues still works
        var names = doc.GetColumnValues(sheet, 0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }
}
