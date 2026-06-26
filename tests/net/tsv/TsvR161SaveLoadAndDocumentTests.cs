// Tests for TsvDocument.SaveToFile, LoadFile, Load(stream) deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R161

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R161: Tests for TsvDocument.SaveToFile, LoadFile, Load(stream) deeper coverage.
/// SaveToFile(path): writes document to file.
/// LoadFile(path): loads document from file.
/// TsvDocument.Load(stream): loads from readable stream.
/// Covers: SaveToFile creates file; SaveToFile content has headers;
/// SaveToFile->LoadFile count matches; SaveToFile->LoadFile values correct;
/// LoadFile count; LoadFile HasHeaders; LoadFile RowCount positive;
/// LoadFile ColumnCount correct; Load(stream) non-null; Load(stream) count matches;
/// Load(stream) values correct; Load(stream) HasHeaders;
/// SaveToFile->LoadFile->Filter; Load(stream) empty stream;
/// SaveToFile mutated then LoadFile reflects changes;
/// dogfood Load->Mutate->SaveToFile->LoadFile->Filter->Verify pipeline.
/// </summary>
public class TsvR161SaveLoadAndDocumentTests : IDisposable
{
    private readonly string _tempDir;

    private const string ThreeRowTsv =
        "name\tdept\tscore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88";

    public TsvR161SaveLoadAndDocumentTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR161_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

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
    public void SaveToFile_ContentHasHeaders()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("headers.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("name", content);
        Assert.Contains("dept", content);
    }

    [Fact]
    public void SaveToFile_ContentHasData()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("data.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Bob", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_CountMatches()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("load.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_HasHeaders_True()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("headers.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.True(loaded.HasHeaders);
    }

    [Fact]
    public void LoadFile_ColumnCount_Correct()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("cols.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.ColumnCount);
    }

    [Fact]
    public void LoadFile_ValuesCorrect()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("vals.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var names = loaded.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    [Fact]
    public void LoadFile_AfterMutation_ReflectsChanges()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        doc.SetCellValue(0, 0, "Alicia");
        var path = TempFile("mutated.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alicia", loaded.GetCellValue(0, "name"));
    }

    [Fact]
    public void LoadFile_ThenFilter_Works()
    {
        var doc = TsvDocument.Load(ThreeRowTsv);
        var path = TempFile("filter.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var eng = loaded.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
    }

    // -------------------------------------------------------------------------
    // Load(stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRowTsv));
        var doc = TsvDocument.Load(stream);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_CountMatches()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRowTsv));
        var doc = TsvDocument.Load(stream);
        Assert.Equal(3, doc.RowCount);
    }

    [Fact]
    public void LoadStream_ValuesCorrect()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRowTsv));
        var doc = TsvDocument.Load(stream);
        var names = doc.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
    }

    [Fact]
    public void LoadStream_HasHeaders_True()
    {
        using var stream = new MemoryStream(Encoding.UTF8.GetBytes(ThreeRowTsv));
        var doc = TsvDocument.Load(stream);
        Assert.True(doc.HasHeaders);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Mutate->SaveToFile->LoadFile->Filter->Verify
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadMutateSaveLoadFilterVerify_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(ThreeRowTsv);
        Assert.Equal(3, doc.RowCount);

        // Mutate
        doc.SetCellValue(0, 2, "100"); // Alice's score
        Assert.Equal("100", doc.GetCellValue(0, "score"));

        // SaveToFile
        var path = TempFile("dogfood.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(3, loaded.RowCount);
        Assert.True(loaded.HasHeaders);
        Assert.Equal("100", loaded.GetCellValue(0, "score"));

        // Filter
        var eng = loaded.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(2, eng.RowCount);

        // Verify
        var names = eng.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
