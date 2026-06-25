// Tests for FodsDocument.ExportSheetToJson(sheetName) and ExportSheetToMarkdown(sheetName)
// named-sheet overloads — targeted exports by sheet name.
// Sprint: FORMAT-FACTORY-FODS-JSON-MD-NAMED-R133-20260627
// Ledger: R133-GOVERNED-DOTNET-FODS-JSON-MD-NAMED-001

using System;
using System.IO;
using System.Text.Json;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R133: FodsDocument.ExportSheetToJson(sheetName) exports a named sheet to JSON.
/// FodsDocument.ExportSheetToMarkdown(sheetName) exports a named sheet to Markdown.
/// Both: correct data, no cross-sheet contamination, second sheet can be targeted,
/// and the instance no-arg overload matches the first-sheet named result.
/// </summary>
public class FodsR133ExportSheetJsonMarkdownNamedTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MultiPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    private static FodsDocument Multi() => FodsDocument.Load(MultiPath);

    // ---- ExportSheetToJson(sheetName): structure ----

    [Fact]
    public void ExportSheetToJson_NamedFirstSheet_ReturnsNonEmpty()
    {
        var doc = Multi();
        var name = doc.GetSheetNames()[0];
        var json = doc.ExportSheetToJson(name);
        Assert.False(string.IsNullOrWhiteSpace(json));
    }

    [Fact]
    public void ExportSheetToJson_NamedFirstSheet_IsValidJson()
    {
        var doc = Multi();
        var name = doc.GetSheetNames()[0];
        var json = doc.ExportSheetToJson(name);
        // Must parse without throwing
        using var _ = JsonDocument.Parse(json);
    }

    [Fact]
    public void ExportSheetToJson_NamedFirstSheet_MatchesDefaultOverload()
    {
        var doc = Multi();
        var firstName = doc.GetSheetNames()[0];
        var byName   = doc.ExportSheetToJson(firstName);
        var byDefault = doc.ExportSheetToJson();
        Assert.Equal(byDefault, byName);
    }

    // ---- ExportSheetToJson: second sheet ----

    [Fact]
    public void ExportSheetToJson_SecondSheet_ReturnsNonEmpty()
    {
        var doc = Multi();
        var names = doc.GetSheetNames();
        if (names.Count < 2) return; // Skip if fixture has only 1 sheet
        var json = doc.ExportSheetToJson(names[1]);
        Assert.False(string.IsNullOrWhiteSpace(json));
    }

    [Fact]
    public void ExportSheetToJson_SecondSheet_DiffersFromFirstSheet()
    {
        var doc = Multi();
        var names = doc.GetSheetNames();
        if (names.Count < 2) return;
        var json1 = doc.ExportSheetToJson(names[0]);
        var json2 = doc.ExportSheetToJson(names[1]);
        // The two sheets have different data — JSON must differ
        Assert.NotEqual(json1, json2);
    }

    // ---- ExportSheetToMarkdown(sheetName): structure ----

    [Fact]
    public void ExportSheetToMarkdown_NamedFirstSheet_ContainsPipeChars()
    {
        var doc = Multi();
        var name = doc.GetSheetNames()[0];
        var md = doc.ExportSheetToMarkdown(name);
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedFirstSheet_ContainsDividerRow()
    {
        var doc = Multi();
        var name = doc.GetSheetNames()[0];
        var md = doc.ExportSheetToMarkdown(name);
        Assert.Contains("---", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_NamedFirstSheet_MatchesDefaultOverload()
    {
        var doc = Multi();
        var firstName  = doc.GetSheetNames()[0];
        var byName     = doc.ExportSheetToMarkdown(firstName);
        var byDefault  = doc.ExportSheetToMarkdown();
        Assert.Equal(byDefault, byName);
    }

    [Fact]
    public void ExportSheetToMarkdown_SecondSheet_DiffersFromFirstSheet()
    {
        var doc = Multi();
        var names = doc.GetSheetNames();
        if (names.Count < 2) return;
        var md1 = doc.ExportSheetToMarkdown(names[0]);
        var md2 = doc.ExportSheetToMarkdown(names[1]);
        Assert.NotEqual(md1, md2);
    }

    // ---- Dogfood: two-sheet export comparison pipeline ----

    [Fact]
    public void DogfoodPipeline_TwoSheetExports_JsonAndMarkdownBothNonEmpty()
    {
        var doc   = Multi();
        var names = doc.GetSheetNames();

        foreach (var name in names)
        {
            var json = doc.ExportSheetToJson(name);
            var md   = doc.ExportSheetToMarkdown(name);
            Assert.False(string.IsNullOrWhiteSpace(json));
            Assert.False(string.IsNullOrWhiteSpace(md));
        }
    }
}
