// Tests for TsvDocument.ToCsv, SaveToFile, LoadFile round-trip deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R176

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R176: Tests for TsvDocument.ToCsv, SaveToFile, LoadFile round-trip deeper.
/// ToCsv(): returns the document content as a CSV string.
/// SaveToFile(path): saves the TSV document to the given path.
/// LoadFile(path): loads a TsvDocument from a file path.
/// ToTsv(): returns the document content as a TSV string.
/// Covers: ToCsv non-null; ToCsv non-empty; ToCsv contains header values;
/// ToCsv contains data values; ToCsv has commas (not tabs) as separator;
/// SaveToFile creates file; SaveToFile non-empty file; LoadFile after SaveToFile correct RowCount;
/// LoadFile headers preserved; LoadFile data accessible via GetCell;
/// ToTsv has tabs as separator; SaveToFile->LoadFile->ToCsv round-trip;
/// dogfood CreateEmpty->AddRows->SaveToFile->LoadFile->ToCsv->Filter->SaveToFile->Verify.
/// </summary>
public class TsvR176ToCsvAndSaveRoundTripDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR176ToCsvAndSaveRoundTripDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR176_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static TsvDocument CreateSample()
    {
        var doc = TsvDocument.CreateEmpty(new System.Collections.Generic.List<string> { "Name", "Dept", "Score" });
        doc.AddRow(new System.Collections.Generic.List<string> { "Alice", "Eng", "92" });
        doc.AddRow(new System.Collections.Generic.List<string> { "Bob", "Finance", "85" });
        doc.AddRow(new System.Collections.Generic.List<string> { "Carol", "Eng", "78" });
        return doc;
    }

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = CreateSample();
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_NonEmpty()
    {
        var doc = CreateSample();
        Assert.NotEmpty(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_ContainsHeaderValues()
    {
        var doc = CreateSample();
        var csv = doc.ToCsv();
        Assert.Contains("Name", csv);
        Assert.Contains("Dept", csv);
    }

    [Fact]
    public void ToCsv_ContainsDataValues()
    {
        var doc = CreateSample();
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Finance", csv);
    }

    [Fact]
    public void ToCsv_HasCommasSeparator()
    {
        var doc = CreateSample();
        var csv = doc.ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_AfterFilter_SmallerOutput()
    {
        var doc = CreateSample();
        var allCsv = doc.ToCsv();
        var filtered = doc.Filter(r => r.GetCell("Dept") == "Eng");
        var filteredCsv = filtered.ToCsv();
        Assert.True(filteredCsv.Length < allCsv.Length);
    }

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_NonNull()
    {
        var doc = CreateSample();
        Assert.NotNull(doc.ToTsv());
    }

    [Fact]
    public void ToTsv_HasTabSeparator()
    {
        var doc = CreateSample();
        var tsv = doc.ToTsv();
        Assert.Contains("\t", tsv);
    }

    [Fact]
    public void ToTsv_ContainsData()
    {
        var doc = CreateSample();
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CreateSample();
        var path = TempFile("output.tsv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNonEmpty()
    {
        var doc = CreateSample();
        var path = TempFile("nonempty.tsv");
        doc.SaveToFile(path);
        Assert.True(new FileInfo(path).Length > 0);
    }

    [Fact]
    public void LoadFile_AfterSaveToFile_CorrectRowCount()
    {
        var doc = CreateSample();
        var path = TempFile("roundtrip.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }

    [Fact]
    public void LoadFile_HeadersPreserved()
    {
        var doc = CreateSample();
        var path = TempFile("headers.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Contains("Name", loaded.Headers);
        Assert.Contains("Dept", loaded.Headers);
    }

    [Fact]
    public void LoadFile_DataAccessibleViaGetCell()
    {
        var doc = CreateSample();
        var path = TempFile("data.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal("Alice", loaded.GetCell(0, "Name"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddRows_SaveToFile_LoadFile_ToCsv_Filter_SaveToFile_Verify()
    {
        // CreateEmpty and add rows
        var doc = TsvDocument.CreateEmpty(new System.Collections.Generic.List<string> { "ID", "Name", "Dept", "Score" });
        doc.AddRow(new System.Collections.Generic.List<string> { "1", "Alice", "Eng", "92" });
        doc.AddRow(new System.Collections.Generic.List<string> { "2", "Bob", "Finance", "85" });
        doc.AddRow(new System.Collections.Generic.List<string> { "3", "Carol", "Eng", "78" });
        doc.AddRow(new System.Collections.Generic.List<string> { "4", "Dave", "HR", "91" });
        Assert.Equal(4, doc.RowCount);

        // SaveToFile
        var mainPath = TempFile("main.tsv");
        doc.SaveToFile(mainPath);
        Assert.True(File.Exists(mainPath));

        // LoadFile
        var loaded = TsvDocument.LoadFile(mainPath);
        Assert.Equal(4, loaded.RowCount);
        Assert.Contains("Name", loaded.Headers);
        Assert.Equal("Alice", loaded.GetCell(0, "Name"));
        Assert.Equal("91", loaded.GetCell(3, "Score"));

        // ToCsv on loaded
        var csv = loaded.ToCsv();
        Assert.NotEmpty(csv);
        Assert.Contains("Alice", csv);
        Assert.Contains(",", csv);

        // Filter and save
        var eng = loaded.Filter(r => r.GetCell("Dept") == "Eng");
        Assert.Equal(2, eng.RowCount);
        var engPath = TempFile("eng.tsv");
        eng.SaveToFile(engPath);
        Assert.True(File.Exists(engPath));

        // Reload filtered
        var engLoaded = TsvDocument.LoadFile(engPath);
        Assert.Equal(2, engLoaded.RowCount);
        var names = engLoaded.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
        Assert.DoesNotContain("Bob", names);
    }
}
