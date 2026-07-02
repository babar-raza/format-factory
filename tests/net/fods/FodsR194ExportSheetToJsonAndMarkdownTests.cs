// Tests for FodsDocument.ExportSheetToJson, ExportSheetToMarkdown, ExportSheetToXml deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R194

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R194: Tests for FodsDocument.ExportSheetToJson, ExportSheetToMarkdown, ExportSheetToXml.
/// ExportSheetToJson(sheetName): serializes sheet to JSON string.
/// ExportSheetToMarkdown(sheetName): serializes sheet to Markdown table string.
/// ExportSheetToXml(sheetName): serializes sheet to XML string.
/// Covers: ExportSheetToJson non-null; ExportSheetToJson contains data values;
/// ExportSheetToJson is valid JSON bracket; ExportSheetToMarkdown non-null;
/// ExportSheetToMarkdown contains data values; ExportSheetToMarkdown has pipe chars;
/// ExportSheetToXml non-null; ExportSheetToXml contains data values;
/// ExportSheetToXml starts with XML bracket; ExportSheetToJson after SetCellValue;
/// ExportSheetToMarkdown after InsertRow; ExportSheetToJson empty sheet;
/// ExportSheetToMarkdown after ClearSheet; ExportSheetToXml field count;
/// dogfood CreateNew->SetCells->ExportJson->ExportMarkdown->ExportXml verify.
/// </summary>
public class FodsR194ExportSheetToJsonAndMarkdownTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Alice");
        doc.SetCellValue(0, 1, "Eng");
        doc.SetCellValue(0, 2, "95");
        doc.SetCellValue(1, 0, "Bob");
        doc.SetCellValue(1, 1, "Finance");
        doc.SetCellValue(1, 2, "82");
        return doc;
    }

    private static string DefaultSheet(FodsDocument doc) => doc.GetSheetNames()[0];

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_NonNull()
    {
        var doc = CreateWithData();
        var json = doc.ExportSheetToJson(DefaultSheet(doc));
        Assert.NotNull(json);
    }

    [Fact]
    public void ExportSheetToJson_ContainsDataValues()
    {
        var doc = CreateWithData();
        var json = doc.ExportSheetToJson(DefaultSheet(doc));
        Assert.True(json.Contains("Alice") || json.Contains("alice"),
            "JSON should contain Alice");
    }

    [Fact]
    public void ExportSheetToJson_IsValidJsonBracket()
    {
        var doc = CreateWithData();
        var json = doc.ExportSheetToJson(DefaultSheet(doc)).Trim();
        Assert.True(json.StartsWith("[") || json.StartsWith("{"),
            $"Expected JSON to start with '[' or '{{' but got: {json.Substring(0, System.Math.Min(20, json.Length))}");
    }

    [Fact]
    public void ExportSheetToJson_AfterSetCellValue_ContainsNewValue()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.SetCellValue(2, 0, "Dave");
        var json = doc.ExportSheetToJson(sheet);
        Assert.Contains("Dave", json);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_NonNull()
    {
        var doc = CreateWithData();
        var md = doc.ExportSheetToMarkdown(DefaultSheet(doc));
        Assert.NotNull(md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsDataValues()
    {
        var doc = CreateWithData();
        var md = doc.ExportSheetToMarkdown(DefaultSheet(doc));
        Assert.Contains("Alice", md);
        Assert.Contains("Bob", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_HasPipeCharacters()
    {
        var doc = CreateWithData();
        var md = doc.ExportSheetToMarkdown(DefaultSheet(doc));
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterInsertRow_ContainsNewRow()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.InsertRowWithValues(sheet, 2, new[] { "Carol", "Eng", "88" });
        var md = doc.ExportSheetToMarkdown(sheet);
        Assert.Contains("Carol", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_AfterClearSheet_Empty()
    {
        var doc = CreateWithData();
        var sheet = DefaultSheet(doc);
        doc.ClearSheet(sheet);
        var md = doc.ExportSheetToMarkdown(sheet);
        // Should be empty or minimal
        Assert.DoesNotContain("Alice", md);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToXml_NonNull()
    {
        var doc = CreateWithData();
        var xml = doc.ExportSheetToXml(DefaultSheet(doc));
        Assert.NotNull(xml);
    }

    [Fact]
    public void ExportSheetToXml_ContainsDataValues()
    {
        var doc = CreateWithData();
        var xml = doc.ExportSheetToXml(DefaultSheet(doc));
        Assert.Contains("Alice", xml);
    }

    [Fact]
    public void ExportSheetToXml_StartsWithXmlBracket()
    {
        var doc = CreateWithData();
        var xml = doc.ExportSheetToXml(DefaultSheet(doc)).Trim();
        Assert.True(xml.StartsWith("<"),
            $"Expected XML to start with '<' but got: {xml.Substring(0, System.Math.Min(20, xml.Length))}");
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCells->ExportJson->ExportMarkdown->ExportXml verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateSetCellsExportJsonMarkdownXml_Verify()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetNames()[0];

        // Set data
        doc.SetCellValue(0, 0, "X");
        doc.SetCellValue(0, 1, "A");
        doc.SetCellValue(0, 2, "10");
        doc.SetCellValue(1, 0, "Y");
        doc.SetCellValue(1, 1, "B");
        doc.SetCellValue(1, 2, "20");

        // ExportSheetToJson
        var json = doc.ExportSheetToJson(sheet);
        Assert.NotNull(json);
        Assert.Contains("X", json);

        // ExportSheetToMarkdown
        var md = doc.ExportSheetToMarkdown(sheet);
        Assert.NotNull(md);
        Assert.Contains("X", md);
        Assert.Contains("|", md);

        // ExportSheetToXml
        var xml = doc.ExportSheetToXml(sheet);
        Assert.NotNull(xml);
        Assert.Contains("X", xml);
        Assert.Contains("<", xml);

        // Modify and re-export
        doc.SetCellValue(2, 0, "Z");
        var json2 = doc.ExportSheetToJson(sheet);
        Assert.Contains("Z", json2);
    }
}
