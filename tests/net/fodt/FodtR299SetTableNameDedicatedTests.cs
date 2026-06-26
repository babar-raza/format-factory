// Tests for FodtDocument.SetTableName dedicated coverage.
// Sprint: ff-sprint-s284-dotnet-deepening-20260630
// Ledger: PC-FODT-R299

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R299: Dedicated tests for FodtDocument.SetTableName(tableIndex, name).
/// Negative table index throws exception.
/// Out-of-bounds table index throws exception.
/// No tables throws exception.
/// Valid call no exception.
/// TableCount unchanged after SetTableName.
/// Set twice no exception.
/// ParagraphCount unchanged after SetTableName.
/// GetTableName returns updated name after SetTableName.
/// Dogfood: add table, set name, get name matches.
/// </summary>
public class FodtR299SetTableNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableName_NegativeTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        Assert.ThrowsAny<Exception>(() => doc.SetTableName(-1, "Table1"));
    }

    [Fact]
    public void SetTableName_OutOfBoundsTableIndex_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int count = doc.TableCount;
        Assert.ThrowsAny<Exception>(() => doc.SetTableName(count, "Table1"));
    }

    [Fact]
    public void SetTableName_NoTables_ThrowsException()
    {
        var doc = FodtDocument.CreateNew();
        Assert.ThrowsAny<Exception>(() => doc.SetTableName(0, "Table1"));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void SetTableName_ValidCall_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        var ex = Record.Exception(() => doc.SetTableName(0, "MyTable"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableName_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int before = doc.TableCount;
        doc.SetTableName(0, "RenamedTable");
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void SetTableName_SetTwice_NoException()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableName(0, "FirstName");
        var ex = Record.Exception(() => doc.SetTableName(0, "SecondName"));
        Assert.Null(ex);
    }

    [Fact]
    public void SetTableName_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        int paraBefore = doc.ParagraphCount;
        doc.SetTableName(0, "Table");
        Assert.Equal(paraBefore, doc.ParagraphCount);
    }

    [Fact]
    public void SetTableName_GetTableNameReturnsUpdated()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3);
        doc.SetTableName(0, "UpdatedTableName");
        string name = doc.GetTableName(0);
        Assert.Contains("UpdatedTableName", name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_AddTableSetNameGetNameMatches()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(4, 4);
        doc.SetTableName(0, "DogfoodTable");
        string name = doc.GetTableName(0);
        Assert.Contains("DogfoodTable", name);
    }
}
