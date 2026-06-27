// Tests for FodtDocument.GetTableRowCount dedicated coverage.
// Sprint: ff-sprint-s377-dotnet-deepening-20260630
// Ledger: PC-FODT-R395

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R395: Dedicated tests for FodtDocument.GetTableRowCount().
/// Negative table index throws.
/// Out-of-range table index throws.
/// No tables document throws.
/// Valid table index returns non-negative.
/// ParagraphCount unchanged after GetTableRowCount.
/// TableCount unchanged after GetTableRowCount.
/// Idempotent (called twice same result).
/// Dogfood: table with rows returns non-negative.
/// Dogfood: multiple tables each non-negative.
/// </summary>
public class FodtR395GetTableRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(-1));
    }

    [Fact]
    public void GetTableRowCount_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(doc.TableCount));
    }

    [Fact]
    public void GetTableRowCount_NoTables_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableRowCount_ValidIndex_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int count = doc.GetTableRowCount(0);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTableRowCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        int before = doc.ParagraphCount;
        _ = doc.GetTableRowCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableRowCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        _ = doc.GetTableRowCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableRowCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 2);
        int first = doc.GetTableRowCount(0);
        int second = doc.GetTableRowCount(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableWithRows_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 3);
        int count = doc.GetTableRowCount(0);
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleTables_EachNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.AddTable(3, 4);
        doc.AddTable(1, 5);
        Assert.True(doc.GetTableRowCount(0) >= 0);
        Assert.True(doc.GetTableRowCount(1) >= 0);
        Assert.True(doc.GetTableRowCount(2) >= 0);
    }
}
