// Tests for FodsDocument.HasSheet, GetUsedRange, ExportSheetToJson, ExportSheetToMarkdown.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R185

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R185: Tests for FodsDocument.HasSheet, GetUsedRange, ExportSheetToJson, ExportSheetToMarkdown.
/// HasSheet(name): checks if a named sheet exists.
/// GetUsedRange(): returns min/max row and col bounds of non-empty cells.
/// ExportSheetToJson(): serializes first sheet to JSON string.
/// ExportSheetToMarkdown(): serializes first sheet to Markdown table.
/// Covers: HasSheet true for existing sheet; HasSheet false for non-existent;
/// HasSheet false after RemoveSheet; GetUsedRange non-null after SetCellValue;
/// GetUsedRange returns correct MinRow and MaxRow; GetUsedRange returns correct MinCol MaxCol;
/// ExportSheetToJson non-null; ExportSheetToJson non-empty; ExportSheetToJson contains values;
/// ExportSheetToMarkdown non-null; ExportSheetToMarkdown contains pipe chars;
/// ExportSheetToMarkdown contains cell values; GetSheetStats non-zero after SetCellValue;
/// dogfood CreateNew->SetCell->HasSheet->GetUsedRange->ExportJson->ExportMarkdown.
/// </summary>
public class FodsR185HasSheetAndGetUsedRangeTests
{
    private static FodsDocument CreateWithData()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue(0, 0, "Product");
        doc.SetCellValue(0, 1, "Price");
        doc.SetCellValue(1, 0, "Widget");
        doc.SetCellValue(1, 1, "9.99");
        doc.SetCellValue(2, 0, "Gadget");
        doc.SetCellValue(2, 1, "24.99");
        return doc;
    }

    // -------------------------------------------------------------------------
    // HasSheet
    // -------------------------------------------------------------------------

    [Fact]
    public void HasSheet_TrueForDefaultSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var defaultName = doc.GetSheetNames()[0];
        Assert.True(doc.HasSheet(defaultName));
    }

    [Fact]
    public void HasSheet_FalseForNonExistentSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.False(doc.HasSheet("NonExistentSheet_R185"));
    }

    [Fact]
    public void HasSheet_TrueForAddedSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("NewSheet");
        Assert.True(doc.HasSheet("NewSheet"));
    }

    [Fact]
    public void HasSheet_FalseAfterRemoveSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("ToRemove");
        doc.RemoveSheet("ToRemove");
        Assert.False(doc.HasSheet("ToRemove"));
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_NonNullAfterSetCellValue()
    {
        var doc = CreateWithData();
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
    }

    [Fact]
    public void GetUsedRange_MinRowIsZero()
    {
        var doc = CreateWithData();
        var range = doc.GetUsedRange()!.Value;
        Assert.Equal(0, range.MinRow);
    }

    [Fact]
    public void GetUsedRange_MaxRowIsTwo()
    {
        var doc = CreateWithData();
        var range = doc.GetUsedRange()!.Value;
        Assert.Equal(2, range.MaxRow);
    }

    [Fact]
    public void GetUsedRange_MinColIsZero()
    {
        var doc = CreateWithData();
        var range = doc.GetUsedRange()!.Value;
        Assert.Equal(0, range.MinCol);
    }

    [Fact]
    public void GetUsedRange_MaxColIsOne()
    {
        var doc = CreateWithData();
        var range = doc.GetUsedRange()!.Value;
        Assert.Equal(1, range.MaxCol);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToJson
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToJson_IsNotNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.ExportSheetToJson());
    }

    [Fact]
    public void ExportSheetToJson_IsNonEmpty()
    {
        var doc = CreateWithData();
        Assert.False(string.IsNullOrEmpty(doc.ExportSheetToJson()));
    }

    [Fact]
    public void ExportSheetToJson_ContainsCellValues()
    {
        var doc = CreateWithData();
        var json = doc.ExportSheetToJson();
        Assert.Contains("Widget", json);
        Assert.Contains("9.99", json);
    }

    // -------------------------------------------------------------------------
    // ExportSheetToMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportSheetToMarkdown_IsNotNull()
    {
        var doc = CreateWithData();
        Assert.NotNull(doc.ExportSheetToMarkdown());
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsPipeChars()
    {
        var doc = CreateWithData();
        Assert.Contains("|", doc.ExportSheetToMarkdown());
    }

    [Fact]
    public void ExportSheetToMarkdown_ContainsCellValues()
    {
        var doc = CreateWithData();
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("Widget", md);
    }

    // -------------------------------------------------------------------------
    // GetSheetStats
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetStats_NonEmptyCellCount_Positive()
    {
        var doc = CreateWithData();
        var sheetName = doc.GetSheetNames()[0];
        var stats = doc.GetSheetStats(sheetName);
        Assert.True(stats.NonEmptyCellCount > 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew->SetCell->HasSheet->GetUsedRange->ExportJson->ExportMarkdown
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_SetCellHasSheetGetUsedRangeExportJsonMarkdown_Pipeline()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheetName = doc.GetSheetNames()[0];

        // HasSheet
        Assert.True(doc.HasSheet(sheetName));
        Assert.False(doc.HasSheet("NonExistent"));

        // Set cell values
        doc.SetCellValue(0, 0, "Name");
        doc.SetCellValue(0, 1, "Score");
        doc.SetCellValue(1, 0, "Alice");
        doc.SetCellValue(1, 1, "95");

        // GetUsedRange
        var range = doc.GetUsedRange();
        Assert.NotNull(range);
        Assert.Equal(0, range!.Value.MinRow);
        Assert.Equal(1, range.Value.MaxRow);
        Assert.Equal(1, range.Value.MaxCol);

        // ExportSheetToJson
        var json = doc.ExportSheetToJson();
        Assert.Contains("Alice", json);
        Assert.Contains("95", json);

        // ExportSheetToMarkdown
        var md = doc.ExportSheetToMarkdown();
        Assert.Contains("|", md);
        Assert.Contains("Alice", md);
    }
}
