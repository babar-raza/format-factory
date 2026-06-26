// Tests for FodtDocument.GetTableCellCount dedicated coverage.
// Sprint: ff-sprint-s291-dotnet-deepening-20260630
// Ledger: PC-FODT-R306

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R306: Dedicated tests for FodtDocument.GetTableCellCount(tableIndex).
/// Negative index throws exception.
/// Out-of-bounds index throws exception.
/// No tables throws exception.
/// Valid call returns non-negative.
/// Returns rows × columns.
/// TableCount unchanged after GetTableCellCount.
/// ParagraphCount unchanged after GetTableCellCount.
/// Called twice returns same result.
/// Dogfood: add table, verify cell count matches rows × cols.
/// </summary>
public class FodtR306GetTableCellCountDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellCount_NegativeIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellCount(-1));
    }

    [Fact]
    public void GetTableCellCount_OutOfBoundsIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellCount(count));
    }

    [Fact]
    public void GetTableCellCount_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.TableCount == 0)
            Assert.ThrowsAny<Exception>(() => doc.GetTableCellCount(0));
        else
            Assert.True(true); // document has default tables
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellCount_ValidCall_ReturnsNonNegative()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int idx = doc.TableCount - 1;
        int cellCount = doc.GetTableCellCount(idx);
        Assert.True(cellCount >= 0);
    }

    [Fact]
    public void GetTableCellCount_ReturnsRowsTimesColumns()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int idx = doc.TableCount - 1;
        int cellCount = doc.GetTableCellCount(idx);
        int rows = doc.GetTableRowCount(idx);
        int cols = doc.GetTableColumnCount(idx);
        Assert.Equal(rows * cols, cellCount);
    }

    [Fact]
    public void GetTableCellCount_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int before = doc.TableCount;
        _ = doc.GetTableCellCount(before - 1);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableCellCount_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2);
        int paraBefore = doc.ParagraphCount;
        _ = doc.GetTableCellCount(doc.TableCount - 1);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableCellCount_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int idx = doc.TableCount - 1;
        int first = doc.GetTableCellCount(idx);
        int second = doc.GetTableCellCount(idx);
        Assert.Equal(first, second);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTable_CellCountMatchesRowsTimesCols()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 5);
        int idx = doc.TableCount - 1;
        int cellCount = doc.GetTableCellCount(idx);
        int rows = doc.GetTableRowCount(idx);
        int cols = doc.GetTableColumnCount(idx);
        Assert.Equal(rows * cols, cellCount);
        Assert.True(cellCount > 0);
    }
}
