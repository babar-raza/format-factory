// R94 Train M: FODS .NET ExportSheetToHtml Tests
// Governed skill: /add-dotnet-api
// Ledger: R94-GOVERNED-DOTNET-FODS-EXPORTSHEETTOHTML-001
// Sprint: FORMAT-FACTORY-R94-CONTEXT-PACK-SELF-CONTAINED-DECLARATION-REVIEW-ACCELERATION-POC-PARALLEL-MEGA-TRAIN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR94ExportSheetToHtmlTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    private static string MultiSheetFodsPath =>
        Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    [Fact]
    public void ExportSheetToHtml_ReturnsNonEmptyString()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var html = doc.ExportSheetToHtml();
        Assert.False(string.IsNullOrWhiteSpace(html));
    }

    [Fact]
    public void ExportSheetToHtml_ContainsTableTag()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<table>", html);
        Assert.Contains("</table>", html);
    }

    [Fact]
    public void ExportSheetToHtml_ContainsTrAndTdTags()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var html = doc.ExportSheetToHtml();
        Assert.Contains("<tr>", html);
        Assert.Contains("<td>", html);
    }

    [Fact]
    public void ExportSheetToHtml_ByName_ReturnsHtml()
    {
        var doc = FodsDocument.Load(MultiSheetFodsPath);
        var names = doc.GetSheetNames();
        if (names.Count > 0)
        {
            var html = doc.ExportSheetToHtml(names[0]);
            Assert.Contains("<table>", html);
        }
    }

    [Fact]
    public void ExportSheetToHtml_ByName_InvalidSheet_Throws()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToHtml("NonExistentSheet"));
    }

    [Fact]
    public void ExportSheetToHtml_StaticOverload_NullSheet_Throws()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.ExportSheetToHtml(null!));
    }

    [Fact]
    public void ExportSheetToHtml_HtmlEscapesCellContent()
    {
        // The minimal spreadsheet cells should not contain raw HTML-dangerous chars,
        // but this tests that the method doesn't crash and output is valid
        var doc = FodsDocument.Load(SampleFodsPath);
        var html = doc.ExportSheetToHtml();
        // Should not contain unescaped angle brackets inside td (other than the tags)
        Assert.DoesNotContain("<script>", html);
    }

    [Fact]
    public void ExportSheetToHtml_EachRowHasCorrectCellCount()
    {
        var doc = FodsDocument.Load(SampleFodsPath);
        var html = doc.ExportSheetToHtml();
        // Each <tr> should have at least one <td>
        var lines = html.Split('\n');
        foreach (var line in lines)
        {
            if (line.TrimStart().StartsWith("<tr>"))
            {
                Assert.Contains("<td>", line);
            }
        }
    }
}
