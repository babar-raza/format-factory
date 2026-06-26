// Tests for TsvDocument.LoadFile(string path, bool hasHeaders) — dedicated path-based load API.
// Sprint: FORMAT-FACTORY-TSV-R126-20260627
// Ledger: R126-GOVERNED-DOTNET-TSV-DOCUMENT-LOAD-FILE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R126: Dedicated tests for TsvDocument.LoadFile(string path, bool hasHeaders = true).
/// LoadFile builds a TsvDocument from a TSV file. The first row becomes Headers when
/// hasHeaders=true. Returns a document with correct RowCount, ColumnCount, and row data.
/// Throws on null/empty path, non-existent file.
/// Covers: non-null result; HasHeaders=true; Headers populated; RowCount correct;
/// ColumnCount correct; row values accessible; hasHeaders=false → all rows in Rows;
/// empty file → empty document; null path throws; non-existent path throws;
/// dogfood LoadFile parity with Load(string).
/// </summary>
public class TsvR126DocumentLoadFileTests
{
    private static string WriteTempTsv(string content)
    {
        var path = Path.GetTempFileName();
        File.WriteAllText(path, content);
        return path;
    }

    private const string SampleContent =
        "Name\tScore\tCity\nAlice\t95\tNYC\nBob\t80\tLondon\nCarol\t88\tParis";

    // -------------------------------------------------------------------------
    // Basic loading with headers
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_ValidFile_ReturnsNonNullDocument()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.NotNull(doc);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_HasHeadersIsTrue()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.True(doc.HasHeaders);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_HeadersArePopulated()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.NotNull(doc.Headers);
            Assert.Equal("Name",  doc.Headers![0]);
            Assert.Equal("Score", doc.Headers[1]);
            Assert.Equal("City",  doc.Headers[2]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_RowCountIsThree()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.Equal(3, doc.RowCount);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_ColumnCountIsThree()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.Equal(3, doc.ColumnCount);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_RowValuesAccessible()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.Equal("Alice", doc.Rows[0][0]);
            Assert.Equal("95",    doc.Rows[0][1]);
            Assert.Equal("Paris", doc.Rows[2][2]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_HasHeadersFalse_AllRowsInRows()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var doc = TsvDocument.LoadFile(path, hasHeaders: false);
            Assert.False(doc.HasHeaders);
            Assert.Equal(4, doc.RowCount); // includes the header line as a data row
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_EmptyFile_ReturnsEmptyDocument()
    {
        var path = WriteTempTsv(string.Empty);
        try
        {
            var doc = TsvDocument.LoadFile(path);
            Assert.Equal(0, doc.RowCount);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Error handling
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NullPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() => TsvDocument.LoadFile(null!));
    }

    [Fact]
    public void LoadFile_NonExistentPath_ThrowsTsvException()
    {
        Assert.Throws<TsvException>(() =>
            TsvDocument.LoadFile("/nonexistent/r126-tsv-test.tsv"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadFile parity with Load(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LoadFile_ParityWithLoadString()
    {
        var path = WriteTempTsv(SampleContent);
        try
        {
            var fromFile   = TsvDocument.LoadFile(path);
            var fromString = TsvDocument.Load(SampleContent);

            Assert.Equal(fromString.RowCount,    fromFile.RowCount);
            Assert.Equal(fromString.ColumnCount, fromFile.ColumnCount);
            Assert.Equal(fromString.Rows[0][0],  fromFile.Rows[0][0]);
            Assert.Equal(fromString.Headers![0], fromFile.Headers![0]);
        }
        finally { File.Delete(path); }
    }
}
