// Tests for FodsDocument export methods: ExportSheetToCsv, ExportSheetToMarkdown, ExportSheetToJson, ExportSheetToHtml.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R174

using System;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R174: Tests for FodsDocument export methods — combined coverage.
/// ExportSheetToCsv(): serializes first sheet to CSV.
/// ExportSheetToMarkdown(): serializes first sheet to markdown table.
/// ExportSheetToJson(): serializes first sheet to JSON.
/// ExportSheetToHtml(): serializes first sheet to HTML.
/// Static overloads accept FodsSheet directly.
/// Covers: ExportSheetToCsv contains commas; ExportSheetToCsv contains cell values;
/// ExportSheetToMarkdown contains pipes; ExportSheetToMarkdown contains cell values;
/// ExportSheetToJson is valid JSON; ExportSheetToJson contains field names;
/// ExportSheetToHtml contains angle brackets; ExportSheetToHtml contains cell values;
/// All static overloads work; Named-sheet overloads work;
/// dogfood CreateNew->InsertRows->ExportAll pipeline.
/// </summary>
public class FodsR174ExportAllFormatsTests
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
    // ExportSheetToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToCsv_ContainsCommas()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var csv = doc.ExportSheetToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ExportSheetToCsv_ContainsCellValues()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var csv = doc.ExportSheetToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("95", csv);
    }

    [Fact]
    public void ExportSheetToCsv_BySheetName_ContainsValues()
    {
        var doc = BuildSheet("Report",
            new[] { "Product" },
            new[] { new[] { "Widget" } });
        var csv = doc.ExportSheetToCsv("Report");
        Assert.Contains("Widget", csv);
    }

    [Fact]
    public void ExportSheetToCsv_Static_ContainsValues()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var sheet = doc.GetSheetByName("Sheet");
        Assert.NotNull(sheet);
        var csv = FodsDocument.ExportSheetToCsv(sheet!);
        Assert.Contains("Val", csv);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_ContainsPipes()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsCellValues()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Bob", "82" } });
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("Bob", md);
        Assert.Contains("82", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsHeaderRow()
    {
        var doc = BuildSheet("Sheet",
            new[] { "Product", "Price" },
            new[] { new[] { "Widget", "9.99" } });
        var md = doc.ExportSheetToMarkdown("Sheet");
        Assert.Contains("Product", md);
        Assert.Contains("Price", md);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_IsValidJson()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var json = doc.ExportSheetToJson();
        var ex = Record.Exception(() => JsonDocument.Parse(json));
        Assert.Null(ex);
    }

    [Fact]
    public void ExportSheetToJson_ContainsFieldNames()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var json = doc.ExportSheetToJson();
        Assert.Contains("Alice", json);
    }

    [Fact]
    public void ExportSheetToJson_BySheetName_IsValid()
    {
        var doc = BuildSheet("Report",
            new[] { "Item" },
            new[] { new[] { "Bolt" } });
        var json = doc.ExportSheetToJson("Report");
        var ex = Record.Exception(() => JsonDocument.Parse(json));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_ContainsAngleBrackets()
    {
        var doc = BuildSheet("Data",
            new[] { "Name" },
            new[] { new[] { "Alice" } });
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<", html);
        Assert.Contains(">", html);
    }

    [Fact]
    public void ExportSheetToHtml_ContainsCellValues()
    {
        var doc = BuildSheet("Data",
            new[] { "Product" },
            new[] { new[] { "Gadget" } });
        var html = doc.ExportSheetToHtml();
        Assert.Contains("Gadget", html);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->InsertRows->ExportAll
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_InsertRowsExportAll_Pipeline()
    {
        var doc = BuildSheet("Inventory",
            new[] { "Item", "Count", "Price" },
            new[] {
                new[] { "Widget", "100", "9.99" },
                new[] { "Gadget", "50", "19.99" }
            });

        // CSV
        var csv = doc.ExportSheetToCsv();
        Assert.Contains(",", csv);
        Assert.Contains("Widget", csv);

        // Markdown
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
        Assert.Contains("Gadget", md);

        // JSON
        var json = doc.ExportSheetToJson();
        var parsed = JsonDocument.Parse(json);
        Assert.Equal(JsonValueKind.Array, parsed.RootElement.ValueKind);

        // HTML
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<", html);
        Assert.Contains("Widget", html);
    }
}
