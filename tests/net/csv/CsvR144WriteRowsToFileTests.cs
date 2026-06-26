// Tests for CsvDocument.WriteRowsToFile (static), CsvDocument.SaveToFile, CsvDocument.LoadFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R144

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R144: Tests for CsvDocument.SaveToFile, CsvDocument.LoadFile round-trips.
/// SaveToFile(path): writes document to file.
/// LoadFile(path, hasHeaders): loads document from file.
/// CsvReader: reads CSV content.
/// CsvWriter: serializes CSV content.
/// Covers: SaveToFile creates file; SaveToFile file non-empty; SaveToFile contains commas;
/// LoadFile round-trip preserves row count; LoadFile round-trip preserves cell values;
/// LoadFile with headers; LoadFile without headers; LoadFile empty file returns empty;
/// CsvWriter.Serialize produces comma output; CsvReader.Deserialize produces document;
/// dogfood Load->SaveToFile->LoadFile->GetColumn pipeline.
/// </summary>
public class CsvR144WriteRowsToFileTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR144WriteRowsToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR144_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRowCsv =
        "Name,Score\n" +
        "Alice,95\n" +
        "Bob,82\n" +
        "Carol,88";

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("saved.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("nonempty.csv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_FileContainsCommas()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("commas.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains(",", content);
    }

    [Fact]
    public void SaveToFile_FileContainsCellValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("values.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_WithHeaders_RowCountCorrect()
    {
        var path = TempFile("headers.csv");
        File.WriteAllText(path, "Name,Score\nAlice,95\nBob,82");
        var doc = CsvDocument.LoadFile(path, hasHeaders: true);
        Assert.Equal(2, doc.RowCount);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_WithoutHeaders_AllRowsInRows()
    {
        var path = TempFile("noheaders.csv");
        File.WriteAllText(path, "Alice,95\nBob,82");
        var doc = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(2, doc.RowCount);
        Assert.False(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_RoundTrip_PreservesRowCount()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("roundtrip.csv");
        doc.SaveToFile(path);
        var reloaded = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void LoadFile_RoundTrip_PreservesCellValues()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var path = TempFile("values2.csv");
        doc.SaveToFile(path);
        var reloaded = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
    }

    [Fact]
    public void LoadFile_EmptyFile_ReturnsEmptyDoc()
    {
        var path = TempFile("empty.csv");
        File.WriteAllText(path, "");
        var doc = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // CsvWriter / CsvReader
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvWriter_Serialize_ProducesCommaDelimited()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        var writer = new CsvWriter();
        var result = writer.Serialize(doc);
        Assert.Contains(",", result);
    }

    [Fact]
    public void CsvReader_Deserialize_ProducesDocument()
    {
        var reader = new CsvReader();
        var doc = reader.Deserialize(ThreeRowCsv);
        Assert.True(doc.RowCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->SaveToFile->LoadFile->GetColumn
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadSaveLoadGetColumn_Pipeline()
    {
        var doc = CsvDocument.Load(ThreeRowCsv);
        Assert.Equal(3, doc.RowCount);

        // Save to file
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload
        var reloaded = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, reloaded.RowCount);

        // Get column
        var names = reloaded.GetColumn(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Carol", names);
        Assert.Equal(3, names.Count);
    }
}
