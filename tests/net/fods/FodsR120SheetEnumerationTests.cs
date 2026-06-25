// Tests for FodsDocument.Sheets, SheetCount, GetSheetNames, and sheet enumeration.
// Sprint: FORMAT-FACTORY-FODS-SHEET-ENUM-20260626
// Ledger: R120-GOVERNED-DOTNET-FODS-SHEET-ENUM-001

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R120: Sheet enumeration APIs — Sheets, SheetCount, GetSheetNames, and multi-sheet
/// traversal for document inspection and pipeline scenarios.
/// </summary>
public class FodsR120SheetEnumerationTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "../../../../../../samples/by-format/fods"));

    private static string MinimalPath => Path.Combine(SamplesDir, "minimal-spreadsheet.fods");
    private static string MultiPath   => Path.Combine(SamplesDir, "multi-sheet-basic.fods");

    // ---- SheetCount ----

    [Fact]
    public void SheetCount_NewDoc_IsZero()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(0, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_AfterAddSheet_IsOne()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Equal(1, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_AfterAddTwoSheets_IsTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        Assert.Equal(2, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_MinimalFixture_IsOne()
    {
        var doc = FodsDocument.Load(MinimalPath);
        Assert.Equal(1, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_MultiSheetFixture_IsTwo()
    {
        var doc = FodsDocument.Load(MultiPath);
        Assert.Equal(2, doc.SheetCount);
    }

    // ---- Sheets collection ----

    [Fact]
    public void Sheets_NewDoc_IsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Empty(doc.Sheets);
    }

    [Fact]
    public void Sheets_AfterAddTwoSheets_HasCorrectNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        doc.AddSheet("Second");
        var names = doc.Sheets.Select(s => s.Name).ToList();
        Assert.Contains("First", names);
        Assert.Contains("Second", names);
    }

    [Fact]
    public void Sheets_MultiSheetFixture_NamesMatchGetSheetNames()
    {
        var doc = FodsDocument.Load(MultiPath);
        var fromSheets = doc.Sheets.Select(s => s.Name).ToList();
        var fromGetNames = doc.GetSheetNames().ToList();
        Assert.Equal(fromGetNames, fromSheets);
    }

    // ---- GetSheetNames ----

    [Fact]
    public void GetSheetNames_NewDoc_IsEmpty()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Empty(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_MultiSheetFixture_ReturnsDataAndSummary()
    {
        var doc = FodsDocument.Load(MultiPath);
        var names = doc.GetSheetNames();
        Assert.Contains("Data", names);
        Assert.Contains("Summary", names);
    }

    [Fact]
    public void GetSheetNames_PreservesOrder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Sheet2");
        doc.AddSheet("Sheet3");
        var names = doc.GetSheetNames().ToList();
        Assert.Equal("Sheet1", names[0]);
        Assert.Equal("Sheet2", names[1]);
        Assert.Equal("Sheet3", names[2]);
    }

    // ---- Enumeration consistency ----

    [Fact]
    public void Sheets_Count_MatchesSheetCount()
    {
        var doc = FodsDocument.Load(MultiPath);
        Assert.Equal(doc.SheetCount, doc.Sheets.Count);
    }

    [Fact]
    public void GetSheetNames_Count_MatchesSheetCount()
    {
        var doc = FodsDocument.Load(MultiPath);
        Assert.Equal(doc.SheetCount, doc.GetSheetNames().Count);
    }

    // ---- Dogfood pipeline ----

    [Fact]
    public void DogfoodPipeline_BuildMultiSheet_ExportEachToTsv()
    {
        var doc = FodsDocument.CreateNew();
        var s1 = doc.AddSheet("Products");
        FodsDocument.SetCellValue(s1, 0, 0, "Name");
        FodsDocument.SetCellValue(s1, 0, 1, "Price");
        FodsDocument.InsertRow(s1, 1, new[] { "Widget", "9.99" });

        var s2 = doc.AddSheet("Orders");
        FodsDocument.SetCellValue(s2, 0, 0, "OrderId");
        FodsDocument.SetCellValue(s2, 0, 1, "ProductName");
        FodsDocument.InsertRow(s2, 1, new[] { "1001", "Widget" });

        Assert.Equal(2, doc.SheetCount);
        Assert.Equal(new[] { "Products", "Orders" }, doc.GetSheetNames());

        // Export each sheet to TSV and verify content
        foreach (var sheet in doc.Sheets)
        {
            var tsv = FodsDocumentExporter.ExportSheetToTsv(sheet);
            Assert.NotEmpty(tsv);
        }

        // Verify individual sheet access
        Assert.NotNull(doc.GetSheetByName("Products"));
        Assert.NotNull(doc.GetSheetByName("Orders"));
        Assert.Null(doc.GetSheetByName("NonExistent"));
    }

    [Fact]
    public void DogfoodPipeline_RemoveSheet_SheetCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");
        doc.AddSheet("C");

        Assert.Equal(3, doc.SheetCount);

        FodsDocument.RemoveSheet(doc, "B");

        Assert.Equal(2, doc.SheetCount);
        Assert.DoesNotContain("B", doc.GetSheetNames());
        Assert.Contains("A", doc.GetSheetNames());
        Assert.Contains("C", doc.GetSheetNames());
    }
}
