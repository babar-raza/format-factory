// Tests for FodtDocument.GetTableName dedicated coverage.
// Sprint: ff-sprint-s344-dotnet-deepening-20260630
// Ledger: PC-FODT-R362

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R362: Dedicated tests for FodtDocument.GetTableName().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Returns non-null for valid table.
/// ParagraphCount unchanged after GetTableName.
/// TableCount unchanged after GetTableName.
/// Idempotent (called twice same result).
/// After AddTable with name returns correct name.
/// Dogfood: multiple tables each returns correct name.
/// </summary>
public class FodtR362GetTableNameDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableName_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Summary");
        Assert.ThrowsAny<Exception>(() => doc.GetTableName(-1));
    }

    [Fact]
    public void GetTableName_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Summary");
        Assert.ThrowsAny<Exception>(() => doc.GetTableName(10));
    }

    [Fact]
    public void GetTableName_ValidTable_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "DataTable");
        string? name = doc.GetTableName(0);
        Assert.NotNull(name);
    }

    [Fact]
    public void GetTableName_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Document content");
        doc.AddTable(2, 3, "Table1");
        int before = doc.ParagraphCount;
        _ = doc.GetTableName(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableName_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Table1");
        int before = doc.TableCount;
        _ = doc.GetTableName(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableName_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "StableTable");
        string? first = doc.GetTableName(0);
        string? second = doc.GetTableName(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableName_AfterAddTableWithName_ReturnsCorrectName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 4, "Revenue Report");
        string? name = doc.GetTableName(0);
        Assert.NotNull(name);
        Assert.Equal("Revenue Report", name);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleTables_EachReturnsCorrectName()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Alpha Table");
        doc.AddTable(3, 3, "Beta Table");
        doc.AddTable(4, 2, "Gamma Table");
        Assert.Equal("Alpha Table", doc.GetTableName(0));
        Assert.Equal("Beta Table", doc.GetTableName(1));
        Assert.Equal("Gamma Table", doc.GetTableName(2));
    }
}
