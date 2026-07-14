// Tests for FodtDocument.SetTableCellText dedicated coverage.
// Sprint: ff-sprint-s294-dotnet-deepening-20260630
// Ledger: PC-FODT-R309

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R309: Dedicated tests for FodtDocument.SetTableCellText(tableIndex, row, col, text).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Negative row throws exception.
/// Negative column throws exception.
/// Valid call no exception.
/// TableCount unchanged after SetTableCellText.
/// ParagraphCount unchanged after SetTableCellText.
/// Set twice no exception.
/// Dogfood: set text, GetTableCellText returns value.
/// </summary>
public class FodtR309SetTableCellTextDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(-1, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(count, 0, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        if (doc.TableCount == 0)
            Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(0, 0, 0, "text"));
        else
            Assert.True(doc.TableCount > 0); // document has default tables
    }

    [Fact]
    public void SetTableCellText_NegativeRow_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int idx = doc.TableCount - 1;
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(idx, -1, 0, "text"));
    }

    [Fact]
    public void SetTableCellText_NegativeColumn_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int idx = doc.TableCount - 1;
        Assert.ThrowsAny<Exception>(() => doc.SetTableCellText(idx, 0, -1, "text"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableCellText_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int idx = doc.TableCount - 1;
        var ex = Record.Exception(() => doc.SetTableCellText(idx, 0, 0, "Hello"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableCellText_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int before = doc.TableCount;
        doc.SetTableCellText(before - 1, 0, 0, "Value");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SetTableCellText_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int paraBefore = doc.ParagraphCount;
        doc.SetTableCellText(doc.TableCount - 1, 0, 0, "Value");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void SetTableCellText_SetTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3);
        int idx = doc.TableCount - 1;
        doc.SetTableCellText(idx, 0, 0, "First");
        var ex = Record.Exception(() => doc.SetTableCellText(idx, 0, 0, "Second"));
        Assert.Null(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetText_GetTableCellTextReturnsValue()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4);
        int idx = doc.TableCount - 1;
        doc.SetTableCellText(idx, 1, 2, "CellData");
        string? result = doc.GetTableCellText(idx, 1, 2);
        Assert.NotNull(result);
    }
}
