// Tests for CsvDocument.LoadFile and SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R140

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R140: Tests for CsvDocument.LoadFile and SaveToFile.
/// LoadFile(path): reads CSV from disk; parses as Load(string).
/// SaveToFile(path): writes ToCsv() to disk.
/// Covers: LoadFile missing path throws; LoadFile valid file correct count;
/// LoadFile with headers parses headers; LoadFile without headers no headers;
/// LoadFile preserves cell values; SaveToFile creates file; SaveToFile file not empty;
/// SaveToFile round-trip preserves row count; SaveToFile round-trip preserves cell values;
/// SaveToFile then LoadFile round-trip; SaveToFile after mutation reflects changes;
/// dogfood Load->AddRow->SaveToFile->LoadFile pipeline.
/// </summary>
public class CsvR140LoadFileAndSaveToFileTests : IDisposable
{
    private const string TwoRowCsv =
        "Name,Score,Active\n" +
        "Alice,95,true\n" +
        "Bob,82,false";

    private readonly string _tempDir;

    public CsvR140LoadFileAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR140_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_MissingPath_Throws()
    {
        Assert.ThrowsAny<Exception>(() =>
            CsvDocument.LoadFile(Path.Combine(_tempDir, "nonexistent.csv")));
    }

    [Fact]
    public void LoadFile_ValidFile_CorrectRowCount()
    {
        var path = TempFile("two-row.csv");
        File.WriteAllText(path, TwoRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(2, doc.RowCount);
    }

    [Fact]
    public void LoadFile_WithHeaders_ParsesHeaders()
    {
        var path = TempFile("headers.csv");
        File.WriteAllText(path, TwoRowCsv);
        var doc = CsvDocument.LoadFile(path, hasHeaders: true);
        Assert.NotNull(doc.Headers);
        Assert.Contains("Name", doc.Headers!);
    }

    [Fact]
    public void LoadFile_WithoutHeaders_NoHeadersParsed()
    {
        var path = TempFile("no-headers.csv");
        File.WriteAllText(path, "Alice,95\nBob,82");
        var doc = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Null(doc.Headers);
    }

    [Fact]
    public void LoadFile_PreservesCellValues()
    {
        var path = TempFile("cell-values.csv");
        File.WriteAllText(path, TwoRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("95", doc.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var path = TempFile("save.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNotEmpty()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var path = TempFile("nonempty.csv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesRowCount()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var path = TempFile("roundtrip.csv");
        doc.SaveToFile(path);
        var reloaded = CsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesCellValues()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        var path = TempFile("cell-roundtrip.csv");
        doc.SaveToFile(path);
        var reloaded = CsvDocument.LoadFile(path);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Bob", reloaded.GetCellValue(1, 0));
    }

    [Fact]
    public void SaveToFile_AfterMutation_ReflectsChanges()
    {
        var doc = CsvDocument.Load(TwoRowCsv);
        doc.SetCell(0, 1, "100"); // Update Alice's score
        var path = TempFile("mutated.csv");
        doc.SaveToFile(path);
        var reloaded = CsvDocument.LoadFile(path);
        Assert.Equal("100", reloaded.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->AddRow->SaveToFile->LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadAddRowSaveToFileLoadFile_Pipeline()
    {
        // Load existing CSV
        var doc = CsvDocument.Load(TwoRowCsv);
        Assert.Equal(2, doc.RowCount);

        // Add a new row
        doc.AddRow(new[] { "Carol", "88", "true" });
        Assert.Equal(3, doc.RowCount);

        // Save to file
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);

        // Reload
        var reloaded = CsvDocument.LoadFile(path);
        Assert.Equal(3, reloaded.RowCount);
        Assert.Equal("Carol", reloaded.GetCellValue(2, 0));

        // Filter and verify
        var highScorers = reloaded.Filter(row =>
            row.Length > 1 && int.TryParse(row[1], out var score) && score >= 88);
        Assert.Equal(2, highScorers.RowCount); // Alice(95) and Carol(88)
    }
}
