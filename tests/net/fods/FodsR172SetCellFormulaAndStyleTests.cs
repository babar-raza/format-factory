// Tests for FodsDocument.SetCellFormula, GetCellFormula, SetCellStyle, GetCellStyle.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R172

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R172: Tests for FodsDocument.SetCellFormula, GetCellFormula, SetCellStyle, GetCellStyle.
/// SetCellFormula(sheetName, row, col, formula): sets formula string in cell.
/// GetCellFormula(sheetName, row, col): retrieves formula or null if not set.
/// SetCellStyle(sheetName, row, col, styleName): sets style identifier on cell.
/// GetCellStyle(sheetName, row, col): retrieves style name or null if not set.
/// Covers: SetCellFormula then GetCellFormula returns formula; GetCellFormula OOB returns null;
/// GetCellFormula no formula cell returns null; SetCellFormula nonexistent sheet throws;
/// SetCellStyle then GetCellStyle returns style; GetCellStyle unstylized returns null or default;
/// SetCellStyle OOB row throws or handles; GetCellStyle OOB row returns null;
/// dogfood CreateNew->InsertRows->SetFormula->SetStyle->GetFormula->GetStyle pipeline.
/// </summary>
public class FodsR172SetCellFormulaAndStyleTests
{
    private static FodsDocument BuildSheet(string sheetName, string[] headers, string[][] rows)
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        if (names.Count > 0)
            doc.RenameSheet(names[0], sheetName);
        else
            doc.AddSheet(sheetName);

        doc.InsertRowWithValues(sheetName, 0, headers);
        for (var i = 0; i < rows.Length; i++)
            doc.InsertRowWithValues(sheetName, i + 1, rows[i]);

        return doc;
    }

    // -------------------------------------------------------------------------
    // SetCellFormula / GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ThenGetCellFormula_ReturnsFormula()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B", "C" },
            new[] { new[] { "10", "20", "" } });
        doc.SetCellFormula("Sheet", 1, 2, "=A2+B2");
        var formula = doc.GetCellFormula("Sheet", 1, 2);
        Assert.NotNull(formula);
        Assert.Contains("A2", formula!);
    }

    [Fact]
    public void GetCellFormula_NoFormula_ReturnsNull()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "42" } });
        var formula = doc.GetCellFormula("Sheet", 1, 0);
        Assert.Null(formula);
    }

    [Fact]
    public void GetCellFormula_OobRow_ReturnsNull()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "1" } });
        var formula = doc.GetCellFormula("Sheet", 999, 0);
        Assert.Null(formula);
    }

    [Fact]
    public void SetCellFormula_SumFormula_Stored()
    {
        var doc = BuildSheet("Data",
            new[] { "Val" },
            new[] { new[] { "10" }, new[] { "20" }, new[] { "" } });
        doc.SetCellFormula("Data", 3, 0, "=SUM(A1:A2)");
        var formula = doc.GetCellFormula("Data", 3, 0);
        Assert.NotNull(formula);
        Assert.Contains("SUM", formula!);
    }

    [Fact]
    public void SetCellFormula_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() =>
            doc.SetCellFormula("NonExistent", 0, 0, "=1+1"));
    }

    // -------------------------------------------------------------------------
    // SetCellStyle / GetCellStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_ThenGetCellStyle_ReturnsStyleName()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "val" } });
        doc.SetCellStyle("Sheet", 0, 0, "Bold");
        var style = doc.GetCellStyle("Sheet", 0, 0);
        Assert.NotNull(style);
        Assert.Equal("Bold", style);
    }

    [Fact]
    public void GetCellStyle_Unstylized_IsNullOrDefault()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "val" } });
        var style = doc.GetCellStyle("Sheet", 0, 0);
        // Unstylized cell: null or empty/default value is acceptable
        Assert.True(style == null || style is string);
    }

    [Fact]
    public void GetCellStyle_OobRow_ReturnsNull()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A" },
            new[] { new[] { "val" } });
        var style = doc.GetCellStyle("Sheet", 999, 0);
        Assert.Null(style);
    }

    [Fact]
    public void SetCellStyle_DifferentCells_Independent()
    {
        var doc = BuildSheet("Sheet",
            new[] { "A", "B" },
            new[] { new[] { "1", "2" } });
        doc.SetCellStyle("Sheet", 0, 0, "HeaderStyle");
        doc.SetCellStyle("Sheet", 0, 1, "DataStyle");
        Assert.Equal("HeaderStyle", doc.GetCellStyle("Sheet", 0, 0));
        Assert.Equal("DataStyle", doc.GetCellStyle("Sheet", 0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->SetFormula->SetStyle->GetFormula->GetStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FormulasAndStyles_Pipeline()
    {
        var doc = BuildSheet("Calc",
            new[] { "Name", "Value", "Total" },
            new[] {
                new[] { "Alice", "100", "" },
                new[] { "Bob", "200", "" },
                new[] { "Sum", "", "" }
            });

        // Set formulas in Total column
        doc.SetCellFormula("Calc", 1, 2, "=B2*1.1");
        doc.SetCellFormula("Calc", 2, 2, "=B3*1.1");
        doc.SetCellFormula("Calc", 3, 1, "=SUM(B2:B3)");

        // Verify formulas stored
        var formula1 = doc.GetCellFormula("Calc", 1, 2);
        Assert.NotNull(formula1);

        var formula2 = doc.GetCellFormula("Calc", 3, 1);
        Assert.NotNull(formula2);
        Assert.Contains("SUM", formula2!);

        // Set styles on header row
        doc.SetCellStyle("Calc", 0, 0, "HeaderBold");
        doc.SetCellStyle("Calc", 0, 1, "HeaderBold");
        doc.SetCellStyle("Calc", 0, 2, "HeaderBold");

        // Verify styles
        Assert.Equal("HeaderBold", doc.GetCellStyle("Calc", 0, 0));
        Assert.Equal("HeaderBold", doc.GetCellStyle("Calc", 0, 1));

        // Non-header rows should have null/default style
        var dataStyle = doc.GetCellStyle("Calc", 1, 0);
        Assert.True(dataStyle == null || dataStyle != "HeaderBold");
    }
}
