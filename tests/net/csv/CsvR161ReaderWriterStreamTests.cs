// Tests for CsvReader.ReadRows (stream), CsvWriter.WriteRows (stream) deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R161

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R161: Tests for CsvReader.ReadRows, CsvWriter.WriteRows, StreamReadRows deeper coverage.
/// CsvReader.ReadRows(content): parses CSV string to list of string arrays.
/// CsvWriter.WriteRows(rows, headers): serializes rows to CSV string.
/// CsvDocument.LoadFile(path): loads from file.
/// CsvDocument.SaveToFile(path): saves to file.
/// Covers: ReadRows count matches data rows; ReadRows fields split by comma;
/// ReadRows first row fields correct; WriteRows non-null; WriteRows contains headers;
/// WriteRows->Load round-trip; WriteRows->ReadRows field values;
/// WriteRows empty rows list; SaveToFile creates file; SaveToFile->LoadFile round-trip;
/// LoadFile count matches; LoadFile field values; ReadRows single row;
/// SaveToFile->LoadFile->Filter count;
/// dogfood WriteRows->Load->Filter->SaveToFile->LoadFile->GetColumn verify.
/// </summary>
public class CsvR161ReaderWriterStreamTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR161ReaderWriterStreamTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR161_" + Guid.NewGuid().ToString("N"));
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
    // CsvReader.ReadRows
    // -------------------------------------------------------------------------

    [Fact]
    public void ReadRows_FieldsSplitByComma()
    {
        var content = "Alice,Eng,95";
        var rows = CsvReader.ReadRows(content);
        Assert.Single(rows);
        Assert.Equal(3, rows[0].Length);
    }

    [Fact]
    public void ReadRows_FirstRowFieldsCorrect()
    {
        var content = "Alice,Eng,95\nBob,Finance,82";
        var rows = CsvReader.ReadRows(content);
        Assert.Equal("Alice", rows[0][0]);
        Assert.Equal("Eng", rows[0][1]);
        Assert.Equal("95", rows[0][2]);
    }

    [Fact]
    public void ReadRows_CountMatchesDataLines()
    {
        var content = "Alice,Eng,95\nBob,Finance,82\nCarol,Eng,88";
        var rows = CsvReader.ReadRows(content);
        Assert.Equal(3, rows.Count);
    }

    [Fact]
    public void ReadRows_SingleRow_Parsed()
    {
        var content = "Only,Row,Here";
        var rows = CsvReader.ReadRows(content);
        Assert.Equal(1, rows.Count);
    }

    // -------------------------------------------------------------------------
    // CsvWriter.WriteRows
    // -------------------------------------------------------------------------

    [Fact]
    public void WriteRows_NonNull()
    {
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        Assert.NotNull(csv);
    }

    [Fact]
    public void WriteRows_ContainsHeaders()
    {
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        Assert.Contains("name", csv);
        Assert.Contains("dept", csv);
    }

    [Fact]
    public void WriteRows_ContainsDataValues()
    {
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
    }

    [Fact]
    public void WriteRows_EmptyRows_ReturnsHeaders()
    {
        var csv = CsvWriter.WriteRows(new List<string[]>(), Headers);
        Assert.Contains("name", csv);
    }

    [Fact]
    public void WriteRows_Load_RoundTrip_CountMatches()
    {
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        var doc = CsvDocument.Load(csv);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void WriteRows_Load_RoundTrip_FieldValues()
    {
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        var doc = CsvDocument.Load(csv);
        var names = doc.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng");
        var path = TempFile("saved.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountMatches()
    {
        var doc = CsvDocument.Load("name,dept,score\nAlice,Eng,95\nBob,Finance,82");
        var path = TempFile("roundtrip.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_FieldValues_Correct()
    {
        var doc = CsvDocument.Load("name,dept\nAlice,Eng\nBob,Finance");
        var path = TempFile("values.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: WriteRows->Load->Filter->SaveToFile->LoadFile->GetColumn verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_WriteLoadFilterSaveLoadGetColumn_Pipeline()
    {
        // WriteRows
        var csv = CsvWriter.WriteRows(ThreeRows, Headers);
        var doc = CsvDocument.Load(csv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // SaveToFile
        var path = TempFile("eng.csv");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount);

        // GetColumn
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
