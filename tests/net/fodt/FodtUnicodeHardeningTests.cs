// FormatFactory.Fodt Tests -- Unicode and Escaping Hardening (G11-E Expanded Prototype)
// Sprint: FORMAT-FACTORY-R24-PARALLEL-CLOSURE-REPAIR-FORWARD-TRAIN-AND-AI-PLATFORM-PLAN-001
// Gate 11 status: commercial_readiness_in_progress — G11-G NOT approved
// commercial_product_ready: false
//
// Hardening test: verifies HTML and Markdown exporters handle Unicode content correctly.
// Tests prototype-level behaviour only — no commercial readiness claim.

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// G11-E hardening: Unicode and HTML-escaping tests.
/// Validates HTML and Markdown exporters correctly handle:
/// - Accented Latin characters (é = U+00E9)
/// - CJK characters (中文)
/// - HTML-special characters (&amp; &lt; &gt; &quot;)
/// Prototype status — no commercial readiness claim.
/// </summary>
public class FodtUnicodeHardeningTests : IDisposable
{
    private static readonly string FixturesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../tests/net/fodt/Fixtures"));

    private static readonly string UnicodeFodt =
        Path.Combine(FixturesDir, "fodt-unicode.fodt");

    private readonly string _tempDir;

    public FodtUnicodeHardeningTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(),
            "fodt-unicode-hardening-" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string ExportHtml()
    {
        var outPath = Path.Combine(_tempDir, "unicode.html");
        FodtHtmlExporter.ExportToHtml(UnicodeFodt, outPath);
        return File.ReadAllText(outPath);
    }

    private string ExportMarkdown()
    {
        var outPath = Path.Combine(_tempDir, "unicode.md");
        FodtMarkdownExporter.ExportToMarkdown(UnicodeFodt, outPath);
        return File.ReadAllText(outPath);
    }

    [Fact]
    public void HtmlExporter_Unicode_ContainsAccentedCharacter()
    {
        var html = ExportHtml();
        // "Café au lait" — é should be present (UTF-8 or as &#233; or &eacute;)
        Assert.True(
            html.Contains("Caf\u00e9") || html.Contains("Caf&#233;") || html.Contains("Caf&eacute;"),
            $"Expected 'Café' in HTML output. Got snippet: {html.Substring(0, Math.Min(300, html.Length))}");
    }

    [Fact]
    public void HtmlExporter_Unicode_ContainsCjkCharacters()
    {
        var html = ExportHtml();
        // Chinese text "中文" — must appear
        Assert.True(
            html.Contains("\u4e2d\u6587") ||
            html.Contains("&#20013;&#25991;") ||
            html.Contains("&#x4e2d;&#x6587;"),
            "Expected CJK characters in HTML output");
    }

    [Fact]
    public void HtmlExporter_Unicode_AmpersandIsEscaped()
    {
        var html = ExportHtml();
        // The text content "HTML entities: & < > \"" (after XML parse) must have & escaped
        Assert.Contains("&amp;", html);
    }

    [Fact]
    public void HtmlExporter_Unicode_LessThanIsEscaped()
    {
        var html = ExportHtml();
        // < must appear as &lt;
        Assert.Contains("&lt;", html);
    }

    [Fact]
    public void HtmlExporter_Unicode_GreaterThanIsEscaped()
    {
        var html = ExportHtml();
        // > must appear as &gt;
        Assert.Contains("&gt;", html);
    }

    [Fact]
    public void HtmlExporter_Unicode_IsWellFormedHtml()
    {
        var html = ExportHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);
        // Minimal HTML structure check
        Assert.True(
            html.ToLower().Contains("<html") || html.Contains("<!DOCTYPE"),
            "Expected HTML structure in output");
    }

    [Fact]
    public void MarkdownExporter_Unicode_ContainsAccentedCharacter()
    {
        var md = ExportMarkdown();
        Assert.True(
            md.Contains("Caf\u00e9") || md.Contains("Caf&#233;"),
            "Expected 'Café' in Markdown output");
    }

    [Fact]
    public void MarkdownExporter_Unicode_IsNonEmpty()
    {
        var md = ExportMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);
    }
}
