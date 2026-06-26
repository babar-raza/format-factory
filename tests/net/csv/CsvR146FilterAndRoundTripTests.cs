// Tests for CsvDocument.Filter, ToCsv round-trip, and file persistence.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R146

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R146: Tests for CsvDocument.Filter, ToCsv round-trip, and file persistence.
/// Filter(predicate): returns new CsvDocument with matching rows.
/// ToCsv: serializes to CSV string.
/// SaveToFile / LoadFile: file persistence.
/// Covers: Filter keep-all preserves count; Filter partial match subset;
/// Filter keep-none returns empty; ToCsv contains commas; ToCsv includes all rows;
/// ToCsv round-trip via Load; SaveToFile creates file; LoadFile row count;
/// Filter result is independent copy; GetCellValue after Filter;
/// GetColumn after Filter; dogfood Load->Filter->SaveToFile->LoadFile pipeline.
/// </summary>
public class CsvR146FilterAndRoundTripTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR146FilterAndRoundTripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR146_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FourRowCsv =
        "Name,Dept,Score\n" +
        "Alice,Eng,95\n" +
        "Bob,Finance,82\n" +
        "Carol,Eng,88\n" +
        "Dave,Finance,91";

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_KeepAll_PreservesCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => true);
        Assert.Equal(doc.RowCount, filtered.RowCount);
    }

    [Fact]
    public void Filter_PartialMatch_ReturnsSubset()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, filtered.RowCount);
    }

    [Fact]
    public void Filter_KeepNone_ReturnsEmpty()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => false);
        Assert.Equal(0, filtered.RowCount);
        Assert.True(filtered.IsEmpty);
    }

    [Fact]
    public void Filter_ResultIsIndependentCopy()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var filtered = doc.Filter(_ => true);
        filtered.Rows.RemoveAt(0);
        Assert.Equal(4, doc.RowCount);
    }

    [Fact]
    public void Filter_GetCellValueAfterFilter()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal("Alice", eng.GetCellValue(0, 0));
    }

    [Fact]
    public void Filter_GetColumnAfterFilter()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        var names = eng.GetColumn(0);
        Assert.Equal(2, names.Count);
        Assert.Contains("Alice", names);
        Assert.Contains("Carol", names);
    }

    // -------------------------------------------------------------------------
    // ToCsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToCsv_ContainsCommas()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains(",", csv);
    }

    [Fact]
    public void ToCsv_IncludesAllRows()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        Assert.Contains("Alice", csv);
        Assert.Contains("Bob", csv);
        Assert.Contains("Carol", csv);
        Assert.Contains("Dave", csv);
    }

    [Fact]
    public void ToCsv_RoundTrip_PreservesRowCount()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var csv = doc.ToCsv();
        var reloaded = CsvDocument.Load(csv, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile
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
    public void LoadFile_RowCountMatches()
    {
        var path = TempFile("load.csv");
        File.WriteAllText(path, FourRowCsv);
        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(4, doc.RowCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_FilterSaveLoadPipeline()
    {
        var doc = CsvDocument.Load(FourRowCsv);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(2, eng.RowCount);

        var path = TempFile("filtered.csv");
        eng.SaveToFile(path);
        Assert.True(File.Exists(path));

        var reloaded = CsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(2, reloaded.RowCount);

        var col = reloaded.GetColumn(0);
        Assert.Contains("Alice", col);
        Assert.Contains("Carol", col);
        Assert.DoesNotContain("Bob", col);
    }
}
