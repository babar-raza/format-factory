// R101 Train A: FODS .NET ExportSheetToMarkdown tests
// Governed skill: /add-dotnet-object-model-feature
// Ledger: R101-GOVERNED-DOTNET-FODS-EXPORTSHEETTOMARKDOWN-001

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsR101ExportSheetToMarkdownTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string MinimalPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void ExportSheetToMarkdown_FirstSheet_ContainsPipeHeaders()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
        Assert.Contains("---", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsSeparatorLine()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var md = doc.ExportSheetToMarkdown();
        var lines = md.Split('\n', StringSplitOptions.RemoveEmptyEntries);
        Assert.True(lines.Length >= 2, "Markdown table must have at least header + separator");
        Assert.Contains("---", lines[1]);
    }

    [Fact]
    public void ExportSheetToMarkdown_ByName_MatchesFirstSheet()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheetName = doc.GetSheetNames()[0];
        var mdFirst = doc.ExportSheetToMarkdown();
        var mdNamed = doc.ExportSheetToMarkdown(sheetName);
        Assert.Equal(mdFirst, mdNamed);
    }

    [Fact]
    public void ExportSheetToMarkdown_NonexistentSheet_Throws()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Throws<ArgumentException>(() => doc.ExportSheetToMarkdown("NoSuchSheet"));
    }

    [Fact]
    public void ExportSheetToMarkdown_PipeInValue_Escaped()
    {
        var doc = FodsDocument.Load(MinimalPath);
        // Set a cell value containing a pipe character
        doc.SetCellValue(0, 0, "A|B");
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("A\\|B", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_StaticOverload_Works()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var sheet = doc.Sheets[0];
        var md = FodsDocument.ExportSheetToMarkdown(sheet);
        Assert.NotEmpty(md);
        Assert.Contains("|", md);
    }

    [Fact]
    public void ExportSheetToMarkdown_EmptySheet_ReturnsEmpty()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var newSheet = doc.AddSheet("EmptyMd");
        var md = FodsDocument.ExportSheetToMarkdown(newSheet);
        Assert.Equal(string.Empty, md);
    }

    [Fact]
    public void ExportSheetToMarkdown_RoundTrip_PreservesData()
    {
        var doc = FodsDocument.Load(MinimalPath);
        var tmp = Path.GetTempFileName() + ".fods";
        try
        {
            doc.Save(tmp);
            var reloaded = FodsDocument.Load(tmp);
            var md1 = doc.ExportSheetToMarkdown();
            var md2 = reloaded.ExportSheetToMarkdown();
            Assert.Equal(md1, md2);
        }
        finally { if (File.Exists(tmp)) File.Delete(tmp); }
    }
}
