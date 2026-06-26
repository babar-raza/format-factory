// Tests for TsvReader.ReadRows(Stream stream) — stream-based TSV reading.
// Sprint: FORMAT-FACTORY-TSV-R124-20260627
// Ledger: R124-GOVERNED-DOTNET-TSV-STREAM-READ-ROWS-001

using System;
using System.IO;
using System.Text;
using FormatFactory.Tsv;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R124: Tests for TsvReader.ReadRows(Stream stream) — the stream-based read overload.
/// Covers: non-empty rows from MemoryStream; column count; row count; tab splitting;
/// parity with string-based ReadRows; empty stream returns empty list; CRLF tolerance;
/// UTF-8 BOM stripped; null stream throws ArgumentNullException; dogfood analytics pipeline.
/// </summary>
public class TsvR124StreamReadRowsTests
{
    private static Stream ToStream(string content)
        => new MemoryStream(Encoding.UTF8.GetBytes(content));

    private const string ThreeLine =
        "Name\tAge\tCity\n" +
        "Alice\t30\tSeattle\n" +
        "Bob\t25\tDenver\n";

    // -------------------------------------------------------------------------
    // Basic stream read
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_ReturnsNonEmptyList()
    {
        using var ms = ToStream(ThreeLine);
        var rows = TsvReader.ReadRows(ms);
        Assert.NotEmpty(rows);
    }

    [Fact]
    public void ReadRows_Stream_RowCountMatchesStringVersion()
    {
        var stringRows = TsvReader.ReadRows(ThreeLine);
        using var ms = ToStream(ThreeLine);
        var streamRows = TsvReader.ReadRows(ms);
        Assert.Equal(stringRows.Count, streamRows.Count);
    }

    [Fact]
    public void ReadRows_Stream_ColumnCountIsThree()
    {
        using var ms = ToStream(ThreeLine);
        var rows = TsvReader.ReadRows(ms);
        Assert.Equal(3, rows[0].Length);
    }

    [Fact]
    public void ReadRows_Stream_FirstRowIsHeader()
    {
        using var ms = ToStream(ThreeLine);
        var rows = TsvReader.ReadRows(ms);
        Assert.Equal("Name", rows[0][0]);
        Assert.Equal("Age", rows[0][1]);
        Assert.Equal("City", rows[0][2]);
    }

    [Fact]
    public void ReadRows_Stream_SecondRowIsFirstData()
    {
        using var ms = ToStream(ThreeLine);
        var rows = TsvReader.ReadRows(ms);
        Assert.Equal("Alice", rows[1][0]);
        Assert.Equal("30", rows[1][1]);
    }

    // -------------------------------------------------------------------------
    // Edge cases
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_EmptyStream_ReturnsEmptyList()
    {
        using var ms = ToStream(string.Empty);
        var rows = TsvReader.ReadRows(ms);
        Assert.Empty(rows);
    }

    [Fact]
    public void ReadRows_Stream_CrlfLineEnding_ParsedCorrectly()
    {
        using var ms = ToStream("a\tb\r\n1\t2\r\n");
        var rows = TsvReader.ReadRows(ms);
        Assert.Equal(2, rows.Count);
        Assert.Equal("a", rows[0][0]);
        Assert.Equal("1", rows[1][0]);
    }

    [Fact]
    public void ReadRows_Stream_BomPrefixed_BomStripped()
    {
        // UTF-8 BOM prefix
        var withBom = new byte[] { 0xEF, 0xBB, 0xBF }
            .Concat(Encoding.UTF8.GetBytes("x\ty\n1\t2\n"))
            .ToArray();
        using var ms = new MemoryStream(withBom);
        var rows = TsvReader.ReadRows(ms);
        Assert.Equal("x", rows[0][0]);
    }

    [Fact]
    public void ReadRows_Stream_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => TsvReader.ReadRows((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Dogfood: stream load → TsvDocument pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_StreamRows_BuildTsvDocument()
    {
        const string content =
            "product\tqty\tprice\n" +
            "Widget\t10\t9.99\n" +
            "Gadget\t5\t24.99\n" +
            "Dongle\t20\t4.99\n";

        using var ms = ToStream(content);
        var rows = TsvReader.ReadRows(ms);

        Assert.Equal(4, rows.Count);  // header + 3 data rows

        // Build TsvDocument from string to verify parity
        var doc = TsvDocument.Load(content);
        Assert.Equal(3, doc.RowCount);  // data rows only
        Assert.NotNull(doc.Headers);
        Assert.Equal("product", doc.Headers![0]);

        // Stream row count (4) = doc.RowCount (3) + 1 header
        Assert.Equal(rows.Count, doc.RowCount + 1);
    }
}
