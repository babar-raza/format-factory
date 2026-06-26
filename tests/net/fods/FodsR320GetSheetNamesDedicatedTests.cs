// Tests for FodsDocument.GetSheetNames dedicated coverage.
// Sprint: ff-sprint-s292-dotnet-deepening-20260630
// Ledger: PC-FODS-R320

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R320: Dedicated tests for FodsDocument.GetSheetNames().
/// Returns non-null collection.
/// Count matches SheetCount.
/// Contains added sheet name.
/// SheetCount unchanged after GetSheetNames.
/// Called twice returns same count.
/// After AddSheet count increases.
/// Names are non-null strings.
/// Dogfood: create two sheets, names collection contains both.
/// Dogfood: rename sheet, new name appears in GetSheetNames.
/// </summary>
public class FodsR320GetSheetNamesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        var names = doc.GetSheetNames();
        Assert.NotNull(names);
    }

    [Fact]
    public void GetSheetNames_CountMatchesSheetCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        var names = doc.GetSheetNames();
        Assert.Equal(doc.SheetCount, names.Count());
    }

    [Fact]
    public void GetSheetNames_ContainsAddedSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("MySheet");
        var names = doc.GetSheetNames();
        Assert.Contains("MySheet", names);
    }

    [Fact]
    public void GetSheetNames_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int before = doc.SheetCount;
        _ = doc.GetSheetNames();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetSheetNames_CalledTwice_SameCount()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        int first = doc.GetSheetNames().Count();
        int second = doc.GetSheetNames().Count();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetSheetNames_AfterAddSheet_CountIncreases()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        int before = doc.GetSheetNames().Count();
        doc.AddSheet("Second");
        int after = doc.GetSheetNames().Count();
        Assert.True(after > before);
    }

    [Fact]
    public void GetSheetNames_AllNamesNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("SheetA");
        doc.AddSheet("SheetB");
        foreach (var name in doc.GetSheetNames())
            Assert.NotNull(name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoSheets_NamesCollectionContainsBoth()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddSheet("Inventory");
        var names = doc.GetSheetNames().ToList();
        Assert.Contains("Sales", names);
        Assert.Contains("Inventory", names);
    }

    [Fact]
    public void DogfoodPipeline_RenameSheet_NewNameAppearsInGetSheetNames()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        var names = doc.GetSheetNames().ToList();
        Assert.Contains("NewName", names);
    }
}
