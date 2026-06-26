// Tests for FodsDocument.RemoveSheet dedicated coverage.
// Sprint: ff-sprint-s151-dotnet-deepening-20260628
// Ledger: PC-FODS-R158

using System;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R158: Dedicated tests for FodsDocument.RemoveSheet(string name).
/// RemoveSheet removes the named sheet from the document.
/// Throws ArgumentException for null/whitespace name.
/// Throws InvalidOperationException if no sheet with that name exists.
/// Covers: null name throws ArgumentException; whitespace name throws ArgumentException;
/// nonexistent name throws InvalidOperationException; sheet count decreases after remove;
/// remaining sheet still accessible; removed sheet no longer in GetSheetNames;
/// dogfood CreateNew->AddSheet->RemoveSheet pipeline;
/// dogfood AddSheet two sheets->RemoveSheet->one sheet remains;
/// dogfood RemoveSheet then GetSheetNames does not contain removed name;
/// dogfood RemoveSheet nonexistent after removal throws.
/// </summary>
public class FodsR158RemoveSheetDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_NullName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.RemoveSheet(null!));
    }

    [Fact]
    public void RemoveSheet_WhitespaceName_ThrowsArgumentException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<ArgumentException>(() => doc.RemoveSheet("   "));
    }

    [Fact]
    public void RemoveSheet_NonexistentName_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.Throws<InvalidOperationException>(() => doc.RemoveSheet("NoSuchSheet"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void RemoveSheet_SheetCountDecreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        var before = doc.GetSheetNames().Count;
        doc.RemoveSheet("Alpha");
        var after = doc.GetSheetNames().Count;
        Assert.Equal(before - 1, after);
    }

    [Fact]
    public void RemoveSheet_RemainingSheetStillAccessible()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.SetCellValue("Beta", 0, 0, "Kept");
        doc.RemoveSheet("Alpha");
        var names = doc.GetSheetNames();
        Assert.Contains("Beta", names);
    }

    [Fact]
    public void RemoveSheet_RemovedSheetNotInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("ToRemove");
        doc.AddSheet("ToKeep");
        doc.RemoveSheet("ToRemove");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("ToRemove", names);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateNew_AddSheet_RemoveSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Temp");
        doc.RemoveSheet("Temp");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("Temp", names);
    }

    [Fact]
    public void DogfoodPipeline_TwoSheets_RemoveOne_OneRemains()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        doc.AddSheet("Second");
        doc.RemoveSheet("First");
        var names = doc.GetSheetNames();
        Assert.Single(names);
        Assert.Equal("Second", names[0]);
    }

    [Fact]
    public void DogfoodPipeline_RemoveSheet_GetSheetNames_ExcludesRemoved()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("A");
        doc.AddSheet("B");
        doc.AddSheet("C");
        doc.RemoveSheet("B");
        var names = doc.GetSheetNames();
        Assert.Equal(2, names.Count);
        Assert.DoesNotContain("B", names);
    }

    [Fact]
    public void DogfoodPipeline_RemoveSheet_ThenRemoveSameAgain_ThrowsInvalidOperationException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Once");
        doc.AddSheet("Twice");
        doc.RemoveSheet("Once");
        Assert.Throws<InvalidOperationException>(() => doc.RemoveSheet("Once"));
    }
}
