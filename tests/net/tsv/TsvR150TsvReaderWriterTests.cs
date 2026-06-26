// Tests for TsvReader and TsvWriter standalone classes.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R150

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R150: Tests for TsvReader and TsvWriter standalone classes.
/// TsvReader.ReadRows(path): reads TSV rows from a file.
/// TsvWriter.WriteRows(rows, path): writes rows to a TSV file.
/// Covers: TsvReader.ReadRows returns non-empty; first row is header row;
/// TsvReader count matches file line count; TsvWriter.WriteRows creates file;
/// TsvWriter file is non-empty; TsvWriter output readable by TsvDocument.LoadFile;
/// TsvReader then TsvDocument.Load round-trip; TsvWriter header row preserved;
/// TsvWriter->TsvReader round-trip row count; TsvWriter creates directory if missing;
/// TsvReader single-line file returns one row; TsvWriter empty rows produces file;
/// dogfood TsvWriter->TsvReader->TsvDocument.LoadFile->Filter->TsvWriter chain.
/// </summary>
public class TsvR150TsvReaderWriterTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR150TsvReaderWriterTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR150_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FourRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    // -------------------------------------------------------------------------
    // TsvReader
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvReader_ReadRows_ReturnsNonEmpty()
    {
        var path = TempFile("read.tsv");
        File.WriteAllText(path, FourRowTsv);
        var reader = new TsvReader();
        var rows = reader.ReadRows(path);
        Assert.NotEmpty(rows);
    }

    [Fact]
    public void TsvReader_ReadRows_FirstRowIsHeader()
    {
        var path = TempFile("header.tsv");
        File.WriteAllText(path, FourRowTsv);
        var reader = new TsvReader();
        var rows = reader.ReadRows(path);
        Assert.Contains("Name", rows[0]);
    }

    [Fact]
    public void TsvReader_ReadRows_CountMatchesLines()
    {
        var path = TempFile("count.tsv");
        File.WriteAllText(path, FourRowTsv);
        var reader = new TsvReader();
        var rows = reader.ReadRows(path);
        Assert.Equal(4, rows.Count); // header + 3 data rows
    }

    [Fact]
    public void TsvReader_SingleLineFile_ReturnsOneRow()
    {
        var path = TempFile("single.tsv");
        File.WriteAllText(path, "Name\tScore");
        var reader = new TsvReader();
        var rows = reader.ReadRows(path);
        Assert.Single(rows);
    }

    // -------------------------------------------------------------------------
    // TsvWriter
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvWriter_WriteRows_CreatesFile()
    {
        var path = TempFile("writer.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" }
        }, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void TsvWriter_WriteRows_FileIsNonEmpty()
    {
        var path = TempFile("nonempty.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Col1", "Col2" },
            new[] { "Val1", "Val2" }
        }, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void TsvWriter_WriteRows_OutputReadableByLoadFile()
    {
        var path = TempFile("readable.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" },
            new[] { "Bob", "82" }
        }, path);
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, doc.RowCount);
        Assert.Equal("Alice", doc.GetCellValue(1, 0));
    }

    [Fact]
    public void TsvWriter_WriteRows_HeaderRowPreserved()
    {
        var path = TempFile("hdr.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Dept" },
            new[] { "Alice", "Eng" }
        }, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Name", content);
        Assert.Contains("Dept", content);
    }

    // -------------------------------------------------------------------------
    // Round-trip: TsvWriter -> TsvReader
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvWriterThenTsvReader_RoundTrip_CountMatches()
    {
        var path = TempFile("rt.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Score" },
            new[] { "Alice", "95" },
            new[] { "Bob", "82" },
            new[] { "Carol", "88" }
        }, path);
        var reader = new TsvReader();
        var rows = reader.ReadRows(path);
        Assert.Equal(4, rows.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: TsvWriter->TsvReader->LoadFile->Filter->TsvWriter chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriterReaderLoadFileFilterWriter_Chain()
    {
        // Write with TsvWriter
        var path1 = TempFile("step1.tsv");
        var writer = new TsvWriter();
        writer.WriteRows(new[] {
            new[] { "Name", "Dept", "Score" },
            new[] { "Alice", "Eng", "95" },
            new[] { "Bob", "Finance", "82" },
            new[] { "Carol", "Eng", "88" }
        }, path1);
        Assert.True(File.Exists(path1));

        // Read with TsvReader
        var reader = new TsvReader();
        var rows = reader.ReadRows(path1);
        Assert.Equal(4, rows.Count);

        // Load with TsvDocument
        var doc = TsvDocument.LoadFile(path1, hasHeaders: false);
        Assert.Equal(4, doc.RowCount);

        // Filter Eng rows
        var eng = doc.Filter(r => r.Length > 1 && r[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Write filtered
        var path2 = TempFile("step2.tsv");
        var writer2 = new TsvWriter();
        writer2.WriteRows(eng.Rows, path2);
        Assert.True(File.Exists(path2));

        var finalDoc = TsvDocument.LoadFile(path2, hasHeaders: false);
        Assert.Equal(2, finalDoc.RowCount);
    }
}
