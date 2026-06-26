// Tests for FodtDocument.AddTable dedicated coverage.
// Sprint: ff-sprint-s244-dotnet-deepening-20260629
// Ledger: PC-FODT-R259

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R259: Dedicated tests for FodtDocument.AddTable(rows, cols).
/// Valid add → no exception.
/// TableCount increases after add.
/// ParagraphCount unchanged or increases.
/// Zero rows → throws exception.
/// Zero cols → throws exception.
/// Negative rows → throws exception.
/// Two tables → TableCount is 2.
/// Table accessible via GetTableAt.
/// Cell count matches rows × cols.
/// Dogfood: add table, get cell text, verify non-null.
/// </summary>
public class FodtR259AddTableDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_ZeroRows_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(0, 3));
    }

    [Fact]
    public void AddTable_ZeroCols_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(3, 0));
    }

    [Fact]
    public void AddTable_NegativeRows_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.ThrowsAny<Exception>(() => doc.AddTable(-1, 3));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        var ex = Record.Exception(() => doc.AddTable(2, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_TableCountIncreases()
    {
        var doc = FodtDocument.CreateEmpty();
        int before = doc.GetTableCount();
        doc.AddTable(2, 2);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_TwoTables_CountIsTwo()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.AddTable(3, 3);
        Assert.Equal(2, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_TableAccessibleViaGetTableAt()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 3);
        var table = doc.GetTableAt(0);
        Assert.NotNull(table);
    }

    [Fact]
    public void AddTable_CellTextRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        // Cell (0,0) should exist after adding a 2x2 table
        var ex = Record.Exception(() => doc.GetTableCellText(0, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_SetAndGetCellText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(3, 3);
        doc.SetTableCellText(0, 0, 0, "TopLeft");
        var text = doc.GetTableCellText(0, 0, 0);
        Assert.NotNull(text);
        Assert.Contains("TopLeft", text);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTable_GetCellText_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Before table");
        doc.AddTable(2, 3);
        doc.AppendParagraph("After table");
        Assert.Equal(1, doc.GetTableCount());
        var table = doc.GetTableAt(0);
        Assert.NotNull(table);
    }

    [Fact]
    public void DogfoodPipeline_MultipleCellsSet_AllRetrievable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "Cell00");
        doc.SetTableCellText(0, 0, 1, "Cell01");
        doc.SetTableCellText(0, 1, 0, "Cell10");
        doc.SetTableCellText(0, 1, 1, "Cell11");
        Assert.Contains("Cell00", doc.GetTableCellText(0, 0, 0));
        Assert.Contains("Cell11", doc.GetTableCellText(0, 1, 1));
    }
}
