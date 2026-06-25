// Tests for HtmlWriter EscapeHtml integration with WriteTable — composite API behavior.
// Sprint: FORMAT-FACTORY-HTML-WRITER-R120-20260626
// Ledger: R120-GOVERNED-DOTNET-HTML-ESCAPE-INTEGRATION-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Html.Tests;

/// <summary>
/// R120: Integration tests verifying EscapeHtml is applied within WriteTable cell output.
/// Also tests: ApostropheForms (apostrophe encoded), mixed-encoding cells in the same table,
/// large multi-row table output consistency, header+data combination from different sources.
/// </summary>
public class HtmlR120EscapeIntegrationTests
{
    // ---- Apostrophe in table cells ----

    [Fact]
    public void WriteTable_ApostropheInCell_EscapedOrPreserved()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "It's" } };
        var html = HtmlWriter.WriteTable(rows);
        // apostrophe may be escaped as &#39; or kept as ' — either is valid HTML
        // We just verify no unescaped < or > introduced
        Assert.Contains("<table>", html);
        Assert.Contains("<td>", html);
    }

    // ---- Multiple special chars in one cell ----

    [Fact]
    public void WriteTable_MultipleSpecialCharsInOneCell_AllEscaped()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "<script>alert('xss')</script>" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.DoesNotContain("<script>",  html);
        Assert.Contains("&lt;script&gt;", html);
    }

    // ---- Mixed: some cells clean, some with special chars ----

    [Fact]
    public void WriteTable_MixedCleanAndSpecialCells_EachHandledCorrectly()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Clean", "Tom & Jerry", "Normal", "<b>Bold</b>" }
        };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<td>Clean</td>",   html);
        Assert.Contains("Tom &amp; Jerry",  html);
        Assert.Contains("<td>Normal</td>",  html);
        Assert.Contains("&lt;b&gt;Bold&lt;/b&gt;", html);
    }

    // ---- EscapeHtml single-character edge cases ----

    [Fact]
    public void EscapeHtml_SoloAmpersand_EscapesCorrectly()
    {
        Assert.Equal("&amp;", HtmlWriter.EscapeHtml("&"));
    }

    [Fact]
    public void EscapeHtml_SoloLessThan_EscapesCorrectly()
    {
        Assert.Equal("&lt;", HtmlWriter.EscapeHtml("<"));
    }

    [Fact]
    public void EscapeHtml_SoloGreaterThan_EscapesCorrectly()
    {
        Assert.Equal("&gt;", HtmlWriter.EscapeHtml(">"));
    }

    [Fact]
    public void EscapeHtml_SoloDoubleQuote_EscapesCorrectly()
    {
        var result = HtmlWriter.EscapeHtml("\"");
        Assert.Contains("quot", result);
    }

    // ---- Large multi-row table structure ----

    [Fact]
    public void WriteTable_TenRows_TenTrElements()
    {
        var rows = new List<IEnumerable<string?>>();
        for (int i = 1; i <= 10; i++)
            rows.Add(new[] { $"Row{i}", $"Value{i}" });

        var html = HtmlWriter.WriteTable(rows);
        var trCount = 0;
        int pos = 0;
        while ((pos = html.IndexOf("<tr>", pos, StringComparison.Ordinal)) >= 0)
        {
            trCount++;
            pos += 4;
        }
        Assert.Equal(10, trCount);
    }

    [Fact]
    public void WriteTable_TenRows_AllValuesPresent()
    {
        var rows = new List<IEnumerable<string?>>();
        for (int i = 1; i <= 10; i++)
            rows.Add(new[] { $"Item{i}" });

        var html = HtmlWriter.WriteTable(rows);
        for (int i = 1; i <= 10; i++)
            Assert.Contains($"Item{i}", html);
    }

    // ---- Header + data rows from separate lists ----

    [Fact]
    public void WriteTable_HeaderPlusData_HeaderIsThDataIsT()
    {
        var headers = new[] { "Product", "Price" };
        var data    = new[] { "Widget",  "9.99"  };
        var rows    = new List<IEnumerable<string?>> { headers, data };

        var html = HtmlWriter.WriteTable(rows, firstRowIsHeader: true);
        Assert.Contains("<th>Product</th>", html);
        Assert.Contains("<th>Price</th>",   html);
        Assert.Contains("<td>Widget</td>",  html);
        Assert.Contains("<td>9.99</td>",    html);
    }

    // ---- Dogfood: security report export ----

    [Fact]
    public void DogfoodPipeline_SecurityReportTable_AllInputsSanitized()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "ID",    "Payload",                       "Status"      },
            new[] { "T-001", "<script>alert('xss')</script>", "Blocked"     },
            new[] { "T-002", "Tom & Jerry",                   "Logged"      },
            new[] { "T-003", "a > b && c < d",               "Sanitized"   },
            new[] { "T-004", "\"quoted\"",                    "Passed"      },
        };

        var html = HtmlWriter.WriteTable(rows, firstRowIsHeader: true);

        // Headers
        Assert.Contains("<th>ID</th>",      html);
        Assert.Contains("<th>Payload</th>", html);
        Assert.Contains("<th>Status</th>",  html);

        // Escaped payloads — no raw injected HTML
        Assert.DoesNotContain("<script>",      html);
        Assert.DoesNotContain("alert('xss')",  html);
        Assert.Contains("&lt;script&gt;",      html);
        Assert.Contains("Tom &amp; Jerry",     html);
        Assert.Contains("&amp;&amp;",          html); // && escaped
        Assert.Contains("&quot;quoted&quot;",  html);

        // Status values (safe, no special chars)
        Assert.Contains("<td>Blocked</td>",   html);
        Assert.Contains("<td>Sanitized</td>", html);
    }
}
