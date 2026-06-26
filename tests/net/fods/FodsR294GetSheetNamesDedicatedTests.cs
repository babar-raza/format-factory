// Tests for FodsDocument.GetSheetNames dedicated coverage.
// Sprint: ff-sprint-s268-dotnet-deepening-20260630
// Ledger: PC-FODS-R294

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R294: Dedicated tests for FodsDocument.GetSheetNames().
/// Returns non-null collection.
/// Count matches SheetCount.
/// Contains added sheet name.
/// After AddSheet new name appears.
/// After RenameSheet old name gone, new name present.
/// SheetCount unchanged after GetSheetNames.
/// Called twice same count.
/// Dogfood: two sheets both names present.
/// Dogfood: rename sheet updates names list.
/// </summary>
public class FodsR294GetSheetNamesDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSheetNames_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
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
    public void GetSheetNames_AfterAddSheet_NewNameAppears()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("First");
        int countBefore = doc.GetSheetNames().Count();
        doc.AddSheet("Second");
        var namesAfter = doc.GetSheetNames();
        Assert.Equal(countBefore + 1, namesAfter.Count());
        Assert.Contains("Second", namesAfter);
    }

    [Fact]
    public void GetSheetNames_AfterRenameSheet_OldNameGone()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("OldName", names);
    }

    [Fact]
    public void GetSheetNames_AfterRenameSheet_NewNamePresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("OldName");
        doc.RenameSheet("OldName", "NewName");
        var names = doc.GetSheetNames();
        Assert.Contains("NewName", names);
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
        doc.AddSheet("A");
        doc.AddSheet("B");
        int first = doc.GetSheetNames().Count();
        int second = doc.GetSheetNames().Count();
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TwoSheets_BothNamesPresent()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sales");
        doc.AddSheet("Inventory");
        var names = doc.GetSheetNames();
        Assert.Contains("Sales", names);
        Assert.Contains("Inventory", names);
    }

    [Fact]
    public void DogfoodPipeline_RenameSheet_UpdatesNamesList()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Draft");
        doc.AddSheet("Final");
        doc.RenameSheet("Draft", "Published");
        var names = doc.GetSheetNames();
        Assert.DoesNotContain("Draft", names);
        Assert.Contains("Published", names);
        Assert.Contains("Final", names);
    }
}
