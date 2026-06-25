// Tests for HtmlWriter static API: EscapeHtml, WriteHeading, WriteParagraphs, WriteTable.
// Sprint: FORMAT-FACTORY-HTML-WRITER-R117-20260626
// Ledger: R117-GOVERNED-DOTNET-HTML-WRITER-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Html.Tests;

/// <summary>
/// R117: HtmlWriter static API — EscapeHtml(value) escapes HTML special characters.
/// WriteHeading(text, level) produces H1-H6 tags. WriteParagraphs(lines) wraps
/// each string in &lt;p&gt; tags. WriteTable(headers, rows) produces an HTML table
/// with &lt;table&gt;/&lt;tr&gt;/&lt;th&gt;/&lt;td&gt; structure.
/// </summary>
public class HtmlR117WriterTests
{
    // ---- EscapeHtml ----

    [Fact]
    public void EscapeHtml_PlainText_ReturnsUnchanged()
    {
        var result = HtmlWriter.EscapeHtml("Hello World");
        Assert.Equal("Hello World", result);
    }

    [Fact]
    public void EscapeHtml_Ampersand_EscapesToAmp()
    {
        var result = HtmlWriter.EscapeHtml("Tom & Jerry");
        Assert.Contains("&amp;", result);
        Assert.DoesNotContain(" & ", result);
    }

    [Fact]
    public void EscapeHtml_LessThan_EscapesToLt()
    {
        var result = HtmlWriter.EscapeHtml("<bold>");
        Assert.Contains("&lt;", result);
    }

    [Fact]
    public void EscapeHtml_GreaterThan_EscapesToGt()
    {
        var result = HtmlWriter.EscapeHtml("5 > 3");
        Assert.Contains("&gt;", result);
    }

    [Fact]
    public void EscapeHtml_NullInput_DoesNotThrow()
    {
        var result = HtmlWriter.EscapeHtml(null);
        Assert.NotNull(result);
    }

    // ---- WriteHeading ----

    [Fact]
    public void WriteHeading_Level1_ProducesH1Tag()
    {
        var html = HtmlWriter.WriteHeading("Main Title", level: 1);
        Assert.Contains("<h1>", html, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("</h1>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void WriteHeading_Level2_ProducesH2Tag()
    {
        var html = HtmlWriter.WriteHeading("Section", level: 2);
        Assert.Contains("<h2>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void WriteHeading_ContentInTag()
    {
        var html = HtmlWriter.WriteHeading("My Heading", level: 1);
        Assert.Contains("My Heading", html);
    }

    // ---- WriteParagraphs ----

    [Fact]
    public void WriteParagraphs_SingleString_ContainsPTag()
    {
        var html = HtmlWriter.WriteParagraphs(new[] { "Hello paragraph" });
        Assert.Contains("<p>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void WriteParagraphs_MultipleStrings_AllContentPresent()
    {
        var html = HtmlWriter.WriteParagraphs(new[] { "Alpha", "Beta", "Gamma" });
        Assert.Contains("Alpha", html);
        Assert.Contains("Beta", html);
        Assert.Contains("Gamma", html);
    }

    // ---- WriteTable ----

    [Fact]
    public void WriteTable_ProducesTableTag()
    {
        var headers = new[] { "Name", "Score" };
        var rows    = new List<IEnumerable<string?>> { new[] { "Alice", "90" } };
        var html    = HtmlWriter.WriteTable(headers, rows);
        Assert.Contains("<table>", html, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void WriteTable_HeadersInThTags()
    {
        var headers = new[] { "Name", "Score" };
        var rows    = new List<IEnumerable<string?>> { new[] { "Alice", "90" } };
        var html    = HtmlWriter.WriteTable(headers, rows);
        Assert.Contains("<th>", html, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Name", html);
        Assert.Contains("Score", html);
    }

    [Fact]
    public void WriteTable_DataInTdTags()
    {
        var headers = new[] { "Name", "Score" };
        var rows    = new List<IEnumerable<string?>> { new[] { "Alice", "90" } };
        var html    = HtmlWriter.WriteTable(headers, rows);
        Assert.Contains("<td>", html, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Alice", html);
    }

    // ---- Dogfood: combined HTML document ----

    [Fact]
    public void DogfoodPipeline_HeadingParagraphsTable_AllPresent()
    {
        var heading    = HtmlWriter.WriteHeading("Report", level: 1);
        var paragraphs = HtmlWriter.WriteParagraphs(new[] { "Introduction.", "Summary." });
        var headers    = new[] { "Item", "Value" };
        var rows       = new List<IEnumerable<string?>> { new[] { "Total", "42" } };
        var table      = HtmlWriter.WriteTable(headers, rows);

        var doc = heading + paragraphs + table;

        Assert.Contains("<h1>", doc, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Report", doc);
        Assert.Contains("Introduction.", doc);
        Assert.Contains("<table>", doc, StringComparison.OrdinalIgnoreCase);
        Assert.Contains("Total", doc);
        Assert.Contains("42", doc);
    }
}
