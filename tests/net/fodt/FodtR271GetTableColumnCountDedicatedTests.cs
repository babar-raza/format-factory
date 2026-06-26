// Tests for FodtDocument.GetTableColumnCount dedicated coverage.
// Sprint: ff-sprint-s256-dotnet-deepening-20260630
// Ledger: PC-FODT-R271

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R271: Dedicated tests for FodtDocument.GetTableColumnCount(tableIndex).
/// Negative table index → throws exception.
/// Out-of-bounds table index → throws exception.
/// No tables → throws exception.
/// Valid table index → returns positive column count.
/// Column count matches cols used to create the table.
/// TableCount unchanged after GetTableColumnCount.
/// Called twice → same result.
/// Dogfood: add 3-column table, verify column count = 3.
/// Dogfood: two tables with different column counts, verify each independently.
/// </summary>
public class FodtR271GetTableColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnCount_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(-1));
    }

    [Fact]
    public void GetTableColumnCount_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(count));
    }

    [Fact]
    public void GetTableColumnCount_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnCount_ValidTable_ReturnsPositive()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 4);
        int colCount = doc.GetTableColumnCount(0);
        Assert.True(colCount > 0);
    }

    [Fact]
    public void GetTableColumnCount_MatchesTableColumns()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 5); // 3 rows, 5 cols
        int colCount = doc.GetTableColumnCount(0);
        Assert.Equal(5, colCount);
    }

    [Fact]
    public void GetTableColumnCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableColumnCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 6);
        int first = doc.GetTableColumnCount(0);
        int second = doc.GetTableColumnCount(0);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ThreeColumnTable_VerifyColumnCount()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3); // 2 rows, 3 cols
        int colCount = doc.GetTableColumnCount(0);
        Assert.Equal(3, colCount);
    }

    [Fact]
    public void DogfoodPipeline_TwoTablesWithDifferentCols_IndependentCounts()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3); // index 0: 3 cols
        doc.AddTable(4, 7); // index 1: 7 cols
        int cols0 = doc.GetTableColumnCount(0);
        int cols1 = doc.GetTableColumnCount(1);
        Assert.Equal(3, cols0);
        Assert.Equal(7, cols1);
    }
}
