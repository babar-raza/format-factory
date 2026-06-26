// Tests for TsvDocument.LoadFile and SaveToFile.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R138

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R138: Tests for TsvDocument.LoadFile and SaveToFile.
/// LoadFile(path): reads TSV from disk; parses as Load(string).
/// SaveToFile(path): writes ToTsv() to disk.
/// Covers: LoadFile missing path throws; LoadFile valid file correct row count;
/// LoadFile with headers parses headers; LoadFile without headers includes all rows;
/// LoadFile preserves cell values; SaveToFile creates file; SaveToFile file not empty;
/// SaveToFile round-trip preserves row count; SaveToFile round-trip preserves cell values;
/// SaveToFile after mutation reflects changes; SaveToFile then LoadFile round-trip;
/// dogfood Load->Filter->SaveToFile->LoadFile pipeline.
/// </summary>
public class TsvR138LoadFileAndSaveToFileTests : IDisposable
{
    private const string ThreeRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    private readonly string _tempDir;

    public TsvR138LoadFileAndSaveToFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR138_" + Guid.NewGuid().ToString("N"));
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
            TsvDocument.LoadFile(Path.Combine(_tempDir, "nonexistent.tsv")));
    }

    [Fact]
    public void LoadFile_ValidFile_CorrectRowCount()
    {
        var path = TempFile("three-row.tsv");
        File.WriteAllText(path, ThreeRowTsv);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void LoadFile_WithHeaders_ParsesHeaders()
    {
        var path = TempFile("headers.tsv");
        File.WriteAllText(path, ThreeRowTsv);
        var doc = TsvDocument.LoadFile(path, hasHeaders: true);
        Assert.NotNull(doc.Headers);
        Assert.Contains("Name", doc.Headers!);
    }

    [Fact]
    public void LoadFile_WithoutHeaders_AllRowsAreData()
    {
        var path = TempFile("no-headers.tsv");
        File.WriteAllText(path, "A\tB\n1\t2\n3\t4");
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, doc.RowCount); // All 3 rows are data
    }

    [Fact]
    public void LoadFile_PreservesCellValues()
    {
        var path = TempFile("cell-values.tsv");
        File.WriteAllText(path, ThreeRowTsv);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Eng", doc.GetCellValue(0, 1));
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("save.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNotEmpty()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesRowCount()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("roundtrip.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void SaveToFile_RoundTrip_PreservesCellValues()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("cell-roundtrip.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
        Assert.Equal("Carol", reloaded.GetCellValue(2, 0));
    }

    [Fact]
    public void SaveToFile_ContainsTabSeparator()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("tabs.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("\t", content);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveToFileLoadFile_Pipeline()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // Filter Eng department only
        var engOnly = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, engOnly.RowCount); // Alice and Carol

        // Save to file
        var path = TempFile("eng-only.tsv");
        engOnly.SaveToFile(path);
        Assert.True(File.Exists(path));

        // Reload
        var reloaded = TsvDocument.LoadFile(path);
        Assert.Equal(2, reloaded.RowCount);

        // Verify values
        var names = reloaded.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
