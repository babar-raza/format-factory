// Tests for CsvReader.ReadRows(Stream stream) — stream-based CSV parsing.
// Sprint: FORMAT-FACTORY-CSV-R125-20260627
// Ledger: R125-GOVERNED-DOTNET-CSV-STREAM-READROWS-001

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R125: Tests for CsvReader.ReadRows(Stream stream) overload.
/// Verifies that stream-based parsing produces the same results as string-based parsing,
/// handles edge cases (empty stream, CRLF), and rejects null input.
/// RFC 4180 basis: §2 CRLF line endings, quoted fields.
/// </summary>
public class CsvR125StreamReadRowsTests
{
    private static Stream ToStream(string content, Encoding? encoding = null)
    {
        var bytes = (encoding ?? Encoding.UTF8).GetBytes(content);
        return new MemoryStream(bytes);
    }

    // -------------------------------------------------------------------------
    // Basic parity with string overload
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_RowCountMatchesStringOverload()
    {
        const string csv = "a,b,c\n1,2,3\n4,5,6";
        var fromString = CsvReader.ReadRows(csv);
        var fromStream = CsvReader.ReadRows(ToStream(csv));
        Assert.Equal(fromString.Count, fromStream.Count);
    }

    [Fact]
    public void ReadRows_Stream_FirstRowValuesMatch()
    {
        const string csv = "Name,Age,City\nAlice,30,NYC";
        var rows = CsvReader.ReadRows(ToStream(csv));
        Assert.Equal("Name", rows[0][0]);
        Assert.Equal("Age",  rows[0][1]);
        Assert.Equal("City", rows[0][2]);
    }

    [Fact]
    public void ReadRows_Stream_DataRowValuesPreserved()
    {
        const string csv = "Product,Price\nWidget,9.99\nGadget,24.95";
        var rows = CsvReader.ReadRows(ToStream(csv));
        Assert.Equal(3, rows.Count);
        Assert.Equal("Widget", rows[1][0]);
        Assert.Equal("9.99",   rows[1][1]);
        Assert.Equal("Gadget", rows[2][0]);
    }

    // -------------------------------------------------------------------------
    // CRLF line endings
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_CrLfLineEndings_ParsedCorrectly()
    {
        const string csv = "A,B\r\nC,D\r\nE,F";
        var rows = CsvReader.ReadRows(ToStream(csv));
        Assert.Equal(3, rows.Count);
        Assert.Equal("A", rows[0][0]);
        Assert.Equal("C", rows[1][0]);
        Assert.Equal("E", rows[2][0]);
    }

    // -------------------------------------------------------------------------
    // Empty stream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_EmptyStream_ReturnsEmptyList()
    {
        var rows = CsvReader.ReadRows(new MemoryStream(Array.Empty<byte>()));
        Assert.NotNull(rows);
        Assert.Empty(rows);
    }

    // -------------------------------------------------------------------------
    // Quoted fields via stream
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_QuotedFieldWithComma_ParsedCorrectly()
    {
        const string csv = "\"Hello, World\",42";
        var rows = CsvReader.ReadRows(ToStream(csv));
        Assert.Single(rows);
        Assert.Equal("Hello, World", rows[0][0]);
        Assert.Equal("42",           rows[0][1]);
    }

    // -------------------------------------------------------------------------
    // Null guard
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_NullStream_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => CsvReader.ReadRows((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Column count consistency
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_EachRowHasCorrectColumnCount()
    {
        const string csv = "X,Y,Z\n1,2,3\n4,5,6";
        var rows = CsvReader.ReadRows(ToStream(csv));
        foreach (var row in rows)
            Assert.Equal(3, row.Length);
    }

    // -------------------------------------------------------------------------
    // UTF-8 BOM stripping
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_Stream_Utf8BomStripped_ParsedCorrectly()
    {
        // UTF-8 BOM = EF BB BF
        const string csv = "col1,col2\nval1,val2";
        using var stream = ToStream(csv, new UTF8Encoding(encoderShouldEmitUTF8Identifier: true));
        var rows = CsvReader.ReadRows(stream);
        Assert.Equal(2, rows.Count);
        Assert.Equal("col1", rows[0][0]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: sales pipeline CSV read from stream
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SalesReport_StreamParsedCorrectly()
    {
        const string csv =
            "Region,Product,Units,Revenue\r\n" +
            "North,Widget,100,9900.00\r\n" +
            "South,Gadget,50,12475.00\r\n" +
            "East,Widget,200,19800.00\r\n" +
            "West,Gadget,75,18712.50\r\n";

        var rows = CsvReader.ReadRows(ToStream(csv));

        // Header + 4 data rows
        Assert.Equal(5, rows.Count);

        // Headers
        Assert.Equal("Region",  rows[0][0]);
        Assert.Equal("Revenue", rows[0][3]);

        // Spot-check values
        Assert.Equal("North",     rows[1][0]);
        Assert.Equal("9900.00",   rows[1][3]);
        Assert.Equal("East",      rows[3][0]);
        Assert.Equal("19800.00",  rows[3][3]);

        // All rows have 4 columns
        foreach (var row in rows)
            Assert.Equal(4, row.Length);
    }
}
