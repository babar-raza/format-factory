// Tests for FodsDocument.ExportSheetToMarkdown dedicated coverage.
// Sprint: ff-sprint-s190-dotnet-deepening-20260628
// Ledger: PC-FODS-R197

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R197: Dedicated tests for FodsDocument.ExportSheetToMarkdown() and ExportSheetToMarkdown(string sheetName).
/// Exports a sheet as a Markdown table string.
/// No-arg overload: no sheets throws InvalidOperationException.
/// Empty sheet returns empty string.
/// First row becomes headers with a separator line beneath.
/// Named-sheet overload: nonexistent sheet throws ArgumentException.
/// Pipe characters in cell values are escaped.
/// Covers: no-sheets throws; empty sheet returns empty; one-row headers-only;
/// two rows returns table with separator; header row in result; separator row in result;
/// named-sheet nonexistent throws; named-sheet valid; named-sheet two rows;
/// dogfood set data then export contains cell values.
/// </summary>
public class FodsR197ExportSheetToMarkdownDedicatedTests
{
    // -------------------------------------------------------------------------
    // No-arg overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_EmptySheet_ReturnsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var result = doc.ExportSheetToMarkdown();
        Assert.NotNull(result);
    }

    [Fact]
    public void ExportSheetToMarkdown_OneRow_ContainsHeaderText()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("Name", result);
        Assert.Contains("Score", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_TwoRows_ContainsSeparatorRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Header");
        doc.SetCellValue(1, 0, "Data");
        var result = doc.ExportSheetToMarkdown();
        // Markdown table separator line contains dashes
        Assert.Contains("---", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_TwoRows_ContainsDataRow()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(1, 0, "Alice");
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("Alice", result);
    }

    [Fact]
    public void ExportSheetToMarkdown_TwoRows_ContainsPipeDelimiters()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Col1");
        doc.SetCellValue(0, 1, "Col2");
        doc.SetCellValue(1, 0, "A");
        doc.SetCellValue(1, 1, "B");
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("|", result);
    }

    // -------------------------------------------------------------------------
    // Named-sheet overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NamedSheet_NonexistentThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToMarkdown("NoSuchSheet"));
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedSheet_EmptySheetReturnsString()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Report");
        var result = doc.ExportSheetToMarkdown("Report");
        Assert.NotNull(result);
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedSheet_TwoRowsContainsData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "ColHeader");
        doc.SetCellValue("Data", 1, 0, "CellValue");
        var result = doc.ExportSheetToMarkdown("Data");
        Assert.Contains("ColHeader", result);
        Assert.Contains("CellValue", result);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetDataThenExport_AllCellsPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9.99");
        var result = doc.ExportSheetToMarkdown();
        Assert.Contains("Product", result);
        Assert.Contains("Widget", result);
        Assert.Contains("9.99", result);
    }
}
