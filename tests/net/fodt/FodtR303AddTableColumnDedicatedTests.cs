// Tests for FodtDocument.AddTableColumn dedicated coverage.
// Sprint: ff-sprint-s288-dotnet-deepening-20260630
// Ledger: PC-FODT-R303

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R303: Dedicated tests for FodtDocument.AddTableColumn(tableIndex).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid call no exception.
/// GetTableColumnCount increases after AddTableColumn.
/// TableCount unchanged after AddTableColumn.
/// ParagraphCount unchanged after AddTableColumn.
/// Called twice no exception.
/// Dogfood: add table then add column, count increases.
/// </summary>
public class FodtR303AddTableColumnDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTableColumn_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.AddTableColumn(-1));
    }

    [Fact]
    public void AddTableColumn_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.AddTableColumn(count));
    }

    [Fact]
    public void AddTableColumn_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTableColumn(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTableColumn_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.AddTableColumn(0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTableColumn_ColumnCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.GetTableColumnCount(0);
        doc.AddTableColumn(0);
        int after = doc.GetTableColumnCount(0);
        Assert.True(after > before);
    }

    [Fact]
    public void AddTableColumn_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.AddTableColumn(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void AddTableColumn_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int paraBefore = doc.ParagraphCount;
        doc.AddTableColumn(0);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AddTableColumn_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.AddTableColumn(0);
        var ex = Record.Exception(() => doc.AddTableColumn(0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableThenAddColumn_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.GetTableColumnCount(0);
        doc.AddTableColumn(0);
        int after = doc.GetTableColumnCount(0);
        Assert.True(after > before);
    }
}
