// Tests for FodsDocument multi-sheet data pipeline: AddSheet + InsertRowWithValues + SortRows + export.
// Sprint: FORMAT-FACTORY-FODS-MULTI-SHEET-PIPE-20260626
// Ledger: R127-GOVERNED-DOTNET-FODS-MULTI-SHEET-PIPE-001

using System;
using System.Linq;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R127: Multi-sheet pipeline tests combining AddSheet, InsertRowWithValues, SortRows,
/// GetColumnAggregates, FilterRows, and export APIs. Tests verify that multi-API
/// workflows produce consistent, correct results across multiple sheets.
/// </summary>
public class FodsR127MultiSheetPipelineTests
{
    // ---- Two sheets, independent data ----

    [Fact]
    public void TwoSheets_IndependentData_BothAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddSheet("Inventory");

        doc.InsertRowWithValues("Sales", 0, new[] { "Product", "Revenue" });
        doc.InsertRowWithValues("Sales", 1, new[] { "Widget", "5000" });

        doc.InsertRowWithValues("Inventory", 0, new[] { "Item", "Stock" });
        doc.InsertRowWithValues("Inventory", 1, new[] { "Gadget", "300" });

        var s1 = doc.GetSheetByName("Sales")!;
        var s2 = doc.GetSheetByName("Inventory")!;

        Assert.Equal("Widget", FodsDocument.GetCellValue(s1, 1, 0));
        Assert.Equal("Gadget", FodsDocument.GetCellValue(s2, 1, 0));
    }

    // ---- SortRows on one sheet does not affect another ----

    [Fact]
    public void SortRows_OneSheet_DoesNotAffectOther()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");

        doc.InsertRowWithValues("A", 0, new[] { "Z" });
        doc.InsertRowWithValues("A", 1, new[] { "A" });

        doc.InsertRowWithValues("B", 0, new[] { "Alpha" });
        doc.InsertRowWithValues("B", 1, new[] { "Omega" });

        doc.SortRows("A", sortColumn: 0, ascending: true);

        // Sheet B unaffected
        var sheetB = doc.GetSheetByName("B")!;
        Assert.Equal("Alpha", FodsDocument.GetCellValue(sheetB, 0, 0));
        Assert.Equal("Omega", FodsDocument.GetCellValue(sheetB, 1, 0));
    }

    // ---- GetSheetNames after AddSheet: count and order ----

    [Fact]
    public void AddMultipleSheets_GetSheetNames_CorrectOrder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        doc.AddSheet("Second");
        doc.AddSheet("Third");

        var names = doc.GetSheetNames();
        Assert.Equal(3, names.Count);
        Assert.Equal("First", names[0]);
        Assert.Equal("Second", names[1]);
        Assert.Equal("Third", names[2]);
    }

    // ---- FilterRows then count ----

    [Fact]
    public void FilterRows_MultipleSheetsIndependent_CorrectResults()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.InsertRowWithValues("Data", 0, new[] { "cat", "1" });
        doc.InsertRowWithValues("Data", 1, new[] { "dog", "2" });
        doc.InsertRowWithValues("Data", 2, new[] { "cat", "3" });

        var catRows = doc.FilterRows("Data", 0, "cat");
        Assert.Equal(2, catRows.Count);
    }

    // ---- Export CSV from named sheet after insert+sort ----

    [Fact]
    public void InsertSortExportCsv_DataOrdered()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.InsertRowWithValues("Report", 0, new[] { "Name" });
        doc.InsertRowWithValues("Report", 1, new[] { "Zoe" });
        doc.InsertRowWithValues("Report", 2, new[] { "Alice" });
        doc.InsertRowWithValues("Report", 3, new[] { "Ben" });

        doc.SortRows("Report", sortColumn: 0, ascending: true);

        var csv = doc.ExportSheetToCsv("Report");
        int alicePos = csv.IndexOf("Alice");
        int benPos = csv.IndexOf("Ben");
        int zoePos = csv.IndexOf("Zoe");

        Assert.True(alicePos < benPos);
        Assert.True(benPos < zoePos);
    }

    // ---- SheetCount after add and remove ----

    [Fact]
    public void AddThenRemoveSheet_SheetCountConsistent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Keep1");
        doc.AddSheet("Remove");
        doc.AddSheet("Keep2");
        Assert.Equal(3, doc.SheetCount);

        doc.RemoveSheet("Remove");
        Assert.Equal(2, doc.SheetCount);

        var names = doc.GetSheetNames();
        Assert.Contains("Keep1", names);
        Assert.Contains("Keep2", names);
        Assert.DoesNotContain("Remove", names);
    }

    // ---- Numeric column aggregates pipeline ----

    [Fact]
    public void GetColumnAggregates_AfterInsertRows_CorrectMinMax()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Numbers");
        doc.InsertRowWithValues("Numbers", 0, new[] { "10" });
        doc.InsertRowWithValues("Numbers", 1, new[] { "30" });
        doc.InsertRowWithValues("Numbers", 2, new[] { "20" });

        var agg = doc.GetColumnAggregates("Numbers", col: 0);
        Assert.Equal(10, agg.Min);
        Assert.Equal(30, agg.Max);
        Assert.Equal(3, agg.Count);
    }

    // ---- GetSheetByIndex returns sheets in order ----

    [Fact]
    public void GetSheetByIndex_ReturnsCorrectSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");

        var s0 = doc.GetSheetByIndex(0);
        var s1 = doc.GetSheetByIndex(1);
        var sNull = doc.GetSheetByIndex(5);

        Assert.NotNull(s0);
        Assert.Equal("Alpha", s0!.Name);
        Assert.NotNull(s1);
        Assert.Equal("Beta", s1!.Name);
        Assert.Null(sNull);
    }

    // ---- GetSheetByName: case-sensitive exact match ----

    [Fact]
    public void GetSheetByName_CaseSensitive_ExactMatchOnly()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MySheet");

        var found = doc.GetSheetByName("MySheet");
        var notFound = doc.GetSheetByName("mysheet"); // different case

        Assert.NotNull(found);
        Assert.Null(notFound); // should be null (case-sensitive)
    }

    // ---- Dogfood: two-sheet sort+filter+export pipeline ----

    [Fact]
    public void DogfoodPipeline_TwoSheetAnalysis_BothExportClean()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("East");
        doc.AddSheet("West");

        foreach (var name in new[] { "East", "West" })
        {
            doc.InsertRowWithValues(name, 0, new[] { "C-Product", "300" });
            doc.InsertRowWithValues(name, 1, new[] { "A-Product", "100" });
            doc.InsertRowWithValues(name, 2, new[] { "B-Product", "200" });
            doc.SortRows(name, sortColumn: 0, ascending: true);
        }

        var eastCsv = doc.ExportSheetToCsv("East");
        var westCsv = doc.ExportSheetToCsv("West");

        // Both should start with A-Product (sorted)
        int eastA = eastCsv.IndexOf("A-Product");
        int eastB = eastCsv.IndexOf("B-Product");
        Assert.True(eastA < eastB);

        int westA = westCsv.IndexOf("A-Product");
        int westB = westCsv.IndexOf("B-Product");
        Assert.True(westA < westB);
    }

}
