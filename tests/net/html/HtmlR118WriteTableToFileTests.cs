// Tests for HtmlWriter.WriteTableToFile() — full HTML5 document file output.
// Sprint: FORMAT-FACTORY-HTML-WRITER-R118-20260626
// Ledger: R118-GOVERNED-DOTNET-HTML-WRITETABLETOFILE-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Html.Tests;

/// <summary>
/// R118: HtmlWriter.WriteTableToFile(rows, path, title, firstRowIsHeader) writes a
/// full HTML5 document to disk. File contains DOCTYPE, html, head, title, body, and
/// table elements. firstRowIsHeader controls th vs td for the first row.
/// UTF-8 without BOM; parent directories are created if absent.
/// </summary>
public class HtmlR118WriteTableToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_html_r118_{Guid.NewGuid():N}.html");

    private static List<IEnumerable<string?>> TwoColumnRows() =>
        new()
        {
            new[] { "Product", "Price" },
            new[] { "Widget",  "9.99"  },
            new[] { "Gadget",  "14.99" },
        };

    // ---- File existence ----

    [Fact]
    public void WriteTableToFile_ValidArgs_CreatesFile()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- DOCTYPE and root element ----

    [Fact]
    public void WriteTableToFile_Output_ContainsDoctype()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("<!DOCTYPE html>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteTableToFile_Output_ContainsHtmlElement()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("<html", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Head / title ----

    [Fact]
    public void WriteTableToFile_DefaultTitle_AppearsInTitleTag()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("<title>", content);
            Assert.Contains("FormatFactory", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteTableToFile_CustomTitle_AppearsInTitleTag()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path, title: "Inventory Report");
            var content = File.ReadAllText(path);
            Assert.Contains("Inventory Report", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Body and table structure ----

    [Fact]
    public void WriteTableToFile_Output_ContainsBodyElement()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("<body>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteTableToFile_Output_ContainsTableElement()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("<table>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Header row rendering ----

    [Fact]
    public void WriteTableToFile_FirstRowIsHeader_UsesThForFirstRow()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path, firstRowIsHeader: true);
            var content = File.ReadAllText(path);
            Assert.Contains("<th>Product</th>", content);
            Assert.Contains("<th>Price</th>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteTableToFile_FirstRowIsHeader_DataRowsUseTd()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path, firstRowIsHeader: true);
            var content = File.ReadAllText(path);
            Assert.Contains("<td>Widget</td>", content);
            Assert.Contains("<td>Gadget</td>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteTableToFile_NoHeader_AllRowsUseTd()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path, firstRowIsHeader: false);
            var content = File.ReadAllText(path);
            Assert.Contains("<td>Product</td>", content);
            Assert.DoesNotContain("<th>", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Encoding ----

    [Fact]
    public void WriteTableToFile_Encoding_NoUtf8Bom()
    {
        var path = TempPath();
        try
        {
            HtmlWriter.WriteTableToFile(TwoColumnRows(), path);
            var bytes = File.ReadAllBytes(path);
            // UTF-8 BOM is EF BB BF
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "File must not start with UTF-8 BOM");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Error handling ----

    [Fact]
    public void WriteTableToFile_NullOrEmptyPath_ThrowsHtmlWriterException()
    {
        Assert.Throws<HtmlWriterException>(() =>
            HtmlWriter.WriteTableToFile(TwoColumnRows(), string.Empty));
    }

    // ---- Dogfood: invoice document pipeline ----

    [Fact]
    public void DogfoodPipeline_InvoiceTable_AllFieldsInFile()
    {
        var path = TempPath();
        try
        {
            var rows = new List<IEnumerable<string?>>
            {
                new[] { "Item",       "Qty", "Unit Price", "Total"   },
                new[] { "Widget A",   "3",   "9.99",       "29.97"   },
                new[] { "Gadget B",   "1",   "49.99",      "49.99"   },
                new[] { "Service C",  "2",   "25.00",      "50.00"   },
            };

            HtmlWriter.WriteTableToFile(rows, path,
                title: "Invoice #2026-001",
                firstRowIsHeader: true);

            var content = File.ReadAllText(path);

            // Document structure
            Assert.Contains("<!DOCTYPE html>", content);
            Assert.Contains("Invoice #2026-001", content);
            Assert.Contains("<table>", content);

            // Header row
            Assert.Contains("<th>Item</th>", content);
            Assert.Contains("<th>Total</th>", content);

            // Data rows
            Assert.Contains("<td>Widget A</td>",  content);
            Assert.Contains("<td>Gadget B</td>",  content);
            Assert.Contains("<td>Service C</td>", content);
            Assert.Contains("<td>50.00</td>",     content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
