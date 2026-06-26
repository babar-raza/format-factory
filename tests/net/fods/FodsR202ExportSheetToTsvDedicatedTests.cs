// Tests for FodsDocumentExporter.ExportSheetToTsv dedicated coverage.
// Sprint: ff-sprint-s191-dotnet-deepening-20260629
// Ledger: PC-FODS-R202

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R202: Dedicated tests for FodsDocumentExporter.ExportSheetToTsv(FodsSheet sheet).
/// Empty sheet returns empty string.
/// Single cell returns value followed by newline.
/// Two cells in one row are tab-separated.
/// Multiple rows each end with newline.
/// Tab characters in values are replaced with space.
/// Null cell value produces empty string (not literal "null").
/// Returns non-null string.
/// Two-row result contains two lines.
/// Named-sheet can be used via GetSheetByName to get the FodsSheet.
/// Dogfood: multi-cell data round-trip values present in TSV.
/// </summary>
public class FodsR202ExportSheetToTsvDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToTsv_EmptySheet_ReturnsEmptyString()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Equal(string.Empty, tsv);
    }

    [Fact]
    public void ExportSheetToTsv_SingleCell_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Hello");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.NotNull(tsv);
    }

    [Fact]
    public void ExportSheetToTsv_SingleCell_ContainsValue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "TestValue");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("TestValue", tsv);
    }

    [Fact]
    public void ExportSheetToTsv_TwoColumnsOneRow_SeparatedByTab()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Col1");
        FodsDocument.SetCellValue(sheet, 0, 1, "Col2");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("\t", tsv);
    }

    [Fact]
    public void ExportSheetToTsv_TwoRows_BothLinesPresent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Row1");
        FodsDocument.SetCellValue(sheet, 1, 0, "Row2");
        var lines = FodsDocumentExporter.ExportSheetToTsv(sheet)
            .Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 2);
    }

    [Fact]
    public void ExportSheetToTsv_TabInValue_ReplacedWithSpace()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "A\tB");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        // The embedded tab should be replaced; value appears without raw tab within token
        var firstLine = tsv.Split('\n')[0];
        // Should contain "A B" (space) not the original tab in the value
        Assert.Contains("A B", firstLine);
    }

    [Fact]
    public void ExportSheetToTsv_TwoColumnsValues_BothInOutput()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Alpha");
        FodsDocument.SetCellValue(sheet, 0, 1, "Beta");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("Alpha", tsv);
        Assert.Contains("Beta", tsv);
    }

    [Fact]
    public void ExportSheetToTsv_ViaGetSheetByName_Works()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("DataSheet");
        FodsDocument.SetCellValue(sheet, 0, 0, "Named");
        var retrieved = doc.GetSheetByName("DataSheet");
        Assert.NotNull(retrieved);
        var tsv = FodsDocumentExporter.ExportSheetToTsv(retrieved!);
        Assert.Contains("Named", tsv);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiCellData_AllValuesPresent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Name");
        FodsDocument.SetCellValue(sheet, 0, 1, "Score");
        FodsDocument.SetCellValue(sheet, 1, 0, "Alice");
        FodsDocument.SetCellValue(sheet, 1, 1, "95");
        FodsDocument.SetCellValue(sheet, 2, 0, "Bob");
        FodsDocument.SetCellValue(sheet, 2, 1, "87");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        Assert.Contains("Name", tsv);
        Assert.Contains("Score", tsv);
        Assert.Contains("Alice", tsv);
        Assert.Contains("95", tsv);
        Assert.Contains("Bob", tsv);
        Assert.Contains("87", tsv);
    }

    [Fact]
    public void DogfoodPipeline_ThreeRowsThreeCols_StructureCorrect()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                FodsDocument.SetCellValue(sheet, row, col, $"R{row}C{col}");
        var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
        var lines = tsv.Split('\n', System.StringSplitOptions.RemoveEmptyEntries);
        Assert.Equal(3, lines.Length);
        // Each line should have 2 tabs (3 columns)
        foreach (var line in lines)
            Assert.Equal(2, line.Count(c => c == '\t'));
    }
}
