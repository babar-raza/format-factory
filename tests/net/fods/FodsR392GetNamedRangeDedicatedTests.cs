// Tests for FodsDocument.GetNamedRange dedicated coverage.
// Sprint: ff-sprint-s353-dotnet-deepening-20260630
// Ledger: PC-FODS-R392

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R392: Dedicated tests for FodsDocument.GetNamedRange().
/// Null name throws.
/// Whitespace name throws.
/// Non-existent name returns null or throws.
/// Valid named range returns non-null.
/// SheetCount unchanged after GetNamedRange.
/// Idempotent (called twice same result).
/// Dogfood: DefineNamedRange then GetNamedRange returns non-null.
/// Dogfood: multiple named ranges each accessible by name.
/// </summary>
public class FodsR392GetNamedRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRange_NullName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNamedRange(null!));
    }

    [Fact]
    public void GetNamedRange_WhitespaceName_Throws()
    {
        var doc = FodsDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetNamedRange("   "));
    }

    [Fact]
    public void GetNamedRange_NonExistentName_ReturnsNullOrThrows()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        // Either null or exception is acceptable for non-existent named range
        string? result = null;
        bool threw = false;
        try { result = doc.GetNamedRange("NoSuchRange"); }
        catch { threw = true; }
        Assert.True(threw || result == null);
    }

    [Fact]
    public void GetNamedRange_AfterDefine_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Budget");
        doc.DefineNamedRange("TotalRevenue", "Budget", 0, 0, 0, 5);
        string? range = doc.GetNamedRange("TotalRevenue");
        Assert.NotNull(range);
    }

    [Fact]
    public void GetNamedRange_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Finance");
        doc.DefineNamedRange("Income", "Finance", 0, 0, 0, 3);
        int before = doc.SheetCount;
        _ = doc.GetNamedRange("Income");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNamedRange_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Stable");
        doc.DefineNamedRange("MyRange", "Stable", 0, 0, 2, 2);
        string? first = doc.GetNamedRange("MyRange");
        string? second = doc.GetNamedRange("MyRange");
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_DefineAndGet_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.DefineNamedRange("QuarterlySales", "Report", 1, 0, 4, 3);
        string? range = doc.GetNamedRange("QuarterlySales");
        Assert.NotNull(range);
    }

    [Fact]
    public void DogfoodPipeline_MultipleRanges_EachAccessibleByName()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.DefineNamedRange("Range1", "Data", 0, 0, 1, 1);
        doc.DefineNamedRange("Range2", "Data", 2, 0, 3, 1);
        doc.DefineNamedRange("Range3", "Data", 4, 0, 5, 1);
        Assert.NotNull(doc.GetNamedRange("Range1"));
        Assert.NotNull(doc.GetNamedRange("Range2"));
        Assert.NotNull(doc.GetNamedRange("Range3"));
    }
}
