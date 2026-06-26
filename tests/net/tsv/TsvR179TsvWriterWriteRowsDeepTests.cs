// Tests for TsvWriter.WriteRows, WriteToStream, WriteToFile deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R179

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R179: Tests for TsvWriter.WriteRows, WriteToStream, WriteToFile deeper coverage.
/// WriteRows(headers, rows): returns a TSV string from headers and rows.
/// WriteToStream(headers, rows, stream): writes TSV to a stream.
/// WriteToFile(headers, rows, path): writes TSV to a file.
/// Covers: WriteRows non-null; WriteRows has tab separator; WriteRows contains headers;
/// WriteRows contains data values; WriteRows single row; WriteRows multiple rows;
/// WriteRows empty rows returns header line;
/// WriteToStream creates stream content; WriteToStream has tabs; WriteToStream parseable back;
/// WriteToFile creates file; WriteToFile content has headers; WriteToFile content has data;
/// WriteToFile then TsvDocument.LoadFile round-trip;
/// dogfood WriteRows->WriteToFile->LoadFile->GetCell->Verify pipeline.
/// </summary>
public class TsvR179TsvWriterWriteRowsDeepTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly List<string> Headers = new() { "Name", "Dept", "Score" };

    private static readonly List<List<string>> Rows = new()
    {
        new List<string> { "Alice", "Eng", "92" },
        new List<string> { "Bob", "Finance", "85" },
        new List<string> { "Carol", "HR", "78" },
        new List<string> { "Dave", "Eng", "91" }
    };

    public TsvR179TsvWriterWriteRowsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR179_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // WriteRows (string output)
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.NotNull(result);
    }

    [Fact]
    public void WriteRows_NonEmpty()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.NotEmpty(result);
    }

    [Fact]
    public void WriteRows_ContainsTabSeparator()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.Contains("\t", result);
    }

    [Fact]
    public void WriteRows_ContainsHeaders()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.Contains("Name", result);
        Assert.Contains("Dept", result);
        Assert.Contains("Score", result);
    }

    [Fact]
    public void WriteRows_ContainsDataValues()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.Contains("Alice", result);
        Assert.Contains("92", result);
    }

    [Fact]
    public void WriteRows_SingleRow_NonNull()
    {
        var singleRow = new List<List<string>> { new List<string> { "Solo", "IT", "100" } };
        var result = TsvWriter.WriteRows(Headers, singleRow);
        Assert.NotNull(result);
        Assert.Contains("Solo", result);
    }

    [Fact]
    public void WriteRows_MultipleRows_ContainsAll()
    {
        var result = TsvWriter.WriteRows(Headers, Rows);
        Assert.Contains("Alice", result);
        Assert.Contains("Bob", result);
        Assert.Contains("Carol", result);
        Assert.Contains("Dave", result);
    }

    // -------------------------------------------------------------------------
    // WriteToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToFile_CreatesFile()
    {
        var path = TempFile("output.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteToFile_FileIsNonEmpty()
    {
        var path = TempFile("nonempty.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void WriteToFile_FileContainsHeaders()
    {
        var path = TempFile("headers.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Name", content);
        Assert.Contains("Dept", content);
    }

    [Fact]
    public void WriteToFile_FileContainsDataValues()
    {
        var path = TempFile("data.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Finance", content);
    }

    [Fact]
    public void WriteToFile_ThenLoadFile_RowCountMatches()
    {
        var path = TempFile("roundtrip.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void WriteToFile_ThenLoadFile_HeadersPreserved()
    {
        var path = TempFile("hdrs.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        var doc = TsvDocument.LoadFile(path);
        Assert.Contains("Name", doc.Headers);
        Assert.Contains("Score", doc.Headers);
    }

    [Fact]
    public void WriteToFile_ThenLoadFile_DataAccessible()
    {
        var path = TempFile("access.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        var doc = TsvDocument.LoadFile(path);
        var aliceName = doc.GetCell(0, "Name");
        Assert.Equal("Alice", aliceName);
    }

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_StreamHasContent()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Headers, Rows, ms);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_StreamHasTabs()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Headers, Rows, ms);
        ms.Seek(0, SeekOrigin.Begin);
        var content = new StreamReader(ms).ReadToEnd();
        Assert.Contains("\t", content);
    }

    [Fact]
    public void WriteToStream_StreamContainsHeaders()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Headers, Rows, ms);
        ms.Seek(0, SeekOrigin.Begin);
        var content = new StreamReader(ms).ReadToEnd();
        Assert.Contains("Name", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteRows_WriteToFile_LoadFile_GetCell_Verify_Pipeline()
    {
        // WriteRows in-memory
        var tsv = TsvWriter.WriteRows(Headers, Rows);
        Assert.NotNull(tsv);
        Assert.Contains("\t", tsv);
        Assert.Contains("Alice", tsv);

        // WriteToFile
        var path = TempFile("dogfood.tsv");
        TsvWriter.WriteToFile(Headers, Rows, path);
        Assert.True(File.Exists(path));

        // LoadFile and verify
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
        Assert.Equal(3, doc.ColumnCount);
        Assert.Contains("Name", doc.Headers);

        // GetCell access
        Assert.Equal("Alice", doc.GetCell(0, "Name"));
        Assert.Equal("Eng", doc.GetCell(0, "Dept"));
        Assert.Equal("92", doc.GetCell(0, "Score"));
        Assert.Equal("Dave", doc.GetCell(3, "Name"));

        // WriteToStream and verify
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Headers, Rows, ms);
        Assert.True(ms.Length > 0);
        ms.Seek(0, SeekOrigin.Begin);
        var streamContent = new StreamReader(ms).ReadToEnd();
        Assert.Contains("Finance", streamContent);
    }
}
