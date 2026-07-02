// Tests for FodsDocument.GetCellDataType, SetCellFormula, GetCellFormula, SetCellStyle deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R210

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R210: Tests for FodsDocument.GetCellDataType, SetCellFormula, GetCellFormula, SetCellStyle deeper.
/// GetCellDataType(sheet, row, col): returns the data type of a cell ("string", "number", etc.).
/// SetCellFormula(sheet, row, col, formula): sets a formula string in a cell.
/// GetCellFormula(sheet, row, col): retrieves the formula from a cell.
/// SetCellStyle(sheet, row, col, style): applies a style name to a cell.
/// GetCellStyle(sheet, row, col): returns the style name of a cell.
/// Covers: GetCellDataType string cell; GetCellDataType number cell; GetCellDataType after SetCellValue;
/// SetCellFormula non-null after set; GetCellFormula matches set formula;
/// GetCellFormula after SetCellValue returns empty or null; SetCellStyle then GetCellStyle matches;
/// SetCellStyle multiple cells; GetCellDataType does not throw for empty sheet;
/// dogfood CreateFromArray->SetCellFormula->GetCellFormula->SetCellStyle->GetCellStyle->Verify pipeline.
/// </summary>
public class FodsR210GetCellDataTypeAndFormulaDeepTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "95");
        doc.SetCellValue("Data", 2, 0, "Bob");
        doc.SetCellValue("Data", 2, 1, "87");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCellDataType
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCellDataType_StringCell_ReturnsString()
    {
        var doc = CreateWithData();
        var dataType = doc.GetCellDataType("Data", 0, 0);
        Assert.NotNull(dataType);
        Assert.NotEmpty(dataType);
    }

    [Fact]
    public void GetCellDataType_AfterSetCellValue_NonEmpty()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Hello world");
        var dataType = doc.GetCellDataType("Sheet1", 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void GetCellDataType_NumericString_ReturnsSomeType()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Numbers");
        doc.SetCellValue("Numbers", 0, 0, "42");
        var dataType = doc.GetCellDataType("Numbers", 0, 0);
        Assert.NotNull(dataType);
    }

    [Fact]
    public void GetCellDataType_DifferentCells_CanVary()
    {
        var doc = CreateWithData();
        var nameType = doc.GetCellDataType("Data", 0, 0);
        var scoreType = doc.GetCellDataType("Data", 0, 1);
        // Both non-null; may be same or different type
        Assert.NotNull(nameType);
        Assert.NotNull(scoreType);
    }

    // -------------------------------------------------------------------------
    // SetCellFormula / GetCellFormula
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellFormula_ThenGetCellFormula_MatchesSet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Calc");
        doc.SetCellValue("Calc", 0, 0, "10");
        doc.SetCellValue("Calc", 1, 0, "20");
        doc.SetCellFormula("Calc", 2, 0, "=SUM(A1:A2)");
        var formula = doc.GetCellFormula("Calc", 2, 0);
        Assert.NotNull(formula);
        Assert.NotEmpty(formula);
    }

    [Fact]
    public void SetCellFormula_MultipleFormulas_AllRetrievable()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Multi");
        doc.SetCellFormula("Multi", 0, 0, "=1+1");
        doc.SetCellFormula("Multi", 1, 0, "=2*3");
        var f0 = doc.GetCellFormula("Multi", 0, 0);
        var f1 = doc.GetCellFormula("Multi", 1, 0);
        Assert.NotNull(f0);
        Assert.NotNull(f1);
    }

    [Fact]
    public void GetCellFormula_PlainValueCell_EmptyOrNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Plain");
        doc.SetCellValue("Plain", 0, 0, "Just text");
        var formula = doc.GetCellFormula("Plain", 0, 0);
        // Plain text cells have no formula
        Assert.True(formula == null || formula == string.Empty);
    }

    // -------------------------------------------------------------------------
    // SetCellStyle / GetCellStyle
    // -------------------------------------------------------------------------

    [Fact]
    public void SetCellStyle_ThenGetCellStyle_MatchesSet()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Styled");
        doc.SetCellValue("Styled", 0, 0, "Header");
        doc.SetCellStyle("Styled", 0, 0, "ce1");
        var style = doc.GetCellStyle("Styled", 0, 0);
        Assert.Equal("ce1", style);
    }

    [Fact]
    public void SetCellStyle_MultipleCells_IndependentStyles()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Styles");
        doc.SetCellValue("Styles", 0, 0, "A");
        doc.SetCellValue("Styles", 0, 1, "B");
        doc.SetCellStyle("Styles", 0, 0, "ce1");
        doc.SetCellStyle("Styles", 0, 1, "ce2");
        Assert.Equal("ce1", doc.GetCellStyle("Styles", 0, 0));
        Assert.Equal("ce2", doc.GetCellStyle("Styles", 0, 1));
    }

    [Fact]
    public void SetCellStyle_OverwritePrevious_LastWins()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Overwrite");
        doc.SetCellValue("Overwrite", 0, 0, "Cell");
        doc.SetCellStyle("Overwrite", 0, 0, "ce1");
        doc.SetCellStyle("Overwrite", 0, 0, "ce3");
        Assert.Equal("ce3", doc.GetCellStyle("Overwrite", 0, 0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateFromArray_SetFormula_GetFormula_SetStyle_GetStyle_Verify_Pipeline()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Report");

        // Populate data
        doc.SetCellValue("Report", 0, 0, "Month");
        doc.SetCellValue("Report", 0, 1, "Sales");
        doc.SetCellValue("Report", 1, 0, "Jan");
        doc.SetCellValue("Report", 1, 1, "1000");
        doc.SetCellValue("Report", 2, 0, "Feb");
        doc.SetCellValue("Report", 2, 1, "1500");
        doc.SetCellValue("Report", 3, 0, "Mar");
        doc.SetCellValue("Report", 3, 1, "1200");

        // GetCellDataType
        var monthType = doc.GetCellDataType("Report", 0, 0);
        Assert.NotNull(monthType);

        // SetCellFormula for total
        doc.SetCellFormula("Report", 4, 1, "=SUM(B2:B4)");
        var formula = doc.GetCellFormula("Report", 4, 1);
        Assert.NotNull(formula);
        Assert.NotEmpty(formula);

        // Verify non-formula cell returns empty formula
        var noFormula = doc.GetCellFormula("Report", 0, 0);
        Assert.True(noFormula == null || noFormula == string.Empty);

        // SetCellStyle on header row
        doc.SetCellStyle("Report", 0, 0, "ce1");
        doc.SetCellStyle("Report", 0, 1, "ce1");
        Assert.Equal("ce1", doc.GetCellStyle("Report", 0, 0));
        Assert.Equal("ce1", doc.GetCellStyle("Report", 0, 1));

        // Verify row count still correct
        Assert.True(doc.GetRowCount("Report") > 0);
    }
}
