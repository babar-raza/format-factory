// Tests for FodtDocument.GetTableRowCount dedicated coverage.
// Sprint: ff-sprint-s255-dotnet-deepening-20260630
// Ledger: PC-FODT-R270

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R270: Dedicated tests for FodtDocument.GetTableRowCount(tableIndex).
/// Negative table index → throws exception.
/// Out-of-bounds table index → throws exception.
/// Valid table index → returns positive row count (tables have at least 1 row).
/// Row count matches rows used to create the table.
/// TableCount unchanged after GetTableRowCount.
/// Called twice → same result.
/// Dogfood: add 3-row table, verify row count = 3.
/// Dogfood: add two tables with different row counts, verify each independently.
/// </summary>
public class FodtR270GetTableRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(-1));
    }

    [Fact]
    public void GetTableRowCount_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(count));
    }

    [Fact]
    public void GetTableRowCount_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_ValidTable_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int rowCount = doc.GetTableRowCount(0);
        Assert.True(rowCount > 0);
    }

    [Fact]
    public void GetTableRowCount_MatchesTableRows()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 3); // 5 rows, 3 cols
        int rowCount = doc.GetTableRowCount(0);
        Assert.Equal(5, rowCount);
    }

    [Fact]
    public void GetTableRowCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        doc.GetTableRowCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableRowCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 3);
        int first = doc.GetTableRowCount(0);
        int second = doc.GetTableRowCount(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeRowTable_VerifyRowCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2); // 3 rows, 2 cols
        int rowCount = doc.GetTableRowCount(0);
        Assert.Equal(3, rowCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoTablesWithDifferentRows_IndependentCounts()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3); // index 0: 2 rows
        doc.AddTable(5, 4); // index 1: 5 rows
        int rows0 = doc.GetTableRowCount(0);
        int rows1 = doc.GetTableRowCount(1);
        Assert.Equal(2, rows0);
        Assert.Equal(5, rows1);
    }
}
