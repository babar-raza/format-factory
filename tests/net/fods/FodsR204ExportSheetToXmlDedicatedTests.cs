// Tests for FodsDocumentExporter.ExportSheetToXml dedicated coverage.
// Sprint: ff-sprint-s192-dotnet-deepening-20260629
// Ledger: PC-FODS-R204

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R204: Dedicated tests for FodsDocumentExporter.ExportSheetToXml(FodsSheet sheet).
/// Empty sheet returns a &lt;table&gt; element string.
/// Root element is &lt;table name="sheetName"&gt;.
/// Each row becomes a &lt;row&gt; element.
/// Each non-empty cell becomes &lt;cell&gt;value&lt;/cell&gt;.
/// Empty cell becomes &lt;cell/&gt;.
/// Special XML characters in cell values are escaped.
/// Sheet name appears in the name attribute.
/// Multi-row data all rows present.
/// Dogfood: multi-cell grid all values present; sheet name in attribute.
/// </summary>
public class FodsR204ExportSheetToXmlDedicatedTests
{
    // -------------------------------------------------------------------------
    // Basic structure tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToXml_EmptySheet_ContainsTableElement()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Empty");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<table", xml);
    }

    [Fact]
    public void ExportSheetToXml_ReturnsNonNullString()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.NotNull(xml);
    }

    [Fact]
    public void ExportSheetToXml_SheetNameInAttribute()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("MyData");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("name=\"MyData\"", xml);
    }

    [Fact]
    public void ExportSheetToXml_OneRow_ContainsRowElement()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Value");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<row>", xml);
    }

    [Fact]
    public void ExportSheetToXml_OneCell_CellElementWithValue()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Hello");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("<cell>Hello</cell>", xml);
    }

    [Fact]
    public void ExportSheetToXml_XmlSpecialChars_Escaped()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "<br/>");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("&lt;br/&gt;", xml);
    }

    [Fact]
    public void ExportSheetToXml_TwoRowsData_BothRowsPresent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Row1");
        FodsDocument.SetCellValue(sheet, 1, 0, "Row2");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("Row1", xml);
        Assert.Contains("Row2", xml);
    }

    [Fact]
    public void ExportSheetToXml_ContainsClosingTableTag()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Test");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("</table>", xml);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiCellGrid_AllValuesPresent()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.Sheets[0];
        FodsDocument.SetCellValue(sheet, 0, 0, "Name");
        FodsDocument.SetCellValue(sheet, 0, 1, "Age");
        FodsDocument.SetCellValue(sheet, 1, 0, "Alice");
        FodsDocument.SetCellValue(sheet, 1, 1, "30");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("Name", xml);
        Assert.Contains("Age", xml);
        Assert.Contains("Alice", xml);
        Assert.Contains("30", xml);
    }

    [Fact]
    public void DogfoodPipeline_NamedSheet_SheetNameInOutput()
    {
        var doc = FodsDocument.CreateNew();
        var sheet = doc.AddSheet("Reports");
        FodsDocument.SetCellValue(sheet, 0, 0, "Q1");
        var xml = FodsDocumentExporter.ExportSheetToXml(sheet);
        Assert.Contains("Reports", xml);
        Assert.Contains("Q1", xml);
    }
}
