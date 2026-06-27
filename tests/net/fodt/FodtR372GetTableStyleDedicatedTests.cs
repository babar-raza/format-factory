// Tests for FodtDocument.GetTableStyle dedicated coverage.
// Sprint: ff-sprint-s354-dotnet-deepening-20260630
// Ledger: PC-FODT-R372

using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R372: Dedicated tests for FodtDocument.GetTableStyle().
/// Negative table index throws.
/// Out-of-range table index throws.
/// Valid table returns non-null.
/// ParagraphCount unchanged after GetTableStyle.
/// TableCount unchanged after GetTableStyle.
/// Idempotent (called twice same result).
/// After SetTableStyle returns expected style.
/// Dogfood: multiple tables with different styles each non-null.
/// </summary>
public class FodtR372GetTableStyleDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableStyle_NegativeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableStyle(-1));
    }

    [Fact]
    public void GetTableStyle_OutOfRangeTableIndex_Throws()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Grid");
        Assert.ThrowsAny<Exception>(() => doc.GetTableStyle(99));
    }

    [Fact]
    public void GetTableStyle_ValidTable_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 4, "Report");
        string? style = doc.GetTableStyle(0);
        Assert.NotNull(style);
    }

    [Fact]
    public void GetTableStyle_ParagraphCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddParagraph("Intro paragraph");
        doc.AddTable(2, 3, "Data");
        int before = doc.ParagraphCount;
        _ = doc.GetTableStyle(0);
        Assert.Equal(before, doc.ParagraphCount);
    }

    [Fact]
    public void GetTableStyle_TableCountUnchanged()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 3, "Summary");
        int before = doc.TableCount;
        _ = doc.GetTableStyle(0);
        Assert.Equal(before, doc.TableCount);
    }

    [Fact]
    public void GetTableStyle_CalledTwice_SameResult()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 5, "Stable");
        string? first = doc.GetTableStyle(0);
        string? second = doc.GetTableStyle(0);
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetTableStyle_AfterSetTableStyle_ReturnsExpected()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(3, 3, "Styled");
        doc.SetTableStyle(0, "Table Grid");
        string? style = doc.GetTableStyle(0);
        Assert.NotNull(style);
        Assert.Equal("Table Grid", style);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleTables_DifferentStylesEachNonNull()
    {
        var doc = FodtDocument.CreateNew();
        doc.AddTable(2, 2, "Table A");
        doc.AddTable(3, 3, "Table B");
        doc.AddTable(4, 4, "Table C");
        doc.SetTableStyle(0, "Plain Table");
        doc.SetTableStyle(1, "Grid Table");
        doc.SetTableStyle(2, "Colorful List");
        Assert.NotNull(doc.GetTableStyle(0));
        Assert.NotNull(doc.GetTableStyle(1));
        Assert.NotNull(doc.GetTableStyle(2));
    }
}
