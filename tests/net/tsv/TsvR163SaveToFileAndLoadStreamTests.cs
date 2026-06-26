// Tests for TsvDocument.SaveToFile, LoadFile, Load(stream) deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R163

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R163: Tests for TsvDocument.SaveToFile, LoadFile, Load(stream) deeper coverage.
/// SaveToFile(path): writes TSV content to file.
/// LoadFile(path): loads TsvDocument from file.
/// Load(stream): loads TsvDocument from a Stream.
/// Covers: SaveToFile creates file; SaveToFile file non-empty;
/// SaveToFile content contains expected rows; LoadFile from written file count matches;
/// LoadFile preserves headers; LoadFile row values correct;
/// Load(stream) non-null; Load(stream) count matches; Load(stream) preserves headers;
/// SaveToFile->LoadFile round-trip values correct;
/// Load(stream) from MemoryStream count correct;
/// Load(stream) headers preserved from MemoryStream;
/// Filter->SaveToFile->LoadFile count preserved;
/// dogfood Load->Filter->SaveToFile->LoadFile->Load(stream)->GetColumnValues verify pipeline.
/// </summary>
public class TsvR163SaveToFileAndLoadStreamTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRowTsv =
        "name\tdept\tscore\tactive\n" +
        "Alice\tEng\t95\ttrue\n" +
        "Bob\tFinance\t82\ttrue\n" +
        "Carol\tEng\t88\tfalse\n" +
        "Dave\tHR\t76\ttrue";

    public TsvR163SaveToFileAndLoadStreamTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR163_" + Guid.NewGuid().ToString("N"));
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
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("out.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNonEmpty()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void SaveToFile_ContentContainsRows()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("rows.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Carol", content);
    }

    [Fact]
    public void SaveToFile_ContentContainsHeaders()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("headers.tsv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("name", content);
        Assert.Contains("dept", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_RowCount_MatchesSaved()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("load.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_PreservesHeaders()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("hdr.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.True(loaded.HasHeaders);
        Assert.Contains("name", loaded.Headers);
    }

    [Fact]
    public void LoadFile_RowValues_Correct()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var path = TempFile("vals.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var names = loaded.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void FilterSaveToFile_LoadFile_CountPreserved()
    {
        var doc = TsvDocument.Load(FourRowTsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var path = TempFile("eng.tsv");
        eng.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Load(stream)
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowTsv);
        using var ms = new MemoryStream(bytes);
        var doc = TsvDocument.Load(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_RowCount_Correct()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowTsv);
        using var ms = new MemoryStream(bytes);
        var doc = TsvDocument.Load(ms);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void LoadStream_PreservesHeaders()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowTsv);
        using var ms = new MemoryStream(bytes);
        var doc = TsvDocument.Load(ms);
        Assert.True(doc.HasHeaders);
        Assert.Contains("score", doc.Headers);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile->Load(stream)->GetColumnValues
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveLoadFileLoadStreamGetColumnValues_Pipeline()
    {
        // Load
        var doc = TsvDocument.Load(FourRowTsv);
        Assert.Equal(4, doc.RowCount);

        // Filter active=true
        var active = doc.Filter(r => r.GetValue("active") == "true");
        Assert.Equal(3, active.RowCount);

        // SaveToFile
        var path = TempFile("active.tsv");
        active.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = TsvDocument.LoadFile(path);
        Assert.Equal(3, fromFile.RowCount);
        Assert.True(fromFile.HasHeaders);

        // Load(stream)
        var bytes = File.ReadAllBytes(path);
        using var ms = new MemoryStream(bytes);
        var fromStream = TsvDocument.Load(ms);
        Assert.Equal(3, fromStream.RowCount);
        Assert.True(fromStream.HasHeaders);

        // GetColumnValues
        var names = fromStream.GetColumnValues("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Dave", names);
        Assert.DoesNotContain("Carol", names);
    }
}
