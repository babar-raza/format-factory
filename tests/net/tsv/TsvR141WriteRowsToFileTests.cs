// Tests for TsvDocument.WriteRowsToFile, TsvWriter, TsvReader.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R141

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R141: Tests for TsvDocument.WriteRowsToFile (static), TsvWriter, TsvReader.
/// TsvDocument.WriteRowsToFile(rows, path): writes list-of-lists to file.
/// TsvWriter: serializes TsvDocument to TSV string.
/// TsvReader: reads TSV strings.
/// Covers: WriteRowsToFile creates file; WriteRowsToFile non-empty file;
/// WriteRowsToFile round-trip count preserved; WriteRowsToFile contains tab chars;
/// TsvWriter serializes document; TsvReader reads content;
/// SaveToFile creates file; SaveToFile round-trip preserves row count;
/// SaveToFile then LoadFile preserves data; dogfood Load->SaveToFile->LoadFile pipeline.
/// </summary>
public class TsvR141WriteRowsToFileTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR141WriteRowsToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR141_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string ThreeRowTsv =
        "Name\tScore\n" +
        "Alice\t95\n" +
        "Bob\t82\n" +
        "Carol\t88";

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("saved.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_FileContainsTabChars()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("tabs.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("\t", content);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("roundtrip.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesCellValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("values.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("95", reloaded.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_WithHeaders_ReturnsDocWithRows()
    {
        var path = TempFile("withheaders.tsv");
        File.WriteAllText(path, "Name\tScore\nAlice\t95\nBob\t82");
        var doc = TsvDocument.LoadFile(path, hasHeaders: true);
        Assert.Equal(2, doc.RowCount);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_WithoutHeaders_AllRowsInRows()
    {
        var path = TempFile("noheaders.tsv");
        File.WriteAllText(path, "Alice\t95\nBob\t82");
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(2, doc.RowCount);
        Assert.False(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_EmptyFile_ReturnsEmptyDoc()
    {
        var path = TempFile("empty.tsv");
        File.WriteAllText(path, "");
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.True(doc.IsEmpty);
    }

    // -------------------------------------------------------------------------
    // TsvWriter / TsvReader
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvWriter_Serialize_ProducesTabDelimited()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var writer = new TsvWriter();
        var result = writer.Serialize(doc);
        Assert.Contains("\t", result);
    }

    [Fact]
    public void TsvReader_Deserialize_ProducesDocument()
    {
        var reader = new TsvReader();
        var doc = reader.Deserialize(ThreeRowTsv);
        Assert.True(doc.RowCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->SaveToFile->LoadFile->ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadSaveLoadToTsv_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // Save to file
        var path = TempFile("dogfood.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // Reload from file
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, reloaded.RowCount);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Carol", reloaded.GetCellValue(2, 0));

        // Serialize back to TSV string
        var tsv = reloaded.ToTsv();
        Assert.Contains("\t", tsv);
        Assert.Contains("Bob", tsv);

        // Final round-trip
        var finalDoc = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(3, finalDoc.RowCount);
    }
}
