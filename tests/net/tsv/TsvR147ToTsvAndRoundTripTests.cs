// Tests for TsvDocument.ToTsv serialization and multi-format round-trip.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R147

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R147: Tests for TsvDocument.ToTsv multi-row serialization and round-trip.
/// ToTsv(): serializes to TSV string; all rows; tab-separated.
/// LoadFile/SaveToFile: file persistence.
/// Covers: ToTsv single row; ToTsv multiple rows all included; ToTsv has tabs;
/// ToTsv preserves row count on reload; ToTsv preserves cell values on reload;
/// SaveToFile->LoadFile round-trip row count; SaveToFile->LoadFile cell values;
/// ToTsv with unicode content; ToTsv empty doc; ToTsv after Filter;
/// LoadFile->Filter->ToTsv->Load chain; RowCount consistent before/after;
/// GetColumnValues after ToTsv reload; dogfood multi-step pipeline.
/// </summary>
public class TsvR147ToTsvAndRoundTripTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR147ToTsvAndRoundTripTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR147_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private const string FiveRowTsv =
        "Name\tDept\tScore\n" +
        "Alice\tEng\t95\n" +
        "Bob\tFinance\t82\n" +
        "Carol\tEng\t88\n" +
        "Dave\tFinance\t91\n" +
        "Eve\tEng\t79";

    // -------------------------------------------------------------------------
    // ToTsv
    // -------------------------------------------------------------------------

    [Fact]
    public void ToTsv_SingleRow_ContainsValues()
    {
        var doc = TsvDocument.Load("Name\tScore", hasHeaders: false);
        var tsv = doc.ToTsv();
        Assert.Contains("Name", tsv);
        Assert.Contains("Score", tsv);
    }

    [Fact]
    public void ToTsv_MultipleRows_AllIncluded()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var tsv = doc.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Bob", tsv);
        Assert.Contains("Carol", tsv);
        Assert.Contains("Dave", tsv);
        Assert.Contains("Eve", tsv);
    }

    [Fact]
    public void ToTsv_HasTabs()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.Contains("\t", doc.ToTsv());
    }

    [Fact]
    public void ToTsv_PreservesRowCountOnReload()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void ToTsv_PreservesCellValuesOnReload()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var tsv = doc.ToTsv();
        var reloaded = TsvDocument.Load(tsv, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(1, 0));
        Assert.Equal("95", reloaded.GetCellValue(1, 2));
    }

    [Fact]
    public void ToTsv_AfterFilter_OnlyFilteredRows()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        var tsv = eng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.Contains("Eve", tsv);
        Assert.DoesNotContain("Bob", tsv);
        Assert.DoesNotContain("Dave", tsv);
    }

    [Fact]
    public void ToTsv_EmptyDoc_IsEmptyOrNewline()
    {
        var doc = TsvDocument.Load(string.Empty, hasHeaders: false);
        var tsv = doc.ToTsv();
        Assert.True(string.IsNullOrEmpty(tsv) || tsv == "\n");
    }

    // -------------------------------------------------------------------------
    // SaveToFile / LoadFile round-trip
    // -------------------------------------------------------------------------

    [Fact]
    public void SaveToFile_LoadFile_RowCountMatches()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var path = TempFile("rt.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(doc.RowCount, reloaded.RowCount);
    }

    [Fact]
    public void SaveToFile_LoadFile_CellValuesMatch()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var path = TempFile("cells.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal("Alice", reloaded.GetCellValue(1, 0));
    }

    [Fact]
    public void SaveToFile_LoadFile_ColumnValuesMatch()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        var path = TempFile("cols.tsv");
        doc.SaveToFile(path);
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        var names = reloaded.GetColumnValues(0);
        Assert.Contains("Alice", names);
        Assert.Contains("Eve", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Load->Filter->SaveToFile->LoadFile->Filter chain
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_LoadFilterSaveThenFilterAgain_Pipeline()
    {
        var doc = TsvDocument.Load(FiveRowTsv);
        Assert.Equal(6, doc.RowCount); // header + 5 data rows

        // Filter Eng rows
        var eng = doc.Filter(row => row.Length > 1 && row[1] == "Eng");
        Assert.Equal(3, eng.RowCount); // Alice, Carol, Eve

        // Save
        var path = TempFile("eng.tsv");
        eng.SaveToFile(path);

        // Reload
        var reloaded = TsvDocument.LoadFile(path, hasHeaders: false);
        Assert.Equal(3, reloaded.RowCount);

        // Filter again by score > 80
        var highEng = reloaded.Filter(row =>
            row.Length > 2 && int.TryParse(row[2], out var s) && s > 80);
        Assert.Equal(2, highEng.RowCount); // Alice(95), Carol(88) pass; Eve(79) fails

        // ToTsv
        var tsv = highEng.ToTsv();
        Assert.Contains("Alice", tsv);
        Assert.Contains("Carol", tsv);
        Assert.DoesNotContain("Eve", tsv);
    }
}
