// Tests for FodtDocument.GetTableColumnCount dedicated coverage.
// Sprint: ff-sprint-s378-dotnet-deepening-20260630
// Ledger: PC-FODT-R396

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R396: Dedicated tests for FodtDocument.GetTableColumnCount().
/// Negative table index throws.
/// Out-of-range table index throws.
/// No tables document throws.
/// Valid table index returns non-negative.
/// ParagraphCount unchanged after GetTableColumnCount.
/// TableCount unchanged after GetTableColumnCount.
/// Idempotent (called twice same result).
/// Dogfood: table with columns returns non-negative.
/// Dogfood: multiple tables each non-negative.
/// </summary>
public class FodtR396GetTableColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnCount_NegativeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(-1));
    }

    [Fact]
    public void GetTableColumnCount_OutOfRangeIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(doc.TableCount));
    }

    [Fact]
    public void GetTableColumnCount_NoTables_Throws()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(0));
    }

    [Fact]
    public void GetTableColumnCount_ValidIndex_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int count = doc.GetTableColumnCount(0);
        Assert.True(count >= 0);
    }

    [Fact]
    public void GetTableColumnCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro");
        doc.AddTable(2, 2);
        int before = doc.ParagraphCount;
        _ = doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableColumnCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        _ = doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableColumnCount_Idempotent()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 2);
        int first = doc.GetTableColumnCount(0);
        int second = doc.GetTableColumnCount(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TableWithColumns_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 3);
        int count = doc.GetTableColumnCount(0);
        Assert.True(count >= 0);
    }

    [Fact]
    public void DogfoodPipeline_MultipleTables_EachNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        doc.AddTable(3, 4);
        doc.AddTable(1, 6);
        Assert.True(doc.GetTableColumnCount(0) >= 0);
        Assert.True(doc.GetTableColumnCount(1) >= 0);
        Assert.True(doc.GetTableColumnCount(2) >= 0);
    }
}
