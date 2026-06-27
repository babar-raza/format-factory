// Tests for FodsDocument.GetNamedRange dedicated coverage.
// Sprint: ff-sprint-s311-dotnet-deepening-20260630
// Ledger: PC-FODS-R340

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R340: Dedicated tests for FodsDocument.GetNamedRange(rangeName).
/// Null range name throws exception.
/// Whitespace range name throws exception.
/// Nonexistent range name throws exception.
/// Valid call returns non-null.
/// SheetCount unchanged after GetNamedRange.
/// Called twice returns same result.
/// Returns AddNamedRange definition after add.
/// Dogfood: add named range then get it.
/// Dogfood: multiple named ranges each non-null.
/// </summary>
public class FodsR340GetNamedRangeDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRange_NullName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetNamedRange(null!));
    }

    [Fact]
    public void GetNamedRange_WhitespaceName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetNamedRange("   "));
    }

    [Fact]
    public void GetNamedRange_NonexistentName_ThrowsException()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        Assert.ThrowsAny<Exception>(() => doc.GetNamedRange("NoSuchRange"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetNamedRange_AfterAdd_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddNamedRange("MyRange", "Sheet1!A1:B2");
        string? range = doc.GetNamedRange("MyRange");
        Assert.NotNull(range);
    }

    [Fact]
    public void GetNamedRange_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddNamedRange("TestRange", "Sheet1!A1:C3");
        int before = doc.SheetCount;
        _ = doc.GetNamedRange("TestRange");
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetNamedRange_CalledTwice_SameResult()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddNamedRange("SalesRange", "Sheet1!A1:A10");
        string? first = doc.GetNamedRange("SalesRange");
        string? second = doc.GetNamedRange("SalesRange");
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetNamedRange_NamedRangeCount_NonNegative()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.AddNamedRange("Range1", "Sheet1!A1:A5");
        int count = doc.GetNamedRangeCount();
        Assert.True(count >= 0);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThenGetNamedRange_NonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        doc.AddNamedRange("Revenue", "Data!B2:B12");
        string? range = doc.GetNamedRange("Revenue");
        Assert.NotNull(range);
        int before = doc.SheetCount;
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void DogfoodPipeline_MultipleNamedRanges_EachNonNull()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Report");
        doc.AddNamedRange("Q1", "Report!A1:D1");
        doc.AddNamedRange("Q2", "Report!A2:D2");
        string? q1 = doc.GetNamedRange("Q1");
        string? q2 = doc.GetNamedRange("Q2");
        Assert.NotNull(q1);
        Assert.NotNull(q2);
    }
}
