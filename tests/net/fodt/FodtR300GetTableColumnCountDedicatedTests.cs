// Tests for FodtDocument.GetTableColumnCount dedicated coverage.
// Sprint: ff-sprint-s285-dotnet-deepening-20260630
// Ledger: PC-FODT-R300

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R300: Dedicated tests for FodtDocument.GetTableColumnCount(tableIndex).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid call returns positive int.
/// Matches AddTable col count.
/// TableCount unchanged after GetTableColumnCount.
/// Called twice returns same result.
/// Two tables have independent column counts.
/// Dogfood: add 3-col table, get col count = 3.
/// </summary>
public class FodtR300GetTableColumnCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableColumnCount_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        Assert.ThrowsAny<Exception>(() => doc.GetTableColumnCount(-1));
    }

    [Fact]
    public void GetTableColumnCount_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
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
        doc.AddTable(3, 4);
        int cols = doc.GetTableColumnCount(0);
        Assert.True(cols > 0);
    }

    [Fact]
    public void GetTableColumnCount_MatchesAddTableCols()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 5);
        int cols = doc.GetTableColumnCount(0);
        Assert.Equal(5, cols);
    }

    [Fact]
    public void GetTableColumnCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int before = doc.TableCount;
        _ = doc.GetTableColumnCount(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableColumnCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int first = doc.GetTableColumnCount(0);
        int second = doc.GetTableColumnCount(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableColumnCount_TwoTables_IndependentCounts()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.AddTable(4, 5);
        int cols0 = doc.GetTableColumnCount(0);
        int cols1 = doc.GetTableColumnCount(1);
        Assert.Equal(3, cols0);
        Assert.Equal(5, cols1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddThreeColTable_GetColCountThree()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int cols = doc.GetTableColumnCount(0);
        Assert.Equal(3, cols);
    }
}
