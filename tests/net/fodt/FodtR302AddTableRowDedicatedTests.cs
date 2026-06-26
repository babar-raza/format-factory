// Tests for FodtDocument.AddTableRow dedicated coverage.
// Sprint: ff-sprint-s287-dotnet-deepening-20260630
// Ledger: PC-FODT-R302

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R302: Dedicated tests for FodtDocument.AddTableRow(tableIndex).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid call no exception.
/// GetTableRowCount increases after AddTableRow.
/// TableCount unchanged after AddTableRow.
/// ParagraphCount unchanged after AddTableRow.
/// Called twice no exception.
/// Dogfood: add table then add row, count increases.
/// </summary>
public class FodtR302AddTableRowDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTableRow_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.AddTableRow(-1));
    }

    [Fact]
    public void AddTableRow_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.AddTableRow(count));
    }

    [Fact]
    public void AddTableRow_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTableRow(0));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTableRow_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.AddTableRow(0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTableRow_RowCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.GetTableRowCount(0);
        doc.AddTableRow(0);
        int after = doc.GetTableRowCount(0);
        Assert.True(after > before);
    }

    [Fact]
    public void AddTableRow_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.AddTableRow(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void AddTableRow_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int paraBefore = doc.ParagraphCount;
        doc.AddTableRow(0);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AddTableRow_CalledTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.AddTableRow(0);
        var ex = Record.Exception(() => doc.AddTableRow(0));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableThenAddRow_CountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.GetTableRowCount(0);
        doc.AddTableRow(0);
        int after = doc.GetTableRowCount(0);
        Assert.True(after > before);
    }
}
