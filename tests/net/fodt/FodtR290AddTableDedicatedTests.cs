// Tests for FodtDocument.AddTable dedicated coverage.
// Sprint: ff-sprint-s275-dotnet-deepening-20260630
// Ledger: PC-FODT-R290

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R290: Dedicated tests for FodtDocument.AddTable(rows, cols).
/// Zero rows throws exception.
/// Zero cols throws exception.
/// Negative rows throws exception.
/// Negative cols throws exception.
/// Valid call no exception.
/// TableCount increases after AddTable.
/// ParagraphCount unchanged after AddTable.
/// Called twice TableCount increases by 2.
/// Dogfood: add table, GetTableRowCount = rows param.
/// Dogfood: add table, GetTableColumnCount = cols param.
/// </summary>
public class FodtR290AddTableDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_ZeroRows_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(0, 3));
    }

    [Fact]
    public void AddTable_ZeroCols_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(3, 0));
    }

    [Fact]
    public void AddTable_NegativeRows_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(-1, 3));
    }

    [Fact]
    public void AddTable_NegativeCols_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(3, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_ValidRowsAndCols_NoException()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddTable(3, 4));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_TableCountIncreases()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(2, 3);
        Assert.True(doc.TableCount > before);
    }

    [Fact]
    public void AddTable_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        int paraBefore = doc.ParagraphCount;
        doc.AddTable(2, 3);
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void AddTable_CalledTwice_TableCountIncreasesByTwo()
    {
        var doc = FodtDocument.CreateNew();
        int before = doc.TableCount;
        doc.AddTable(2, 3);
        doc.AddTable(4, 5);
        Assert.Equal(before + 2, doc.TableCount);
    }

    [Fact]
    public void AddTable_OneByOne_ValidTable()
    {
        var doc = FodtDocument.CreateNew();
        var ex = Record.Exception(() => doc.AddTable(1, 1));
        Assert.Null(ex);
        Assert.True(doc.TableCount >= 1);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTable_RowCountMatchesParam()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(5, 3);
        int tableIdx = doc.TableCount - 1;
        Assert.Equal(5, doc.GetTableRowCount(tableIdx));
    }

    [Fact]
    public void DogfoodPipeline_AddTable_ColCountMatchesParam()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 7);
        int tableIdx = doc.TableCount - 1;
        Assert.Equal(7, doc.GetTableColumnCount(tableIdx));
    }
}
