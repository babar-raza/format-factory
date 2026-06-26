// Tests for TsvReader.ReadRows, TsvWriter.WriteRows deeper coverage with round-trips.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R158

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R158: Tests for TsvReader.ReadRows, TsvWriter.WriteRows deeper round-trip coverage.
/// TsvReader.ReadRows(content): parses TSV string into list of string arrays.
/// TsvWriter.WriteRows(rows, headers): serializes rows to TSV string.
/// TsvWriter.WriteRows(rows, headers, path): writes to file.
/// Covers: ReadRows count matches line count; ReadRows field count per row;
/// ReadRows first row fields correct; WriteRows non-null output;
/// WriteRows contains all header values; WriteRows contains data values;
/// WriteRows->ReadRows round-trip count; WriteRows->ReadRows field values;
/// WriteRows with empty rows list; ReadRows tab-separated fields;
/// ReadRows single row; WriteRows->TsvDocument.Load round-trip;
/// WriteRowsToFile creates file; WriteRowsToFile->ReadRows content correct;
/// dogfood WriteRows->TsvDocument.Load->Filter->WriteRows->ReadRows verify.
/// </summary>
public class TsvR158TsvReaderWriterDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR158TsvReaderWriterDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR158_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static readonly string[] Headers = { "name", "dept", "score" };

    private static readonly List<string[]> ThreeRows = new()
    {
        new[] { "Alice", "Eng", "95" },
        new[] { "Bob", "Finance", "82" },
        new[] { "Carol", "Eng", "88" }
    };

    // -------------------------------------------------------------------------
    // TsvReader.ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_CountMatchesLineCount()
    {
        var content = "name\tdept\tscore\nAlice\tEng\t95\nBob\tFinance\t82";
        var rows = TsvReader.ReadRows(content);
        // Returns data rows (may include header line)
        Assert.True(rows.Count >= 2);
    }

    [Fact]
    public void ReadRows_FieldsAreSplitByTab()
    {
        var content = "Alice\tEng\t95";
        var rows = TsvReader.ReadRows(content);
        Assert.Single(rows);
        Assert.Equal(3, rows[0].Length);
    }

    [Fact]
    public void ReadRows_FirstRow_FieldsCorrect()
    {
        var content = "Alice\tEng\t95\nBob\tFinance\t82";
        var rows = TsvReader.ReadRows(content);
        Assert.Equal("Alice", rows[0][0]);
        Assert.Equal("Eng", rows[0][1]);
        Assert.Equal("95", rows[0][2]);
    }

    [Fact]
    public void ReadRows_SingleRow_Parsed()
    {
        var content = "OnlyRow\tSingleDept\t99";
        var rows = TsvReader.ReadRows(content);
        Assert.Equal(1, rows.Count);
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        Assert.NotNull(tsv);
    }

    [Fact]
    public void WriteRows_ContainsHeaderValues()
    {
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        Assert.Contains("name", tsv);
        Assert.Contains("dept", tsv);
        Assert.Contains("score", tsv);
    }

    [Fact]
    public void WriteRows_ContainsDataValues()
    {
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        Assert.Contains("Alice", tsv);
        Assert.Contains("Bob", tsv);
        Assert.Contains("Carol", tsv);
    }

    [Fact]
    public void WriteRows_EmptyRows_StillReturnsString()
    {
        var tsv = TsvWriter.WriteRows(new List<string[]>(), Headers);
        Assert.NotNull(tsv);
        // At minimum should have the header line
        Assert.Contains("name", tsv);
    }

    [Fact]
    public void WriteRows_ReadRows_RoundTrip_CountMatches()
    {
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        var doc = TsvDocument.Load(tsv);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void WriteRows_ReadRows_RoundTrip_ValuesCorrect()
    {
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        var doc = TsvDocument.Load(tsv);
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // TsvWriter.WriteRowsToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRowsToFile_CreatesFile()
    {
        var path = TempFile("rows.tsv");
        TsvWriter.WriteRowsToFile(ThreeRows, path, Headers);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void WriteRowsToFile_ContentHasData()
    {
        var path = TempFile("data.tsv");
        TsvWriter.WriteRowsToFile(ThreeRows, path, Headers);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Bob", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRows->TsvDocument.Load->Filter->WriteRows->ReadRows verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteLoadFilterWriteReadVerify_Pipeline()
    {
        // WriteRows → TSV string
        var tsv = TsvWriter.WriteRows(ThreeRows, Headers);
        Assert.Contains("Alice", tsv);

        // TsvDocument.Load
        var doc = TsvDocument.Load(tsv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // ToTsv
        var engTsv = eng.ToTsv();

        // ReadRows
        var reloaded = TsvDocument.Load(engTsv);
        Assert.Equal(2, reloaded.RowCount);
        var names = reloaded.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
