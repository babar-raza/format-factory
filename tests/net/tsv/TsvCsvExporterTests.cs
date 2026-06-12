// FormatFactory.Tsv.Tests — TsvCsvExporter unit tests

using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

public class TsvCsvExporterTests
{
    [Fact]
    public void Export_SimpleDocument_ProducesCsv()
    {
        var doc = TsvDocument.Load("Name\tAge\nAlice\t30\nBob\t25\n");
        var csv = TsvCsvExporter.Export(doc);
        Assert.Equal("Name,Age\nAlice,30\nBob,25\n", csv);
    }

    [Fact]
    public void Export_FieldRequiresQuoting_CommaQuoted()
    {
        // Build a doc where a data field contains a comma
        var doc = new TsvDocument
        {
            HasHeaders = true,
            Headers = new[] { "Name", "Notes" },
            Rows = new List<string[]>
            {
                new[] { "Alice", "hello, world" },
            }
        };
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains("\"hello, world\"", csv);
        Assert.Equal("Name,Notes\nAlice,\"hello, world\"\n", csv);
    }

    [Fact]
    public void Export_FieldWithDoubleQuote_EscapedCorrectly()
    {
        var doc = new TsvDocument
        {
            HasHeaders = true,
            Headers = new[] { "Col" },
            Rows = new List<string[]>
            {
                new[] { "say \"hi\"" },
            }
        };
        var csv = TsvCsvExporter.Export(doc);
        Assert.Contains("\"say \"\"hi\"\"\"", csv);
    }

    [Fact]
    public void Export_EmptyDocument_ReturnsEmptyString()
    {
        var doc = TsvDocument.Load("", hasHeaders: false);
        var csv = TsvCsvExporter.Export(doc);
        Assert.Equal(string.Empty, csv);
    }

    [Fact]
    public void Export_NoHeaders_DataOnly()
    {
        var doc = TsvDocument.Load("a\tb\n1\t2\n", hasHeaders: false);
        var csv = TsvCsvExporter.Export(doc);
        Assert.Equal("a,b\n1,2\n", csv);
    }

    [Fact]
    public void Export_NullDoc_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => TsvCsvExporter.Export(null!));
    }
}
