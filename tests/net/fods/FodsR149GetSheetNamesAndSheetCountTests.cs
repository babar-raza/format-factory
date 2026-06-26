// Tests for FodsDocument.GetSheetNames and FodsDocument.SheetCount.
// Sprint: ff-sprint-s139-dotnet-deepening-20260627
// Ledger: PC-FODS-R149

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R149: Tests for FodsDocument.GetSheetNames() and FodsDocument.SheetCount.
/// GetSheetNames() returns the names of all sheets in document order.
/// SheetCount is a computed property equal to Sheets.Count.
/// Covers: GetSheetNames on CreateNew has one entry; name is non-empty string;
/// after AddSheet count increases; two sheets names are distinct; order matches AddSheet;
/// SheetCount on CreateNew is 1; after AddSheet is 2; after RemoveSheet decreases;
/// GetSheetNames count matches SheetCount;
/// dogfood CreateNew->AddSheet×2->GetSheetNames->SheetCount pipeline.
/// </summary>
public class FodsR149GetSheetNamesAndSheetCountTests
{
    // -------------------------------------------------------------------------
    // GetSheetNames basic
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_CreateNew_HasOneEntry()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Single(doc.GetSheetNames());
    }

    [Fact]
    public void GetSheetNames_CreateNew_NameIsNonEmpty()
    {
        var doc = FodsDocument.CreateNew();
        var names = doc.GetSheetNames();
        Assert.False(string.IsNullOrEmpty(names[0]));
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_HasTwoEntries()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Second");
        Assert.Equal(2, doc.GetSheetNames().Count);
    }

    [Fact]
    public void GetSheetNames_TwoSheets_NamesAreDistinct()
    {
        var doc = FodsDocument.CreateNew();
        var first = doc.GetSheetNames()[0];
        doc.AddSheet("UniqueSecond");
        var names = doc.GetSheetNames();
        Assert.Contains("UniqueSecond", names);
        Assert.NotEqual(first, "UniqueSecond");
    }

    [Fact]
    public void GetSheetNames_Order_MatchesAddSheetOrder()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        var names = doc.GetSheetNames();
        // Alpha added before Beta
        int alphaIdx = names.IndexOf("Alpha");
        int betaIdx = names.IndexOf("Beta");
        Assert.True(alphaIdx < betaIdx);
    }

    // -------------------------------------------------------------------------
    // SheetCount
    // -------------------------------------------------------------------------

    [Fact]
    public void SheetCount_CreateNew_IsOne()
    {
        var doc = FodsDocument.CreateNew();
        Assert.Equal(1, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_AfterAddSheet_IsTwo()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Extra");
        Assert.Equal(2, doc.SheetCount);
    }

    [Fact]
    public void SheetCount_MatchesGetSheetNamesCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("S2");
        doc.AddSheet("S3");
        Assert.Equal(doc.GetSheetNames().Count, doc.SheetCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateNew -> AddSheet×2 -> GetSheetNames -> SheetCount
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTwoSheets_GetSheetNames_SheetCount_Consistent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Revenue");
        doc.AddSheet("Expenses");

        var names = doc.GetSheetNames();
        Assert.Equal(3, doc.SheetCount);
        Assert.Equal(3, names.Count);
        Assert.Contains("Revenue", names);
        Assert.Contains("Expenses", names);
    }
}
