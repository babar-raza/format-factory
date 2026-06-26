// Tests for FodtDocument.GetTableCellText dedicated coverage.
// Sprint: ff-sprint-s230-dotnet-deepening-20260629
// Ledger: PC-FODT-R245

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R245: Dedicated tests for FodtDocument.GetTableCellText(tableIndex, row, col).
/// Negative table index → throws exception.
/// OOB table index → throws exception.
/// Negative row → throws exception.
/// Negative col → throws exception.
/// Valid call → no exception.
/// Returns string or null.
/// Set cell text, then get returns it.
/// ParagraphCount unchanged.
/// Called twice: same result.
/// Dogfood: add table with data, get multiple cells.
/// </summary>
public class FodtR245GetTableCellTextTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(-1, 0, 0));
    }

    [Fact]
    public void GetTableCellText_OobTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(10, 0, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, -1, 0));
    }

    [Fact]
    public void GetTableCellText_NegativeCol_ThrowsException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        Assert.ThrowsAny<Exception>(() => doc.GetTableCellText(0, 0, -1));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCellText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.GetTableCellText(0, 0, 0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCellText_ReturnsStringOrNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        var result = doc.GetTableCellText(0, 0, 0);
        Assert.True(result == null || result is string);
    }

    [Fact]
    public void GetTableCellText_AfterSetCell_ReturnsText()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 0, "CellContent");
        var text = doc.GetTableCellText(0, 0, 0);
        Assert.Contains("CellContent", text ?? "");
    }

    [Fact]
    public void GetTableCellText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Para");
        doc.AddTable(2, 2);
        int before = doc.ParagraphCount;
        doc.GetTableCellText(0, 0, 0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableCellText_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 2);
        doc.SetTableCellText(0, 0, 1, "Consistent");
        var v1 = doc.GetTableCellText(0, 0, 1);
        var v2 = doc.GetTableCellText(0, 0, 1);
        Assert.Equal(v1, v2);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableWithData_GetMultipleCells()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AddTable(2, 3);
        doc.SetTableCellText(0, 0, 0, "R0C0");
        doc.SetTableCellText(0, 0, 1, "R0C1");
        doc.SetTableCellText(0, 1, 0, "R1C0");
        Assert.Contains("R0C0", doc.GetTableCellText(0, 0, 0) ?? "");
        Assert.Contains("R0C1", doc.GetTableCellText(0, 0, 1) ?? "");
        Assert.Contains("R1C0", doc.GetTableCellText(0, 1, 0) ?? "");
    }
}
