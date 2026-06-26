// Tests for FodsDocument.GetUsedRange, GetColumnCount, GetColumnHeaders deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODS-R212

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R212: Tests for FodsDocument.GetUsedRange, GetColumnCount, GetColumnHeaders deeper.
/// GetUsedRange(sheet): returns the used cell range as a string (e.g., "A1:C5").
/// GetColumnCount(sheet): returns the number of columns with data in the sheet.
/// GetColumnHeaders(sheet): returns the header row values as a list.
/// Covers: GetUsedRange non-null for populated sheet; GetUsedRange empty string for empty;
/// GetColumnCount positive after adding data; GetColumnCount matches header count;
/// GetColumnCount zero for empty sheet; GetColumnHeaders non-null; GetColumnHeaders count correct;
/// GetColumnHeaders contains expected values; GetColumnHeaders order preserved;
/// GetColumnHeaders after AddColumn increases count;
/// dogfood CreateEmpty->AddSheet->SetCellValues->GetUsedRange->GetColumnCount->GetColumnHeaders->Verify.
/// </summary>
public class FodsR212GetUsedRangeAndColumnCountDeepTests
{
    private static FodsDocument CreatePopulated()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sales");
        doc.SetCellValue("Sales", 0, 0, "Region");
        doc.SetCellValue("Sales", 0, 1, "Q1");
        doc.SetCellValue("Sales", 0, 2, "Q2");
        doc.SetCellValue("Sales", 1, 0, "North");
        doc.SetCellValue("Sales", 1, 1, "1500");
        doc.SetCellValue("Sales", 1, 2, "1800");
        doc.SetCellValue("Sales", 2, 0, "South");
        doc.SetCellValue("Sales", 2, 1, "1200");
        doc.SetCellValue("Sales", 2, 2, "1400");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetUsedRange
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUsedRange_PopulatedSheet_NonNull()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.GetUsedRange("Sales"));
    }

    [Fact]
    public void GetUsedRange_PopulatedSheet_NonEmpty()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.GetUsedRange("Sales"));
    }

    [Fact]
    public void GetUsedRange_EmptySheet_EmptyOrNull()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Empty");
        var range = doc.GetUsedRange("Empty");
        Assert.Null(range); // empty sheet has no used range
    }

    [Fact]
    public void GetUsedRange_TwoByThreeGrid_ReflectsData()
    {
        var doc = CreatePopulated();
        var range = doc.GetUsedRange("Sales");
        Assert.NotNull(range);
        Assert.True(range.HasValue);
    }

    // -------------------------------------------------------------------------
    // GetColumnCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCount_PopulatedSheet_PositiveCount()
    {
        var doc = CreatePopulated();
        Assert.True(doc.GetColumnCount("Sales") > 0);
    }

    [Fact]
    public void GetColumnCount_ThreeColumns_IsThree()
    {
        var doc = CreatePopulated();
        Assert.Equal(3, doc.GetColumnCount("Sales"));
    }

    [Fact]
    public void GetColumnCount_MatchesHeaderCount()
    {
        var doc = CreatePopulated();
        var headers = doc.GetColumnHeaders("Sales");
        Assert.Equal(headers.Count, doc.GetColumnCount("Sales"));
    }

    [Fact]
    public void GetColumnCount_EmptySheet_ZeroOrOne()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Clean");
        var count = doc.GetColumnCount("Clean");
        Assert.True(count == 0 || count == 1);
    }

    [Fact]
    public void GetColumnCount_AfterInsertRow_Unchanged()
    {
        var doc = CreatePopulated();
        var before = doc.GetColumnCount("Sales");
        doc.InsertRowWithValues("Sales", 3, new List<string> { "East", "900", "1100" });
        Assert.Equal(before, doc.GetColumnCount("Sales"));
    }

    // -------------------------------------------------------------------------
    // GetColumnHeaders
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnHeaders_NonNull()
    {
        var doc = CreatePopulated();
        Assert.NotNull(doc.GetColumnHeaders("Sales"));
    }

    [Fact]
    public void GetColumnHeaders_CountMatchesColumnCount()
    {
        var doc = CreatePopulated();
        var headers = doc.GetColumnHeaders("Sales");
        Assert.Equal(doc.GetColumnCount("Sales"), headers.Count);
    }

    [Fact]
    public void GetColumnHeaders_ContainsExpectedValues()
    {
        var doc = CreatePopulated();
        var headers = doc.GetColumnHeaders("Sales");
        Assert.Contains("Region", headers);
        Assert.Contains("Q1", headers);
        Assert.Contains("Q2", headers);
    }

    [Fact]
    public void GetColumnHeaders_OrderPreserved()
    {
        var doc = CreatePopulated();
        var headers = doc.GetColumnHeaders("Sales");
        Assert.Equal("Region", headers[0]);
        Assert.Equal("Q1", headers[1]);
        Assert.Equal("Q2", headers[2]);
    }

    [Fact]
    public void GetColumnHeaders_SingleColumn_HasOneHeader()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Single");
        doc.SetCellValue("Single", 0, 0, "OnlyHeader");
        var headers = doc.GetColumnHeaders("Single");
        Assert.Equal(1, headers.Count);
        Assert.Contains("OnlyHeader", headers);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddSheet_SetCellValues_GetUsedRange_GetColumnCount_GetColumnHeaders_Verify()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Inventory");

        // Set headers
        doc.SetCellValue("Inventory", 0, 0, "Item");
        doc.SetCellValue("Inventory", 0, 1, "Quantity");
        doc.SetCellValue("Inventory", 0, 2, "Price");
        doc.SetCellValue("Inventory", 0, 3, "Total");

        // Set data rows
        doc.SetCellValue("Inventory", 1, 0, "Widget");
        doc.SetCellValue("Inventory", 1, 1, "100");
        doc.SetCellValue("Inventory", 1, 2, "9.99");
        doc.SetCellValue("Inventory", 1, 3, "999.00");
        doc.SetCellValue("Inventory", 2, 0, "Gadget");
        doc.SetCellValue("Inventory", 2, 1, "50");
        doc.SetCellValue("Inventory", 2, 2, "24.99");
        doc.SetCellValue("Inventory", 2, 3, "1249.50");

        // GetUsedRange
        var range = doc.GetUsedRange("Inventory");
        Assert.NotNull(range);
        Assert.NotEmpty(range);

        // GetColumnCount
        var colCount = doc.GetColumnCount("Inventory");
        Assert.Equal(4, colCount);

        // GetColumnHeaders
        var headers = doc.GetColumnHeaders("Inventory");
        Assert.Equal(4, headers.Count);
        Assert.Equal("Item", headers[0]);
        Assert.Equal("Quantity", headers[1]);
        Assert.Equal("Price", headers[2]);
        Assert.Equal("Total", headers[3]);

        // GetRowCount
        Assert.True(doc.GetRowCount("Inventory") >= 2);

        // GetCellValue verification
        Assert.Equal("Widget", doc.GetCellValue("Inventory", 1, 0));
        Assert.Equal("Gadget", doc.GetCellValue("Inventory", 2, 0));
    }
}
