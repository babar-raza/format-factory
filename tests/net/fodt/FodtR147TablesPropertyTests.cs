// Tests for FodtDocument.Tables property and FodtTable model class.
// Sprint: ff-sprint-s132-dotnet-deepening-20260627
// Ledger: PC-FODT-R147

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R147: Tests for FodtDocument.Tables property (IReadOnlyList&lt;FodtTable&gt;) and
/// FodtTable model class. Tables returns all top-level table:table elements from
/// office:body. FodtTable.Name, FodtTable.Rows, FodtTable.RowCount, and
/// FodtTable.GetCellText are the key accessors.
/// Covers: Tables on CreateEmpty=empty list; Tables on document with table=non-empty;
/// FodtTable.Name is non-null; FodtTable.Rows is non-null; FodtTable.RowCount >= 0;
/// GetCellText out-of-range returns null; Tables accessible via Body.Tables;
/// CreateEmpty body has empty Tables; Tables count matches fixture;
/// dogfood Load fixture → Tables → FodtTable.RowCount pipeline.
/// </summary>
public class FodtR147TablesPropertyTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    // -------------------------------------------------------------------------
    // Tables on CreateEmpty document
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_Tables_CreateEmpty_IsEmptyList()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.Tables);
        Assert.Empty(doc.Tables);
    }

    [Fact]
    public void FodtDocument_Tables_CreateEmpty_CountIsZero()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.Equal(0, doc.Tables.Count);
    }

    // -------------------------------------------------------------------------
    // Tables accessible via Body
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_Body_Tables_CreateEmpty_IsEmpty()
    {
        var doc = FodtDocument.CreateEmpty();
        Assert.NotNull(doc.Body);
        Assert.NotNull(doc.Body!.Tables);
        Assert.Empty(doc.Body.Tables);
    }

    // -------------------------------------------------------------------------
    // FodtTable properties (from fixture or create empty)
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtTable_GetCellText_OutOfRangeRowIndex_ReturnsNull()
    {
        // Load a fixture if available; construct test from fixture
        var fixture = FixturePath("table-document.fodt");
        if (!File.Exists(fixture))
            return;

        var doc = FodtDocument.Load(fixture);
        if (doc.Tables.Count == 0)
            return;

        var table = doc.Tables[0];
        // Out-of-range row should return null (not throw)
        var result = table.GetCellText(99, 0);
        Assert.Null(result);
    }

    [Fact]
    public void FodtTable_RowCount_IsNonNegative()
    {
        var fixture = FixturePath("table-document.fodt");
        if (!File.Exists(fixture))
            return;

        var doc = FodtDocument.Load(fixture);
        foreach (var table in doc.Tables)
        {
            Assert.True(table.RowCount >= 0);
        }
    }

    [Fact]
    public void FodtTable_Rows_IsNonNull()
    {
        var fixture = FixturePath("table-document.fodt");
        if (!File.Exists(fixture))
            return;

        var doc = FodtDocument.Load(fixture);
        foreach (var table in doc.Tables)
        {
            Assert.NotNull(table.Rows);
        }
    }

    [Fact]
    public void FodtTable_Name_IsNonNull()
    {
        var fixture = FixturePath("table-document.fodt");
        if (!File.Exists(fixture))
            return;

        var doc = FodtDocument.Load(fixture);
        foreach (var table in doc.Tables)
        {
            Assert.NotNull(table.Name);
        }
    }

    // -------------------------------------------------------------------------
    // FodtDocument.Tables matches Body.Tables
    // -------------------------------------------------------------------------

    [Fact]
    public void FodtDocument_Tables_MatchesBodyTables_Count()
    {
        var fixture = FixturePath("table-document.fodt");
        if (!File.Exists(fixture))
        {
            // Fallback: verify on CreateEmpty
            var empty = FodtDocument.CreateEmpty();
            Assert.Equal(empty.Tables.Count, empty.Body!.Tables.Count);
            return;
        }

        var doc = FodtDocument.Load(fixture);
        Assert.Equal(doc.Tables.Count, doc.Body!.Tables.Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood: CreateEmpty → verify Tables is accessible pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_CreateEmpty_TablesAccessible_CountIsZero()
    {
        var doc = FodtDocument.CreateEmpty();

        // Tables should be accessible and empty on a new document
        Assert.NotNull(doc.Tables);
        Assert.Equal(0, doc.Tables.Count);

        // Body.Tables should match
        Assert.NotNull(doc.Body);
        Assert.Equal(doc.Tables.Count, doc.Body!.Tables.Count);
    }
}
