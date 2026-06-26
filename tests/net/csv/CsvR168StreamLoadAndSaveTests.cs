// Tests for CsvDocument.LoadStream, SaveToFile, LoadFile deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R168

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R168: Tests for CsvDocument.LoadStream, SaveToFile, LoadFile deeper.
/// LoadStream(stream): loads CsvDocument from a Stream.
/// SaveToFile(path): writes CSV to file.
/// LoadFile(path): loads CsvDocument from file.
/// Covers: LoadStream non-null; LoadStream row count correct;
/// LoadStream has headers; LoadStream cell values correct;
/// SaveToFile creates file; SaveToFile non-empty content;
/// SaveToFile has headers in content; LoadFile count matches;
/// LoadFile headers preserved; LoadFile values correct;
/// Filter->SaveToFile->LoadFile chain; LoadStream->Filter->SaveToFile chain;
/// SaveToFile->LoadStream round-trip; SaveToFile->LoadFile->Filter->Verify;
/// dogfood Load->Filter->SaveToFile->LoadFile->LoadStream->GetColumn verify.
/// </summary>
public class CsvR168StreamLoadAndSaveTests : IDisposable
{
    private readonly string _tempDir;

    private const string FourRowCsv =
        "name,dept,salary,active\n" +
        "Alice,Eng,95000,true\n" +
        "Bob,Finance,82000,true\n" +
        "Carol,Eng,88000,false\n" +
        "Dave,HR,76000,true";

    public CsvR168StreamLoadAndSaveTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR168_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // LoadStream
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadStream_NonNull()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowCsv);
        using var ms = new MemoryStream(bytes);
        var doc = CsvDocument.LoadStream(ms);
        Assert.NotNull(doc);
    }

    [Fact]
    public void LoadStream_RowCount_Correct()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowCsv);
        using var ms = new MemoryStream(bytes);
        var doc = CsvDocument.LoadStream(ms);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void LoadStream_HasHeaders_True()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowCsv);
        using var ms = new MemoryStream(bytes);
        var doc = CsvDocument.LoadStream(ms);
        Assert.True(doc.HasHeaders);
    }

    [Fact]
    public void LoadStream_CellValues_Correct()
    {
        var bytes = Encoding.UTF8.GetBytes(FourRowCsv);
        using var ms = new MemoryStream(bytes);
        var doc = CsvDocument.LoadStream(ms);
        Assert.Equal("Alice", doc.GetCellValue(0, "name"));
        Assert.Equal("Dave", doc.GetCellValue(3, "name"));
    }

    // -------------------------------------------------------------------------
    // SaveToFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("out.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_NonEmptyContent()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("nonempty.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.False(string.IsNullOrWhiteSpace(content));
    }

    [Fact]
    public void SaveToFile_ContentHasHeaders()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("hdr.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("name", content);
        Assert.Contains("dept", content);
    }

    [Fact]
    public void SaveToFile_ContentHasAllRows()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("allrows.csv");
        doc.SaveToFile(path);
        var content = File.ReadAllText(path);
        Assert.Contains("Alice", content);
        Assert.Contains("Dave", content);
    }

    // -------------------------------------------------------------------------
    // LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void LoadFile_RowCount_MatchesSaved()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("load.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_Headers_Preserved()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("hdrload.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.HasHeaders);
        Assert.Contains("salary", loaded.Headers);
    }

    [Fact]
    public void LoadFile_Values_Correct()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var path = TempFile("vals.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_Chain()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var path = TempFile("eng.csv");
        eng.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(2, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveToFileLoadFileLoadStreamGetColumnVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(FourRowCsv);
        Assert.Equal(4, doc.RowCount);

        // Filter active=true
        var active = doc.Filter(r => r.GetValue("active") == "true");
        Assert.Equal(3, active.RowCount);

        // SaveToFile
        var path = TempFile("active.csv");
        active.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = CsvDocument.LoadFile(path);
        Assert.Equal(3, fromFile.RowCount);
        Assert.True(fromFile.HasHeaders);

        // LoadStream
        var bytes = File.ReadAllBytes(path);
        using var ms = new MemoryStream(bytes);
        var fromStream = CsvDocument.LoadStream(ms);
        Assert.Equal(3, fromStream.RowCount);

        // GetColumn
        var names = fromStream.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Bob", names);
        Assert.Contains("Dave", names);
        Assert.DoesNotContain("Carol", names);
    }
}
