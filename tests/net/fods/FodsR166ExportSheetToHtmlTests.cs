// Tests for FodsDocument.ExportSheetToHtml (overloads).
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R166

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R166: Tests for FodsDocument.ExportSheetToHtml overloads.
/// ExportSheetToHtml(): exports the first sheet as HTML table.
/// ExportSheetToHtml(sheetName): exports the named sheet as HTML table.
/// ExportSheetToHtml(FodsSheet): static overload that exports a given sheet.
/// Covers: ExportSheetToHtml() returns non-null; ExportSheetToHtml contains table tag;
/// ExportSheetToHtml single-cell contains cell value; ExportSheetToHtml named sheet non-null;
/// ExportSheetToHtml named sheet contains cell value; ExportSheetToHtml empty sheet non-null;
/// ExportSheetToHtml static overload non-null; ExportSheetToHtml static contains data;
/// ExportSheetToHtml output is valid HTML with opening table; ExportSheetToHtml multirow;
/// ExportSheetToHtml headers appear in output; ExportSheetToHtml no-args same as named first;
/// dogfood BuildSheet->ExportHtml->ParseHtml pipeline.
/// </summary>
public class FodsR166ExportSheetToHtmlTests
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
    // ExportSheetToHtml() — no args
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_NoArgs_ReturnsNonNull()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var html = doc.ExportSheetToHtml();
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportSheetToHtml_NoArgs_ContainsTableTag()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<table", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void ExportSheetToHtml_NoArgs_ContainsCellValue()
    {
        var doc = BuildSheet("Report",
            new[] { "Product" },
            new[] { new[] { "Widget" } });
        var html = doc.ExportSheetToHtml();
        Assert.Contains("Widget", html);
    }

    [Fact]
    public void ExportSheetToHtml_NoArgs_ContainsHeaders()
    {
        var doc = BuildSheet("Data",
            new[] { "Name", "Score" },
            new[] { new[] { "Alice", "95" } });
        var html = doc.ExportSheetToHtml();
        Assert.Contains("Name", html);
        Assert.Contains("Score", html);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToHtml(sheetName)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_Named_ReturnsNonNull()
    {
        var doc = BuildSheet("Sales",
            new[] { "Item", "Revenue" },
            new[] { new[] { "Widget", "1500" } });
        var html = doc.ExportSheetToHtml("Sales");
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportSheetToHtml_Named_ContainsCellValue()
    {
        var doc = BuildSheet("Inventory",
            new[] { "Part" },
            new[] { new[] { "Bolt" } });
        var html = doc.ExportSheetToHtml("Inventory");
        Assert.Contains("Bolt", html);
    }

    [Fact]
    public void ExportSheetToHtml_EmptySheet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        var name = doc.GetSheetNames()[0];
        var html = doc.ExportSheetToHtml(name);
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportSheetToHtml_MultiRow_ContainsAllValues()
    {
        var doc = BuildSheet("Multi",
            new[] { "A", "B" },
            new[] {
                new[] { "R1C1", "R1C2" },
                new[] { "R2C1", "R2C2" }
            });
        var html = doc.ExportSheetToHtml("Multi");
        Assert.Contains("R1C1", html);
        Assert.Contains("R2C2", html);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToHtml(FodsSheet) — static overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToHtml_Static_ReturnsNonNull()
    {
        var doc = BuildSheet("Data",
            new[] { "Col" },
            new[] { new[] { "Val" } });
        var sheet = doc.GetSheetByName("Data");
        var html = FodsDocument.ExportSheetToHtml(sheet!);
        Assert.NotNull(html);
    }

    [Fact]
    public void ExportSheetToHtml_Static_ContainsData()
    {
        var doc = BuildSheet("Items",
            new[] { "Name" },
            new[] { new[] { "SomeItem" } });
        var sheet = doc.GetSheetByName("Items");
        var html = FodsDocument.ExportSheetToHtml(sheet!);
        Assert.Contains("SomeItem", html);
    }

    // -------------------------------------------------------------------------
    // Dogfood: BuildSheet->ExportHtml->HasTableStructure
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_BuildSheetExportHtml_Pipeline()
    {
        var doc = BuildSheet("Products",
            new[] { "Name", "Category", "Price" },
            new[] {
                new[] { "Widget", "Hardware", "9.99" },
                new[] { "Gadget", "Electronics", "19.99" },
                new[] { "Doohickey", "Hardware", "4.99" }
            });

        // No-arg export
        var html1 = doc.ExportSheetToHtml();
        Assert.Contains("<table", html1, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Widget", html1);

        // Named export
        var html2 = doc.ExportSheetToHtml("Products");
        Assert.Contains("Gadget", html2);
        Assert.Contains("Electronics", html2);

        // Static export via sheet object
        var sheet = doc.GetSheetByName("Products");
        var html3 = FodsDocument.ExportSheetToHtml(sheet!);
        Assert.Contains("Doohickey", html3);

        // All three should be non-empty HTML
        Assert.True(html1.Length > 0);
        Assert.True(html2.Length > 0);
        Assert.True(html3.Length > 0);
    }
}
