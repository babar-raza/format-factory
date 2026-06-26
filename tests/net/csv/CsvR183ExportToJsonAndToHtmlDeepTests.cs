// Tests for CsvDocument.ExportToJson, ToHtml deeper pipeline coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R183

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R183: Tests for CsvDocument.ExportToJson, ToHtml deeper pipeline coverage.
/// ExportToJson(): returns a JSON string representation.
/// ToHtml(): returns an HTML string with a table representation.
/// Covers: ExportToJson non-null; ExportToJson non-empty; ExportToJson contains field names;
/// ExportToJson contains data values; ExportToJson after AddRow includes new;
/// ExportToJson after Filter smaller; ExportToJson after SetCellValue reflects change;
/// ToHtml non-null; ToHtml contains table tag; ToHtml contains header values;
/// ToHtml contains data values; ToHtml after AddRow includes new row;
/// ToHtml after Filter smaller; ToHtml after SetCellValue reflects change;
/// dogfood LoadContent->AddRow->SetCellValue->ExportToJson->ToHtml->Verify pipeline.
/// </summary>
public class CsvR183ExportToJsonAndToHtmlDeepTests
{
    private const string SampleContent =
        "Name,Dept,Score\n" +
        "Alice,Eng,92\n" +
        "Bob,Finance,85\n" +
        "Carol,HR,78\n" +
        "Dave,Eng,91";

    // -------------------------------------------------------------------------
    // ExportToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_NonNull()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.NotNull(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_NonEmpty()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.NotEmpty(doc.ExportToJson());
    }

    [Fact]
    public void ExportToJson_ContainsFieldNames()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var json = doc.ExportToJson();
        Assert.Contains("Name", json);
        Assert.Contains("Dept", json);
        Assert.Contains("Score", json);
    }

    [Fact]
    public void ExportToJson_ContainsDataValues()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var json = doc.ExportToJson();
        Assert.Contains("Alice", json);
        Assert.Contains("Finance", json);
        Assert.Contains("92", json);
    }

    [Fact]
    public void ExportToJson_AfterAddRow_IncludesNewRecord()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.AddRow(new[] { "Eve", "Legal", "95" });
        var json = doc.ExportToJson();
        Assert.Contains("Eve", json);
        Assert.Contains("Legal", json);
    }

    [Fact]
    public void ExportToJson_AfterFilter_Smaller()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var full = doc.ExportToJson();
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var filtered = engOnly.ExportToJson();
        Assert.True(filtered.Length < full.Length);
    }

    [Fact]
    public void ExportToJson_AfterSetCellValue_ReflectsChange()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, "Score", "100");
        var json = doc.ExportToJson();
        Assert.Contains("100", json);
    }

    [Fact]
    public void ExportToJson_IsValidJsonStructure()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var json = doc.ExportToJson();
        // Should be array or object JSON
        Assert.True(json.StartsWith("[") || json.StartsWith("{"));
    }

    // -------------------------------------------------------------------------
    // ToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ToHtml_NonNull()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.NotNull(doc.ToHtml());
    }

    [Fact]
    public void ToHtml_NonEmpty()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.NotEmpty(doc.ToHtml());
    }

    [Fact]
    public void ToHtml_ContainsTableTag()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var html = doc.ToHtml();
        Assert.Contains("<table", html.ToLower());
    }

    [Fact]
    public void ToHtml_ContainsHeaderValues()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var html = doc.ToHtml();
        Assert.Contains("Name", html);
        Assert.Contains("Dept", html);
        Assert.Contains("Score", html);
    }

    [Fact]
    public void ToHtml_ContainsDataValues()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var html = doc.ToHtml();
        Assert.Contains("Alice", html);
        Assert.Contains("Finance", html);
    }

    [Fact]
    public void ToHtml_AfterAddRow_IncludesNewData()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.AddRow(new[] { "Zara", "Legal", "99" });
        var html = doc.ToHtml();
        Assert.Contains("Zara", html);
        Assert.Contains("Legal", html);
    }

    [Fact]
    public void ToHtml_AfterFilter_Smaller()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        var full = doc.ToHtml();
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        var filtered = engOnly.ToHtml();
        Assert.True(filtered.Length < full.Length);
    }

    [Fact]
    public void ToHtml_AfterSetCellValue_ReflectsChange()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        doc.SetCellValue(0, "Name", "ALICE_UPDATED");
        var html = doc.ToHtml();
        Assert.Contains("ALICE_UPDATED", html);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadContent_AddRow_SetCellValue_ExportToJson_ToHtml_Verify_Pipeline()
    {
        var doc = CsvDocument.LoadContent(SampleContent);
        Assert.Equal(4, doc.RowCount);

        // AddRow
        doc.AddRow(new[] { "Eve", "Legal", "95" });
        Assert.Equal(5, doc.RowCount);

        // SetCellValue
        doc.SetCellValue(0, "Score", "100");
        Assert.Equal("100", doc.GetCellValue(0, "Score"));

        // ExportToJson
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.Contains("Alice", json);
        Assert.Contains("Eve", json);
        Assert.Contains("100", json);

        // ToHtml
        var html = doc.ToHtml();
        Assert.NotNull(html);
        Assert.Contains("<table", html.ToLower());
        Assert.Contains("Alice", html);
        Assert.Contains("Eve", html);

        // Filter and export
        var engOnly = doc.Filter(r => r.GetCellValue("Dept") == "Eng");
        Assert.Equal(2, engOnly.RowCount); // Alice and Dave

        var engJson = engOnly.ExportToJson();
        Assert.Contains("Alice", engJson);
        Assert.DoesNotContain("Finance", engJson);

        var engHtml = engOnly.ToHtml();
        Assert.Contains("Alice", engHtml);
        Assert.DoesNotContain("Finance", engHtml);

        // GetDistinctValues
        var distinct = doc.GetDistinctValues("Dept");
        Assert.True(distinct.Count >= 3); // Eng, Finance, HR, Legal
        Assert.Contains("Legal", distinct);
    }
}
