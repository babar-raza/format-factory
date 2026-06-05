// FormatFactory.Html.Tests — HtmlWriter unit tests
// Sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-MWP-DOGFOOD-UNBLOCKING-001

using System;
using System.Collections.Generic;
using System.IO;
using FormatFactory.Html;
using Xunit;

namespace FormatFactory.Html.Tests;

public class HtmlWriterTests
{
    // -------------------------------------------------------------------------
    // EscapeHtml
    // -------------------------------------------------------------------------

    [Fact]
    public void EscapeHtml_Null_ReturnsEmpty()
    {
        Assert.Equal(string.Empty, HtmlWriter.EscapeHtml(null));
    }

    [Fact]
    public void EscapeHtml_Ampersand_Escaped()
    {
        Assert.Contains("&amp;", HtmlWriter.EscapeHtml("a&b"));
    }

    [Fact]
    public void EscapeHtml_LessThan_Escaped()
    {
        Assert.Contains("&lt;", HtmlWriter.EscapeHtml("a<b"));
    }

    [Fact]
    public void EscapeHtml_GreaterThan_Escaped()
    {
        Assert.Contains("&gt;", HtmlWriter.EscapeHtml("a>b"));
    }

    [Fact]
    public void EscapeHtml_DoubleQuote_Escaped()
    {
        Assert.Contains("&quot;", HtmlWriter.EscapeHtml("a\"b"));
    }

    [Fact]
    public void EscapeHtml_PlainText_Unchanged()
    {
        Assert.Equal("hello world", HtmlWriter.EscapeHtml("hello world"));
    }

    // -------------------------------------------------------------------------
    // WriteTable — in-memory
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteTable_SingleRow_ContainsTableAndTd()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "a", "b" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<table>", html);
        Assert.Contains("<td>a</td>", html);
        Assert.Contains("<td>b</td>", html);
    }

    [Fact]
    public void WriteTable_FirstRowIsHeader_UsesTh()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Name", "Value" },
            new[] { "x", "1" },
        };
        var html = HtmlWriter.WriteTable(rows, firstRowIsHeader: true);
        Assert.Contains("<th>Name</th>", html);
        Assert.Contains("<th>Value</th>", html);
        Assert.Contains("<td>x</td>", html);
    }

    [Fact]
    public void WriteTable_HtmlSpecialChars_Escaped()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "<script>" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.DoesNotContain("<script>", html.Replace("<table>", "").Replace("</table>", "")
            .Replace("<tr>", "").Replace("</tr>", "").Replace("<td>", "").Replace("</td>", ""));
        Assert.Contains("&lt;script&gt;", html);
    }

    [Fact]
    public void WriteTable_NullCell_EmptyTd()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { null } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<td></td>", html);
    }

    // -------------------------------------------------------------------------
    // WriteTableToFile — physical file output
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteTableToFile_CreatesFile()
    {
        var path = Path.Combine(Path.GetTempPath(), $"ff_html_test_{Guid.NewGuid():N}.html");
        try
        {
            var rows = new List<IEnumerable<string?>> { new[] { "a", "b" } };
            HtmlWriter.WriteTableToFile(rows, path);
            Assert.True(File.Exists(path));
            var content = File.ReadAllText(path);
            Assert.Contains("<!DOCTYPE html>", content);
            Assert.Contains("<td>a</td>", content);
        }
        finally
        {
            if (File.Exists(path)) File.Delete(path);
        }
    }

    [Fact]
    public void WriteTableToFile_NullPath_Throws()
    {
        Assert.Throws<HtmlWriterException>(() =>
            HtmlWriter.WriteTableToFile(new List<IEnumerable<string?>>(), null!));
    }
}
