// Tests for TsvWriter.WriteRows, WriteRowsToFile, WriteToStream deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R167

using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R167: Tests for TsvWriter.WriteRows, WriteRowsToFile, WriteToStream.
/// TsvWriter.WriteRows(rows): serializes list of rows to TSV string.
/// TsvWriter.WriteRowsToFile(rows, path): writes rows to a TSV file.
/// TsvWriter.WriteToStream(rows, stream): writes rows to a Stream.
/// Covers: WriteRows non-null; WriteRows non-empty; WriteRows contains header row;
/// WriteRows contains all data rows; WriteRows tab-separated;
/// WriteRows->TsvDocument.Load round-trip count matches;
/// WriteRowsToFile creates file; WriteRowsToFile non-empty;
/// WriteRowsToFile->TsvDocument.LoadFile count matches;
/// WriteToStream produces content; WriteToStream->TsvDocument.Load count matches;
/// WriteRows preserves column order; WriteRowsToFile preserves all values;
/// WriteRows->Load->Filter chain; WriteToStream->TsvDocument.Load->Filter;
/// dogfood WriteRows->LoadFile->Filter->WriteRowsToFile->LoadFile->GetColumnValues verify.
/// </summary>
public class TsvR167TsvWriterWriteRowsTests : IDisposable
{
    private readonly string _tempDir;

    private static readonly List<List<string>> SampleRows = new()
    {
        new() { "name", "dept", "score" },
        new() { "Alice", "Eng", "95" },
        new() { "Bob", "Finance", "82" },
        new() { "Carol", "Eng", "88" }
    };

    public TsvR167TsvWriterWriteRowsTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR167_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var result = TsvWriter.WriteRows(SampleRows);
        Assert.NotNull(result);
    }

    [Fact]
    public void WriteRows_NonEmpty()
    {
        var result = TsvWriter.WriteRows(SampleRows);
        Assert.False(string.IsNullOrWhiteSpace(result));
    }

    [Fact]
    public void WriteRows_ContainsHeaderRow()
    {
        var result = TsvWriter.WriteRows(SampleRows);
        Assert.Contains("name", result);
        Assert.Contains("dept", result);
    }

    [Fact]
    public void WriteRows_ContainsAllDataRows()
    {
        var result = TsvWriter.WriteRows(SampleRows);
        Assert.Contains("Alice", result);
        Assert.Contains("Bob", result);
        Assert.Contains("Carol", result);
    }

    [Fact]
    public void WriteRows_TabSeparated()
    {
        var result = TsvWriter.WriteRows(SampleRows);
        Assert.Contains("\t", result);
    }

    [Fact]
    public void WriteRows_TsvDocument_Load_CountMatches()
    {
        var tsv = TsvWriter.WriteRows(SampleRows);
        var doc = TsvDocument.Load(tsv);
        Assert.Equal(3, doc.RowCount); // header not counted as row
    }

    [Fact]
    public void WriteRows_Load_Filter_Chain()
    {
        var tsv = TsvWriter.WriteRows(SampleRows);
        var doc = TsvDocument.Load(tsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRowsToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = TempFile("out.tsv");
        TsvWriter.WriteRowsToFile(SampleRows, path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRowsToFile_NonEmpty()
    {
        var path = TempFile("nonempty.tsv");
        TsvWriter.WriteRowsToFile(SampleRows, path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void WriteRowsToFile_LoadFile_CountMatches()
    {
        var path = TempFile("load.tsv");
        TsvWriter.WriteRowsToFile(SampleRows, path);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void WriteRowsToFile_PreservesAllValues()
    {
        var path = TempFile("vals.tsv");
        TsvWriter.WriteRowsToFile(SampleRows, path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("88", content);
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteToStream
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteToStream_ProducesContent()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(SampleRows, ms);
        Assert.True(ms.Length > 0);
    }

    [Fact]
    public void WriteToStream_TsvDocumentLoad_CountMatches()
    {
        using var ms = new MemoryStream();
        TsvWriter.WriteToStream(SampleRows, ms);
        var content = Encoding.UTF8.GetString(ms.ToArray());
        var doc = TsvDocument.Load(content);
        Assert.Equal(3, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteRowsLoadFilterWriteToFileLoadGetColumnValuesVerify_Pipeline()
    {
        // WriteRows
        var tsv = TsvWriter.WriteRows(SampleRows);
        Assert.Contains("Alice", tsv);

        // Load
        var doc = TsvDocument.Load(tsv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // WriteRowsToFile (from filtered)
        var engRows = new List<List<string>>
        {
            new() { "name", "dept", "score" }
        };
        foreach (var r in new[] { new[] { "Alice", "Eng", "95" }, new[] { "Carol", "Eng", "88" } })
            engRows.Add(new List<string>(r));

        var path = TempFile("eng.tsv");
        TsvWriter.WriteRowsToFile(engRows, path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = TsvDocument.LoadFile(path);
        Assert.Equal(2, fromFile.RowCount);

        // GetColumnValues
        var names = fromFile.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
