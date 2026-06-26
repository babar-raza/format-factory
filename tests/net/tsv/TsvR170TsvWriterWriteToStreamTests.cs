// Tests for TsvWriter.WriteToStream, WriteRows, WriteRowsToFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R170

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R170: Tests for TsvWriter.WriteToStream, WriteRows, WriteRowsToFile deeper.
/// TsvWriter.WriteToStream(rows, headers, stream): writes TSV content to a Stream.
/// TsvWriter.WriteRows(rows, headers): returns TSV string from rows and headers.
/// TsvWriter.WriteRowsToFile(rows, headers, path): writes TSV to file.
/// Covers: WriteToStream produces non-empty output; WriteToStream content has tabs;
/// WriteToStream content contains headers; WriteToStream content contains row values;
/// WriteToStream then read back row count correct; WriteRows non-null; WriteRows has tabs;
/// WriteRows contains headers; WriteRows contains row values;
/// WriteRowsToFile creates file; WriteRowsToFile file non-empty;
/// WriteRowsToFile->LoadFile round-trip count correct;
/// dogfood WriteToStream->MemoryStream->Load verify pipeline.
/// </summary>
public class TsvR170TsvWriterWriteToStreamTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly IReadOnlyList<string> Headers =
        new[] { "name", "dept", "score" };

    private static readonly IReadOnlyList<IReadOnlyList<string>> Rows =
        new[]
        {
            (IReadOnlyList<string>)new[] { "Alice", "Eng", "95" },
            new[] { "Bob", "Finance", "82" },
            new[] { "Carol", "Eng", "88" }
        };

    public TsvR170TsvWriterWriteToStreamTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR170_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_ProducesNonEmptyOutput()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_ContentHasTabs()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("\t", content);
    }

    [Fact]
    public void WriteToStream_ContentContainsHeaders()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("name", content);
        Assert.Contains("dept", content);
        Assert.Contains("score", content);
    }

    [Fact]
    public void WriteToStream_ContentContainsRowValues()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
        Assert.Contains("Eng", content);
    }

    [Fact]
    public void WriteToStream_ThenLoad_RowCountCorrect()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        ms.Position = 0;
        var doc = TsvDocument.Load(ms);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void WriteToStream_ThenLoad_PreservesHeaders()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        ms.Position = 0;
        var doc = TsvDocument.Load(ms);
        Assert.True(doc.HasHeaders);
        Assert.Contains("name", doc.Headers);
    }

    // -------------------------------------------------------------------------
    // WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var result = TsvWriter.WriteRows(Rows, Headers);
        Assert.NotNull(result);
    }

    [Fact]
    public void WriteRows_HasTabs()
    {
        var result = TsvWriter.WriteRows(Rows, Headers);
        Assert.Contains("\t", result);
    }

    [Fact]
    public void WriteRows_ContainsHeaders()
    {
        var result = TsvWriter.WriteRows(Rows, Headers);
        Assert.Contains("name", result);
        Assert.Contains("dept", result);
    }

    [Fact]
    public void WriteRows_ContainsRowValues()
    {
        var result = TsvWriter.WriteRows(Rows, Headers);
        Assert.Contains("Alice", result);
        Assert.Contains("Finance", result);
    }

    [Fact]
    public void WriteRows_ThenLoad_RowCountCorrect()
    {
        var tsv = TsvWriter.WriteRows(Rows, Headers);
        var doc = TsvDocument.Load(tsv);
        Assert.Equal(3, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // WriteRowsToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = TempFile("rows.tsv");
        TsvWriter.WriteRowsToFile(Rows, Headers, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRowsToFile_FileNonEmpty()
    {
        var path = TempFile("nonempty.tsv");
        TsvWriter.WriteRowsToFile(Rows, Headers, path);
        Assert.False(string.IsNullOrWhiteSpace(File.ReadAllText(path)));
    }

    [Fact]
    public void WriteRowsToFile_LoadFile_RoundTripCountCorrect()
    {
        var path = TempFile("roundtrip.tsv");
        TsvWriter.WriteRowsToFile(Rows, Headers, path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteToStreamMemoryStreamLoadVerify_Pipeline()
    {
        // WriteToStream
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(Rows, Headers, ms);
        Assert.True(ms.Length > 0);

        // Load from stream
        ms.Position = 0;
        var doc = TsvDocument.Load(ms);
        Assert.Equal(3, doc.RowCount);
        Assert.True(doc.HasHeaders);

        // Verify values
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);

        // WriteRows (string) round-trip
        var tsvString = TsvWriter.WriteRows(Rows, Headers);
        var fromString = TsvDocument.Load(tsvString);
        Assert.Equal(3, fromString.RowCount);
        Assert.Equal(doc.RowCount, fromString.RowCount);

        // WriteRowsToFile round-trip
        var path = TempFile("dogfood.tsv");
        TsvWriter.WriteRowsToFile(Rows, Headers, path);
        var fromFile = TsvDocument.LoadFile(path);
        Assert.Equal(3, fromFile.RowCount);
        Assert.True(fromFile.HasHeaders);
        Assert.Contains("dept", fromFile.Headers);
    }
}
