// FormatFactory.Fods Tests -- FodsHtmlExporter G11-E Expanded Prototype Tests
// Sprint: FORMAT-FACTORY-R23-MEGA-TRAIN-001
// Gate 11 status: g11e_prototype_complete — G11-G NOT approved
// commercial_product_ready: false

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Tests for the G11-E FODS → HTML export prototype.
/// Tests cover: basic export, HTML structure, escaping, null guards.
/// All tests use local fixture files only — no network.
/// </summary>
public class FodsHtmlExporterTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fods/Fixtures"));

    private static readonly string MinimalFods =
        Path.Combine(FixturesDir, "fods-minimal-roundtrip.fods");

    private readonly string _tempDir;

    public FodsHtmlExporterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fods-html-export-tests-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    // -------------------------------------------------------------------------
    // Null guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_NullFodsPath_Throws()
    {
        Assert.Throws<FodsHtmlExportException>(() =>
            FodsHtmlExporter.ExportToHtml(null!, Path.Combine(_tempDir, "out.html")));
    }

    [Fact]
    public void ExportToHtml_EmptyFodsPath_Throws()
    {
        Assert.Throws<FodsHtmlExportException>(() =>
            FodsHtmlExporter.ExportToHtml("", Path.Combine(_tempDir, "out.html")));
    }

    [Fact]
    public void ExportToHtml_NullHtmlPath_Throws()
    {
        Assert.Throws<FodsHtmlExportException>(() =>
            FodsHtmlExporter.ExportToHtml(MinimalFods, null!));
    }

    [Fact]
    public void ExportToHtml_NonExistentFodsPath_Throws()
    {
        Assert.Throws<FodsHtmlExportException>(() =>
            FodsHtmlExporter.ExportToHtml(
                Path.Combine(_tempDir, "nonexistent.fods"),
                Path.Combine(_tempDir, "out.html")));
    }

    // -------------------------------------------------------------------------
    // HtmlEscape unit tests
    // -------------------------------------------------------------------------

    [Fact]
    public void HtmlEscape_Null_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodsHtmlExporter.HtmlEscape(null));
    }

    [Fact]
    public void HtmlEscape_Empty_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, FodsHtmlExporter.HtmlEscape(""));
    }

    [Fact]
    public void HtmlEscape_PlainText_ReturnedAsIs()
    {
        Assert.Equal("hello", FodsHtmlExporter.HtmlEscape("hello"));
    }

    [Fact]
    public void HtmlEscape_LtGt_EscapedCorrectly()
    {
        var result = FodsHtmlExporter.HtmlEscape("<b>bold</b>");
        Assert.DoesNotContain("<b>", result);
        Assert.Contains("&lt;", result);
        Assert.Contains("&gt;", result);
    }

    [Fact]
    public void HtmlEscape_Ampersand_EscapedCorrectly()
    {
        var result = FodsHtmlExporter.HtmlEscape("A & B");
        Assert.Contains("&amp;", result);
        Assert.DoesNotContain(" & ", result);
    }

    [Fact]
    public void HtmlEscape_DoubleQuote_EscapedCorrectly()
    {
        var result = FodsHtmlExporter.HtmlEscape("say \"hi\"");
        Assert.DoesNotContain("\"", result);
    }

    // -------------------------------------------------------------------------
    // Integration tests (using fixture)
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_MinimalFods_CreatesHtmlFile()
    {
        var outHtml = Path.Combine(_tempDir, "minimal.html");
        var result = FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        Assert.True(File.Exists(outHtml), "HTML output file must be created");
        Assert.Equal("exported", result.Status);
        Assert.Equal(outHtml, result.OutputPath);
    }

    [Fact]
    public void ExportToHtml_MinimalFods_ContainsDoctype()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("<!DOCTYPE html>", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFods_ContainsCharsetUtf8()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("UTF-8", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFods_ContainsTableElement()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("<table", text);
    }

    [Fact]
    public void ExportToHtml_MinimalFods_OutputNonEmpty()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var info = new FileInfo(outHtml);
        Assert.True(info.Length > 0, "HTML output file must be non-empty");
    }

    [Fact]
    public void ExportToHtml_MinimalFods_HasBodyTag()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("<body>", text);
        Assert.Contains("</body>", text);
    }

    // -------------------------------------------------------------------------
    // Governance tests
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToHtml_Prototype_CommentInOutput()
    {
        // G11-E prototype governance: output must contain prototype marker
        var outHtml = Path.Combine(_tempDir, "out.html");
        FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        var text = File.ReadAllText(outHtml);
        Assert.Contains("commercial_product_ready=false", text);
    }

    [Fact]
    public void ExportToHtml_ResultStatus_IsExportedOrEmpty()
    {
        var outHtml = Path.Combine(_tempDir, "out.html");
        var result = FodsHtmlExporter.ExportToHtml(MinimalFods, outHtml);

        Assert.True(
            result.Status == "exported" ||
            result.Status == "exported_empty_no_sheets",
            $"Status must be 'exported' or 'exported_empty_no_sheets', got: {result.Status}");
    }
}
