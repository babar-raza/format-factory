// Tests for CsvDocument.ToCsv, SaveToFile, LoadFile round-trip deeper coverage.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R174

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R174: Tests for CsvDocument.ToCsv, SaveToFile, LoadFile round-trip deeper coverage.
/// ToCsv(): serializes the document back to CSV string format.
/// SaveToFile(path): writes CSV content to a file.
/// LoadFile(path): loads CsvDocument from a file.
/// Covers: ToCsv non-null; ToCsv non-empty; ToCsv contains headers; ToCsv contains row data;
/// ToCsv uses commas; ToCsv->Load round-trip count correct; ToCsv->Load values correct;
/// SaveToFile creates file; SaveToFile file non-empty; SaveToFile->LoadFile count correct;
/// SaveToFile->LoadFile headers preserved; SaveToFile->LoadFile values correct;
/// Filter->SaveToFile->LoadFile count preserved; Filter->ToCsv->Load values correct;
/// dogfood Load->Filter->ToCsv->Load->SaveToFile->LoadFile->Filter->verify pipeline.
/// </summary>
public class CsvR174ToCsvAndSaveLoadRoundTripDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string FiveRowCsv =
        "name,dept,score,active\n" +
        "Alice,Eng,95,true\n" +
        "Bob,Finance,82,true\n" +
        "Carol,Eng,88,false\n" +
        "Dave,HR,76,true\n" +
        "Eve,Eng,91,true";

    public CsvR174ToCsvAndSaveLoadRoundTripDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR174_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_NonNull()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.NotNull(doc.ToCsv());
    }

    [Fact]
    public void ToCsv_NonEmpty()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.False(string.IsNullOrWhiteSpace(doc.ToCsv()));
    }

    [Fact]
    public void ToCsv_ContainsHeaders()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("name", csv);
        Assert.Contains("dept", csv);
        Assert.Contains("score", csv);
    }

    [Fact]
    public void ToCsv_ContainsRowData()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Eve", csv);
    }

    [Fact]
    public void ToCsv_UsesCommas()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_RoundTrip_CountCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(5, reloaded.RowCount);
    }

    [Fact]
    public void ToCsv_RoundTrip_ValuesCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        var names = reloaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    [Fact]
    public void Filter_ThenToCsv_RoundTrip_CountCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        var csv = eng.ToCsv();
        var reloaded = CsvDocument.Load(csv);
        Assert.Equal(3, reloaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_CreatesFile()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("out.csv");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
    }

    [Fact]
    public void SaveToFile_FileNonEmpty()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("nonempty.csv");
        doc.SaveToFile(path);
        Assert.False(string.IsNullOrWhiteSpace(File.ReadAllText(path)));
    }

    [Fact]
    public void SaveToFile_LoadFile_CountCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("count.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(5, loaded.RowCount);
    }

    [Fact]
    public void SaveToFile_LoadFile_HeadersPreserved()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("hdr.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.True(loaded.HasHeaders);
        Assert.Contains("name", loaded.Headers);
        Assert.Contains("active", loaded.Headers);
    }

    [Fact]
    public void SaveToFile_LoadFile_ValuesCorrect()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var path = TempFile("vals.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        var names = loaded.GetColumn("name");
        Assert.Contains("Alice", names);
        Assert.Contains("Dave", names);
    }

    [Fact]
    public void Filter_SaveToFile_LoadFile_CountPreserved()
    {
        var doc = CsvDocument.Load(FiveRowCsv);
        var active = doc.Filter(r => r.GetValue("active") == "true");
        var path = TempFile("active.csv");
        active.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(4, loaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterToCsvLoadSaveToFileLoadFileFilterVerify_Pipeline()
    {
        // Load
        var doc = CsvDocument.Load(FiveRowCsv);
        Assert.Equal(5, doc.RowCount);

        // Filter Eng
        var eng = doc.Filter(r => r.GetValue("dept") == "Eng");
        Assert.Equal(3, eng.RowCount);

        // ToCsv round-trip
        var csv = eng.ToCsv();
        var fromCsv = CsvDocument.Load(csv);
        Assert.Equal(3, fromCsv.RowCount);
        Assert.Contains("Alice", fromCsv.GetColumn("name"));

        // SaveToFile
        var path = TempFile("dogfood.csv");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        // LoadFile
        var fromFile = CsvDocument.LoadFile(path);
        Assert.Equal(3, fromFile.RowCount);
        Assert.True(fromFile.HasHeaders);

        // Filter high scorers from loaded file
        var high = fromFile.Filter(r =>
            int.TryParse(r.GetValue("score"), out var s) && s >= 91);
        Assert.Equal(2, high.RowCount); // Alice(95), Eve(91)

        // ToCsv from filtered
        var highCsv = high.ToCsv();
        Assert.Contains("Alice", highCsv);
        Assert.Contains("Eve", highCsv);
        Assert.DoesNotContain("Carol", highCsv);
    }
}
