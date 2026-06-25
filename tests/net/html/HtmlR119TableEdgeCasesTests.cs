// Tests for HtmlWriter.WriteTable() edge cases: special characters, null cells, empty table.
// Sprint: FORMAT-FACTORY-HTML-WRITER-R119-20260626
// Ledger: R119-GOVERNED-DOTNET-HTML-TABLE-EDGECASES-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Html.Tests;

/// <summary>
/// R119: HtmlWriter.WriteTable() edge cases — special characters in cells are HTML-escaped,
/// null cell values produce empty td elements, empty row list produces a table tag with no rows,
/// single-cell table renders correctly, many-column rows all render as td/th.
/// </summary>
public class HtmlR119TableEdgeCasesTests
{
    // ---- Special character escaping in cells ----

    [Fact]
    public void WriteTable_CellWithAmpersand_EscapedInTd()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Tom & Jerry" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("&amp;", html);
        Assert.DoesNotContain("Tom & Jerry", html);
    }

    [Fact]
    public void WriteTable_CellWithLessThan_EscapedInTd()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "<em>bold</em>" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("&lt;", html);
        Assert.DoesNotContain("<em>", html);
    }

    [Fact]
    public void WriteTable_CellWithGreaterThan_EscapedInTd()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "a > b" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("&gt;", html);
    }

    [Fact]
    public void WriteTable_CellWithDoubleQuote_EscapedInTd()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "Say \"hello\"" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("&quot;", html);
    }

    // ---- Null cell values ----

    [Fact]
    public void WriteTable_NullCell_RendersEmptyTd()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { null } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<td></td>", html);
    }

    [Fact]
    public void WriteTable_MixedNullAndValue_BothRendered()
    {
        var rows = new List<IEnumerable<string?>> { new string?[] { "Alpha", null, "Gamma" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<td>Alpha</td>", html);
        Assert.Contains("<td></td>", html);
        Assert.Contains("<td>Gamma</td>", html);
    }

    // ---- Empty table ----

    [Fact]
    public void WriteTable_EmptyRowList_StillContainsTableTag()
    {
        var html = HtmlWriter.WriteTable(new List<IEnumerable<string?>>());
        Assert.Contains("<table>", html);
        Assert.DoesNotContain("<tr>", html);
    }

    // ---- Single-cell table ----

    [Fact]
    public void WriteTable_SingleCellSingleRow_RendersCorrectly()
    {
        var rows = new List<IEnumerable<string?>> { new[] { "OnlyCell" } };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<table>", html);
        Assert.Contains("<tr>", html);
        Assert.Contains("<td>OnlyCell</td>", html);
    }

    // ---- Many-column row ----

    [Fact]
    public void WriteTable_FiveColumnRow_AllCellsPresent()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "A", "B", "C", "D", "E" }
        };
        var html = HtmlWriter.WriteTable(rows);
        Assert.Contains("<td>A</td>", html);
        Assert.Contains("<td>B</td>", html);
        Assert.Contains("<td>C</td>", html);
        Assert.Contains("<td>D</td>", html);
        Assert.Contains("<td>E</td>", html);
    }

    // ---- firstRowIsHeader with special chars ----

    [Fact]
    public void WriteTable_HeaderRowWithSpecialChar_EscapedInTh()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Price <USD>", "Discount & Tax" },
            new[] { "100",         "10"              },
        };
        var html = HtmlWriter.WriteTable(rows, firstRowIsHeader: true);
        Assert.Contains("&lt;USD&gt;", html);
        Assert.Contains("&amp;", html);
        Assert.DoesNotContain("<USD>", html);
    }

    // ---- Dogfood: spreadsheet export with mixed special chars ----

    [Fact]
    public void DogfoodPipeline_SpreadsheetWithSpecialChars_AllEscapedCorrectly()
    {
        var rows = new List<IEnumerable<string?>>
        {
            new[] { "Column A",   "Formula",       "Notes"           },
            new[] { "Item & Tax", "=A1+B1",        "Value > 100"     },
            new[] { "<Draft>",    "\"quoted\"",    null              },
        };

        var html = HtmlWriter.WriteTable(rows, firstRowIsHeader: true);

        // Structure
        Assert.Contains("<table>", html);
        Assert.Contains("<th>Column A</th>", html);

        // Escaped data
        Assert.Contains("Item &amp; Tax", html);
        Assert.Contains("&lt;Draft&gt;",  html);
        Assert.Contains("&quot;quoted&quot;", html);
        Assert.Contains("Value &gt; 100", html);

        // Null cell
        Assert.Contains("<td></td>", html);
    }
}
