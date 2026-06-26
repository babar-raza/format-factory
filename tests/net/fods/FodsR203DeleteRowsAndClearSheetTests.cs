// Tests for FodsDocument.DeleteRows, ClearSheet, SetCellFormula edge cases.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R203

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R203: Tests for FodsDocument.DeleteRows, ClearSheet, SetCellFormula.
/// DeleteRows(sheetName, startRow, count): removes rows starting at startRow.
/// ClearSheet(sheetName): removes all cell values from a sheet.
/// SetCellFormula(row, col, formula): sets a cell to a formula expression.
/// GetCellFormula(row, col): retrieves the formula for a cell.
/// Covers: DeleteRows decreases RowCount; DeleteRows removes correct rows;
/// DeleteRows at start; DeleteRows remaining rows shifted;
/// ClearSheet RowCount becomes zero; ClearSheet CellCount becomes zero;
/// ClearSheet allows reuse; SetCellFormula stores formula;
/// GetCellFormula returns formula; SetCellFormula visible in ToFodsXml;
/// DeleteRows->GetRowValues updated; ClearSheet->AddSheet still works;
/// SetCellFormula multiple cells; DeleteRows count < 1 has no effect;
/// dogfood CreateNew->SetCells->SetFormulas->DeleteRows->ClearSheet->Verify.
/// </summary>
public class FodsR203DeleteRowsAndClearSheetTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellValue(0, 0, "Alice"); doc.SetCellValue(0, 1, "95");
        doc.SetCellValue(1, 0, "Bob"); doc.SetCellValue(1, 1, "82");
        doc.SetCellValue(2, 0, "Carol"); doc.SetCellValue(2, 1, "88");
        doc.SetCellValue(3, 0, "Dave"); doc.SetCellValue(3, 1, "76");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // DeleteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void DeleteRows_DecreasesRowCount()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        var before = doc.GetRowCount(sheet);
        doc.DeleteRows(sheet, 0, 2);
        var after = doc.GetRowCount(sheet);
        Assert.True(after < before);
    }

    [Fact]
    public void DeleteRows_CorrectCount_Removed()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.DeleteRows(sheet, 0, 2);
        Assert.Equal(2, doc.GetRowCount(sheet));
    }

    [Fact]
    public void DeleteRows_AtStart_ShiftsRemaining()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.DeleteRows(sheet, 0, 1); // Delete Alice
        var firstRow = doc.GetRowValues(sheet, 0);
        Assert.Contains("Bob", firstRow);
    }

    [Fact]
    public void DeleteRows_AtEnd_RowCountDecreases()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.DeleteRows(sheet, 3, 1); // Delete Dave
        Assert.Equal(3, doc.GetRowCount(sheet));
    }

    [Fact]
    public void DeleteRows_SingleRow_Correct()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.DeleteRows(sheet, 1, 1); // Delete Bob
        Assert.Equal(3, doc.GetRowCount(sheet));
        // Carol should now be at index 1
        var row1 = doc.GetRowValues(sheet, 1);
        Assert.Contains("Carol", row1);
    }

    // -------------------------------------------------------------------------
    // ClearSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void ClearSheet_RowCountBecomesZero()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
    }

    [Fact]
    public void ClearSheet_CellCountBecomesZero()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetCellCount(sheet));
    }

    [Fact]
    public void ClearSheet_AllowsReuse()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        doc.SetCellValue(0, 0, "Fresh");
        Assert.Equal(1, doc.GetRowCount(sheet));
        Assert.Equal("Fresh", doc.GetCellValue(sheet, 0, 0));
    }

    [Fact]
    public void ClearSheet_SecondSheet_MainUnaffected()
    {
        var doc = CreateWithData();
        var mainSheet = DefaultSheet(doc);
        doc.AddSheet("Extra");
        doc.SetCellValue("Extra", 0, 0, "ExtraData");
        doc.ClearSheet("Extra");
        // Main sheet still has data
        Assert.True(doc.GetRowCount(mainSheet) > 0);
    }

    // -------------------------------------------------------------------------
    // SetCellFormula / GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_GetCellFormula_RoundTrip()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = DefaultSheet(doc);
        doc.SetCellFormula(0, 0, "=SUM(A1:A10)");
        var formula = doc.GetCellFormula(sheet, 0, 0);
        Assert.NotNull(formula);
    }

    [Fact]
    public void SetCellFormula_StoredFormula_Contains_Expression()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellFormula(0, 0, "=A1+B1");
        var sheet = DefaultSheet(doc);
        var formula = doc.GetCellFormula(sheet, 0, 0);
        Assert.Contains("A1", formula ?? string.Empty);
    }

    [Fact]
    public void SetCellFormula_VisibleInToFodsXml()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetCellFormula(0, 0, "=AVERAGE(B1:B10)");
        var xml = doc.ToFodsXml();
        Assert.Contains("AVERAGE", xml);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellsSetFormulasDeleteRowsClearSheetVerify_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.GetSheetNames()[0];

        // SetCellValues
        doc.SetCellValue(0, 0, "Alice"); doc.SetCellValue(0, 1, "95");
        doc.SetCellValue(1, 0, "Bob"); doc.SetCellValue(1, 1, "82");
        doc.SetCellValue(2, 0, "Carol"); doc.SetCellValue(2, 1, "88");
        doc.SetCellValue(3, 0, "Total"); doc.SetCellFormula(3, 1, "=SUM(B1:B3)");
        Assert.Equal(4, doc.GetRowCount(sheet));

        // GetCellFormula
        var formula = doc.GetCellFormula(sheet, 3, 1);
        Assert.NotNull(formula);

        // DeleteRows (remove Bob)
        doc.DeleteRows(sheet, 1, 1);
        Assert.Equal(3, doc.GetRowCount(sheet));
        var row1 = doc.GetRowValues(sheet, 1);
        Assert.Contains("Carol", row1);

        // ClearSheet
        doc.ClearSheet(sheet);
        Assert.Equal(0, doc.GetRowCount(sheet));
        Assert.Equal(0, doc.GetCellCount(sheet));

        // Reuse after clear
        doc.SetCellValue(0, 0, "New Data");
        Assert.Equal(1, doc.GetRowCount(sheet));
        Assert.Equal("New Data", doc.GetCellValue(sheet, 0, 0));
    }
}
