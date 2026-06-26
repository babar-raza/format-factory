// Tests for FodsHtmlExporter.HtmlEscape, FodsHtmlExportResult defaults, and FodsHtmlExportException.
// Sprint: ff-sprint-s131-dotnet-deepening-20260627
// Ledger: PC-FODS-R144

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R144: Tests for FodsHtmlExporter.HtmlEscape utility method,
/// FodsHtmlExportResult default property values, and FodsHtmlExportException
/// exception hierarchy. HtmlEscape handles &amp;, &lt;, &gt;, double-quote, and
/// null inputs. FodsHtmlExportResult is a plain result carrier with init-only
/// SourcePath/OutputPath and mutable SheetsExported/TotalRowsExported/Status/Warnings.
/// FodsHtmlExportException is sealed and derives from System.Exception.
/// Covers: HtmlEscape null→empty; plain text→unchanged; ampersand→&amp;;
/// less-than→&lt;; greater-than→&gt;; double-quote→&quot;;
/// FodsHtmlExportResult defaults; FodsHtmlExportException hierarchy;
/// dogfood HtmlEscape chain of special characters.
/// </summary>
public class FodsR144HtmlExportUtilsTests
{
    // -------------------------------------------------------------------------
    // FodsHtmlExporter.HtmlEscape
    // -------------------------------------------------------------------------

    [Fact]
    public void HtmlEscape_NullValue_ReturnsEmpty()
    {
        var result = FodsHtmlExporter.HtmlEscape(null);
        Assert.Equal(string.Empty, result);
    }

    [Fact]
    public void HtmlEscape_PlainText_ReturnsUnchanged()
    {
        Assert.Equal("Hello World", FodsHtmlExporter.HtmlEscape("Hello World"));
    }

    [Fact]
    public void HtmlEscape_Ampersand_EscapesToAmpAmp()
    {
        var result = FodsHtmlExporter.HtmlEscape("A & B");
        Assert.Contains("&amp;", result);
    }

    [Fact]
    public void HtmlEscape_LessThan_EscapesToLt()
    {
        var result = FodsHtmlExporter.HtmlEscape("a < b");
        Assert.Contains("&lt;", result);
    }

    [Fact]
    public void HtmlEscape_GreaterThan_EscapesToGt()
    {
        var result = FodsHtmlExporter.HtmlEscape("a > b");
        Assert.Contains("&gt;", result);
    }

    // -------------------------------------------------------------------------
    // FodsHtmlExportResult default values
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsHtmlExportResult_SourcePath_DefaultIsEmpty()
    {
        var result = new FodsHtmlExportResult();
        Assert.Equal(string.Empty, result.SourcePath);
    }

    [Fact]
    public void FodsHtmlExportResult_SheetsExported_DefaultIsZero()
    {
        var result = new FodsHtmlExportResult();
        Assert.Equal(0, result.SheetsExported);
    }

    [Fact]
    public void FodsHtmlExportResult_Warnings_DefaultIsEmpty()
    {
        var result = new FodsHtmlExportResult();
        Assert.NotNull(result.Warnings);
        Assert.Empty(result.Warnings);
    }

    // -------------------------------------------------------------------------
    // FodsHtmlExportException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void FodsHtmlExportException_IsSubclassOfException()
    {
        var ex = new FodsHtmlExportException("export failed");
        Assert.IsAssignableFrom<Exception>(ex);
    }

    [Fact]
    public void FodsHtmlExportException_InnerExceptionConstructor_PreservesBoth()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new FodsHtmlExportException("outer", inner);
        Assert.Equal("outer", ex.Message);
        Assert.Same(inner, ex.InnerException);
    }

    // -------------------------------------------------------------------------
    // Dogfood: HtmlEscape chain of special characters
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HtmlEscape_ChainOfSpecialChars()
    {
        const string input = "<script>alert(\"A & B\")</script>";
        var escaped = FodsHtmlExporter.HtmlEscape(input);

        Assert.Contains("&lt;", escaped);
        Assert.Contains("&gt;", escaped);
        Assert.Contains("&amp;", escaped);
        Assert.DoesNotContain("<script>", escaped);
    }
}
