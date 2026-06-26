// Tests for CsvDocument.LoadFile(string path, bool hasHeaders) — dedicated path-based load API.
// Sprint: FORMAT-FACTORY-CSV-R128-20260627
// Ledger: R128-GOVERNED-DOTNET-CSV-DOCUMENT-LOAD-FILE-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R128: Dedicated tests for CsvDocument.LoadFile(string path, bool hasHeaders = true).
/// LoadFile reads the CSV file, splits rows and fields, and builds a CsvDocument.
/// The first row becomes Headers when hasHeaders=true.
/// Throws CsvException for null/empty path and non-existent files.
/// Covers: non-null result; HasHeaders=true; Headers populated; RowCount correct;
/// ColumnCount correct; row cell values accessible; hasHeaders=false (all rows in Rows);
/// empty file → RowCount=0; null path throws; non-existent path throws;
/// dogfood LoadFile parity with Load(string).
/// RFC 4180 basis: §2 — first record may be a header record.
/// </summary>
public class CsvR128DocumentLoadFileTests
{
    private static string WriteTempCsv(string content)
    {
        var path = Path.GetTempFileName();
        File.WriteAllText(path, content);
        return path;
    }

    private const string SampleContent =
        "Name,Score,City\r\nAlice,95,NYC\r\nBob,80,London\r\nCarol,88,Paris";

    // -------------------------------------------------------------------------
    // Basic loading with headers
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_ValidFile_ReturnsNonNullDocument()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.NotNull(doc);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_HasHeadersIsTrue()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.True(doc.HasHeaders);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_HeadersArePopulated()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
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
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.Equal(3, doc.RowCount);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_ColumnCountIsThree()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.Equal(3, doc.ColumnCount);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_ValidFile_CellValuesAccessible()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.Equal("Alice", doc.Rows[0][0]);
            Assert.Equal("95",    doc.Rows[0][1]);
            Assert.Equal("Paris", doc.Rows[2][2]);
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_HasHeadersFalse_AllRowsInRows()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var doc = CsvDocument.LoadFile(path, hasHeaders: false);
            Assert.False(doc.HasHeaders);
            Assert.Equal(4, doc.RowCount); // includes the header line as a data row
        }
        finally { File.Delete(path); }
    }

    [Fact]
    public void LoadFile_EmptyFile_RowCountIsZero()
    {
        var path = WriteTempCsv(string.Empty);
        try
        {
            var doc = CsvDocument.LoadFile(path);
            Assert.Equal(0, doc.RowCount);
        }
        finally { File.Delete(path); }
    }

    // -------------------------------------------------------------------------
    // Error handling
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_NullPath_ThrowsCsvException()
    {
        Assert.Throws<CsvException>(() => CsvDocument.LoadFile(null!));
    }

    [Fact]
    public void LoadFile_NonExistentPath_ThrowsCsvException()
    {
        Assert.Throws<CsvException>(() =>
            CsvDocument.LoadFile("/nonexistent/r128-csv-test.csv"));
    }

    // -------------------------------------------------------------------------
    // Dogfood: LoadFile parity with Load(string)
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_LoadFile_ParityWithLoadString()
    {
        var path = WriteTempCsv(SampleContent);
        try
        {
            var fromFile   = CsvDocument.LoadFile(path);
            var fromString = CsvDocument.Load(SampleContent);

            Assert.Equal(fromString.RowCount,    fromFile.RowCount);
            Assert.Equal(fromString.ColumnCount, fromFile.ColumnCount);
            Assert.Equal(fromString.Rows[0][0],  fromFile.Rows[0][0]);
            Assert.Equal(fromString.Headers![0], fromFile.Headers![0]);
        }
        finally { File.Delete(path); }
    }
}
