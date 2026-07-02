// Tests for FodsDocument.GetSheetByIndex.
// Sprint: ff-sprint-s137-dotnet-deepening-20260627
// Ledger: PC-FODS-R148

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R148: Tests for FodsDocument.GetSheetByIndex.
/// GetSheetByIndex returns null for out-of-range indices and the sheet at valid indices.
/// Covers: index -1 returns null; index 0 with one sheet returns sheet; index 0 two sheets;
/// index 1 two sheets returns second; index equal count returns null;
/// returned sheet name matches expected; returned sheet is not null for valid index;
/// SheetCount reflects added sheets; AddSheet then GetSheetByIndex;
/// dogfood CreateNew->AddSheet->GetSheetByIndex->SetCellValue pipeline.
/// </summary>
public class FodsR148GetSheetByIndexTests
{
    // -------------------------------------------------------------------------
    // Out-of-range guards
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_NegativeIndex_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(-1));
    }

    [Fact]
    public void GetSheetByIndex_IndexEqualToSheetCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        // One sheet by default
        Assert.Null(doc.GetSheetByIndex(doc.SheetCount));
    }

    [Fact]
    public void GetSheetByIndex_IndexBeyondSheetCount_ReturnsNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Null(doc.GetSheetByIndex(99));
    }

    // -------------------------------------------------------------------------
    // Valid index returns correct sheet
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetByIndex_ZeroIndex_ReturnsFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var sheet = doc.GetSheetByIndex(0);
        Assert.NotNull(sheet);
    }

    [Fact]
    public void GetSheetByIndex_ZeroIndex_SheetNameMatchesGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var expectedName = doc.GetSheetNames()[0];
        var sheet = doc.GetSheetByIndex(0);
        Assert.Equal(expectedName, sheet!.Name);
    }

    [Fact]
    public void GetSheetByIndex_OneIndex_ReturnsSecondSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("SecondSheet");
        var sheet = doc.GetSheetByIndex(1);
        Assert.NotNull(sheet);
        Assert.Equal("SecondSheet", sheet!.Name);
    }

    [Fact]
    public void GetSheetByIndex_TwoSheets_IndexZero_ReturnsFirstSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var firstName = doc.GetSheetNames()[0];
        doc.AddSheet("AnotherSheet");
        var sheet = doc.GetSheetByIndex(0);
        Assert.Equal(firstName, sheet!.Name);
    }

    [Fact]
    public void GetSheetByIndex_AfterAddSheet_SheetCountReflectsAddition()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        doc.AddSheet("Extra");
        Assert.Equal(before + 1, doc.SheetCount);
        Assert.NotNull(doc.GetSheetByIndex(before));
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> AddSheet -> GetSheetByIndex -> SetCellValue
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddSheet_GetSheetByIndex_SetCellValue_VerifiesValue()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddSheet("DataSheet");

        // Use index 1 (second sheet = DataSheet)
        var sheet = doc.GetSheetByIndex(1);
        Assert.NotNull(sheet);
        Assert.Equal("DataSheet", sheet!.Name);

        // Set a cell on the document using the sheet name
        FodsDocument.SetCellValue(sheet, 0, 0, "Revenue");
        var value = FodsDocument.GetCellValue(sheet, 0, 0);
        Assert.Equal("Revenue", value);
    }
}
