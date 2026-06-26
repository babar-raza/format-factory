// Tests for FodtDocument.GetTableRowCount dedicated coverage.
// Sprint: ff-sprint-s267-dotnet-deepening-20260630
// Ledger: PC-FODT-R282

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R282: Dedicated tests for FodtDocument.GetTableRowCount(tableIndex).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid table returns positive row count.
/// Row count matches rows used to create the table.
/// TableCount unchanged after GetTableRowCount.
/// Called twice returns same result.
/// Dogfood: add 3-row table, verify row count = 3.
/// Dogfood: two tables with different row counts, verify each independently.
/// </summary>
public class FodtR282GetTableRowCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableRowCount(-1));
    }

    [Fact]
    public void GetTableRowCount_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 2);
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
        doc.AddTable(4, 3);
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
        doc.AddTable(3, 2);
        int before = doc.TableCount;
        doc.GetTableRowCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableRowCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 6);
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
        doc.AddTable(3, 2); // index 0: 3 rows
        doc.AddTable(7, 4); // index 1: 7 rows
        int rows0 = doc.GetTableRowCount(0);
        int rows1 = doc.GetTableRowCount(1);
        Assert.Equal(3, rows0);
        Assert.Equal(7, rows1);
    }
}
