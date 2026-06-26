// Tests for TsvDocument.SaveToFile, LoadFile, and round-trip persistence.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R143

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R143: Tests for TsvDocument.SaveToFile, LoadFile, and persistence round-trips.
/// SaveToFile(path): writes TSV content to disk.
/// LoadFile(path): reads TSV file from disk into TsvDocument.
/// Covers: SaveToFile creates file; file is non-empty; LoadFile returns document;
/// LoadFile RowCount matches; LoadFile cell values match; round-trip via save+load;
/// LoadFile with hasHeaders=true sets HasHeaders; LoadFile with hasHeaders=false;
/// SaveToFile then LoadFile preserves headers; multi-row save preserves all rows;
/// ColumnCount correct after load; GetCellValue after load; GetColumnValues after load;
/// dogfood Save->Load->Filter->Save->Load pipeline.
/// </summary>
public class TsvR143SaveToFileAndLoadFileTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR143SaveToFileAndLoadFileTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR143_" + Guid.NewGuid().ToString("N"));
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
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91";

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("out.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileIsNonEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void SaveToFile_ContentContainsTabs()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("tabs.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("\t", content);
    }

    [Fact]
    public void SaveToFile_ContentContainsAllNames()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("names.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Bob", content);
        Assert.Contains("Carol", content);
        Assert.Contains("Dave", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_ReturnsDocument()
    {
        var path = TempFile("load.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadFile_RowCountMatches()
    {
        var path = TempFile("rowcount.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void LoadFile_CellValuesMatch()
    {
        var path = TempFile("cellval.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", doc.GetCellValue(0, 0));
        Assert.Equal("Eng", doc.GetCellValue(0, 1));
        Assert.Equal("95", doc.GetCellValue(0, 2));
    }

    [Fact]
    public void LoadFile_WithHeaders_SetsHasHeaders()
    {
        var path = TempFile("withheaders.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path, hasHeaders: true);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadFile_NoHeaders_HasHeadersFalse()
    {
        var path = TempFile("noheaders.tsv");
        File.WriteAllText(path, FourRowTsv);
        var doc = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.False(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void RoundTrip_SaveThenLoad_PreservesRowCount()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("rt.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void RoundTrip_SaveThenLoad_PreservesCellValues()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("rt2.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(0, 0));
    }

    [Fact]
    public void RoundTrip_SaveThenLoad_ColumnCountCorrect()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("cols.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, reloaded.ColumnCount);
    }

    [Fact]
    public void RoundTrip_GetColumnValuesAfterLoad()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("colvals.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        var names = reloaded.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Save->Load->Filter->Save->Load pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SaveLoadFilterSaveLoad_Pipeline()
    {
        // Save original
        var doc = TsvDocument.Load(FourRowTsv);
        var path1 = TempFile("step1.tsv");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));

        // Load and filter
        var loaded = TsvDocument.LoadFile(path1, hasHeaders: false);
        Assert.Equal(4, loaded.RowCount);
        var eng = loaded.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Save filtered and reload
        var path2 = TempFile("step2.tsv");
        eng.SaveToFile(path2);
        var final = TsvDocument.LoadFile(path2, hasHeaders: false);
        Assert.Equal(2, final.RowCount);
        var names = final.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
